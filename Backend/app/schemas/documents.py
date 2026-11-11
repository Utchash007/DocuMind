"""Document DTOs: ``/projects/{id}/documents``."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.schemas.common import CamelModel, DocumentStatus
from app.schemas.jobs import ProcessingJob


class Document(CamelModel):
    """Public document payload.

    Excludes ``appwrite_file_id`` (server-only storage reference),
    ``content_sha256`` and Chroma internals.  ``file_name`` is a display
    label; identity is ``id``.  ``processingError`` is a safe diagnostic
    summary only (never a raw provider payload).
    """

    id: UUID
    project_id: UUID
    file_name: str
    file_size: int | None = None
    mime_type: str | None = None
    status: DocumentStatus
    upload_completed_at: datetime | None = None
    processing_epoch: int
    active_index_version: UUID | None = None
    chunk_count: int | None = None
    processed_at: datetime | None = None
    processing_error: str | None = None
    deleted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class DocumentDeleteAccepted(CamelModel):
    """``DELETE .../documents/{id}`` -> 202 body while cleanup is pending.

    The document is tombstoned and hidden from reads/retrieval
    immediately; ``jobId`` identifies the queued ``delete_document``
    cleanup job (poll it via ``GET /jobs/{jobId}``).
    """

    project_id: UUID
    document_id: UUID
    job_id: UUID
    accepted: bool = True


class UploadAcceptance(CamelModel):
    """``POST .../documents`` and ``POST .../documents/{id}/retry`` -> 202.

    Receiving this response means the PDF bytes are stored and the job is
    durably queued -- it does NOT mean chunks are indexed.  Poll
    ``document.status`` / ``job.status`` until a terminal state.
    Re-sending the same ``Idempotency-Key`` (``upload_request_id``)
    returns the originally created pair, never a reset job.
    """

    document: Document
    job: ProcessingJob


__all__ = ["Document", "DocumentDeleteAccepted", "UploadAcceptance"]
