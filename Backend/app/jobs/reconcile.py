"""Worker reconciliation and grace-period cleanup.

The worker's durability story: a job is only ever *triggered* by a PG
row, so a reconciler periodically repairs every place where reality
(storage, Chroma, a dead worker) can drift from the rows:

1. **Expired ``awaiting_upload``** (UPL-05/06): jobs whose reservation
   aged past the TTL are inspected in storage.  A complete file (chunk
   completion satisfied, size matches the expected size) is queued and
   the document's upload completion is recorded; a partial/missing
   file is terminally failed and its partial storage object is
   deleted best-effort (idempotent).
2. **Expired leases** (JOB-03): ``running`` jobs past
   ``lease_expires_at`` are revoked -- requeued with bounded backoff,
   or terminally failed once attempts are exhausted.  A concurrently
   renewed lease is skipped, never stolen.
3. **Orphaned jobs**: nonterminal *processing* jobs whose document was
   tombstoned or hard-deleted are cancelled (fencing token bumped, so a
   live holder cannot publish into the deleted scope).  Pending
   ``delete_document`` jobs are left alone: they are the cleanup path
   for the tombstoned storage object and index versions.
4. **Grace-period sweep** (JOB-11): unpublished/superseded index
   namespaces older than the grace window are deleted from Chroma.
   The document's active pointer is **re-read immediately before each
   delete** -- a lost commit acknowledgment means publication may have
   succeeded, and the active version must never be swept (JOB-09).

All storage/Chroma calls happen outside DB transactions (find -> act
-> apply).  Each pass is best-effort and isolated: a provider outage
in one pass is logged and retried on the next loop, never fatal to
the worker (JOB-06 restart resilience).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID



from app.jobs.errors import (  # noqa: E402
    ERROR_STORAGE_MISSING,
    ERROR_UPLOAD_INCOMPLETE,
    safe_message,
)
from app.jobs.ports import IndexPort, StoragePort  # noqa: E402
from app.jobs.queue import JobContext, JobQueueStore  # noqa: E402
from app.schemas.services import StorageFileInfo  # noqa: E402

log = logging.getLogger("documind.worker.reconcile")

DEFAULT_AWAITING_UPLOAD_TTL_SECONDS = 24 * 60 * 60
DEFAULT_SWEEP_GRACE_SECONDS = 24 * 60 * 60


@dataclass
class ReconcileReport:
    """Counts + human-readable actions for one reconciliation round."""

    queued_uploads: int = 0
    failed_uploads: int = 0
    requeued_leases: int = 0
    failed_leases: int = 0
    cancelled_orphans: int = 0
    swept_versions: int = 0
    skipped_active_versions: int = 0
    actions: list[str] = field(default_factory=list)

    def add(self, action: str) -> None:
        self.actions.append(action)


class AwaitingUploadOutcomeError(Exception):
    """Raised when storage inspection itself fails (retry next round)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def awaiting_upload_outcome(
    *,
    info: StorageFileInfo | None,
    expected_size_bytes: int | None,
) -> tuple[str, str | None, str | None]:
    """Pure decision: queue vs. fail an expired ``awaiting_upload`` job.

    Returns ``(outcome, error_code, error_message)`` where ``outcome``
    is ``"queued"`` or ``"failed"``.  A file counts as complete when
    chunk completion is satisfied (``chunks_uploaded == chunks_total``
    whenever a chunked upload is declared, or the ``completed`` flag)
    *and* its size matches the expected size when one is known.  Byte
    fingerprint verification happens at processing time (the frozen
    inspection protocol carries no hash); a mismatch there is a
    terminal ``fingerprint_mismatch``.
    """
    if info is None:
        return "failed", ERROR_STORAGE_MISSING, "reconciled upload file is missing from storage"
    chunks_complete = True
    if info.chunks_total > 0:
        chunks_complete = info.chunks_uploaded >= info.chunks_total
    if not info.completed and not chunks_complete:
        return (
            "failed",
            ERROR_UPLOAD_INCOMPLETE,
            f"reconciled upload is incomplete ({info.chunks_uploaded}/{info.chunks_total} chunks)",
        )
    if (
        expected_size_bytes is not None
        and info.size is not None
        and int(info.size) != int(expected_size_bytes)
    ):
        return (
            "failed",
            ERROR_UPLOAD_INCOMPLETE,
            f"reconciled upload size {info.size} does not match expected {expected_size_bytes}",
        )
    return "queued", None, None


