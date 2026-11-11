"""NoteMind v2 database layer: models, sessions, and owned lookups.

Import surface for consumers::

    from app.db import Base, User, Project, Document, Conversation, Message, ProcessingJob
    from app.db.session import get_db, request_transaction, worker_transaction
    from app.db.queries import get_owned_project, next_message_position

``Base``/models import without any environment variable set; only the
session factories require ``DATABASE_URL`` / ``TEST_DATABASE_URL``.
"""

from app.db.base import Base, utcnow
from app.db.models import (
    Conversation,
    Document,
    Message,
    ProcessingJob,
    Project,
    User,
)
# Importing models registers all tables on Base.metadata (for Alembic).
from app.db import models as _models  # noqa: F401  (side effect: registration)

__all__ = [
    "Base",
    "Conversation",
    "Document",
    "Message",
    "ProcessingJob",
    "Project",
    "User",
    "utcnow",
]
