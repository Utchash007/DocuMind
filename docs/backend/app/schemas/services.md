# `app/schemas/services.py`

[Source](../../../../Backend/app/schemas/services.py) · [Backend index](../../README.md)

Internal structural interfaces shared across API, repositories, providers, and workers. `Session` and ORM types are imported only under `TYPE_CHECKING`; postponed annotations avoid runtime imports.

## Payloads

| Model | Fields |
| --- | --- |
| `StorageFileInfo` | `file_id`, `bucket_id`, `size`, `mime_type`, counters `chunks_uploaded=0`/`chunks_total=0`, `completed=False`; no checksum field |
| `AuthorizedSource` | UUID `document_id`, UUID `index_version`, display `file_name`; the IDs authorize an exact pair |
| `HistoryTurn` | `role`, `content`, `position` |
| `GeneratedAnswer` | `answer` and `list[Citation]` |
| `PdfChunk` | `chunk_id`, text, one-based `page_number`, source label; a normal Pydantic model, not configured frozen |
| `JobClaim` | Job ID/kind, target document/epoch, nullable index version, fencing lease token and expiry |

## Protocol methods

Every method below takes `self` as the implementing adapter. Their bodies here are declarations (`...`), with no provider/database work; the return types describe the **implementation contract**. Calling a declaration itself simply falls through to `None`. Concrete behavior is documented in the linked modules. Protocol conformance is structural; adapters need not inherit these classes.

### `PrincipalResolver.resolve_principal(self, authorization_header: str) -> Any`

Accepts the full Bearer authorization header. Contract: verify with Appwrite, bootstrap the internal account, and return `AuthenticatedUser`, or raise an auth/service HTTP error. Implementation: [auth/principal.md](../auth/principal.md).

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-principalresolver-resolve-principal"></a>

#### Line-by-line execution

