"""Message DTOs: ``.../conversations/{id}/messages``."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.common import (
    CamelModel,
    Citation,
    GenerationStatus,
    MessageRole,
    RequestModel,
)

# Public question budget (docs/v2-contracts.md).
MAX_QUESTION_LENGTH = 8000


class Message(CamelModel):
    """Public message payload.

    ``citations`` contains verified :class:`Citation` objects.
    ``metadata`` is the public
    name of the SQL ``metadata`` column (Python attr ``message_metadata``).
    ``generation_token`` is fencing state and is never serialized.
    """

    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    position: int
    citations: list[Citation] | None = None
    message_metadata: dict[str, Any] | None = Field(default=None, alias="metadata")
    client_request_id: UUID | None = None
    reply_to_message_id: UUID | None = None
    generation_status: GenerationStatus | None = None
    generation_expires_at: datetime | None = None
    created_at: datetime


class MessageCreateRequest(RequestModel):
    """``POST .../messages`` body.

    ``clientRequestId`` is required on every new user turn: it is the
    idempotency key behind the partial unique
    ``(conversation_id, client_request_id)`` index.  A repeated key with
    identical content returns the original turn; with different content
    it returns ``409 duplicate_request_conflict``.
    """

    content: str = Field(min_length=1, max_length=MAX_QUESTION_LENGTH)
    client_request_id: UUID

    @field_validator("content")
    @classmethod
    def _content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("content must not be blank")
        return value


class TurnResponse(CamelModel):
    """Successful message submission: both turns persisted, then returned."""

    user_message: Message
    assistant_message: Message


class MessageRetryRequest(RequestModel):
    """``POST .../messages/{messageId}/retry`` body (all fields optional).

    Retrying never creates a second user message: the existing failed /
    interrupted user turn is re-claimed.  ``clientRequestId``, when sent,
    must match the original turn's request ID (idempotent retry).
    """

    client_request_id: UUID | None = None


class MessageCancelResponse(CamelModel):
    """``POST .../messages/{messageId}/cancel`` -> 200 body."""

    user_message: Message
    cancelled: bool


__all__ = [
    "MAX_QUESTION_LENGTH",
    "Message",
    "MessageCancelResponse",
    "MessageCreateRequest",
    "MessageRetryRequest",
    "TurnResponse",
]
