"""Server-side authentication dependencies.

Server-side identity for the v2 API:

* Next.js owns the Appwrite email-OTP/session lifecycle and forwards a
  short-lived Appwrite JWT as ``Authorization: Bearer ...``.
* FastAPI verifies that JWT through Appwrite and resolves the internal
  PostgreSQL ``users.id`` (never a browser-supplied owner header or ID).

Public dependency surface::

    from app.auth import PrincipalDep, OnboardedPrincipalDep, get_principal

``PrincipalDep`` yields the verified :class:`AuthenticatedUser` (first
login bootstraps the row idempotently).  ``OnboardedPrincipalDep`` also
enforces profile completion (403 ``onboarding_required``).  Both are
``Annotated`` FastAPI dependencies; the underlying handlers are
synchronous because Appwrite/PG calls block.
"""

__all__ = [
    "OnboardedPrincipalDep",
    "PrincipalDep",
    "PrincipalResolver",
    "get_principal",
    "get_principal_resolver",
    "require_onboarded",
    "verify_appwrite_identity",
]

_EXPORTS = {
    "OnboardedPrincipalDep": "OnboardedPrincipalDep",
    "PrincipalDep": "PrincipalDep",
    "PrincipalResolver": "PrincipalResolver",
    "get_principal": "get_principal",
    "get_principal_resolver": "get_principal_resolver",
    "require_onboarded": "require_onboarded",
    "verify_appwrite_identity": "verify_appwrite_identity",
}


def __getattr__(name: str):
    # Lazy imports: app.repositories.users imports app.auth.errors, while
    # app.auth.principal imports app.repositories.users. Eager imports here
    # would create a cycle; defer principal until first use (PEP 562).
    if name in _EXPORTS:
        from app.auth import principal

        return getattr(principal, _EXPORTS[name])
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)
