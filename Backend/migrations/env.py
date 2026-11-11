"""Alembic environment: URL selection, offline SQL, and metadata.

Environment selection (``alembic -x environment=test ...``):

* ``test``  -> ``TEST_DATABASE_URL`` is *required*; missing/empty raises
  immediately.  There is no fallback to ``DATABASE_URL``.
* anything else (default) -> ``DATABASE_URL`` is required.

Offline mode (``alembic upgrade head --sql``) needs no database and no
environment variables: it emits SQL from the migration files themselves
using a placeholder URL.  This is the only mode allowed to run without
a configured URL -- online commands always fail closed.
"""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Make ``app`` importable when Alembic is invoked from Backend/.
_BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.db.base import Base  # noqa: E402
from app.db import models  # noqa: E402, F401  (registers all tables)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _environment_name() -> str:
    """Parse ``-x environment=<name>`` from the Alembic command line.

    Alembic delivers ``-x`` values as ``config.cmd_opts.x`` (a list of
    ``key=value`` strings); there is no ``Config.get_option`` API.
    """
    raw = getattr(getattr(config, "cmd_opts", None), "x", None) or []
    for item in raw:
        key, sep, value = str(item).partition("=")
        if sep and key.strip() == "environment":
            return value.strip().lower() or "default"
    return "default"


def _database_url() -> str:
    """Resolve the online URL, failing closed when it is not configured."""
    env_name = _environment_name()
    variable = "TEST_DATABASE_URL" if env_name == "test" else "DATABASE_URL"
    url = os.environ.get(variable, "").strip()
    if not url:
        raise RuntimeError(
            f"{variable} is required for Alembic environment {env_name!r} "
            "but is not set. Refusing to fall back to another database URL."
        )
    return url


def run_migrations_offline() -> None:
    """Render migrations to SQL without a live database."""
    context.configure(
        url="postgresql+psycopg://placeholder:placeholder@localhost/placeholder",
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against the environment-selected database."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _database_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
