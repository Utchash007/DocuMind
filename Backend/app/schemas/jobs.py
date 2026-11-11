"""Processing-job DTOs: upload acceptance and ``GET /jobs/{jobId}``.

Internal-only fields (``lease_owner``, ``lease_token``,
``lease_expires_at``, ``resource_snapshot``) are never serialized: they
are worker fencing/reconciliation state, not client state.  Consumers
poll the public fields below; a ``succeeded``/``failed``/``cancelled``
status is terminal.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.schemas.common import CamelModel, JobKind, JobStage, JobStatus

TERMINAL_JOB_STATUSES = frozenset({JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED})


class ProcessingJob(CamelModel):
    id: UUID
    document_id: UUID | None = None
    project_id: UUID
    target_document_id: UUID
    kind: JobKind
    status: JobStatus
    stage: JobStage | None = None
    attempt_count: int
    max_attempts: int
    available_at: datetime
    index_version: UUID | None = None
    progress_current: int | None = None
    progress_total: int | None = None
    last_error_code: str | None = None
    last_error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    finished_at: datetime | None = None

    def is_terminal(self) -> bool:
        return self.status in TERMINAL_JOB_STATUSES


__all__ = ["ProcessingJob", "TERMINAL_JOB_STATUSES"]
