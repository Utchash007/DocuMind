"""Owner-scoped project API routes.

Routes (FastAPI paths; browser calls go via ``/api/backend``)::

    GET    /projects                  paginated owner-scoped listing
    POST   /projects                  create (name/description) -> 201
    GET    /projects/{project_id}     read
    PATCH  /projects/{project_id}     update
    DELETE /projects/{project_id}     coordinated deletion -> 202

All handlers are synchronous (blocking PG), use ``Annotated``
parameters, and return DTOs (camelCase via serialization aliases).
Every route requires a verified principal **and** completed
onboarding (``403 onboarding_required`` otherwise); ownership is
always the internal ``users.id`` from the principal — never a
client-supplied owner header.

Principal resolution
------------------------------------
``get_current_principal`` delegates to the configured Appwrite verifier
and internal-user resolver. ``CurrentPrincipalDep`` exposes it to routes.

Database wiring
---------------
Reads/writes use the ``get_db`` session dependency.
Handlers ``flush`` via repositories and ``commit`` here;
no transaction is held across Storage/Chroma/provider calls.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.documents import (
    DirectJobQueue,
    enqueue_document_delete,
    get_job_queue,
    list_live_documents_for_project,
    tombstone_document,
)
from app.repositories.projects import (
    create_owned_project,
    get_owned_project_or_404,
    list_owned_projects,
    project_to_dto,
    raise_api_error,
    tombstone_project,
    update_owned_project,
)
from app.schemas.common import ErrorCode, PaginatedResponse
from app.schemas.projects import Project as ProjectDto
from app.schemas.projects import (
    ProjectCreateRequest,
    ProjectDeleteAccepted,
    ProjectUpdateRequest,
)
from app.schemas.users import AuthenticatedUser

__all__ = [
    "CurrentPrincipalDep",
    "OnboardedPrincipalDep",
    "SessionDep",
    "get_current_principal",
    "require_onboarded",
    "router",
]


def get_current_principal(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> AuthenticatedUser:
    """Resolve the principal through Appwrite and the internal-user repository.

    Appwrite JWT verification + internal-user resolution via
    ``PrincipalResolver``. Identity comes from validated credentials
    only (plan §4.1.7); tests override this dependency.
    """
    from app.auth.principal import get_principal_resolver

    return get_principal_resolver().resolve_principal(authorization or "")


def require_onboarded(principal: AuthenticatedUser) -> AuthenticatedUser:
    """Enforce completed onboarding for every workspace route."""
    if not principal.onboarding_completed:
        raise_api_error(
            403,
            ErrorCode.ONBOARDING_REQUIRED,
            "Complete your profile before using the workspace.",
        )
    return principal


def _get_onboarded_principal(
    principal: Annotated[AuthenticatedUser, Depends(get_current_principal)],
) -> AuthenticatedUser:
    return require_onboarded(principal)


CurrentPrincipalDep = Annotated[AuthenticatedUser, Depends(get_current_principal)]
OnboardedPrincipalDep = Annotated[AuthenticatedUser, Depends(_get_onboarded_principal)]
SessionDep = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/projects", tags=["projects"])


def _paginated_dto(rows, next_cursor: str | None) -> PaginatedResponse[ProjectDto]:
    return PaginatedResponse[ProjectDto](
        items=[project_to_dto(row) for row in rows],
        next_cursor=next_cursor,
    )


@router.get("", response_model=PaginatedResponse[ProjectDto])
def list_projects(
    principal: OnboardedPrincipalDep,
    session: SessionDep,
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> PaginatedResponse[ProjectDto]:
    """GET /projects -> paginated owner-scoped listing."""
    rows, next_cursor = list_owned_projects(
        session, user_id=principal.id, cursor=cursor, limit=limit
    )
    return _paginated_dto(rows, next_cursor)


@router.post("", response_model=ProjectDto, status_code=201)
def create_project(
    payload: ProjectCreateRequest,
    principal: OnboardedPrincipalDep,
    session: SessionDep,
) -> ProjectDto:
    """POST /projects -> create (system stamps the internal owner)."""
    try:
        project = create_owned_project(
            session,
            user_id=principal.id,
            name=payload.name,
            description=payload.description,
        )
    except Exception:
        session.rollback()
        raise
    session.commit()
    return project_to_dto(project)


@router.get("/{project_id}", response_model=ProjectDto)
def read_project(
    project_id: UUID,
    principal: OnboardedPrincipalDep,
    session: SessionDep,
) -> ProjectDto:
    """GET /projects/{id} -> owner-scoped read (404 if forged/foreign)."""
    project = get_owned_project_or_404(
        session, user_id=principal.id, project_id=project_id
    )
    return project_to_dto(project)


@router.patch("/{project_id}", response_model=ProjectDto)
def update_project(
    project_id: UUID,
    payload: ProjectUpdateRequest,
    principal: OnboardedPrincipalDep,
    session: SessionDep,
) -> ProjectDto:
    """PATCH /projects/{id} -> rename / change description."""
    project = get_owned_project_or_404(
        session, user_id=principal.id, project_id=project_id
    )
    fields_set = set(payload.model_fields_set)
    if not fields_set:
        session.rollback()
        raise_api_error(
            422,
            ErrorCode.VALIDATION_ERROR,
            "Provide at least one field to update.",
            project_id=project_id,
        )
    try:
        project = update_owned_project(
            session,
            project,
            name=payload.name,
            description=payload.description,
            fields_set=fields_set,
        )
    except Exception:
        session.rollback()
        raise
    session.commit()
    return project_to_dto(project)


@router.delete("/{project_id}", response_model=ProjectDeleteAccepted, status_code=202)
def delete_project(
    project_id: UUID,
    principal: OnboardedPrincipalDep,
    session: SessionDep,
    job_queue: Annotated[DirectJobQueue, Depends(get_job_queue)],
) -> ProjectDeleteAccepted:
    """DELETE /projects/{id} -> 202 while cleanup is pending.

    Tombstones the project (hidden from reads immediately), tombstones
    every live document, cancels their processing claims, and enqueues
    one ``delete_document`` cleanup job per document in the same
    transaction.  The hard delete (SQL cascades) happens only after
    every cleanup job succeeds (A4 worker).

    A second delete of an already-tombstoned project returns
    ``409 conflict`` (distinct from ``404`` for never-owned IDs).
    """
    from app.db.queries import get_owned_project as _query_project

    project_or_none = _query_project(
        session,
        user_id=principal.id,
        project_id=project_id,
        include_deleted=True,
    )
    if project_or_none is None:
        raise_api_error(
            404,
            ErrorCode.NOT_FOUND,
            "Project not found.",
            project_id=project_id,
        )
    if project_or_none.deleted_at is not None:
        session.rollback()
        raise_api_error(
            409,
            ErrorCode.CONFLICT,
            "Project is already being deleted.",
            project_id=project_id,
        )
    project = project_or_none

    documents = list_live_documents_for_project(session, project_id=project.id)
    bucket_id: str | None = None
    if documents:
        from app.services.storage import default_bucket_id

        try:
            bucket_id = default_bucket_id()
        except RuntimeError:
            session.rollback()
            raise_api_error(
                503,
                ErrorCode.SERVICE_UNAVAILABLE,
                "Storage is not configured.",
                project_id=project_id,
            )

    try:
        for document in documents:
            tombstone_document(session, document)
            # bucket_id is set whenever documents is non-empty.
            enqueue_document_delete(
                session,
                document=document,
                bucket_id=bucket_id or "",
                job_queue=job_queue,
            )
        tombstone_project(session, project)
    except Exception:
        session.rollback()
        raise
    session.commit()
    return ProjectDeleteAccepted(project_id=project.id, accepted=True)
