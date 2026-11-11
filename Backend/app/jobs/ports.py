"""Structural ports the worker depends on (no HTTP-route imports).

These mirror the frozen ``app.schemas.services`` protocols at the
narrowest width the worker needs.  Production adapters are injected by
the entry point (``app.workers.pdf_worker``):

* storage: the Appwrite adapter (``app.services.storage``) -- the
  worker only ever calls ``inspect_storage_file`` /
  ``open_storage_range`` / ``delete_storage_file`` on it.  It never
  imports HTTP route modules.
* queue: :class:`app.jobs.queue.JobQueueStore` (or an in-memory test
  double with the same surface).
* embeddings: :class:`app.rag.embeddings.EmbeddingService`.
* indexing: :class:`app.rag.indexing.IndexService`.

Method shapes intentionally match the frozen protocols exactly so a
real adapter is assignable without adaptation.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol
from uuid import UUID



from app.schemas.services import JobClaim, PdfChunk, StorageFileInfo  # noqa: E402


class StoragePort(Protocol):
    """Subset of A3's ``StorageAdapter`` used by the worker."""

    def inspect_storage_file(self, *, bucket_id: str, file_id: str) -> StorageFileInfo:
        ...

    def open_storage_range(
        self, *, bucket_id: str, file_id: str, range_header: str | None
    ) -> tuple[bytes, dict[str, str]]:
        ...

    def delete_storage_file(self, *, bucket_id: str, file_id: str) -> None:
        ...


class EmbedderPort(Protocol):
    """``PdfPipeline.embed_texts``: batch embeddings (batch 16)."""

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        ...


class IndexPort(Protocol):
    """``PdfPipeline.publish/delete_index_version`` (A4/A5 contract)."""

    def publish_index_version(
        self,
        *,
        user_id: UUID | str,
        project_id: UUID | str,
        document_id: UUID | str,
        index_version: UUID | str,
        chunks: Sequence[PdfChunk],
        embeddings: Sequence[Sequence[float]] | None = None,
    ) -> int:
        ...

    def delete_index_version(
        self,
        *,
        user_id: UUID | str | None = None,
        project_id: UUID | str | None = None,
        document_id: UUID | str,
        index_version: UUID | str,
    ) -> None:
        ...


class QueuePort(Protocol):
    """Worker-side surface of ``JobQueueStore`` (short tx per call)."""

    def claim_next_jobs(
        self, *, worker_id: str, limit: int, lease_seconds: int
    ) -> list[JobClaim]:
        ...

    def renew_job_lease(
        self, *, job_id: UUID, lease_token: int, worker_id: str, lease_seconds: int
    ) -> bool:
        ...

    def update_progress(
        self,
        *,
        job_id: UUID,
        lease_token: int,
        worker_id: str,
        stage: str | None = None,
        progress_current: int | None = None,
        progress_total: int | None = None,
    ) -> bool:
        ...

    def complete_job(
        self, *, job_id: UUID, lease_token: int, worker_id: str, chunk_count: int | None = None
    ) -> bool:
        ...

    def fail_job(
        self,
        *,
        job_id: UUID,
        lease_token: int,
        worker_id: str,
        error_code: str,
        error_message: str,
        retryable: bool,
        **backoff: Any,
    ) -> bool:
        ...

    def load_job_context(self, job_id: UUID) -> Any:
        ...


__all__ = ["EmbedderPort", "IndexPort", "QueuePort", "StoragePort"]
