"""Server-side Appwrite configuration for identity verification.

The backend never creates sessions or OTPs; it only validates the
short-lived JWT that Next.js minted from the user's session.  That
needs the Appwrite endpoint and project ID only -- no API key is
required (verification happens Appwrite-side via the JWT header, which
is exactly what the session-bound Appwrite SDK call does).

Variables are read lazily at request time (never at import) so tests
and the worker can run without them.  Missing values fail closed with
a retryable ``service_unavailable`` error, never with a pass.
"""

from __future__ import annotations

import os

DEFAULT_ENDPOINT = "https://cloud.appwrite.io/v1"


def appwrite_endpoint() -> str:
    endpoint = (
        os.environ.get("APPWRITE_ENDPOINT", "").strip()
        or os.environ.get("NEXT_PUBLIC_APPWRITE_ENDPOINT", "").strip()
    )
    return (endpoint or DEFAULT_ENDPOINT).rstrip("/")


def appwrite_project_id() -> str:
    return (
        os.environ.get("APPWRITE_PROJECT_ID", "").strip()
        or os.environ.get("NEXT_PUBLIC_APPWRITE_PROJECT_ID", "").strip()
    )


def appwrite_configured() -> bool:
    return bool(appwrite_project_id())


__all__ = [
    "DEFAULT_ENDPOINT",
    "appwrite_configured",
    "appwrite_endpoint",
    "appwrite_project_id",
]
