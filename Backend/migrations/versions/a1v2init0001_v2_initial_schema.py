"""NoteMind v2 initial schema: users, projects, documents, conversations,
messages, processing_jobs.

Revision ID: a1v2init0001
Revises:
Create Date: 2026-11-09

Executable mirror of ``app/db/models.py`` (plan.md sections 3.1-3.3).
Reversible: ``alembic downgrade base`` drops the six tables and their
indexes.  The ``pgcrypto`` extension is left installed on downgrade (it
is shared infrastructure; dropping it could break unrelated objects).

Constraint/index naming follows ``app.db.base.NAMING_CONVENTION``:
``pk_<table>``, ``ck_<table>_<name>``, ``uq_<table>_<column>``,
``fk_<table>_<column>_<referred_table>``, plus the explicit ``ix_*`` /
``uq_*`` index names declared in the models.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a1v2init0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UUID = sa.Uuid(native_uuid=True)
TS = sa.DateTime(timezone=True)
NOW = sa.text("now()")
NEW_UUID = sa.text("gen_random_uuid()")


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # ---------------------------------------------------------------- users
    op.create_table(
        "users",
        sa.Column("id", UUID, nullable=False, server_default=NEW_UUID),
        sa.Column("appwrite_user_id", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(150), nullable=True),
        sa.Column("date_of_birth", sa.Date, nullable=True),
        sa.Column(
            "onboarding_completed",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("created_at", TS, nullable=False, server_default=NOW),
        sa.Column("updated_at", TS, nullable=False, server_default=NOW),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("appwrite_user_id", name="uq_users_appwrite_user_id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.CheckConstraint(
            "email <> '' AND email = btrim(email)", name="ck_users_email_nonempty"
        ),
        sa.CheckConstraint("email = lower(email)", name="ck_users_email_normalized"),
        sa.CheckConstraint(
            "name IS NULL OR (btrim(name) <> '' AND length(name) <= 150)",
            name="ck_users_name_valid",
        ),
        sa.CheckConstraint(
            "date_of_birth IS NULL OR date_of_birth <= CURRENT_DATE",
            name="ck_users_date_of_birth_not_future",
        ),
        sa.CheckConstraint(
            "NOT onboarding_completed OR "
            "(name IS NOT NULL AND btrim(name) <> '' AND date_of_birth IS NOT NULL)",
            name="ck_users_onboarding_requires_profile",
        ),
    )

    # ------------------------------------------------------------- projects
    op.create_table(
        "projects",
        sa.Column("id", UUID, nullable=False, server_default=NEW_UUID),
        sa.Column("user_id", UUID, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("deleted_at", TS, nullable=True),
        sa.Column("created_at", TS, nullable=False, server_default=NOW),
        sa.Column("updated_at", TS, nullable=False, server_default=NOW),
        sa.PrimaryKeyConstraint("id", name="pk_projects"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_projects_user_id_users",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "length(btrim(name)) BETWEEN 1 AND 255",
            name="ck_projects_name_trimmed_nonempty",
        ),
        sa.CheckConstraint(
            "description IS NULL OR length(btrim(description)) > 0",
            name="ck_projects_description_valid",
        ),
    )
    op.create_index("ix_projects_user_id", "projects", ["user_id"])
    op.create_index(
        "ix_projects_owner_listing", "projects", ["user_id", "updated_at", "id"]
    )
    op.create_index(
        "ix_projects_owner_live",
        "projects",
        ["user_id", "updated_at", "id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # ------------------------------------------------------------ documents
    op.create_table(
        "documents",
        sa.Column("id", UUID, nullable=False, server_default=NEW_UUID),
        sa.Column("project_id", UUID, nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("appwrite_file_id", sa.String(255), nullable=False),
        sa.Column("chroma_collection", sa.String(255), nullable=True),
        sa.Column("chroma_document_id", sa.String(255), nullable=True),
        sa.Column("file_size", sa.BigInteger, nullable=True),
        sa.Column(
            "mime_type",
            sa.String(100),
            nullable=True,
            server_default=sa.text("'application/pdf'"),
        ),
        sa.Column(
            "status",
            sa.String(30),
            nullable=False,
            server_default=sa.text("'Pending'"),
        ),
        sa.Column("upload_request_id", UUID, nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=True),
        sa.Column("upload_completed_at", TS, nullable=True),
        sa.Column(
            "processing_epoch", sa.BigInteger, nullable=False, server_default=sa.text("0")
        ),
        sa.Column("active_index_version", UUID, nullable=True),
        sa.Column("chunk_count", sa.Integer, nullable=True),
        sa.Column("processed_at", TS, nullable=True),
        sa.Column("processing_error", sa.Text, nullable=True),
        sa.Column("deleted_at", TS, nullable=True),
        sa.Column("created_at", TS, nullable=False, server_default=NOW),
        sa.Column("updated_at", TS, nullable=False, server_default=NOW),
        sa.PrimaryKeyConstraint("id", name="pk_documents"),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name="fk_documents_project_id_projects",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "appwrite_file_id", name="uq_documents_appwrite_file_id"
        ),
        sa.CheckConstraint(
            "length(btrim(file_name)) BETWEEN 1 AND 255",
            name="ck_documents_file_name_valid",
        ),
        sa.CheckConstraint(
            "content_sha256 IS NULL OR content_sha256 ~ '^[0-9a-f]{64}$'",
            name="ck_documents_content_sha256_hex",
        ),
        sa.CheckConstraint(
            "file_size IS NULL OR file_size > 0", name="ck_documents_file_size_positive"
        ),
        sa.CheckConstraint(
            "mime_type IS NULL OR mime_type = 'application/pdf'",
            name="ck_documents_mime_type_pdf",
        ),
        sa.CheckConstraint(
            "status IN ('Pending', 'Processing', 'Completed', 'Failed')",
            name="ck_documents_status_valid",
        ),
        sa.CheckConstraint(
            "processing_epoch >= 0", name="ck_documents_processing_epoch_nonnegative"
        ),
        sa.CheckConstraint(
            "chunk_count IS NULL OR chunk_count >= 0",
            name="ck_documents_chunk_count_nonnegative",
        ),
        sa.CheckConstraint(
            "status <> 'Completed' OR "
            "(file_size IS NOT NULL AND chunk_count IS NOT NULL "
            "AND active_index_version IS NOT NULL AND processed_at IS NOT NULL)",
            name="ck_documents_completed_requires_publish",
        ),
    )
    op.create_index("ix_documents_project_id", "documents", ["project_id"])
    op.create_index(
        "uq_documents_project_upload_request",
        "documents",
        ["project_id", "upload_request_id"],
        unique=True,
    )
    op.create_index(
        "ix_documents_project_status",
        "documents",
        ["project_id", "status", "deleted_at"],
    )
    op.create_index(
        "ix_documents_project_live",
        "documents",
        ["project_id", "status", "created_at"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # --------------------------------------------------------- conversations
    op.create_table(
        "conversations",
        sa.Column("id", UUID, nullable=False, server_default=NEW_UUID),
        sa.Column("project_id", UUID, nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("created_at", TS, nullable=False, server_default=NOW),
        sa.Column("updated_at", TS, nullable=False, server_default=NOW),
        sa.PrimaryKeyConstraint("id", name="pk_conversations"),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name="fk_conversations_project_id_projects",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "title IS NULL OR length(btrim(title)) BETWEEN 1 AND 255",
            name="ck_conversations_title_valid",
        ),
    )
    op.create_index("ix_conversations_project_id", "conversations", ["project_id"])
    op.create_index(
        "ix_conversations_project_activity",
        "conversations",
        ["project_id", "updated_at", "id"],
    )

    # -------------------------------------------------------------- messages
    op.create_table(
        "messages",
        sa.Column("id", UUID, nullable=False, server_default=NEW_UUID),
        sa.Column("conversation_id", UUID, nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("position", sa.BigInteger, nullable=False),
        sa.Column("citations", postgresql.JSONB, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("client_request_id", UUID, nullable=True),
        sa.Column("reply_to_message_id", UUID, nullable=True),
        sa.Column("generation_status", sa.String(20), nullable=True),
        sa.Column("generation_token", UUID, nullable=True),
        sa.Column("generation_expires_at", TS, nullable=True),
        sa.Column("created_at", TS, nullable=False, server_default=NOW),
        sa.PrimaryKeyConstraint("id", name="pk_messages"),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            name="fk_messages_conversation_id_conversations",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["reply_to_message_id"],
            ["messages.id"],
            name="fk_messages_reply_to_message_id_messages",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "role IN ('user', 'assistant', 'system')", name="ck_messages_role_valid"
        ),
        sa.CheckConstraint("position >= 1", name="ck_messages_position_positive"),
        sa.CheckConstraint("length(content) > 0", name="ck_messages_content_nonempty"),
        sa.CheckConstraint(
            "reply_to_message_id IS NULL OR reply_to_message_id <> id",
            name="ck_messages_reply_not_self",
        ),
        sa.CheckConstraint(
            "generation_status IN ('pending', 'generating', 'completed', 'failed', 'cancelled')",
            name="ck_messages_generation_status_valid",
        ),
        sa.CheckConstraint(
            "generation_status IS NULL OR role = 'user'",
            name="ck_messages_generation_status_user_only",
        ),
        sa.CheckConstraint(
            "generation_expires_at IS NULL "
            "OR generation_status IN ('pending', 'generating')",
            name="ck_messages_generation_expiry_only_while_active",
        ),
        sa.CheckConstraint(
            "citations IS NULL OR jsonb_typeof(citations) = 'array'",
            name="ck_messages_citations_is_array",
        ),
        sa.CheckConstraint(
            "metadata IS NULL OR jsonb_typeof(metadata) = 'object'",
            name="ck_messages_metadata_is_object",
        ),
    )
    op.create_index(
        "uq_messages_conversation_position",
        "messages",
        ["conversation_id", "position"],
        unique=True,
    )
    op.create_index(
        "ix_messages_conversation_created",
        "messages",
        ["conversation_id", "created_at", "position"],
    )
    op.create_index(
        "uq_messages_conversation_client_request",
        "messages",
        ["conversation_id", "client_request_id"],
        unique=True,
        postgresql_where=sa.text(
            "role = 'user' AND client_request_id IS NOT NULL"
        ),
    )
    op.create_index(
        "uq_messages_reply_to",
        "messages",
        ["reply_to_message_id"],
        unique=True,
        postgresql_where=sa.text(
            "role = 'assistant' AND reply_to_message_id IS NOT NULL"
        ),
    )
    op.create_index(
        "uq_messages_one_active_generation",
        "messages",
        ["conversation_id"],
        unique=True,
        postgresql_where=sa.text(
            "role = 'user' AND generation_status IN ('pending', 'generating')"
        ),
    )
    op.create_index("ix_messages_reply_to", "messages", ["reply_to_message_id"])
    op.create_index(
        "ix_messages_generation_expiry", "messages", ["generation_expires_at"]
    )

    # -------------------------------------------------------- processing_jobs
    op.create_table(
        "processing_jobs",
        sa.Column("id", UUID, nullable=False, server_default=NEW_UUID),
        sa.Column("document_id", UUID, nullable=True),
        # Immutable snapshots: intentionally NO foreign key (see models.py).
        sa.Column("owner_user_id", UUID, nullable=False),
        sa.Column("project_id", UUID, nullable=False),
        sa.Column("target_document_id", UUID, nullable=False),
        sa.Column(
            "resource_snapshot",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "target_epoch", sa.BigInteger, nullable=False, server_default=sa.text("0")
        ),
        sa.Column("kind", sa.String(30), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("stage", sa.String(30), nullable=True),
        sa.Column(
            "attempt_count", sa.Integer, nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "max_attempts", sa.Integer, nullable=False, server_default=sa.text("3")
        ),
        sa.Column("available_at", TS, nullable=False, server_default=NOW),
        sa.Column("lease_owner", sa.String(255), nullable=True),
        sa.Column("lease_token", sa.BigInteger, nullable=True),
        sa.Column("lease_expires_at", TS, nullable=True),
        sa.Column("index_version", UUID, nullable=True),
        sa.Column("progress_current", sa.Integer, nullable=True),
        sa.Column("progress_total", sa.Integer, nullable=True),
        sa.Column("last_error_code", sa.String(100), nullable=True),
        sa.Column("last_error_message", sa.Text, nullable=True),
        sa.Column("created_at", TS, nullable=False, server_default=NOW),
        sa.Column("updated_at", TS, nullable=False, server_default=NOW),
        sa.Column("finished_at", TS, nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_processing_jobs"),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name="fk_processing_jobs_document_id_documents",
            ondelete="SET NULL",
        ),
        sa.CheckConstraint(
            "kind IN ('process_document', 'delete_document')",
            name="ck_processing_jobs_kind_valid",
        ),
        sa.CheckConstraint(
            "status IN ('awaiting_upload', 'queued', 'running', 'retry_wait', "
            "'succeeded', 'failed', 'cancelled')",
            name="ck_processing_jobs_status_valid",
        ),
        sa.CheckConstraint(
            "stage IS NULL OR stage IN ('uploading', 'extracting', 'chunking', "
            "'embedding', 'indexing', 'publishing', 'deleting')",
            name="ck_processing_jobs_stage_valid",
        ),
        sa.CheckConstraint(
            "target_epoch >= 0", name="ck_processing_jobs_target_epoch_nonnegative"
        ),
        sa.CheckConstraint(
            "attempt_count >= 0", name="ck_processing_jobs_attempt_count_nonnegative"
        ),
        sa.CheckConstraint(
            "max_attempts >= 1", name="ck_processing_jobs_max_attempts_positive"
        ),
        sa.CheckConstraint(
            "lease_token IS NULL OR lease_token >= 1",
            name="ck_processing_jobs_lease_token_positive",
        ),
        sa.CheckConstraint(
            "progress_current IS NULL OR progress_current >= 0",
            name="ck_processing_jobs_progress_current_nonnegative",
        ),
        sa.CheckConstraint(
            "progress_total IS NULL OR progress_total >= 0",
            name="ck_processing_jobs_progress_total_nonnegative",
        ),
        sa.CheckConstraint(
            "progress_current IS NULL OR progress_total IS NULL "
            "OR progress_current <= progress_total",
            name="ck_processing_jobs_progress_current_le_total",
        ),
        sa.CheckConstraint(
            "jsonb_typeof(resource_snapshot) = 'object'",
            name="ck_processing_jobs_resource_snapshot_is_object",
        ),
        sa.CheckConstraint(
            "finished_at IS NULL OR finished_at >= created_at",
            name="ck_processing_jobs_finished_after_created",
        ),
    )
    op.create_index(
        "ix_processing_jobs_due",
        "processing_jobs",
        ["status", "available_at", "created_at"],
    )
    op.create_index(
        "ix_processing_jobs_due_claimable",
        "processing_jobs",
        ["available_at", "created_at"],
        postgresql_where=sa.text("status IN ('queued', 'retry_wait')"),
    )
    op.create_index(
        "ix_processing_jobs_lease_expiry",
        "processing_jobs",
        ["lease_expires_at"],
        postgresql_where=sa.text(
            "status = 'running' AND lease_expires_at IS NOT NULL"
        ),
    )
    op.create_index(
        "ix_processing_jobs_owner",
        "processing_jobs",
        ["owner_user_id", "created_at", "id"],
    )
    op.create_index(
        "ix_processing_jobs_document",
        "processing_jobs",
        ["document_id"],
        postgresql_where=sa.text("document_id IS NOT NULL"),
    )
    op.create_index(
        "ix_processing_jobs_project",
        "processing_jobs",
        ["project_id", "created_at", "id"],
    )
    op.create_index(
        "ix_processing_jobs_target",
        "processing_jobs",
        ["target_document_id", "created_at", "id"],
    )
    op.create_index(
        "uq_processing_jobs_one_nonterminal_per_target_kind",
        "processing_jobs",
        ["target_document_id", "kind"],
        unique=True,
        postgresql_where=sa.text(
            "status IN ('awaiting_upload', 'queued', 'running', 'retry_wait')"
        ),
    )


def downgrade() -> None:
    op.drop_table("processing_jobs")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("documents")
    op.drop_table("projects")
    op.drop_table("users")
