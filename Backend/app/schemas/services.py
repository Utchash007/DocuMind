"""Frozen internal service boundaries (``plan.md`` section 4.3).

These :class:`typing.Protocol` classes define callable contracts for
the application adapters. They are documentation +
type-checking artifacts: implementations must match the method names,
parameter names, and return shapes below, but no implementation is
required to inherit from them.  All methods are synchronous (blocking
FastAPI handlers and the worker run in a threadpool).

Global rules for every signature here:

* Network calls (Appwrite, Chroma, Groq, Hugging Face) run **outside**
  any open database transaction.  Claim/persist -> commit -> provider
  call -> persist result guarded by the fencing token.
* The worker imports these shared services, never HTTP handlers or the
  FastAPI application entry point.
* Identity/ownership always comes from the verified principal, never
  from a browser-supplied owner header or ID.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol
from uuid import UUID

from app.schemas.common import CamelModel, Citation, JobKind

if TYPE_CHECKING:  # pragma: no cover - typing only
    from sqlalchemy.orm import Session

    from app.db.models import Conversation, Document, Message, ProcessingJob, Project, User

# ---------------------------------------------------------------------------
# Small internal payloads
# ---------------------------------------------------------------------------


class StorageFileInfo(CamelModel):
    """Result of Storage creation/inspection (A3 adapter)."""

    file_id: str
    bucket_id: str
    size: int
    mime_type: str
    chunks_uploaded: int = 0
    chunks_total: int = 0
    completed: bool = False


class AuthorizedSource(CamelModel):
    """One retrievable (document, active index version) pair (A5).

    Retrieval pairs must be exact: a document ID and an index version are
    only authorized together, never as independent lists.
    """

    document_id: UUID
    index_version: UUID
    file_name: str


class HistoryTurn(CamelModel):
    """One completed turn of bounded conversation history (A5)."""

    role: str
    content: str
    position: int


class GeneratedAnswer(CamelModel):
    """Answer plus validated citations, without writing conversation rows."""

    answer: str
    citations: list[Citation]


class PdfChunk(CamelModel):
    """Immutable chunk metadata produced by extraction (A4)."""

    chunk_id: str
    text: str
    page_number: int
    source: str


class JobClaim(CamelModel):
    """Claimed job handed to the worker (A4 queue)."""

    job_id: UUID
    kind: JobKind
    target_document_id: UUID
    target_epoch: int
    index_version: UUID | None
    lease_token: int
    lease_expires_at: datetime


# ---------------------------------------------------------------------------
# Protocols (implementations are owned by the named agent)
# ---------------------------------------------------------------------------


class PrincipalResolver(Protocol):
    """A2: verify an Appwrite credential and resolve the internal user."""

    def resolve_principal(self, authorization_header: str) -> Any:
        """Return ``AuthenticatedUser`` or raise the 401/503 auth error.

        Fails closed: provider verification outages raise a retryable
        service error, they never produce an anonymous principal.
        """
        ...


class OwnedResourceLookups(Protocol):
    """A3/A5: owner-scoped lookups (concrete helpers in app.db.queries)."""

    def get_owned_project(
        self, session: Session, *, user_id: UUID, project_id: UUID, include_deleted: bool = False
    ) -> Project | None:
        ...

    def get_owned_document(
        self,
        session: Session,
        *,
        user_id: UUID,
        project_id: UUID,
        document_id: UUID,
        include_deleted: bool = False,
    ) -> Document | None:
        ...

    def get_owned_conversation(
        self,
        session: Session,
        *,
        user_id: UUID,
        project_id: UUID,
        conversation_id: UUID,
        include_deleted: bool = False,
    ) -> Conversation | None:
        ...

    def get_owned_job(self, session: Session, *, user_id: UUID, job_id: UUID) -> ProcessingJob | None:
        ...


class StorageAdapter(Protocol):
    """A3: private Appwrite Storage operations (server-side only)."""

    def create_storage_file(
        self, *, bucket_id: str, file_id: str, data: bytes, mime_type: str
    ) -> StorageFileInfo:
        """Upload with a pre-reserved file ID and owner-only access."""
        ...

    def inspect_storage_file(self, *, bucket_id: str, file_id: str) -> StorageFileInfo:
        """Return size/fingerprint/chunk completion for reconciliation."""
        ...

    def open_storage_range(
        self, *, bucket_id: str, file_id: str, range_header: str | None
    ) -> tuple[bytes, dict[str, str]]:
        """Return (chunk bytes, response headers) for inline PDF serving."""
        ...

    def delete_storage_file(self, *, bucket_id: str, file_id: str) -> None:
        """Idempotent delete: already-missing files count as deleted."""
        ...


class JobQueue(Protocol):
    """A4: transactional job enqueue/claim/lease/finish primitives."""

    def enqueue_job(
        self,
        session: Session,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        target_document_id: UUID,
        document_id: UUID | None,
        kind: JobKind,
        target_epoch: int,
        resource_snapshot: dict[str, Any],
        available_at: datetime | None = None,
        max_attempts: int = 3,
    ) -> ProcessingJob:
        """Insert the job in the caller's transaction (idempotent per
        the partial unique nonterminal (target, kind) index)."""
        ...

    def claim_next_jobs(
        self, session: Session, *, worker_id: str, limit: int, lease_seconds: int
    ) -> list[JobClaim]:
        """``FOR UPDATE SKIP LOCKED`` claim of due jobs; bumps the fencing
        token and attempt count before releasing the lock."""
        ...

    def renew_job_lease(
        self, session: Session, *, job_id: UUID, lease_token: int, worker_id: str, lease_seconds: int
    ) -> bool:
        """Compare-and-set heartbeat; False when the claim is no longer ours."""
        ...

    def complete_job(
        self, session: Session, *, job_id: UUID, lease_token: int, worker_id: str
    ) -> bool:
        """Publish success (with the document pointer, if applicable) in
        the caller's transaction after fencing checks. False = stale."""
        ...

    def fail_job(
        self,
        session: Session,
        *,
        job_id: UUID,
        lease_token: int,
        worker_id: str,
        error_code: str,
        error_message: str,
        retryable: bool,
    ) -> bool:
        """Move to ``retry_wait`` (bounded backoff) or terminal ``failed``."""
        ...

    def cancel_job(self, session: Session, *, job_id: UUID, reason: str) -> bool:
        """Cancel a nonterminal job (deletion/retry invalidation)."""
        ...