[Current source: lines 109–115](../../../../Backend/app/schemas/services.py#L109-L115). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `authorization_header` | `str`; required; positional or keyword | Authorization header to parse and verify through Appwrite. |

**Declared result:** `Any`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 109 |     def resolve_principal(self, authorization_header: str) -> Any:
 110 |         """Return ``AuthenticatedUser`` or raise the 401/503 auth error.
 111 | 
 112 |         Fails closed: provider verification outages raise a retryable
 113 |         service error, they never produce an anonymous principal.
 114 |         """
 115 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L109 | Define `PrincipalResolver.resolve_principal`; bind its arguments when called. The body executes only when invoked. |
| L110 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L112 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L113 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L114 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L115 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `OwnedResourceLookups.get_owned_project(self, session, *, user_id, project_id, include_deleted=False) -> Project | None`

Accepts a session, internal owner UUID, project UUID, and cleanup-only tombstone flag. Contract: filter by ID/owner and normally exclude deleted projects, returning the ORM row or `None`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-ownedresourcelookups-get-owned-project"></a>

#### Line-by-line execution

[Current source: lines 121–124](../../../../Backend/app/schemas/services.py#L121-L124). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `include_deleted` | `bool`; default `False`; keyword-only | Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |

**Declared result:** `Project | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 121 |     def get_owned_project(
 122 |         self, session: Session, *, user_id: UUID, project_id: UUID, include_deleted: bool = False
 123 |     ) -> Project | None:
 124 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L121 | Define `OwnedResourceLookups.get_owned_project`; bind its arguments when called. The body executes only when invoked. |
| L122 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. Declare parameter `include_deleted` with annotation `bool`. Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |
| L123 | Finish/continue the signature; the declared return annotation is `Project \| None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L124 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `OwnedResourceLookups.get_owned_document(self, session, *, user_id, project_id, document_id, include_deleted=False) -> Document | None`

Accepts the same scope plus document UUID. Contract: join through the owned project and hide project/document tombstones by default; return the row or `None`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-ownedresourcelookups-get-owned-document"></a>

#### Line-by-line execution

[Current source: lines 126–135](../../../../Backend/app/schemas/services.py#L126-L135). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID`; required; keyword-only | Document UUID; filenames do not establish document identity. |
| `include_deleted` | `bool`; default `False`; keyword-only | Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |

**Declared result:** `Document | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 126 |     def get_owned_document(
 127 |         self,
 128 |         session: Session,
 129 |         *,
 130 |         user_id: UUID,
 131 |         project_id: UUID,
 132 |         document_id: UUID,
 133 |         include_deleted: bool = False,
 134 |     ) -> Document | None:
 135 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L126 | Define `OwnedResourceLookups.get_owned_document`; bind its arguments when called. The body executes only when invoked. |
| L127 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L128 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L129 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L130 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L131 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L132 | Declare parameter `document_id` with annotation `UUID`. Document UUID; filenames do not establish document identity. |
| L133 | Declare parameter `include_deleted` with annotation `bool`. Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |
| L134 | Finish/continue the signature; the declared return annotation is `Document \| None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L135 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `OwnedResourceLookups.get_owned_conversation(self, session, *, user_id, project_id, conversation_id, include_deleted=False) -> Conversation | None`

Accepts owner/project/conversation UUIDs and the deletion flag. Contract: verify project ownership and liveness and return the conversation or `None`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-ownedresourcelookups-get-owned-conversation"></a>

#### Line-by-line execution

[Current source: lines 137–146](../../../../Backend/app/schemas/services.py#L137-L146). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |
| `include_deleted` | `bool`; default `False`; keyword-only | Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |

**Declared result:** `Conversation | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 137 |     def get_owned_conversation(
 138 |         self,
 139 |         session: Session,
 140 |         *,
 141 |         user_id: UUID,
 142 |         project_id: UUID,
 143 |         conversation_id: UUID,
 144 |         include_deleted: bool = False,
 145 |     ) -> Conversation | None:
 146 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L137 | Define `OwnedResourceLookups.get_owned_conversation`; bind its arguments when called. The body executes only when invoked. |
| L138 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L139 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L140 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L141 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L142 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L143 | Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L144 | Declare parameter `include_deleted` with annotation `bool`. Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |
| L145 | Finish/continue the signature; the declared return annotation is `Conversation \| None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L146 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `OwnedResourceLookups.get_owned_job(self, session, *, user_id, job_id) -> ProcessingJob | None`

Accepts a session, owner UUID, and job UUID. Contract: match the job's owner snapshot, even after resource deletion, returning the row or `None`. All four concrete lookup algorithms are in [db/queries.md](../db/queries.md); they do not commit.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-ownedresourcelookups-get-owned-job"></a>

#### Line-by-line execution

[Current source: lines 148–149](../../../../Backend/app/schemas/services.py#L148-L149). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |

**Declared result:** `ProcessingJob | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 148 |     def get_owned_job(self, session: Session, *, user_id: UUID, job_id: UUID) -> ProcessingJob | None:
 149 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L148 | Define `OwnedResourceLookups.get_owned_job`; bind its arguments when called. The body executes only when invoked. |
| L149 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `StorageAdapter.create_storage_file(self, *, bucket_id: str, file_id: str, data: bytes, mime_type: str) -> StorageFileInfo`

Accepts the private bucket, pre-reserved file ID, file bytes, and MIME type. Contract: upload outside any SQL transaction with private access and return completion metadata. The concrete Appwrite adapter additionally accepts an optional owner Appwrite ID.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-storageadapter-create-storage-file"></a>

#### Line-by-line execution

[Current source: lines 155–159](../../../../Backend/app/schemas/services.py#L155-L159). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |
| `data` | `bytes`; required; keyword-only | File bytes or input payload consumed by this operation, as specified by the annotation. |
| `mime_type` | `str`; required; keyword-only | Declared storage content type; accepted application uploads use application/pdf. |

**Declared result:** `StorageFileInfo`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 155 |     def create_storage_file(
 156 |         self, *, bucket_id: str, file_id: str, data: bytes, mime_type: str
 157 |     ) -> StorageFileInfo:
 158 |         """Upload with a pre-reserved file ID and owner-only access."""
 159 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L155 | Define `StorageAdapter.create_storage_file`; bind its arguments when called. The body executes only when invoked. |
| L156 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `bucket_id` with annotation `str`. Appwrite bucket identifier. Declare parameter `file_id` with annotation `str`. Reserved Appwrite storage-object identifier. Declare parameter `data` with annotation `bytes`. File bytes or input payload consumed by this operation, as specified by the annotation. Declare parameter `mime_type` with annotation `str`. Declared storage content type; accepted application uploads use application/pdf. |
| L157 | Finish/continue the signature; the declared return annotation is `StorageFileInfo`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L158 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L159 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `StorageAdapter.inspect_storage_file(self, *, bucket_id: str, file_id: str) -> StorageFileInfo`

Accepts storage identifiers. Contract: fetch size/MIME/chunk completion metadata, without downloading or calculating a content hash.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-storageadapter-inspect-storage-file"></a>

#### Line-by-line execution

[Current source: lines 161–163](../../../../Backend/app/schemas/services.py#L161-L163). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |

**Declared result:** `StorageFileInfo`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 161 |     def inspect_storage_file(self, *, bucket_id: str, file_id: str) -> StorageFileInfo:
 162 |         """Return size/fingerprint/chunk completion for reconciliation."""
 163 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L161 | Define `StorageAdapter.inspect_storage_file`; bind its arguments when called. The body executes only when invoked. |
| L162 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L163 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `StorageAdapter.open_storage_range(self, *, bucket_id: str, file_id: str, range_header: str | None) -> tuple[bytes, dict[str, str]]`

Accepts storage identifiers and optional HTTP Range. Contract: return selected PDF bytes and content/range headers or raise a storage/range error.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-storageadapter-open-storage-range"></a>

#### Line-by-line execution

[Current source: lines 165–169](../../../../Backend/app/schemas/services.py#L165-L169). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |
| `range_header` | `str \| None`; required; keyword-only | Optional HTTP byte-range selector; parsing determines full, partial, or unsatisfiable behavior. |

**Declared result:** `tuple[bytes, dict[str, str]]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 165 |     def open_storage_range(
 166 |         self, *, bucket_id: str, file_id: str, range_header: str | None
 167 |     ) -> tuple[bytes, dict[str, str]]:
 168 |         """Return (chunk bytes, response headers) for inline PDF serving."""
 169 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L165 | Define `StorageAdapter.open_storage_range`; bind its arguments when called. The body executes only when invoked. |
| L166 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `bucket_id` with annotation `str`. Appwrite bucket identifier. Declare parameter `file_id` with annotation `str`. Reserved Appwrite storage-object identifier. Declare parameter `range_header` with annotation `str \| None`. Optional HTTP byte-range selector; parsing determines full, partial, or unsatisfiable behavior. |
| L167 | Finish/continue the signature; the declared return annotation is `tuple[bytes, dict[str, str]]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L168 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L169 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `StorageAdapter.delete_storage_file(self, *, bucket_id: str, file_id: str) -> None`

Accepts storage identifiers. Contract: delete idempotently (missing counts as success). All storage methods are implemented in [services/storage.md](../services/storage.md).

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-storageadapter-delete-storage-file"></a>

#### Line-by-line execution

[Current source: lines 171–173](../../../../Backend/app/schemas/services.py#L171-L173). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 171 |     def delete_storage_file(self, *, bucket_id: str, file_id: str) -> None:
 172 |         """Idempotent delete: already-missing files count as deleted."""
 173 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L171 | Define `StorageAdapter.delete_storage_file`; bind its arguments when called. The body executes only when invoked. |
| L172 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L173 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `JobQueue.enqueue_job(self, session, *, owner_user_id, project_id, target_document_id, document_id, kind, target_epoch, resource_snapshot, available_at=None, max_attempts=3) -> ProcessingJob`

Accepts a caller-owned session; immutable owner/project/target UUIDs; optional live document FK; `JobKind`; expected epoch; JSON cleanup/input snapshot; optional due time and attempt cap. Contract: insert or return the existing nonterminal target/kind winner within that transaction, without committing.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueue-enqueue-job"></a>

#### Line-by-line execution

[Current source: lines 179–195](../../../../Backend/app/schemas/services.py#L179-L195). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `owner_user_id` | `UUID`; required; keyword-only | Internal owner UUID copied into the job's durable ownership snapshot. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `target_document_id` | `UUID`; required; keyword-only | Immutable target UUID retained even when the live document relationship disappears. |
| `document_id` | `UUID \| None`; required; keyword-only | Document UUID; filenames do not establish document identity. |
| `kind` | `JobKind`; required; keyword-only | Caller-supplied kind; each read, transformation, and validation is traced below. |
| `target_epoch` | `int`; required; keyword-only | Expected document processing epoch used to invalidate obsolete attempts. |
| `resource_snapshot` | `dict[str, Any]`; required; keyword-only | JSON-compatible resource facts copied into a durable job. |
| `available_at` | `datetime \| None`; default `None`; keyword-only | Earliest time a queued/retry-wait job may be claimed. |
| `max_attempts` | `int`; default `3`; keyword-only | Maximum number of claims before retryable failures become terminal. |

**Declared result:** `ProcessingJob`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 179 |     def enqueue_job(
 180 |         self,
 181 |         session: Session,
 182 |         *,
 183 |         owner_user_id: UUID,
 184 |         project_id: UUID,
 185 |         target_document_id: UUID,
 186 |         document_id: UUID | None,
 187 |         kind: JobKind,
 188 |         target_epoch: int,
 189 |         resource_snapshot: dict[str, Any],
 190 |         available_at: datetime | None = None,
 191 |         max_attempts: int = 3,
 192 |     ) -> ProcessingJob:
 193 |         """Insert the job in the caller's transaction (idempotent per
 194 |         the partial unique nonterminal (target, kind) index)."""
 195 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L179 | Define `JobQueue.enqueue_job`; bind its arguments when called. The body executes only when invoked. |
| L180 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L181 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L182 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L183 | Declare parameter `owner_user_id` with annotation `UUID`. Internal owner UUID copied into the job's durable ownership snapshot. |
| L184 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L185 | Declare parameter `target_document_id` with annotation `UUID`. Immutable target UUID retained even when the live document relationship disappears. |
| L186 | Declare parameter `document_id` with annotation `UUID \| None`. Document UUID; filenames do not establish document identity. |
| L187 | Declare parameter `kind` with annotation `JobKind`. Caller-supplied kind; its uses and transformations are traced below. |
| L188 | Declare parameter `target_epoch` with annotation `int`. Expected document processing epoch used to invalidate obsolete attempts. |
| L189 | Declare parameter `resource_snapshot` with annotation `dict[str, Any]`. JSON-compatible resource facts copied into a durable job. |
| L190 | Declare parameter `available_at` with annotation `datetime \| None`. Earliest time a queued/retry-wait job may be claimed. |
| L191 | Declare parameter `max_attempts` with annotation `int`. Maximum number of claims before retryable failures become terminal. |
| L192 | Finish/continue the signature; the declared return annotation is `ProcessingJob`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L193 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L194 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L195 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `JobQueue.claim_next_jobs(self, session, *, worker_id: str, limit: int, lease_seconds: int) -> list[JobClaim]`

Accepts caller session, worker identity, claim-batch cap, and lease duration. Contract: lock due jobs with `SKIP LOCKED`, increment attempt/fencing tokens, assign namespaces, and return claims.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueue-claim-next-jobs"></a>

#### Line-by-line execution

[Current source: lines 197–202](../../../../Backend/app/schemas/services.py#L197-L202). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `limit` | `int`; required; keyword-only | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |
| `lease_seconds` | `int`; required; keyword-only | Lease duration in seconds; positive-duration validation is not implicit in this parameter. |

**Declared result:** `list[JobClaim]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 197 |     def claim_next_jobs(
 198 |         self, session: Session, *, worker_id: str, limit: int, lease_seconds: int
 199 |     ) -> list[JobClaim]:
 200 |         """``FOR UPDATE SKIP LOCKED`` claim of due jobs; bumps the fencing
 201 |         token and attempt count before releasing the lock."""
 202 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L197 | Define `JobQueue.claim_next_jobs`; bind its arguments when called. The body executes only when invoked. |
| L198 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. Declare parameter `limit` with annotation `int`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. Declare parameter `lease_seconds` with annotation `int`. Lease duration in seconds; positive-duration validation is not implicit in this parameter. |
| L199 | Finish/continue the signature; the declared return annotation is `list[JobClaim]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L200 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L201 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L202 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `JobQueue.renew_job_lease(self, session, *, job_id, lease_token: int, worker_id: str, lease_seconds: int) -> bool`

Accepts job UUID and exact claim identity plus renewal duration. Contract: extend only a matching unexpired running lease; return `False` for stale work.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueue-renew-job-lease"></a>

#### Line-by-line execution

[Current source: lines 204–208](../../../../Backend/app/schemas/services.py#L204-L208). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `lease_token` | `int`; required; keyword-only | Monotonic claim token used to reject stale worker writes. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `lease_seconds` | `int`; required; keyword-only | Lease duration in seconds; positive-duration validation is not implicit in this parameter. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 204 |     def renew_job_lease(
 205 |         self, session: Session, *, job_id: UUID, lease_token: int, worker_id: str, lease_seconds: int
 206 |     ) -> bool:
 207 |         """Compare-and-set heartbeat; False when the claim is no longer ours."""
 208 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L204 | Define `JobQueue.renew_job_lease`; bind its arguments when called. The body executes only when invoked. |
| L205 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. Declare parameter `lease_token` with annotation `int`. Monotonic claim token used to reject stale worker writes. Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. Declare parameter `lease_seconds` with annotation `int`. Lease duration in seconds; positive-duration validation is not implicit in this parameter. |
| L206 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L207 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L208 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `JobQueue.complete_job(self, session, *, job_id, lease_token: int, worker_id: str) -> bool`

Accepts the claim identity. Contract: verify lease/epoch/resource liveness and publish success transactionally; return whether publication/idempotent completion succeeded.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueue-complete-job"></a>

#### Line-by-line execution

[Current source: lines 210–215](../../../../Backend/app/schemas/services.py#L210-L215). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `lease_token` | `int`; required; keyword-only | Monotonic claim token used to reject stale worker writes. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 210 |     def complete_job(
 211 |         self, session: Session, *, job_id: UUID, lease_token: int, worker_id: str
 212 |     ) -> bool:
 213 |         """Publish success (with the document pointer, if applicable) in
 214 |         the caller's transaction after fencing checks. False = stale."""
 215 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L210 | Define `JobQueue.complete_job`; bind its arguments when called. The body executes only when invoked. |
| L211 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. Declare parameter `lease_token` with annotation `int`. Monotonic claim token used to reject stale worker writes. Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. |
| L212 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L213 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L214 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L215 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `JobQueue.fail_job(self, session, *, job_id, lease_token: int, worker_id: str, error_code: str, error_message: str, retryable: bool) -> bool`

Accepts the claim identity, safe diagnostic, and retry decision. Contract: fenced transition to delayed retry or terminal failure; return `False` for an obsolete claim.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueue-fail-job"></a>

#### Line-by-line execution

[Current source: lines 217–229](../../../../Backend/app/schemas/services.py#L217-L229). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `lease_token` | `int`; required; keyword-only | Monotonic claim token used to reject stale worker writes. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `error_code` | `str`; required; keyword-only | Machine-readable failure category stored or exposed by the operation. |
| `error_message` | `str`; required; keyword-only | Human-readable failure detail; truncation alone does not redact sensitive content. |
| `retryable` | `bool`; required; keyword-only | Whether the failure may be retried while the attempt budget remains. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 217 |     def fail_job(
 218 |         self,
 219 |         session: Session,
 220 |         *,
 221 |         job_id: UUID,
 222 |         lease_token: int,
 223 |         worker_id: str,
 224 |         error_code: str,
 225 |         error_message: str,
 226 |         retryable: bool,
 227 |     ) -> bool:
 228 |         """Move to ``retry_wait`` (bounded backoff) or terminal ``failed``."""
 229 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L217 | Define `JobQueue.fail_job`; bind its arguments when called. The body executes only when invoked. |
| L218 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L219 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L220 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L221 | Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. |
| L222 | Declare parameter `lease_token` with annotation `int`. Monotonic claim token used to reject stale worker writes. |
| L223 | Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. |
| L224 | Declare parameter `error_code` with annotation `str`. Machine-readable failure category stored or exposed by the operation. |
| L225 | Declare parameter `error_message` with annotation `str`. Human-readable failure detail; truncation alone does not redact sensitive content. |
| L226 | Declare parameter `retryable` with annotation `bool`. Whether the failure may be retried while the attempt budget remains. |
| L227 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L228 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L229 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `JobQueue.cancel_job(self, session, *, job_id, reason: str) -> bool`

Accepts a job UUID and safe cancellation reason. Contract: revoke nonterminal work and its token; return whether a job changed. Queue implementations and transaction boundaries are in [jobs/queue.md](../jobs/queue.md).

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueue-cancel-job"></a>

#### Line-by-line execution

[Current source: lines 231–233](../../../../Backend/app/schemas/services.py#L231-L233). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `reason` | `str`; required; keyword-only | Human-readable cancellation/decision reason recorded or returned by this operation. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 231 |     def cancel_job(self, session: Session, *, job_id: UUID, reason: str) -> bool:
 232 |         """Cancel a nonterminal job (deletion/retry invalidation)."""
 233 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L231 | Define `JobQueue.cancel_job`; bind its arguments when called. The body executes only when invoked. |
| L232 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L233 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `PdfPipeline.extract_pdf_chunks(self, pdf_path: Path, *, file_name: str) -> list[PdfChunk]`

Accepts a local PDF path and display filename. Contract: completely extract text into page-bound chunks around 800 characters; reject invalid/textless input. [rag/pdf.md](../rag/pdf.md) describes the concrete function's extra identity/limit options.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-pdfpipeline-extract-pdf-chunks"></a>

#### Line-by-line execution

[Current source: lines 239–241](../../../../Backend/app/schemas/services.py#L239-L241). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `pdf_path` | `Path`; required; positional or keyword | Caller-supplied pdf path; each read, transformation, and validation is traced below. |
| `file_name` | `str`; required; keyword-only | Display PDF filename; immutable IDs establish ownership and evidence identity. |

**Declared result:** `list[PdfChunk]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 239 |     def extract_pdf_chunks(self, pdf_path: Path, *, file_name: str) -> list[PdfChunk]:
 240 |         """Page-bound chunks (~800 chars, one page per chunk, 1-based pages)."""
 241 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L239 | Define `PdfPipeline.extract_pdf_chunks`; bind its arguments when called. The body executes only when invoked. |
| L240 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L241 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `PdfPipeline.embed_texts(self, texts: Sequence[str]) -> list[list[float]]`

Accepts ordered texts. Contract: return one validated provider vector per text with explicit-only mock fallback. Implementation: [rag/embeddings.md](../rag/embeddings.md).

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-pdfpipeline-embed-texts"></a>

#### Line-by-line execution

[Current source: lines 243–245](../../../../Backend/app/schemas/services.py#L243-L245). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `texts` | `Sequence[str]`; required; positional or keyword | Input text sequence; embedding output preserves its order. |

**Declared result:** `list[list[float]]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 243 |     def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
 244 |         """Batch embeddings; production never silently uses mock vectors."""
 245 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L243 | Define `PdfPipeline.embed_texts`; bind its arguments when called. The body executes only when invoked. |
| L244 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L245 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `PdfPipeline.publish_index_version(self, *, user_id, project_id, document_id, index_version, chunks: Sequence[PdfChunk]) -> None`

Accepts four UUIDs and chunks. Contract: write a fresh versioned index namespace; database active-pointer publication remains a queue operation. The concrete `IndexService` also accepts supplied embeddings; see [rag/indexing.md](../rag/indexing.md).

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-pdfpipeline-publish-index-version"></a>

#### Line-by-line execution

[Current source: lines 247–251](../../../../Backend/app/schemas/services.py#L247-L251). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID`; required; keyword-only | Document UUID; filenames do not establish document identity. |
| `index_version` | `UUID`; required; keyword-only | UUID of one document's vector-index namespace, separate from its active publication pointer. |
| `chunks` | `Sequence[PdfChunk]`; required; keyword-only | PDF text chunks with the metadata required by this operation. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 247 |     def publish_index_version(
 248 |         self, *, user_id: UUID, project_id: UUID, document_id: UUID, index_version: UUID, chunks: Sequence[PdfChunk]
 249 |     ) -> None:
 250 |         """Write chunks into the fresh ``index_version`` namespace."""
 251 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L247 | Define `PdfPipeline.publish_index_version`; bind its arguments when called. The body executes only when invoked. |
| L248 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. Declare parameter `document_id` with annotation `UUID`. Document UUID; filenames do not establish document identity. Declare parameter `index_version` with annotation `UUID`. UUID of one document's vector-index namespace, separate from its active publication pointer. Declare parameter `chunks` with annotation `Sequence[PdfChunk]`. PDF text chunks with the metadata required by this operation. |
| L249 | Finish/continue the signature; the declared return annotation is `None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L250 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L251 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `PdfPipeline.delete_index_version(self, *, user_id, project_id, document_id, index_version) -> None`

Accepts the four namespace UUIDs. Contract: idempotently delete only that exact owned version through the index adapter.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-pdfpipeline-delete-index-version"></a>

#### Line-by-line execution

[Current source: lines 253–257](../../../../Backend/app/schemas/services.py#L253-L257). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID`; required; keyword-only | Document UUID; filenames do not establish document identity. |
| `index_version` | `UUID`; required; keyword-only | UUID of one document's vector-index namespace, separate from its active publication pointer. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 253 |     def delete_index_version(
 254 |         self, *, user_id: UUID, project_id: UUID, document_id: UUID, index_version: UUID
 255 |     ) -> None:
 256 |         """Idempotent delete of one index namespace (all versions on cleanup)."""
 257 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L253 | Define `PdfPipeline.delete_index_version`; bind its arguments when called. The body executes only when invoked. |
| L254 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. Declare parameter `document_id` with annotation `UUID`. Document UUID; filenames do not establish document identity. Declare parameter `index_version` with annotation `UUID`. UUID of one document's vector-index namespace, separate from its active publication pointer. |
| L255 | Finish/continue the signature; the declared return annotation is `None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L256 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L257 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `AnswerGenerator.generate_answer(self, *, question: str, history: Sequence[HistoryTurn], authorized_sources: Sequence[AuthorizedSource], user_id: UUID, project_id: UUID) -> GeneratedAnswer`

Accepts the current question, bounded prior context, exact authorized source pairs, and required owner/project scope. Contract: retrieve scoped evidence, generate a grounded answer, refine citations, and return the answer without writing messages. Implementation: [rag/generation.md](../rag/generation.md).

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-answergenerator-generate-answer"></a>

#### Line-by-line execution

[Current source: lines 263–273](../../../../Backend/app/schemas/services.py#L263-L273). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `question` | `str`; required; keyword-only | Current user question, separate from historical messages and PDF evidence. |
| `history` | `Sequence[HistoryTurn]`; required; keyword-only | Prior conversation turns used as context; they are not source evidence. |
| `authorized_sources` | `Sequence[AuthorizedSource]`; required; keyword-only | Exact authorized document/version pairs; these bound the evidence search. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |

**Declared result:** `GeneratedAnswer`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 263 |     def generate_answer(
 264 |         self, *, question: str, history: Sequence[HistoryTurn], authorized_sources: Sequence[AuthorizedSource],
 265 |         user_id: UUID, project_id: UUID
 266 |     ) -> GeneratedAnswer:
 267 |         """Return an answer and citations refined against retrieved chunks.
 268 | 
 269 |         Must not write conversation rows, must not treat earlier assistant
 270 |         output as source evidence, and must include the current question
 271 |         exactly once in the assembled prompt.
 272 |         """
 273 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L263 | Define `AnswerGenerator.generate_answer`; bind its arguments when called. The body executes only when invoked. |
| L264 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `question` with annotation `str`. Current user question, separate from historical messages and PDF evidence. Declare parameter `history` with annotation `Sequence[HistoryTurn]`. Prior conversation turns used as context; they are not source evidence. Declare parameter `authorized_sources` with annotation `Sequence[AuthorizedSource]`. Exact authorized document/version pairs; these bound the evidence search. |
| L265 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L266 | Finish/continue the signature; the declared return annotation is `GeneratedAnswer`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L267 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L269 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L270 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L271 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L272 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L273 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->
