"""Transactional PostgreSQL job queue and worker transaction facade.

Implements the frozen ``JobQueue`` protocol from
``app.schemas.services`` plus the reconciliation read/write helpers the
worker loop needs. This module supplies request-side operations (enqueue /
status / cancel) and the interface the worker uses (claim / lease /
progress / complete / fail).

## Lease / fencing contract

* Claims run in one short transaction with ``SELECT ... FOR UPDATE
  SKIP LOCKED`` over due ``queued`` / ``retry_wait`` jobs.  The fencing
  ``lease_token`` and ``attempt_count`` are incremented *before* the
  lock is released, and every processing attempt gets a fresh
  ``index_version`` namespace (recorded in the job row; the previous
  version is appended to ``resource_snapshot["superseded_index_versions"]``
  so the grace-period sweep can clean it up).
* Heartbeats and every later write are compare-and-set updates guarded
  by ``(lease_owner, lease_token, unexpired lease)`` and
  ``status = 'running'``.  A stale holder's write touches zero rows and
  returns ``False`` -- it can never move the job, the document status,
  or the active index pointer.  Expired leases are revoked by
  :func:`expire_lease` (requeue with backoff, or terminal ``failed``
  when attempts are exhausted); claims never steal a live lease.
* Publication (:func:`complete_job`) is a *single* transaction that
  re-verifies the running job, the unexpired lease/token, the expected
  document epoch, and the live document/project before setting the
  document ``Completed`` with ``active_index_version`` /
  ``chunk_count`` / ``processed_at`` and the job ``succeeded``.
  Retry/deletion invalidates prior claims by advancing
  ``processing_epoch`` and by :func:`cancel_job` bumping
  ``lease_token``.  Re-completing an already-published version is an
  idempotent no-op (lost commit acknowledgment, JOB-09).
* ``chunk_count`` comes from the caller's ``chunk_count`` argument, or
  from ``progress_total`` when omitted -- processors must therefore
  record ``progress_total = number of chunks`` before completing.

## Resource snapshot keys

``resource_snapshot`` is a JSON object. The worker reads these keys:

* process jobs: ``bucket_id``, ``file_id``, ``expected_size_bytes``
  (int), ``expected_sha256`` (hex string), ``file_name``;
* delete jobs: ``bucket_id``, ``file_id``, ``index_versions`` (list of
  version UUID strings), ``active_index_version`` (string or null);
* The queue additionally maintains ``superseded_index_versions`` (list of
  strings) on process jobs across attempts.

## Concurrency notes

Two workers claiming concurrently can never claim the same row
(``SKIP LOCKED`` grades over rows in priority order).  All functions
here take an open ``Session`` and run in the caller's transaction --
callers must never hold that transaction across a provider call.
:class:`JobQueueStore` wraps these functions so the worker gets one
short transaction per operation.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session



from app.db.base import utcnow  # noqa: E402
from app.db.models import (  # noqa: E402
    Document,
    ProcessingJob,
    Project,
)
from app.jobs.errors import (  # noqa: E402
    ERROR_LEASE_EXPIRED,
    compute_backoff_seconds,
)
from app.rag.indexing import COLLECTION_NAME  # noqa: E402
from app.schemas.services import JobClaim  # noqa: E402

KIND_PROCESS = "process_document"
KIND_DELETE = "delete_document"

STATUS_AWAITING_UPLOAD = "awaiting_upload"
STATUS_QUEUED = "queued"
STATUS_RUNNING = "running"
STATUS_RETRY_WAIT = "retry_wait"
STATUS_SUCCEEDED = "succeeded"
STATUS_FAILED = "failed"
STATUS_CANCELLED = "cancelled"
TERMINAL_STATUSES = (STATUS_SUCCEEDED, STATUS_FAILED, STATUS_CANCELLED)
CANCELLED_MARKER = "cancelled"

STAGE_EXTRACTING = "extracting"
STAGE_DELETING = "deleting"

DEFAULT_BACKOFF_BASE_SECONDS = 5
DEFAULT_BACKOFF_CAP_SECONDS = 3600


# ---------------------------------------------------------------------------
# Context / candidate payloads
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class JobContext:
    """Everything the worker needs for one job, loaded in a read tx."""

    job_id: UUID
    kind: str
    status: str
    target_document_id: UUID
    target_epoch: int
    owner_user_id: UUID
    project_id: UUID
    document_id: UUID | None
    attempt_count: int
    max_attempts: int
    lease_token: int | None
    index_version: UUID | None
    resource_snapshot: dict[str, Any] = field(default_factory=dict)
    # From the snapshot (A3-produced; treated as trusted server data):
    bucket_id: str | None = None
    file_id: str | None = None
    expected_size_bytes: int | None = None
    expected_sha256: str | None = None
    file_name: str | None = None
    # From the live document row when it still exists:
    doc_file_name: str | None = None
    doc_appwrite_file_id: str | None = None
    doc_file_size: int | None = None
    doc_content_sha256: str | None = None
    doc_processing_epoch: int | None = None
    doc_status: str | None = None
    doc_deleted: bool = False
    doc_exists: bool = False
    doc_active_index_version: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def storage_file_id(self) -> str | None:
        return self.file_id or self.doc_appwrite_file_id

    @property
    def storage_bucket_id(self) -> str | None:
        return self.bucket_id

    @property
    def storage_file_name(self) -> str | None:
        return self.file_name or self.doc_file_name


@dataclass(frozen=True)
class SweepCandidate:
    """One published/attempted index namespace eligible for sweeping."""

    target_document_id: UUID
    project_id: UUID
    owner_user_id: UUID
    index_version: UUID
    job_id: UUID


# ---------------------------------------------------------------------------
# Pure fencing predicates (shared by the PG paths and no-DB tests)
# ---------------------------------------------------------------------------


def lease_is_current(
    *,
    status: str | None,
    lease_owner: str | None,
    lease_token: int | None,
    lease_expires_at: datetime | None,
    worker_id: str,
    token: int,
    now: datetime,
) -> bool:
    """True iff the caller's claim is the live, unexpired one."""
    return (
        status == STATUS_RUNNING
        and lease_owner == worker_id
        and lease_token == token
        and lease_expires_at is not None
        and lease_expires_at > now
    )


