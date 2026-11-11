# `app/db/models.py`

[Source](../../../../Backend/app/db/models.py) · [Backend index](../../README.md)

Declares six PostgreSQL tables using SQLAlchemy 2. All primary keys use `uuid_pk()`; timestamps use [base.md](base.md). Import registers metadata without connecting. The corresponding DDL is in [the initial migration](../../migrations/versions/a1v2init0001_v2_initial_schema.md).

## Tables and relationships

### `User` → `users`

| Columns | Meaning / defaults |
| --- | --- |
| `id` | Internal UUID primary key |
| `appwrite_user_id`, `email` | Required, independently unique strings, each up to 255 characters |
| `name`, `date_of_birth` | Nullable profile (name up to 150 characters) |
| `onboarding_completed` | Required boolean, Python/server default false |
| `created_at`, `updated_at` | Required timezone-aware timestamps |

Checks require nonempty trimmed lowercase email, valid nonblank bounded names when present, DOB no later than the current date, and both profile fields for completed onboarding. `projects` is an ORM `all, delete-orphan` relationship; project FKs also cascade on user deletion. Bootstrap resolves identities by Appwrite ID, not email.

### `Project` → `projects`

Columns: UUID `id`; required UUID `user_id` (`users.id`, `ON DELETE CASCADE`); required `name` (255); nullable text `description`; nullable timestamp `deleted_at`; creation/update timestamps.

Checks require a trimmed-name length of 1–255 and a nonblank description when present. Indexes: `ix_projects_user_id`, `ix_projects_owner_listing(user_id, updated_at, id)`, and partial `ix_projects_owner_live` on the same columns where `deleted_at IS NULL`. `user` is the parent relationship; `documents` and `conversations` have ORM delete-orphan cascades. Normal repositories hide tombstones while external cleanup proceeds.

### `Document` → `documents`

| Columns | Meaning / defaults |
| --- | --- |
| `id`, `project_id` | UUID primary key and required cascading project FK |
| `file_name`, `appwrite_file_id` | Required 255-character label and independently unique private storage ID; labels need not be unique |
| `chroma_collection`, `chroma_document_id` | Nullable stored index-reference strings |
| `file_size`, `mime_type` | Nullable byte size; nullable MIME with `application/pdf` default |
| `status` | Required string, default `Pending` |
| `upload_request_id`, `content_sha256`, `upload_completed_at` | Required request UUID; nullable lowercase 64-hex digest and completion time |
| `processing_epoch` | Required nonnegative bigint, default 0; invalidates stale workers |
| `active_index_version`, `chunk_count`, `processed_at`, `processing_error` | Nullable published namespace/count/time and safe error summary |
| `deleted_at`, `created_at`, `updated_at` | Tombstone and lifecycle timestamps |

Checks validate filename length, digest syntax, positive optional file size, PDF-only optional MIME, four allowed statuses, nonnegative epoch/count, and require size/count/active version/processed time for `Completed`. They do not enforce the full upload/worker state machine.

Indexes: `ix_documents_project_id`; unique `uq_documents_project_upload_request(project_id, upload_request_id)`; `ix_documents_project_status(project_id, status, deleted_at)`; partial `ix_documents_project_live(project_id, status, created_at)` for live documents. `project` links upward; `jobs` uses passive deletion matching its nullable `SET NULL` FK.

### `Conversation` → `conversations`

Columns: UUID `id`, required cascading `project_id`, nullable title (255), creation/update timestamps. The title check accepts null or trimmed length 1–255. Indexes: `ix_conversations_project_id` and `ix_conversations_project_activity(project_id, updated_at, id)`. `messages` cascades/delete-orphans; there is no conversation tombstone.

### `Message` → `messages`

| Columns | Meaning |
| --- | --- |
| `id`, `conversation_id` | UUID primary key and required cascading conversation FK |
| `role`, `content`, `position` | Required role string, nonempty text, positive bigint order |
| `citations` | Nullable JSONB array; Python `None` persists as SQL NULL |
| `message_metadata` → SQL `metadata` | Nullable JSONB object; avoids SQLAlchemy's reserved `metadata` attribute |
| `client_request_id` | Nullable request UUID for user-turn idempotency |
| `reply_to_message_id` | Nullable self-FK, `ON DELETE CASCADE` |
| `generation_status`, `generation_token`, `generation_expires_at` | Nullable user-turn lifecycle/fencing state |
| `created_at` | Required timestamp; there is no `updated_at` column |

