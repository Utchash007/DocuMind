"""Shared DTO primitives: camelCase serialization, enums, errors, cursors.

Contract rules frozen here (``plan.md`` section 4.2, ``docs/v2-contracts.md``):

* Python attributes are snake_case; public JSON is camelCase via explicit
  serialization aliases (``alias_generator`` + ``by_alias=True`` dumps).
  ``populate_by_name=True`` lets server code construct DTOs with either
  spelling.
* Errors keep the FastAPI ``detail`` envelope: ``{"detail": {...}}`` where
  the object carries a stable ``code`` plus a human ``message`` and
  optional resource IDs. Application routes use :class:`ApiError`;
  framework validation errors retain their standard detail arrays.
* Lists return ``{"items": [...], "nextCursor": "..."}`` (see
  :class:`PaginatedResponse`).  Cursors are opaque to clients.
"""

from __future__ import annotations

import base64
import json
from enum import StrEnum
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

T = TypeVar("T")


def to_camel(name: str) -> str:
    """Convert a snake_case attribute name to camelCase (``_id`` aware).

    ``user_id`` -> ``userId``, ``appwrite_user_id`` -> ``appwriteUserId``,
    ``id`` -> ``id``.  Single leading underscores are preserved so private
    validator helpers are never accidentally exposed as public fields.
    """
    head, *tail = name.split("_")
    if not tail:
        return name
    return head + "".join(part[:1].upper() + part[1:] for part in tail if part)


class CamelModel(BaseModel):
    """Base model: camelCase JSON, snake_case Python, ORM-friendly."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        extra="ignore",
    )


class RequestModel(CamelModel):
    """Base model for request bodies: unknown fields are rejected (422)."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        extra="forbid",
    )


# ---------------------------------------------------------------------------
# Enums (values match the DB CHECK constraints in app/db/models.py)
# ---------------------------------------------------------------------------


class DocumentStatus(StrEnum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class GenerationStatus(StrEnum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobKind(StrEnum):
    PROCESS_DOCUMENT = "process_document"
    DELETE_DOCUMENT = "delete_document"


class JobStatus(StrEnum):
    AWAITING_UPLOAD = "awaiting_upload"
    QUEUED = "queued"
    RUNNING = "running"
    RETRY_WAIT = "retry_wait"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobStage(StrEnum):
    UPLOADING = "uploading"
    EXTRACTING = "extracting"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    PUBLISHING = "publishing"
    DELETING = "deleting"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ErrorCode(StrEnum):
    """Stable machine-readable error codes (see docs/v2-contracts.md)."""

    UNAUTHENTICATED = "unauthenticated"
    ONBOARDING_REQUIRED = "onboarding_required"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    VALIDATION_ERROR = "validation_error"
    CONFLICT = "conflict"
    DUPLICATE_REQUEST_CONFLICT = "duplicate_request_conflict"
    ACTIVE_TURN_IN_PROGRESS = "active_turn_in_progress"
    INVALID_STATE = "invalid_state"
    NO_READY_SOURCES = "no_ready_sources"
    PROCESSING_IN_PROGRESS = "processing_in_progress"
    SERVICE_UNAVAILABLE = "service_unavailable"
    INTERNAL_ERROR = "internal_error"


class ApiError(CamelModel):
    """Body of the ``detail`` field for every v2 error response."""

    code: ErrorCode
    message: str = Field(min_length=1)
    job_id: UUID | None = None
    message_id: UUID | None = None
    document_id: UUID | None = None
    project_id: UUID | None = None
    conversation_id: UUID | None = None


class ErrorEnvelope(CamelModel):
    """Full error wire shape: ``{"detail": ApiError}`` (FastAPI envelope)."""

    detail: ApiError


# ---------------------------------------------------------------------------
# Citations
# ---------------------------------------------------------------------------


class Citation(CamelModel):
    """Verified citation: identity, page and exact text from a chunk.

    This is the persisted ``messages.citations`` element shape and the
    public wire shape (``plan.md`` section 4.2).  ``index_version`` is the
    Chroma index namespace the chunk was retrieved from. Identity must
    come from an authorized matched chunk, never from a filename alone.
    """

    document_id: UUID
    file_name: str = Field(min_length=1)
    page_number: int = Field(ge=1)
    chunk_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    index_version: UUID

    @field_validator("file_name", "chunk_id", "text")
    @classmethod
    def _strip(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("value must not be blank")
        return stripped


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------


class CursorPageParams(CamelModel):
    """Shared list-query parameters.

    ``cursor`` is the opaque ``nextCursor`` from the previous page (never
    parsed by the client).  ``limit`` defaults to 50 and is capped at
    200 for every list endpoint; message history uses the same bounds.
    """

    cursor: str | None = None
    limit: int = Field(default=50, ge=1, le=200)


class PaginatedResponse(CamelModel, Generic[T]):
    """List envelope: ``{"items": [...], "nextCursor": str | null}``."""

    items: list[T]
    next_cursor: str | None = None


def encode_cursor(payload: dict[str, Any]) -> str:
    """Encode a server-side cursor payload as an opaque base64url string."""
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def decode_cursor(cursor: str) -> dict[str, Any]:
    """Decode a cursor produced by :func:`encode_cursor`.

    Raises :class:`ValueError` for malformed or non-object payloads so
    handlers can convert bad cursors into a ``422 validation_error``.
    """
    if not cursor or not cursor.strip():
        raise ValueError("cursor must not be blank")
    padded = cursor.strip() + "=" * (-len(cursor.strip()) % 4)
    try:
        decoded = base64.urlsafe_b64decode(padded.encode("ascii"))
        payload = json.loads(decoded.decode("utf-8"))
    except Exception as exc:  # binascii/unicode/json errors
        raise ValueError("invalid cursor") from exc
    if not isinstance(payload, dict):
        raise ValueError("invalid cursor")
    return payload


__all__ = [
    "ApiError",
    "Citation",
    "CursorPageParams",
    "DocumentStatus",
    "ErrorCode",
    "ErrorEnvelope",
    "GenerationStatus",
    "JobKind",
    "JobStage",
    "JobStatus",
    "MessageRole",
    "PaginatedResponse",
    "RequestModel",
    "CamelModel",
    "decode_cursor",
    "encode_cursor",
    "to_camel",
]