def lease_expiry_outcome(*, attempt_count: int, max_attempts: int) -> str:
    """Pure decision: requeue (``retry_wait``) or fail an expired lease."""
    return "retry_wait" if attempt_count < max_attempts else "failed"


def sweep_eligible(
    *,
    candidate_version: UUID | str,
    active_version: UUID | str | None,
    document_live: bool,
) -> bool:
    """Pure guard: may this namespace be swept right now?

    Never the active version of a live document (JOB-09/11).  Versions
    of documents that are gone/tombstoned are always sweepable.
    """
    if not document_live:
        return True
    if active_version is None:
        return True
    return str(candidate_version) != str(active_version)


class Reconciler:
    """Runs the four reconciliation passes against the queue store."""

    def __init__(
        self,
        store: JobQueueStore,
        *,
        storage: StoragePort | None = None,
        index_service: IndexPort | None = None,
        awaiting_upload_ttl_seconds: int = DEFAULT_AWAITING_UPLOAD_TTL_SECONDS,
        sweep_grace_seconds: int = DEFAULT_SWEEP_GRACE_SECONDS,
        batch_size: int = 50,
        backoff_base_seconds: int = 5,
        backoff_cap_seconds: int = 3600,
    ) -> None:
        self.store = store
        self.storage = storage
        self.index_service = index_service
        self.awaiting_upload_ttl_seconds = awaiting_upload_ttl_seconds
        self.sweep_grace_seconds = sweep_grace_seconds
        self.batch_size = batch_size
        self.backoff_base_seconds = backoff_base_seconds
        self.backoff_cap_seconds = backoff_cap_seconds

    # -- pass 1: expired awaiting_upload --------------------------------
    def reconcile_awaiting_upload(self, now: datetime) -> ReconcileReport:
        report = ReconcileReport()
        cutoff = now - timedelta(seconds=self.awaiting_upload_ttl_seconds)
        candidates = self.store.find_expired_awaiting_upload(cutoff=cutoff, limit=self.batch_size)
        for context in candidates:
            try:
                outcome, error_code, error_message = self._inspect_awaiting_upload(context)
            except AwaitingUploadOutcomeError as exc:
                log.warning("reconcile awaiting_upload job %s: %s", context.job_id, exc.message)
                continue
            applied = self.store.apply_awaiting_upload_outcome(
                job_id=context.job_id,
                outcome=outcome,
                error_code=error_code,
                error_message=error_message,
            )
            if not applied:
                # The normal upload path won the race; nothing to do.
                continue
            if outcome == "queued":
                report.queued_uploads += 1
                report.add(f"queued reconciled upload for job {context.job_id}")
            else:
                report.failed_uploads += 1
                report.add(f"failed reconciled upload for job {context.job_id}: {error_code}")
                self._delete_partial_storage(context)
        return report

    def _inspect_awaiting_upload(
        self, context: JobContext
    ) -> tuple[str, str | None, str | None]:
        bucket_id = context.storage_bucket_id
        file_id = context.storage_file_id
        if bucket_id is None or file_id is None:
            return "failed", ERROR_STORAGE_MISSING, "job has no storage bucket/file reference"
        if self.storage is None:
            raise AwaitingUploadOutcomeError("storage adapter is not configured")
        try:
            info = self.storage.inspect_storage_file(bucket_id=bucket_id, file_id=file_id)
        except Exception as exc:
            raise AwaitingUploadOutcomeError(
                f"storage inspection failed: {safe_message(exc)}"
            ) from exc
        return awaiting_upload_outcome(
            info=info, expected_size_bytes=context.expected_size_bytes
        )

    def _delete_partial_storage(self, context: JobContext) -> None:
        """Best-effort cleanup of an abandoned partial upload."""
        bucket_id = context.storage_bucket_id
        file_id = context.storage_file_id
        if bucket_id is None or file_id is None or self.storage is None:
            return
        try:
            self.storage.delete_storage_file(bucket_id=bucket_id, file_id=file_id)
        except Exception as exc:  # idempotent cleanup is retried next round
            log.warning(
                "reconcile: partial-storage cleanup for job %s failed: %s",
                context.job_id,
                safe_message(exc),
            )

    # -- pass 2: expired leases ------------------------------------------
    def reconcile_expired_leases(self, now: datetime) -> ReconcileReport:
        report = ReconcileReport()
        candidates = self.store.find_expired_leases(now=now, limit=self.batch_size)
        for context in candidates:
            outcome = self.store.expire_lease(
                job_id=context.job_id,
                now=now,
                backoff_base_seconds=self.backoff_base_seconds,
                backoff_cap_seconds=self.backoff_cap_seconds,
            )
            if outcome == "retry_wait":
                report.requeued_leases += 1
                report.add(f"requeued expired lease for job {context.job_id}")
            elif outcome == "failed":
                report.failed_leases += 1
                report.add(f"failed expired lease for job {context.job_id}")
        return report

    # -- pass 3: orphaned jobs -------------------------------------------
    def reconcile_orphaned_jobs(self) -> ReconcileReport:
        report = ReconcileReport()
        cancelled = self.store.cancel_jobs_for_deleted_documents(limit=self.batch_size)
        report.cancelled_orphans = cancelled
        if cancelled:
            report.add(f"cancelled {cancelled} job(s) for deleted documents")
        return report

    # -- pass 4: grace-period version sweep ------------------------------
    def sweep_stale_versions(self, now: datetime) -> ReconcileReport:
        report = ReconcileReport()
        if self.index_service is None:
            return report
        candidates = self.store.find_stale_index_versions(
            now=now, grace_seconds=self.sweep_grace_seconds, limit=self.batch_size
        )
        for candidate in candidates:
            # JOB-09: never trust the candidate snapshot -- re-read the
            # active pointer at delete time.
            live, active = self.store.get_active_version(candidate.target_document_id)
            if not sweep_eligible(
                candidate_version=candidate.index_version,
                active_version=active,
                document_live=live,
            ):
                report.skipped_active_versions += 1
                report.add(
                    f"kept active version {candidate.index_version} "
                    f"for document {candidate.target_document_id}"
                )
                continue
            try:
                self.index_service.delete_index_version(
                    user_id=candidate.owner_user_id,
                    project_id=candidate.project_id,
                    document_id=candidate.target_document_id,
                    index_version=candidate.index_version,
                )
            except Exception as exc:
                log.warning(
                    "sweep: delete of version %s failed (retry next round): %s",
                    candidate.index_version,
                    safe_message(exc),
                )
                continue
            report.swept_versions += 1
            report.add(
                f"swept version {candidate.index_version} "
                f"for document {candidate.target_document_id}"
            )
        return report

    def run_once(self, now: datetime | None = None) -> ReconcileReport:
        """Run all four passes; one pass failing never blocks the rest."""
        from app.db.base import utcnow

        moment = now or utcnow()
        total = ReconcileReport()
        passes = (
            ("awaiting_upload", lambda: self.reconcile_awaiting_upload(moment)),
            ("expired_leases", lambda: self.reconcile_expired_leases(moment)),
            ("orphans", lambda: self.reconcile_orphaned_jobs()),
            ("sweep", lambda: self.sweep_stale_versions(moment)),
        )
        for name, fn in passes:
            try:
                part = fn()
            except Exception as exc:
                log.warning("reconcile pass %s failed: %s", name, safe_message(exc))
                continue
            total.queued_uploads += part.queued_uploads
            total.failed_uploads += part.failed_uploads
            total.requeued_leases += part.requeued_leases
            total.failed_leases += part.failed_leases
            total.cancelled_orphans += part.cancelled_orphans
            total.swept_versions += part.swept_versions
            total.skipped_active_versions += part.skipped_active_versions
            total.actions.extend(part.actions)
        return total


__all__ = [
    "DEFAULT_AWAITING_UPLOAD_TTL_SECONDS",
    "DEFAULT_SWEEP_GRACE_SECONDS",
    "AwaitingUploadOutcomeError",
    "ReconcileReport",
    "Reconciler",
    "awaiting_upload_outcome",
    "lease_expiry_outcome",
    "sweep_eligible",
]
