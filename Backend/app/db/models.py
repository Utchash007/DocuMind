"""SQLAlchemy 2 models for the NoteMind v2 PostgreSQL schema.

Source contract: ``plan.md`` sections 3.1-3.3 and
``project_db_auth_rag_flow_v2.md`` section 2.7, plus the operational
``processing_jobs`` table.  The Alembic migration
``migrations/versions/a1v2init0001_v2_initial_schema.py`` is the executable
mirror of this file; keep the two in lockstep (``Backend/tests/
test_database.py`` asserts the table/column/index/constraint inventory).

Ownership flow (enforced by application code, not by DB alone):

    document/conversation -> project -> users.id

``processing_jobs`` snapshot columns (``owner_user_id``, ``project_id``,
``target_document_id``) intentionally carry *no* foreign key.  They are
immutable server-set copies that must survive deletion of the user-facing
parent rows so cleanup can be reconciled and ``GET /jobs/{jobId}`` stays
owner-scoped after a project/document is deleted.  Only ``document_id``
is a real FK (``ON DELETE SET NULL``) so the job keeps the live document
while it exists and preserves history afterwards.

The ``messages`` table stores its JSONB payload in the SQL column named
``metadata``.  SQLAlchemy reserves ``metadata`` on declarative models, so
the Python attribute is ``message_metadata`` mapped to column ``metadata``.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
    false,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, created_at_col, updated_at_col, uuid_pk

# ---------------------------------------------------------------------------
# Enumerations (values must match the CHECK constraints and the Pydantic
# enums in app/schemas/common.py exactly).
# ---------------------------------------------------------------------------

DOCUMENT_STATUSES = ("Pending", "Processing", "Completed", "Failed")
MESSAGE_ROLES = ("user", "assistant", "system")
GENERATION_STATUSES = ("pending", "generating", "completed", "failed", "cancelled")
JOB_KINDS = ("process_document", "delete_document")
JOB_STATUSES = (
    "awaiting_upload",
    "queued",
    "running",
    "retry_wait",
    "succeeded",
    "failed",
    "cancelled",
)
# Terminal job states: no further worker transition is allowed.
JOB_TERMINAL_STATUSES = ("succeeded", "failed", "cancelled")
JOB_STAGES = (
    "uploading",
    "extracting",
    "chunking",
    "embedding",
    "indexing",
    "publishing",
    "deleting",
)
# Non-terminal job states participating in the one-active-job-per-target rule.
JOB_NONTERMINAL_STATUSES = ("awaiting_upload", "queued", "running", "retry_wait")


def _in_list(column: str, values: tuple[str, ...]) -> str:
    rendered = ", ".join(f"'{value}'" for value in values)
    return f"{column} IN ({rendered})"


# ---------------------------------------------------------------------------
# users
# ---------------------------------------------------------------------------


class User(Base):
    """Application user. ``id`` is the internal UUID used everywhere.

    ``appwrite_user_id`` links to Appwrite Auth and is unique; ``email`` is
    stored normalized (trimmed, lower-cased) and unique.  Email conflicts
    must never merge identities: consumers upsert by ``appwrite_user_id``
    only (see ``docs/v2-contracts.md``).  Profile fields stay NULL until
    onboarding; the CHECK below forbids ``onboarding_completed = true``
    without a name and a date of birth.
    """

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("email <> '' AND email = btrim(email)", name="email_nonempty"),
        CheckConstraint("email = lower(email)", name="email_normalized"),
        CheckConstraint(
            "name IS NULL OR (btrim(name) <> '' AND length(name) <= 150)",
            name="name_valid",
        ),
        CheckConstraint(
            "date_of_birth IS NULL OR date_of_birth <= CURRENT_DATE",
            name="date_of_birth_not_future",
        ),
        CheckConstraint(
            "NOT onboarding_completed OR "
            "(name IS NOT NULL AND btrim(name) <> '' AND date_of_birth IS NOT NULL)",
            name="onboarding_requires_profile",
        ),
    )

    id: Mapped[UUID] = uuid_pk()
    appwrite_user_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    onboarding_completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()

    projects: Mapped[list["Project"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# projects
# ---------------------------------------------------------------------------


class Project(Base):
    """Workspace owned by exactly one internal user.

    ``deleted_at`` is a coordinated-deletion tombstone: normal reads hide
    tombstoned projects, and the hard delete (with its SQL cascades) only
    happens after every child document's cleanup job has succeeded.
    """

    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint(
            "length(btrim(name)) BETWEEN 1 AND 255", name="name_trimmed_nonempty"
        ),
        CheckConstraint(
            "description IS NULL OR length(btrim(description)) > 0",
            name="description_valid",
        ),
        Index("ix_projects_user_id", "user_id"),
        Index("ix_projects_owner_listing", "user_id", "updated_at", "id"),
        Index(
            "ix_projects_owner_live",
            "user_id",
            "updated_at",
            "id",
            postgresql_where="deleted_at IS NULL",
        ),
    )

    id: Mapped[UUID] = uuid_pk()
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()

    user: Mapped[User] = relationship(back_populates="projects")
    documents: Mapped[list["Document"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# documents
# ---------------------------------------------------------------------------


class Document(Base):
    """One PDF belonging to exactly one project.

    ``file_name`` is a display label only; identity is ``id`` plus the
    unique ``appwrite_file_id``.  Same-name uploads are therefore distinct
    documents.  ``upload_request_id`` makes the initial
    document+job reservation idempotent per project: the same request key
    with different file content must surface as a ``409`` (consumer rule),
    never as a second row.
    """

    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint(
            "length(btrim(file_name)) BETWEEN 1 AND 255", name="file_name_valid"
        ),
        CheckConstraint(
            "content_sha256 IS NULL OR content_sha256 ~ '^[0-9a-f]{64}$'",
            name="content_sha256_hex",
        ),
        CheckConstraint("file_size IS NULL OR file_size > 0", name="file_size_positive"),
        CheckConstraint(
            "mime_type IS NULL OR mime_type = 'application/pdf'", name="mime_type_pdf"
        ),
        CheckConstraint(_in_list("status", DOCUMENT_STATUSES), name="status_valid"),
        CheckConstraint("processing_epoch >= 0", name="processing_epoch_nonnegative"),
        CheckConstraint(
            "chunk_count IS NULL OR chunk_count >= 0", name="chunk_count_nonnegative"
        ),
        CheckConstraint(
            "status <> 'Completed' OR "
            "(file_size IS NOT NULL AND chunk_count IS NOT NULL "
            "AND active_index_version IS NOT NULL AND processed_at IS NOT NULL)",
            name="completed_requires_publish",
        ),
        Index("ix_documents_project_id", "project_id"),
        Index(
            "uq_documents_project_upload_request",
            "project_id",
            "upload_request_id",
            unique=True,
        ),
        Index(
            "ix_documents_project_status",
            "project_id",
            "status",
            "deleted_at",
        ),
        Index(
            "ix_documents_project_live",
            "project_id",
            "status",
            "created_at",
            postgresql_where="deleted_at IS NULL",
        ),
    )

    id: Mapped[UUID] = uuid_pk()
    project_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    appwrite_file_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    chroma_collection: Mapped[str | None] = mapped_column(String(255), nullable=True)
    chroma_document_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default="application/pdf", server_default="application/pdf"
    )
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="Pending", server_default="Pending"
    )
    upload_request_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    content_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    upload_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    processing_epoch: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, server_default="0"
    )
    active_index_version: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    chunk_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()

    project: Mapped[Project] = relationship(back_populates="documents")
    jobs: Mapped[list["ProcessingJob"]] = relationship(
        back_populates="document",
        foreign_keys="ProcessingJob.document_id",
        # ORM-level mirror of the FK's ON DELETE SET NULL.
        passive_deletes=True,
    )


# ---------------------------------------------------------------------------
# conversations
# ---------------------------------------------------------------------------


class Conversation(Base):
    """Independent conversation inside a project.

    Positions of its messages are allocated monotonically (see
    :func:`app.db.queries.next_message_position`); the unique
    ``(conversation_id, position)`` index makes the allocation safe and
    gives deterministic pagination order.
    """

    __tablename__ = "conversations"
    __table_args__ = (
        CheckConstraint(
            "title IS NULL OR length(btrim(title)) BETWEEN 1 AND 255",
            name="title_valid",
        ),
        Index("ix_conversations_project_id", "project_id"),
        Index("ix_conversations_project_activity", "project_id", "updated_at", "id"),
    )

    id: Mapped[UUID] = uuid_pk()
    project_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()

    project: Mapped[Project] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# messages
# ---------------------------------------------------------------------------


class Message(Base):
    """One user/assistant/system turn.

    Generation lifecycle (user rows only): ``pending`` -> ``generating`` ->
    ``completed`` | ``failed`` | ``cancelled``.  The partial unique index
    ``uq_messages_one_active_generation`` hard-enforces at most one
    ``pending``/``generating`` user turn per conversation; the owning
    service must claim/reclaim it transactionally with
    ``generation_token`` fencing before calling any provider.

    ``citations`` holds a JSON array of v2 ``Citation`` objects (see
    ``app/schemas/common.py``); ``message_metadata`` holds
    implementation-controlled diagnostics (model, latency, source snapshot)
    and is stored in the SQL column ``metadata``.
    """

    __tablename__ = "messages"
    __table_args__ = (
        CheckConstraint(_in_list("role", MESSAGE_ROLES), name="role_valid"),
        CheckConstraint("position >= 1", name="position_positive"),
        CheckConstraint("length(content) > 0", name="content_nonempty"),
        CheckConstraint(
            "reply_to_message_id IS NULL OR reply_to_message_id <> id",
            name="reply_not_self",
        ),
        CheckConstraint(
            _in_list("generation_status", GENERATION_STATUSES),
            name="generation_status_valid",
        ),
        CheckConstraint(
            "generation_status IS NULL OR role = 'user'",
            name="generation_status_user_only",
        ),
        CheckConstraint(
            "generation_expires_at IS NULL "
            "OR generation_status IN ('pending', 'generating')",
            name="generation_expiry_only_while_active",
        ),
        CheckConstraint(
            "citations IS NULL OR jsonb_typeof(citations) = 'array'",
            name="citations_is_array",
        ),
        CheckConstraint(
            "metadata IS NULL OR jsonb_typeof(metadata) = 'object'",
            name="metadata_is_object",
        ),
        Index("uq_messages_conversation_position", "conversation_id", "position", unique=True),
        Index(
            "ix_messages_conversation_created",
            "conversation_id",
            "created_at",
            "position",
        ),
        Index(
            "uq_messages_conversation_client_request",
            "conversation_id",
            "client_request_id",
            unique=True,
            postgresql_where="role = 'user' AND client_request_id IS NOT NULL",
        ),
        Index(
            "uq_messages_reply_to",
            "reply_to_message_id",
            unique=True,
            postgresql_where="role = 'assistant' AND reply_to_message_id IS NOT NULL",
        ),
        Index(
            "uq_messages_one_active_generation",
            "conversation_id",
            unique=True,
            postgresql_where=(
                "role = 'user' AND generation_status IN ('pending', 'generating')"
            ),
        ),
        Index("ix_messages_reply_to", "reply_to_message_id"),
        Index("ix_messages_generation_expiry", "generation_expires_at"),
    )

    id: Mapped[UUID] = uuid_pk()
    conversation_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(BigInteger, nullable=False)
    citations: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    # SQL column name is ``metadata``; the Python attribute cannot be
    # ``metadata`` because SQLAlchemy reserves that name on models.
    message_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata", JSONB(none_as_null=True), nullable=True
    )
    client_request_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    reply_to_message_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("messages.id", ondelete="CASCADE"), nullable=True
    )
    generation_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    generation_token: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    generation_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = created_at_col()

    conversation: Mapped[Conversation] = relationship(back_populates="messages")
    reply_to: Mapped["Message | None"] = relationship(
        foreign_keys="Message.reply_to_message_id", remote_side="Message.id"
    )
    replies: Mapped[list["Message"]] = relationship(
        foreign_keys="Message.reply_to_message_id",
        back_populates="reply_to",
        cascade="all, delete-orphan",
    )


# ---------------------------------------------------------------------------
# processing_jobs
# ---------------------------------------------------------------------------


class ProcessingJob(Base):
    """Durable PostgreSQL work queue for PDF processing and cleanup.

    The worker claims due rows with ``FOR UPDATE SKIP LOCKED`` in a short
    transaction, increments ``lease_token`` (fencing token) and
    ``attempt_count`` before releasing the lock, and performs all external
    work (Storage/Chroma/providers) *outside* any open transaction.
    Progress/completion/failure updates must re-check the current
    unexpired ``(lease_owner, lease_token)`` claim.

    Each ``process_document`` attempt gets a fresh ``index_version``
    namespace; deterministic chunk IDs include document/version/page/chunk
    so a stale worker can only write into its obsolete namespace and can
    never switch the document's ``active_index_version`` pointer.
    """

    __tablename__ = "processing_jobs"
    __table_args__ = (
        CheckConstraint(_in_list("kind", JOB_KINDS), name="kind_valid"),
        CheckConstraint(_in_list("status", JOB_STATUSES), name="status_valid"),
        CheckConstraint(
            "stage IS NULL OR " + _in_list("stage", JOB_STAGES), name="stage_valid"
        ),
        CheckConstraint("target_epoch >= 0", name="target_epoch_nonnegative"),
        CheckConstraint("attempt_count >= 0", name="attempt_count_nonnegative"),
        CheckConstraint("max_attempts >= 1", name="max_attempts_positive"),
        CheckConstraint(
            "lease_token IS NULL OR lease_token >= 1", name="lease_token_positive"
        ),
        CheckConstraint(
            "progress_current IS NULL OR progress_current >= 0",
            name="progress_current_nonnegative",
        ),
        CheckConstraint(
            "progress_total IS NULL OR progress_total >= 0",
            name="progress_total_nonnegative",
        ),
        CheckConstraint(
            "progress_current IS NULL OR progress_total IS NULL "
            "OR progress_current <= progress_total",
            name="progress_current_le_total",
        ),
        CheckConstraint(
            "jsonb_typeof(resource_snapshot) = 'object'",
            name="resource_snapshot_is_object",
        ),
        CheckConstraint(
            "finished_at IS NULL OR finished_at >= created_at",
            name="finished_after_created",
        ),
        Index(
            "ix_processing_jobs_due",
            "status",
            "available_at",
            "created_at",
        ),
        Index(
            "ix_processing_jobs_due_claimable",
            "available_at",
            "created_at",
            postgresql_where="status IN ('queued', 'retry_wait')",
        ),
        Index(
            "ix_processing_jobs_lease_expiry",
            "lease_expires_at",
            postgresql_where="status = 'running' AND lease_expires_at IS NOT NULL",
        ),
        Index("ix_processing_jobs_owner", "owner_user_id", "created_at", "id"),
        Index(
            "ix_processing_jobs_document",
            "document_id",
            postgresql_where="document_id IS NOT NULL",
        ),
        Index("ix_processing_jobs_project", "project_id", "created_at", "id"),
        Index("ix_processing_jobs_target", "target_document_id", "created_at", "id"),
        Index(
            "uq_processing_jobs_one_nonterminal_per_target_kind",
            "target_document_id",
            "kind",
            unique=True,
            postgresql_where=(
                "status IN ('awaiting_upload', 'queued', 'running', 'retry_wait')"
            ),
        ),
    )

    id: Mapped[UUID] = uuid_pk()
    # Live link while the document exists; SET NULL preserves job history.
    document_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )
    # Immutable snapshots (no FK): survive document/project deletion.
    owner_user_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    project_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    target_document_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    resource_snapshot: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}"
    )
    target_epoch: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, server_default="0"
    )
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    stage: Mapped[str | None] = mapped_column(String(30), nullable=True)
    attempt_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    max_attempts: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3, server_default="3"
    )
    available_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        # Defaulted by callers to created_at/now(); server default covers raw SQL.
        server_default=func.now(),
    )
    lease_owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lease_token: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    lease_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    index_version: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    progress_current: Mapped[int | None] = mapped_column(Integer, nullable=True)
    progress_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    document: Mapped[Document | None] = relationship(back_populates="jobs")


__all__ = [
    "Conversation",
    "DOCUMENT_STATUSES",
    "Document",
    "GENERATION_STATUSES",
    "JOB_KINDS",
    "JOB_NONTERMINAL_STATUSES",
    "JOB_STAGES",
    "JOB_STATUSES",
    "JOB_TERMINAL_STATUSES",
    "MESSAGE_ROLES",
    "Message",
    "ProcessingJob",
    "Project",
    "User",
]