Checks constrain role/status values, forbid self-replies, require positive positions/nonempty content, restrict generation status to user rows and expiry to active states, and enforce JSON array/object top-level types. Citation provenance is application validation, not a database JSON-schema constraint.

Unique indexes enforce `(conversation_id, position)`, `(conversation_id, client_request_id)` for keyed user rows, one assistant per non-null `reply_to_message_id`, and one pending/generating user row per conversation. Other indexes cover conversation creation/order, reply target, and generation expiry. `conversation`, `reply_to`, and cascading `replies` are the ORM relationships.

### `ProcessingJob` → `processing_jobs`

| Columns | Meaning / defaults |
| --- | --- |
| `id`, `document_id` | UUID primary key; nullable live document FK with `ON DELETE SET NULL` |
| `owner_user_id`, `project_id`, `target_document_id` | Required UUID snapshots **without FKs**, preserving ownership/cleanup after resource deletion |
| `resource_snapshot` | Required JSONB object, default `{}` |
| `target_epoch` | Nonnegative bigint, default 0 |
| `kind`, `status`, `stage` | Required kind/status, nullable stage |
| `attempt_count`, `max_attempts`, `available_at` | Defaults 0, 3, and server `now()` |
| `lease_owner`, `lease_token`, `lease_expires_at` | Nullable worker identity, positive bigint fencing token, expiry |
| `index_version` | Nullable per-attempt namespace UUID |
| `progress_current`, `progress_total` | Nullable nonnegative integers; current must not exceed total when both exist |
| `last_error_code`, `last_error_message` | Nullable diagnostic code (100) and safe text |
| `created_at`, `updated_at`, `finished_at` | Required creation/update and nullable terminal timestamp |

Checks cover kind/status/stage enumerations, counters, lease token, snapshot JSON type, and finish time no earlier than creation. Indexes support due order, partial claimable due order, running lease expiry, immutable owner/project/target history, and non-null live document links. The partial unique `uq_processing_jobs_one_nonterminal_per_target_kind` prevents two active jobs for the same target and kind (`awaiting_upload`, `queued`, `running`, `retry_wait`).

## Enumerations

`DOCUMENT_STATUSES`, `MESSAGE_ROLES`, `GENERATION_STATUSES`, `JOB_KINDS`, `JOB_STATUSES`, `JOB_STAGES`, and terminal/nonterminal job tuples mirror [schema enums](../schemas/common.md). These tuples construct SQL checks and queue filters; they do not perform transitions.

## Functions

### `_in_list(column: str, values: tuple[str, ...]) -> str`

- **Arguments:** A trusted schema column name and trusted constant string values.
- **Returns:** SQL text such as `status IN ('Pending', 'Processing', 'Completed', 'Failed')`.
- **Work:** Single-quotes each constant, joins with commas, and formats the expression for `CheckConstraint`. It is not a user-input SQL escaping function.

The six ORM classes have no locally implemented methods; constructors, attribute instrumentation, and persistence behavior come from SQLAlchemy and the declared relationships/defaults.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--in-list"></a>

#### Line-by-line execution

[Current source: lines 86–88](../../../../Backend/app/db/models.py#L86-L88). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `column` | `str`; required; positional or keyword | Caller-supplied column; each read, transformation, and validation is traced below. |
| `values` | `tuple[str, ...]`; required; positional or keyword | Input values used to build the result; transformations are shown below. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  86 | def _in_list(column: str, values: tuple[str, ...]) -> str:
  87 |     rendered = ", ".join(f"'{value}'" for value in values)
  88 |     return f"{column} IN ({rendered})"
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L86 | Define `_in_list`; bind its arguments when called. The body executes only when invoked. |
| L87 | Evaluate the right-hand side, then bind/store it in `rendered`: `', '.join((f"'{value}'" for value in values))` — Join the supplied string items using `', '` between adjacent items; inputs include iterate `values`, binding each item to `value`; produce `f"'{value}'"` into a lazy generator (items computed when consumed). |
| L88 | Compute the return value: format a string by inserting `column`, `rendered` into the literal text; !r uses repr, and this formatting does not escape or redact values. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
