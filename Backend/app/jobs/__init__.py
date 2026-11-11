"""Durable PostgreSQL job queue.

Exports the interface used for enqueue/status/cancel and the
worker uses for claim/lease/progress/complete/fail, plus the
reconciler and error/backoff helpers.  See :mod:`app.jobs.queue` for
the lease/fencing contract and ``app.workers.pdf_worker`` for run
instructions.
"""

from __future__ import annotations

from app.jobs.errors import (  # noqa: E402
    JobError,
    compute_backoff_seconds,
    safe_message,
)
from app.jobs.queue import (
    JobContext,
    JobQueueStore,
    SweepCandidate,
    apply_awaiting_upload_outcome,
    cancel_job,
    claim_next_jobs,
    complete_job,
    enqueue_job,
    evaluate_publication,
    expire_lease,
    fail_job,
    find_nonterminal_job,
    lease_is_current,
    load_job_context,
    renew_job_lease,
    update_progress,
)
from app.jobs.reconcile import (
    ReconcileReport,
    Reconciler,
    awaiting_upload_outcome,
    lease_expiry_outcome,
    sweep_eligible,
)

__all__ = [
    "JobContext",
    "JobError",
    "JobQueueStore",
    "ReconcileReport",
    "Reconciler",
    "SweepCandidate",
    "apply_awaiting_upload_outcome",
    "awaiting_upload_outcome",
    "cancel_job",
    "claim_next_jobs",
    "complete_job",
    "compute_backoff_seconds",
    "enqueue_job",
    "evaluate_publication",
    "expire_lease",
    "fail_job",
    "find_nonterminal_job",
    "lease_expiry_outcome",
    "lease_is_current",
    "load_job_context",
    "renew_job_lease",
    "safe_message",
    "sweep_eligible",
    "update_progress",
]
