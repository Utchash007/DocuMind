"""Concrete owned-resource lookups and position allocation.

These helpers implement the shared authorization joins:
``document/conversation -> project -> users.id``.
They perform no writes and never touch external services; callers run
them inside a short ``request_transaction`` (or request session).

Deleted (tombstoned) rows are hidden by default.  Pass
``include_deleted=True`` only for cleanup/reconciliation code paths.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Conversation, Document, Message, ProcessingJob, Project


def get_owned_project(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    include_deleted: bool = False,
) -> Project | None:
    """Return the project iff it exists and belongs to ``user_id``."""
    statement = select(Project).where(
        Project.id == project_id,
        Project.user_id == user_id,
    )
    if not include_deleted:
        statement = statement.where(Project.deleted_at.is_(None))
    return session.scalar(statement)


def get_owned_document(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    document_id: UUID,
    include_deleted: bool = False,
) -> Document | None:
    """Return the document iff its project belongs to ``user_id``."""
    statement = (
        select(Document)
        .join(Project, Project.id == Document.project_id)
        .where(
            Document.id == document_id,
            Document.project_id == project_id,
            Project.user_id == user_id,
        )
    )
    if not include_deleted:
        statement = statement.where(
            Document.deleted_at.is_(None),
            Project.deleted_at.is_(None),
        )
    return session.scalar(statement)


def get_owned_conversation(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    conversation_id: UUID,
    include_deleted: bool = False,
) -> Conversation | None:
    """Return the conversation iff its project belongs to ``user_id``."""
    statement = (
        select(Conversation)
        .join(Project, Project.id == Conversation.project_id)
        .where(
            Conversation.id == conversation_id,
            Conversation.project_id == project_id,
            Project.user_id == user_id,
        )
    )
    if not include_deleted:
        statement = statement.where(Project.deleted_at.is_(None))
    return session.scalar(statement)


def get_owned_job(
    session: Session,
    *,
    user_id: UUID,
    job_id: UUID,
) -> ProcessingJob | None:
    """Return the job iff its immutable ``owner_user_id`` snapshot matches.

    Jobs are addressed by snapshot, not by a live join, so a job stays
    owner-scoped after its document/project rows are deleted.
    """
    return session.scalar(
        select(ProcessingJob).where(
            ProcessingJob.id == job_id,
            ProcessingJob.owner_user_id == user_id,
        )
    )


def next_message_position(session: Session, *, conversation_id: UUID) -> int:
    """Allocate the next monotonic ``position`` inside a conversation.

    Must be called inside an open transaction.  The conversation row is
    locked with ``FOR UPDATE`` so concurrent writers serialize on it;
    combined with the unique ``(conversation_id, position)`` index this
    gives gap-checked, strictly increasing positions starting at 1.
    Raises :class:`LookupError` if the conversation does not exist.
    """
    locked = session.scalar(
        select(Conversation.id)
        .where(Conversation.id == conversation_id)
        .with_for_update()
    )
    if locked is None:
        raise LookupError(f"conversation not found: {conversation_id}")
    current_max = session.scalar(
        select(func.coalesce(func.max(Message.position), 0)).where(
            Message.conversation_id == conversation_id
        )
    )
    return int(current_max or 0) + 1


__all__ = [
    "get_owned_conversation",
    "get_owned_document",
    "get_owned_job",
    "get_owned_project",
    "next_message_position",
]
