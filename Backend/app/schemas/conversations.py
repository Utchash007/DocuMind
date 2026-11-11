"""Conversation DTOs: ``/projects/{id}/conversations``."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.common import CamelModel, RequestModel


class Conversation(CamelModel):
    id: UUID
    project_id: UUID
    title: str | None = None
    created_at: datetime
    updated_at: datetime


def _strip_title(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("title must not be blank")
    if len(stripped) > 255:
        raise ValueError("title must be at most 255 characters")
    return stripped


class ConversationCreateRequest(RequestModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)

    @field_validator("title")
    @classmethod
    def _title(cls, value: str | None) -> str | None:
        return None if value is None else _strip_title(value)


class ConversationUpdateRequest(RequestModel):
    """``PATCH .../conversations/{id}``: rename only."""

    title: str = Field(min_length=1, max_length=255)

    @field_validator("title")
    @classmethod
    def _title(cls, value: str) -> str:
        return _strip_title(value)


class ConversationDeleteAccepted(CamelModel):
    """``DELETE .../conversations/{id}`` -> 200 body (messages cascade).

    Conversation deletion is synchronous: the conversation and its
    messages are removed in one transaction, so no cleanup job is needed.
    (Project/document deletion is the asynchronous, 202 case.)
    """

    conversation_id: UUID
    accepted: bool = True


__all__ = [
    "Conversation",
    "ConversationCreateRequest",
    "ConversationDeleteAccepted",
    "ConversationUpdateRequest",
]
