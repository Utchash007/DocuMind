"""Session factories and transaction patterns for the v2 database.

Design rules (see ``docs/v2-contracts.md`` and ``plan.md`` section 4.3):

* Sessions are synchronous (SQLAlchemy 2 ``Session``); the existing
  FastAPI handlers and the PDF worker are blocking, so no async session
  variant is provided.
* **Never hold a database transaction open across a provider call**
  (Appwrite Storage/Auth, Chroma, Groq, Hugging Face).  Claim/persist in a
  short transaction, commit, call the provider, then persist the result
  in a second short transaction guarded by the generation/lease fencing
  token.
* Database URLs come from the environment only.  ``environment="test"``
  reads ``TEST_DATABASE_URL`` exclusively and raises if it is missing --
  there is intentionally no silent fallback to ``DATABASE_URL``, so tests
  can never run against (or migrate) the application database by accident.
* Nothing in this module connects at import time.  Engines/session
  factories are created lazily and cached per (url, pool settings).
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import Session, sessionmaker

ENV_TEST = "test"
ENV_DEFAULT = "default"

# Cache: database_url -> sessionmaker.  Factories are cheap to build but
# engines own a connection pool, so exactly one engine per URL is kept.
_FACTORY_CACHE: dict[str, sessionmaker[Session]] = {}


def validate_test_database_url(url: str, application_url: str | None = None) -> str:
    """Validate an explicitly supplied, disposable PostgreSQL test target.

    Pure configuration check: never creates an engine or opens a connection.
    """
    try:
        target = make_url(url)
        if target.get_backend_name() != "postgresql" or not re.search(r"(^|[_-])tests?([_-]|$)", target.database or "", re.IGNORECASE):
            raise ValueError("not a clearly named PostgreSQL test database")
        # Connection target overrides can defeat host/database comparison.
        if any(key in target.query for key in ("host", "hostaddr", "port", "dbname", "service")):
            raise ValueError("connection target overrides are not allowed")
        if application_url:
            application = make_url(application_url)
            def identity(value):
                return ((value.host or "").lower(), value.port or 5432, value.database)
            if identity(target) == identity(application):
                raise ValueError("same database as the application")
    except (ArgumentError, ValueError, TypeError) as exc:
        raise RuntimeError("TEST_DATABASE_URL must target a separate, clearly test-named PostgreSQL database.") from exc
    return url


def get_database_url(environment: str | None = None) -> str:
    """Return the database URL for ``environment`` from the environment.

    ``environment="test"`` requires ``TEST_DATABASE_URL``; every other
    value (including ``None``) requires ``DATABASE_URL``.  Missing or
    empty variables raise :class:`RuntimeError` instead of falling back.
    """
    env = (environment or ENV_DEFAULT).strip().lower()
    variable = "TEST_DATABASE_URL" if env == ENV_TEST else "DATABASE_URL"
    url = os.environ.get(variable, "").strip()
    if not url:
        raise RuntimeError(
            f"{variable} is required (environment={env!r}) but is not set. "
            "Refusing to fall back to another database URL."
        )
    if env == ENV_TEST:
        return validate_test_database_url(url, os.environ.get("DATABASE_URL", "").strip() or None)
    return url


def make_engine(database_url: str | None = None, *, environment: str | None = None) -> Engine:
    """Create a synchronous SQLAlchemy engine for PostgreSQL (psycopg)."""
    url = database_url or get_database_url(environment)
    return create_engine(
        url,
        pool_pre_ping=True,  # tolerate idle/balancer-dropped connections
        future=True,
    )


def make_session_factory(
    database_url: str | None = None,
    *,
    environment: str | None = None,
    expire_on_commit: bool = False,
) -> sessionmaker[Session]:
    """Return a cached ``sessionmaker`` for the resolved database URL.

    ``expire_on_commit=False`` (default) keeps attribute access safe after
    the transaction commits, which is how the request handlers in this
    codebase serialize DTOs.  Note the cache key includes the URL only:
    the first caller's ``expire_on_commit`` wins for a given URL, so use
    :func:`make_worker_session_factory` explicitly for worker code that
    needs detached instances.
    """
    url = database_url or get_database_url(environment)
    cached = _FACTORY_CACHE.get(url)
    if cached is not None:
        return cached
    factory: sessionmaker[Session] = sessionmaker(
        bind=make_engine(url),
        autoflush=False,
        autocommit=False,
        expire_on_commit=expire_on_commit,
        future=True,
    )
    _FACTORY_CACHE[url] = factory
    return factory


def get_session_factory(environment: str | None = None) -> sessionmaker[Session]:
    """Lazily resolve the request-scoped session factory from the env."""
    return make_session_factory(environment=environment)


def make_worker_session_factory(
    database_url: str | None = None,
    *,
    environment: str | None = None,
) -> sessionmaker[Session]:
    """Session factory for the PDF worker (separate, uncached-by-default).

    Workers must not share the request factory's engine lifecycle: the
    worker process outlives requests and claims jobs in many short
    transactions.  Each call builds a fresh factory bound to its own
    engine; the worker entry point owns and disposes it.
    """
    url = database_url or get_database_url(environment)
    return sessionmaker(
        bind=make_engine(url),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )


@contextmanager
def request_transaction(
    session_factory: sessionmaker[Session] | None = None,
) -> Iterator[Session]:
    """Run a short unit of work: commit on success, rollback on error.

    Usage pattern for every repository/service write path::

        with request_transaction() as session:
            ... pure DB reads/writes only, no provider calls ...

    The session is closed on exit.  Keep the ``with`` body free of
    network calls; see the module docstring.
    """
    factory = session_factory or get_session_factory()
    with factory() as session:
        try:
            with session.begin():
                yield session
        except Exception:
            raise


@contextmanager
def worker_transaction(
    session_factory: sessionmaker[Session] | None = None,
) -> Iterator[Session]:
    """Worker counterpart of :func:`request_transaction` (same semantics)."""
    if session_factory is None:
        session_factory = make_worker_session_factory()
    with session_factory() as session:
        try:
            with session.begin():
                yield session
        except Exception:
            raise


def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding a request-scoped session.

    Handlers that only read (or that manage their own short transactions
    via :func:`request_transaction`) use this dependency.  It never
    commits implicitly; write handlers must use ``request_transaction``
    or an explicit ``session.begin()`` block so commit boundaries stay
    visible in code review.
    """
    factory = get_session_factory()
    with factory() as session:
        yield session


# Alias for Annotated dependency declarations (FastAPI skill convention).
DbSessionDep = Annotated[Session, Depends(get_db)]

__all__ = [
    "DbSessionDep",
    "ENV_DEFAULT",
    "ENV_TEST",
    "get_database_url",
    "get_db",
    "get_session_factory",
    "make_engine",
    "make_session_factory",
    "make_worker_session_factory",
    "request_transaction",
    "worker_transaction",
]
