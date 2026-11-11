"""``GET/PATCH /me``: application-user bootstrap and onboarding.

``GET /me`` is idempotent and safe to retry: the principal dependency
already bootstrapped the row, so this handler just returns it (a
PostgreSQL outage after OTP verification is therefore retryable
without resubmitting the consumed code).  ``PATCH /me`` accepts exactly
``name`` + ``dateOfBirth`` (both required, unknown fields rejected by
``ProfileUpdateRequest``); onboarding completion is derived on the
server.

Registration in ``app/main.py``::

    from app.api.users import router as users_router
    app.include_router(users_router)

Workspace routes can use ``OnboardedPrincipalDep`` from
``app.auth``; profile/bootstrap/sign-out and ``/onboarding`` stay
reachable for incomplete users through plain ``PrincipalDep``.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.auth import PrincipalDep
from app.auth.errors import unauthenticated
from app.db.session import request_transaction
from app.repositories.users import get_user, update_profile
from app.schemas.users import ApplicationUser, ProfileUpdateRequest

router = APIRouter(prefix="/me", tags=["users"])


@router.get("", response_model=ApplicationUser, response_model_by_alias=True)
def read_me(principal: PrincipalDep) -> ApplicationUser:
    """Return (and idempotently bootstrap) the signed-in application user."""
    with request_transaction() as session:
        user = get_user(session, principal.id)
        if user is None:
            raise unauthenticated()
        return ApplicationUser.model_validate(user)


@router.patch("", response_model=ApplicationUser, response_model_by_alias=True)
def update_me(payload: ProfileUpdateRequest, principal: PrincipalDep) -> ApplicationUser:
    """Complete or update the caller's profile; onboarding is derived."""
    with request_transaction() as session:
        user = update_profile(
            session,
            user_id=principal.id,
            name=payload.name,
            date_of_birth=payload.date_of_birth,
        )
        if user is None:
            raise unauthenticated()
        return ApplicationUser.model_validate(user)


__all__ = ["router"]
