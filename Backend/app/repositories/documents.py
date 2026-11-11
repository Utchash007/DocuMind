"""Document and job repository.

Owns the PostgreSQL half of plan.md §5.1 (upload reservation /
idempotency / finalize / retry / coordinated deletion) and the
reconciliation hooks the worker consumes. No network I/O happens
here; the caller commits each short transaction *before* any Storage
call and *after* inspecting storage completion.

Job enqueue is done through the frozen :class:`JobQueue` Protocol
(``app/schemas/services.py``) so queue adapters can be supplied without
touching these functions.  :class:`DirectJobQueue` is the default
implementation (canonical durable enqueue + owner-scoped
cancel); it obeys the same enqueue rules as the worker queue:

* Inserts happen in the caller's transaction (no commit here).
* Enqueue is idempotent per the partial unique nonterminal
  ``(target_document_id, kind)`` index: an existing nonterminal job
  for the same target/kind is returned, never duplicated.
* ``cancel_job`` only cancels nonterminal jobs and sets ``finished_at``.

The API adapter and worker share canonical enqueue semantics. Worker
claims and fenced publication are handled by ``JobQueueStore``.

Reconciliation hooks
---------------------------
``find_awaiting_upload_jobs`` returns upload-stalled jobs oldest-first
so the worker's reconciliation pass can queue complete files (size +
fingerprint match) and fail abandoned partials (DEL/UPL-05/06).
``find_live_documents_for_project`` enumerates documents for project
cleanup.  These scan *live* rows only; tombstone handling is explicit
via ``include_deleted`` on the owned-lookup helpers in
:mod:`app.repositories.projects`.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Document, ProcessingJob
from app.db.queries import get_owned_project as _query_owned_project
from app.jobs.queue import enqueue_job as enqueue_durable_job
from app.schemas.common import ApiError, ErrorCode, decode_cursor, encode_cursor
from app.schemas.documents import Document as DocumentDto
from app.schemas.jobs import ProcessingJob as ProcessingJobDto
from app.services.storage import make_resource_snapshot

__all__ = [
    "AlreadyDeletingError",
    "DirectJobQueue",
    "DocumentConflictError",
    "InvalidRetryError",
    "ProcessingInProgressError",
    "confirm_upload_completion",
    "document_to_dto",
    "enqueue_document_delete",
    "find_awaiting_upload_jobs",
    "get_document_by_upload_request",
    "get_job_queue",
    "job_to_dto",
    "list_live_documents_for_project",
    "list_owned_documents",
    "nonterminal_process_job",
    "prepare_document_retry",
    "reserve_upload",
    "tombstone_document",
]


# ---------------------------------------------------------------------------
# DTO conversion
# ---------------------------------------------------------------------------


def document_to_dto(document: Document) -> DocumentDto:
    return DocumentDto.model_validate(document)


def job_to_dto(job: ProcessingJob) -> ProcessingJobDto:
    return ProcessingJobDto.model_validate(job)


# ---------------------------------------------------------------------------
# Domain errors (repositories raise; handlers map to HTTP)
# ---------------------------------------------------------------------------


class DocumentConflictError(Exception):
    """Same idempotency key with different content (HTTP 409)."""

    def __init__(self, *, document: Document, message: str = "duplicate_request_conflict") -> None:
        super().__init__(message)
        self.document = document


class InvalidRetryError(Exception):
    """Retry requested for an ineligible document (HTTP 409)."""


class ProcessingInProgressError(Exception):
    """Delete/retry requested while processing is active (HTTP 409)."""


class AlreadyDeletingError(Exception):
    """Second delete of an already-tombstoned resource (HTTP 409)."""


def _raise_api(status_code: int, code: ErrorCode, message: str, **ids: Any) -> None:
    detail = ApiError(code=code, message=message, **ids).model_dump(
        by_alias=True, mode="json"
    )
    raise HTTPException(status_code=status_code, detail=detail)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Direct queue (default JobQueue implementation; A4 replaces at wiring)
# ---------------------------------------------------------------------------


class DirectJobQueue:
    """Protocol-compatible adapter for the canonical durable job queue.

    API routes use the request transaction, while worker operations use
    :class:`app.jobs.queue.JobQueueStore`; both now share the same
    idempotent enqueue implementation.
    """

    _NONTERMINAL = ("awaiting_upload", "queued", "running", "retry_wait")

    def enqueue_job(
        self,
        session: Session,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        target_document_id: UUID,
        document_id: UUID | None,
        kind: str,
        target_epoch: int,
        resource_snapshot: dict[str, Any],
        available_at: datetime | None = None,
        max_attempts: int = 3,
        status: str = "awaiting_upload",
        stage: str | None = "uploading",
    ) -> ProcessingJob:
        """Idempotent insert per the nonterminal (target, kind) index.

        ``status``/``stage`` default to the upload path
        (``awaiting_upload``/``uploading``) and are optional extras
        beyond the frozen Protocol (callers may instead set these
        attributes on the returned row after the call).  Enqueue
        insert uses a SAVEPOINT so a concurrent duplicate losing the
        race returns the winner without aborting the caller's
        transaction.
        """
        job = enqueue_durable_job(
            session,
            owner_user_id=owner_user_id,
            project_id=project_id,
            target_document_id=target_document_id,
            document_id=document_id,
            kind=str(kind),
            target_epoch=target_epoch,
            resource_snapshot=resource_snapshot,
            available_at=available_at,
            max_attempts=max_attempts,
            status=status,
            stage=stage,
        )
        return job

    def cancel_job(self, session: Session, *, job_id: UUID, reason: str) -> bool:
        """Cancel one nonterminal job; False when already terminal/missing."""
        job = session.get(ProcessingJob, job_id)
        if job is None or job.status not in self._NONTERMINAL:
            return False
        job.status = "cancelled"
        job.finished_at = _utcnow()
        if job.last_error_code is None:
            job.last_error_code = "cancelled"
            job.last_error_message = reason[:1000] if reason else "cancelled"
        session.flush()
        return True

    def cancel_process_jobs_for_document(
        self, session: Session, *, document_id: UUID, reason: str
    ) -> list[ProcessingJob]:
        """Cancel every nonterminal ``process_document`` job for a document."""
        return cancel_process_jobs(session, document_id=document_id, reason=reason)


def cancel_process_jobs(
    session: Session, *, document_id: UUID, reason: str
) -> list[ProcessingJob]:
    """Cancel every nonterminal ``process_document`` job for a document.

    Standalone helper (not a ``JobQueue`` method) so retry/delete keep
    working when A4's queue replaces :class:`DirectJobQueue`.
    """
    jobs = list(
        session.execute(
            select(ProcessingJob).where(
                ProcessingJob.target_document_id == document_id,
                ProcessingJob.kind == "process_document",
                ProcessingJob.status.in_(
                    ("awaiting_upload", "queued", "running", "retry_wait")
                ),
            )
        ).scalars().all()
    )
    cancelled: list[ProcessingJob] = []
    for job in jobs:
        job.status = "cancelled"
        job.finished_at = _utcnow()
        if job.last_error_code is None:
            job.last_error_code = "cancelled"
            job.last_error_message = reason[:1000]
        cancelled.append(job)
    if cancelled:
        session.flush()
    return cancelled


def get_job_queue() -> DirectJobQueue:
    """FastAPI factory for the default queue (A0 overrides with A4's queue)."""
    return DirectJobQueue()


# ---------------------------------------------------------------------------
# Owned lookups (local copy; central 404 wrappers live in projects repo)
# ---------------------------------------------------------------------------


def _get_owned_project(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    include_deleted: bool = False,
):
    return _query_owned_project(
        session, user_id=user_id, project_id=project_id, include_deleted=include_deleted
    )


def get_document_by_upload_request(
    session: Session, *, project_id: UUID, upload_request_id: UUID
) -> Document | None:
    """Find the document reserved for one idempotency key in one project."""
    return session.scalar(
        select(Document).where(
            Document.project_id == project_id,
            Document.upload_request_id == upload_request_id,
        )
    )


def _latest_process_job(
    session: Session, *, target_document_id: UUID
) -> ProcessingJob | None:
    return session.scalar(
        select(ProcessingJob)
        .where(
            ProcessingJob.target_document_id == target_document_id,
            ProcessingJob.kind == "process_document",
        )
        .order_by(ProcessingJob.created_at.desc(), ProcessingJob.id.desc())
        .limit(1)
    )


# ---------------------------------------------------------------------------
# Upload reservation + finalize (§5.1)
# ---------------------------------------------------------------------------


def reserve_upload(
    session: Session,
    *,
    owner_user_id: UUID,
    project_id: UUID,
    document_id: UUID,
    appwrite_file_id: str,
    file_name: str,
    file_size: int,
    mime_type: str,
    upload_request_id: UUID,
    content_sha256: str,
    bucket_id: str,
    job_queue: DirectJobQueue,
) -> tuple[Document, ProcessingJob, bool]:
    """Create Pending + awaiting_upload atomically, or return the duplicate.

    Returns ``(document, job, is_duplicate)``.  When ``is_duplicate``
    is true the caller must verify ``content_sha256`` against the
    stored fingerprint and return the original pair without touching
    storage (never resets a running/completed job).  A fingerprint
    mismatch raises :class:`DocumentConflictError` (``409``).
    """
    existing = get_document_by_upload_request(
        session, project_id=project_id, upload_request_id=upload_request_id
    )
    if existing is not None:
        if existing.content_sha256 is not None and existing.content_sha256 != content_sha256:
            raise DocumentConflictError(document=existing)
        if existing.content_sha256 is None and existing.file_size not in (None, file_size):
            raise DocumentConflictError(document=existing)
        job = _latest_process_job(session, target_document_id=existing.id)
        if job is None:
            # Should not happen (every reservation creates a job), but
            # never leave a duplicate without its job: recreate the
            # awaiting_upload reservation for the existing document.
            job = job_queue.enqueue_job(
                session,
                owner_user_id=owner_user_id,
                project_id=project_id,
                target_document_id=existing.id,
                document_id=existing.id,
                kind="process_document",
                target_epoch=existing.processing_epoch,
                resource_snapshot=make_resource_snapshot(
                    bucket_id=bucket_id,
                    file_id=existing.appwrite_file_id,
                    file_name=existing.file_name,
                    file_size=int(existing.file_size or file_size),
                    content_sha256=content_sha256,
                ),
            )
            if job.status not in ("awaiting_upload", "queued", "running", "retry_wait"):
                job.status = "awaiting_upload"
            job.stage = "uploading"
        return existing, job, True

    document = Document(
        id=document_id,
        project_id=project_id,
        file_name=file_name,
        appwrite_file_id=appwrite_file_id,
        file_size=file_size,
        mime_type=mime_type,
        status="Pending",
        upload_request_id=upload_request_id,
        content_sha256=content_sha256,
        processing_epoch=0,
    )
    try:
        with session.begin_nested():
            session.add(document)
            session.flush()
    except IntegrityError:
        # Lost a concurrent reservation race: return the winner
        # (SAVEPOINT rolls back only this insert).
        winner = get_document_by_upload_request(
            session, project_id=project_id, upload_request_id=upload_request_id
        )
        if winner is not None:
            winner_job = _latest_process_job(session, target_document_id=winner.id)
            if winner_job is not None:
                if winner.content_sha256 is not None and winner.content_sha256 != content_sha256:
                    raise DocumentConflictError(document=winner)
                return winner, winner_job, True
        raise DocumentConflictError(document=winner) if winner is not None else ValueError(
            "document reservation failed"
        )

    job = job_queue.enqueue_job(
        session,
        owner_user_id=owner_user_id,
        project_id=project_id,
        target_document_id=document.id,
        document_id=document.id,
        kind="process_document",
        target_epoch=document.processing_epoch,
        resource_snapshot=make_resource_snapshot(
            bucket_id=bucket_id,
            file_id=appwrite_file_id,
            file_name=file_name,
            file_size=file_size,
            content_sha256=content_sha256,
        ),
    )
    # Normalize to the upload state regardless of the queue's default
    # for a fresh row (Protocol-only enqueue guarantees this).
    if job.status not in ("awaiting_upload", "queued", "running", "retry_wait"):
        job.status = "awaiting_upload"
    job.stage = "uploading"
    session.flush()
    return document, job, False


def confirm_upload_completion(
    session: Session,
    *,
    document: Document,
    job: ProcessingJob,
) -> bool:
    """Conditionally queue a storage-complete upload.

    Sets ``document.upload_completed_at`` and moves the job
    ``awaiting_upload -> queued`` *only* while the job is still
    ``awaiting_upload``.  A job already ``queued`` (reconciliation
    race) or terminal is left untouched.  Returns True when this call
    performed the transition.
    """
    if job.status != "awaiting_upload":
        return False
    now = _utcnow()
    if document.upload_completed_at is None:
        document.upload_completed_at = now
    job.status = "queued"
    job.stage = None
    session.flush()
    return True


def prepare_document_retry(
    session: Session,
    *,
    document: Document,
    bucket_id: str,
    job_queue: DirectJobQueue,
) -> tuple[Document, ProcessingJob]:
    """Create a fresh queued job for a Failed document and advance its epoch.

    Caller must have verified eligibility (document ``Failed`` + no
    nonterminal job).  The failed history stays terminal; attempt
    history is preserved by leaving old rows untouched.
    """
    # Fresh snapshot from the live document (file already in storage).
    # Enqueue uses Protocol-only args so any JobQueue implementation
    # works; the queued state is set on the returned row below.
    cancel_process_jobs(session, document_id=document.id, reason="retry epoch advance")
    document.processing_epoch = int(document.processing_epoch or 0) + 1
    document.status = "Pending"
    document.processing_error = None
    if document.upload_completed_at is None:
        document.upload_completed_at = _utcnow()
    session.flush()
    job = job_queue.enqueue_job(
        session,
        owner_user_id=_job_owner(session, document),
        project_id=document.project_id,
        target_document_id=document.id,
        document_id=document.id,
        kind="process_document",
        target_epoch=document.processing_epoch,
        resource_snapshot=make_resource_snapshot(
            bucket_id=bucket_id,
            file_id=document.appwrite_file_id,
            file_name=document.file_name,
            file_size=int(document.file_size or 0),
            content_sha256=str(document.content_sha256 or ""),
        ),
    )
    # Force the retry state regardless of the queue's default for a
    # fresh row (no nonterminal exists by eligibility, so this never
    # downgrades an active job).
    if job.status not in ("queued",):
        job.status = "queued"
    job.stage = None
    session.flush()
    return document, job


def _job_owner(session: Session, document: Document) -> UUID:
    """Resolve ``owner_user_id`` from the document's project row.

    Works for live and tombstoned parents (no deleted filter) so
    retry/delete snapshots stay owner-correct during cleanup.
    """
    from app.db.models import Project as _Project

    owner = session.scalar(
        select(_Project.user_id).where(_Project.id == document.project_id)
    )
    if owner is None:
        raise ValueError(f"project not found for document {document.id}")
    return owner


def tombstone_document(
    session: Session, document: Document, *, now: datetime | None = None
) -> Document:
    if document.deleted_at is None:
        document.deleted_at = now or _utcnow()
    session.flush()
    return document


def enqueue_document_delete(
    session: Session,
    *,
    document: Document,
    bucket_id: str,
    job_queue: DirectJobQueue,
) -> ProcessingJob:
    """Cancel processing + enqueue the ``delete_document`` cleanup job."""
    cancel_process_jobs(session, document_id=document.id, reason="document deleted")
    snapshot = make_resource_snapshot(
        bucket_id=bucket_id,
        file_id=document.appwrite_file_id,
        file_name=document.file_name,
        file_size=int(document.file_size or 0),
        content_sha256=str(document.content_sha256 or ""),
        active_index_version=(
            str(document.active_index_version)
            if document.active_index_version is not None
            else None
        ),
    )
    delete_job = job_queue.enqueue_job(
        session,
        owner_user_id=_job_owner(session, document),
        project_id=document.project_id,
        target_document_id=document.id,
        document_id=document.id,
        kind="delete_document",
        target_epoch=int(document.processing_epoch or 0),
        resource_snapshot=snapshot,
    )
    # Normalize to the cleanup state (Protocol-only enqueue args).
    if delete_job.kind == "delete_document":
        delete_job.status = "queued"
        delete_job.stage = "deleting"
    session.flush()
    return delete_job


# ---------------------------------------------------------------------------
# Listing (keyset pagination, (created_at, id) DESC)
# ---------------------------------------------------------------------------


def _parse_doc_cursor(cursor: str) -> tuple[datetime, UUID]:
    try:
        payload = decode_cursor(cursor)
        created_raw = payload.get("c")
        id_raw = payload.get("i")
        if not isinstance(created_raw, str) or not isinstance(id_raw, str):
            raise ValueError("malformed cursor payload")
        created_at = datetime.fromisoformat(created_raw)
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        document_id = UUID(id_raw)
    except (ValueError, TypeError) as exc:
        _raise_api(
            422, ErrorCode.VALIDATION_ERROR, "Invalid pagination cursor."
        )
        raise exc  # pragma: no cover
    return created_at, document_id


def list_owned_documents(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    cursor: str | None,
    limit: int,
) -> tuple[list[Document], str | None]:
    """Live documents of an owned project, newest-first, keyset-paginated.

    Callers verify project ownership first (this helper assumes it).
    Malformed cursors raise ``422 validation_error``.
    """
    if limit < 1 or limit > 200:
        _raise_api(
            422, ErrorCode.VALIDATION_ERROR, "limit must be between 1 and 200."
        )
    # Ownership guard (documents -> project -> user) via live project.
    project = _get_owned_project(
        session, user_id=user_id, project_id=project_id, include_deleted=False
    )
    if project is None:
        _raise_api(
            404,
            ErrorCode.NOT_FOUND,
            "Project not found.",
            project_id=project_id,
        )

    statement = (
        select(Document)
        .where(
            Document.project_id == project_id,
            Document.deleted_at.is_(None),
        )
        .order_by(Document.created_at.desc(), Document.id.desc())
        .limit(limit + 1)
    )
    if cursor is not None:
        created_before, id_before = _parse_doc_cursor(cursor)
        statement = statement.where(
            or_(
                Document.created_at < created_before,
                (Document.created_at == created_before) & (Document.id < id_before),
            )
        )
    rows = list(session.execute(statement).scalars().all())
    next_cursor: str | None = None
    if len(rows) > limit:
        rows = rows[:limit]
        last = rows[-1]
        next_cursor = encode_cursor(
            {"c": last.created_at.isoformat(), "i": str(last.id)}
        )
    return rows, next_cursor


def list_live_documents_for_project(
    session: Session, *, project_id: UUID
) -> list[Document]:
    """All live documents of a project (cleanup enumeration)."""
    return list(
        session.execute(
            select(Document)
            .where(
                Document.project_id == project_id,
                Document.deleted_at.is_(None),
            )
            .order_by(Document.created_at.asc(), Document.id.asc())
        ).scalars().all()
    )


# ---------------------------------------------------------------------------
# Reconciliation hooks for the A4 worker
# ---------------------------------------------------------------------------


def find_awaiting_upload_jobs(
    session: Session,
    *,
    cutoff: datetime,
    limit: int = 100,
) -> list[ProcessingJob]:
    """Stalled ``awaiting_upload`` jobs older than ``cutoff``, oldest-first.

    The worker's reconciliation pass inspects each candidate's storage
    completion (size + fingerprint via the snapshot) and either queues
    complete files (``confirm_upload_completion`` semantics) or fails
    abandoned partials with a terminal ``failed`` job.  Ordering is
    stable (``created_at ASC, id ASC``) so overlapping workers make
    progress without starvation; the partial unique nonterminal index
    prevents double-queuing.
    """
    if cutoff.tzinfo is None:
        cutoff = cutoff.replace(tzinfo=timezone.utc)
    return list(
        session.execute(
            select(ProcessingJob)
            .where(
                ProcessingJob.status == "awaiting_upload",
                ProcessingJob.created_at < cutoff,
            )
            .order_by(ProcessingJob.created_at.asc(), ProcessingJob.id.asc())
            .limit(limit)
        ).scalars().all()
    )


def nonterminal_process_job(
    session: Session, *, target_document_id: UUID
) -> ProcessingJob | None:
    """Any nonterminal ``process_document`` job for a document, if present."""
    return session.scalar(
        select(ProcessingJob).where(
            ProcessingJob.target_document_id == target_document_id,
            ProcessingJob.kind == "process_document",
            ProcessingJob.status.in_(
                ("awaiting_upload", "queued", "running", "retry_wait")
            ),
        )
    )
