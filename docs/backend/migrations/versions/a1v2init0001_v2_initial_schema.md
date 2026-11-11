# `migrations/versions/a1v2init0001_v2_initial_schema.py`

[Source](../../../../Backend/migrations/versions/a1v2init0001_v2_initial_schema.py) · [Backend index](../../README.md)

Initial Alembic revision **`a1v2init0001`**, with no parent, branch label, or dependency revision. Its stable revision identifier is migration history, not an obsolete header comment. Schema inventory and column semantics are documented in [db/models.md](../../app/db/models.md).

Shared DDL objects: `UUID = sa.Uuid(native_uuid=True)`, timezone-aware `TS`, SQL `NOW = now()`, and `NEW_UUID = gen_random_uuid()`. Migration operations use these server expressions; ORM Python defaults/on-update hooks are not SQL triggers.

## Functions

### `upgrade() -> None`

- **Arguments:** None; Alembic provides the operations context.
- **Returns:** `None`.
- **Work:** Executes `CREATE EXTENSION IF NOT EXISTS pgcrypto`, then creates tables in dependency order: `users`, `projects`, `documents`, `conversations`, `messages`, `processing_jobs`. Each table gets explicit PK/FK/unique/check names and server defaults. It creates the ownership/listing, upload-idempotency, message-order/reply/active-turn, and job-due/lease/history/one-active-job indexes immediately after their owning tables.
- **Key details:** User/project/document/conversation/message relationships cascade on deletion; a job's live document link uses `SET NULL`, while owner/project/target snapshots have no FK. JSONB stores citations, message metadata, and job resource snapshots. Partial unique indexes enforce active-turn and active-job rules without preventing historical completed rows.
- **Side effects/errors:** Creates PostgreSQL schema objects (or emits their SQL offline). Permission/DDL errors propagate to Alembic's transaction. `pgcrypto` creation is idempotent, but table creation is an initial revision, not a repair/upsert routine.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-upgrade"></a>

#### Line-by-line execution

