"""Project repository and central owned-resource lookups.

This module is the single home for owner-scoped project reads/writes
and the *central owned-lookup functions consumed by conversation APIs*
and the job-status endpoint:

    get_owned_project_or_404(session, *, user_id, project_id)
    get_owned_document_or_404(session, *, user_id, project_id, document_id)
    get_owned_conversation_or_404(session, *, user_id, project_id, conversation_id)
    get_owned_job_or_404(session, *, user_id, job_id)

Every lookup enforces ``document/conversation -> project -> users.id``
using :mod:`app.db.queries` helpers. Client-supplied IDs are
never trusted for ownership; the verified principal's internal
``users.id`` is the only owner input.  Inaccessible resources
(including forged IDs for another user) surface as ``404 not_found``
with no existence oracle.

Reads hide tombstoned (``deleted_at`` not null) projects/documents by
default.  ``include_deleted=True`` is for cleanup/reconciliation only
and must never be reachable from a client-controlled flag.  Job
lookups are deliberately *not* tombstone-filtered: jobs are addressed
by their immutable ``owner_user_id`` snapshot so owners can poll
cleanup status after a document/project is deleted (DEL-06).

All functions are synchronous and perform no network I/O.  Write
helpers only ``flush``; the handler owns ``commit``/``rollback`` and
must not hold a transaction open across Storage/Chroma/provider calls.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.models import Conversation, Document, ProcessingJob, Project
from app.db.queries import (
    get_owned_conversation as _query_owned_conversation,
)
from app.db.queries import (
    get_owned_document as _query_owned_document,
)
from app.db.queries import (
    get_owned_job as _query_owned_job,
)
from app.db.queries import (
    get_owned_project as _query_owned_project,
)
from app.schemas.common import ApiError, ErrorCode, decode_cursor, encode_cursor
from app.schemas.projects import Project as ProjectDto

__all__ = [
    "create_owned_project",
    "get_owned_conversation_or_404",
    "get_owned_document_or_404",
    "get_owned_job_or_404",
    "get_owned_project_or_404",
    "list_owned_projects",
    "project_to_dto",
    "raise_api_error",
    "tombstone_project",
    "update_owned_project",
]


# ---------------------------------------------------------------------------
# Error helper (shared by all v2 routes; FastAPI detail envelope)
# ---------------------------------------------------------------------------


def raise_api_error(
    status_code: int,
    code: ErrorCode,
    message: str,
    *,
    project_id: UUID | None = None,
    document_id: UUID | None = None,
    job_id: UUID | None = None,
    message_id: UUID | None = None,
    conversation_id: UUID | None = None,
) -> None:
    """Raise an HTTP error with ``{"detail": ApiError}`` (camelCase IDs)."""
    detail = ApiError(
        code=code,
        message=message,
        project_id=project_id,
        document_id=document_id,
        job_id=job_id,
        message_id=message_id,
        conversation_id=conversation_id,
    ).model_dump(by_alias=True, mode="json")
    raise HTTPException(status_code=status_code, detail=detail)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def project_to_dto(project: Project) -> ProjectDto:
    """Convert an ORM project to its public DTO (never exposes owner IDs)."""
    return ProjectDto.model_validate(project)


# ---------------------------------------------------------------------------
# Central owned lookups (A5 consumes these; handlers wrap with 404)
# ---------------------------------------------------------------------------


def get_owned_project_or_404(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    include_deleted: bool = False,
) -> Project:
    project = _query_owned_project(
        session,
        user_id=user_id,
        project_id=project_id,
        include_deleted=include_deleted,
    )
    if project is None:
        raise_api_error(
            404,
            ErrorCode.NOT_FOUND,
            "Project not found.",
            project_id=project_id,
        )
    return project


def get_owned_document_or_404(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    document_id: UUID,
    include_deleted: bool = False,
) -> Document:
    document = _query_owned_document(
        session,
        user_id=user_id,
        project_id=project_id,
        document_id=document_id,
        include_deleted=include_deleted,
    )
    if document is None:
        raise_api_error(
            404,
            ErrorCode.NOT_FOUND,
            "Document not found.",
            project_id=project_id,
            document_id=document_id,
        )
    return document


def get_owned_conversation_or_404(
    session: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    conversation_id: UUID,
    include_deleted: bool = False,
) -> Conversation:
    """Conversation -> project -> user lookup for A5 handlers."""
    conversation = _query_owned_conversation(
        session,
        user_id=user_id,
        project_id=project_id,
        conversation_id=conversation_id,
        include_deleted=include_deleted,
    )
    if conversation is None:
        raise_api_error(
            404,
            ErrorCode.NOT_FOUND,
            "Conversation not found.",
            project_id=project_id,
            conversation_id=conversation_id,
        )
    return conversation


def get_owned_job_or_404(
    session: Session,
    *,
    user_id: UUID,
    job_id: UUID,
) -> ProcessingJob:
    """Return the job iff its snapshot ``owner_user_id`` matches.

    No tombstone filter: cleanup jobs stay pollable after their
    document/project rows are deleted.
    """
    job = _query_owned_job(session, user_id=user_id, job_id=job_id)
    if job is None:
        raise_api_error(
            404,
            ErrorCode.NOT_FOUND,
            "Job not found.",
            job_id=job_id,
        )
    return job


# ---------------------------------------------------------------------------
# Listing (keyset pagination, stable (updated_at, id) DESC order)
# ---------------------------------------------------------------------------


def _parse_project_cursor(cursor: str) -> tuple[datetime, UUID]:
    try:
        payload = decode_cursor(cursor)
        updated_raw = payload.get("u")
        id_raw = payload.get("i")
        if not isinstance(updated_raw, str) or not isinstance(id_raw, str):
            raise ValueError("malformed cursor payload")
        updated_at = datetime.fromisoformat(updated_raw)
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        project_id = UUID(id_raw)
    except (ValueError, TypeError) as exc:
        raise_api_error(
            422,
            ErrorCode.VALIDATION_ERROR,
            "Invalid pagination cursor.",
        )
        raise exc  # pragma: no cover - raise_api_error always raises
    return updated_at, project_id


def list_owned_projects(
    session: Session,
    *,
    user_id: UUID,
    cursor: str | None,
    limit: int,
) -> tuple[list[Project], str | None]:
    """Return ``(items, next_cursor)`` for live projects of ``user_id``.

    Ordering ``updated_at DESC, id DESC`` matches the
    ``ix_projects_owner_live`` index.  ``next_cursor`` is ``None`` on
    the last page.  Malformed cursors raise ``422 validation_error``.
    """
    if limit < 1 or limit > 200:
        raise_api_error(
            422,
            ErrorCode.VALIDATION_ERROR,
            "limit must be between 1 and 200.",
        )

    statement = (
        select(Project)
        .where(
            Project.user_id == user_id,
            Project.deleted_at.is_(None),
        )
        .order_by(Project.updated_at.desc(), Project.id.desc())
        .limit(limit + 1)
    )
    if cursor is not None:
        updated_before, id_before = _parse_project_cursor(cursor)
        statement = statement.where(
            or_(
                Project.updated_at < updated_before,
                (Project.updated_at == updated_before) & (Project.id < id_before),
            )
        )
    rows = list(session.execute(statement).scalars().all())
    next_cursor: str | None = None
    if len(rows) > limit:
        rows = rows[:limit]
        last = rows[-1]
        next_cursor = encode_cursor(
            {"u": last.updated_at.isoformat(), "i": str(last.id)}
        )
    return rows, next_cursor


# ---------------------------------------------------------------------------
# Writes (flush only; handler commits)
# ---------------------------------------------------------------------------


def create_owned_project(
    session: Session,
    *,
    user_id: UUID,
    name: str,
    description: str | None,
) -> Project:
    """Create a project owned by ``user_id``.  Name is already trimmed by DTO."""
    project = Project(user_id=user_id, name=name, description=description)
    session.add(project)
    session.flush()
    return project


def update_owned_project(
    session: Session,
    project: Project,
    *,
    name: str | None,
    description: str | None,
    fields_set: set[str],
) -> Project:
    """Apply a PATCH body to ``project``.

    ``fields_set`` (``model_fields_set``) distinguishes omitted fields
    (no change) from explicit values: an explicit ``description: null``
    clears the description, while an explicit ``name: null`` is
    rejected (name can never be null).  An empty set means the caller
    sent no changes (handler maps this to ``422`` before calling).
    """
    if "name" in fields_set:
        if name is None or not name.strip():
            raise_api_error(
                422,
                ErrorCode.VALIDATION_ERROR,
                "name must not be blank.",
                project_id=project.id,
            )
        project.name = name.strip()
    if "description" in fields_set:
        # None / blank => cleared (DTO normalizes blank to None already).
        project.description = None if description is None else (description.strip() or None)
    session.flush()
    return project


def tombstone_project(
    session: Session,
    project: Project,
    *,
    now: datetime | None = None,
) -> Project:
    """Mark a project deleted (tombstone); cleanup jobs are enqueued by the caller."""
    if project.deleted_at is None:
        project.deleted_at = now or _utcnow()
    session.flush()
    return project


__all__ = [
    "create_owned_project",
    "get_owned_conversation_or_404",
    "get_owned_document_or_404",
    "get_owned_job_or_404",
    "get_owned_project_or_404",
    "list_owned_projects",
    "project_to_dto",
    "raise_api_error",
    "tombstone_project",
    "update_owned_project",
]
