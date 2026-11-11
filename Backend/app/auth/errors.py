"""Frozen error helpers for authentication (``docs/v2-contracts.md``).

Every v2 error uses the FastAPI envelope ``{"detail": ApiError}`` with a
stable machine ``code``.  Authentication failures are 401
``unauthenticated``; an authenticated but incomplete profile is 403
``onboarding_required``; provider verification outages fail closed as a
retryable 503 ``service_unavailable`` (never an anonymous principal);
inaccessible resources are 404 ``not_found``.
"""

from __future__ import annotations

from fastapi import HTTPException

from app.schemas.common import ApiError, ErrorCode


def _error(
    status_code: int,
    code: ErrorCode,
    message: str,
) -> HTTPException:
    error = ApiError(code=code, message=message)
    return HTTPException(status_code=status_code, detail=error.model_dump(by_alias=True))


def unauthenticated(message: str = "Sign in to access NoteMind.") -> HTTPException:
    return _error(401, ErrorCode.UNAUTHENTICATED, message)


def onboarding_required(
    message: str = "Complete your profile to continue.",
) -> HTTPException:
    return _error(403, ErrorCode.ONBOARDING_REQUIRED, message)


def forbidden(message: str = "You do not have access to this resource.") -> HTTPException:
    return _error(403, ErrorCode.FORBIDDEN, message)


def not_found(message: str = "The requested resource does not exist.") -> HTTPException:
    return _error(404, ErrorCode.NOT_FOUND, message)


def conflict(message: str) -> HTTPException:
    return _error(409, ErrorCode.CONFLICT, message)


def service_unavailable(
    message: str = "Identity verification is temporarily unavailable. Please try again.",
) -> HTTPException:
    return _error(503, ErrorCode.SERVICE_UNAVAILABLE, message)


__all__ = [
    "conflict",
    "forbidden",
    "not_found",
    "onboarding_required",
    "service_unavailable",
    "unauthenticated",
]