[Current source: lines 38–486](../../../../Backend/migrations/versions/a1v2init0001_v2_initial_schema.py#L38-L486). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  38 | def upgrade() -> None:
  39 |     op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
  40 | 
  41 |     # ---------------------------------------------------------------- users
  42 |     op.create_table(
  43 |         "users",
  44 |         sa.Column("id", UUID, nullable=False, server_default=NEW_UUID),
  45 |         sa.Column("appwrite_user_id", sa.String(255), nullable=False),
  46 |         sa.Column("email", sa.String(255), nullable=False),
  47 |         sa.Column("name", sa.String(150), nullable=True),
  48 |         sa.Column("date_of_birth", sa.Date, nullable=True),
  49 |         sa.Column(
  50 |             "onboarding_completed",
  51 |             sa.Boolean,
  52 |             nullable=False,
  53 |             server_default=sa.text("false"),
  54 |         ),
  55 |         sa.Column("created_at", TS, nullable=False, server_default=NOW),
  56 |         sa.Column("updated_at", TS, nullable=False, server_default=NOW),
  57 |         sa.PrimaryKeyConstraint("id", name="pk_users"),
  58 |         sa.UniqueConstraint("appwrite_user_id", name="uq_users_appwrite_user_id"),
  59 |         sa.UniqueConstraint("email", name="uq_users_email"),
  60 |         sa.CheckConstraint(
  61 |             "email <> '' AND email = btrim(email)", name="ck_users_email_nonempty"
  62 |         ),
  63 |         sa.CheckConstraint("email = lower(email)", name="ck_users_email_normalized"),
  64 |         sa.CheckConstraint(
  65 |             "name IS NULL OR (btrim(name) <> '' AND length(name) <= 150)",
  66 |             name="ck_users_name_valid",
  67 |         ),
  68 |         sa.CheckConstraint(
  69 |             "date_of_birth IS NULL OR date_of_birth <= CURRENT_DATE",
  70 |             name="ck_users_date_of_birth_not_future",
  71 |         ),
  72 |         sa.CheckConstraint(
  73 |             "NOT onboarding_completed OR "
  74 |             "(name IS NOT NULL AND btrim(name) <> '' AND date_of_birth IS NOT NULL)",
  75 |             name="ck_users_onboarding_requires_profile",
  76 |         ),
  77 |     )
  78 | 
  79 |     # ------------------------------------------------------------- projects
  80 |     op.create_table(
  81 |         "projects",
  82 |         sa.Column("id", UUID, nullable=False, server_default=NEW_UUID),
  83 |         sa.Column("user_id", UUID, nullable=False),
  84 |         sa.Column("name", sa.String(255), nullable=False),
  85 |         sa.Column("description", sa.Text, nullable=True),
  86 |         sa.Column("deleted_at", TS, nullable=True),
  87 |         sa.Column("created_at", TS, nullable=False, server_default=NOW),
  88 |         sa.Column("updated_at", TS, nullable=False, server_default=NOW),
  89 |         sa.PrimaryKeyConstraint("id", name="pk_projects"),
  90 |         sa.ForeignKeyConstraint(
  91 |             ["user_id"],
  92 |             ["users.id"],
  93 |             name="fk_projects_user_id_users",
  94 |             ondelete="CASCADE",
  95 |         ),
  96 |         sa.CheckConstraint(
  97 |             "length(btrim(name)) BETWEEN 1 AND 255",
  98 |             name="ck_projects_name_trimmed_nonempty",
  99 |         ),
 100 |         sa.CheckConstraint(
 101 |             "description IS NULL OR length(btrim(description)) > 0",
 102 |             name="ck_projects_description_valid",
 103 |         ),
 104 |     )
 105 |     op.create_index("ix_projects_user_id", "projects", ["user_id"])
 106 |     op.create_index(
 107 |         "ix_projects_owner_listing", "projects", ["user_id", "updated_at", "id"]
 108 |     )
 109 |     op.create_index(
 110 |         "ix_projects_owner_live",
 111 |         "projects",
 112 |         ["user_id", "updated_at", "id"],
 113 |         postgresql_where=sa.text("deleted_at IS NULL"),
 114 |     )
 115 | 
 116 |     # ------------------------------------------------------------ documents
 117 |     op.create_table(
 118 |         "documents",
 119 |         sa.Column("id", UUID, nullable=False, server_default=NEW_UUID),
 120 |         sa.Column("project_id", UUID, nullable=False),
 121 |         sa.Column("file_name", sa.String(255), nullable=False),
 122 |         sa.Column("appwrite_file_id", sa.String(255), nullable=False),
 123 |         sa.Column("chroma_collection", sa.String(255), nullable=True),
 124 |         sa.Column("chroma_document_id", sa.String(255), nullable=True),
 125 |         sa.Column("file_size", sa.BigInteger, nullable=True),
 126 |         sa.Column(
 127 |             "mime_type",
 128 |             sa.String(100),
 129 |             nullable=True,
 130 |             server_default=sa.text("'application/pdf'"),
 131 |         ),
 132 |         sa.Column(
 133 |             "status",
 134 |             sa.String(30),
 135 |             nullable=False,
 136 |             server_default=sa.text("'Pending'"),
 137 |         ),
 138 |         sa.Column("upload_request_id", UUID, nullable=False),
 139 |         sa.Column("content_sha256", sa.String(64), nullable=True),
 140 |         sa.Column("upload_completed_at", TS, nullable=True),
 141 |         sa.Column(
 142 |             "processing_epoch", sa.BigInteger, nullable=False, server_default=sa.text("0")
 143 |         ),
 144 |         sa.Column("active_index_version", UUID, nullable=True),
 145 |         sa.Column("chunk_count", sa.Integer, nullable=True),
 146 |         sa.Column("processed_at", TS, nullable=True),
 147 |         sa.Column("processing_error", sa.Text, nullable=True),
 148 |         sa.Column("deleted_at", TS, nullable=True),
 149 |         sa.Column("created_at", TS, nullable=False, server_default=NOW),
 150 |         sa.Column("updated_at", TS, nullable=False, server_default=NOW),
 151 |         sa.PrimaryKeyConstraint("id", name="pk_documents"),
 152 |         sa.ForeignKeyConstraint(
 153 |             ["project_id"],
 154 |             ["projects.id"],
 155 |             name="fk_documents_project_id_projects",
 156 |             ondelete="CASCADE",
 157 |         ),
 158 |         sa.UniqueConstraint(
 159 |             "appwrite_file_id", name="uq_documents_appwrite_file_id"
 160 |         ),
 161 |         sa.CheckConstraint(
 162 |             "length(btrim(file_name)) BETWEEN 1 AND 255",
 163 |             name="ck_documents_file_name_valid",
 164 |         ),
 165 |         sa.CheckConstraint(
 166 |             "content_sha256 IS NULL OR content_sha256 ~ '^[0-9a-f]{64}$'",
 167 |             name="ck_documents_content_sha256_hex",
 168 |         ),
 169 |         sa.CheckConstraint(
 170 |             "file_size IS NULL OR file_size > 0", name="ck_documents_file_size_positive"
 171 |         ),
 172 |         sa.CheckConstraint(
 173 |             "mime_type IS NULL OR mime_type = 'application/pdf'",
 174 |             name="ck_documents_mime_type_pdf",
 175 |         ),
 176 |         sa.CheckConstraint(
 177 |             "status IN ('Pending', 'Processing', 'Completed', 'Failed')",
 178 |             name="ck_documents_status_valid",
 179 |         ),
 180 |         sa.CheckConstraint(
 181 |             "processing_epoch >= 0", name="ck_documents_processing_epoch_nonnegative"
 182 |         ),
 183 |         sa.CheckConstraint(
 184 |             "chunk_count IS NULL OR chunk_count >= 0",
 185 |             name="ck_documents_chunk_count_nonnegative",
 186 |         ),
 187 |         sa.CheckConstraint(
 188 |             "status <> 'Completed' OR "
 189 |             "(file_size IS NOT NULL AND chunk_count IS NOT NULL "
 190 |             "AND active_index_version IS NOT NULL AND processed_at IS NOT NULL)",
 191 |             name="ck_documents_completed_requires_publish",
 192 |         ),
 193 |     )
 194 |     op.create_index("ix_documents_project_id", "documents", ["project_id"])
 195 |     op.create_index(
 196 |         "uq_documents_project_upload_request",
 197 |         "documents",
 198 |         ["project_id", "upload_request_id"],
 199 |         unique=True,
 200 |     )
 201 |     op.create_index(
 202 |         "ix_documents_project_status",
 203 |         "documents",
 204 |         ["project_id", "status", "deleted_at"],
 205 |     )
 206 |     op.create_index(
 207 |         "ix_documents_project_live",
 208 |         "documents",
 209 |         ["project_id", "status", "created_at"],
 210 |         postgresql_where=sa.text("deleted_at IS NULL"),
 211 |     )
 212 | 
 213 |     # --------------------------------------------------------- conversations
 214 |     op.create_table(
 215 |         "conversations",
 216 |         sa.Column("id", UUID, nullable=False, server_default=NEW_UUID),
 217 |         sa.Column("project_id", UUID, nullable=False),
 218 |         sa.Column("title", sa.String(255), nullable=True),
 219 |         sa.Column("created_at", TS, nullable=False, server_default=NOW),
 220 |         sa.Column("updated_at", TS, nullable=False, server_default=NOW),
 221 |         sa.PrimaryKeyConstraint("id", name="pk_conversations"),
 222 |         sa.ForeignKeyConstraint(
 223 |             ["project_id"],
 224 |             ["projects.id"],
 225 |             name="fk_conversations_project_id_projects",
 226 |             ondelete="CASCADE",
 227 |         ),
 228 |         sa.CheckConstraint(
 229 |             "title IS NULL OR length(btrim(title)) BETWEEN 1 AND 255",
 230 |             name="ck_conversations_title_valid",
 231 |         ),
 232 |     )
 233 |     op.create_index("ix_conversations_project_id", "conversations", ["project_id"])
 234 |     op.create_index(
 235 |         "ix_conversations_project_activity",
 236 |         "conversations",
 237 |         ["project_id", "updated_at", "id"],
 238 |     )
 239 | 
 240 |     # -------------------------------------------------------------- messages
 241 |     op.create_table(
 242 |         "messages",
 243 |         sa.Column("id", UUID, nullable=False, server_default=NEW_UUID),
 244 |         sa.Column("conversation_id", UUID, nullable=False),
 245 |         sa.Column("role", sa.String(20), nullable=False),
 246 |         sa.Column("content", sa.Text, nullable=False),
 247 |         sa.Column("position", sa.BigInteger, nullable=False),
 248 |         sa.Column("citations", postgresql.JSONB, nullable=True),
 249 |         sa.Column("metadata", postgresql.JSONB, nullable=True),
 250 |         sa.Column("client_request_id", UUID, nullable=True),
 251 |         sa.Column("reply_to_message_id", UUID, nullable=True),
 252 |         sa.Column("generation_status", sa.String(20), nullable=True),
 253 |         sa.Column("generation_token", UUID, nullable=True),
 254 |         sa.Column("generation_expires_at", TS, nullable=True),
 255 |         sa.Column("created_at", TS, nullable=False, server_default=NOW),
 256 |         sa.PrimaryKeyConstraint("id", name="pk_messages"),
 257 |         sa.ForeignKeyConstraint(
 258 |             ["conversation_id"],
 259 |             ["conversations.id"],
 260 |             name="fk_messages_conversation_id_conversations",
 261 |             ondelete="CASCADE",
 262 |         ),
 263 |         sa.ForeignKeyConstraint(
 264 |             ["reply_to_message_id"],
 265 |             ["messages.id"],
 266 |             name="fk_messages_reply_to_message_id_messages",
 267 |             ondelete="CASCADE",
 268 |         ),
 269 |         sa.CheckConstraint(
 270 |             "role IN ('user', 'assistant', 'system')", name="ck_messages_role_valid"
 271 |         ),
 272 |         sa.CheckConstraint("position >= 1", name="ck_messages_position_positive"),
 273 |         sa.CheckConstraint("length(content) > 0", name="ck_messages_content_nonempty"),
 274 |         sa.CheckConstraint(
 275 |             "reply_to_message_id IS NULL OR reply_to_message_id <> id",
 276 |             name="ck_messages_reply_not_self",
 277 |         ),
 278 |         sa.CheckConstraint(
 279 |             "generation_status IN ('pending', 'generating', 'completed', 'failed', 'cancelled')",
 280 |             name="ck_messages_generation_status_valid",
 281 |         ),
 282 |         sa.CheckConstraint(
 283 |             "generation_status IS NULL OR role = 'user'",
 284 |             name="ck_messages_generation_status_user_only",
 285 |         ),
 286 |         sa.CheckConstraint(
 287 |             "generation_expires_at IS NULL "
 288 |             "OR generation_status IN ('pending', 'generating')",
 289 |             name="ck_messages_generation_expiry_only_while_active",
 290 |         ),
 291 |         sa.CheckConstraint(
 292 |             "citations IS NULL OR jsonb_typeof(citations) = 'array'",
 293 |             name="ck_messages_citations_is_array",
 294 |         ),
 295 |         sa.CheckConstraint(
 296 |             "metadata IS NULL OR jsonb_typeof(metadata) = 'object'",
 297 |             name="ck_messages_metadata_is_object",
 298 |         ),
 299 |     )
 300 |     op.create_index(
 301 |         "uq_messages_conversation_position",
 302 |         "messages",
 303 |         ["conversation_id", "position"],
 304 |         unique=True,
 305 |     )
 306 |     op.create_index(
 307 |         "ix_messages_conversation_created",
 308 |         "messages",
 309 |         ["conversation_id", "created_at", "position"],
 310 |     )
 311 |     op.create_index(
 312 |         "uq_messages_conversation_client_request",
 313 |         "messages",
 314 |         ["conversation_id", "client_request_id"],
 315 |         unique=True,
 316 |         postgresql_where=sa.text(
 317 |             "role = 'user' AND client_request_id IS NOT NULL"
 318 |         ),
 319 |     )
 320 |     op.create_index(
 321 |         "uq_messages_reply_to",
 322 |         "messages",
 323 |         ["reply_to_message_id"],
 324 |         unique=True,
 325 |         postgresql_where=sa.text(
 326 |             "role = 'assistant' AND reply_to_message_id IS NOT NULL"
 327 |         ),
 328 |     )
 329 |     op.create_index(
 330 |         "uq_messages_one_active_generation",
 331 |         "messages",
 332 |         ["conversation_id"],
 333 |         unique=True,
 334 |         postgresql_where=sa.text(
 335 |             "role = 'user' AND generation_status IN ('pending', 'generating')"
 336 |         ),
 337 |     )
 338 |     op.create_index("ix_messages_reply_to", "messages", ["reply_to_message_id"])
 339 |     op.create_index(
 340 |         "ix_messages_generation_expiry", "messages", ["generation_expires_at"]
 341 |     )
 342 | 
 343 |     # -------------------------------------------------------- processing_jobs
 344 |     op.create_table(
 345 |         "processing_jobs",
 346 |         sa.Column("id", UUID, nullable=False, server_default=NEW_UUID),
 347 |         sa.Column("document_id", UUID, nullable=True),
 348 |         # Immutable snapshots: intentionally NO foreign key (see models.py).
 349 |         sa.Column("owner_user_id", UUID, nullable=False),
 350 |         sa.Column("project_id", UUID, nullable=False),
 351 |         sa.Column("target_document_id", UUID, nullable=False),
 352 |         sa.Column(
 353 |             "resource_snapshot",
 354 |             postgresql.JSONB,
 355 |             nullable=False,
 356 |             server_default=sa.text("'{}'::jsonb"),
 357 |         ),
 358 |         sa.Column(
 359 |             "target_epoch", sa.BigInteger, nullable=False, server_default=sa.text("0")
 360 |         ),
 361 |         sa.Column("kind", sa.String(30), nullable=False),
 362 |         sa.Column("status", sa.String(30), nullable=False),
 363 |         sa.Column("stage", sa.String(30), nullable=True),
 364 |         sa.Column(
 365 |             "attempt_count", sa.Integer, nullable=False, server_default=sa.text("0")
 366 |         ),
 367 |         sa.Column(
 368 |             "max_attempts", sa.Integer, nullable=False, server_default=sa.text("3")
 369 |         ),
 370 |         sa.Column("available_at", TS, nullable=False, server_default=NOW),
 371 |         sa.Column("lease_owner", sa.String(255), nullable=True),
 372 |         sa.Column("lease_token", sa.BigInteger, nullable=True),
 373 |         sa.Column("lease_expires_at", TS, nullable=True),
 374 |         sa.Column("index_version", UUID, nullable=True),
 375 |         sa.Column("progress_current", sa.Integer, nullable=True),
 376 |         sa.Column("progress_total", sa.Integer, nullable=True),
 377 |         sa.Column("last_error_code", sa.String(100), nullable=True),
 378 |         sa.Column("last_error_message", sa.Text, nullable=True),
 379 |         sa.Column("created_at", TS, nullable=False, server_default=NOW),
 380 |         sa.Column("updated_at", TS, nullable=False, server_default=NOW),
 381 |         sa.Column("finished_at", TS, nullable=True),
 382 |         sa.PrimaryKeyConstraint("id", name="pk_processing_jobs"),
 383 |         sa.ForeignKeyConstraint(
 384 |             ["document_id"],
 385 |             ["documents.id"],
 386 |             name="fk_processing_jobs_document_id_documents",
 387 |             ondelete="SET NULL",
 388 |         ),
 389 |         sa.CheckConstraint(
 390 |             "kind IN ('process_document', 'delete_document')",
 391 |             name="ck_processing_jobs_kind_valid",
 392 |         ),
 393 |         sa.CheckConstraint(
 394 |             "status IN ('awaiting_upload', 'queued', 'running', 'retry_wait', "
 395 |             "'succeeded', 'failed', 'cancelled')",
 396 |             name="ck_processing_jobs_status_valid",
 397 |         ),
 398 |         sa.CheckConstraint(
 399 |             "stage IS NULL OR stage IN ('uploading', 'extracting', 'chunking', "
 400 |             "'embedding', 'indexing', 'publishing', 'deleting')",
 401 |             name="ck_processing_jobs_stage_valid",
 402 |         ),
 403 |         sa.CheckConstraint(
 404 |             "target_epoch >= 0", name="ck_processing_jobs_target_epoch_nonnegative"
 405 |         ),
 406 |         sa.CheckConstraint(
 407 |             "attempt_count >= 0", name="ck_processing_jobs_attempt_count_nonnegative"
 408 |         ),
 409 |         sa.CheckConstraint(
 410 |             "max_attempts >= 1", name="ck_processing_jobs_max_attempts_positive"
 411 |         ),
 412 |         sa.CheckConstraint(
 413 |             "lease_token IS NULL OR lease_token >= 1",
 414 |             name="ck_processing_jobs_lease_token_positive",
 415 |         ),
 416 |         sa.CheckConstraint(
 417 |             "progress_current IS NULL OR progress_current >= 0",
 418 |             name="ck_processing_jobs_progress_current_nonnegative",
 419 |         ),
 420 |         sa.CheckConstraint(
 421 |             "progress_total IS NULL OR progress_total >= 0",
 422 |             name="ck_processing_jobs_progress_total_nonnegative",
 423 |         ),
 424 |         sa.CheckConstraint(
 425 |             "progress_current IS NULL OR progress_total IS NULL "
 426 |             "OR progress_current <= progress_total",
 427 |             name="ck_processing_jobs_progress_current_le_total",
 428 |         ),
 429 |         sa.CheckConstraint(
 430 |             "jsonb_typeof(resource_snapshot) = 'object'",
 431 |             name="ck_processing_jobs_resource_snapshot_is_object",
 432 |         ),
 433 |         sa.CheckConstraint(
 434 |             "finished_at IS NULL OR finished_at >= created_at",
 435 |             name="ck_processing_jobs_finished_after_created",
 436 |         ),
 437 |     )
 438 |     op.create_index(
 439 |         "ix_processing_jobs_due",
 440 |         "processing_jobs",
 441 |         ["status", "available_at", "created_at"],
 442 |     )
 443 |     op.create_index(
 444 |         "ix_processing_jobs_due_claimable",
 445 |         "processing_jobs",
 446 |         ["available_at", "created_at"],
 447 |         postgresql_where=sa.text("status IN ('queued', 'retry_wait')"),
 448 |     )
 449 |     op.create_index(
 450 |         "ix_processing_jobs_lease_expiry",
 451 |         "processing_jobs",
 452 |         ["lease_expires_at"],
 453 |         postgresql_where=sa.text(
 454 |             "status = 'running' AND lease_expires_at IS NOT NULL"
 455 |         ),
 456 |     )
 457 |     op.create_index(
 458 |         "ix_processing_jobs_owner",
 459 |         "processing_jobs",
 460 |         ["owner_user_id", "created_at", "id"],
 461 |     )
 462 |     op.create_index(
 463 |         "ix_processing_jobs_document",
 464 |         "processing_jobs",
 465 |         ["document_id"],
 466 |         postgresql_where=sa.text("document_id IS NOT NULL"),
 467 |     )
 468 |     op.create_index(
 469 |         "ix_processing_jobs_project",
 470 |         "processing_jobs",
 471 |         ["project_id", "created_at", "id"],
 472 |     )
 473 |     op.create_index(
 474 |         "ix_processing_jobs_target",
 475 |         "processing_jobs",
 476 |         ["target_document_id", "created_at", "id"],
 477 |     )
 478 |     op.create_index(
 479 |         "uq_processing_jobs_one_nonterminal_per_target_kind",
 480 |         "processing_jobs",
 481 |         ["target_document_id", "kind"],
 482 |         unique=True,
 483 |         postgresql_where=sa.text(
 484 |             "status IN ('awaiting_upload', 'queued', 'running', 'retry_wait')"
 485 |         ),
 486 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L38 | Define `upgrade`; bind its arguments when called. The body executes only when invoked. |
| L39 | `op.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto')` — Execute the literal migration SQL through Alembic; CREATE EXTENSION IF NOT EXISTS pgcrypto enables UUID support without recreating an existing extension. The return value is not assigned here. |
| L41 | Comment only: ---------------------------------------------------------------- users. It does not execute; the neighboring code determines behavior. |
| L42 | `op.create_table` with the arguments detailed below — Issue Alembic DDL to create the named table with the listed columns and constraints; inputs include `sa.Column('id', UUID, nullable=False, server_default=NEW_UUID)` — Declare column `'id'` with type `UUID`; require a non-null value; PostgreSQL supplies `NEW_UUID` when an INSERT omits the column; `sa.Column('appwrite_user_id', sa.String(255), nullable=False)` — Declare column `'appwrite_user_id'` with type `sa.String(255)`; require a non-null value; no server default is supplied by this declaration. The return value is not assigned here. |
| L43 | Supply positional argument 1 to `op.create_table`: `'users'`. |
| L44 | `sa.Column('id', UUID, nullable=False, server_default=NEW_UUID)` — Declare column `'id'` with type `UUID`; require a non-null value; PostgreSQL supplies `NEW_UUID` when an INSERT omits the column. |
| L45 | `sa.Column('appwrite_user_id', sa.String(255), nullable=False)` — Declare column `'appwrite_user_id'` with type `sa.String(255)`; require a non-null value; no server default is supplied by this declaration; inputs include `sa.String(255)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L46 | `sa.Column('email', sa.String(255), nullable=False)` — Declare column `'email'` with type `sa.String(255)`; require a non-null value; no server default is supplied by this declaration; inputs include `sa.String(255)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L47 | `sa.Column('name', sa.String(150), nullable=True)` — Declare column `'name'` with type `sa.String(150)`; allow SQL NULL; no server default is supplied by this declaration; inputs include `sa.String(150)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L48 | `sa.Column('date_of_birth', sa.Date, nullable=True)` — Declare column `'date_of_birth'` with type `sa.Date`; allow SQL NULL; no server default is supplied by this declaration. |
| L49 | `sa.Column('onboarding_completed', sa.Boolean, nullable=False, server_default=sa.text('false'))` — Declare column `'onboarding_completed'` with type `sa.Boolean`; require a non-null value; PostgreSQL supplies `sa.text('false')` when an INSERT omits the column. |
| L50 | Supply positional argument 1 to `sa.Column`: `'onboarding_completed'`. |
| L51 | Supply positional argument 2 to `sa.Column`: the `Boolean` attribute of `sa`. |
| L52 | Supply `nullable` = `False`.  Evaluate the value as: `False`. |
| L53 | Supply `server_default` = `sa.text('false')`.  Evaluate the value as: `sa.text('false')` — Wrap trusted literal SQL for SQLAlchemy/Alembic; it is not an input-escaping function. |
| L54 | Close the expression/container begun at L49; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L55 | `sa.Column('created_at', TS, nullable=False, server_default=NOW)` — Declare column `'created_at'` with type `TS`; require a non-null value; PostgreSQL supplies `NOW` when an INSERT omits the column. |
| L56 | `sa.Column('updated_at', TS, nullable=False, server_default=NOW)` — Declare column `'updated_at'` with type `TS`; require a non-null value; PostgreSQL supplies `NOW` when an INSERT omits the column. |
| L57 | `sa.PrimaryKeyConstraint('id', name='pk_users')` — Declare the columns identifying each row uniquely and non-nullably. |
| L58 | `sa.UniqueConstraint('appwrite_user_id', name='uq_users_appwrite_user_id')` — Declare uniqueness across the named columns; conflicting inserted/updated values are rejected by PostgreSQL. |
| L59 | `sa.UniqueConstraint('email', name='uq_users_email')` — Declare uniqueness across the named columns; conflicting inserted/updated values are rejected by PostgreSQL. |
| L60 | `sa.CheckConstraint("email <> '' AND email = btrim(email)", name='ck_users_email_nonempty')` — Email must be nonempty and already trimmed; leading/trailing spaces are rejected rather than silently removed by SQL; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L61 | Supply `name` = `'ck_users_email_nonempty'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_users_email_nonempty'`. |
| L62 | Close the expression/container begun at L60; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L63 | `sa.CheckConstraint('email = lower(email)', name='ck_users_email_normalized')` — Email must already be lowercase; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L64 | `sa.CheckConstraint("name IS NULL OR (btrim(name) <> '' AND length(name) <= 150)", name='ck_users_name_valid')` — Allow a missing name; otherwise require nonblank trimmed content and at most 150 original characters; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L65 | Supply positional argument 1 to `sa.CheckConstraint`: `"name IS NULL OR (btrim(name) <> '' AND length(name) <= 150)"`. |
| L66 | Supply `name` = `'ck_users_name_valid'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_users_name_valid'`. |
| L67 | Close the expression/container begun at L64; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L68 | `sa.CheckConstraint('date_of_birth IS NULL OR date_of_birth <= CURRENT_DATE', name='ck_users_date_of_birth_not_future')` — Allow a missing birth date; otherwise reject a future date using the database's current date; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L69 | Supply positional argument 1 to `sa.CheckConstraint`: `'date_of_birth IS NULL OR date_of_birth <= CURRENT_DATE'`. |
| L70 | Supply `name` = `'ck_users_date_of_birth_not_future'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_users_date_of_birth_not_future'`. |
| L71 | Close the expression/container begun at L68; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L72 | `sa.CheckConstraint` with the arguments detailed below — When onboarding is true, require a nonblank name and a birth date; incomplete profiles may retain missing values; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L73 | Supply positional argument 1 to `sa.CheckConstraint`: `"NOT onboarding_completed OR (name IS NOT NULL AND btrim(name) <> '' AND date_of_birth IS NOT NULL)"`. |
| L74 | Supply positional argument 1 to `sa.CheckConstraint`: `"NOT onboarding_completed OR (name IS NOT NULL AND btrim(name) <> '' AND date_of_birth IS NOT NULL)"`. |
| L75 | Supply `name` = `'ck_users_onboarding_requires_profile'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_users_onboarding_requires_profile'`. |
| L76 | Close the expression/container begun at L72; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L77 | Close the expression/container begun at L42; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L79 | Comment only: ------------------------------------------------------------- projects. It does not execute; the neighboring code determines behavior. |
| L80 | `op.create_table` with the arguments detailed below — Issue Alembic DDL to create the named table with the listed columns and constraints; inputs include `sa.Column('id', UUID, nullable=False, server_default=NEW_UUID)` — Declare column `'id'` with type `UUID`; require a non-null value; PostgreSQL supplies `NEW_UUID` when an INSERT omits the column; `sa.Column('user_id', UUID, nullable=False)` — Declare column `'user_id'` with type `UUID`; require a non-null value; no server default is supplied by this declaration. The return value is not assigned here. |
| L81 | Supply positional argument 1 to `op.create_table`: `'projects'`. |
| L82 | `sa.Column('id', UUID, nullable=False, server_default=NEW_UUID)` — Declare column `'id'` with type `UUID`; require a non-null value; PostgreSQL supplies `NEW_UUID` when an INSERT omits the column. |
| L83 | `sa.Column('user_id', UUID, nullable=False)` — Declare column `'user_id'` with type `UUID`; require a non-null value; no server default is supplied by this declaration. |
| L84 | `sa.Column('name', sa.String(255), nullable=False)` — Declare column `'name'` with type `sa.String(255)`; require a non-null value; no server default is supplied by this declaration; inputs include `sa.String(255)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L85 | `sa.Column('description', sa.Text, nullable=True)` — Declare column `'description'` with type `sa.Text`; allow SQL NULL; no server default is supplied by this declaration. |
| L86 | `sa.Column('deleted_at', TS, nullable=True)` — Declare column `'deleted_at'` with type `TS`; allow SQL NULL; no server default is supplied by this declaration. |
| L87 | `sa.Column('created_at', TS, nullable=False, server_default=NOW)` — Declare column `'created_at'` with type `TS`; require a non-null value; PostgreSQL supplies `NOW` when an INSERT omits the column. |
| L88 | `sa.Column('updated_at', TS, nullable=False, server_default=NOW)` — Declare column `'updated_at'` with type `TS`; require a non-null value; PostgreSQL supplies `NOW` when an INSERT omits the column. |
| L89 | `sa.PrimaryKeyConstraint('id', name='pk_projects')` — Declare the columns identifying each row uniquely and non-nullably. |
| L90 | `sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_projects_user_id_users', ondelete='CASCADE')` — Declare the referenced table/columns and configured deletion behavior. |
| L91 | Supply positional argument 1 to `sa.ForeignKeyConstraint`: build a list containing `'user_id'`. |
| L92 | Supply positional argument 2 to `sa.ForeignKeyConstraint`: build a list containing `'users.id'`. |
| L93 | Supply `name` = `'fk_projects_user_id_users'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'fk_projects_user_id_users'`. |
| L94 | Supply `ondelete` = `'CASCADE'`.  Evaluate the value as: `'CASCADE'`. |
| L95 | Close the expression/container begun at L90; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L96 | `sa.CheckConstraint('length(btrim(name)) BETWEEN 1 AND 255', name='ck_projects_name_trimmed_nonempty')` — Require 1–255 characters after trimming the project name; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L97 | Supply positional argument 1 to `sa.CheckConstraint`: `'length(btrim(name)) BETWEEN 1 AND 255'`. |
| L98 | Supply `name` = `'ck_projects_name_trimmed_nonempty'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_projects_name_trimmed_nonempty'`. |
| L99 | Close the expression/container begun at L96; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L100 | `sa.CheckConstraint('description IS NULL OR length(btrim(description)) > 0', name='ck_projects_description_valid')` — Allow null description, but reject a supplied blank/whitespace-only description; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L101 | Supply positional argument 1 to `sa.CheckConstraint`: `'description IS NULL OR length(btrim(description)) > 0'`. |
| L102 | Supply `name` = `'ck_projects_description_valid'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_projects_description_valid'`. |
| L103 | Close the expression/container begun at L100; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L104 | Close the expression/container begun at L80; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L105 | `op.create_index('ix_projects_user_id', 'projects', ['user_id'])` — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L106 | `op.create_index('ix_projects_owner_listing', 'projects', ['user_id', 'updated_at', 'id'])` — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L107 | Supply positional argument 1 to `op.create_index`: `'ix_projects_owner_listing'`. |
| L108 | Close the expression/container begun at L106; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L109 | `op.create_index('ix_projects_owner_live', 'projects', ['user_id', 'updated_at', 'id'], postgresql_where=sa.text('deleted_at IS NULL'))` — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L110 | Supply positional argument 1 to `op.create_index`: `'ix_projects_owner_live'`. |
| L111 | Supply positional argument 2 to `op.create_index`: `'projects'`. |
| L112 | Supply positional argument 3 to `op.create_index`: build a list containing `'user_id'`, `'updated_at'`, `'id'`. |
| L113 | Supply `postgresql_where` = `sa.text('deleted_at IS NULL')`.  Evaluate the value as: `sa.text('deleted_at IS NULL')` — Wrap trusted literal SQL for SQLAlchemy/Alembic; it is not an input-escaping function. |
| L114 | Close the expression/container begun at L109; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L116 | Comment only: ------------------------------------------------------------ documents. It does not execute; the neighboring code determines behavior. |
| L117 | `op.create_table` with the arguments detailed below — Issue Alembic DDL to create the named table with the listed columns and constraints; inputs include `sa.Column('id', UUID, nullable=False, server_default=NEW_UUID)` — Declare column `'id'` with type `UUID`; require a non-null value; PostgreSQL supplies `NEW_UUID` when an INSERT omits the column; `sa.Column('project_id', UUID, nullable=False)` — Declare column `'project_id'` with type `UUID`; require a non-null value; no server default is supplied by this declaration. The return value is not assigned here. |
| L118 | Supply positional argument 1 to `op.create_table`: `'documents'`. |
| L119 | `sa.Column('id', UUID, nullable=False, server_default=NEW_UUID)` — Declare column `'id'` with type `UUID`; require a non-null value; PostgreSQL supplies `NEW_UUID` when an INSERT omits the column. |
| L120 | `sa.Column('project_id', UUID, nullable=False)` — Declare column `'project_id'` with type `UUID`; require a non-null value; no server default is supplied by this declaration. |
| L121 | `sa.Column('file_name', sa.String(255), nullable=False)` — Declare column `'file_name'` with type `sa.String(255)`; require a non-null value; no server default is supplied by this declaration; inputs include `sa.String(255)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L122 | `sa.Column('appwrite_file_id', sa.String(255), nullable=False)` — Declare column `'appwrite_file_id'` with type `sa.String(255)`; require a non-null value; no server default is supplied by this declaration; inputs include `sa.String(255)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L123 | `sa.Column('chroma_collection', sa.String(255), nullable=True)` — Declare column `'chroma_collection'` with type `sa.String(255)`; allow SQL NULL; no server default is supplied by this declaration; inputs include `sa.String(255)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L124 | `sa.Column('chroma_document_id', sa.String(255), nullable=True)` — Declare column `'chroma_document_id'` with type `sa.String(255)`; allow SQL NULL; no server default is supplied by this declaration; inputs include `sa.String(255)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L125 | `sa.Column('file_size', sa.BigInteger, nullable=True)` — Declare column `'file_size'` with type `sa.BigInteger`; allow SQL NULL; no server default is supplied by this declaration. |
| L126 | `sa.Column('mime_type', sa.String(100), nullable=True, server_default=sa.text("'application/pdf'"))` — Declare column `'mime_type'` with type `sa.String(100)`; allow SQL NULL; PostgreSQL supplies `sa.text("'application/pdf'")` when an INSERT omits the column; inputs include `sa.String(100)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L127 | Supply positional argument 1 to `sa.Column`: `'mime_type'`. |
| L128 | `sa.String(100)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L129 | Supply `nullable` = `True`.  Evaluate the value as: `True`. |
| L130 | Supply `server_default` = `sa.text("'application/pdf'")`.  Evaluate the value as: `sa.text("'application/pdf'")` — Wrap trusted literal SQL for SQLAlchemy/Alembic; it is not an input-escaping function. |
| L131 | Close the expression/container begun at L126; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L132 | `sa.Column('status', sa.String(30), nullable=False, server_default=sa.text("'Pending'"))` — Declare column `'status'` with type `sa.String(30)`; require a non-null value; PostgreSQL supplies `sa.text("'Pending'")` when an INSERT omits the column; inputs include `sa.String(30)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L133 | Supply positional argument 1 to `sa.Column`: `'status'`. |
| L134 | `sa.String(30)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L135 | Supply `nullable` = `False`.  Evaluate the value as: `False`. |
| L136 | Supply `server_default` = `sa.text("'Pending'")`.  Evaluate the value as: `sa.text("'Pending'")` — Wrap trusted literal SQL for SQLAlchemy/Alembic; it is not an input-escaping function. |
| L137 | Close the expression/container begun at L132; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L138 | `sa.Column('upload_request_id', UUID, nullable=False)` — Declare column `'upload_request_id'` with type `UUID`; require a non-null value; no server default is supplied by this declaration. |
| L139 | `sa.Column('content_sha256', sa.String(64), nullable=True)` — Declare column `'content_sha256'` with type `sa.String(64)`; allow SQL NULL; no server default is supplied by this declaration; inputs include `sa.String(64)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L140 | `sa.Column('upload_completed_at', TS, nullable=True)` — Declare column `'upload_completed_at'` with type `TS`; allow SQL NULL; no server default is supplied by this declaration. |
| L141 | `sa.Column('processing_epoch', sa.BigInteger, nullable=False, server_default=sa.text('0'))` — Declare column `'processing_epoch'` with type `sa.BigInteger`; require a non-null value; PostgreSQL supplies `sa.text('0')` when an INSERT omits the column. |
| L142 | Supply `nullable` = `False`.  Evaluate the value as: `False`. Supply `server_default` = `sa.text('0')`.  Evaluate the value as: `sa.text('0')` — Wrap trusted literal SQL for SQLAlchemy/Alembic; it is not an input-escaping function. |
| L143 | Close the expression/container begun at L141; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L144 | `sa.Column('active_index_version', UUID, nullable=True)` — Declare column `'active_index_version'` with type `UUID`; allow SQL NULL; no server default is supplied by this declaration. |
| L145 | `sa.Column('chunk_count', sa.Integer, nullable=True)` — Declare column `'chunk_count'` with type `sa.Integer`; allow SQL NULL; no server default is supplied by this declaration. |
| L146 | `sa.Column('processed_at', TS, nullable=True)` — Declare column `'processed_at'` with type `TS`; allow SQL NULL; no server default is supplied by this declaration. |
| L147 | `sa.Column('processing_error', sa.Text, nullable=True)` — Declare column `'processing_error'` with type `sa.Text`; allow SQL NULL; no server default is supplied by this declaration. |
| L148 | `sa.Column('deleted_at', TS, nullable=True)` — Declare column `'deleted_at'` with type `TS`; allow SQL NULL; no server default is supplied by this declaration. |
| L149 | `sa.Column('created_at', TS, nullable=False, server_default=NOW)` — Declare column `'created_at'` with type `TS`; require a non-null value; PostgreSQL supplies `NOW` when an INSERT omits the column. |
| L150 | `sa.Column('updated_at', TS, nullable=False, server_default=NOW)` — Declare column `'updated_at'` with type `TS`; require a non-null value; PostgreSQL supplies `NOW` when an INSERT omits the column. |
| L151 | `sa.PrimaryKeyConstraint('id', name='pk_documents')` — Declare the columns identifying each row uniquely and non-nullably. |
| L152 | `sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='fk_documents_project_id_projects', ondelete='CASCADE')` — Declare the referenced table/columns and configured deletion behavior. |
| L153 | Supply positional argument 1 to `sa.ForeignKeyConstraint`: build a list containing `'project_id'`. |
| L154 | Supply positional argument 2 to `sa.ForeignKeyConstraint`: build a list containing `'projects.id'`. |
| L155 | Supply `name` = `'fk_documents_project_id_projects'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'fk_documents_project_id_projects'`. |
| L156 | Supply `ondelete` = `'CASCADE'`.  Evaluate the value as: `'CASCADE'`. |
| L157 | Close the expression/container begun at L152; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L158 | `sa.UniqueConstraint('appwrite_file_id', name='uq_documents_appwrite_file_id')` — Declare uniqueness across the named columns; conflicting inserted/updated values are rejected by PostgreSQL. |
| L159 | Supply `name` = `'uq_documents_appwrite_file_id'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'uq_documents_appwrite_file_id'`. |
| L160 | Close the expression/container begun at L158; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L161 | `sa.CheckConstraint('length(btrim(file_name)) BETWEEN 1 AND 255', name='ck_documents_file_name_valid')` — Require 1–255 characters in the trimmed filename label; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L162 | Supply positional argument 1 to `sa.CheckConstraint`: `'length(btrim(file_name)) BETWEEN 1 AND 255'`. |
| L163 | Supply `name` = `'ck_documents_file_name_valid'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_documents_file_name_valid'`. |
| L164 | Close the expression/container begun at L161; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L165 | `sa.CheckConstraint("content_sha256 IS NULL OR content_sha256 ~ '^[0-9a-f]{64}$'", name='ck_documents_content_sha256_hex')` — Allow a missing digest, or exactly 64 lowercase hexadecimal characters anchored at both ends; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L166 | Supply positional argument 1 to `sa.CheckConstraint`: `"content_sha256 IS NULL OR content_sha256 ~ '^[0-9a-f]{64}$'"`. |
| L167 | Supply `name` = `'ck_documents_content_sha256_hex'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_documents_content_sha256_hex'`. |
| L168 | Close the expression/container begun at L165; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L169 | `sa.CheckConstraint('file_size IS NULL OR file_size > 0', name='ck_documents_file_size_positive')` — Allow unknown size, otherwise require a strictly positive byte count; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L170 | Supply `name` = `'ck_documents_file_size_positive'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_documents_file_size_positive'`. |
| L171 | Close the expression/container begun at L169; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L172 | `sa.CheckConstraint("mime_type IS NULL OR mime_type = 'application/pdf'", name='ck_documents_mime_type_pdf')` — Allow unknown MIME, otherwise require application/pdf; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L173 | Supply positional argument 1 to `sa.CheckConstraint`: `"mime_type IS NULL OR mime_type = 'application/pdf'"`. |
| L174 | Supply `name` = `'ck_documents_mime_type_pdf'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_documents_mime_type_pdf'`. |
| L175 | Close the expression/container begun at L172; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L176 | `sa.CheckConstraint("status IN ('Pending', 'Processing', 'Completed', 'Failed')", name='ck_documents_status_valid')` — Restrict the state/role to the listed literal values (column nullability is enforced separately); install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L177 | Supply positional argument 1 to `sa.CheckConstraint`: `"status IN ('Pending', 'Processing', 'Completed', 'Failed')"`. |
| L178 | Supply `name` = `'ck_documents_status_valid'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_documents_status_valid'`. |
| L179 | Close the expression/container begun at L176; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L180 | `sa.CheckConstraint('processing_epoch >= 0', name='ck_documents_processing_epoch_nonnegative')` — Reject negative document processing epochs; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L181 | Supply `name` = `'ck_documents_processing_epoch_nonnegative'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_documents_processing_epoch_nonnegative'`. |
| L182 | Close the expression/container begun at L180; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L183 | `sa.CheckConstraint('chunk_count IS NULL OR chunk_count >= 0', name='ck_documents_chunk_count_nonnegative')` — Allow unknown chunk count, otherwise require a nonnegative count; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L184 | Supply positional argument 1 to `sa.CheckConstraint`: `'chunk_count IS NULL OR chunk_count >= 0'`. |
| L185 | Supply `name` = `'ck_documents_chunk_count_nonnegative'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_documents_chunk_count_nonnegative'`. |
| L186 | Close the expression/container begun at L183; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L187 | `sa.CheckConstraint` with the arguments detailed below — A Completed document must have size, chunk count, active version, and processed timestamp; other states may leave these absent; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L188 | Supply positional argument 1 to `sa.CheckConstraint`: `"status <> 'Completed' OR (file_size IS NOT NULL AND chunk_count IS NOT NULL AND active_index_version IS NOT NULL AND processed_at IS NOT NULL)"`. |
| L189 | Supply positional argument 1 to `sa.CheckConstraint`: `"status <> 'Completed' OR (file_size IS NOT NULL AND chunk_count IS NOT NULL AND active_index_version IS NOT NULL AND processed_at IS NOT NULL)"`. |
| L190 | Supply positional argument 1 to `sa.CheckConstraint`: `"status <> 'Completed' OR (file_size IS NOT NULL AND chunk_count IS NOT NULL AND active_index_version IS NOT NULL AND processed_at IS NOT NULL)"`. |
| L191 | Supply `name` = `'ck_documents_completed_requires_publish'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_documents_completed_requires_publish'`. |
| L192 | Close the expression/container begun at L187; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L193 | Close the expression/container begun at L117; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L194 | `op.create_index('ix_documents_project_id', 'documents', ['project_id'])` — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L195 | `op.create_index('uq_documents_project_upload_request', 'documents', ['project_id', 'upload_request_id'], unique=True)` — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L196 | Supply positional argument 1 to `op.create_index`: `'uq_documents_project_upload_request'`. |
| L197 | Supply positional argument 2 to `op.create_index`: `'documents'`. |
| L198 | Supply positional argument 3 to `op.create_index`: build a list containing `'project_id'`, `'upload_request_id'`. |
| L199 | Supply `unique` = `True`.  Evaluate the value as: `True`. |
| L200 | Close the expression/container begun at L195; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L201 | `op.create_index('ix_documents_project_status', 'documents', ['project_id', 'status', 'deleted_at'])` — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L202 | Supply positional argument 1 to `op.create_index`: `'ix_documents_project_status'`. |
| L203 | Supply positional argument 2 to `op.create_index`: `'documents'`. |
| L204 | Supply positional argument 3 to `op.create_index`: build a list containing `'project_id'`, `'status'`, `'deleted_at'`. |
| L205 | Close the expression/container begun at L201; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L206 | `op.create_index('ix_documents_project_live', 'documents', ['project_id', 'status', 'created_at'], postgresql_where=sa.text('deleted_at IS NULL'))` — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L207 | Supply positional argument 1 to `op.create_index`: `'ix_documents_project_live'`. |
| L208 | Supply positional argument 2 to `op.create_index`: `'documents'`. |
| L209 | Supply positional argument 3 to `op.create_index`: build a list containing `'project_id'`, `'status'`, `'created_at'`. |
| L210 | Supply `postgresql_where` = `sa.text('deleted_at IS NULL')`.  Evaluate the value as: `sa.text('deleted_at IS NULL')` — Wrap trusted literal SQL for SQLAlchemy/Alembic; it is not an input-escaping function. |
| L211 | Close the expression/container begun at L206; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L213 | Comment only: --------------------------------------------------------- conversations. It does not execute; the neighboring code determines behavior. |
| L214 | `op.create_table` with the arguments detailed below — Issue Alembic DDL to create the named table with the listed columns and constraints; inputs include `sa.Column('id', UUID, nullable=False, server_default=NEW_UUID)` — Declare column `'id'` with type `UUID`; require a non-null value; PostgreSQL supplies `NEW_UUID` when an INSERT omits the column; `sa.Column('project_id', UUID, nullable=False)` — Declare column `'project_id'` with type `UUID`; require a non-null value; no server default is supplied by this declaration. The return value is not assigned here. |
| L215 | Supply positional argument 1 to `op.create_table`: `'conversations'`. |
| L216 | `sa.Column('id', UUID, nullable=False, server_default=NEW_UUID)` — Declare column `'id'` with type `UUID`; require a non-null value; PostgreSQL supplies `NEW_UUID` when an INSERT omits the column. |
| L217 | `sa.Column('project_id', UUID, nullable=False)` — Declare column `'project_id'` with type `UUID`; require a non-null value; no server default is supplied by this declaration. |
| L218 | `sa.Column('title', sa.String(255), nullable=True)` — Declare column `'title'` with type `sa.String(255)`; allow SQL NULL; no server default is supplied by this declaration; inputs include `sa.String(255)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L219 | `sa.Column('created_at', TS, nullable=False, server_default=NOW)` — Declare column `'created_at'` with type `TS`; require a non-null value; PostgreSQL supplies `NOW` when an INSERT omits the column. |
| L220 | `sa.Column('updated_at', TS, nullable=False, server_default=NOW)` — Declare column `'updated_at'` with type `TS`; require a non-null value; PostgreSQL supplies `NOW` when an INSERT omits the column. |
| L221 | `sa.PrimaryKeyConstraint('id', name='pk_conversations')` — Declare the columns identifying each row uniquely and non-nullably. |
| L222 | `sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='fk_conversations_project_id_projects', ondelete='CASCADE')` — Declare the referenced table/columns and configured deletion behavior. |
| L223 | Supply positional argument 1 to `sa.ForeignKeyConstraint`: build a list containing `'project_id'`. |
| L224 | Supply positional argument 2 to `sa.ForeignKeyConstraint`: build a list containing `'projects.id'`. |
| L225 | Supply `name` = `'fk_conversations_project_id_projects'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'fk_conversations_project_id_projects'`. |
| L226 | Supply `ondelete` = `'CASCADE'`.  Evaluate the value as: `'CASCADE'`. |
| L227 | Close the expression/container begun at L222; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L228 | `sa.CheckConstraint('title IS NULL OR length(btrim(title)) BETWEEN 1 AND 255', name='ck_conversations_title_valid')` — Allow an absent conversation title, otherwise require 1–255 trimmed characters; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L229 | Supply positional argument 1 to `sa.CheckConstraint`: `'title IS NULL OR length(btrim(title)) BETWEEN 1 AND 255'`. |
| L230 | Supply `name` = `'ck_conversations_title_valid'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_conversations_title_valid'`. |
| L231 | Close the expression/container begun at L228; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L232 | Close the expression/container begun at L214; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L233 | `op.create_index('ix_conversations_project_id', 'conversations', ['project_id'])` — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L234 | `op.create_index('ix_conversations_project_activity', 'conversations', ['project_id', 'updated_at', 'id'])` — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L235 | Supply positional argument 1 to `op.create_index`: `'ix_conversations_project_activity'`. |
| L236 | Supply positional argument 2 to `op.create_index`: `'conversations'`. |
| L237 | Supply positional argument 3 to `op.create_index`: build a list containing `'project_id'`, `'updated_at'`, `'id'`. |
| L238 | Close the expression/container begun at L234; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L240 | Comment only: -------------------------------------------------------------- messages. It does not execute; the neighboring code determines behavior. |
| L241 | `op.create_table` with the arguments detailed below — Issue Alembic DDL to create the named table with the listed columns and constraints; inputs include `sa.Column('id', UUID, nullable=False, server_default=NEW_UUID)` — Declare column `'id'` with type `UUID`; require a non-null value; PostgreSQL supplies `NEW_UUID` when an INSERT omits the column; `sa.Column('conversation_id', UUID, nullable=False)` — Declare column `'conversation_id'` with type `UUID`; require a non-null value; no server default is supplied by this declaration. The return value is not assigned here. |
| L242 | Supply positional argument 1 to `op.create_table`: `'messages'`. |
| L243 | `sa.Column('id', UUID, nullable=False, server_default=NEW_UUID)` — Declare column `'id'` with type `UUID`; require a non-null value; PostgreSQL supplies `NEW_UUID` when an INSERT omits the column. |
| L244 | `sa.Column('conversation_id', UUID, nullable=False)` — Declare column `'conversation_id'` with type `UUID`; require a non-null value; no server default is supplied by this declaration. |
| L245 | `sa.Column('role', sa.String(20), nullable=False)` — Declare column `'role'` with type `sa.String(20)`; require a non-null value; no server default is supplied by this declaration; inputs include `sa.String(20)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L246 | `sa.Column('content', sa.Text, nullable=False)` — Declare column `'content'` with type `sa.Text`; require a non-null value; no server default is supplied by this declaration. |
| L247 | `sa.Column('position', sa.BigInteger, nullable=False)` — Declare column `'position'` with type `sa.BigInteger`; require a non-null value; no server default is supplied by this declaration. |
| L248 | `sa.Column('citations', postgresql.JSONB, nullable=True)` — Declare column `'citations'` with type `postgresql.JSONB`; allow SQL NULL; no server default is supplied by this declaration. |
| L249 | `sa.Column('metadata', postgresql.JSONB, nullable=True)` — Declare column `'metadata'` with type `postgresql.JSONB`; allow SQL NULL; no server default is supplied by this declaration. |
| L250 | `sa.Column('client_request_id', UUID, nullable=True)` — Declare column `'client_request_id'` with type `UUID`; allow SQL NULL; no server default is supplied by this declaration. |
| L251 | `sa.Column('reply_to_message_id', UUID, nullable=True)` — Declare column `'reply_to_message_id'` with type `UUID`; allow SQL NULL; no server default is supplied by this declaration. |
| L252 | `sa.Column('generation_status', sa.String(20), nullable=True)` — Declare column `'generation_status'` with type `sa.String(20)`; allow SQL NULL; no server default is supplied by this declaration; inputs include `sa.String(20)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L253 | `sa.Column('generation_token', UUID, nullable=True)` — Declare column `'generation_token'` with type `UUID`; allow SQL NULL; no server default is supplied by this declaration. |
| L254 | `sa.Column('generation_expires_at', TS, nullable=True)` — Declare column `'generation_expires_at'` with type `TS`; allow SQL NULL; no server default is supplied by this declaration. |
| L255 | `sa.Column('created_at', TS, nullable=False, server_default=NOW)` — Declare column `'created_at'` with type `TS`; require a non-null value; PostgreSQL supplies `NOW` when an INSERT omits the column. |
| L256 | `sa.PrimaryKeyConstraint('id', name='pk_messages')` — Declare the columns identifying each row uniquely and non-nullably. |
| L257 | `sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], name='fk_messages_conversation_id_conversations', ondelete='CASCADE')` — Declare the referenced table/columns and configured deletion behavior. |
| L258 | Supply positional argument 1 to `sa.ForeignKeyConstraint`: build a list containing `'conversation_id'`. |
| L259 | Supply positional argument 2 to `sa.ForeignKeyConstraint`: build a list containing `'conversations.id'`. |
| L260 | Supply `name` = `'fk_messages_conversation_id_conversations'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'fk_messages_conversation_id_conversations'`. |
| L261 | Supply `ondelete` = `'CASCADE'`.  Evaluate the value as: `'CASCADE'`. |
| L262 | Close the expression/container begun at L257; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L263 | `sa.ForeignKeyConstraint(['reply_to_message_id'], ['messages.id'], name='fk_messages_reply_to_message_id_messages', ondelete='CASCADE')` — Declare the referenced table/columns and configured deletion behavior. |
| L264 | Supply positional argument 1 to `sa.ForeignKeyConstraint`: build a list containing `'reply_to_message_id'`. |
| L265 | Supply positional argument 2 to `sa.ForeignKeyConstraint`: build a list containing `'messages.id'`. |
| L266 | Supply `name` = `'fk_messages_reply_to_message_id_messages'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'fk_messages_reply_to_message_id_messages'`. |
| L267 | Supply `ondelete` = `'CASCADE'`.  Evaluate the value as: `'CASCADE'`. |
| L268 | Close the expression/container begun at L263; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L269 | `sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name='ck_messages_role_valid')` — Restrict the state/role to the listed literal values (column nullability is enforced separately); install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L270 | Supply `name` = `'ck_messages_role_valid'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_messages_role_valid'`. |
| L271 | Close the expression/container begun at L269; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L272 | `sa.CheckConstraint('position >= 1', name='ck_messages_position_positive')` — Require one-based positive message positions; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L273 | `sa.CheckConstraint('length(content) > 0', name='ck_messages_content_nonempty')` — Reject empty message content; this SQL check alone still accepts whitespace-only text; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L274 | `sa.CheckConstraint('reply_to_message_id IS NULL OR reply_to_message_id <> id', name='ck_messages_reply_not_self')` — Allow no reply target, otherwise forbid a message replying to itself; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L275 | Supply positional argument 1 to `sa.CheckConstraint`: `'reply_to_message_id IS NULL OR reply_to_message_id <> id'`. |
| L276 | Supply `name` = `'ck_messages_reply_not_self'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_messages_reply_not_self'`. |
| L277 | Close the expression/container begun at L274; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L278 | `sa.CheckConstraint("generation_status IN ('pending', 'generating', 'completed', 'failed', 'cancelled')", name='ck_messages_generation_status_valid')` — Restrict the state/role to the listed literal values (column nullability is enforced separately); install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L279 | Supply positional argument 1 to `sa.CheckConstraint`: `"generation_status IN ('pending', 'generating', 'completed', 'failed', 'cancelled')"`. |
| L280 | Supply `name` = `'ck_messages_generation_status_valid'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_messages_generation_status_valid'`. |
| L281 | Close the expression/container begun at L278; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L282 | `sa.CheckConstraint("generation_status IS NULL OR role = 'user'", name='ck_messages_generation_status_user_only')` — Only user messages may store a non-null generation status; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L283 | Supply positional argument 1 to `sa.CheckConstraint`: `"generation_status IS NULL OR role = 'user'"`. |
| L284 | Supply `name` = `'ck_messages_generation_status_user_only'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_messages_generation_status_user_only'`. |
| L285 | Close the expression/container begun at L282; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L286 | `sa.CheckConstraint("generation_expires_at IS NULL OR generation_status IN ('pending', 'generating')", name='ck_messages_generation_expiry_only_while_active')` — A non-null generation expiry requires an active generation state; SQL NULL truth semantics are subject to the column's other constraints; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L287 | Supply positional argument 1 to `sa.CheckConstraint`: `"generation_expires_at IS NULL OR generation_status IN ('pending', 'generating')"`. |
| L288 | Supply positional argument 1 to `sa.CheckConstraint`: `"generation_expires_at IS NULL OR generation_status IN ('pending', 'generating')"`. |
| L289 | Supply `name` = `'ck_messages_generation_expiry_only_while_active'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_messages_generation_expiry_only_while_active'`. |
| L290 | Close the expression/container begun at L286; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L291 | `sa.CheckConstraint("citations IS NULL OR jsonb_typeof(citations) = 'array'", name='ck_messages_citations_is_array')` — Allow no citations or a top-level JSON array; this does not validate each citation object's evidence; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L292 | Supply positional argument 1 to `sa.CheckConstraint`: `"citations IS NULL OR jsonb_typeof(citations) = 'array'"`. |
| L293 | Supply `name` = `'ck_messages_citations_is_array'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_messages_citations_is_array'`. |
| L294 | Close the expression/container begun at L291; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L295 | `sa.CheckConstraint("metadata IS NULL OR jsonb_typeof(metadata) = 'object'", name='ck_messages_metadata_is_object')` — Allow absent message metadata or a top-level JSON object; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L296 | Supply positional argument 1 to `sa.CheckConstraint`: `"metadata IS NULL OR jsonb_typeof(metadata) = 'object'"`. |
| L297 | Supply `name` = `'ck_messages_metadata_is_object'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_messages_metadata_is_object'`. |
| L298 | Close the expression/container begun at L295; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L299 | Close the expression/container begun at L241; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L300 | `op.create_index('uq_messages_conversation_position', 'messages', ['conversation_id', 'position'], unique=True)` — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L301 | Supply positional argument 1 to `op.create_index`: `'uq_messages_conversation_position'`. |
| L302 | Supply positional argument 2 to `op.create_index`: `'messages'`. |
| L303 | Supply positional argument 3 to `op.create_index`: build a list containing `'conversation_id'`, `'position'`. |
| L304 | Supply `unique` = `True`.  Evaluate the value as: `True`. |
| L305 | Close the expression/container begun at L300; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L306 | `op.create_index('ix_messages_conversation_created', 'messages', ['conversation_id', 'created_at', 'position'])` — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L307 | Supply positional argument 1 to `op.create_index`: `'ix_messages_conversation_created'`. |
| L308 | Supply positional argument 2 to `op.create_index`: `'messages'`. |
| L309 | Supply positional argument 3 to `op.create_index`: build a list containing `'conversation_id'`, `'created_at'`, `'position'`. |
| L310 | Close the expression/container begun at L306; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L311 | `op.create_index` with the arguments detailed below — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L312 | Supply positional argument 1 to `op.create_index`: `'uq_messages_conversation_client_request'`. |
| L313 | Supply positional argument 2 to `op.create_index`: `'messages'`. |
| L314 | Supply positional argument 3 to `op.create_index`: build a list containing `'conversation_id'`, `'client_request_id'`. |
| L315 | Supply `unique` = `True`.  Evaluate the value as: `True`. |
| L316 | Supply `postgresql_where` = `sa.text("role = 'user' AND client_request_id IS NOT NULL")`.  Evaluate the value as: `sa.text("role = 'user' AND client_request_id IS NOT NULL")` — Wrap trusted literal SQL for SQLAlchemy/Alembic; it is not an input-escaping function. |
| L317 | Supply positional argument 1 to `sa.text`: `"role = 'user' AND client_request_id IS NOT NULL"`. |
| L318 | Close the expression/container begun at L316; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L319 | Close the expression/container begun at L311; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L320 | `op.create_index` with the arguments detailed below — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L321 | Supply positional argument 1 to `op.create_index`: `'uq_messages_reply_to'`. |
| L322 | Supply positional argument 2 to `op.create_index`: `'messages'`. |
| L323 | Supply positional argument 3 to `op.create_index`: build a list containing `'reply_to_message_id'`. |
| L324 | Supply `unique` = `True`.  Evaluate the value as: `True`. |
| L325 | Supply `postgresql_where` = `sa.text("role = 'assistant' AND reply_to_message_id IS NOT NULL")`.  Evaluate the value as: `sa.text("role = 'assistant' AND reply_to_message_id IS NOT NULL")` — Wrap trusted literal SQL for SQLAlchemy/Alembic; it is not an input-escaping function. |
| L326 | Supply positional argument 1 to `sa.text`: `"role = 'assistant' AND reply_to_message_id IS NOT NULL"`. |
| L327 | Close the expression/container begun at L325; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L328 | Close the expression/container begun at L320; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L329 | `op.create_index` with the arguments detailed below — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L330 | Supply positional argument 1 to `op.create_index`: `'uq_messages_one_active_generation'`. |
| L331 | Supply positional argument 2 to `op.create_index`: `'messages'`. |
| L332 | Supply positional argument 3 to `op.create_index`: build a list containing `'conversation_id'`. |
| L333 | Supply `unique` = `True`.  Evaluate the value as: `True`. |
| L334 | Supply `postgresql_where` = `sa.text("role = 'user' AND generation_status IN ('pending', 'generating')")`.  Evaluate the value as: `sa.text("role = 'user' AND generation_status IN ('pending', 'generating')")` — Wrap trusted literal SQL for SQLAlchemy/Alembic; it is not an input-escaping function. |
| L335 | Supply positional argument 1 to `sa.text`: `"role = 'user' AND generation_status IN ('pending', 'generating')"`. |
| L336 | Close the expression/container begun at L334; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L337 | Close the expression/container begun at L329; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L338 | `op.create_index('ix_messages_reply_to', 'messages', ['reply_to_message_id'])` — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L339 | `op.create_index('ix_messages_generation_expiry', 'messages', ['generation_expires_at'])` — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L340 | Supply positional argument 1 to `op.create_index`: `'ix_messages_generation_expiry'`. |
| L341 | Close the expression/container begun at L339; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L343 | Comment only: -------------------------------------------------------- processing_jobs. It does not execute; the neighboring code determines behavior. |
| L344 | `op.create_table` with the arguments detailed below — Issue Alembic DDL to create the named table with the listed columns and constraints; inputs include `sa.Column('id', UUID, nullable=False, server_default=NEW_UUID)` — Declare column `'id'` with type `UUID`; require a non-null value; PostgreSQL supplies `NEW_UUID` when an INSERT omits the column; `sa.Column('document_id', UUID, nullable=True)` — Declare column `'document_id'` with type `UUID`; allow SQL NULL; no server default is supplied by this declaration. The return value is not assigned here. |
| L345 | Supply positional argument 1 to `op.create_table`: `'processing_jobs'`. |
| L346 | `sa.Column('id', UUID, nullable=False, server_default=NEW_UUID)` — Declare column `'id'` with type `UUID`; require a non-null value; PostgreSQL supplies `NEW_UUID` when an INSERT omits the column. |
| L347 | `sa.Column('document_id', UUID, nullable=True)` — Declare column `'document_id'` with type `UUID`; allow SQL NULL; no server default is supplied by this declaration. |
| L348 | Comment only: Immutable snapshots: intentionally NO foreign key (see models.py).. It does not execute; the neighboring code determines behavior. |
| L349 | `sa.Column('owner_user_id', UUID, nullable=False)` — Declare column `'owner_user_id'` with type `UUID`; require a non-null value; no server default is supplied by this declaration. |
| L350 | `sa.Column('project_id', UUID, nullable=False)` — Declare column `'project_id'` with type `UUID`; require a non-null value; no server default is supplied by this declaration. |
| L351 | `sa.Column('target_document_id', UUID, nullable=False)` — Declare column `'target_document_id'` with type `UUID`; require a non-null value; no server default is supplied by this declaration. |
| L352 | `sa.Column('resource_snapshot', postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))` — Declare column `'resource_snapshot'` with type `postgresql.JSONB`; require a non-null value; PostgreSQL supplies `sa.text("'{}'::jsonb")` when an INSERT omits the column. |
| L353 | Supply positional argument 1 to `sa.Column`: `'resource_snapshot'`. |
| L354 | Supply positional argument 2 to `sa.Column`: the `JSONB` attribute of `postgresql`. |
| L355 | Supply `nullable` = `False`.  Evaluate the value as: `False`. |
| L356 | Supply `server_default` = `sa.text("'{}'::jsonb")`.  Evaluate the value as: `sa.text("'{}'::jsonb")` — Wrap trusted literal SQL for SQLAlchemy/Alembic; it is not an input-escaping function. |
| L357 | Close the expression/container begun at L352; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L358 | `sa.Column('target_epoch', sa.BigInteger, nullable=False, server_default=sa.text('0'))` — Declare column `'target_epoch'` with type `sa.BigInteger`; require a non-null value; PostgreSQL supplies `sa.text('0')` when an INSERT omits the column. |
| L359 | Supply `nullable` = `False`.  Evaluate the value as: `False`. Supply `server_default` = `sa.text('0')`.  Evaluate the value as: `sa.text('0')` — Wrap trusted literal SQL for SQLAlchemy/Alembic; it is not an input-escaping function. |
| L360 | Close the expression/container begun at L358; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L361 | `sa.Column('kind', sa.String(30), nullable=False)` — Declare column `'kind'` with type `sa.String(30)`; require a non-null value; no server default is supplied by this declaration; inputs include `sa.String(30)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L362 | `sa.Column('status', sa.String(30), nullable=False)` — Declare column `'status'` with type `sa.String(30)`; require a non-null value; no server default is supplied by this declaration; inputs include `sa.String(30)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L363 | `sa.Column('stage', sa.String(30), nullable=True)` — Declare column `'stage'` with type `sa.String(30)`; allow SQL NULL; no server default is supplied by this declaration; inputs include `sa.String(30)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L364 | `sa.Column('attempt_count', sa.Integer, nullable=False, server_default=sa.text('0'))` — Declare column `'attempt_count'` with type `sa.Integer`; require a non-null value; PostgreSQL supplies `sa.text('0')` when an INSERT omits the column. |
| L365 | Supply `nullable` = `False`.  Evaluate the value as: `False`. Supply `server_default` = `sa.text('0')`.  Evaluate the value as: `sa.text('0')` — Wrap trusted literal SQL for SQLAlchemy/Alembic; it is not an input-escaping function. |
| L366 | Close the expression/container begun at L364; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L367 | `sa.Column('max_attempts', sa.Integer, nullable=False, server_default=sa.text('3'))` — Declare column `'max_attempts'` with type `sa.Integer`; require a non-null value; PostgreSQL supplies `sa.text('3')` when an INSERT omits the column. |
| L368 | Supply `nullable` = `False`.  Evaluate the value as: `False`. Supply `server_default` = `sa.text('3')`.  Evaluate the value as: `sa.text('3')` — Wrap trusted literal SQL for SQLAlchemy/Alembic; it is not an input-escaping function. |
| L369 | Close the expression/container begun at L367; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L370 | `sa.Column('available_at', TS, nullable=False, server_default=NOW)` — Declare column `'available_at'` with type `TS`; require a non-null value; PostgreSQL supplies `NOW` when an INSERT omits the column. |
| L371 | `sa.Column('lease_owner', sa.String(255), nullable=True)` — Declare column `'lease_owner'` with type `sa.String(255)`; allow SQL NULL; no server default is supplied by this declaration; inputs include `sa.String(255)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L372 | `sa.Column('lease_token', sa.BigInteger, nullable=True)` — Declare column `'lease_token'` with type `sa.BigInteger`; allow SQL NULL; no server default is supplied by this declaration. |
| L373 | `sa.Column('lease_expires_at', TS, nullable=True)` — Declare column `'lease_expires_at'` with type `TS`; allow SQL NULL; no server default is supplied by this declaration. |
| L374 | `sa.Column('index_version', UUID, nullable=True)` — Declare column `'index_version'` with type `UUID`; allow SQL NULL; no server default is supplied by this declaration. |
| L375 | `sa.Column('progress_current', sa.Integer, nullable=True)` — Declare column `'progress_current'` with type `sa.Integer`; allow SQL NULL; no server default is supplied by this declaration. |
| L376 | `sa.Column('progress_total', sa.Integer, nullable=True)` — Declare column `'progress_total'` with type `sa.Integer`; allow SQL NULL; no server default is supplied by this declaration. |
| L377 | `sa.Column('last_error_code', sa.String(100), nullable=True)` — Declare column `'last_error_code'` with type `sa.String(100)`; allow SQL NULL; no server default is supplied by this declaration; inputs include `sa.String(100)` — Construct `sa.String` with the shown fields; its class/model initialization rules apply. |
| L378 | `sa.Column('last_error_message', sa.Text, nullable=True)` — Declare column `'last_error_message'` with type `sa.Text`; allow SQL NULL; no server default is supplied by this declaration. |
| L379 | `sa.Column('created_at', TS, nullable=False, server_default=NOW)` — Declare column `'created_at'` with type `TS`; require a non-null value; PostgreSQL supplies `NOW` when an INSERT omits the column. |
| L380 | `sa.Column('updated_at', TS, nullable=False, server_default=NOW)` — Declare column `'updated_at'` with type `TS`; require a non-null value; PostgreSQL supplies `NOW` when an INSERT omits the column. |
| L381 | `sa.Column('finished_at', TS, nullable=True)` — Declare column `'finished_at'` with type `TS`; allow SQL NULL; no server default is supplied by this declaration. |
| L382 | `sa.PrimaryKeyConstraint('id', name='pk_processing_jobs')` — Declare the columns identifying each row uniquely and non-nullably. |
| L383 | `sa.ForeignKeyConstraint(['document_id'], ['documents.id'], name='fk_processing_jobs_document_id_documents', ondelete='SET NULL')` — Declare the referenced table/columns and configured deletion behavior. |
| L384 | Supply positional argument 1 to `sa.ForeignKeyConstraint`: build a list containing `'document_id'`. |
| L385 | Supply positional argument 2 to `sa.ForeignKeyConstraint`: build a list containing `'documents.id'`. |
| L386 | Supply `name` = `'fk_processing_jobs_document_id_documents'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'fk_processing_jobs_document_id_documents'`. |
| L387 | Supply `ondelete` = `'SET NULL'`.  Evaluate the value as: `'SET NULL'`. |
| L388 | Close the expression/container begun at L383; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L389 | `sa.CheckConstraint("kind IN ('process_document', 'delete_document')", name='ck_processing_jobs_kind_valid')` — Restrict the state/role to the listed literal values (column nullability is enforced separately); install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L390 | Supply positional argument 1 to `sa.CheckConstraint`: `"kind IN ('process_document', 'delete_document')"`. |
| L391 | Supply `name` = `'ck_processing_jobs_kind_valid'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_processing_jobs_kind_valid'`. |
| L392 | Close the expression/container begun at L389; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L393 | `sa.CheckConstraint` with the arguments detailed below — Restrict the state/role to the listed literal values (column nullability is enforced separately); install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L394 | Supply positional argument 1 to `sa.CheckConstraint`: `"status IN ('awaiting_upload', 'queued', 'running', 'retry_wait', 'succeeded', 'failed', 'cancelled')"`. |
| L395 | Supply positional argument 1 to `sa.CheckConstraint`: `"status IN ('awaiting_upload', 'queued', 'running', 'retry_wait', 'succeeded', 'failed', 'cancelled')"`. |
| L396 | Supply `name` = `'ck_processing_jobs_status_valid'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_processing_jobs_status_valid'`. |
| L397 | Close the expression/container begun at L393; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L398 | `sa.CheckConstraint` with the arguments detailed below — Restrict the state/role to the listed literal values, explicitly allowing NULL here; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L399 | Supply positional argument 1 to `sa.CheckConstraint`: `"stage IS NULL OR stage IN ('uploading', 'extracting', 'chunking', 'embedding', 'indexing', 'publishing', 'deleting')"`. |
| L400 | Supply positional argument 1 to `sa.CheckConstraint`: `"stage IS NULL OR stage IN ('uploading', 'extracting', 'chunking', 'embedding', 'indexing', 'publishing', 'deleting')"`. |
| L401 | Supply `name` = `'ck_processing_jobs_stage_valid'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_processing_jobs_stage_valid'`. |
| L402 | Close the expression/container begun at L398; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L403 | `sa.CheckConstraint('target_epoch >= 0', name='ck_processing_jobs_target_epoch_nonnegative')` — Require a nonnegative target document epoch; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L404 | Supply `name` = `'ck_processing_jobs_target_epoch_nonnegative'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_processing_jobs_target_epoch_nonnegative'`. |
| L405 | Close the expression/container begun at L403; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L406 | `sa.CheckConstraint('attempt_count >= 0', name='ck_processing_jobs_attempt_count_nonnegative')` — Require a nonnegative claimed-attempt count; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L407 | Supply `name` = `'ck_processing_jobs_attempt_count_nonnegative'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_processing_jobs_attempt_count_nonnegative'`. |
| L408 | Close the expression/container begun at L406; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L409 | `sa.CheckConstraint('max_attempts >= 1', name='ck_processing_jobs_max_attempts_positive')` — Require at least one permitted attempt; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L410 | Supply `name` = `'ck_processing_jobs_max_attempts_positive'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_processing_jobs_max_attempts_positive'`. |
| L411 | Close the expression/container begun at L409; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L412 | `sa.CheckConstraint('lease_token IS NULL OR lease_token >= 1', name='ck_processing_jobs_lease_token_positive')` — Allow null token where permitted by column nullability, otherwise require a positive fencing token; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L413 | Supply positional argument 1 to `sa.CheckConstraint`: `'lease_token IS NULL OR lease_token >= 1'`. |
| L414 | Supply `name` = `'ck_processing_jobs_lease_token_positive'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_processing_jobs_lease_token_positive'`. |
| L415 | Close the expression/container begun at L412; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L416 | `sa.CheckConstraint('progress_current IS NULL OR progress_current >= 0', name='ck_processing_jobs_progress_current_nonnegative')` — Allow unknown current progress, otherwise require a nonnegative counter; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L417 | Supply positional argument 1 to `sa.CheckConstraint`: `'progress_current IS NULL OR progress_current >= 0'`. |
| L418 | Supply `name` = `'ck_processing_jobs_progress_current_nonnegative'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_processing_jobs_progress_current_nonnegative'`. |
| L419 | Close the expression/container begun at L416; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L420 | `sa.CheckConstraint('progress_total IS NULL OR progress_total >= 0', name='ck_processing_jobs_progress_total_nonnegative')` — Allow unknown total progress, otherwise require a nonnegative counter; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L421 | Supply positional argument 1 to `sa.CheckConstraint`: `'progress_total IS NULL OR progress_total >= 0'`. |
| L422 | Supply `name` = `'ck_processing_jobs_progress_total_nonnegative'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_processing_jobs_progress_total_nonnegative'`. |
| L423 | Close the expression/container begun at L420; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L424 | `sa.CheckConstraint` with the arguments detailed below — When both progress counters exist, require current ≤ total; either unknown value bypasses this comparison; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L425 | Supply positional argument 1 to `sa.CheckConstraint`: `'progress_current IS NULL OR progress_total IS NULL OR progress_current <= progress_total'`. |
| L426 | Supply positional argument 1 to `sa.CheckConstraint`: `'progress_current IS NULL OR progress_total IS NULL OR progress_current <= progress_total'`. |
| L427 | Supply `name` = `'ck_processing_jobs_progress_current_le_total'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_processing_jobs_progress_current_le_total'`. |
| L428 | Close the expression/container begun at L424; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L429 | `sa.CheckConstraint("jsonb_typeof(resource_snapshot) = 'object'", name='ck_processing_jobs_resource_snapshot_is_object')` — Require a top-level JSON object for the durable resource snapshot, not an array or scalar; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L430 | Supply positional argument 1 to `sa.CheckConstraint`: `"jsonb_typeof(resource_snapshot) = 'object'"`. |
| L431 | Supply `name` = `'ck_processing_jobs_resource_snapshot_is_object'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_processing_jobs_resource_snapshot_is_object'`. |
| L432 | Close the expression/container begun at L429; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L433 | `sa.CheckConstraint('finished_at IS NULL OR finished_at >= created_at', name='ck_processing_jobs_finished_after_created')` — Allow unfinished jobs; otherwise prevent finish time from preceding creation; install this CHECK constraint so PostgreSQL rejects rows when its expression is false. |
| L434 | Supply positional argument 1 to `sa.CheckConstraint`: `'finished_at IS NULL OR finished_at >= created_at'`. |
| L435 | Supply `name` = `'ck_processing_jobs_finished_after_created'`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: `'ck_processing_jobs_finished_after_created'`. |
| L436 | Close the expression/container begun at L433; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L437 | Close the expression/container begun at L344; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L438 | `op.create_index('ix_processing_jobs_due', 'processing_jobs', ['status', 'available_at', 'created_at'])` — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L439 | Supply positional argument 1 to `op.create_index`: `'ix_processing_jobs_due'`. |
| L440 | Supply positional argument 2 to `op.create_index`: `'processing_jobs'`. |
| L441 | Supply positional argument 3 to `op.create_index`: build a list containing `'status'`, `'available_at'`, `'created_at'`. |
| L442 | Close the expression/container begun at L438; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L443 | `op.create_index` with the arguments detailed below — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L444 | Supply positional argument 1 to `op.create_index`: `'ix_processing_jobs_due_claimable'`. |
| L445 | Supply positional argument 2 to `op.create_index`: `'processing_jobs'`. |
| L446 | Supply positional argument 3 to `op.create_index`: build a list containing `'available_at'`, `'created_at'`. |
| L447 | Supply `postgresql_where` = `sa.text("status IN ('queued', 'retry_wait')")`.  Evaluate the value as: `sa.text("status IN ('queued', 'retry_wait')")` — Wrap trusted literal SQL for SQLAlchemy/Alembic; it is not an input-escaping function. |
| L448 | Close the expression/container begun at L443; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L449 | `op.create_index` with the arguments detailed below — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L450 | Supply positional argument 1 to `op.create_index`: `'ix_processing_jobs_lease_expiry'`. |
| L451 | Supply positional argument 2 to `op.create_index`: `'processing_jobs'`. |
| L452 | Supply positional argument 3 to `op.create_index`: build a list containing `'lease_expires_at'`. |
| L453 | Supply `postgresql_where` = `sa.text("status = 'running' AND lease_expires_at IS NOT NULL")`.  Evaluate the value as: `sa.text("status = 'running' AND lease_expires_at IS NOT NULL")` — Wrap trusted literal SQL for SQLAlchemy/Alembic; it is not an input-escaping function. |
| L454 | Supply positional argument 1 to `sa.text`: `"status = 'running' AND lease_expires_at IS NOT NULL"`. |
| L455 | Close the expression/container begun at L453; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L456 | Close the expression/container begun at L449; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L457 | `op.create_index('ix_processing_jobs_owner', 'processing_jobs', ['owner_user_id', 'created_at', 'id'])` — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L458 | Supply positional argument 1 to `op.create_index`: `'ix_processing_jobs_owner'`. |
| L459 | Supply positional argument 2 to `op.create_index`: `'processing_jobs'`. |
| L460 | Supply positional argument 3 to `op.create_index`: build a list containing `'owner_user_id'`, `'created_at'`, `'id'`. |
| L461 | Close the expression/container begun at L457; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L462 | `op.create_index('ix_processing_jobs_document', 'processing_jobs', ['document_id'], postgresql_where=sa.text('document_id IS NOT NULL'))` — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L463 | Supply positional argument 1 to `op.create_index`: `'ix_processing_jobs_document'`. |
| L464 | Supply positional argument 2 to `op.create_index`: `'processing_jobs'`. |
| L465 | Supply positional argument 3 to `op.create_index`: build a list containing `'document_id'`. |
| L466 | Supply `postgresql_where` = `sa.text('document_id IS NOT NULL')`.  Evaluate the value as: `sa.text('document_id IS NOT NULL')` — Wrap trusted literal SQL for SQLAlchemy/Alembic; it is not an input-escaping function. |
| L467 | Close the expression/container begun at L462; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L468 | `op.create_index('ix_processing_jobs_project', 'processing_jobs', ['project_id', 'created_at', 'id'])` — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L469 | Supply positional argument 1 to `op.create_index`: `'ix_processing_jobs_project'`. |
| L470 | Supply positional argument 2 to `op.create_index`: `'processing_jobs'`. |
| L471 | Supply positional argument 3 to `op.create_index`: build a list containing `'project_id'`, `'created_at'`, `'id'`. |
| L472 | Close the expression/container begun at L468; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L473 | `op.create_index('ix_processing_jobs_target', 'processing_jobs', ['target_document_id', 'created_at', 'id'])` — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L474 | Supply positional argument 1 to `op.create_index`: `'ix_processing_jobs_target'`. |
| L475 | Supply positional argument 2 to `op.create_index`: `'processing_jobs'`. |
| L476 | Supply positional argument 3 to `op.create_index`: build a list containing `'target_document_id'`, `'created_at'`, `'id'`. |
| L477 | Close the expression/container begun at L473; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L478 | `op.create_index` with the arguments detailed below — Issue Alembic DDL to create the named index; unique and postgresql_where configure its enforcement scope. The return value is not assigned here. |
| L479 | Supply positional argument 1 to `op.create_index`: `'uq_processing_jobs_one_nonterminal_per_target_kind'`. |
| L480 | Supply positional argument 2 to `op.create_index`: `'processing_jobs'`. |
| L481 | Supply positional argument 3 to `op.create_index`: build a list containing `'target_document_id'`, `'kind'`. |
| L482 | Supply `unique` = `True`.  Evaluate the value as: `True`. |
| L483 | Supply `postgresql_where` = `sa.text("status IN ('awaiting_upload', 'queued', 'running', 'retry_wait')")`.  Evaluate the value as: `sa.text("status IN ('awaiting_upload', 'queued', 'running', 'retry_wait')")` — Wrap trusted literal SQL for SQLAlchemy/Alembic; it is not an input-escaping function. |
| L484 | Supply positional argument 1 to `sa.text`: `"status IN ('awaiting_upload', 'queued', 'running', 'retry_wait')"`. |
| L485 | Close the expression/container begun at L483; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L486 | Close the expression/container begun at L478; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `downgrade() -> None`

