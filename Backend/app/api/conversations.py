"""Conversation routes and shared principal/session-factory dependencies.

Authorization follows ``conversation -> project -> users.id``
(``app.db.queries``); missing and unowned resources both return
``404 not_found``.  Workspace routes require completed onboarding
(``403 onboarding_required``).  Handlers are synchronous (blocking DB
work runs in the threadpool) and use ``Annotated`` dependencies per
the FastAPI skill.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from sqlalchemy.orm import sessionmaker

from app.db.session import get_session_factory
from app.repositories import conversations as repo
from app.repositories.conversations import CursorError
from app.schemas.common import ApiError, ErrorCode, PaginatedResponse
from app.schemas.conversations import (
    Conversation as ConversationDto,
)
from app.schemas.conversations import (
    ConversationCreateRequest,
    ConversationDeleteAccepted,
    ConversationUpdateRequest,
)
from app.schemas.users import AuthenticatedUser

RouterDep = APIRouter(prefix="/projects/{project_id}/conversations", tags=["conversations"])
router = RouterDep


# ---------------------------------------------------------------------------
# Shared dependencies
# ---------------------------------------------------------------------------


def api_error(
    status_code: int,
    code: ErrorCode,
    message: str,
    **ids: object,
) -> HTTPException:
    """Build an ``{"detail": ApiError}`` HTTP error (frozen envelope)."""
    payload = ApiError(code=code, message=message, **ids).model_dump(  # type: ignore[arg-type]
        by_alias=True, mode="json"
    )
    return HTTPException(status_code=status_code, detail=payload)


def get_current_principal(request: Request) -> AuthenticatedUser:
    """Verify the Appwrite principal and require completed onboarding."""
    authorization = request.headers.get("Authorization", "").strip()
    from app.auth.principal import get_principal_resolver

    try:
        user = get_principal_resolver().resolve_principal(authorization)
    except HTTPException:
        raise
    except Exception as exc:  # provider outage fails closed (retryable)
        raise api_error(
            503,
            ErrorCode.SERVICE_UNAVAILABLE,
            "Identity verification is temporarily unavailable.",
        ) from exc
    if not bool(getattr(user, "onboarding_completed", False)):
        raise api_error(
            403,
            ErrorCode.ONBOARDING_REQUIRED,
            "Complete your profile before using the workspace.",
        )
    return user


def get_session_factory_dep() -> sessionmaker:
    """Return the production session factory for short request transactions."""
    return get_session_factory()


PrincipalDep = Annotated[AuthenticatedUser, Depends(get_current_principal)]
SessionFactoryDep = Annotated[sessionmaker, Depends(get_session_factory_dep)]


# ---------------------------------------------------------------------------
# Conversation routes
# ---------------------------------------------------------------------------


@router.get("", response_model=PaginatedResponse[ConversationDto], response_model_by_alias=True)
def list_conversations(
    project_id: Annotated[UUID, Path()],
    principal: PrincipalDep,
    factory: SessionFactoryDep,
    cursor: Annotated[str | None, Query(description="Opaque nextCursor from the previous page")] = None,
    limit: Annotated[int, Query(ge=1, le=200, description="Bounded page size (1-200)")] = 50,
) -> PaginatedResponse[ConversationDto]:
    """List a project's conversations newest-activity-first (``{items, nextCursor}``)."""
    from app.db.session import request_transaction

    try:
        with request_transaction(factory) as session:
            return repo.list_conversations(
                session,
                user_id=principal.id,
                project_id=project_id,
                cursor=cursor,
                limit=limit,
            )
    except repo.NotFoundError as exc:
        raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc
    except CursorError as exc:
        raise api_error(422, ErrorCode.VALIDATION_ERROR, str(exc)) from exc


@router.post("", response_model=ConversationDto, status_code=201, response_model_by_alias=True)
def create_conversation(
    project_id: Annotated[UUID, Path()],
    body: ConversationCreateRequest,
    principal: PrincipalDep,
    factory: SessionFactoryDep,
) -> ConversationDto:
    """Create an independent conversation (``201`` with the persisted row)."""
    from app.db.session import request_transaction

    try:
        with request_transaction(factory) as session:
            return repo.create_conversation(
                session,
                user_id=principal.id,
                project_id=project_id,
                title=body.title,
            )
    except repo.NotFoundError as exc:
        raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc


@router.get("/{conversation_id}", response_model=ConversationDto, response_model_by_alias=True)
def get_conversation(
    project_id: Annotated[UUID, Path()],
    conversation_id: Annotated[UUID, Path()],
    principal: PrincipalDep,
    factory: SessionFactoryDep,
) -> ConversationDto:
    """Read one owned conversation."""
    from app.db.session import request_transaction

    try:
        with request_transaction(factory) as session:
            return repo.get_conversation(
                session,
                user_id=principal.id,
                project_id=project_id,
                conversation_id=conversation_id,
            )
    except repo.NotFoundError as exc:
        raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc


@router.patch("/{conversation_id}", response_model=ConversationDto, response_model_by_alias=True)
def rename_conversation(
    project_id: Annotated[UUID, Path()],
    conversation_id: Annotated[UUID, Path()],
    body: ConversationUpdateRequest,
    principal: PrincipalDep,
    factory: SessionFactoryDep,
) -> ConversationDto:
    """Rename an owned conversation."""
    from app.db.session import request_transaction

    try:
        with request_transaction(factory) as session:
            return repo.rename_conversation(
                session,
                user_id=principal.id,
                project_id=project_id,
                conversation_id=conversation_id,
                title=body.title,
            )
    except repo.NotFoundError as exc:
        raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc


@router.delete("/{conversation_id}", response_model=ConversationDeleteAccepted, response_model_by_alias=True)
def delete_conversation(
    project_id: Annotated[UUID, Path()],
    conversation_id: Annotated[UUID, Path()],
    principal: PrincipalDep,
    factory: SessionFactoryDep,
) -> ConversationDeleteAccepted:
    """Delete a conversation and its messages synchronously (``200``)."""
    from app.db.session import request_transaction

    try:
        with request_transaction(factory) as session:
            deleted_id = repo.delete_conversation(
                session,
                user_id=principal.id,
                project_id=project_id,
                conversation_id=conversation_id,
            )
    except repo.NotFoundError as exc:
        raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc
    return ConversationDeleteAccepted(conversation_id=deleted_id, accepted=True)


__all__ = ["get_current_principal", "get_session_factory_dep", "router"]
