# `app/repositories/documents.py`

[Source](../../../../Backend/app/repositories/documents.py) · [Backend index](../../README.md)

Document reservation, processing retry, tombstones/cleanup enqueue, pagination, and a request-transaction queue adapter. Functions perform SQL only and leave commits to callers. `InvalidRetryError`, `ProcessingInProgressError`, and `AlreadyDeletingError` are marker exceptions with no local methods; current routes mostly raise structured HTTP errors directly.

## Conversion, errors, and queue adapter

### `document_to_dto(document: Document) -> DocumentDto`

**Arguments:** ORM document. **Returns:** Public document DTO. **Work:** Uses Pydantic attribute validation; private storage/hash fields are omitted by schema.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-document-to-dto"></a>

#### Line-by-line execution

[Current source: lines 81–82](../../../../Backend/app/repositories/documents.py#L81-L82). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `document` | `Document`; required; positional or keyword | Caller-supplied document; each read, transformation, and validation is traced below. |

**Declared result:** `DocumentDto`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  81 | def document_to_dto(document: Document) -> DocumentDto:
  82 |     return DocumentDto.model_validate(document)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L81 | Define `document_to_dto`; bind its arguments when called. The body executes only when invoked. |
| L82 | Compute the return value: `DocumentDto.model_validate(document)` — Validate/coerce the input into this Pydantic model, including configured field validators. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `job_to_dto(job: ProcessingJob) -> ProcessingJobDto`

**Arguments:** ORM job. **Returns:** Public job DTO. **Work:** Uses `model_validate`; lease/resource secrets are excluded.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-job-to-dto"></a>

#### Line-by-line execution

[Current source: lines 85–86](../../../../Backend/app/repositories/documents.py#L85-L86). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `job` | `ProcessingJob`; required; positional or keyword | Caller-supplied job; each read, transformation, and validation is traced below. |

**Declared result:** `ProcessingJobDto`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  85 | def job_to_dto(job: ProcessingJob) -> ProcessingJobDto:
  86 |     return ProcessingJobDto.model_validate(job)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L85 | Define `job_to_dto`; bind its arguments when called. The body executes only when invoked. |
| L86 | Compute the return value: `ProcessingJobDto.model_validate(job)` — Validate/coerce the input into this Pydantic model, including configured field validators. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `DocumentConflictError.__init__(self, *, document: Document, message="duplicate_request_conflict") -> None`

**Arguments:** Conflicting stored document and optional message. **Returns:** `None`. **Work:** Initializes the exception and exposes `.document` so the route can identify the original reservation.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-documentconflicterror---init--"></a>

#### Line-by-line execution

[Current source: lines 97–99](../../../../Backend/app/repositories/documents.py#L97-L99). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `document` | `Document`; required; keyword-only | Caller-supplied document; each read, transformation, and validation is traced below. |
| `message` | `str`; default `'duplicate_request_conflict'`; keyword-only | Caller-supplied message; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  97 |     def __init__(self, *, document: Document, message: str = "duplicate_request_conflict") -> None:
  98 |         super().__init__(message)
  99 |         self.document = document
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L97 | Define `DocumentConflictError.__init__`; bind its arguments when called. The body executes only when invoked. |
| L98 | `super().__init__(message)` — Initialize the base exception/object with the supplied arguments; first obtain the receiver: `super()` — Resolve the superclass proxy for the current method and instance. The return value is not assigned here. |
| L99 | Evaluate the right-hand side, then bind/store it in `self.document`: the current `document` value. |

<!-- END LINE WALKTHROUGH -->

### `_raise_api(status_code: int, code: ErrorCode, message: str, **ids: Any) -> None`

**Arguments:** HTTP status, code, safe message, resource-ID fields. **Returns:** Never normally. **Work:** Validates/JSON-serializes `ApiError` with aliases and raises `HTTPException`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--raise-api"></a>

#### Line-by-line execution

[Current source: lines 114–118](../../../../Backend/app/repositories/documents.py#L114-L118). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `status_code` | `int`; required; positional or keyword | Caller-supplied status code; each read, transformation, and validation is traced below. |
| `code` | `ErrorCode`; required; positional or keyword | Caller-supplied code; each read, transformation, and validation is traced below. |
| `message` | `str`; required; positional or keyword | Caller-supplied message; each read, transformation, and validation is traced below. |
| `ids` | `Any`; implicitly supplied/collected; ** keyword extras | Caller-supplied ids; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 114 | def _raise_api(status_code: int, code: ErrorCode, message: str, **ids: Any) -> None:
 115 |     detail = ApiError(code=code, message=message, **ids).model_dump(
 116 |         by_alias=True, mode="json"
 117 |     )
 118 |     raise HTTPException(status_code=status_code, detail=detail)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L114 | Define `_raise_api`; bind its arguments when called. The body executes only when invoked. |
| L115 | Evaluate the right-hand side, then bind/store it in `detail`: `ApiError(code=code, message=message, **ids).model_dump(by_alias=True, mode='json')` — Serialize Pydantic fields into a dictionary; by_alias=True uses wire names and mode='json' converts JSON-compatible values; first obtain the receiver: `ApiError(code=code, message=message, **ids)` — Construct `ApiError` with the supplied diagnostic fields; the surrounding raise determines propagation. |
| L116 | Supply `by_alias` = `True`.  Evaluate the value as: `True`. Supply `mode` = `'json'`.  Evaluate the value as: `'json'`. |
| L117 | Close the expression/container begun at L115; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L118 | Raise `HTTPException(status_code=status_code, detail=detail)`; stop the normal path and transfer control to the nearest matching exception handler. |

<!-- END LINE WALKTHROUGH -->

### `_utcnow() -> datetime`

**Arguments:** None. **Returns:** Current aware UTC time. **Work:** Calls `datetime.now(timezone.utc)`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--utcnow"></a>

#### Line-by-line execution

[Current source: lines 121–122](../../../../Backend/app/repositories/documents.py#L121-L122). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `datetime`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 121 | def _utcnow() -> datetime:
 122 |     return datetime.now(timezone.utc)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L121 | Define `_utcnow`; bind its arguments when called. The body executes only when invoked. |
| L122 | Compute the return value: `datetime.now(timezone.utc)` — Read the current wall-clock date/time in the supplied timezone. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `DirectJobQueue.enqueue_job(self, session, *, owner_user_id, project_id, target_document_id, document_id, kind, target_epoch, resource_snapshot, available_at=None, max_attempts=3, status="awaiting_upload", stage="uploading") -> ProcessingJob`

**Arguments:** Caller session; immutable owner/project/target UUIDs; nullable document FK; kind string; epoch; JSON snapshot; optional due time, attempt cap, initial state/stage. **Returns:** New job or existing nonterminal winner. **Work:** Delegates all values to canonical `app.jobs.queue.enqueue_job`, converting kind to `str`. Defaults target upload reservation; savepoint/idempotency details are in [jobs/queue.md](../jobs/queue.md).

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-directjobqueue-enqueue-job"></a>

#### Line-by-line execution

[Current source: lines 140–180](../../../../Backend/app/repositories/documents.py#L140-L180). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `owner_user_id` | `UUID`; required; keyword-only | Internal owner UUID copied into the job's durable ownership snapshot. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `target_document_id` | `UUID`; required; keyword-only | Immutable target UUID retained even when the live document relationship disappears. |
| `document_id` | `UUID \| None`; required; keyword-only | Document UUID; filenames do not establish document identity. |
| `kind` | `str`; required; keyword-only | Caller-supplied kind; each read, transformation, and validation is traced below. |
| `target_epoch` | `int`; required; keyword-only | Expected document processing epoch used to invalidate obsolete attempts. |
| `resource_snapshot` | `dict[str, Any]`; required; keyword-only | JSON-compatible resource facts copied into a durable job. |
| `available_at` | `datetime \| None`; default `None`; keyword-only | Earliest time a queued/retry-wait job may be claimed. |
| `max_attempts` | `int`; default `3`; keyword-only | Maximum number of claims before retryable failures become terminal. |
| `status` | `str`; default `'awaiting_upload'`; keyword-only | Caller-supplied status; each read, transformation, and validation is traced below. |
| `stage` | `str \| None`; default `'uploading'`; keyword-only | Public job stage to record, such as extracting, embedding, indexing, or publishing. |

**Declared result:** `ProcessingJob`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 140 |     def enqueue_job(
 141 |         self,
 142 |         session: Session,
 143 |         *,
 144 |         owner_user_id: UUID,
 145 |         project_id: UUID,
 146 |         target_document_id: UUID,
 147 |         document_id: UUID | None,
 148 |         kind: str,
 149 |         target_epoch: int,
 150 |         resource_snapshot: dict[str, Any],
 151 |         available_at: datetime | None = None,
 152 |         max_attempts: int = 3,
 153 |         status: str = "awaiting_upload",
 154 |         stage: str | None = "uploading",
 155 |     ) -> ProcessingJob:
 156 |         """Idempotent insert per the nonterminal (target, kind) index.
 157 | 
 158 |         ``status``/``stage`` default to the upload path
 159 |         (``awaiting_upload``/``uploading``) and are optional extras
 160 |         beyond the frozen Protocol (callers may instead set these
 161 |         attributes on the returned row after the call).  Enqueue
 162 |         insert uses a SAVEPOINT so a concurrent duplicate losing the
 163 |         race returns the winner without aborting the caller's
 164 |         transaction.
 165 |         """
 166 |         job = enqueue_durable_job(
 167 |             session,
 168 |             owner_user_id=owner_user_id,
 169 |             project_id=project_id,
 170 |             target_document_id=target_document_id,
 171 |             document_id=document_id,
 172 |             kind=str(kind),
 173 |             target_epoch=target_epoch,
 174 |             resource_snapshot=resource_snapshot,
 175 |             available_at=available_at,
 176 |             max_attempts=max_attempts,
 177 |             status=status,
 178 |             stage=stage,
 179 |         )
 180 |         return job
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L140 | Define `DirectJobQueue.enqueue_job`; bind its arguments when called. The body executes only when invoked. |
| L141 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L142 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L143 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L144 | Declare parameter `owner_user_id` with annotation `UUID`. Internal owner UUID copied into the job's durable ownership snapshot. |
| L145 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L146 | Declare parameter `target_document_id` with annotation `UUID`. Immutable target UUID retained even when the live document relationship disappears. |
| L147 | Declare parameter `document_id` with annotation `UUID \| None`. Document UUID; filenames do not establish document identity. |
| L148 | Declare parameter `kind` with annotation `str`. Caller-supplied kind; its uses and transformations are traced below. |
| L149 | Declare parameter `target_epoch` with annotation `int`. Expected document processing epoch used to invalidate obsolete attempts. |
| L150 | Declare parameter `resource_snapshot` with annotation `dict[str, Any]`. JSON-compatible resource facts copied into a durable job. |
| L151 | Declare parameter `available_at` with annotation `datetime \| None`. Earliest time a queued/retry-wait job may be claimed. |
| L152 | Declare parameter `max_attempts` with annotation `int`. Maximum number of claims before retryable failures become terminal. |
| L153 | Declare parameter `status` with annotation `str`. Caller-supplied status; its uses and transformations are traced below. |
| L154 | Declare parameter `stage` with annotation `str \| None`. Public job stage to record, such as extracting, embedding, indexing, or publishing. |
| L155 | Finish/continue the signature; the declared return annotation is `ProcessingJob`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L156 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L158 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L159 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L160 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L161 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L162 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L163 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L164 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L165 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L166 | Evaluate the right-hand side, then bind/store it in `job`: `enqueue_durable_job` with the arguments detailed below — Call [enqueue_durable_job](../jobs/queue.md#walk-enqueue-job) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L167 | Supply positional argument 1 to `enqueue_durable_job`: the current `session` value. |
| L168 | Supply `owner_user_id` = `owner_user_id`. Internal owner UUID copied into the job's durable ownership snapshot. Evaluate the value as: the current `owner_user_id` value. |
| L169 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L170 | Supply `target_document_id` = `target_document_id`. Immutable target UUID retained even when the live document relationship disappears. Evaluate the value as: the current `target_document_id` value. |
| L171 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L172 | Supply `kind` = `str(kind)`.  Evaluate the value as: `str(kind)` — Convert the input to its string representation. |
| L173 | Supply `target_epoch` = `target_epoch`. Expected document processing epoch used to invalidate obsolete attempts. Evaluate the value as: the current `target_epoch` value. |
| L174 | Supply `resource_snapshot` = `resource_snapshot`. JSON-compatible resource facts copied into a durable job. Evaluate the value as: the current `resource_snapshot` value. |
| L175 | Supply `available_at` = `available_at`. Earliest time a queued/retry-wait job may be claimed. Evaluate the value as: the current `available_at` value. |
| L176 | Supply `max_attempts` = `max_attempts`. Maximum number of claims before retryable failures become terminal. Evaluate the value as: the current `max_attempts` value. |
| L177 | Supply `status` = `status`.  Evaluate the value as: the current `status` value. |
| L178 | Supply `stage` = `stage`. Public job stage to record, such as extracting, embedding, indexing, or publishing. Evaluate the value as: the current `stage` value. |
| L179 | Close the expression/container begun at L166; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L180 | Compute the return value: the current `job` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `DirectJobQueue.cancel_job(self, session, *, job_id: UUID, reason: str) -> bool`

**Arguments:** Session, job ID, safe reason. **Returns:** Whether a nonterminal job changed. **Work:** Loads by PK, returns false if absent/terminal, sets `cancelled`/finish time, sets cancellation diagnostics only if no error code exists (message capped at 1000), and flushes. This adapter does not bump the lease token or clear lease fields; later queue writes reject the non-running status.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-directjobqueue-cancel-job"></a>

#### Line-by-line execution

[Current source: lines 182–193](../../../../Backend/app/repositories/documents.py#L182-L193). Line numbers below are file line numbers, not a separate example.

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
 182 |     def cancel_job(self, session: Session, *, job_id: UUID, reason: str) -> bool:
 183 |         """Cancel one nonterminal job; False when already terminal/missing."""
 184 |         job = session.get(ProcessingJob, job_id)
 185 |         if job is None or job.status not in self._NONTERMINAL:
 186 |             return False
 187 |         job.status = "cancelled"
 188 |         job.finished_at = _utcnow()
 189 |         if job.last_error_code is None:
 190 |             job.last_error_code = "cancelled"
 191 |             job.last_error_message = reason[:1000] if reason else "cancelled"
 192 |         session.flush()
 193 |         return True
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L182 | Define `DirectJobQueue.cancel_job`; bind its arguments when called. The body executes only when invoked. |
| L183 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L184 | Evaluate the right-hand side, then bind/store it in `job`: `session.get(ProcessingJob, job_id)` — Look up the mapped object by primary key, using the session identity map when possible, otherwise SQL. |
| L185 | Evaluate the branch condition: evaluate `job is None or job.status not in self._NONTERMINAL` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L186; otherwise skip this indented block and continue after it. |
| L186 | Compute the return value: `False`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L187 | Evaluate the right-hand side, then bind/store it in `job.status`: `'cancelled'`. |
| L188 | Evaluate the right-hand side, then bind/store it in `job.finished_at`: `_utcnow()` — Read the module's current UTC timestamp helper. |
| L189 | Evaluate the branch condition: compare whether `job.last_error_code` is the same object as `None`. If truthy, enter L190; otherwise skip this indented block and continue after it. |
| L190 | Evaluate the right-hand side, then bind/store it in `job.last_error_code`: `'cancelled'`. |
| L191 | Evaluate the right-hand side, then bind/store it in `job.last_error_message`: check `reason`; when true use slice `reason` from the beginning up to `1000` (exclusive stop), otherwise `'cancelled'` (only the selected branch is evaluated). |
| L192 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L193 | Compute the return value: `True`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `DirectJobQueue.cancel_process_jobs_for_document(self, session, *, document_id: UUID, reason: str) -> list[ProcessingJob]`

**Arguments:** Session, target document, reason. **Returns:** Cancelled jobs. **Work:** Delegates to `cancel_process_jobs`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-directjobqueue-cancel-process-jobs-for-document"></a>

#### Line-by-line execution

[Current source: lines 195–199](../../../../Backend/app/repositories/documents.py#L195-L199). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `document_id` | `UUID`; required; keyword-only | Document UUID; filenames do not establish document identity. |
| `reason` | `str`; required; keyword-only | Human-readable cancellation/decision reason recorded or returned by this operation. |

**Declared result:** `list[ProcessingJob]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 195 |     def cancel_process_jobs_for_document(
 196 |         self, session: Session, *, document_id: UUID, reason: str
 197 |     ) -> list[ProcessingJob]:
 198 |         """Cancel every nonterminal ``process_document`` job for a document."""
 199 |         return cancel_process_jobs(session, document_id=document_id, reason=reason)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L195 | Define `DirectJobQueue.cancel_process_jobs_for_document`; bind its arguments when called. The body executes only when invoked. |
| L196 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `document_id` with annotation `UUID`. Document UUID; filenames do not establish document identity. Declare parameter `reason` with annotation `str`. Human-readable cancellation/decision reason recorded or returned by this operation. |
| L197 | Finish/continue the signature; the declared return annotation is `list[ProcessingJob]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L198 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L199 | Compute the return value: `cancel_process_jobs(session, document_id=document_id, reason=reason)` — Call [cancel_process_jobs](#walk-cancel-process-jobs) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `cancel_process_jobs(session, *, document_id: UUID, reason: str) -> list[ProcessingJob]`

**Arguments:** Session, target UUID, safe reason. **Returns:** All changed process-job rows. **Work:** Selects matching `process_document` jobs in four nonterminal statuses, marks them cancelled/finished, preserves existing error diagnostics or adds capped cancellation text, and flushes if any changed. It does not cancel cleanup jobs or independently verify ownership.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-cancel-process-jobs"></a>

#### Line-by-line execution

[Current source: lines 202–231](../../../../Backend/app/repositories/documents.py#L202-L231). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `document_id` | `UUID`; required; keyword-only | Document UUID; filenames do not establish document identity. |
| `reason` | `str`; required; keyword-only | Human-readable cancellation/decision reason recorded or returned by this operation. |

**Declared result:** `list[ProcessingJob]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 202 | def cancel_process_jobs(
 203 |     session: Session, *, document_id: UUID, reason: str
 204 | ) -> list[ProcessingJob]:
 205 |     """Cancel every nonterminal ``process_document`` job for a document.
 206 | 
 207 |     Standalone helper (not a ``JobQueue`` method) so retry/delete keep
 208 |     working when A4's queue replaces :class:`DirectJobQueue`.
 209 |     """
 210 |     jobs = list(
 211 |         session.execute(
 212 |             select(ProcessingJob).where(
 213 |                 ProcessingJob.target_document_id == document_id,
 214 |                 ProcessingJob.kind == "process_document",
 215 |                 ProcessingJob.status.in_(
 216 |                     ("awaiting_upload", "queued", "running", "retry_wait")
 217 |                 ),
 218 |             )
 219 |         ).scalars().all()
 220 |     )
 221 |     cancelled: list[ProcessingJob] = []
 222 |     for job in jobs:
 223 |         job.status = "cancelled"
 224 |         job.finished_at = _utcnow()
 225 |         if job.last_error_code is None:
 226 |             job.last_error_code = "cancelled"
 227 |             job.last_error_message = reason[:1000]
 228 |         cancelled.append(job)
 229 |     if cancelled:
 230 |         session.flush()
 231 |     return cancelled
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L202 | Define `cancel_process_jobs`; bind its arguments when called. The body executes only when invoked. |
| L203 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `document_id` with annotation `UUID`. Document UUID; filenames do not establish document identity. Declare parameter `reason` with annotation `str`. Human-readable cancellation/decision reason recorded or returned by this operation. |
| L204 | Finish/continue the signature; the declared return annotation is `list[ProcessingJob]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L205 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L207 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L208 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L209 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L210 | Evaluate the right-hand side, then bind/store it in `jobs`: `list` with the arguments detailed below — Materialize the iterable in order into a list (or create an empty list); inputs include `session.execute(select(ProcessingJob).where(ProcessingJob.target_document_id == document_id, ProcessingJob.kind == 'process_document', ProcessingJob.status.in_(('awaiting_upload', 'queued', 'running', 'retry_wait')))).scalars().all` with the arguments detailed below — Materialize all remaining values in this SQL result; first obtain the receiver: `session.execute(select(ProcessingJob).where(ProcessingJob.target_document_id == document_id, ProcessingJob.kind == 'process_document', ProcessingJob.status.in_(('awaiting_upload', 'queued', 'running', 'retry_wait')))).scalars` with the arguments detailed below — Expose only the first selected column from each row of the SQL result. |
| L211 | `session.execute` with the arguments detailed below — Execute the SQL statement in the current transaction and return its Result (including rowcount for guarded updates); inputs include `select(ProcessingJob).where` with the arguments detailed below — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L212 | `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L213 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.target_document_id` equals `document_id`. |
| L214 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.kind` equals `'process_document'`. |
| L215 | `ProcessingJob.status.in_(('awaiting_upload', 'queued', 'running', 'retry_wait'))` — Build a SQL membership predicate for the supplied allowed values. |
| L216 | Supply positional argument 1 to `ProcessingJob.status.in_`: build a tuple containing `'awaiting_upload'`, `'queued'`, `'running'`, `'retry_wait'`. |
| L217 | Close the expression/container begun at L215; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L218 | Close the expression/container begun at L212; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L219 | Supply positional argument 1 to `list`: `session.execute(select(ProcessingJob).where(ProcessingJob.target_document_id == document_id, ProcessingJob.kind == 'process_document', ProcessingJob.status.in_(('awaiting_upload', 'queued', 'running', 'retry_wait')))).scalars().all` with the arguments detailed below — Materialize all remaining values in this SQL result; first obtain the receiver: `session.execute(select(ProcessingJob).where(ProcessingJob.target_document_id == document_id, ProcessingJob.kind == 'process_document', ProcessingJob.status.in_(('awaiting_upload', 'queued', 'running', 'retry_wait')))).scalars` with the arguments detailed below — Expose only the first selected column from each row of the SQL result; first obtain the receiver: `session.execute` with the arguments detailed below — Execute the SQL statement in the current transaction and return its Result (including rowcount for guarded updates). |
| L220 | Close the expression/container begun at L210; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L221 | Evaluate the right-hand side, then bind/store it in `cancelled`: build a list containing no items. |
| L222 | Iterate `jobs` (the current `jobs` value), assigning each item to `job`. Execute the indented body once per item; an empty iterable skips it. |
| L223 | Evaluate the right-hand side, then bind/store it in `job.status`: `'cancelled'`. |
| L224 | Evaluate the right-hand side, then bind/store it in `job.finished_at`: `_utcnow()` — Read the module's current UTC timestamp helper. |
| L225 | Evaluate the branch condition: compare whether `job.last_error_code` is the same object as `None`. If truthy, enter L226; otherwise skip this indented block and continue after it. |
| L226 | Evaluate the right-hand side, then bind/store it in `job.last_error_code`: `'cancelled'`. |
| L227 | Evaluate the right-hand side, then bind/store it in `job.last_error_message`: slice `reason` from the beginning up to `1000` (exclusive stop). |
| L228 | `cancelled.append(job)` — Append one object to the mutable list in place. The return value is not assigned here. |
| L229 | Evaluate the branch condition: the current `cancelled` value. If truthy, enter L230; otherwise skip this indented block and continue after it. |
| L230 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L231 | Compute the return value: the current `cancelled` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `get_job_queue() -> DirectJobQueue`

**Arguments:** None. **Returns:** New request-side queue adapter. **Work:** Constructs the lightweight adapter without SQL/provider calls.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-job-queue"></a>

#### Line-by-line execution

[Current source: lines 234–236](../../../../Backend/app/repositories/documents.py#L234-L236). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `DirectJobQueue`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 234 | def get_job_queue() -> DirectJobQueue:
 235 |     """FastAPI factory for the default queue (A0 overrides with A4's queue)."""
 236 |     return DirectJobQueue()
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L234 | Define `get_job_queue`; bind its arguments when called. The body executes only when invoked. |
| L235 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L236 | Compute the return value: `DirectJobQueue()` — Construct `DirectJobQueue` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

## Reservation and lifecycle helpers

### `_get_owned_project(session, *, user_id, project_id, include_deleted=False)`

**Arguments:** Session, owner/project UUIDs, tombstone visibility. **Returns:** Owned project or `None`. **Work:** Delegates to `app.db.queries.get_owned_project`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--get-owned-project"></a>

#### Line-by-line execution

[Current source: lines 244–253](../../../../Backend/app/repositories/documents.py#L244-L253). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `include_deleted` | `bool`; default `False`; keyword-only | Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |

**Declared result:** No return annotation; follow the return/yield lines below. Python supplies None when a non-generator reaches the end without return.

**Numbered source**

```text
 244 | def _get_owned_project(
 245 |     session: Session,
 246 |     *,
 247 |     user_id: UUID,
 248 |     project_id: UUID,
 249 |     include_deleted: bool = False,
 250 | ):
 251 |     return _query_owned_project(
 252 |         session, user_id=user_id, project_id=project_id, include_deleted=include_deleted
 253 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L244 | Define `_get_owned_project`; bind its arguments when called. The body executes only when invoked. |
| L245 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L246 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L247 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L248 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L249 | Declare parameter `include_deleted` with annotation `bool`. Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |
| L250 | Finish/continue the signature; no return annotation is declared. |
| L251 | Compute the return value: `_query_owned_project(session, user_id=user_id, project_id=project_id, include_deleted=include_deleted)` — Call [_query_owned_project](../db/queries.md#walk-get-owned-project) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L252 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. Supply `include_deleted` = `include_deleted`. Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. Evaluate the value as: the current `include_deleted` value. |
| L253 | Close the expression/container begun at L251; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `get_document_by_upload_request(session, *, project_id, upload_request_id) -> Document | None`

**Arguments:** Session, project UUID, request UUID. **Returns:** Matching reservation or `None`, including tombstones. **Work:** Queries the unique project/request pair. Caller must already authorize the project.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-document-by-upload-request"></a>

#### Line-by-line execution

[Current source: lines 256–265](../../../../Backend/app/repositories/documents.py#L256-L265). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `upload_request_id` | `UUID`; required; keyword-only | Upload request UUID used for per-project idempotency. |

**Declared result:** `Document | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 256 | def get_document_by_upload_request(
 257 |     session: Session, *, project_id: UUID, upload_request_id: UUID
 258 | ) -> Document | None:
 259 |     """Find the document reserved for one idempotency key in one project."""
 260 |     return session.scalar(
 261 |         select(Document).where(
 262 |             Document.project_id == project_id,
 263 |             Document.upload_request_id == upload_request_id,
 264 |         )
 265 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L256 | Define `get_document_by_upload_request`; bind its arguments when called. The body executes only when invoked. |
| L257 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. Declare parameter `upload_request_id` with annotation `UUID`. Upload request UUID used for per-project idempotency. |
| L258 | Finish/continue the signature; the declared return annotation is `Document \| None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L259 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L260 | Compute the return value: `session.scalar(select(Document).where(Document.project_id == project_id, Document.upload_request_id == upload_request_id))` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(Document).where(Document.project_id == project_id, Document.upload_request_id == upload_request_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(Document)` — Construct a SQL SELECT expression; building it does not execute SQL. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L261 | `select(Document)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L262 | Continue the enclosing expression: build a SQL predicate requiring `Document.project_id` equals `project_id`. |
| L263 | Continue the enclosing expression: build a SQL predicate requiring `Document.upload_request_id` equals `upload_request_id`. |
| L264 | Close the expression/container begun at L261; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L265 | Close the expression/container begun at L260; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `_latest_process_job(session, *, target_document_id) -> ProcessingJob | None`

**Arguments:** Session and target UUID. **Returns:** Most recently created process job, regardless of status. **Work:** Filters kind/target, orders `created_at DESC, id DESC`, limits to one.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--latest-process-job"></a>

#### Line-by-line execution

[Current source: lines 268–279](../../../../Backend/app/repositories/documents.py#L268-L279). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `target_document_id` | `UUID`; required; keyword-only | Immutable target UUID retained even when the live document relationship disappears. |

**Declared result:** `ProcessingJob | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 268 | def _latest_process_job(
 269 |     session: Session, *, target_document_id: UUID
 270 | ) -> ProcessingJob | None:
 271 |     return session.scalar(
 272 |         select(ProcessingJob)
 273 |         .where(
 274 |             ProcessingJob.target_document_id == target_document_id,
 275 |             ProcessingJob.kind == "process_document",
 276 |         )
 277 |         .order_by(ProcessingJob.created_at.desc(), ProcessingJob.id.desc())
 278 |         .limit(1)
 279 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L268 | Define `_latest_process_job`; bind its arguments when called. The body executes only when invoked. |
| L269 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `target_document_id` with annotation `UUID`. Immutable target UUID retained even when the live document relationship disappears. |
| L270 | Finish/continue the signature; the declared return annotation is `ProcessingJob \| None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L271 | Compute the return value: `session.scalar` with the arguments detailed below — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(ProcessingJob).where(ProcessingJob.target_document_id == target_document_id, ProcessingJob.kind == 'process_document').order_by(ProcessingJob.created_at.desc(), ProcessingJob.id.desc()).limit` with the arguments detailed below — Apply a SQL row limit; fetching limit+1 allows continuation detection; first obtain the receiver: `select(ProcessingJob).where(ProcessingJob.target_document_id == target_document_id, ProcessingJob.kind == 'process_document').order_by` with the arguments detailed below — Set SQL result ordering in the listed priority order. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L272 | `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L273 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L274 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.target_document_id` equals `target_document_id`. |
| L275 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.kind` equals `'process_document'`. |
| L276 | Close the expression/container begun at L272; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L277 | Set SQL result ordering in the listed priority order; apply this method to the result built by the preceding chain. |
| L278 | Apply a SQL row limit; fetching limit+1 allows continuation detection; apply this method to the result built by the preceding chain. |
| L279 | Close the expression/container begun at L271; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `reserve_upload(session, *, owner_user_id, project_id, document_id, appwrite_file_id, file_name, file_size, mime_type, upload_request_id, content_sha256, bucket_id, job_queue) -> tuple[Document, ProcessingJob, bool]`

- **Arguments:** Caller session, verified owner/project IDs, preallocated document/storage IDs, validated filename/bytes metadata/hash/MIME, request key, bucket, and queue adapter.
- **Returns:** `(document, job, is_duplicate)`; the route commits before uploading.
- **Work:** Looks up the request pair. Existing hash mismatch raises `DocumentConflictError`; hashless existing rows compare known size. Finds the latest job; if missing, recreates a reservation using stored document identity. Otherwise returns the existing pair unchanged. For a new upload, inserts a `Pending`, epoch-0 document inside a savepoint. A unique-race loser re-reads the winning document/job, checks its hash when available, and returns it; an unrecoverable collision becomes a conflict or `ValueError`.
- **Before returning a new pair:** Builds the durable storage snapshot, enqueues a process job, ensures an upload-compatible state/stage, and flushes. Ownership, byte parsing, remote upload, and commit are caller responsibilities.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-reserve-upload"></a>

#### Line-by-line execution

[Current source: lines 287–398](../../../../Backend/app/repositories/documents.py#L287-L398). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `owner_user_id` | `UUID`; required; keyword-only | Internal owner UUID copied into the job's durable ownership snapshot. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID`; required; keyword-only | Document UUID; filenames do not establish document identity. |
| `appwrite_file_id` | `str`; required; keyword-only | Caller-supplied appwrite file id; each read, transformation, and validation is traced below. |
| `file_name` | `str`; required; keyword-only | Display PDF filename; immutable IDs establish ownership and evidence identity. |
| `file_size` | `int`; required; keyword-only | PDF size in bytes recorded in document metadata or checked during upload. |
| `mime_type` | `str`; required; keyword-only | Declared storage content type; accepted application uploads use application/pdf. |
| `upload_request_id` | `UUID`; required; keyword-only | Upload request UUID used for per-project idempotency. |
| `content_sha256` | `str`; required; keyword-only | Lowercase SHA-256 content fingerprint used for upload identity/integrity expectations. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `job_queue` | `DirectJobQueue`; required; keyword-only | Caller-supplied job queue; each read, transformation, and validation is traced below. |

**Declared result:** `tuple[Document, ProcessingJob, bool]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 287 | def reserve_upload(
 288 |     session: Session,
 289 |     *,
 290 |     owner_user_id: UUID,
 291 |     project_id: UUID,
 292 |     document_id: UUID,
 293 |     appwrite_file_id: str,
 294 |     file_name: str,
 295 |     file_size: int,
 296 |     mime_type: str,
 297 |     upload_request_id: UUID,
 298 |     content_sha256: str,
 299 |     bucket_id: str,
 300 |     job_queue: DirectJobQueue,
 301 | ) -> tuple[Document, ProcessingJob, bool]:
 302 |     """Create Pending + awaiting_upload atomically, or return the duplicate.
 303 | 
 304 |     Returns ``(document, job, is_duplicate)``.  When ``is_duplicate``
 305 |     is true the caller must verify ``content_sha256`` against the
 306 |     stored fingerprint and return the original pair without touching
 307 |     storage (never resets a running/completed job).  A fingerprint
 308 |     mismatch raises :class:`DocumentConflictError` (``409``).
 309 |     """
 310 |     existing = get_document_by_upload_request(
 311 |         session, project_id=project_id, upload_request_id=upload_request_id
 312 |     )
 313 |     if existing is not None:
 314 |         if existing.content_sha256 is not None and existing.content_sha256 != content_sha256:
 315 |             raise DocumentConflictError(document=existing)
 316 |         if existing.content_sha256 is None and existing.file_size not in (None, file_size):
 317 |             raise DocumentConflictError(document=existing)
 318 |         job = _latest_process_job(session, target_document_id=existing.id)
 319 |         if job is None:
 320 |             # Should not happen (every reservation creates a job), but
 321 |             # never leave a duplicate without its job: recreate the
 322 |             # awaiting_upload reservation for the existing document.
 323 |             job = job_queue.enqueue_job(
 324 |                 session,
 325 |                 owner_user_id=owner_user_id,
 326 |                 project_id=project_id,
 327 |                 target_document_id=existing.id,
 328 |                 document_id=existing.id,
 329 |                 kind="process_document",
 330 |                 target_epoch=existing.processing_epoch,
 331 |                 resource_snapshot=make_resource_snapshot(
 332 |                     bucket_id=bucket_id,
 333 |                     file_id=existing.appwrite_file_id,
 334 |                     file_name=existing.file_name,
 335 |                     file_size=int(existing.file_size or file_size),
 336 |                     content_sha256=content_sha256,
 337 |                 ),
 338 |             )
 339 |             if job.status not in ("awaiting_upload", "queued", "running", "retry_wait"):
 340 |                 job.status = "awaiting_upload"
 341 |             job.stage = "uploading"
 342 |         return existing, job, True
 343 | 
 344 |     document = Document(
 345 |         id=document_id,
 346 |         project_id=project_id,
 347 |         file_name=file_name,
 348 |         appwrite_file_id=appwrite_file_id,
 349 |         file_size=file_size,
 350 |         mime_type=mime_type,
 351 |         status="Pending",
 352 |         upload_request_id=upload_request_id,
 353 |         content_sha256=content_sha256,
 354 |         processing_epoch=0,
 355 |     )
 356 |     try:
 357 |         with session.begin_nested():
 358 |             session.add(document)
 359 |             session.flush()
 360 |     except IntegrityError:
 361 |         # Lost a concurrent reservation race: return the winner
 362 |         # (SAVEPOINT rolls back only this insert).
 363 |         winner = get_document_by_upload_request(
 364 |             session, project_id=project_id, upload_request_id=upload_request_id
 365 |         )
 366 |         if winner is not None:
 367 |             winner_job = _latest_process_job(session, target_document_id=winner.id)
 368 |             if winner_job is not None:
 369 |                 if winner.content_sha256 is not None and winner.content_sha256 != content_sha256:
 370 |                     raise DocumentConflictError(document=winner)
 371 |                 return winner, winner_job, True
 372 |         raise DocumentConflictError(document=winner) if winner is not None else ValueError(
 373 |             "document reservation failed"
 374 |         )
 375 | 
 376 |     job = job_queue.enqueue_job(
 377 |         session,
 378 |         owner_user_id=owner_user_id,
 379 |         project_id=project_id,
 380 |         target_document_id=document.id,
 381 |         document_id=document.id,
 382 |         kind="process_document",
 383 |         target_epoch=document.processing_epoch,
 384 |         resource_snapshot=make_resource_snapshot(
 385 |             bucket_id=bucket_id,
 386 |             file_id=appwrite_file_id,
 387 |             file_name=file_name,
 388 |             file_size=file_size,
 389 |             content_sha256=content_sha256,
 390 |         ),
 391 |     )
 392 |     # Normalize to the upload state regardless of the queue's default
 393 |     # for a fresh row (Protocol-only enqueue guarantees this).
 394 |     if job.status not in ("awaiting_upload", "queued", "running", "retry_wait"):
 395 |         job.status = "awaiting_upload"
 396 |     job.stage = "uploading"
 397 |     session.flush()
 398 |     return document, job, False
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L287 | Define `reserve_upload`; bind its arguments when called. The body executes only when invoked. |
| L288 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L289 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L290 | Declare parameter `owner_user_id` with annotation `UUID`. Internal owner UUID copied into the job's durable ownership snapshot. |
| L291 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L292 | Declare parameter `document_id` with annotation `UUID`. Document UUID; filenames do not establish document identity. |
| L293 | Declare parameter `appwrite_file_id` with annotation `str`. Caller-supplied appwrite file id; its uses and transformations are traced below. |
| L294 | Declare parameter `file_name` with annotation `str`. Display PDF filename; immutable IDs establish ownership and evidence identity. |
| L295 | Declare parameter `file_size` with annotation `int`. PDF size in bytes recorded in document metadata or checked during upload. |
| L296 | Declare parameter `mime_type` with annotation `str`. Declared storage content type; accepted application uploads use application/pdf. |
| L297 | Declare parameter `upload_request_id` with annotation `UUID`. Upload request UUID used for per-project idempotency. |
| L298 | Declare parameter `content_sha256` with annotation `str`. Lowercase SHA-256 content fingerprint used for upload identity/integrity expectations. |
| L299 | Declare parameter `bucket_id` with annotation `str`. Appwrite bucket identifier. |
| L300 | Declare parameter `job_queue` with annotation `DirectJobQueue`. Caller-supplied job queue; its uses and transformations are traced below. |
| L301 | Finish/continue the signature; the declared return annotation is `tuple[Document, ProcessingJob, bool]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L302 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L304 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L305 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L306 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L307 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L308 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L309 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L310 | Evaluate the right-hand side, then bind/store it in `existing`: `get_document_by_upload_request(session, project_id=project_id, upload_request_id=upload_request_id)` — Call [get_document_by_upload_request](#walk-get-document-by-upload-request) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L311 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. Supply `upload_request_id` = `upload_request_id`. Upload request UUID used for per-project idempotency. Evaluate the value as: the current `upload_request_id` value. |
| L312 | Close the expression/container begun at L310; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L313 | Evaluate the branch condition: compare whether `existing` is not the same object as `None`. If truthy, enter L314; otherwise skip this indented block and continue after it. |
| L314 | Evaluate the branch condition: evaluate `existing.content_sha256 is not None and existing.content_sha256 != content_sha256` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L315; otherwise skip this indented block and continue after it. |
| L315 | Raise `DocumentConflictError(document=existing)`; stop the normal path and transfer control to the nearest matching exception handler. |
| L316 | Evaluate the branch condition: evaluate `existing.content_sha256 is None and existing.file_size not in (None, file_size)` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L317; otherwise skip this indented block and continue after it. |
| L317 | Raise `DocumentConflictError(document=existing)`; stop the normal path and transfer control to the nearest matching exception handler. |
| L318 | Evaluate the right-hand side, then bind/store it in `job`: `_latest_process_job(session, target_document_id=existing.id)` — Call [_latest_process_job](#walk--latest-process-job) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L319 | Evaluate the branch condition: compare whether `job` is the same object as `None`. If truthy, enter L323; otherwise skip this indented block and continue after it. |
| L320 | Comment only: Should not happen (every reservation creates a job), but. It does not execute; the neighboring code determines behavior. |
| L321 | Comment only: never leave a duplicate without its job: recreate the. It does not execute; the neighboring code determines behavior. |
| L322 | Comment only: awaiting_upload reservation for the existing document.. It does not execute; the neighboring code determines behavior. |
| L323 | Evaluate the right-hand side, then bind/store it in `job`: `job_queue.enqueue_job` with the arguments detailed below — Enqueue the durable job or return the existing nonterminal target/kind winner, preserving duplicate state. |
| L324 | Supply positional argument 1 to `job_queue.enqueue_job`: the current `session` value. |
| L325 | Supply `owner_user_id` = `owner_user_id`. Internal owner UUID copied into the job's durable ownership snapshot. Evaluate the value as: the current `owner_user_id` value. |
| L326 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L327 | Supply `target_document_id` = `existing.id`. Immutable target UUID retained even when the live document relationship disappears. Evaluate the value as: the `id` attribute of `existing`. |
| L328 | Supply `document_id` = `existing.id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the `id` attribute of `existing`. |
| L329 | Supply `kind` = `'process_document'`.  Evaluate the value as: `'process_document'`. |
| L330 | Supply `target_epoch` = `existing.processing_epoch`. Expected document processing epoch used to invalidate obsolete attempts. Evaluate the value as: the `processing_epoch` attribute of `existing`. |
| L331 | Supply `resource_snapshot` = `make_resource_snapshot(bucket_id=bucket_id, file_id=existing.appwrite_file_id, file_name=existing.file_name, file_size=int(existing.file_size or file_size), content_sha256=content_sha256)`. JSON-compatible resource facts copied into a durable job. Evaluate the value as: `make_resource_snapshot` with the arguments detailed below — Call [make_resource_snapshot](../services/storage.md#walk-make-resource-snapshot) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L332 | Supply `bucket_id` = `bucket_id`. Appwrite bucket identifier. Evaluate the value as: the current `bucket_id` value. |
| L333 | Supply `file_id` = `existing.appwrite_file_id`. Reserved Appwrite storage-object identifier. Evaluate the value as: the `appwrite_file_id` attribute of `existing`. |
| L334 | Supply `file_name` = `existing.file_name`. Display PDF filename; immutable IDs establish ownership and evidence identity. Evaluate the value as: the `file_name` attribute of `existing`. |
| L335 | Supply `file_size` = `int(existing.file_size or file_size)`. PDF size in bytes recorded in document metadata or checked during upload. Evaluate the value as: `int(existing.file_size or file_size)` — Convert the input to an integer (using the optional numeric base). |
| L336 | Supply `content_sha256` = `content_sha256`. Lowercase SHA-256 content fingerprint used for upload identity/integrity expectations. Evaluate the value as: the current `content_sha256` value. |
| L337 | Close the expression/container begun at L331; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L338 | Close the expression/container begun at L323; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L339 | Evaluate the branch condition: compare whether `job.status` is absent from `('awaiting_upload', 'queued', 'running', 'retry_wait')`. If truthy, enter L340; otherwise skip this indented block and continue after it. |
| L340 | Evaluate the right-hand side, then bind/store it in `job.status`: `'awaiting_upload'`. |
| L341 | Evaluate the right-hand side, then bind/store it in `job.stage`: `'uploading'`. |
| L342 | Compute the return value: build a tuple containing `existing`, `job`, `True`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L344 | Evaluate the right-hand side, then bind/store it in `document`: `Document` with the arguments detailed below — Construct `Document` with the shown fields; its class/model initialization rules apply. |
| L345 | Supply `id` = `document_id`.  Evaluate the value as: the current `document_id` value. |
| L346 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L347 | Supply `file_name` = `file_name`. Display PDF filename; immutable IDs establish ownership and evidence identity. Evaluate the value as: the current `file_name` value. |
| L348 | Supply `appwrite_file_id` = `appwrite_file_id`.  Evaluate the value as: the current `appwrite_file_id` value. |
| L349 | Supply `file_size` = `file_size`. PDF size in bytes recorded in document metadata or checked during upload. Evaluate the value as: the current `file_size` value. |
| L350 | Supply `mime_type` = `mime_type`. Declared storage content type; accepted application uploads use application/pdf. Evaluate the value as: the current `mime_type` value. |
| L351 | Supply `status` = `'Pending'`.  Evaluate the value as: `'Pending'`. |
| L352 | Supply `upload_request_id` = `upload_request_id`. Upload request UUID used for per-project idempotency. Evaluate the value as: the current `upload_request_id` value. |
| L353 | Supply `content_sha256` = `content_sha256`. Lowercase SHA-256 content fingerprint used for upload identity/integrity expectations. Evaluate the value as: the current `content_sha256` value. |
| L354 | Supply `processing_epoch` = `0`.  Evaluate the value as: `0`. |
| L355 | Close the expression/container begun at L344; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L356 | Enter the protected block; failures are matched against `IntegrityError` in order. |
| L357 | Enter `session.begin_nested()` — Open a SAVEPOINT after SQLAlchemy's pre-flush; a duplicate-insert failure can roll back this savepoint while preserving the outer transaction. Context exits run in reverse order, including on return/exception. |
| L358 | `session.add(document)` — Attach the ORM object to this session for insertion/update tracking; this does not commit it. The return value is not assigned here. |
| L359 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L360 | Handle `IntegrityError`; only a matching error from the associated try enters this body. |
| L361 | Comment only: Lost a concurrent reservation race: return the winner. It does not execute; the neighboring code determines behavior. |
| L362 | Comment only: (SAVEPOINT rolls back only this insert).. It does not execute; the neighboring code determines behavior. |
| L363 | Evaluate the right-hand side, then bind/store it in `winner`: `get_document_by_upload_request(session, project_id=project_id, upload_request_id=upload_request_id)` — Call [get_document_by_upload_request](#walk-get-document-by-upload-request) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L364 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. Supply `upload_request_id` = `upload_request_id`. Upload request UUID used for per-project idempotency. Evaluate the value as: the current `upload_request_id` value. |
| L365 | Close the expression/container begun at L363; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L366 | Evaluate the branch condition: compare whether `winner` is not the same object as `None`. If truthy, enter L367; otherwise skip this indented block and continue after it. |
| L367 | Evaluate the right-hand side, then bind/store it in `winner_job`: `_latest_process_job(session, target_document_id=winner.id)` — Call [_latest_process_job](#walk--latest-process-job) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L368 | Evaluate the branch condition: compare whether `winner_job` is not the same object as `None`. If truthy, enter L369; otherwise skip this indented block and continue after it. |
| L369 | Evaluate the branch condition: evaluate `winner.content_sha256 is not None and winner.content_sha256 != content_sha256` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L370; otherwise skip this indented block and continue after it. |
| L370 | Raise `DocumentConflictError(document=winner)`; stop the normal path and transfer control to the nearest matching exception handler. |
| L371 | Compute the return value: build a tuple containing `winner`, `winner_job`, `True`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L372 | Raise `DocumentConflictError(document=winner) if winner is not None else ValueError('document reservation failed')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L373 | Supply positional argument 1 to `ValueError`: `'document reservation failed'`. |
| L374 | Close the expression/container begun at L372; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L376 | Evaluate the right-hand side, then bind/store it in `job`: `job_queue.enqueue_job` with the arguments detailed below — Enqueue the durable job or return the existing nonterminal target/kind winner, preserving duplicate state. |
| L377 | Supply positional argument 1 to `job_queue.enqueue_job`: the current `session` value. |
| L378 | Supply `owner_user_id` = `owner_user_id`. Internal owner UUID copied into the job's durable ownership snapshot. Evaluate the value as: the current `owner_user_id` value. |
| L379 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L380 | Supply `target_document_id` = `document.id`. Immutable target UUID retained even when the live document relationship disappears. Evaluate the value as: the `id` attribute of `document`. |
| L381 | Supply `document_id` = `document.id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the `id` attribute of `document`. |
| L382 | Supply `kind` = `'process_document'`.  Evaluate the value as: `'process_document'`. |
| L383 | Supply `target_epoch` = `document.processing_epoch`. Expected document processing epoch used to invalidate obsolete attempts. Evaluate the value as: the `processing_epoch` attribute of `document`. |
| L384 | Supply `resource_snapshot` = `make_resource_snapshot(bucket_id=bucket_id, file_id=appwrite_file_id, file_name=file_name, file_size=file_size, content_sha256=content_sha256)`. JSON-compatible resource facts copied into a durable job. Evaluate the value as: `make_resource_snapshot(bucket_id=bucket_id, file_id=appwrite_file_id, file_name=file_name, file_size=file_size, content_sha256=content_sha256)` — Call [make_resource_snapshot](../services/storage.md#walk-make-resource-snapshot) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L385 | Supply `bucket_id` = `bucket_id`. Appwrite bucket identifier. Evaluate the value as: the current `bucket_id` value. |
| L386 | Supply `file_id` = `appwrite_file_id`. Reserved Appwrite storage-object identifier. Evaluate the value as: the current `appwrite_file_id` value. |
| L387 | Supply `file_name` = `file_name`. Display PDF filename; immutable IDs establish ownership and evidence identity. Evaluate the value as: the current `file_name` value. |
| L388 | Supply `file_size` = `file_size`. PDF size in bytes recorded in document metadata or checked during upload. Evaluate the value as: the current `file_size` value. |
| L389 | Supply `content_sha256` = `content_sha256`. Lowercase SHA-256 content fingerprint used for upload identity/integrity expectations. Evaluate the value as: the current `content_sha256` value. |
| L390 | Close the expression/container begun at L384; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L391 | Close the expression/container begun at L376; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L392 | Comment only: Normalize to the upload state regardless of the queue's default. It does not execute; the neighboring code determines behavior. |
| L393 | Comment only: for a fresh row (Protocol-only enqueue guarantees this).. It does not execute; the neighboring code determines behavior. |
| L394 | Evaluate the branch condition: compare whether `job.status` is absent from `('awaiting_upload', 'queued', 'running', 'retry_wait')`. If truthy, enter L395; otherwise skip this indented block and continue after it. |
| L395 | Evaluate the right-hand side, then bind/store it in `job.status`: `'awaiting_upload'`. |
| L396 | Evaluate the right-hand side, then bind/store it in `job.stage`: `'uploading'`. |
| L397 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L398 | Compute the return value: build a tuple containing `document`, `job`, `False`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `confirm_upload_completion(session, *, document, job) -> bool`

**Arguments:** Session and already-inspected reservation rows. **Returns:** True if this in-memory job was `awaiting_upload`, otherwise false. **Work:** Adds missing upload-completion time, sets `queued`, clears stage, and flushes. It does not inspect storage, lock/re-read rows, or execute a compare-and-set SQL update itself.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-confirm-upload-completion"></a>

#### Line-by-line execution

[Current source: lines 401–423](../../../../Backend/app/repositories/documents.py#L401-L423). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `document` | `Document`; required; keyword-only | Caller-supplied document; each read, transformation, and validation is traced below. |
| `job` | `ProcessingJob`; required; keyword-only | Caller-supplied job; each read, transformation, and validation is traced below. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 401 | def confirm_upload_completion(
 402 |     session: Session,
 403 |     *,
 404 |     document: Document,
 405 |     job: ProcessingJob,
 406 | ) -> bool:
 407 |     """Conditionally queue a storage-complete upload.
 408 | 
 409 |     Sets ``document.upload_completed_at`` and moves the job
 410 |     ``awaiting_upload -> queued`` *only* while the job is still
 411 |     ``awaiting_upload``.  A job already ``queued`` (reconciliation
 412 |     race) or terminal is left untouched.  Returns True when this call
 413 |     performed the transition.
 414 |     """
 415 |     if job.status != "awaiting_upload":
 416 |         return False
 417 |     now = _utcnow()
 418 |     if document.upload_completed_at is None:
 419 |         document.upload_completed_at = now
 420 |     job.status = "queued"
 421 |     job.stage = None
 422 |     session.flush()
 423 |     return True
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L401 | Define `confirm_upload_completion`; bind its arguments when called. The body executes only when invoked. |
| L402 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L403 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L404 | Declare parameter `document` with annotation `Document`. Caller-supplied document; its uses and transformations are traced below. |
| L405 | Declare parameter `job` with annotation `ProcessingJob`. Caller-supplied job; its uses and transformations are traced below. |
| L406 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L407 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L409 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L410 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L411 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L412 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L413 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L414 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L415 | Evaluate the branch condition: compare whether `job.status` differs from `'awaiting_upload'`. If truthy, enter L416; otherwise skip this indented block and continue after it. |
| L416 | Compute the return value: `False`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L417 | Evaluate the right-hand side, then bind/store it in `now`: `_utcnow()` — Read the module's current UTC timestamp helper. |
| L418 | Evaluate the branch condition: compare whether `document.upload_completed_at` is the same object as `None`. If truthy, enter L419; otherwise skip this indented block and continue after it. |
| L419 | Evaluate the right-hand side, then bind/store it in `document.upload_completed_at`: the current `now` value. |
| L420 | Evaluate the right-hand side, then bind/store it in `job.status`: `'queued'`. |
| L421 | Evaluate the right-hand side, then bind/store it in `job.stage`: None (no value). |
| L422 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L423 | Compute the return value: `True`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `prepare_document_retry(session, *, document, bucket_id: str, job_queue) -> tuple[Document, ProcessingJob]`

**Arguments:** Session, caller-validated failed document, bucket, queue. **Returns:** Reset document and new queued process job. **Work:** Cancels active process jobs, increments epoch, sets `Pending`, clears processing error, fills missing upload time, and flushes. Resolves owner from the project, snapshots current storage metadata, enqueues for the new epoch, sets queued/no stage, and flushes. Existing failed history remains; eligibility is checked in the route.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-prepare-document-retry"></a>

#### Line-by-line execution

[Current source: lines 426–472](../../../../Backend/app/repositories/documents.py#L426-L472). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `document` | `Document`; required; keyword-only | Caller-supplied document; each read, transformation, and validation is traced below. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `job_queue` | `DirectJobQueue`; required; keyword-only | Caller-supplied job queue; each read, transformation, and validation is traced below. |

**Declared result:** `tuple[Document, ProcessingJob]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 426 | def prepare_document_retry(
 427 |     session: Session,
 428 |     *,
 429 |     document: Document,
 430 |     bucket_id: str,
 431 |     job_queue: DirectJobQueue,
 432 | ) -> tuple[Document, ProcessingJob]:
 433 |     """Create a fresh queued job for a Failed document and advance its epoch.
 434 | 
 435 |     Caller must have verified eligibility (document ``Failed`` + no
 436 |     nonterminal job).  The failed history stays terminal; attempt
 437 |     history is preserved by leaving old rows untouched.
 438 |     """
 439 |     # Fresh snapshot from the live document (file already in storage).
 440 |     # Enqueue uses Protocol-only args so any JobQueue implementation
 441 |     # works; the queued state is set on the returned row below.
 442 |     cancel_process_jobs(session, document_id=document.id, reason="retry epoch advance")
 443 |     document.processing_epoch = int(document.processing_epoch or 0) + 1
 444 |     document.status = "Pending"
 445 |     document.processing_error = None
 446 |     if document.upload_completed_at is None:
 447 |         document.upload_completed_at = _utcnow()
 448 |     session.flush()
 449 |     job = job_queue.enqueue_job(
 450 |         session,
 451 |         owner_user_id=_job_owner(session, document),
 452 |         project_id=document.project_id,
 453 |         target_document_id=document.id,
 454 |         document_id=document.id,
 455 |         kind="process_document",
 456 |         target_epoch=document.processing_epoch,
 457 |         resource_snapshot=make_resource_snapshot(
 458 |             bucket_id=bucket_id,
 459 |             file_id=document.appwrite_file_id,
 460 |             file_name=document.file_name,
 461 |             file_size=int(document.file_size or 0),
 462 |             content_sha256=str(document.content_sha256 or ""),
 463 |         ),
 464 |     )
 465 |     # Force the retry state regardless of the queue's default for a
 466 |     # fresh row (no nonterminal exists by eligibility, so this never
 467 |     # downgrades an active job).
 468 |     if job.status not in ("queued",):
 469 |         job.status = "queued"
 470 |     job.stage = None
 471 |     session.flush()
 472 |     return document, job
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L426 | Define `prepare_document_retry`; bind its arguments when called. The body executes only when invoked. |
| L427 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L428 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L429 | Declare parameter `document` with annotation `Document`. Caller-supplied document; its uses and transformations are traced below. |
| L430 | Declare parameter `bucket_id` with annotation `str`. Appwrite bucket identifier. |
| L431 | Declare parameter `job_queue` with annotation `DirectJobQueue`. Caller-supplied job queue; its uses and transformations are traced below. |
| L432 | Finish/continue the signature; the declared return annotation is `tuple[Document, ProcessingJob]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L433 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L435 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L436 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L437 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L438 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L439 | Comment only: Fresh snapshot from the live document (file already in storage).. It does not execute; the neighboring code determines behavior. |
| L440 | Comment only: Enqueue uses Protocol-only args so any JobQueue implementation. It does not execute; the neighboring code determines behavior. |
| L441 | Comment only: works; the queued state is set on the returned row below.. It does not execute; the neighboring code determines behavior. |
| L442 | `cancel_process_jobs(session, document_id=document.id, reason='retry epoch advance')` — Call [cancel_process_jobs](#walk-cancel-process-jobs) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L443 | Evaluate the right-hand side, then bind/store it in `document.processing_epoch`: add/concatenate `int(document.processing_epoch or 0)` and `1`, following the parentheses/operator precedence shown in `int(document.processing_epoch or 0) + 1`. |
| L444 | Evaluate the right-hand side, then bind/store it in `document.status`: `'Pending'`. |
| L445 | Evaluate the right-hand side, then bind/store it in `document.processing_error`: None (no value). |
| L446 | Evaluate the branch condition: compare whether `document.upload_completed_at` is the same object as `None`. If truthy, enter L447; otherwise skip this indented block and continue after it. |
| L447 | Evaluate the right-hand side, then bind/store it in `document.upload_completed_at`: `_utcnow()` — Read the module's current UTC timestamp helper. |
| L448 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L449 | Evaluate the right-hand side, then bind/store it in `job`: `job_queue.enqueue_job` with the arguments detailed below — Enqueue the durable job or return the existing nonterminal target/kind winner, preserving duplicate state. |
| L450 | Supply positional argument 1 to `job_queue.enqueue_job`: the current `session` value. |
| L451 | Supply `owner_user_id` = `_job_owner(session, document)`. Internal owner UUID copied into the job's durable ownership snapshot. Evaluate the value as: `_job_owner(session, document)` — Call [_job_owner](#walk--job-owner) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L452 | Supply `project_id` = `document.project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the `project_id` attribute of `document`. |
| L453 | Supply `target_document_id` = `document.id`. Immutable target UUID retained even when the live document relationship disappears. Evaluate the value as: the `id` attribute of `document`. |
| L454 | Supply `document_id` = `document.id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the `id` attribute of `document`. |
| L455 | Supply `kind` = `'process_document'`.  Evaluate the value as: `'process_document'`. |
| L456 | Supply `target_epoch` = `document.processing_epoch`. Expected document processing epoch used to invalidate obsolete attempts. Evaluate the value as: the `processing_epoch` attribute of `document`. |
| L457 | Supply `resource_snapshot` = `make_resource_snapshot(bucket_id=bucket_id, file_id=document.appwrite_file_id, file_name=document.file_name, file_size=int(document.file_size or 0), content_sha256=str(document.content_sha256 or ''))`. JSON-compatible resource facts copied into a durable job. Evaluate the value as: `make_resource_snapshot` with the arguments detailed below — Call [make_resource_snapshot](../services/storage.md#walk-make-resource-snapshot) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L458 | Supply `bucket_id` = `bucket_id`. Appwrite bucket identifier. Evaluate the value as: the current `bucket_id` value. |
| L459 | Supply `file_id` = `document.appwrite_file_id`. Reserved Appwrite storage-object identifier. Evaluate the value as: the `appwrite_file_id` attribute of `document`. |
| L460 | Supply `file_name` = `document.file_name`. Display PDF filename; immutable IDs establish ownership and evidence identity. Evaluate the value as: the `file_name` attribute of `document`. |
| L461 | Supply `file_size` = `int(document.file_size or 0)`. PDF size in bytes recorded in document metadata or checked during upload. Evaluate the value as: `int(document.file_size or 0)` — Convert the input to an integer (using the optional numeric base). |
| L462 | Supply `content_sha256` = `str(document.content_sha256 or '')`. Lowercase SHA-256 content fingerprint used for upload identity/integrity expectations. Evaluate the value as: `str(document.content_sha256 or '')` — Convert the input to its string representation. |
| L463 | Close the expression/container begun at L457; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L464 | Close the expression/container begun at L449; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L465 | Comment only: Force the retry state regardless of the queue's default for a. It does not execute; the neighboring code determines behavior. |
| L466 | Comment only: fresh row (no nonterminal exists by eligibility, so this never. It does not execute; the neighboring code determines behavior. |
| L467 | Comment only: downgrades an active job).. It does not execute; the neighboring code determines behavior. |
| L468 | Evaluate the branch condition: compare whether `job.status` is absent from `('queued',)`. If truthy, enter L469; otherwise skip this indented block and continue after it. |
| L469 | Evaluate the right-hand side, then bind/store it in `job.status`: `'queued'`. |
| L470 | Evaluate the right-hand side, then bind/store it in `job.stage`: None (no value). |
| L471 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L472 | Compute the return value: build a tuple containing `document`, `job`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_job_owner(session, document: Document) -> UUID`

**Arguments:** Session and document. **Returns:** Its project's internal owner UUID. **Work:** Selects `Project.user_id` without a tombstone filter so cleanup can work on deleted parents; missing parent raises `ValueError`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--job-owner"></a>

#### Line-by-line execution

[Current source: lines 475–488](../../../../Backend/app/repositories/documents.py#L475-L488). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `document` | `Document`; required; positional or keyword | Caller-supplied document; each read, transformation, and validation is traced below. |

**Declared result:** `UUID`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 475 | def _job_owner(session: Session, document: Document) -> UUID:
 476 |     """Resolve ``owner_user_id`` from the document's project row.
 477 | 
 478 |     Works for live and tombstoned parents (no deleted filter) so
 479 |     retry/delete snapshots stay owner-correct during cleanup.
 480 |     """
 481 |     from app.db.models import Project as _Project
 482 | 
 483 |     owner = session.scalar(
 484 |         select(_Project.user_id).where(_Project.id == document.project_id)
 485 |     )
 486 |     if owner is None:
 487 |         raise ValueError(f"project not found for document {document.id}")
 488 |     return owner
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L475 | Define `_job_owner`; bind its arguments when called. The body executes only when invoked. |
| L476 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L478 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L479 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L480 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L481 | Import `Project` as `_Project` from `app.db.models`; inside a function this import is deferred until this path is reached. |
| L483 | Evaluate the right-hand side, then bind/store it in `owner`: `session.scalar(select(_Project.user_id).where(_Project.id == document.project_id))` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(_Project.user_id).where(_Project.id == document.project_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(_Project.user_id)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L484 | `select(_Project.user_id).where(_Project.id == document.project_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(_Project.user_id)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L485 | Close the expression/container begun at L483; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L486 | Evaluate the branch condition: compare whether `owner` is the same object as `None`. If truthy, enter L487; otherwise skip this indented block and continue after it. |
| L487 | Raise `ValueError(f'project not found for document {document.id}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L488 | Compute the return value: the current `owner` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `tombstone_document(session, document, *, now: datetime | None = None) -> Document`

**Arguments:** Session, document, optional time. **Returns:** Same document. **Work:** Sets `deleted_at` once and flushes. It does not itself increment `processing_epoch`, cancel jobs, or delete provider objects.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-tombstone-document"></a>

#### Line-by-line execution

[Current source: lines 491–497](../../../../Backend/app/repositories/documents.py#L491-L497). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `document` | `Document`; required; positional or keyword | Caller-supplied document; each read, transformation, and validation is traced below. |
| `now` | `datetime \| None`; default `None`; keyword-only | Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |

**Declared result:** `Document`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 491 | def tombstone_document(
 492 |     session: Session, document: Document, *, now: datetime | None = None
 493 | ) -> Document:
 494 |     if document.deleted_at is None:
 495 |         document.deleted_at = now or _utcnow()
 496 |     session.flush()
 497 |     return document
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L491 | Define `tombstone_document`; bind its arguments when called. The body executes only when invoked. |
| L492 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `document` with annotation `Document`. Caller-supplied document; its uses and transformations are traced below. Declare parameter `now` with annotation `datetime \| None`. Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |
| L493 | Finish/continue the signature; the declared return annotation is `Document`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L494 | Evaluate the branch condition: compare whether `document.deleted_at` is the same object as `None`. If truthy, enter L495; otherwise skip this indented block and continue after it. |
| L495 | Evaluate the right-hand side, then bind/store it in `document.deleted_at`: evaluate `now or _utcnow()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L496 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L497 | Compute the return value: the current `document` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `enqueue_document_delete(session, *, document, bucket_id: str, job_queue) -> ProcessingJob`

**Arguments:** Session, document (normally already tombstoned), bucket, queue. **Returns:** Cleanup job. **Work:** Cancels process jobs; snapshots file metadata and any active index version; resolves owner; enqueues `delete_document` at the document's current epoch. When the returned kind matches, sets `queued`/`deleting` and flushes. This layer does not enumerate every historical index version; other cleanup/sweep paths handle obsolete namespaces.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-enqueue-document-delete"></a>

#### Line-by-line execution

[Current source: lines 500–536](../../../../Backend/app/repositories/documents.py#L500-L536). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `document` | `Document`; required; keyword-only | Caller-supplied document; each read, transformation, and validation is traced below. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `job_queue` | `DirectJobQueue`; required; keyword-only | Caller-supplied job queue; each read, transformation, and validation is traced below. |

**Declared result:** `ProcessingJob`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 500 | def enqueue_document_delete(
 501 |     session: Session,
 502 |     *,
 503 |     document: Document,
 504 |     bucket_id: str,
 505 |     job_queue: DirectJobQueue,
 506 | ) -> ProcessingJob:
 507 |     """Cancel processing + enqueue the ``delete_document`` cleanup job."""
 508 |     cancel_process_jobs(session, document_id=document.id, reason="document deleted")
 509 |     snapshot = make_resource_snapshot(
 510 |         bucket_id=bucket_id,
 511 |         file_id=document.appwrite_file_id,
 512 |         file_name=document.file_name,
 513 |         file_size=int(document.file_size or 0),
 514 |         content_sha256=str(document.content_sha256 or ""),
 515 |         active_index_version=(
 516 |             str(document.active_index_version)
 517 |             if document.active_index_version is not None
 518 |             else None
 519 |         ),
 520 |     )
 521 |     delete_job = job_queue.enqueue_job(
 522 |         session,
 523 |         owner_user_id=_job_owner(session, document),
 524 |         project_id=document.project_id,
 525 |         target_document_id=document.id,
 526 |         document_id=document.id,
 527 |         kind="delete_document",
 528 |         target_epoch=int(document.processing_epoch or 0),
 529 |         resource_snapshot=snapshot,
 530 |     )
 531 |     # Normalize to the cleanup state (Protocol-only enqueue args).
 532 |     if delete_job.kind == "delete_document":
 533 |         delete_job.status = "queued"
 534 |         delete_job.stage = "deleting"
 535 |     session.flush()
 536 |     return delete_job
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L500 | Define `enqueue_document_delete`; bind its arguments when called. The body executes only when invoked. |
| L501 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L502 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L503 | Declare parameter `document` with annotation `Document`. Caller-supplied document; its uses and transformations are traced below. |
| L504 | Declare parameter `bucket_id` with annotation `str`. Appwrite bucket identifier. |
| L505 | Declare parameter `job_queue` with annotation `DirectJobQueue`. Caller-supplied job queue; its uses and transformations are traced below. |
| L506 | Finish/continue the signature; the declared return annotation is `ProcessingJob`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L507 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L508 | `cancel_process_jobs(session, document_id=document.id, reason='document deleted')` — Call [cancel_process_jobs](#walk-cancel-process-jobs) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L509 | Evaluate the right-hand side, then bind/store it in `snapshot`: `make_resource_snapshot` with the arguments detailed below — Call [make_resource_snapshot](../services/storage.md#walk-make-resource-snapshot) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L510 | Supply `bucket_id` = `bucket_id`. Appwrite bucket identifier. Evaluate the value as: the current `bucket_id` value. |
| L511 | Supply `file_id` = `document.appwrite_file_id`. Reserved Appwrite storage-object identifier. Evaluate the value as: the `appwrite_file_id` attribute of `document`. |
| L512 | Supply `file_name` = `document.file_name`. Display PDF filename; immutable IDs establish ownership and evidence identity. Evaluate the value as: the `file_name` attribute of `document`. |
| L513 | Supply `file_size` = `int(document.file_size or 0)`. PDF size in bytes recorded in document metadata or checked during upload. Evaluate the value as: `int(document.file_size or 0)` — Convert the input to an integer (using the optional numeric base). |
| L514 | Supply `content_sha256` = `str(document.content_sha256 or '')`. Lowercase SHA-256 content fingerprint used for upload identity/integrity expectations. Evaluate the value as: `str(document.content_sha256 or '')` — Convert the input to its string representation. |
| L515 | Supply `active_index_version` = `str(document.active_index_version) if document.active_index_version is not None else None`.  Evaluate the value as: check `document.active_index_version is not None`; when true use `str(document.active_index_version)` — Convert the input to its string representation, otherwise None (no value) (only the selected branch is evaluated). |
| L516 | `str(document.active_index_version)` — Convert the input to its string representation. |
| L517 | Continue the enclosing expression: compare whether `document.active_index_version` is not the same object as `None`. |
| L518 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L519 | Close the expression/container begun at L509; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L520 | Close the expression/container begun at L509; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L521 | Evaluate the right-hand side, then bind/store it in `delete_job`: `job_queue.enqueue_job` with the arguments detailed below — Enqueue the durable job or return the existing nonterminal target/kind winner, preserving duplicate state. |
| L522 | Supply positional argument 1 to `job_queue.enqueue_job`: the current `session` value. |
| L523 | Supply `owner_user_id` = `_job_owner(session, document)`. Internal owner UUID copied into the job's durable ownership snapshot. Evaluate the value as: `_job_owner(session, document)` — Call [_job_owner](#walk--job-owner) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L524 | Supply `project_id` = `document.project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the `project_id` attribute of `document`. |
| L525 | Supply `target_document_id` = `document.id`. Immutable target UUID retained even when the live document relationship disappears. Evaluate the value as: the `id` attribute of `document`. |
| L526 | Supply `document_id` = `document.id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the `id` attribute of `document`. |
| L527 | Supply `kind` = `'delete_document'`.  Evaluate the value as: `'delete_document'`. |
| L528 | Supply `target_epoch` = `int(document.processing_epoch or 0)`. Expected document processing epoch used to invalidate obsolete attempts. Evaluate the value as: `int(document.processing_epoch or 0)` — Convert the input to an integer (using the optional numeric base). |
| L529 | Supply `resource_snapshot` = `snapshot`. JSON-compatible resource facts copied into a durable job. Evaluate the value as: the current `snapshot` value. |
| L530 | Close the expression/container begun at L521; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L531 | Comment only: Normalize to the cleanup state (Protocol-only enqueue args).. It does not execute; the neighboring code determines behavior. |
| L532 | Evaluate the branch condition: compare whether `delete_job.kind` equals `'delete_document'`. If truthy, enter L533; otherwise skip this indented block and continue after it. |
| L533 | Evaluate the right-hand side, then bind/store it in `delete_job.status`: `'queued'`. |
| L534 | Evaluate the right-hand side, then bind/store it in `delete_job.stage`: `'deleting'`. |
| L535 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L536 | Compute the return value: the current `delete_job` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

## Lists and reconciliation reads

### `_parse_doc_cursor(cursor: str) -> tuple[datetime, UUID]`

**Arguments:** Encoded document cursor. **Returns:** Creation timestamp and document UUID. **Work:** Requires string `c`/`i`, parses ISO time and UUID, attaches UTC to naive time, and converts parse failures to structured 422.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--parse-doc-cursor"></a>

#### Line-by-line execution

[Current source: lines 544–560](../../../../Backend/app/repositories/documents.py#L544-L560). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `cursor` | `str`; required; positional or keyword | Opaque page continuation token; null starts the first page. |

**Declared result:** `tuple[datetime, UUID]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 544 | def _parse_doc_cursor(cursor: str) -> tuple[datetime, UUID]:
 545 |     try:
 546 |         payload = decode_cursor(cursor)
 547 |         created_raw = payload.get("c")
 548 |         id_raw = payload.get("i")
 549 |         if not isinstance(created_raw, str) or not isinstance(id_raw, str):
 550 |             raise ValueError("malformed cursor payload")
 551 |         created_at = datetime.fromisoformat(created_raw)
 552 |         if created_at.tzinfo is None:
 553 |             created_at = created_at.replace(tzinfo=timezone.utc)
 554 |         document_id = UUID(id_raw)
 555 |     except (ValueError, TypeError) as exc:
 556 |         _raise_api(
 557 |             422, ErrorCode.VALIDATION_ERROR, "Invalid pagination cursor."
 558 |         )
 559 |         raise exc  # pragma: no cover
 560 |     return created_at, document_id
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L544 | Define `_parse_doc_cursor`; bind its arguments when called. The body executes only when invoked. |
| L545 | Enter the protected block; failures are matched against `(ValueError, TypeError)` in order. |
| L546 | Evaluate the right-hand side, then bind/store it in `payload`: `decode_cursor(cursor)` — Call [decode_cursor](../schemas/common.md#walk-decode-cursor) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L547 | Evaluate the right-hand side, then bind/store it in `created_raw`: `payload.get('c')` — Look up `'c'` in `payload`, using None when the key is absent (an existing null value is not replaced). |
| L548 | Evaluate the right-hand side, then bind/store it in `id_raw`: `payload.get('i')` — Look up `'i'` in `payload`, using None when the key is absent (an existing null value is not replaced). |
| L549 | Evaluate the branch condition: evaluate `not isinstance(created_raw, str) or not isinstance(id_raw, str)` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L550; otherwise skip this indented block and continue after it. |
| L550 | Raise `ValueError('malformed cursor payload')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L551 | Evaluate the right-hand side, then bind/store it in `created_at`: `datetime.fromisoformat(created_raw)` — Parse an ISO-format timestamp; invalid text raises ValueError. |
| L552 | Evaluate the branch condition: compare whether `created_at.tzinfo` is the same object as `None`. If truthy, enter L553; otherwise skip this indented block and continue after it. |
| L553 | Evaluate the right-hand side, then bind/store it in `created_at`: `created_at.replace(tzinfo=timezone.utc)` — Return a value with the specified replacements applied. |
| L554 | Evaluate the right-hand side, then bind/store it in `document_id`: `UUID(id_raw)` — Parse or construct a UUID; invalid text raises a conversion error. |
| L555 | Handle `(ValueError, TypeError)` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L556 | `_raise_api(422, ErrorCode.VALIDATION_ERROR, 'Invalid pagination cursor.')` — Call [_raise_api](#walk--raise-api) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L557 | Supply positional argument 1 to `_raise_api`: `422`. |
| L558 | Close the expression/container begun at L556; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L559 | Raise `exc`; stop the normal path and transfer control to the nearest matching exception handler. |
| L560 | Compute the return value: build a tuple containing `created_at`, `document_id`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `list_owned_documents(session, *, user_id, project_id, cursor: str | None, limit: int) -> tuple[list[Document], str | None]`

**Arguments:** Session, owner/project UUIDs, cursor, size. **Returns:** Live document page plus continuation. **Work:** Enforces 1–200 and live project ownership, filters live documents, sorts `created_at DESC, id DESC`, applies a strict lexicographic cursor boundary, fetches one extra row, and encodes the last returned row only when more exist.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-list-owned-documents"></a>

#### Line-by-line execution

[Current source: lines 563–617](../../../../Backend/app/repositories/documents.py#L563-L617). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `cursor` | `str \| None`; required; keyword-only | Opaque page continuation token; null starts the first page. |
| `limit` | `int`; required; keyword-only | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |

**Declared result:** `tuple[list[Document], str | None]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 563 | def list_owned_documents(
 564 |     session: Session,
 565 |     *,
 566 |     user_id: UUID,
 567 |     project_id: UUID,
 568 |     cursor: str | None,
 569 |     limit: int,
 570 | ) -> tuple[list[Document], str | None]:
 571 |     """Live documents of an owned project, newest-first, keyset-paginated.
 572 | 
 573 |     Callers verify project ownership first (this helper assumes it).
 574 |     Malformed cursors raise ``422 validation_error``.
 575 |     """
 576 |     if limit < 1 or limit > 200:
 577 |         _raise_api(
 578 |             422, ErrorCode.VALIDATION_ERROR, "limit must be between 1 and 200."
 579 |         )
 580 |     # Ownership guard (documents -> project -> user) via live project.
 581 |     project = _get_owned_project(
 582 |         session, user_id=user_id, project_id=project_id, include_deleted=False
 583 |     )
 584 |     if project is None:
 585 |         _raise_api(
 586 |             404,
 587 |             ErrorCode.NOT_FOUND,
 588 |             "Project not found.",
 589 |             project_id=project_id,
 590 |         )
 591 | 
 592 |     statement = (
 593 |         select(Document)
 594 |         .where(
 595 |             Document.project_id == project_id,
 596 |             Document.deleted_at.is_(None),
 597 |         )
 598 |         .order_by(Document.created_at.desc(), Document.id.desc())
 599 |         .limit(limit + 1)
 600 |     )
 601 |     if cursor is not None:
 602 |         created_before, id_before = _parse_doc_cursor(cursor)
 603 |         statement = statement.where(
 604 |             or_(
 605 |                 Document.created_at < created_before,
 606 |                 (Document.created_at == created_before) & (Document.id < id_before),
 607 |             )
 608 |         )
 609 |     rows = list(session.execute(statement).scalars().all())
 610 |     next_cursor: str | None = None
 611 |     if len(rows) > limit:
 612 |         rows = rows[:limit]
 613 |         last = rows[-1]
 614 |         next_cursor = encode_cursor(
 615 |             {"c": last.created_at.isoformat(), "i": str(last.id)}
 616 |         )
 617 |     return rows, next_cursor
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L563 | Define `list_owned_documents`; bind its arguments when called. The body executes only when invoked. |
| L564 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L565 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L566 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L567 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L568 | Declare parameter `cursor` with annotation `str \| None`. Opaque page continuation token; null starts the first page. |
| L569 | Declare parameter `limit` with annotation `int`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. |
| L570 | Finish/continue the signature; the declared return annotation is `tuple[list[Document], str \| None]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L571 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L573 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L574 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L575 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L576 | Evaluate the branch condition: evaluate `limit < 1 or limit > 200` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L577; otherwise skip this indented block and continue after it. |
| L577 | `_raise_api(422, ErrorCode.VALIDATION_ERROR, 'limit must be between 1 and 200.')` — Call [_raise_api](#walk--raise-api) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L578 | Supply positional argument 1 to `_raise_api`: `422`. |
| L579 | Close the expression/container begun at L577; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L580 | Comment only: Ownership guard (documents -> project -> user) via live project.. It does not execute; the neighboring code determines behavior. |
| L581 | Evaluate the right-hand side, then bind/store it in `project`: `_get_owned_project(session, user_id=user_id, project_id=project_id, include_deleted=False)` — Call [_get_owned_project](#walk--get-owned-project) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L582 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. Supply `include_deleted` = `False`. Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. Evaluate the value as: `False`. |
| L583 | Close the expression/container begun at L581; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L584 | Evaluate the branch condition: compare whether `project` is the same object as `None`. If truthy, enter L585; otherwise skip this indented block and continue after it. |
| L585 | `_raise_api(404, ErrorCode.NOT_FOUND, 'Project not found.', project_id=project_id)` — Call [_raise_api](#walk--raise-api) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L586 | Supply positional argument 1 to `_raise_api`: `404`. |
| L587 | Supply positional argument 2 to `_raise_api`: the `NOT_FOUND` attribute of `ErrorCode`. |
| L588 | Supply positional argument 3 to `_raise_api`: `'Project not found.'`. |
| L589 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L590 | Close the expression/container begun at L585; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L592 | Evaluate the right-hand side, then bind/store it in `statement`: `select(Document).where(Document.project_id == project_id, Document.deleted_at.is_(None)).order_by(Document.created_at.desc(), Document.id.desc()).limit` with the arguments detailed below — Apply a SQL row limit; fetching limit+1 allows continuation detection; first obtain the receiver: `select(Document).where(Document.project_id == project_id, Document.deleted_at.is_(None)).order_by(Document.created_at.desc(), Document.id.desc())` — Set SQL result ordering in the listed priority order; first obtain the receiver: `select(Document).where(Document.project_id == project_id, Document.deleted_at.is_(None))` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; inputs include add/concatenate `limit` and `1`, following the parentheses/operator precedence shown in `limit + 1`. |
| L593 | `select(Document)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L594 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L595 | Continue the enclosing expression: build a SQL predicate requiring `Document.project_id` equals `project_id`. |
| L596 | `Document.deleted_at.is_(None)` — Build an SQL IS predicate, commonly IS NULL for a live-row filter. |
| L597 | Close the expression/container begun at L593; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L598 | Set SQL result ordering in the listed priority order; apply this method to the result built by the preceding chain. |
| L599 | Apply a SQL row limit; fetching limit+1 allows continuation detection; apply this method to the result built by the preceding chain. |
| L600 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L601 | Evaluate the branch condition: compare whether `cursor` is not the same object as `None`. If truthy, enter L602; otherwise skip this indented block and continue after it. |
| L602 | Evaluate the right-hand side, then bind/store it in `(created_before, id_before)`: `_parse_doc_cursor(cursor)` — Call [_parse_doc_cursor](#walk--parse-doc-cursor) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L603 | Evaluate the right-hand side, then bind/store it in `statement`: `statement.where(or_(Document.created_at < created_before, (Document.created_at == created_before) & (Document.id < id_before)))` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; inputs include `or_(Document.created_at < created_before, (Document.created_at == created_before) & (Document.id < id_before))` — Combine SQL predicates with OR so at least one condition must hold. |
| L604 | `or_(Document.created_at < created_before, (Document.created_at == created_before) & (Document.id < id_before))` — Combine SQL predicates with OR so at least one condition must hold; inputs include combine with & `Document.created_at == created_before` and `Document.id < id_before`, following the parentheses/operator precedence shown in `(Document.created_at == created_before) & (Document.id < id_before)`. |
| L605 | Continue the enclosing expression: build a SQL predicate requiring `Document.created_at` is less than `created_before`. |
| L606 | Continue the enclosing expression: combine with & `Document.created_at == created_before` and `Document.id < id_before`, following the parentheses/operator precedence shown in `(Document.created_at == created_before) & (Document.id < id_before)`. |
| L607 | Close the expression/container begun at L604; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L608 | Close the expression/container begun at L603; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L609 | Evaluate the right-hand side, then bind/store it in `rows`: `list(session.execute(statement).scalars().all())` — Materialize the iterable in order into a list (or create an empty list); inputs include `session.execute(statement).scalars().all()` — Materialize all remaining values in this SQL result; first obtain the receiver: `session.execute(statement).scalars()` — Expose only the first selected column from each row of the SQL result. |
| L610 | Evaluate the right-hand side, then bind/store it in `next_cursor`: None (no value). |
| L611 | Evaluate the branch condition: compare whether `len(rows)` is greater than `limit`. If truthy, enter L612; otherwise skip this indented block and continue after it. |
| L612 | Evaluate the right-hand side, then bind/store it in `rows`: slice `rows` from the beginning up to `limit` (exclusive stop). |
| L613 | Evaluate the right-hand side, then bind/store it in `last`: look up index/key `-1` in `rows`; a missing key or out-of-range index raises. |
| L614 | Evaluate the right-hand side, then bind/store it in `next_cursor`: `encode_cursor({'c': last.created_at.isoformat(), 'i': str(last.id)})` — Call [encode_cursor](../schemas/common.md#walk-encode-cursor) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L615 | Add mapping entry `'c'`: `last.created_at.isoformat()` — Format the timestamp/date as an ISO-format string for the cursor/payload. Add mapping entry `'i'`: `str(last.id)` — Convert the input to its string representation. |
| L616 | Close the expression/container begun at L614; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L617 | Compute the return value: build a tuple containing `rows`, `next_cursor`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `list_live_documents_for_project(session, *, project_id) -> list[Document]`

**Arguments:** Session and already-authorized project ID. **Returns:** All non-tombstoned documents oldest-first (`created_at`, then ID ascending). **Work:** Executes the filtered unpaginated cleanup enumeration; no independent ownership check.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-list-live-documents-for-project"></a>

#### Line-by-line execution

[Current source: lines 620–633](../../../../Backend/app/repositories/documents.py#L620-L633). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |

**Declared result:** `list[Document]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 620 | def list_live_documents_for_project(
 621 |     session: Session, *, project_id: UUID
 622 | ) -> list[Document]:
 623 |     """All live documents of a project (cleanup enumeration)."""
 624 |     return list(
 625 |         session.execute(
 626 |             select(Document)
 627 |             .where(
 628 |                 Document.project_id == project_id,
 629 |                 Document.deleted_at.is_(None),
 630 |             )
 631 |             .order_by(Document.created_at.asc(), Document.id.asc())
 632 |         ).scalars().all()
 633 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L620 | Define `list_live_documents_for_project`; bind its arguments when called. The body executes only when invoked. |
| L621 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L622 | Finish/continue the signature; the declared return annotation is `list[Document]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L623 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L624 | Compute the return value: `list` with the arguments detailed below — Materialize the iterable in order into a list (or create an empty list); inputs include `session.execute(select(Document).where(Document.project_id == project_id, Document.deleted_at.is_(None)).order_by(Document.created_at.asc(), Document.id.asc())).scalars().all` with the arguments detailed below — Materialize all remaining values in this SQL result; first obtain the receiver: `session.execute(select(Document).where(Document.project_id == project_id, Document.deleted_at.is_(None)).order_by(Document.created_at.asc(), Document.id.asc())).scalars` with the arguments detailed below — Expose only the first selected column from each row of the SQL result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L625 | `session.execute` with the arguments detailed below — Execute the SQL statement in the current transaction and return its Result (including rowcount for guarded updates); inputs include `select(Document).where(Document.project_id == project_id, Document.deleted_at.is_(None)).order_by(Document.created_at.asc(), Document.id.asc())` — Set SQL result ordering in the listed priority order; first obtain the receiver: `select(Document).where(Document.project_id == project_id, Document.deleted_at.is_(None))` — Add SQL filtering predicates; multiple supplied predicates are combined with AND. |
| L626 | `select(Document)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L627 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L628 | Continue the enclosing expression: build a SQL predicate requiring `Document.project_id` equals `project_id`. |
| L629 | `Document.deleted_at.is_(None)` — Build an SQL IS predicate, commonly IS NULL for a live-row filter. |
| L630 | Close the expression/container begun at L626; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L631 | Set SQL result ordering in the listed priority order; apply this method to the result built by the preceding chain. |
| L632 | Supply positional argument 1 to `list`: `session.execute(select(Document).where(Document.project_id == project_id, Document.deleted_at.is_(None)).order_by(Document.created_at.asc(), Document.id.asc())).scalars().all` with the arguments detailed below — Materialize all remaining values in this SQL result; first obtain the receiver: `session.execute(select(Document).where(Document.project_id == project_id, Document.deleted_at.is_(None)).order_by(Document.created_at.asc(), Document.id.asc())).scalars` with the arguments detailed below — Expose only the first selected column from each row of the SQL result; first obtain the receiver: `session.execute` with the arguments detailed below — Execute the SQL statement in the current transaction and return its Result (including rowcount for guarded updates). |
| L633 | Close the expression/container begun at L624; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `find_awaiting_upload_jobs(session, *, cutoff: datetime, limit=100) -> list[ProcessingJob]`

**Arguments:** Session, reservation-age cutoff, maximum rows. **Returns:** Awaiting jobs created strictly before cutoff, oldest-first. **Work:** Treats a naive cutoff as UTC, filters status/creation time, orders by creation/ID, and applies limit. It performs no provider inspection or state repair.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-find-awaiting-upload-jobs"></a>

#### Line-by-line execution

[Current source: lines 641–669](../../../../Backend/app/repositories/documents.py#L641-L669). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `cutoff` | `datetime`; required; keyword-only | Inclusive age cutoff used to select old work. |
| `limit` | `int`; default `100`; keyword-only | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |

**Declared result:** `list[ProcessingJob]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 641 | def find_awaiting_upload_jobs(
 642 |     session: Session,
 643 |     *,
 644 |     cutoff: datetime,
 645 |     limit: int = 100,
 646 | ) -> list[ProcessingJob]:
 647 |     """Stalled ``awaiting_upload`` jobs older than ``cutoff``, oldest-first.
 648 | 
 649 |     The worker's reconciliation pass inspects each candidate's storage
 650 |     completion (size + fingerprint via the snapshot) and either queues
 651 |     complete files (``confirm_upload_completion`` semantics) or fails
 652 |     abandoned partials with a terminal ``failed`` job.  Ordering is
 653 |     stable (``created_at ASC, id ASC``) so overlapping workers make
 654 |     progress without starvation; the partial unique nonterminal index
 655 |     prevents double-queuing.
 656 |     """
 657 |     if cutoff.tzinfo is None:
 658 |         cutoff = cutoff.replace(tzinfo=timezone.utc)
 659 |     return list(
 660 |         session.execute(
 661 |             select(ProcessingJob)
 662 |             .where(
 663 |                 ProcessingJob.status == "awaiting_upload",
 664 |                 ProcessingJob.created_at < cutoff,
 665 |             )
 666 |             .order_by(ProcessingJob.created_at.asc(), ProcessingJob.id.asc())
 667 |             .limit(limit)
 668 |         ).scalars().all()
 669 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L641 | Define `find_awaiting_upload_jobs`; bind its arguments when called. The body executes only when invoked. |
| L642 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L643 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L644 | Declare parameter `cutoff` with annotation `datetime`. Inclusive age cutoff used to select old work. |
| L645 | Declare parameter `limit` with annotation `int`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. |
| L646 | Finish/continue the signature; the declared return annotation is `list[ProcessingJob]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L647 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L649 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L650 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L651 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L652 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L653 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L654 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L655 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L656 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L657 | Evaluate the branch condition: compare whether `cutoff.tzinfo` is the same object as `None`. If truthy, enter L658; otherwise skip this indented block and continue after it. |
| L658 | Evaluate the right-hand side, then bind/store it in `cutoff`: `cutoff.replace(tzinfo=timezone.utc)` — Return a value with the specified replacements applied. |
| L659 | Compute the return value: `list` with the arguments detailed below — Materialize the iterable in order into a list (or create an empty list); inputs include `session.execute(select(ProcessingJob).where(ProcessingJob.status == 'awaiting_upload', ProcessingJob.created_at < cutoff).order_by(ProcessingJob.created_at.asc(), ProcessingJob.id.asc()).limit(limit)).scalars().all` with the arguments detailed below — Materialize all remaining values in this SQL result; first obtain the receiver: `session.execute(select(ProcessingJob).where(ProcessingJob.status == 'awaiting_upload', ProcessingJob.created_at < cutoff).order_by(ProcessingJob.created_at.asc(), ProcessingJob.id.asc()).limit(limit)).scalars` with the arguments detailed below — Expose only the first selected column from each row of the SQL result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L660 | `session.execute` with the arguments detailed below — Execute the SQL statement in the current transaction and return its Result (including rowcount for guarded updates); inputs include `select(ProcessingJob).where(ProcessingJob.status == 'awaiting_upload', ProcessingJob.created_at < cutoff).order_by(ProcessingJob.created_at.asc(), ProcessingJob.id.asc()).limit` with the arguments detailed below — Apply a SQL row limit; fetching limit+1 allows continuation detection; first obtain the receiver: `select(ProcessingJob).where(ProcessingJob.status == 'awaiting_upload', ProcessingJob.created_at < cutoff).order_by` with the arguments detailed below — Set SQL result ordering in the listed priority order. |
| L661 | `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L662 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L663 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.status` equals `'awaiting_upload'`. |
| L664 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.created_at` is less than `cutoff`. |
| L665 | Close the expression/container begun at L661; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L666 | Set SQL result ordering in the listed priority order; apply this method to the result built by the preceding chain. |
| L667 | Apply a SQL row limit; fetching limit+1 allows continuation detection; apply this method to the result built by the preceding chain. |
| L668 | Supply positional argument 1 to `list`: `session.execute(select(ProcessingJob).where(ProcessingJob.status == 'awaiting_upload', ProcessingJob.created_at < cutoff).order_by(ProcessingJob.created_at.asc(), ProcessingJob.id.asc()).limit(limit)).scalars().all` with the arguments detailed below — Materialize all remaining values in this SQL result; first obtain the receiver: `session.execute(select(ProcessingJob).where(ProcessingJob.status == 'awaiting_upload', ProcessingJob.created_at < cutoff).order_by(ProcessingJob.created_at.asc(), ProcessingJob.id.asc()).limit(limit)).scalars` with the arguments detailed below — Expose only the first selected column from each row of the SQL result; first obtain the receiver: `session.execute` with the arguments detailed below — Execute the SQL statement in the current transaction and return its Result (including rowcount for guarded updates). |
| L669 | Close the expression/container begun at L659; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `nonterminal_process_job(session, *, target_document_id) -> ProcessingJob | None`

**Arguments:** Session and target UUID. **Returns:** Active process job or `None`. **Work:** Filters exact target/kind and the four nonterminal states. The partial unique index ensures at most one active target/kind row.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-nonterminal-process-job"></a>

#### Line-by-line execution

[Current source: lines 672–684](../../../../Backend/app/repositories/documents.py#L672-L684). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `target_document_id` | `UUID`; required; keyword-only | Immutable target UUID retained even when the live document relationship disappears. |

**Declared result:** `ProcessingJob | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 672 | def nonterminal_process_job(
 673 |     session: Session, *, target_document_id: UUID
 674 | ) -> ProcessingJob | None:
 675 |     """Any nonterminal ``process_document`` job for a document, if present."""
 676 |     return session.scalar(
 677 |         select(ProcessingJob).where(
 678 |             ProcessingJob.target_document_id == target_document_id,
 679 |             ProcessingJob.kind == "process_document",
 680 |             ProcessingJob.status.in_(
 681 |                 ("awaiting_upload", "queued", "running", "retry_wait")
 682 |             ),
 683 |         )
 684 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L672 | Define `nonterminal_process_job`; bind its arguments when called. The body executes only when invoked. |
| L673 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `target_document_id` with annotation `UUID`. Immutable target UUID retained even when the live document relationship disappears. |
| L674 | Finish/continue the signature; the declared return annotation is `ProcessingJob \| None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L675 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L676 | Compute the return value: `session.scalar` with the arguments detailed below — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(ProcessingJob).where` with the arguments detailed below — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L677 | `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L678 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.target_document_id` equals `target_document_id`. |
| L679 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.kind` equals `'process_document'`. |
| L680 | `ProcessingJob.status.in_(('awaiting_upload', 'queued', 'running', 'retry_wait'))` — Build a SQL membership predicate for the supplied allowed values. |
| L681 | Supply positional argument 1 to `ProcessingJob.status.in_`: build a tuple containing `'awaiting_upload'`, `'queued'`, `'running'`, `'retry_wait'`. |
| L682 | Close the expression/container begun at L680; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L683 | Close the expression/container begun at L677; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L684 | Close the expression/container begun at L676; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->
