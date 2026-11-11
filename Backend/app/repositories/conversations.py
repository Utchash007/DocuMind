"""Conversation repository.

Owner-scoped conversation CRUD plus chronological message listing, built on
the database models and owned lookups. Every function assumes the caller has
authorized the principal; :func:`get_owned_project` /
:func:`get_owned_conversation` enforce
``conversation -> project -> users.id`` (``plan.md`` section 3.3).

Pagination is keyset-based.  Conversations page newest-activity-first
(``updated_at`` descending, UUID ascending-descending tiebreak) using the
``ix_conversations_project_activity`` index; messages page
chronologically by the stable ``position`` column.  Both return
``{items, nextCursor}`` (``docs/v2-contracts.md`` section 2.3).  Cursors
are opaque base64url blobs (see :mod:`app.schemas.common`); a malformed
cursor raises :class:`CursorError` so the router can answer
``422 validation_error``.

All functions perform pure database reads/writes (no provider calls) and
must run inside a short ``request_transaction`` (see
:mod:`app.db.session`).
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.models import Conversation, Message
from app.db.queries import get_owned_conversation, get_owned_project
from app.schemas.common import (
    Citation,
    PaginatedResponse,
    decode_cursor,
    encode_cursor,
)
from app.schemas.conversations import Conversation as ConversationDto
from app.schemas.messages import Message as MessageDto


class NotFoundError(Exception):
    """Resource missing or not owned by the caller (never leaks existence)."""


class CursorError(ValueError):
    """Malformed pagination cursor (mapped to ``422 validation_error``)."""


def to_conversation_dto(row: Conversation) -> ConversationDto:
    """Convert an ORM conversation row to its public DTO."""
    return ConversationDto(
        id=row.id,
        project_id=row.project_id,
        title=row.title,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def to_message_dto(row: Message) -> MessageDto:
    """Convert an ORM message row to its public DTO.

    Persisted citations are stored as camelCase JSONB (the public wire
    shape) and validate as :class:`Citation`. The SQL ``metadata`` column is
    exposed as the public ``metadata`` field.
    """
    citations = [Citation(**entry) for entry in row.citations] if row.citations is not None else None
    return MessageDto(
        id=row.id,
        conversation_id=row.conversation_id,
        role=row.role,
        content=row.content,
        position=row.position,
        citations=citations,
        message_metadata=row.message_metadata,
        client_request_id=row.client_request_id,
        reply_to_message_id=row.reply_to_message_id,
        generation_status=row.generation_status,
        generation_expires_at=row.generation_expires_at,
        created_at=row.created_at,
    )


def require_owned_project(session: Session, *, user_id: UUID, project_id: UUID):
    """Return the project or raise :class:`NotFoundError`."""
    project = get_owned_project(session, user_id=user_id, project_id=project_id)
    if project is None:
        raise NotFoundError(f"project not found: {project_id}")
    return project


def require_owned_conversation(
    session: Session, *, user_id: UUID, project_id: UUID, conversation_id: UUID
):
    """Return the conversation or raise :class:`NotFoundError`.

    Missing and unowned conversations raise the same error (``404``), so
    callers have no existence oracle.
    """
    conversation = get_owned_conversation(
        session,
        user_id=user_id,
        project_id=project_id,
        conversation_id=conversation_id,
    )
    if conversation is None:
        raise NotFoundError(f"conversation not found: {conversation_id}")
    return conversation


def list_conversations(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    cursor: str | None,
    limit: int,
) -> PaginatedResponse[ConversationDto]:
    """List a project's conversations newest-activity-first."""
    require_owned_project(session, user_id=user_id, project_id=project_id)
    statement = (
        select(Conversation)
        .where(Conversation.project_id == project_id)
        .order_by(Conversation.updated_at.desc(), Conversation.id.desc())
    )
    if cursor:
        payload = _decode(payload_cursor=cursor, kind="conversation")
        seen_updated_at: datetime = payload["updatedAt"]
        seen_id: UUID = payload["id"]
        statement = statement.where(
            or_(
                Conversation.updated_at < seen_updated_at,
                (Conversation.updated_at == seen_updated_at)
                & (Conversation.id < seen_id),
            )
        )
    statement = statement.limit(limit + 1)
    rows = list(session.scalars(statement))
    next_cursor: str | None = None
    if len(rows) > limit:
        rows = rows[:limit]
        last = rows[-1]
        next_cursor = encode_cursor(
            {"updatedAt": last.updated_at.isoformat(), "id": str(last.id)}
        )
    return PaginatedResponse[ConversationDto](
        items=[to_conversation_dto(row) for row in rows],
        next_cursor=next_cursor,
    )


