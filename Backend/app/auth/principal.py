"""Appwrite JWT verification and internal-principal resolution.

Implements the frozen :class:`PrincipalResolver` protocol from
``app.schemas.services``: ``resolve_principal(authorization_header)``
verifies a short-lived Appwrite JWT through Appwrite and resolves the
internal PostgreSQL ``users.id``.  First login bootstraps the
application-user row (concurrency-safe upsert by the verified
``appwrite_user_id``); verified-email changes are synchronized without
ever merging identities.

Fail-closed rules:

* Missing/malformed ``Authorization`` header -> 401 ``unauthenticated``.
* Appwrite rejects the credential (401/403, expired, revoked) ->
  401 ``unauthenticated``.
* Appwrite is unreachable, returns 5xx, or the backend has no
  endpoint/project configured -> 503 ``service_unavailable`` (a
  retryable outage, never an anonymous principal).
* An identity without an email cannot bootstrap a ``users`` row ->
  401 ``unauthenticated`` (email-less accounts have no workspace).

The Appwrite SDK is imported lazily inside the verifier so unit tests
can double the verification boundary without importing the SDK, and
the repository boundary (``bootstrap_user``) is likewise a module-level
call that tests may patch.

FastAPI consumers must depend on :data:`PrincipalDep` or
:data:`OnboardedPrincipalDep` -- never on a browser-supplied owner
header or ID::

    from app.auth import PrincipalDep, OnboardedPrincipalDep

    @router.get("/projects")
    def list_projects(principal: PrincipalDep): ...

    @router.post("/projects")
    def create_project(principal: OnboardedPrincipalDep): ...
"""

from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Annotated, Any

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.auth import config
from app.auth.errors import onboarding_required, service_unavailable, unauthenticated
from app.db.session import request_transaction
from app.repositories.users import bootstrap_user
from app.schemas.users import AuthenticatedUser

# callable that turns a raw bearer token into the verified identity dict
# {"appwrite_user_id": str, "email": str}; raises the 401/503 auth errors.
IdentityVerifier = Callable[[str], dict[str, str]]
# factory for the short transaction around bootstrap (A1's
# ``request_transaction`` by default; tests pass a double).
SessionScope = Callable[[], AbstractContextManager[Session]]


def extract_bearer_token(authorization_header: str) -> str:
    """Return the token from ``Authorization: Bearer <token>`` or 401."""
    (scheme, separator, token) = authorization_header.partition(" ")
    if not separator or scheme.lower() != "bearer":
        raise unauthenticated()
    token = token.strip()
    if not token or any(character.isspace() for character in token):
        raise unauthenticated()
    return token


def verify_appwrite_identity(token: str) -> dict[str, str]:
    """Verify ``token`` through Appwrite; return the verified identity.

    The Appwrite server performs the signature/expiry checks: we send
    the JWT in ``x-appwrite-jwt`` and read back the account.  Client
    auth rejections map to 401; transport/5xx/configuration problems
    map to a retryable 503 (fail closed).
    """
    project_id = config.appwrite_project_id()
    endpoint = config.appwrite_endpoint()
    if not project_id:
        raise service_unavailable(
            "Identity verification is not configured. Please try again."
        )

    try:
        from appwrite.client import Client
        from appwrite.exception import AppwriteException
        from appwrite.services.account import Account
    except Exception:
        raise service_unavailable() from None

    client = Client().set_endpoint(endpoint).set_project(project_id).set_jwt(token)
    try:
        user: Any = Account(client).get()
    except AppwriteException as error:
        code = getattr(error, "code", None)
        if isinstance(code, int) and code in (401, 403):
            raise unauthenticated() from None
        raise service_unavailable() from None
    except Exception:
        raise service_unavailable() from None

    appwrite_user_id = str(user.get("$id") or "").strip()
    email = str(user.get("email") or "").strip().lower()
    if not appwrite_user_id or not email:
        raise unauthenticated("An email account is required to access NoteMind.")
    return {"appwrite_user_id": appwrite_user_id, "email": email}


class PrincipalResolver:
    """Concrete ``PrincipalResolver`` (see ``app.schemas.services``).

    Synchronous by design: Appwrite and PostgreSQL calls block, so the
    FastAPI dependencies below are plain ``def`` handlers.
    """

    def __init__(
        self,
        verify_identity: IdentityVerifier | None = None,
        session_scope: SessionScope | None = None,
    ) -> None:
        self._verify_identity = verify_identity or verify_appwrite_identity
        self._session_scope = session_scope or (lambda: request_transaction())

    def resolve_principal(self, authorization_header: str) -> AuthenticatedUser:
        token = extract_bearer_token(authorization_header)
        identity = self._verify_identity(token)
        with self._session_scope() as session:
            user = bootstrap_user(
                session,
                appwrite_user_id=identity["appwrite_user_id"],
                email=identity["email"],
            )
            return AuthenticatedUser(
                id=user.id,
                appwrite_user_id=user.appwrite_user_id,
                email=user.email,
                onboarding_completed=user.onboarding_completed,
            )


_default_resolver: PrincipalResolver | None = None


def get_principal_resolver() -> PrincipalResolver:
    """Default resolver factory (tests override this via FastAPI)."""
    global _default_resolver
    if _default_resolver is None:
        _default_resolver = PrincipalResolver()
    return _default_resolver


def get_principal(
    resolver: Annotated[PrincipalResolver, Depends(get_principal_resolver)],
    authorization: Annotated[str | None, Header()] = None,
) -> AuthenticatedUser:
    """FastAPI dependency: the verified principal for this request."""
    return resolver.resolve_principal(authorization or "")


def require_onboarded(
    principal: Annotated[AuthenticatedUser, Depends(get_principal)],
) -> AuthenticatedUser:
    """FastAPI dependency: the principal, with profile completion enforced."""
    if not principal.onboarding_completed:
        raise onboarding_required()
    return principal


# Reusable Annotated aliases for resource services (A3/A5).
PrincipalDep = Annotated[AuthenticatedUser, Depends(get_principal)]
OnboardedPrincipalDep = Annotated[AuthenticatedUser, Depends(require_onboarded)]

__all__ = [
    "IdentityVerifier",
    "OnboardedPrincipalDep",
    "PrincipalDep",
    "PrincipalResolver",
    "SessionScope",
    "extract_bearer_token",
    "get_principal",
    "get_principal_resolver",
    "require_onboarded",
    "verify_appwrite_identity",
]