class PdfPipeline(Protocol):
    """A4: extraction, embeddings, and versioned index publication."""

    def extract_pdf_chunks(self, pdf_path: Path, *, file_name: str) -> list[PdfChunk]:
        """Page-bound chunks (~800 chars, one page per chunk, 1-based pages)."""
        ...

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Batch embeddings; production never silently uses mock vectors."""
        ...

    def publish_index_version(
        self, *, user_id: UUID, project_id: UUID, document_id: UUID, index_version: UUID, chunks: Sequence[PdfChunk]
    ) -> None:
        """Write chunks into the fresh ``index_version`` namespace."""
        ...

    def delete_index_version(
        self, *, user_id: UUID, project_id: UUID, document_id: UUID, index_version: UUID
    ) -> None:
        """Idempotent delete of one index namespace (all versions on cleanup)."""
        ...


class AnswerGenerator(Protocol):
    """A5: grounded answer generation without persistence side effects."""

    def generate_answer(
        self, *, question: str, history: Sequence[HistoryTurn], authorized_sources: Sequence[AuthorizedSource],
        user_id: UUID, project_id: UUID
    ) -> GeneratedAnswer:
        """Return an answer and citations refined against retrieved chunks.

        Must not write conversation rows, must not treat earlier assistant
        output as source evidence, and must include the current question
        exactly once in the assembled prompt.
        """
        ...


__all__ = [
    "AnswerGenerator",
    "AuthorizedSource",
    "GeneratedAnswer",
    "HistoryTurn",
    "JobClaim",
    "JobQueue",
    "OwnedResourceLookups",
    "PdfChunk",
    "PdfPipeline",
    "PrincipalResolver",
    "StorageAdapter",
    "StorageFileInfo",
]