def evaluate_publication(
    job: Any,
    document: Any,
    project: Any,
    *,
    worker_id: str,
    lease_token: int,
    now: datetime,
) -> tuple[bool, str]:
    """Fenced-publication check for a ``process_document`` job.

    Returns ``(allowed, reason)``; ``reason`` is a stable token for
    logs/metrics (``ok``, ``lease_lost``, ``epoch_mismatch``,
    ``document_gone``, ``project_gone``, ``missing_index_version``,
    ``already_terminal``, ``already_published``).  Operates on anything
    with the right attributes (ORM rows or test doubles).
    ``document``/``project`` may be ``None`` (hard-deleted rows).
    """
    if job.status == STATUS_SUCCEEDED:
        if document is not None and document.active_index_version == job.index_version:
            return True, "already_published"
        return False, "already_terminal"
    if job.status != STATUS_RUNNING:
        return False, "already_terminal"
    if not lease_is_current(
        status=job.status,
        lease_owner=job.lease_owner,
        lease_token=job.lease_token,
        lease_expires_at=job.lease_expires_at,
        worker_id=worker_id,
        token=lease_token,
        now=now,
    ):
        return False, "lease_lost"
    if job.index_version is None:
        return False, "missing_index_version"
    if document is None or getattr(document, "deleted_at", None) is not None:
        return False, "document_gone"
    if project is not None and project.deleted_at is not None:
        return False, "project_gone"
    if document.processing_epoch != job.target_epoch:
        return False, "epoch_mismatch"
    return True, "ok"


def _clear_lease(job: ProcessingJob) -> None:
    # Keep lease_token: fencing tokens must be monotonic per job.  A
    # reclaimed job always gets a strictly larger token, so a zombie
    # holder's token can never match again.  Owner/expiry are cleared
    # so the "current claim" checks (which require a live expiry)
    # fail until the next claim.
    job.lease_owner = None
    job.lease_expires_at = None


def _snapshot_get(snapshot: Mapping[str, Any] | None, key: str, default: Any = None) -> Any:
    if isinstance(snapshot, Mapping):
        return snapshot.get(key, default)
    return default


# ---------------------------------------------------------------------------
# Enqueue (A3-facing)
# ---------------------------------------------------------------------------