- **Arguments:** None; Alembic provides the operations context.
- **Returns:** `None`.
- **Work:** Drops `processing_jobs`, `messages`, `conversations`, `documents`, `projects`, and `users` in reverse dependency order. Dropping each table also removes its indexes and constraints. Leaves the shared `pgcrypto` extension installed.
- **Side effects:** Removes those tables and their data when executed online; it is not a data-preserving conversion or a legacy import.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-downgrade"></a>

#### Line-by-line execution

[Current source: lines 489–495](../../../../Backend/migrations/versions/a1v2init0001_v2_initial_schema.py#L489-L495). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 489 | def downgrade() -> None:
 490 |     op.drop_table("processing_jobs")
 491 |     op.drop_table("messages")
 492 |     op.drop_table("conversations")
 493 |     op.drop_table("documents")
 494 |     op.drop_table("projects")
 495 |     op.drop_table("users")
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L489 | Define `downgrade`; bind its arguments when called. The body executes only when invoked. |
| L490 | `op.drop_table('processing_jobs')` — Issue Alembic DDL to drop the named table during downgrade. The return value is not assigned here. |
| L491 | `op.drop_table('messages')` — Issue Alembic DDL to drop the named table during downgrade. The return value is not assigned here. |
| L492 | `op.drop_table('conversations')` — Issue Alembic DDL to drop the named table during downgrade. The return value is not assigned here. |
| L493 | `op.drop_table('documents')` — Issue Alembic DDL to drop the named table during downgrade. The return value is not assigned here. |
| L494 | `op.drop_table('projects')` — Issue Alembic DDL to drop the named table during downgrade. The return value is not assigned here. |
| L495 | `op.drop_table('users')` — Issue Alembic DDL to drop the named table during downgrade. The return value is not assigned here. |

<!-- END LINE WALKTHROUGH -->
