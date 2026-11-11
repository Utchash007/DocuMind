"""Application-user DTOs: ``GET/PATCH /me``."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.common import CamelModel, RequestModel


def derive_onboarding_completed(name: str | None, date_of_birth: date | None) -> bool:
    """Server-side onboarding derivation: both required fields present.

    ``onboarding_completed`` is never client-settable; the backend sets it
    only when name (non-blank after trim) and date of birth (not in the
    future) are both present, mirroring the DB CHECK
    ``onboarding_requires_profile``.
    """
    return bool(
        name is not None
        and name.strip() != ""
        and date_of_birth is not None
        and date_of_birth <= date.today()
    )


class ApplicationUser(CamelModel):
    """Public ``/me`` payload.

    Deliberately excludes ``appwrite_user_id`` (server-only identity
    mapping) and any session/OTP material.
    """

    id: UUID
    email: str
    name: str | None = None
    date_of_birth: date | None = None
    onboarding_completed: bool
    created_at: datetime
    updated_at: datetime


class ProfileUpdateRequest(RequestModel):
    """``PATCH /me`` body.  Unknown fields (incl. ``onboardingCompleted``,
    ``id``, ``email``) are rejected with 422."""

    name: str = Field(min_length=1, max_length=150)
    date_of_birth: date

    @field_validator("name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("name must not be blank")
        return stripped

    @field_validator("date_of_birth")
    @classmethod
    def _dob_not_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("date_of_birth must not be in the future")
        return value


# Internal (non-wire) principal resolved from a verified Appwrite identity.
# Lives here so A2 and every resource service share one shape; it is never
# serialized to the browser.
class AuthenticatedUser(CamelModel):
    """Verified principal: internal user plus its Appwrite mapping."""

    id: UUID
    appwrite_user_id: str
    email: str
    onboarding_completed: bool


__all__ = [
    "ApplicationUser",
    "AuthenticatedUser",
    "ProfileUpdateRequest",
    "derive_onboarding_completed",
]