def enqueue_job(
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
    status: str = STATUS_QUEUED,
    stage: str | None = None,
) -> ProcessingJob:
    """Insert or return one active job row in the caller's transaction.

    ``status`` is ``awaiting_upload`` for the upload reservation flow
    (A3 flips it to ``queued`` after storage completion) and ``queued``
    for retry/cleanup jobs.  The partial unique nonterminal
    ``(target_document_id, kind)`` index enforces at most one active
    job per target/kind. Concurrent duplicate enqueues return the
    winning active job without aborting the caller's transaction.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")
    if not isinstance(resource_snapshot, dict):
        raise ValueError("resource_snapshot must be a JSON object")
    job = ProcessingJob(
        document_id=document_id,
        owner_user_id=owner_user_id,
        project_id=project_id,
        target_document_id=target_document_id,
        resource_snapshot=dict(resource_snapshot),
        target_epoch=target_epoch,
        kind=kind,
        status=status,
        stage=stage,
        attempt_count=0,
        max_attempts=max_attempts,
        available_at=available_at or utcnow(),
    )
    existing = find_nonterminal_job(
        session, target_document_id=target_document_id, kind=kind
    )
    if existing is not None:
        return existing
    try:
        with session.begin_nested():
            session.add(job)
            session.flush()
    except IntegrityError:
        winner = find_nonterminal_job(
            session, target_document_id=target_document_id, kind=kind
        )
        if winner is not None:
            return winner
        raise
    return job


def find_nonterminal_job(
    session: Session, *, target_document_id: UUID, kind: str
) -> ProcessingJob | None:
    """Fetch the active job for a target/kind, if one exists."""
    return session.scalar(
        select(ProcessingJob).where(
            ProcessingJob.target_document_id == target_document_id,
            ProcessingJob.kind == kind,
            ProcessingJob.status.in_(
                (STATUS_AWAITING_UPLOAD, STATUS_QUEUED, STATUS_RUNNING, STATUS_RETRY_WAIT)
            ),
        )
    )


# ---------------------------------------------------------------------------
# Claim / lease / progress
# ---------------------------------------------------------------------------


def claim_next_jobs(
    session: Session, *, worker_id: str, limit: int, lease_seconds: int
) -> list[JobClaim]:
    """Claim up to ``limit`` due jobs in the caller's transaction.

    Due = ``queued``/``retry_wait`` with ``available_at <= now`` and
    attempts remaining.  Rows are locked ``FOR UPDATE SKIP LOCKED`` in
    ``(available_at, created_at)`` order; each claimed row gets its
    fencing token + attempt bumped, a fresh ``index_version`` (process
    jobs), and ``status = running`` before the lock is released.
    Jobs whose document is tombstoned/hard-deleted are cancelled in
    place (never claimed), except ``delete_document`` cleanup jobs: they
    must run *after* tombstoning to remove the private PDF and index
    versions.  The caller must commit immediately -- the claim is the
    trigger, and all provider work happens after commit.
    """
    if limit < 1:
        return []
    now = utcnow()
    rows = session.scalars(
        select(ProcessingJob)
        .where(
            ProcessingJob.status.in_((STATUS_QUEUED, STATUS_RETRY_WAIT)),
            ProcessingJob.available_at <= now,
            ProcessingJob.attempt_count < ProcessingJob.max_attempts,
        )
        .order_by(ProcessingJob.available_at, ProcessingJob.created_at)
        .limit(limit)
        .with_for_update(skip_locked=True)
    ).all()
    claims: list[JobClaim] = []
    for job in rows:
        document = (
            session.get(Document, job.target_document_id) if job.target_document_id else None
        )
        if document is None or (
            document.deleted_at is not None and job.kind != KIND_DELETE
        ):
            # Never claim work for a doc that can no longer be published.
            # delete_document is the exception: its cleanup runs after the
            # tombstone, so cancelling it would orphan the PDF and vectors.
            job.status = STATUS_CANCELLED
            job.finished_at = now
            job.last_error_code = CANCELLED_MARKER
            job.last_error_message = "document was deleted before the job was claimed"
            _clear_lease(job)
            continue
        job.attempt_count = (job.attempt_count or 0) + 1
        job.lease_token = (job.lease_token or 0) + 1
        job.lease_owner = worker_id
        job.lease_expires_at = now + timedelta(seconds=lease_seconds)
        job.status = STATUS_RUNNING
        job.stage = STAGE_DELETING if job.kind == KIND_DELETE else STAGE_EXTRACTING
        job.finished_at = None
        if job.kind == KIND_PROCESS:
            if job.index_version is not None:
                snapshot = dict(job.resource_snapshot or {})
                superseded = list(snapshot.get("superseded_index_versions") or [])
                superseded.append(str(job.index_version))
                snapshot["superseded_index_versions"] = superseded
                job.resource_snapshot = snapshot
            job.index_version = uuid4()
            if document.processing_epoch == job.target_epoch:
                document.status = "Processing"
                document.processing_error = None
        claims.append(
            JobClaim(
                job_id=job.id,
                kind=job.kind,
                target_document_id=job.target_document_id,
                target_epoch=job.target_epoch,
                index_version=job.index_version,
                lease_token=int(job.lease_token or 0),
                lease_expires_at=job.lease_expires_at,
            )
        )
    session.flush()
    return claims


def renew_job_lease(
    session: Session,
    *,
    job_id: UUID,
    lease_token: int,
    worker_id: str,
    lease_seconds: int,
) -> bool:
    """Compare-and-set heartbeat.  False when the claim is no longer ours."""
    now = utcnow()
    result = session.execute(
        update(ProcessingJob)
        .where(
            ProcessingJob.id == job_id,
            ProcessingJob.status == STATUS_RUNNING,
            ProcessingJob.lease_owner == worker_id,
            ProcessingJob.lease_token == lease_token,
            ProcessingJob.lease_expires_at > now,
        )
        .values(lease_expires_at=now + timedelta(seconds=lease_seconds))
    )
    return bool(result.rowcount)


def update_progress(
    session: Session,
    *,
    job_id: UUID,
    lease_token: int,
    worker_id: str,
    stage: str | None = None,
    progress_current: int | None = None,
    progress_total: int | None = None,
) -> bool:
    """Guarded stage/progress update (same fencing guard as renewal)."""
    now = utcnow()
    values: dict[str, Any] = {}
    if stage is not None:
        values["stage"] = stage
    if progress_current is not None:
        values["progress_current"] = progress_current
    if progress_total is not None:
        values["progress_total"] = progress_total
    if not values:
        return True
    result = session.execute(
        update(ProcessingJob)
        .where(
            ProcessingJob.id == job_id,
            ProcessingJob.status == STATUS_RUNNING,
            ProcessingJob.lease_owner == worker_id,
            ProcessingJob.lease_token == lease_token,
            ProcessingJob.lease_expires_at > now,
        )
        .values(**values)
    )
    return bool(result.rowcount)


# ---------------------------------------------------------------------------
# Completion (fenced publication) / failure / cancellation
# ---------------------------------------------------------------------------


def complete_job(
    session: Session,
    *,
    job_id: UUID,
    lease_token: int,
    worker_id: str,
    chunk_count: int | None = None,
) -> bool:
    """Publish success in the caller's transaction after fencing checks.

    For ``process_document`` this is the atomic publication: verify the
    running job + unexpired lease/token + expected epoch + live
    document/project, then set the document ``Completed`` (active
    version, chunk count, processed time) and the job ``succeeded``.
    Returns ``False`` -- writing nothing -- when the claim is stale.
    Re-completing an already-published version returns ``True`` as a
    no-op (lost commit acknowledgment).  For ``delete_document`` the
    job is marked ``succeeded`` without touching the document row (the
    tombstone/hard-delete ordering belongs to A3).
    """
    now = utcnow()
    job = session.scalar(
        select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()
    )
    if job is None:
        return False
    if job.status == STATUS_SUCCEEDED:
        if job.kind != KIND_PROCESS:
            return True
        document = session.get(Document, job.target_document_id)
        return bool(document is not None and document.active_index_version == job.index_version)
    document = session.get(Document, job.target_document_id)
    project = session.get(Project, job.project_id)
    if job.kind == KIND_DELETE:
        # Cleanup jobs intentionally run *after* the tombstone, so only
        # the live lease/token fences completion.  Document/project
        # liveness and the process-job publication checks do not apply.
        if not lease_is_current(
            status=job.status,
            lease_owner=job.lease_owner,
            lease_token=job.lease_token,
            lease_expires_at=job.lease_expires_at,
            worker_id=worker_id,
            token=lease_token,
            now=now,
        ):
            return False
    else:
        allowed, _reason = evaluate_publication(
            job, document, project, worker_id=worker_id, lease_token=lease_token, now=now
        )
        if not allowed:
            return False
    if job.kind == KIND_PROCESS:
        count = chunk_count if chunk_count is not None else job.progress_total
        if count is None:
            raise ValueError(
                "complete_job needs chunk_count (or progress_total) for process jobs"
            )
        assert document is not None  # evaluate_publication guarantees it
        document.status = "Completed"
        document.active_index_version = job.index_version
        document.chunk_count = int(count)
        document.processed_at = now
        document.processing_error = None
        document.chroma_collection = COLLECTION_NAME
        document.chroma_document_id = str(job.index_version)
    job.status = STATUS_SUCCEEDED
    job.stage = None
    job.finished_at = now
    job.last_error_code = None
    job.last_error_message = None
    _clear_lease(job)
    session.flush()
    return True


def fail_job(
    session: Session,
    *,
    job_id: UUID,
    lease_token: int,
    worker_id: str,
    error_code: str,
    error_message: str,
    retryable: bool,
    backoff_base_seconds: int = DEFAULT_BACKOFF_BASE_SECONDS,
    backoff_cap_seconds: int = DEFAULT_BACKOFF_CAP_SECONDS,
) -> bool:
    """Move to ``retry_wait`` (bounded backoff) or terminal ``failed``.

    Guarded by the live lease; returns ``False`` (writing nothing) for
    a stale holder.  On terminal failure of a process job the document
    is marked ``Failed`` with the safe error summary -- but only when
    the document is still live and its epoch still matches, so a stale
    worker can never clobber a newer epoch's ``Pending`` state.
    """
    now = utcnow()
    job = session.scalar(
        select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()
    )
    if job is None or not lease_is_current(
        status=job.status,
        lease_owner=job.lease_owner,
        lease_token=job.lease_token,
        lease_expires_at=job.lease_expires_at,
        worker_id=worker_id,
        token=lease_token,
        now=now,
    ):
        return False
    job.last_error_code = error_code
    job.last_error_message = error_message
    will_retry = retryable and (job.attempt_count or 0) < (job.max_attempts or 1)
    if will_retry:
        job.status = STATUS_RETRY_WAIT
        job.stage = None
        job.available_at = now + timedelta(
            seconds=compute_backoff_seconds(
                job.attempt_count or 1,
                base_seconds=backoff_base_seconds,
                cap_seconds=backoff_cap_seconds,
                jitter_seed=str(job.id),
            )
        )
        _clear_lease(job)
    else:
        job.status = STATUS_FAILED
        job.finished_at = now
        _clear_lease(job)
        if job.kind == KIND_PROCESS:
            document = session.get(Document, job.target_document_id)
            if (
                document is not None
                and document.deleted_at is None
                and document.processing_epoch == job.target_epoch
            ):
                document.status = "Failed"
                document.processing_error = f"{error_code}: {error_message}"
    session.flush()
    return True


def cancel_job(session: Session, *, job_id: UUID, reason: str) -> bool:
    """Cancel a nonterminal job (deletion/retry invalidation).

    Bumps ``lease_token`` so any in-flight worker holding the previous
    token is fenced out, then marks the job ``cancelled``.  Returns
    ``False`` when the job is already terminal or missing.
    """
    job = session.scalar(
        select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()
    )
    if job is None or job.status in TERMINAL_STATUSES:
        return False
    job.lease_token = (job.lease_token or 0) + 1
    job.status = STATUS_CANCELLED
    job.finished_at = utcnow()
    job.last_error_code = CANCELLED_MARKER
    job.last_error_message = reason
    _clear_lease(job)
    session.flush()
    return True


# ---------------------------------------------------------------------------
# Reconciliation reads/writes
# ---------------------------------------------------------------------------


def load_job_context(session: Session, job_id: UUID) -> JobContext | None:
    """Load a job plus its snapshot/document facts for the worker."""
    job = session.get(ProcessingJob, job_id)
    if job is None:
        return None
    document = session.get(Document, job.target_document_id)
    snapshot = dict(job.resource_snapshot or {})
    return JobContext(
        job_id=job.id,
        kind=job.kind,
        status=job.status,
        target_document_id=job.target_document_id,
        target_epoch=job.target_epoch,
        owner_user_id=job.owner_user_id,
        project_id=job.project_id,
        document_id=job.document_id,
        attempt_count=job.attempt_count or 0,
        max_attempts=job.max_attempts or 1,
        lease_token=job.lease_token,
        index_version=job.index_version,
        resource_snapshot=snapshot,
        bucket_id=_snapshot_get(snapshot, "bucket_id"),
        file_id=_snapshot_get(snapshot, "file_id"),
        expected_size_bytes=_snapshot_get(snapshot, "expected_size_bytes"),
        expected_sha256=_snapshot_get(snapshot, "expected_sha256"),
        file_name=_snapshot_get(snapshot, "file_name"),
        doc_file_name=document.file_name if document else None,
        doc_appwrite_file_id=document.appwrite_file_id if document else None,
        doc_file_size=document.file_size if document else None,
        doc_content_sha256=document.content_sha256 if document else None,
        doc_processing_epoch=document.processing_epoch if document else None,
        doc_status=document.status if document else None,
        doc_deleted=bool(document is not None and document.deleted_at is not None),
        doc_exists=document is not None,
        doc_active_index_version=document.active_index_version if document else None,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def find_expired_awaiting_upload(
    session: Session, *, cutoff: datetime, limit: int
) -> list[JobContext]:
    """Jobs still ``awaiting_upload`` past their TTL (reconciliation)."""
    rows = session.scalars(
        select(ProcessingJob)
        .where(
            ProcessingJob.status == STATUS_AWAITING_UPLOAD,
            ProcessingJob.created_at <= cutoff,
        )
        .order_by(ProcessingJob.created_at)
        .limit(limit)
        .with_for_update(skip_locked=True)
    ).all()
    contexts = []
    for row in rows:
        context = load_job_context(session, row.id)
        if context is not None:
            contexts.append(context)
    return contexts


def apply_awaiting_upload_outcome(
    session: Session,
    *,
    job_id: UUID,
    outcome: str,
    error_code: str | None = None,
    error_message: str | None = None,
) -> bool:
    """Apply a reconciliation outcome for an ``awaiting_upload`` job.

    ``outcome="queued"`` sets upload completion on the document (size,
    fingerprint, ``upload_completed_at``) and queues the job;
    ``outcome="failed"`` terminally fails job + document with the
    given classification.  Returns ``False`` when the job already left
    ``awaiting_upload`` (the normal upload path won the race -- the
    reconciliation was a no-op, which is also how a lost commit
    acknowledgment stays safe).
    """
    now = utcnow()
    job = session.scalar(
        select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()
    )
    if job is None or job.status != STATUS_AWAITING_UPLOAD:
        return False
    document = session.get(Document, job.target_document_id)
    snapshot = dict(job.resource_snapshot or {})
    if outcome == "queued":
        job.status = STATUS_QUEUED
        job.available_at = now
        job.stage = None
        if document is not None and document.deleted_at is None:
            if _snapshot_get(snapshot, "expected_size_bytes") is not None:
                document.file_size = int(_snapshot_get(snapshot, "expected_size_bytes"))
            if _snapshot_get(snapshot, "expected_sha256") is not None:
                document.content_sha256 = str(
                    _snapshot_get(snapshot, "expected_sha256")
                )
            document.upload_completed_at = now
    elif outcome == "failed":
        job.status = STATUS_FAILED
        job.finished_at = now
        job.last_error_code = error_code
        job.last_error_message = error_message
        _clear_lease(job)
        if (
            document is not None
            and document.deleted_at is None
            and document.processing_epoch == job.target_epoch
        ):
            document.status = "Failed"
            document.processing_error = f"{error_code}: {error_message}"
    else:
        raise ValueError(f"unknown awaiting-upload outcome: {outcome!r}")
    session.flush()
    return True


def find_expired_leases(session: Session, *, now: datetime, limit: int) -> list[JobContext]:
    """``running`` jobs whose lease has expired (worker presumably dead)."""
    rows = session.scalars(
        select(ProcessingJob)
        .where(
            ProcessingJob.status == STATUS_RUNNING,
            ProcessingJob.lease_expires_at.is_not(None),
            ProcessingJob.lease_expires_at <= now,
        )
        .order_by(ProcessingJob.lease_expires_at)
        .limit(limit)
        .with_for_update(skip_locked=True)
    ).all()
    contexts = []
    for row in rows:
        context = load_job_context(session, row.id)
        if context is not None:
            contexts.append(context)
    return contexts


def expire_lease(
    session: Session,
    *,
    job_id: UUID,
    now: datetime,
    backoff_base_seconds: int = DEFAULT_BACKOFF_BASE_SECONDS,
    backoff_cap_seconds: int = DEFAULT_BACKOFF_CAP_SECONDS,
) -> str:
    """Revoke one expired lease: requeue with backoff or fail.

    Returns ``"retry_wait"``, ``"failed"``, or ``"skipped"`` (the lease
    was renewed concurrently -- another worker is alive, leave it).
    """
    job = session.scalar(
        select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()
    )
    if (
        job is None
        or job.status != STATUS_RUNNING
        or job.lease_expires_at is None
        or job.lease_expires_at > now
    ):
        return "skipped"
    job.last_error_code = ERROR_LEASE_EXPIRED
    job.last_error_message = "worker lease expired without heartbeat"
    if (job.attempt_count or 0) < (job.max_attempts or 1):
        job.status = STATUS_RETRY_WAIT
        job.stage = None
        job.available_at = now + timedelta(
            seconds=compute_backoff_seconds(
                job.attempt_count or 1,
                base_seconds=backoff_base_seconds,
                cap_seconds=backoff_cap_seconds,
                jitter_seed=str(job.id),
            )
        )
        _clear_lease(job)
        session.flush()
        return STATUS_RETRY_WAIT
    job.status = STATUS_FAILED
    job.finished_at = now
    _clear_lease(job)
    if job.kind == KIND_PROCESS:
        document = session.get(Document, job.target_document_id)
        if (
            document is not None
            and document.deleted_at is None
            and document.processing_epoch == job.target_epoch
        ):
            document.status = "Failed"
            document.processing_error = (
                f"{ERROR_LEASE_EXPIRED}: worker lease expired without heartbeat"
            )
    session.flush()
    return STATUS_FAILED


def cancel_jobs_for_deleted_documents(
    session: Session, *, limit: int, reason: str = "document was deleted"
) -> int:
    """Cancel nonterminal *processing* jobs whose document is tombstoned/gone.

    Covers the delete race where A3 tombstoned a document but a process
    job was queued/retrying/running at the time.  Cancelling bumps the
    fencing token, so a live holder cannot publish into the deleted
    scope.

    ``delete_document`` jobs are deliberately excluded: their whole
    purpose is to remove the storage object and index versions *after*
    the row is tombstoned, so treating them as orphans would cancel the
    only cleanup path and leave the PDF orphaned in storage.
    """
    rows = session.scalars(
        select(ProcessingJob)
        .outerjoin(Document, Document.id == ProcessingJob.target_document_id)
        .where(
            ProcessingJob.kind != KIND_DELETE,
            ProcessingJob.status.in_(
                (STATUS_QUEUED, STATUS_RUNNING, STATUS_RETRY_WAIT)
            ),
            (Document.id.is_(None)) | (Document.deleted_at.is_not(None)),
        )
        .order_by(ProcessingJob.created_at)
        .limit(limit)
        .with_for_update(skip_locked=True, of=ProcessingJob)
    ).all()
    count = 0
    for job in rows:
        job.lease_token = (job.lease_token or 0) + 1
        job.status = STATUS_CANCELLED
        job.finished_at = utcnow()
        job.last_error_code = CANCELLED_MARKER
        job.last_error_message = reason
        _clear_lease(job)
        count += 1
    session.flush()
    return count


def find_stale_index_versions(
    session: Session, *, now: datetime, grace_seconds: int, limit: int
) -> list[SweepCandidate]:
    """Index namespaces eligible for the grace-period sweep.

    Covers terminal process jobs (their current version, which for
    failed/cancelled jobs is unpublished, and for succeeded jobs is the
    active version and therefore excluded) and any job's recorded
    superseded attempts.  The reconciler re-reads the document's
    active pointer immediately before deleting (JOB-09), so this list
    is only a candidate set, never a deletion order.
    """
    cutoff = now - timedelta(seconds=grace_seconds)
    rows = session.scalars(
        select(ProcessingJob)
        .where(
            ProcessingJob.kind == KIND_PROCESS,
            (
                (
                    ProcessingJob.status.in_(TERMINAL_STATUSES)
                    & ProcessingJob.index_version.is_not(None)
                    & ProcessingJob.finished_at.is_not(None)
                    & (ProcessingJob.finished_at <= cutoff)
                )
                | (
                    ProcessingJob.resource_snapshot.op("?")("superseded_index_versions")
                    & (ProcessingJob.updated_at <= cutoff)
                )
            ),
        )
        .order_by(ProcessingJob.updated_at)
        .limit(limit)
    ).all()
    candidates: list[SweepCandidate] = []
    seen: set[tuple[UUID, str]] = set()
    for job in rows:
        document = session.get(Document, job.target_document_id)
        active = document.active_index_version if document else None
        versions: list[str] = []
        if job.index_version is not None:
            versions.append(str(job.index_version))
        superseded = (job.resource_snapshot or {}).get("superseded_index_versions") or []
        versions.extend(str(v) for v in superseded)
        for version in versions:
            if active is not None and version == str(active):
                continue  # never sweep the active pointer (JOB-11)
            if job.status == STATUS_SUCCEEDED and version == str(job.index_version):
                continue  # succeeded job's version is the active one
            key = (job.target_document_id, version)
            if key in seen:
                continue
            seen.add(key)
            candidates.append(
                SweepCandidate(
                    target_document_id=job.target_document_id,
                    project_id=job.project_id,
                    owner_user_id=job.owner_user_id,
                    index_version=UUID(version),
                    job_id=job.id,
                )
            )
    return candidates


def get_active_version(
    session: Session, target_document_id: UUID
) -> tuple[bool, UUID | None]:
    """Return ``(document_exists_live, active_index_version)``."""
    document = session.get(Document, target_document_id)
    if document is None or document.deleted_at is not None:
        return False, None
    return True, document.active_index_version


# ---------------------------------------------------------------------------
# Short-transaction store for the worker (one tx per operation)
# ---------------------------------------------------------------------------


class JobQueueStore:
    """Worker-side facade: each method is one short DB transaction.

    ``session_factory`` is a SQLAlchemy ``sessionmaker`` (see
    ``app.db.session.make_worker_session_factory``).  Provider work
    never happens inside these transactions -- the processor commits
    the claim before touching storage/embeddings/Chroma, then commits
    the fenced result afterwards.
    """

    def __init__(self, session_factory: Any) -> None:
        self._factory = session_factory

    # -- tiny transaction helper -------------------------------------
    def _tx(self, fn: Any) -> Any:
        with self._factory() as session:
            with session.begin():
                return fn(session)

    # -- protocol operations ------------------------------------------
    def enqueue_job(self, **kwargs: Any) -> ProcessingJob:
        return self._tx(lambda s: enqueue_job(s, **kwargs))

    def find_nonterminal_job(self, **kwargs: Any) -> ProcessingJob | None:
        return self._tx(lambda s: find_nonterminal_job(s, **kwargs))

    def claim_next_jobs(self, *, worker_id: str, limit: int, lease_seconds: int) -> list[JobClaim]:
        return self._tx(
            lambda s: claim_next_jobs(s, worker_id=worker_id, limit=limit, lease_seconds=lease_seconds)
        )

    def renew_job_lease(
        self, *, job_id: UUID, lease_token: int, worker_id: str, lease_seconds: int
    ) -> bool:
        return self._tx(
            lambda s: renew_job_lease(
                s, job_id=job_id, lease_token=lease_token, worker_id=worker_id, lease_seconds=lease_seconds
            )
        )

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
        return self._tx(
            lambda s: update_progress(
                s,
                job_id=job_id,
                lease_token=lease_token,
                worker_id=worker_id,
                stage=stage,
                progress_current=progress_current,
                progress_total=progress_total,
            )
        )

    def complete_job(
        self, *, job_id: UUID, lease_token: int, worker_id: str, chunk_count: int | None = None
    ) -> bool:
        return self._tx(
            lambda s: complete_job(
                s, job_id=job_id, lease_token=lease_token, worker_id=worker_id, chunk_count=chunk_count
            )
        )

    def fail_job(
        self,
        *,
        job_id: UUID,
        lease_token: int,
        worker_id: str,
        error_code: str,
        error_message: str,
        retryable: bool,
        backoff_base_seconds: int = DEFAULT_BACKOFF_BASE_SECONDS,
        backoff_cap_seconds: int = DEFAULT_BACKOFF_CAP_SECONDS,
    ) -> bool:
        return self._tx(
            lambda s: fail_job(
                s,
                job_id=job_id,
                lease_token=lease_token,
                worker_id=worker_id,
                error_code=error_code,
                error_message=error_message,
                retryable=retryable,
                backoff_base_seconds=backoff_base_seconds,
                backoff_cap_seconds=backoff_cap_seconds,
            )
        )

    def cancel_job(self, *, job_id: UUID, reason: str) -> bool:
        return self._tx(lambda s: cancel_job(s, job_id=job_id, reason=reason))

    # -- reconciliation operations -------------------------------------
    def load_job_context(self, job_id: UUID) -> JobContext | None:
        with self._factory() as session:
            return load_job_context(session, job_id)

    def find_expired_awaiting_upload(self, *, cutoff: datetime, limit: int) -> list[JobContext]:
        return self._tx(lambda s: find_expired_awaiting_upload(s, cutoff=cutoff, limit=limit))

    def apply_awaiting_upload_outcome(
        self, *, job_id: UUID, outcome: str, error_code: str | None = None, error_message: str | None = None
    ) -> bool:
        return self._tx(
            lambda s: apply_awaiting_upload_outcome(
                s, job_id=job_id, outcome=outcome, error_code=error_code, error_message=error_message
            )
        )

    def find_expired_leases(self, *, now: datetime, limit: int) -> list[JobContext]:
        return self._tx(lambda s: find_expired_leases(s, now=now, limit=limit))

    def expire_lease(self, *, job_id: UUID, now: datetime, **backoff: int) -> str:
        return self._tx(lambda s: expire_lease(s, job_id=job_id, now=now, **backoff))

    def cancel_jobs_for_deleted_documents(self, *, limit: int) -> int:
        return self._tx(lambda s: cancel_jobs_for_deleted_documents(s, limit=limit))

    def find_stale_index_versions(
        self, *, now: datetime, grace_seconds: int, limit: int
    ) -> list[SweepCandidate]:
        return self._tx(
            lambda s: find_stale_index_versions(s, now=now, grace_seconds=grace_seconds, limit=limit)
        )

    def get_active_version(self, target_document_id: UUID) -> tuple[bool, UUID | None]:
        with self._factory() as session:
            return get_active_version(session, target_document_id)


__all__ = [
    "KIND_DELETE",
    "KIND_PROCESS",
    "JobContext",
    "JobQueueStore",
    "SweepCandidate",
    "apply_awaiting_upload_outcome",
    "cancel_job",
    "cancel_jobs_for_deleted_documents",
    "claim_next_jobs",
    "complete_job",
    "enqueue_job",
    "evaluate_publication",
    "expire_lease",
    "fail_job",
    "find_expired_awaiting_upload",
    "find_expired_leases",
    "find_nonterminal_job",
    "find_stale_index_versions",
    "get_active_version",
    "lease_is_current",
    "load_job_context",
    "renew_job_lease",
    "update_progress",
]
