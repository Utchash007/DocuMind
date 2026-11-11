# `app/repositories/projects.py`

[Source](../../../../Backend/app/repositories/projects.py) · [Backend index](../../README.md)

Shared HTTP error construction, owned-resource lookups, and project SQL mutations. All database helpers use the supplied session; writes flush but do not commit. Owner inputs are internal UUIDs resolved from authentication.

## Functions

### `raise_api_error(status_code, code, message, *, project_id=None, document_id=None, job_id=None, message_id=None, conversation_id=None) -> None`

**Arguments:** HTTP integer status, `ErrorCode`, safe message, and optional UUID resource context. **Returns:** Never normally. **Work:** Builds `ApiError`, serializes camelCase fields in JSON mode (UUIDs become strings), then raises `HTTPException` with that object as `detail`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-raise-api-error"></a>

#### Line-by-line execution

[Current source: lines 75–96](../../../../Backend/app/repositories/projects.py#L75-L96). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `status_code` | `int`; required; positional or keyword | Caller-supplied status code; each read, transformation, and validation is traced below. |
| `code` | `ErrorCode`; required; positional or keyword | Caller-supplied code; each read, transformation, and validation is traced below. |
| `message` | `str`; required; positional or keyword | Caller-supplied message; each read, transformation, and validation is traced below. |
| `project_id` | `UUID \| None`; default `None`; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID \| None`; default `None`; keyword-only | Document UUID; filenames do not establish document identity. |
| `job_id` | `UUID \| None`; default `None`; keyword-only | Durable processing-job UUID. |
| `message_id` | `UUID \| None`; default `None`; keyword-only | Persisted message UUID identifying the turn being read, retried, or cancelled. |
| `conversation_id` | `UUID \| None`; default `None`; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  75 | def raise_api_error(
  76 |     status_code: int,
  77 |     code: ErrorCode,
  78 |     message: str,
  79 |     *,
  80 |     project_id: UUID | None = None,
  81 |     document_id: UUID | None = None,
  82 |     job_id: UUID | None = None,
  83 |     message_id: UUID | None = None,
  84 |     conversation_id: UUID | None = None,
  85 | ) -> None:
  86 |     """Raise an HTTP error with ``{"detail": ApiError}`` (camelCase IDs)."""
  87 |     detail = ApiError(
  88 |         code=code,
  89 |         message=message,
  90 |         project_id=project_id,
  91 |         document_id=document_id,
  92 |         job_id=job_id,
  93 |         message_id=message_id,
  94 |         conversation_id=conversation_id,
  95 |     ).model_dump(by_alias=True, mode="json")
  96 |     raise HTTPException(status_code=status_code, detail=detail)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L75 | Define `raise_api_error`; bind its arguments when called. The body executes only when invoked. |
| L76 | Declare parameter `status_code` with annotation `int`. Caller-supplied status code; its uses and transformations are traced below. |
| L77 | Declare parameter `code` with annotation `ErrorCode`. Caller-supplied code; its uses and transformations are traced below. |
| L78 | Declare parameter `message` with annotation `str`. Caller-supplied message; its uses and transformations are traced below. |
| L79 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L80 | Declare parameter `project_id` with annotation `UUID \| None`. Project UUID used to constrain resource lookup or provider metadata. |
| L81 | Declare parameter `document_id` with annotation `UUID \| None`. Document UUID; filenames do not establish document identity. |
| L82 | Declare parameter `job_id` with annotation `UUID \| None`. Durable processing-job UUID. |
| L83 | Declare parameter `message_id` with annotation `UUID \| None`. Persisted message UUID identifying the turn being read, retried, or cancelled. |
| L84 | Declare parameter `conversation_id` with annotation `UUID \| None`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L85 | Finish/continue the signature; the declared return annotation is `None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L86 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L87 | Evaluate the right-hand side, then bind/store it in `detail`: `ApiError(code=code, message=message, project_id=project_id, document_id=document_id, job_id=job_id, message_id=message_id, conversation_id=conversation_id).model_dump` with the arguments detailed below — Serialize Pydantic fields into a dictionary; by_alias=True uses wire names and mode='json' converts JSON-compatible values; first obtain the receiver: `ApiError(code=code, message=message, project_id=project_id, document_id=document_id, job_id=job_id, message_id=message_id, conversation_id=conversation_id)` — Construct `ApiError` with the supplied diagnostic fields; the surrounding raise determines propagation. |
| L88 | Supply `code` = `code`.  Evaluate the value as: the current `code` value. |
| L89 | Supply `message` = `message`.  Evaluate the value as: the current `message` value. |
| L90 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L91 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L92 | Supply `job_id` = `job_id`. Durable processing-job UUID. Evaluate the value as: the current `job_id` value. |
| L93 | Supply `message_id` = `message_id`. Persisted message UUID identifying the turn being read, retried, or cancelled. Evaluate the value as: the current `message_id` value. |
| L94 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L95 | Supply `by_alias` = `True`.  Evaluate the value as: `True`. Supply `mode` = `'json'`.  Evaluate the value as: `'json'`. |
| L96 | Raise `HTTPException(status_code=status_code, detail=detail)`; stop the normal path and transfer control to the nearest matching exception handler. |

<!-- END LINE WALKTHROUGH -->

### `_utcnow() -> datetime`

**Arguments:** None. **Returns:** Current aware UTC time. **Work:** Calls `datetime.now(timezone.utc)` for tombstone timestamps.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--utcnow"></a>

#### Line-by-line execution

[Current source: lines 99–100](../../../../Backend/app/repositories/projects.py#L99-L100). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `datetime`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  99 | def _utcnow() -> datetime:
 100 |     return datetime.now(timezone.utc)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L99 | Define `_utcnow`; bind its arguments when called. The body executes only when invoked. |
| L100 | Compute the return value: `datetime.now(timezone.utc)` — Read the current wall-clock date/time in the supplied timezone. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `project_to_dto(project: Project) -> ProjectDto`

**Arguments:** ORM project. **Returns:** Public Pydantic project DTO. **Work:** Uses `model_validate` with attribute loading; owner identity is excluded by the DTO schema.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-project-to-dto"></a>

#### Line-by-line execution

[Current source: lines 103–105](../../../../Backend/app/repositories/projects.py#L103-L105). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project` | `Project`; required; positional or keyword | Caller-supplied project; each read, transformation, and validation is traced below. |

**Declared result:** `ProjectDto`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 103 | def project_to_dto(project: Project) -> ProjectDto:
 104 |     """Convert an ORM project to its public DTO (never exposes owner IDs)."""
 105 |     return ProjectDto.model_validate(project)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L103 | Define `project_to_dto`; bind its arguments when called. The body executes only when invoked. |
| L104 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L105 | Compute the return value: `ProjectDto.model_validate(project)` — Validate/coerce the input into this Pydantic model, including configured field validators. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `get_owned_project_or_404(session, *, user_id, project_id, include_deleted=False) -> Project`

**Arguments:** Session, owner/project UUIDs, internal tombstone flag. **Returns:** Owned ORM project. **Work:** Calls the corresponding [db lookup](../db/queries.md); if missing/inaccessible, raises structured 404 with project context.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-owned-project-or-404"></a>

#### Line-by-line execution

[Current source: lines 113–133](../../../../Backend/app/repositories/projects.py#L113-L133). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `include_deleted` | `bool`; default `False`; keyword-only | Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |

**Declared result:** `Project`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 113 | def get_owned_project_or_404(
 114 |     session: Session,
 115 |     *,
 116 |     user_id: UUID,
 117 |     project_id: UUID,
 118 |     include_deleted: bool = False,
 119 | ) -> Project:
 120 |     project = _query_owned_project(
 121 |         session,
 122 |         user_id=user_id,
 123 |         project_id=project_id,
 124 |         include_deleted=include_deleted,
 125 |     )
 126 |     if project is None:
 127 |         raise_api_error(
 128 |             404,
 129 |             ErrorCode.NOT_FOUND,
 130 |             "Project not found.",
 131 |             project_id=project_id,
 132 |         )
 133 |     return project
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L113 | Define `get_owned_project_or_404`; bind its arguments when called. The body executes only when invoked. |
| L114 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L115 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L116 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L117 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L118 | Declare parameter `include_deleted` with annotation `bool`. Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |
| L119 | Finish/continue the signature; the declared return annotation is `Project`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L120 | Evaluate the right-hand side, then bind/store it in `project`: `_query_owned_project(session, user_id=user_id, project_id=project_id, include_deleted=include_deleted)` — Call [_query_owned_project](../db/queries.md#walk-get-owned-project) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L121 | Supply positional argument 1 to `_query_owned_project`: the current `session` value. |
| L122 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L123 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L124 | Supply `include_deleted` = `include_deleted`. Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. Evaluate the value as: the current `include_deleted` value. |
| L125 | Close the expression/container begun at L120; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L126 | Evaluate the branch condition: compare whether `project` is the same object as `None`. If truthy, enter L127; otherwise skip this indented block and continue after it. |
| L127 | `raise_api_error(404, ErrorCode.NOT_FOUND, 'Project not found.', project_id=project_id)` — Call [raise_api_error](#walk-raise-api-error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L128 | Supply positional argument 1 to `raise_api_error`: `404`. |
| L129 | Supply positional argument 2 to `raise_api_error`: the `NOT_FOUND` attribute of `ErrorCode`. |
| L130 | Supply positional argument 3 to `raise_api_error`: `'Project not found.'`. |
| L131 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L132 | Close the expression/container begun at L127; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L133 | Compute the return value: the current `project` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `get_owned_document_or_404(session, *, user_id, project_id, document_id, include_deleted=False) -> Document`

**Arguments:** Session, owner/project/document UUIDs, optional tombstone flag. **Returns:** Owned ORM document. **Work:** Delegates the joined ownership/liveness lookup; `None` becomes 404 with project/document IDs.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-owned-document-or-404"></a>

#### Line-by-line execution

[Current source: lines 136–159](../../../../Backend/app/repositories/projects.py#L136-L159). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID`; required; keyword-only | Document UUID; filenames do not establish document identity. |
| `include_deleted` | `bool`; default `False`; keyword-only | Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |

**Declared result:** `Document`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 136 | def get_owned_document_or_404(
 137 |     session: Session,
 138 |     *,
 139 |     user_id: UUID,
 140 |     project_id: UUID,
 141 |     document_id: UUID,
 142 |     include_deleted: bool = False,
 143 | ) -> Document:
 144 |     document = _query_owned_document(
 145 |         session,
 146 |         user_id=user_id,
 147 |         project_id=project_id,
 148 |         document_id=document_id,
 149 |         include_deleted=include_deleted,
 150 |     )
 151 |     if document is None:
 152 |         raise_api_error(
 153 |             404,
 154 |             ErrorCode.NOT_FOUND,
 155 |             "Document not found.",
 156 |             project_id=project_id,
 157 |             document_id=document_id,
 158 |         )
 159 |     return document
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L136 | Define `get_owned_document_or_404`; bind its arguments when called. The body executes only when invoked. |
| L137 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L138 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L139 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L140 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L141 | Declare parameter `document_id` with annotation `UUID`. Document UUID; filenames do not establish document identity. |
| L142 | Declare parameter `include_deleted` with annotation `bool`. Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |
| L143 | Finish/continue the signature; the declared return annotation is `Document`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L144 | Evaluate the right-hand side, then bind/store it in `document`: `_query_owned_document(session, user_id=user_id, project_id=project_id, document_id=document_id, include_deleted=include_deleted)` — Call [_query_owned_document](../db/queries.md#walk-get-owned-document) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L145 | Supply positional argument 1 to `_query_owned_document`: the current `session` value. |
| L146 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L147 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L148 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L149 | Supply `include_deleted` = `include_deleted`. Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. Evaluate the value as: the current `include_deleted` value. |
| L150 | Close the expression/container begun at L144; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L151 | Evaluate the branch condition: compare whether `document` is the same object as `None`. If truthy, enter L152; otherwise skip this indented block and continue after it. |
| L152 | `raise_api_error(404, ErrorCode.NOT_FOUND, 'Document not found.', project_id=project_id, document_id=document_id)` — Call [raise_api_error](#walk-raise-api-error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L153 | Supply positional argument 1 to `raise_api_error`: `404`. |
| L154 | Supply positional argument 2 to `raise_api_error`: the `NOT_FOUND` attribute of `ErrorCode`. |
| L155 | Supply positional argument 3 to `raise_api_error`: `'Document not found.'`. |
| L156 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L157 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L158 | Close the expression/container begun at L152; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L159 | Compute the return value: the current `document` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `get_owned_conversation_or_404(session, *, user_id, project_id, conversation_id, include_deleted=False) -> Conversation`

**Arguments:** Session, owner/project/conversation UUIDs, optional deleted-project visibility. **Returns:** Owned conversation. **Work:** Delegates the project join and raises 404 with scope IDs on a miss.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-owned-conversation-or-404"></a>

#### Line-by-line execution

[Current source: lines 162–186](../../../../Backend/app/repositories/projects.py#L162-L186). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |
| `include_deleted` | `bool`; default `False`; keyword-only | Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |

**Declared result:** `Conversation`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 162 | def get_owned_conversation_or_404(
 163 |     session: Session,
 164 |     *,
 165 |     user_id: UUID,
 166 |     project_id: UUID,
 167 |     conversation_id: UUID,
 168 |     include_deleted: bool = False,
 169 | ) -> Conversation:
 170 |     """Conversation -> project -> user lookup for A5 handlers."""
 171 |     conversation = _query_owned_conversation(
 172 |         session,
 173 |         user_id=user_id,
 174 |         project_id=project_id,
 175 |         conversation_id=conversation_id,
 176 |         include_deleted=include_deleted,
 177 |     )
 178 |     if conversation is None:
 179 |         raise_api_error(
 180 |             404,
 181 |             ErrorCode.NOT_FOUND,
 182 |             "Conversation not found.",
 183 |             project_id=project_id,
 184 |             conversation_id=conversation_id,
 185 |         )
 186 |     return conversation
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L162 | Define `get_owned_conversation_or_404`; bind its arguments when called. The body executes only when invoked. |
| L163 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L164 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L165 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L166 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L167 | Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L168 | Declare parameter `include_deleted` with annotation `bool`. Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |
| L169 | Finish/continue the signature; the declared return annotation is `Conversation`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L170 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L171 | Evaluate the right-hand side, then bind/store it in `conversation`: `_query_owned_conversation(session, user_id=user_id, project_id=project_id, conversation_id=conversation_id, include_deleted=include_deleted)` — Call [_query_owned_conversation](../db/queries.md#walk-get-owned-conversation) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L172 | Supply positional argument 1 to `_query_owned_conversation`: the current `session` value. |
| L173 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L174 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L175 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L176 | Supply `include_deleted` = `include_deleted`. Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. Evaluate the value as: the current `include_deleted` value. |
| L177 | Close the expression/container begun at L171; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L178 | Evaluate the branch condition: compare whether `conversation` is the same object as `None`. If truthy, enter L179; otherwise skip this indented block and continue after it. |
| L179 | `raise_api_error(404, ErrorCode.NOT_FOUND, 'Conversation not found.', project_id=project_id, conversation_id=conversation_id)` — Call [raise_api_error](#walk-raise-api-error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L180 | Supply positional argument 1 to `raise_api_error`: `404`. |
| L181 | Supply positional argument 2 to `raise_api_error`: the `NOT_FOUND` attribute of `ErrorCode`. |
| L182 | Supply positional argument 3 to `raise_api_error`: `'Conversation not found.'`. |
| L183 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L184 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L185 | Close the expression/container begun at L179; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L186 | Compute the return value: the current `conversation` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `get_owned_job_or_404(session, *, user_id, job_id) -> ProcessingJob`

**Arguments:** Session, owner UUID, job UUID. **Returns:** The owner's job. **Work:** Queries its immutable owner snapshot; raises 404 on a miss. Does not hide jobs whose original resources were deleted.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-owned-job-or-404"></a>

#### Line-by-line execution

[Current source: lines 189–208](../../../../Backend/app/repositories/projects.py#L189-L208). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |

**Declared result:** `ProcessingJob`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 189 | def get_owned_job_or_404(
 190 |     session: Session,
 191 |     *,
 192 |     user_id: UUID,
 193 |     job_id: UUID,
 194 | ) -> ProcessingJob:
 195 |     """Return the job iff its snapshot ``owner_user_id`` matches.
 196 | 
 197 |     No tombstone filter: cleanup jobs stay pollable after their
 198 |     document/project rows are deleted.
 199 |     """
 200 |     job = _query_owned_job(session, user_id=user_id, job_id=job_id)
 201 |     if job is None:
 202 |         raise_api_error(
 203 |             404,
 204 |             ErrorCode.NOT_FOUND,
 205 |             "Job not found.",
 206 |             job_id=job_id,
 207 |         )
 208 |     return job
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L189 | Define `get_owned_job_or_404`; bind its arguments when called. The body executes only when invoked. |
| L190 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L191 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L192 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L193 | Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. |
| L194 | Finish/continue the signature; the declared return annotation is `ProcessingJob`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L195 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L197 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L198 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L199 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L200 | Evaluate the right-hand side, then bind/store it in `job`: `_query_owned_job(session, user_id=user_id, job_id=job_id)` — Call [_query_owned_job](../db/queries.md#walk-get-owned-job) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L201 | Evaluate the branch condition: compare whether `job` is the same object as `None`. If truthy, enter L202; otherwise skip this indented block and continue after it. |
| L202 | `raise_api_error(404, ErrorCode.NOT_FOUND, 'Job not found.', job_id=job_id)` — Call [raise_api_error](#walk-raise-api-error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L203 | Supply positional argument 1 to `raise_api_error`: `404`. |
| L204 | Supply positional argument 2 to `raise_api_error`: the `NOT_FOUND` attribute of `ErrorCode`. |
| L205 | Supply positional argument 3 to `raise_api_error`: `'Job not found.'`. |
| L206 | Supply `job_id` = `job_id`. Durable processing-job UUID. Evaluate the value as: the current `job_id` value. |
| L207 | Close the expression/container begun at L202; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L208 | Compute the return value: the current `job` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_parse_project_cursor(cursor: str) -> tuple[datetime, UUID]`

**Arguments:** Encoded page cursor. **Returns:** `(updated_at, project_id)`. **Work:** Decodes an object, requires string keys `u` and `i`, parses ISO timestamp/UUID, and treats naive timestamps as UTC. Value/type errors become HTTP 422 / `validation_error`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--parse-project-cursor"></a>

#### Line-by-line execution

[Current source: lines 216–234](../../../../Backend/app/repositories/projects.py#L216-L234). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `cursor` | `str`; required; positional or keyword | Opaque page continuation token; null starts the first page. |

**Declared result:** `tuple[datetime, UUID]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 216 | def _parse_project_cursor(cursor: str) -> tuple[datetime, UUID]:
 217 |     try:
 218 |         payload = decode_cursor(cursor)
 219 |         updated_raw = payload.get("u")
 220 |         id_raw = payload.get("i")
 221 |         if not isinstance(updated_raw, str) or not isinstance(id_raw, str):
 222 |             raise ValueError("malformed cursor payload")
 223 |         updated_at = datetime.fromisoformat(updated_raw)
 224 |         if updated_at.tzinfo is None:
 225 |             updated_at = updated_at.replace(tzinfo=timezone.utc)
 226 |         project_id = UUID(id_raw)
 227 |     except (ValueError, TypeError) as exc:
 228 |         raise_api_error(
 229 |             422,
 230 |             ErrorCode.VALIDATION_ERROR,
 231 |             "Invalid pagination cursor.",
 232 |         )
 233 |         raise exc  # pragma: no cover - raise_api_error always raises
 234 |     return updated_at, project_id
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L216 | Define `_parse_project_cursor`; bind its arguments when called. The body executes only when invoked. |
| L217 | Enter the protected block; failures are matched against `(ValueError, TypeError)` in order. |
| L218 | Evaluate the right-hand side, then bind/store it in `payload`: `decode_cursor(cursor)` — Call [decode_cursor](../schemas/common.md#walk-decode-cursor) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L219 | Evaluate the right-hand side, then bind/store it in `updated_raw`: `payload.get('u')` — Look up `'u'` in `payload`, using None when the key is absent (an existing null value is not replaced). |
| L220 | Evaluate the right-hand side, then bind/store it in `id_raw`: `payload.get('i')` — Look up `'i'` in `payload`, using None when the key is absent (an existing null value is not replaced). |
| L221 | Evaluate the branch condition: evaluate `not isinstance(updated_raw, str) or not isinstance(id_raw, str)` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L222; otherwise skip this indented block and continue after it. |
| L222 | Raise `ValueError('malformed cursor payload')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L223 | Evaluate the right-hand side, then bind/store it in `updated_at`: `datetime.fromisoformat(updated_raw)` — Parse an ISO-format timestamp; invalid text raises ValueError. |
| L224 | Evaluate the branch condition: compare whether `updated_at.tzinfo` is the same object as `None`. If truthy, enter L225; otherwise skip this indented block and continue after it. |
| L225 | Evaluate the right-hand side, then bind/store it in `updated_at`: `updated_at.replace(tzinfo=timezone.utc)` — Return a value with the specified replacements applied. |
| L226 | Evaluate the right-hand side, then bind/store it in `project_id`: `UUID(id_raw)` — Parse or construct a UUID; invalid text raises a conversion error. |
| L227 | Handle `(ValueError, TypeError)` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L228 | `raise_api_error(422, ErrorCode.VALIDATION_ERROR, 'Invalid pagination cursor.')` — Call [raise_api_error](#walk-raise-api-error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L229 | Supply positional argument 1 to `raise_api_error`: `422`. |
| L230 | Supply positional argument 2 to `raise_api_error`: the `VALIDATION_ERROR` attribute of `ErrorCode`. |
| L231 | Supply positional argument 3 to `raise_api_error`: `'Invalid pagination cursor.'`. |
| L232 | Close the expression/container begun at L228; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L233 | Raise `exc`; stop the normal path and transfer control to the nearest matching exception handler. |
| L234 | Compute the return value: build a tuple containing `updated_at`, `project_id`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `list_owned_projects(session, *, user_id, cursor: str | None, limit: int) -> tuple[list[Project], str | None]`

**Arguments:** Session, owner UUID, optional cursor, page size. **Returns:** Live rows and next cursor (null at end). **Work:** Requires 1–200, filters ownership/tombstones, orders `updated_at DESC, id DESC`, applies lexicographic "older than" cursor predicates, and fetches `limit+1`. If extra rows exist, truncates and encodes the last returned timestamp/ID as the continuation.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-list-owned-projects"></a>

#### Line-by-line execution

[Current source: lines 237–282](../../../../Backend/app/repositories/projects.py#L237-L282). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `cursor` | `str \| None`; required; keyword-only | Opaque page continuation token; null starts the first page. |
| `limit` | `int`; required; keyword-only | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |

**Declared result:** `tuple[list[Project], str | None]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 237 | def list_owned_projects(
 238 |     session: Session,
 239 |     *,
 240 |     user_id: UUID,
 241 |     cursor: str | None,
 242 |     limit: int,
 243 | ) -> tuple[list[Project], str | None]:
 244 |     """Return ``(items, next_cursor)`` for live projects of ``user_id``.
 245 | 
 246 |     Ordering ``updated_at DESC, id DESC`` matches the
 247 |     ``ix_projects_owner_live`` index.  ``next_cursor`` is ``None`` on
 248 |     the last page.  Malformed cursors raise ``422 validation_error``.
 249 |     """
 250 |     if limit < 1 or limit > 200:
 251 |         raise_api_error(
 252 |             422,
 253 |             ErrorCode.VALIDATION_ERROR,
 254 |             "limit must be between 1 and 200.",
 255 |         )
 256 | 
 257 |     statement = (
 258 |         select(Project)
 259 |         .where(
 260 |             Project.user_id == user_id,
 261 |             Project.deleted_at.is_(None),
 262 |         )
 263 |         .order_by(Project.updated_at.desc(), Project.id.desc())
 264 |         .limit(limit + 1)
 265 |     )
 266 |     if cursor is not None:
 267 |         updated_before, id_before = _parse_project_cursor(cursor)
 268 |         statement = statement.where(
 269 |             or_(
 270 |                 Project.updated_at < updated_before,
 271 |                 (Project.updated_at == updated_before) & (Project.id < id_before),
 272 |             )
 273 |         )
 274 |     rows = list(session.execute(statement).scalars().all())
 275 |     next_cursor: str | None = None
 276 |     if len(rows) > limit:
 277 |         rows = rows[:limit]
 278 |         last = rows[-1]
 279 |         next_cursor = encode_cursor(
 280 |             {"u": last.updated_at.isoformat(), "i": str(last.id)}
 281 |         )
 282 |     return rows, next_cursor
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L237 | Define `list_owned_projects`; bind its arguments when called. The body executes only when invoked. |
| L238 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L239 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L240 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L241 | Declare parameter `cursor` with annotation `str \| None`. Opaque page continuation token; null starts the first page. |
| L242 | Declare parameter `limit` with annotation `int`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. |
| L243 | Finish/continue the signature; the declared return annotation is `tuple[list[Project], str \| None]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L244 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L246 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L247 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L248 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L249 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L250 | Evaluate the branch condition: evaluate `limit < 1 or limit > 200` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L251; otherwise skip this indented block and continue after it. |
| L251 | `raise_api_error(422, ErrorCode.VALIDATION_ERROR, 'limit must be between 1 and 200.')` — Call [raise_api_error](#walk-raise-api-error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L252 | Supply positional argument 1 to `raise_api_error`: `422`. |
| L253 | Supply positional argument 2 to `raise_api_error`: the `VALIDATION_ERROR` attribute of `ErrorCode`. |
| L254 | Supply positional argument 3 to `raise_api_error`: `'limit must be between 1 and 200.'`. |
| L255 | Close the expression/container begun at L251; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L257 | Evaluate the right-hand side, then bind/store it in `statement`: `select(Project).where(Project.user_id == user_id, Project.deleted_at.is_(None)).order_by(Project.updated_at.desc(), Project.id.desc()).limit(limit + 1)` — Apply a SQL row limit; fetching limit+1 allows continuation detection; first obtain the receiver: `select(Project).where(Project.user_id == user_id, Project.deleted_at.is_(None)).order_by(Project.updated_at.desc(), Project.id.desc())` — Set SQL result ordering in the listed priority order; first obtain the receiver: `select(Project).where(Project.user_id == user_id, Project.deleted_at.is_(None))` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; inputs include add/concatenate `limit` and `1`, following the parentheses/operator precedence shown in `limit + 1`. |
| L258 | `select(Project)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L259 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L260 | Continue the enclosing expression: build a SQL predicate requiring `Project.user_id` equals `user_id`. |
| L261 | `Project.deleted_at.is_(None)` — Build an SQL IS predicate, commonly IS NULL for a live-row filter. |
| L262 | Close the expression/container begun at L258; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L263 | Set SQL result ordering in the listed priority order; apply this method to the result built by the preceding chain. |
| L264 | Apply a SQL row limit; fetching limit+1 allows continuation detection; apply this method to the result built by the preceding chain. |
| L265 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L266 | Evaluate the branch condition: compare whether `cursor` is not the same object as `None`. If truthy, enter L267; otherwise skip this indented block and continue after it. |
| L267 | Evaluate the right-hand side, then bind/store it in `(updated_before, id_before)`: `_parse_project_cursor(cursor)` — Call [_parse_project_cursor](#walk--parse-project-cursor) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L268 | Evaluate the right-hand side, then bind/store it in `statement`: `statement.where(or_(Project.updated_at < updated_before, (Project.updated_at == updated_before) & (Project.id < id_before)))` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; inputs include `or_(Project.updated_at < updated_before, (Project.updated_at == updated_before) & (Project.id < id_before))` — Combine SQL predicates with OR so at least one condition must hold. |
| L269 | `or_(Project.updated_at < updated_before, (Project.updated_at == updated_before) & (Project.id < id_before))` — Combine SQL predicates with OR so at least one condition must hold; inputs include combine with & `Project.updated_at == updated_before` and `Project.id < id_before`, following the parentheses/operator precedence shown in `(Project.updated_at == updated_before) & (Project.id < id_before)`. |
| L270 | Continue the enclosing expression: build a SQL predicate requiring `Project.updated_at` is less than `updated_before`. |
| L271 | Continue the enclosing expression: combine with & `Project.updated_at == updated_before` and `Project.id < id_before`, following the parentheses/operator precedence shown in `(Project.updated_at == updated_before) & (Project.id < id_before)`. |
| L272 | Close the expression/container begun at L269; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L273 | Close the expression/container begun at L268; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L274 | Evaluate the right-hand side, then bind/store it in `rows`: `list(session.execute(statement).scalars().all())` — Materialize the iterable in order into a list (or create an empty list); inputs include `session.execute(statement).scalars().all()` — Materialize all remaining values in this SQL result; first obtain the receiver: `session.execute(statement).scalars()` — Expose only the first selected column from each row of the SQL result. |
| L275 | Evaluate the right-hand side, then bind/store it in `next_cursor`: None (no value). |
| L276 | Evaluate the branch condition: compare whether `len(rows)` is greater than `limit`. If truthy, enter L277; otherwise skip this indented block and continue after it. |
| L277 | Evaluate the right-hand side, then bind/store it in `rows`: slice `rows` from the beginning up to `limit` (exclusive stop). |
| L278 | Evaluate the right-hand side, then bind/store it in `last`: look up index/key `-1` in `rows`; a missing key or out-of-range index raises. |
| L279 | Evaluate the right-hand side, then bind/store it in `next_cursor`: `encode_cursor({'u': last.updated_at.isoformat(), 'i': str(last.id)})` — Call [encode_cursor](../schemas/common.md#walk-encode-cursor) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L280 | Add mapping entry `'u'`: `last.updated_at.isoformat()` — Format the timestamp/date as an ISO-format string for the cursor/payload. Add mapping entry `'i'`: `str(last.id)` — Convert the input to its string representation. |
| L281 | Close the expression/container begun at L279; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L282 | Compute the return value: build a tuple containing `rows`, `next_cursor`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `create_owned_project(session, *, user_id, name: str, description: str | None) -> Project`

**Arguments:** Session, server-derived owner UUID, validated project fields. **Returns:** Newly flushed project with generated defaults. **Work:** Constructs/adds the row, flushes, and leaves commit to the route.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-create-owned-project"></a>

#### Line-by-line execution

[Current source: lines 290–301](../../../../Backend/app/repositories/projects.py#L290-L301). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `name` | `str`; required; keyword-only | Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. |
| `description` | `str \| None`; required; keyword-only | Optional project description; update logic distinguishes clearing it from leaving it unchanged. |

**Declared result:** `Project`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 290 | def create_owned_project(
 291 |     session: Session,
 292 |     *,
 293 |     user_id: UUID,
 294 |     name: str,
 295 |     description: str | None,
 296 | ) -> Project:
 297 |     """Create a project owned by ``user_id``.  Name is already trimmed by DTO."""
 298 |     project = Project(user_id=user_id, name=name, description=description)
 299 |     session.add(project)
 300 |     session.flush()
 301 |     return project
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L290 | Define `create_owned_project`; bind its arguments when called. The body executes only when invoked. |
| L291 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L292 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L293 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L294 | Declare parameter `name` with annotation `str`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. |
| L295 | Declare parameter `description` with annotation `str \| None`. Optional project description; update logic distinguishes clearing it from leaving it unchanged. |
| L296 | Finish/continue the signature; the declared return annotation is `Project`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L297 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L298 | Evaluate the right-hand side, then bind/store it in `project`: `Project(user_id=user_id, name=name, description=description)` — Construct `Project` with the shown fields; its class/model initialization rules apply. |
| L299 | `session.add(project)` — Attach the ORM object to this session for insertion/update tracking; this does not commit it. The return value is not assigned here. |
| L300 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L301 | Compute the return value: the current `project` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `update_owned_project(session, project, *, name, description, fields_set: set[str]) -> Project`

**Arguments:** Session, already-owned ORM row, nullable request values, and explicitly supplied field names. **Returns:** Updated project. **Work:** Changes only present fields. Explicit null/blank name raises 422; names are trimmed. Description null/blank clears it. Flushes the mutation; empty-field rejection is handled by the route.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-update-owned-project"></a>

#### Line-by-line execution

[Current source: lines 304–333](../../../../Backend/app/repositories/projects.py#L304-L333). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `project` | `Project`; required; positional or keyword | Caller-supplied project; each read, transformation, and validation is traced below. |
| `name` | `str \| None`; required; keyword-only | Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. |
| `description` | `str \| None`; required; keyword-only | Optional project description; update logic distinguishes clearing it from leaving it unchanged. |
| `fields_set` | `set[str]`; required; keyword-only | Caller-supplied fields set; each read, transformation, and validation is traced below. |

**Declared result:** `Project`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 304 | def update_owned_project(
 305 |     session: Session,
 306 |     project: Project,
 307 |     *,
 308 |     name: str | None,
 309 |     description: str | None,
 310 |     fields_set: set[str],
 311 | ) -> Project:
 312 |     """Apply a PATCH body to ``project``.
 313 | 
 314 |     ``fields_set`` (``model_fields_set``) distinguishes omitted fields
 315 |     (no change) from explicit values: an explicit ``description: null``
 316 |     clears the description, while an explicit ``name: null`` is
 317 |     rejected (name can never be null).  An empty set means the caller
 318 |     sent no changes (handler maps this to ``422`` before calling).
 319 |     """
 320 |     if "name" in fields_set:
 321 |         if name is None or not name.strip():
 322 |             raise_api_error(
 323 |                 422,
 324 |                 ErrorCode.VALIDATION_ERROR,
 325 |                 "name must not be blank.",
 326 |                 project_id=project.id,
 327 |             )
 328 |         project.name = name.strip()
 329 |     if "description" in fields_set:
 330 |         # None / blank => cleared (DTO normalizes blank to None already).
 331 |         project.description = None if description is None else (description.strip() or None)
 332 |     session.flush()
 333 |     return project
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L304 | Define `update_owned_project`; bind its arguments when called. The body executes only when invoked. |
| L305 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L306 | Declare parameter `project` with annotation `Project`. Caller-supplied project; its uses and transformations are traced below. |
| L307 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L308 | Declare parameter `name` with annotation `str \| None`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. |
| L309 | Declare parameter `description` with annotation `str \| None`. Optional project description; update logic distinguishes clearing it from leaving it unchanged. |
| L310 | Declare parameter `fields_set` with annotation `set[str]`. Caller-supplied fields set; its uses and transformations are traced below. |
| L311 | Finish/continue the signature; the declared return annotation is `Project`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L312 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L314 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L315 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L316 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L317 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L318 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L319 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L320 | Evaluate the branch condition: compare whether `'name'` is contained in `fields_set`. If truthy, enter L321; otherwise skip this indented block and continue after it. |
| L321 | Evaluate the branch condition: evaluate `name is None or not name.strip()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L322; otherwise skip this indented block and continue after it. |
| L322 | `raise_api_error(422, ErrorCode.VALIDATION_ERROR, 'name must not be blank.', project_id=project.id)` — Call [raise_api_error](#walk-raise-api-error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L323 | Supply positional argument 1 to `raise_api_error`: `422`. |
| L324 | Supply positional argument 2 to `raise_api_error`: the `VALIDATION_ERROR` attribute of `ErrorCode`. |
| L325 | Supply positional argument 3 to `raise_api_error`: `'name must not be blank.'`. |
| L326 | Supply `project_id` = `project.id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the `id` attribute of `project`. |
| L327 | Close the expression/container begun at L322; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L328 | Evaluate the right-hand side, then bind/store it in `project.name`: `name.strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed. |
| L329 | Evaluate the branch condition: compare whether `'description'` is contained in `fields_set`. If truthy, enter L331; otherwise skip this indented block and continue after it. |
| L330 | Comment only: None / blank => cleared (DTO normalizes blank to None already).. It does not execute; the neighboring code determines behavior. |
| L331 | Evaluate the right-hand side, then bind/store it in `project.description`: check `description is None`; when true use None (no value), otherwise evaluate `description.strip() or None` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool (only the selected branch is evaluated). |
| L332 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L333 | Compute the return value: the current `project` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `tombstone_project(session, project, *, now: datetime | None = None) -> Project`

**Arguments:** Session, project, optional injected time. **Returns:** The same project. **Work:** Sets `deleted_at` only if not already set, using supplied time or UTC now, then flushes. It does not enumerate documents, enqueue cleanup, or hard-delete the row; the caller coordinates those steps.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-tombstone-project"></a>

#### Line-by-line execution

[Current source: lines 336–346](../../../../Backend/app/repositories/projects.py#L336-L346). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `project` | `Project`; required; positional or keyword | Caller-supplied project; each read, transformation, and validation is traced below. |
| `now` | `datetime \| None`; default `None`; keyword-only | Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |

**Declared result:** `Project`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 336 | def tombstone_project(
 337 |     session: Session,
 338 |     project: Project,
 339 |     *,
 340 |     now: datetime | None = None,
 341 | ) -> Project:
 342 |     """Mark a project deleted (tombstone); cleanup jobs are enqueued by the caller."""
 343 |     if project.deleted_at is None:
 344 |         project.deleted_at = now or _utcnow()
 345 |     session.flush()
 346 |     return project
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L336 | Define `tombstone_project`; bind its arguments when called. The body executes only when invoked. |
| L337 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L338 | Declare parameter `project` with annotation `Project`. Caller-supplied project; its uses and transformations are traced below. |
| L339 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L340 | Declare parameter `now` with annotation `datetime \| None`. Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |
| L341 | Finish/continue the signature; the declared return annotation is `Project`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L342 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L343 | Evaluate the branch condition: compare whether `project.deleted_at` is the same object as `None`. If truthy, enter L344; otherwise skip this indented block and continue after it. |
| L344 | Evaluate the right-hand side, then bind/store it in `project.deleted_at`: evaluate `now or _utcnow()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L345 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L346 | Compute the return value: the current `project` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
