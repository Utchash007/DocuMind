"""Declarative base and shared column helpers for the v2 PostgreSQL schema.

This module is deliberately importable without a database URL or any
external service: it only defines SQLAlchemy metadata. Consumers
should import the models from :mod:`app.db.models` and session
factories from :mod:`app.db.session`; nothing here opens a connection.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import DateTime, MetaData, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    """Timezone-aware "now" used as the Python-side timestamp default.

    The database also applies ``now()`` as a server default, so rows
    inserted through raw SQL still receive timezone-aware timestamps.
    """
    return datetime.now(timezone.utc)


# Stable, explicit constraint/index names.  The Alembic migration uses the
# same names so model metadata and migrations stay in lockstep.
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_label)s",
    # %(column_0_label)s already renders as "<table>_<column>", so the
    # table name must not be repeated here.
    "uq": "uq_%(column_0_label)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(column_0_label)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """SQLAlchemy 2 declarative base for all v2 tables."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def uuid_pk() -> Mapped[UUID]:
    """Application UUID primary key (Python default + PG server default)."""
    return mapped_column(
        Uuid,  # native UUID on PostgreSQL
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
    )


def created_at_col() -> Mapped[datetime]:
    """Timezone-aware creation timestamp with a ``now()`` server default."""
    return mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )


def updated_at_col() -> Mapped[datetime]:
    """Timezone-aware update timestamp, refreshed on every ORM update."""
    return mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
        onupdate=utcnow,
    )


__all__ = ["Base", "NAMING_CONVENTION", "created_at_col", "updated_at_col", "utcnow", "uuid_pk"]