def create_conversation(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    title: str | None,
) -> ConversationDto:
    """Create a conversation in an owned project."""
    require_owned_project(session, user_id=user_id, project_id=project_id)
    row = Conversation(project_id=project_id, title=title)
    session.add(row)
    session.flush()
    return to_conversation_dto(row)


def get_conversation(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    conversation_id: UUID,
) -> ConversationDto:
    """Read one owned conversation."""
    row = require_owned_conversation(
        session,
        user_id=user_id,
        project_id=project_id,
        conversation_id=conversation_id,
    )
    return to_conversation_dto(row)


def rename_conversation(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    conversation_id: UUID,
    title: str,
) -> ConversationDto:
    """Rename an owned conversation (bumps ``updated_at`` via ORM onupdate)."""
    row = require_owned_conversation(
        session,
        user_id=user_id,
        project_id=project_id,
        conversation_id=conversation_id,
    )
    row.title = title
    session.flush()
    return to_conversation_dto(row)


def delete_conversation(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    conversation_id: UUID,
) -> UUID:
    """Delete an owned conversation and its messages in one transaction.

    Messages cascade from the SQL ``ON DELETE CASCADE`` on
    ``messages.conversation_id`` (and assistant replies cascade from their
    user message), so no per-message cleanup is needed.

    In-flight generations are invalidated by the same delete: a late
    provider response cannot find the user turn and fails the persist
    guard in :mod:`app.repositories.messages`.
    """
    row = require_owned_conversation(
        session,
        user_id=user_id,
        project_id=project_id,
        conversation_id=conversation_id,
    )
    deleted_id = row.id
    session.delete(row)
    session.flush()
    return deleted_id


def list_messages(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    conversation_id: UUID,
    cursor: str | None,
    limit: int,
) -> PaginatedResponse[MessageDto]:
    """List a conversation's history chronologically by ``position``.

    Stable positions make pages immune to inserts mid-traversal (no
    duplicates or skips).  The cursor is the last returned position; the
    next page contains ``position > cursor`` in ascending order.
    """
    require_owned_conversation(
        session,
        user_id=user_id,
        project_id=project_id,
        conversation_id=conversation_id,
    )
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.position.asc())
    )
    if cursor:
        payload = _decode(payload_cursor=cursor, kind="message")
        statement = statement.where(Message.position > payload["position"])
    statement = statement.limit(limit + 1)
    rows = list(session.scalars(statement))
    next_cursor: str | None = None
    if len(rows) > limit:
        rows = rows[:limit]
        next_cursor = encode_cursor({"position": rows[-1].position})
    return PaginatedResponse[MessageDto](
        items=[to_message_dto(row) for row in rows],
        next_cursor=next_cursor,
    )


def _decode(*, payload_cursor: str, kind: str) -> dict:
    """Decode and validate a cursor payload for the given list kind."""
    try:
        payload = decode_cursor(payload_cursor)
    except ValueError as exc:
        raise CursorError("cursor is invalid") from exc
    if kind == "conversation":
        try:
            updated_at = datetime.fromisoformat(str(payload["updatedAt"]))
            rid = UUID(str(payload["id"]))
        except (KeyError, ValueError, TypeError) as exc:
            raise CursorError("cursor is invalid") from exc
        if updated_at.tzinfo is None:
            raise CursorError("cursor is invalid")
        return {"updatedAt": updated_at, "id": rid}
    try:
        position = int(payload["position"])
    except (KeyError, ValueError, TypeError) as exc:
        raise CursorError("cursor is invalid") from exc
    if position < 1:
        raise CursorError("cursor is invalid")
    return {"position": position}


__all__ = [
    "CursorError",
    "NotFoundError",
    "create_conversation",
    "delete_conversation",
    "get_conversation",
    "list_conversations",
    "list_messages",
    "rename_conversation",
    "require_owned_conversation",
    "require_owned_project",
    "to_conversation_dto",
    "to_message_dto",
]
