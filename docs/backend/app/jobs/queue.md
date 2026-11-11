# `app/jobs/queue.py`

[Source](../../../../Backend/app/jobs/queue.py) · [Backend index](../../README.md)

Durable PostgreSQL job operations. Module functions take an open `Session`, flush where needed, and leave commit/rollback to the caller. `JobQueueStore` supplies short transaction boundaries for worker callers. Providers run outside these scopes.

## Data and states

`JobContext` is a frozen dataclass copying job identity/kind/status/epoch/owner/project/document, attempt counts, token/version, a shallow-copied resource snapshot, storage expectations, live-document facts, and timestamps. Its nested dictionary remains mutable. `SweepCandidate` carries document/project/owner/version/job UUIDs. Both constructors are dataclass-generated.

Kinds are `process_document` and `delete_document`. Statuses are `awaiting_upload`, `queued`, `running`, `retry_wait`, `succeeded`, `failed`, `cancelled`; the last three are terminal. Default backoff base/cap are 5/3600 seconds.

## Functions

### `JobContext.storage_file_id(self) -> str | None`

Property; returns the truthy snapshot `file_id`, falling back to the live document's Appwrite file ID. It performs no storage access.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobcontext-storage-file-id"></a>

#### Line-by-line execution

[Current source: lines 147–149](../../../../Backend/app/jobs/queue.py#L147-L149). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |

**Declared result:** `str | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 147 |     @property
 148 |     def storage_file_id(self) -> str | None:
 149 |         return self.file_id or self.doc_appwrite_file_id
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L147 | Expose this getter as an attribute; reading the property invokes the body instead of requiring an explicit method call. |
| L148 | Define `JobContext.storage_file_id`; bind its arguments when called. The body executes only when invoked. |
| L149 | Compute the return value: evaluate `self.file_id or self.doc_appwrite_file_id` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `JobContext.storage_bucket_id(self) -> str | None`

Property; returns snapshot `bucket_id` directly, without an environment fallback.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobcontext-storage-bucket-id"></a>

#### Line-by-line execution

[Current source: lines 151–153](../../../../Backend/app/jobs/queue.py#L151-L153). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |

**Declared result:** `str | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 151 |     @property
 152 |     def storage_bucket_id(self) -> str | None:
 153 |         return self.bucket_id
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L151 | Expose this getter as an attribute; reading the property invokes the body instead of requiring an explicit method call. |
| L152 | Define `JobContext.storage_bucket_id`; bind its arguments when called. The body executes only when invoked. |
| L153 | Compute the return value: the `bucket_id` attribute of `self`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `JobContext.storage_file_name(self) -> str | None`

Property; returns snapshot filename or live document filename, whichever is first truthy.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobcontext-storage-file-name"></a>

#### Line-by-line execution

[Current source: lines 155–157](../../../../Backend/app/jobs/queue.py#L155-L157). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |

**Declared result:** `str | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 155 |     @property
 156 |     def storage_file_name(self) -> str | None:
 157 |         return self.file_name or self.doc_file_name
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L155 | Expose this getter as an attribute; reading the property invokes the body instead of requiring an explicit method call. |
| L156 | Define `JobContext.storage_file_name`; bind its arguments when called. The body executes only when invoked. |
| L157 | Compute the return value: evaluate `self.file_name or self.doc_file_name` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `lease_is_current(*, status, lease_owner, lease_token, lease_expires_at, worker_id, token, now) -> bool`

Accepts stored claim fields, expected worker/token, and current timestamp. Returns true only for `running`, exact worker/token equality, non-null expiry, and expiry strictly after `now`. Pure comparisons; compatible timezone-aware timestamps are the caller's responsibility.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-lease-is-current"></a>

#### Line-by-line execution

[Current source: lines 176–193](../../../../Backend/app/jobs/queue.py#L176-L193). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `status` | `str \| None`; required; keyword-only | Caller-supplied status; each read, transformation, and validation is traced below. |
| `lease_owner` | `str \| None`; required; keyword-only | Caller-supplied lease owner; each read, transformation, and validation is traced below. |
| `lease_token` | `int \| None`; required; keyword-only | Monotonic claim token used to reject stale worker writes. |
| `lease_expires_at` | `datetime \| None`; required; keyword-only | Caller-supplied lease expires at; each read, transformation, and validation is traced below. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `token` | `int`; required; keyword-only | Expected claim/generation token compared with persisted state. |
| `now` | `datetime`; required; keyword-only | Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 176 | def lease_is_current(
 177 |     *,
 178 |     status: str | None,
 179 |     lease_owner: str | None,
 180 |     lease_token: int | None,
 181 |     lease_expires_at: datetime | None,
 182 |     worker_id: str,
 183 |     token: int,
 184 |     now: datetime,
 185 | ) -> bool:
 186 |     """True iff the caller's claim is the live, unexpired one."""
 187 |     return (
 188 |         status == STATUS_RUNNING
 189 |         and lease_owner == worker_id
 190 |         and lease_token == token
 191 |         and lease_expires_at is not None
 192 |         and lease_expires_at > now
 193 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L176 | Define `lease_is_current`; bind its arguments when called. The body executes only when invoked. |
| L177 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L178 | Declare parameter `status` with annotation `str \| None`. Caller-supplied status; its uses and transformations are traced below. |
| L179 | Declare parameter `lease_owner` with annotation `str \| None`. Caller-supplied lease owner; its uses and transformations are traced below. |
| L180 | Declare parameter `lease_token` with annotation `int \| None`. Monotonic claim token used to reject stale worker writes. |
| L181 | Declare parameter `lease_expires_at` with annotation `datetime \| None`. Caller-supplied lease expires at; its uses and transformations are traced below. |
| L182 | Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. |
| L183 | Declare parameter `token` with annotation `int`. Expected claim/generation token compared with persisted state. |
| L184 | Declare parameter `now` with annotation `datetime`. Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |
| L185 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L186 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L187 | Compute the return value: evaluate `status == STATUS_RUNNING and lease_owner == worker_id and (lease_token == token) and (lease_expires_at is not None) and (lease_expires_at > now)` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L188 | Continue the enclosing expression: evaluate `status == STATUS_RUNNING and lease_owner == worker_id and (lease_token == token) and (lease_expires_at is not None) and (lease_expires_at > now)` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. |
| L189 | Continue the enclosing expression: compare whether `lease_owner` equals `worker_id`. |
| L190 | Continue the enclosing expression: compare whether `lease_token` equals `token`. |
| L191 | Continue the enclosing expression: compare whether `lease_expires_at` is not the same object as `None`. |
| L192 | Continue the enclosing expression: compare whether `lease_expires_at` is greater than `now`. |
| L193 | Close the parenthesized expression; delimiters only group the preceding operation. |

<!-- END LINE WALKTHROUGH -->

### `evaluate_publication(job, document, project, *, worker_id, lease_token, now) -> tuple[bool, str]`

Accepts row-like objects and expected claim/time. Returns an allow flag plus reason. A succeeded job is an idempotent success only when its version equals the document active pointer; other non-running states fail. Running jobs must pass the lease check, have a version, have a live document, have no tombstoned supplied project, and match document epoch. Reasons are `already_published`, `already_terminal`, `lease_lost`, `missing_index_version`, `document_gone`, `project_gone`, `epoch_mismatch`, `ok`. A `None` project is not explicitly rejected; the function also does not lock rows itself.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-evaluate-publication"></a>

#### Line-by-line execution

[Current source: lines 196–238](../../../../Backend/app/jobs/queue.py#L196-L238). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `job` | `Any`; required; positional or keyword | Caller-supplied job; each read, transformation, and validation is traced below. |
| `document` | `Any`; required; positional or keyword | Caller-supplied document; each read, transformation, and validation is traced below. |
| `project` | `Any`; required; positional or keyword | Caller-supplied project; each read, transformation, and validation is traced below. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `lease_token` | `int`; required; keyword-only | Monotonic claim token used to reject stale worker writes. |
| `now` | `datetime`; required; keyword-only | Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |

**Declared result:** `tuple[bool, str]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 196 | def evaluate_publication(
 197 |     job: Any,
 198 |     document: Any,
 199 |     project: Any,
 200 |     *,
 201 |     worker_id: str,
 202 |     lease_token: int,
 203 |     now: datetime,
 204 | ) -> tuple[bool, str]:
 205 |     """Fenced-publication check for a ``process_document`` job.
 206 | 
 207 |     Returns ``(allowed, reason)``; ``reason`` is a stable token for
 208 |     logs/metrics (``ok``, ``lease_lost``, ``epoch_mismatch``,
 209 |     ``document_gone``, ``project_gone``, ``missing_index_version``,
 210 |     ``already_terminal``, ``already_published``).  Operates on anything
 211 |     with the right attributes (ORM rows or test doubles).
 212 |     ``document``/``project`` may be ``None`` (hard-deleted rows).
 213 |     """
 214 |     if job.status == STATUS_SUCCEEDED:
 215 |         if document is not None and document.active_index_version == job.index_version:
 216 |             return True, "already_published"
 217 |         return False, "already_terminal"
 218 |     if job.status != STATUS_RUNNING:
 219 |         return False, "already_terminal"
 220 |     if not lease_is_current(
 221 |         status=job.status,
 222 |         lease_owner=job.lease_owner,
 223 |         lease_token=job.lease_token,
 224 |         lease_expires_at=job.lease_expires_at,
 225 |         worker_id=worker_id,
 226 |         token=lease_token,
 227 |         now=now,
 228 |     ):
 229 |         return False, "lease_lost"
 230 |     if job.index_version is None:
 231 |         return False, "missing_index_version"
 232 |     if document is None or getattr(document, "deleted_at", None) is not None:
 233 |         return False, "document_gone"
 234 |     if project is not None and project.deleted_at is not None:
 235 |         return False, "project_gone"
 236 |     if document.processing_epoch != job.target_epoch:
 237 |         return False, "epoch_mismatch"
 238 |     return True, "ok"
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L196 | Define `evaluate_publication`; bind its arguments when called. The body executes only when invoked. |
| L197 | Declare parameter `job` with annotation `Any`. Caller-supplied job; its uses and transformations are traced below. |
| L198 | Declare parameter `document` with annotation `Any`. Caller-supplied document; its uses and transformations are traced below. |
| L199 | Declare parameter `project` with annotation `Any`. Caller-supplied project; its uses and transformations are traced below. |
| L200 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L201 | Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. |
| L202 | Declare parameter `lease_token` with annotation `int`. Monotonic claim token used to reject stale worker writes. |
| L203 | Declare parameter `now` with annotation `datetime`. Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |
| L204 | Finish/continue the signature; the declared return annotation is `tuple[bool, str]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L205 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L207 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L208 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L209 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L210 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L211 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L212 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L213 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L214 | Evaluate the branch condition: compare whether `job.status` equals `STATUS_SUCCEEDED`. If truthy, enter L215; otherwise skip this indented block and continue after it. |
| L215 | Evaluate the branch condition: evaluate `document is not None and document.active_index_version == job.index_version` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L216; otherwise skip this indented block and continue after it. |
| L216 | Compute the return value: build a tuple containing `True`, `'already_published'`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L217 | Compute the return value: build a tuple containing `False`, `'already_terminal'`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L218 | Evaluate the branch condition: compare whether `job.status` differs from `STATUS_RUNNING`. If truthy, enter L219; otherwise skip this indented block and continue after it. |
| L219 | Compute the return value: build a tuple containing `False`, `'already_terminal'`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L220 | Evaluate the branch condition: invert the truthiness of `lease_is_current(status=job.status, lease_owner=job.lease_owner, lease_token=job.lease_token, lease_expires_at=job.lease_expires_at, worker_id=worker_id, token=lease_token, now=now)`. If truthy, enter L229; otherwise skip this indented block and continue after it. |
| L221 | Supply `status` = `job.status`.  Evaluate the value as: the `status` attribute of `job`. |
| L222 | Supply `lease_owner` = `job.lease_owner`.  Evaluate the value as: the `lease_owner` attribute of `job`. |
| L223 | Supply `lease_token` = `job.lease_token`. Monotonic claim token used to reject stale worker writes. Evaluate the value as: the `lease_token` attribute of `job`. |
| L224 | Supply `lease_expires_at` = `job.lease_expires_at`.  Evaluate the value as: the `lease_expires_at` attribute of `job`. |
| L225 | Supply `worker_id` = `worker_id`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: the current `worker_id` value. |
| L226 | Supply `token` = `lease_token`. Expected claim/generation token compared with persisted state. Evaluate the value as: the current `lease_token` value. |
| L227 | Supply `now` = `now`. Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. Evaluate the value as: the current `now` value. |
| L228 | Close the expression/container begun at L220; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L229 | Compute the return value: build a tuple containing `False`, `'lease_lost'`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L230 | Evaluate the branch condition: compare whether `job.index_version` is the same object as `None`. If truthy, enter L231; otherwise skip this indented block and continue after it. |
| L231 | Compute the return value: build a tuple containing `False`, `'missing_index_version'`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L232 | Evaluate the branch condition: evaluate `document is None or getattr(document, 'deleted_at', None) is not None` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L233; otherwise skip this indented block and continue after it. |
| L233 | Compute the return value: build a tuple containing `False`, `'document_gone'`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L234 | Evaluate the branch condition: evaluate `project is not None and project.deleted_at is not None` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L235; otherwise skip this indented block and continue after it. |
| L235 | Compute the return value: build a tuple containing `False`, `'project_gone'`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L236 | Evaluate the branch condition: compare whether `document.processing_epoch` differs from `job.target_epoch`. If truthy, enter L237; otherwise skip this indented block and continue after it. |
| L237 | Compute the return value: build a tuple containing `False`, `'epoch_mismatch'`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L238 | Compute the return value: build a tuple containing `True`, `'ok'`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_clear_lease(job: ProcessingJob) -> None`

Clears lease owner and expiry on the ORM object, preserving the monotonic token. No flush/commit occurs here.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--clear-lease"></a>

#### Line-by-line execution

[Current source: lines 241–248](../../../../Backend/app/jobs/queue.py#L241-L248). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `job` | `ProcessingJob`; required; positional or keyword | Caller-supplied job; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 241 | def _clear_lease(job: ProcessingJob) -> None:
 242 |     # Keep lease_token: fencing tokens must be monotonic per job.  A
 243 |     # reclaimed job always gets a strictly larger token, so a zombie
 244 |     # holder's token can never match again.  Owner/expiry are cleared
 245 |     # so the "current claim" checks (which require a live expiry)
 246 |     # fail until the next claim.
 247 |     job.lease_owner = None
 248 |     job.lease_expires_at = None
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L241 | Define `_clear_lease`; bind its arguments when called. The body executes only when invoked. |
| L242 | Comment only: Keep lease_token: fencing tokens must be monotonic per job.  A. It does not execute; the neighboring code determines behavior. |
| L243 | Comment only: reclaimed job always gets a strictly larger token, so a zombie. It does not execute; the neighboring code determines behavior. |
| L244 | Comment only: holder's token can never match again.  Owner/expiry are cleared. It does not execute; the neighboring code determines behavior. |
| L245 | Comment only: so the "current claim" checks (which require a live expiry). It does not execute; the neighboring code determines behavior. |
| L246 | Comment only: fail until the next claim.. It does not execute; the neighboring code determines behavior. |
| L247 | Evaluate the right-hand side, then bind/store it in `job.lease_owner`: None (no value). |
| L248 | Evaluate the right-hand side, then bind/store it in `job.lease_expires_at`: None (no value). |

<!-- END LINE WALKTHROUGH -->

### `_snapshot_get(snapshot, key: str, default=None) -> Any`

Accepts a possibly missing mapping, key, and fallback. Returns `snapshot.get(key, default)` for a `Mapping`, otherwise the fallback; no coercion or alias resolution.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--snapshot-get"></a>

#### Line-by-line execution

[Current source: lines 251–254](../../../../Backend/app/jobs/queue.py#L251-L254). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `snapshot` | `Mapping[str, Any] \| None`; required; positional or keyword | Caller-supplied snapshot; each read, transformation, and validation is traced below. |
| `key` | `str`; required; positional or keyword | Caller-supplied key; each read, transformation, and validation is traced below. |
| `default` | `Any`; default `None`; positional or keyword | Fallback returned when the selected input is absent or cannot be parsed where explicitly handled. |

**Declared result:** `Any`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 251 | def _snapshot_get(snapshot: Mapping[str, Any] | None, key: str, default: Any = None) -> Any:
 252 |     if isinstance(snapshot, Mapping):
 253 |         return snapshot.get(key, default)
 254 |     return default
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L251 | Define `_snapshot_get`; bind its arguments when called. The body executes only when invoked. |
| L252 | Evaluate the branch condition: `isinstance(snapshot, Mapping)` — Check the runtime type against the supplied class or tuple of classes. If truthy, enter L253; otherwise skip this indented block and continue after it. |
| L253 | Compute the return value: `snapshot.get(key, default)` — Look up `key` in `snapshot`, using `default` when the key is absent (an existing null value is not replaced). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L254 | Compute the return value: the current `default` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `enqueue_job(session, *, owner_user_id, project_id, target_document_id, document_id, kind, target_epoch, resource_snapshot, available_at=None, max_attempts=3, status="queued", stage=None) -> ProcessingJob`

Accepts trusted UUID ownership/target inputs, nullable live document FK, kind/epoch, JSON snapshot, scheduling/retry/state options. Returns an inserted job or the existing nonterminal target/kind winner **unchanged**. Requires positive max attempts and a dictionary snapshot, constructs a shallow copy with zero attempts, then checks for a winner. On a miss, adds/flushes inside `begin_nested()`; a unique-race loser re-queries after savepoint rollback. If no winner exists, the original `IntegrityError` propagates. No network or ownership lookup occurs here.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-enqueue-job"></a>

#### Line-by-line execution

[Current source: lines 262–320](../../../../Backend/app/jobs/queue.py#L262-L320). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
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
| `status` | `str`; default `STATUS_QUEUED`; keyword-only | Caller-supplied status; each read, transformation, and validation is traced below. |
| `stage` | `str \| None`; default `None`; keyword-only | Public job stage to record, such as extracting, embedding, indexing, or publishing. |

**Declared result:** `ProcessingJob`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 262 | def enqueue_job(
 263 |     session: Session,
 264 |     *,
 265 |     owner_user_id: UUID,
 266 |     project_id: UUID,
 267 |     target_document_id: UUID,
 268 |     document_id: UUID | None,
 269 |     kind: str,
 270 |     target_epoch: int,
 271 |     resource_snapshot: dict[str, Any],
 272 |     available_at: datetime | None = None,
 273 |     max_attempts: int = 3,
 274 |     status: str = STATUS_QUEUED,
 275 |     stage: str | None = None,
 276 | ) -> ProcessingJob:
 277 |     """Insert or return one active job row in the caller's transaction.
 278 | 
 279 |     ``status`` is ``awaiting_upload`` for the upload reservation flow
 280 |     (A3 flips it to ``queued`` after storage completion) and ``queued``
 281 |     for retry/cleanup jobs.  The partial unique nonterminal
 282 |     ``(target_document_id, kind)`` index enforces at most one active
 283 |     job per target/kind. Concurrent duplicate enqueues return the
 284 |     winning active job without aborting the caller's transaction.
 285 |     """
 286 |     if max_attempts < 1:
 287 |         raise ValueError("max_attempts must be >= 1")
 288 |     if not isinstance(resource_snapshot, dict):
 289 |         raise ValueError("resource_snapshot must be a JSON object")
 290 |     job = ProcessingJob(
 291 |         document_id=document_id,
 292 |         owner_user_id=owner_user_id,
 293 |         project_id=project_id,
 294 |         target_document_id=target_document_id,
 295 |         resource_snapshot=dict(resource_snapshot),
 296 |         target_epoch=target_epoch,
 297 |         kind=kind,
 298 |         status=status,
 299 |         stage=stage,
 300 |         attempt_count=0,
 301 |         max_attempts=max_attempts,
 302 |         available_at=available_at or utcnow(),
 303 |     )
 304 |     existing = find_nonterminal_job(
 305 |         session, target_document_id=target_document_id, kind=kind
 306 |     )
 307 |     if existing is not None:
 308 |         return existing
 309 |     try:
 310 |         with session.begin_nested():
 311 |             session.add(job)
 312 |             session.flush()
 313 |     except IntegrityError:
 314 |         winner = find_nonterminal_job(
 315 |             session, target_document_id=target_document_id, kind=kind
 316 |         )
 317 |         if winner is not None:
 318 |             return winner
 319 |         raise
 320 |     return job
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L262 | Define `enqueue_job`; bind its arguments when called. The body executes only when invoked. |
| L263 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L264 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L265 | Declare parameter `owner_user_id` with annotation `UUID`. Internal owner UUID copied into the job's durable ownership snapshot. |
| L266 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L267 | Declare parameter `target_document_id` with annotation `UUID`. Immutable target UUID retained even when the live document relationship disappears. |
| L268 | Declare parameter `document_id` with annotation `UUID \| None`. Document UUID; filenames do not establish document identity. |
| L269 | Declare parameter `kind` with annotation `str`. Caller-supplied kind; its uses and transformations are traced below. |
| L270 | Declare parameter `target_epoch` with annotation `int`. Expected document processing epoch used to invalidate obsolete attempts. |
| L271 | Declare parameter `resource_snapshot` with annotation `dict[str, Any]`. JSON-compatible resource facts copied into a durable job. |
| L272 | Declare parameter `available_at` with annotation `datetime \| None`. Earliest time a queued/retry-wait job may be claimed. |
| L273 | Declare parameter `max_attempts` with annotation `int`. Maximum number of claims before retryable failures become terminal. |
| L274 | Declare parameter `status` with annotation `str`. Caller-supplied status; its uses and transformations are traced below. |
| L275 | Declare parameter `stage` with annotation `str \| None`. Public job stage to record, such as extracting, embedding, indexing, or publishing. |
| L276 | Finish/continue the signature; the declared return annotation is `ProcessingJob`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L277 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L279 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L280 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L281 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L282 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L283 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L284 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L285 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L286 | Evaluate the branch condition: compare whether `max_attempts` is less than `1`. If truthy, enter L287; otherwise skip this indented block and continue after it. |
| L287 | Raise `ValueError('max_attempts must be >= 1')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L288 | Evaluate the branch condition: invert the truthiness of `isinstance(resource_snapshot, dict)`. If truthy, enter L289; otherwise skip this indented block and continue after it. |
| L289 | Raise `ValueError('resource_snapshot must be a JSON object')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L290 | Evaluate the right-hand side, then bind/store it in `job`: `ProcessingJob` with the arguments detailed below — Construct `ProcessingJob` with the shown fields; its class/model initialization rules apply. |
| L291 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L292 | Supply `owner_user_id` = `owner_user_id`. Internal owner UUID copied into the job's durable ownership snapshot. Evaluate the value as: the current `owner_user_id` value. |
| L293 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L294 | Supply `target_document_id` = `target_document_id`. Immutable target UUID retained even when the live document relationship disappears. Evaluate the value as: the current `target_document_id` value. |
| L295 | Supply `resource_snapshot` = `dict(resource_snapshot)`. JSON-compatible resource facts copied into a durable job. Evaluate the value as: `dict(resource_snapshot)` — Build a mapping from the supplied items/keywords; copying a mapping is shallow. |
| L296 | Supply `target_epoch` = `target_epoch`. Expected document processing epoch used to invalidate obsolete attempts. Evaluate the value as: the current `target_epoch` value. |
| L297 | Supply `kind` = `kind`.  Evaluate the value as: the current `kind` value. |
| L298 | Supply `status` = `status`.  Evaluate the value as: the current `status` value. |
| L299 | Supply `stage` = `stage`. Public job stage to record, such as extracting, embedding, indexing, or publishing. Evaluate the value as: the current `stage` value. |
| L300 | Supply `attempt_count` = `0`. Number of attempts already claimed; used to decide retries and calculate delay. Evaluate the value as: `0`. |
| L301 | Supply `max_attempts` = `max_attempts`. Maximum number of claims before retryable failures become terminal. Evaluate the value as: the current `max_attempts` value. |
| L302 | Supply `available_at` = `available_at or utcnow()`. Earliest time a queued/retry-wait job may be claimed. Evaluate the value as: evaluate `available_at or utcnow()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L303 | Close the expression/container begun at L290; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L304 | Evaluate the right-hand side, then bind/store it in `existing`: `find_nonterminal_job(session, target_document_id=target_document_id, kind=kind)` — Call [find_nonterminal_job](#walk-find-nonterminal-job) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L305 | Supply `target_document_id` = `target_document_id`. Immutable target UUID retained even when the live document relationship disappears. Evaluate the value as: the current `target_document_id` value. Supply `kind` = `kind`.  Evaluate the value as: the current `kind` value. |
| L306 | Close the expression/container begun at L304; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L307 | Evaluate the branch condition: compare whether `existing` is not the same object as `None`. If truthy, enter L308; otherwise skip this indented block and continue after it. |
| L308 | Compute the return value: the current `existing` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L309 | Enter the protected block; failures are matched against `IntegrityError` in order. |
| L310 | Enter `session.begin_nested()` — Open a SAVEPOINT after SQLAlchemy's pre-flush; a duplicate-insert failure can roll back this savepoint while preserving the outer transaction. Context exits run in reverse order, including on return/exception. |
| L311 | `session.add(job)` — Attach the ORM object to this session for insertion/update tracking; this does not commit it. The return value is not assigned here. |
| L312 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L313 | Handle `IntegrityError`; only a matching error from the associated try enters this body. |
| L314 | Evaluate the right-hand side, then bind/store it in `winner`: `find_nonterminal_job(session, target_document_id=target_document_id, kind=kind)` — Call [find_nonterminal_job](#walk-find-nonterminal-job) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L315 | Supply `target_document_id` = `target_document_id`. Immutable target UUID retained even when the live document relationship disappears. Evaluate the value as: the current `target_document_id` value. Supply `kind` = `kind`.  Evaluate the value as: the current `kind` value. |
| L316 | Close the expression/container begun at L314; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L317 | Evaluate the branch condition: compare whether `winner` is not the same object as `None`. If truthy, enter L318; otherwise skip this indented block and continue after it. |
| L318 | Compute the return value: the current `winner` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L319 | Re-raise the currently handled exception with its traceback; no replacement result is returned. |
| L320 | Compute the return value: the current `job` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `find_nonterminal_job(session, *, target_document_id, kind) -> ProcessingJob | None`

Selects exact target/kind among awaiting/queued/running/retry-wait states and returns a scalar row. The partial unique index enforces one active winner.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-find-nonterminal-job"></a>

#### Line-by-line execution

[Current source: lines 323–335](../../../../Backend/app/jobs/queue.py#L323-L335). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `target_document_id` | `UUID`; required; keyword-only | Immutable target UUID retained even when the live document relationship disappears. |
| `kind` | `str`; required; keyword-only | Caller-supplied kind; each read, transformation, and validation is traced below. |

**Declared result:** `ProcessingJob | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 323 | def find_nonterminal_job(
 324 |     session: Session, *, target_document_id: UUID, kind: str
 325 | ) -> ProcessingJob | None:
 326 |     """Fetch the active job for a target/kind, if one exists."""
 327 |     return session.scalar(
 328 |         select(ProcessingJob).where(
 329 |             ProcessingJob.target_document_id == target_document_id,
 330 |             ProcessingJob.kind == kind,
 331 |             ProcessingJob.status.in_(
 332 |                 (STATUS_AWAITING_UPLOAD, STATUS_QUEUED, STATUS_RUNNING, STATUS_RETRY_WAIT)
 333 |             ),
 334 |         )
 335 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L323 | Define `find_nonterminal_job`; bind its arguments when called. The body executes only when invoked. |
| L324 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `target_document_id` with annotation `UUID`. Immutable target UUID retained even when the live document relationship disappears. Declare parameter `kind` with annotation `str`. Caller-supplied kind; its uses and transformations are traced below. |
| L325 | Finish/continue the signature; the declared return annotation is `ProcessingJob \| None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L326 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L327 | Compute the return value: `session.scalar` with the arguments detailed below — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(ProcessingJob).where` with the arguments detailed below — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L328 | `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L329 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.target_document_id` equals `target_document_id`. |
| L330 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.kind` equals `kind`. |
| L331 | `ProcessingJob.status.in_((STATUS_AWAITING_UPLOAD, STATUS_QUEUED, STATUS_RUNNING, STATUS_RETRY_WAIT))` — Build a SQL membership predicate for the supplied allowed values. |
| L332 | Supply positional argument 1 to `ProcessingJob.status.in_`: build a tuple containing `STATUS_AWAITING_UPLOAD`, `STATUS_QUEUED`, `STATUS_RUNNING`, `STATUS_RETRY_WAIT`. |
| L333 | Close the expression/container begun at L331; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L334 | Close the expression/container begun at L328; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L335 | Close the expression/container begun at L327; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `claim_next_jobs(session, *, worker_id: str, limit: int, lease_seconds: int) -> list[JobClaim]`

Returns `[]` for limit <1; otherwise locks up to `limit` due queued/retry-wait jobs with remaining attempts, ordered by availability/creation and `FOR UPDATE SKIP LOCKED`. Missing documents cancel **all** job kinds; tombstoned documents cancel processing but allow delete jobs. For eligible rows, increments attempts/token, sets worker/expiry/running stage, clears finish time, and allocates a fresh process-version UUID. Any previous version is appended to snapshot `superseded_index_versions`. Matching-epoch process documents become `Processing` with cleared error. Flushes and returns detached-shape claims; cancelled candidates are not replaced by additional queries. Project liveness and positive lease duration are not independently checked here.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-claim-next-jobs"></a>

#### Line-by-line execution

[Current source: lines 343–420](../../../../Backend/app/jobs/queue.py#L343-L420). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `limit` | `int`; required; keyword-only | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |
| `lease_seconds` | `int`; required; keyword-only | Lease duration in seconds; positive-duration validation is not implicit in this parameter. |

**Declared result:** `list[JobClaim]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 343 | def claim_next_jobs(
 344 |     session: Session, *, worker_id: str, limit: int, lease_seconds: int
 345 | ) -> list[JobClaim]:
 346 |     """Claim up to ``limit`` due jobs in the caller's transaction.
 347 | 
 348 |     Due = ``queued``/``retry_wait`` with ``available_at <= now`` and
 349 |     attempts remaining.  Rows are locked ``FOR UPDATE SKIP LOCKED`` in
 350 |     ``(available_at, created_at)`` order; each claimed row gets its
 351 |     fencing token + attempt bumped, a fresh ``index_version`` (process
 352 |     jobs), and ``status = running`` before the lock is released.
 353 |     Jobs whose document is tombstoned/hard-deleted are cancelled in
 354 |     place (never claimed), except ``delete_document`` cleanup jobs: they
 355 |     must run *after* tombstoning to remove the private PDF and index
 356 |     versions.  The caller must commit immediately -- the claim is the
 357 |     trigger, and all provider work happens after commit.
 358 |     """
 359 |     if limit < 1:
 360 |         return []
 361 |     now = utcnow()
 362 |     rows = session.scalars(
 363 |         select(ProcessingJob)
 364 |         .where(
 365 |             ProcessingJob.status.in_((STATUS_QUEUED, STATUS_RETRY_WAIT)),
 366 |             ProcessingJob.available_at <= now,
 367 |             ProcessingJob.attempt_count < ProcessingJob.max_attempts,
 368 |         )
 369 |         .order_by(ProcessingJob.available_at, ProcessingJob.created_at)
 370 |         .limit(limit)
 371 |         .with_for_update(skip_locked=True)
 372 |     ).all()
 373 |     claims: list[JobClaim] = []
 374 |     for job in rows:
 375 |         document = (
 376 |             session.get(Document, job.target_document_id) if job.target_document_id else None
 377 |         )
 378 |         if document is None or (
 379 |             document.deleted_at is not None and job.kind != KIND_DELETE
 380 |         ):
 381 |             # Never claim work for a doc that can no longer be published.
 382 |             # delete_document is the exception: its cleanup runs after the
 383 |             # tombstone, so cancelling it would orphan the PDF and vectors.
 384 |             job.status = STATUS_CANCELLED
 385 |             job.finished_at = now
 386 |             job.last_error_code = CANCELLED_MARKER
 387 |             job.last_error_message = "document was deleted before the job was claimed"
 388 |             _clear_lease(job)
 389 |             continue
 390 |         job.attempt_count = (job.attempt_count or 0) + 1
 391 |         job.lease_token = (job.lease_token or 0) + 1
 392 |         job.lease_owner = worker_id
 393 |         job.lease_expires_at = now + timedelta(seconds=lease_seconds)
 394 |         job.status = STATUS_RUNNING
 395 |         job.stage = STAGE_DELETING if job.kind == KIND_DELETE else STAGE_EXTRACTING
 396 |         job.finished_at = None
 397 |         if job.kind == KIND_PROCESS:
 398 |             if job.index_version is not None:
 399 |                 snapshot = dict(job.resource_snapshot or {})
 400 |                 superseded = list(snapshot.get("superseded_index_versions") or [])
 401 |                 superseded.append(str(job.index_version))
 402 |                 snapshot["superseded_index_versions"] = superseded
 403 |                 job.resource_snapshot = snapshot
 404 |             job.index_version = uuid4()
 405 |             if document.processing_epoch == job.target_epoch:
 406 |                 document.status = "Processing"
 407 |                 document.processing_error = None
 408 |         claims.append(
 409 |             JobClaim(
 410 |                 job_id=job.id,
 411 |                 kind=job.kind,
 412 |                 target_document_id=job.target_document_id,
 413 |                 target_epoch=job.target_epoch,
 414 |                 index_version=job.index_version,
 415 |                 lease_token=int(job.lease_token or 0),
 416 |                 lease_expires_at=job.lease_expires_at,
 417 |             )
 418 |         )
 419 |     session.flush()
 420 |     return claims
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L343 | Define `claim_next_jobs`; bind its arguments when called. The body executes only when invoked. |
| L344 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. Declare parameter `limit` with annotation `int`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. Declare parameter `lease_seconds` with annotation `int`. Lease duration in seconds; positive-duration validation is not implicit in this parameter. |
| L345 | Finish/continue the signature; the declared return annotation is `list[JobClaim]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L346 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L348 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L349 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L350 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L351 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L352 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L353 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L354 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L355 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L356 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L357 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L358 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L359 | Evaluate the branch condition: compare whether `limit` is less than `1`. If truthy, enter L360; otherwise skip this indented block and continue after it. |
| L360 | Compute the return value: build a list containing no items. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L361 | Evaluate the right-hand side, then bind/store it in `now`: `utcnow()` — Read the current timezone-aware UTC timestamp. |
| L362 | Evaluate the right-hand side, then bind/store it in `rows`: `session.scalars(select(ProcessingJob).where(ProcessingJob.status.in_((STATUS_QUEUED, STATUS_RETRY_WAIT)), ProcessingJob.available_at <= now, ProcessingJob.attempt_count < ProcessingJob.max_attempts).order_by(ProcessingJob.available_at, ProcessingJob.created_at).limit(limit).with_for_update(skip_locked=True)).all` with the arguments detailed below — Materialize all remaining values in this SQL result; first obtain the receiver: `session.scalars` with the arguments detailed below — Execute the SQL expression and expose first-column values through a ScalarResult. |
| L363 | `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L364 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L365 | `ProcessingJob.status.in_((STATUS_QUEUED, STATUS_RETRY_WAIT))` — Build a SQL membership predicate for the supplied allowed values. |
| L366 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.available_at` is at most `now`. |
| L367 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.attempt_count` is less than `ProcessingJob.max_attempts`. |
| L368 | Close the expression/container begun at L363; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L369 | Set SQL result ordering in the listed priority order; apply this method to the result built by the preceding chain. |
| L370 | Apply a SQL row limit; fetching limit+1 allows continuation detection; apply this method to the result built by the preceding chain. |
| L371 | Request row locks until transaction end; skip_locked=True avoids waiting on rows claimed elsewhere; apply this method to the result built by the preceding chain. |
| L372 | Continue the operation begun at L362: Evaluate the right-hand side, then bind/store it in `rows`: `session.scalars(select(ProcessingJob).where(ProcessingJob.status.in_((STATUS_QUEUED, STATUS_RETRY_WAIT)), ProcessingJob.available_at <= now, ProcessingJob.attempt_count < ProcessingJob.max_attempts).order_by(ProcessingJob.available_at, ProcessingJob.created_at).limit(limit).with_for_update(skip_locked=True)).all` with the arguments detailed below — Materialize all remaining values in this SQL result; first obtain the receiver: `session.scalars` with the arguments detailed below — Execute the SQL expression and expose first-column values through a ScalarResult. |
| L373 | Evaluate the right-hand side, then bind/store it in `claims`: build a list containing no items. |
| L374 | Iterate `rows` (the current `rows` value), assigning each item to `job`. Execute the indented body once per item; an empty iterable skips it. |
| L375 | Evaluate the right-hand side, then bind/store it in `document`: check `job.target_document_id`; when true use `session.get(Document, job.target_document_id)` — Look up the mapped object by primary key, using the session identity map when possible, otherwise SQL, otherwise None (no value) (only the selected branch is evaluated). |
| L376 | `session.get(Document, job.target_document_id)` — Look up the mapped object by primary key, using the session identity map when possible, otherwise SQL. |
| L377 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L378 | Evaluate the branch condition: evaluate `document is None or (document.deleted_at is not None and job.kind != KIND_DELETE)` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L384; otherwise skip this indented block and continue after it. |
| L379 | Continue the enclosing expression: evaluate `document.deleted_at is not None and job.kind != KIND_DELETE` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. |
| L380 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L381 | Comment only: Never claim work for a doc that can no longer be published.. It does not execute; the neighboring code determines behavior. |
| L382 | Comment only: delete_document is the exception: its cleanup runs after the. It does not execute; the neighboring code determines behavior. |
| L383 | Comment only: tombstone, so cancelling it would orphan the PDF and vectors.. It does not execute; the neighboring code determines behavior. |
| L384 | Evaluate the right-hand side, then bind/store it in `job.status`: the current `STATUS_CANCELLED` value. |
| L385 | Evaluate the right-hand side, then bind/store it in `job.finished_at`: the current `now` value. |
| L386 | Evaluate the right-hand side, then bind/store it in `job.last_error_code`: the current `CANCELLED_MARKER` value. |
| L387 | Evaluate the right-hand side, then bind/store it in `job.last_error_message`: `'document was deleted before the job was claimed'`. |
| L388 | `_clear_lease(job)` — Call [_clear_lease](#walk--clear-lease) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L389 | Skip the rest of this iteration and advance the innermost loop to its next item; active finally/context exits still apply. |
| L390 | Evaluate the right-hand side, then bind/store it in `job.attempt_count`: add/concatenate `job.attempt_count or 0` and `1`, following the parentheses/operator precedence shown in `(job.attempt_count or 0) + 1`. |
| L391 | Evaluate the right-hand side, then bind/store it in `job.lease_token`: add/concatenate `job.lease_token or 0` and `1`, following the parentheses/operator precedence shown in `(job.lease_token or 0) + 1`. |
| L392 | Evaluate the right-hand side, then bind/store it in `job.lease_owner`: the current `worker_id` value. |
| L393 | Evaluate the right-hand side, then bind/store it in `job.lease_expires_at`: add/concatenate `now` and `timedelta(seconds=lease_seconds)`, following the parentheses/operator precedence shown in `now + timedelta(seconds=lease_seconds)`. |
| L394 | Evaluate the right-hand side, then bind/store it in `job.status`: the current `STATUS_RUNNING` value. |
| L395 | Evaluate the right-hand side, then bind/store it in `job.stage`: check `job.kind == KIND_DELETE`; when true use the current `STAGE_DELETING` value, otherwise the current `STAGE_EXTRACTING` value (only the selected branch is evaluated). |
| L396 | Evaluate the right-hand side, then bind/store it in `job.finished_at`: None (no value). |
| L397 | Evaluate the branch condition: compare whether `job.kind` equals `KIND_PROCESS`. If truthy, enter L398; otherwise skip this indented block and continue after it. |
| L398 | Evaluate the branch condition: compare whether `job.index_version` is not the same object as `None`. If truthy, enter L399; otherwise skip this indented block and continue after it. |
| L399 | Evaluate the right-hand side, then bind/store it in `snapshot`: `dict(job.resource_snapshot or {})` — Build a mapping from the supplied items/keywords; copying a mapping is shallow. |
| L400 | Evaluate the right-hand side, then bind/store it in `superseded`: `list(snapshot.get('superseded_index_versions') or [])` — Materialize the iterable in order into a list (or create an empty list). |
| L401 | `superseded.append(str(job.index_version))` — Append one object to the mutable list in place; inputs include `str(job.index_version)` — Convert the input to its string representation. The return value is not assigned here. |
| L402 | Evaluate the right-hand side, then bind/store it in `snapshot['superseded_index_versions']`: the current `superseded` value. |
| L403 | Evaluate the right-hand side, then bind/store it in `job.resource_snapshot`: the current `snapshot` value. |
| L404 | Evaluate the right-hand side, then bind/store it in `job.index_version`: `uuid4()` — Generate a new random UUID. |
| L405 | Evaluate the branch condition: compare whether `document.processing_epoch` equals `job.target_epoch`. If truthy, enter L406; otherwise skip this indented block and continue after it. |
| L406 | Evaluate the right-hand side, then bind/store it in `document.status`: `'Processing'`. |
| L407 | Evaluate the right-hand side, then bind/store it in `document.processing_error`: None (no value). |
| L408 | `claims.append` with the arguments detailed below — Append one object to the mutable list in place; inputs include `JobClaim` with the arguments detailed below — Construct `JobClaim` with the shown fields; its class/model initialization rules apply. The return value is not assigned here. |
| L409 | `JobClaim` with the arguments detailed below — Construct `JobClaim` with the shown fields; its class/model initialization rules apply. |
| L410 | Supply `job_id` = `job.id`. Durable processing-job UUID. Evaluate the value as: the `id` attribute of `job`. |
| L411 | Supply `kind` = `job.kind`.  Evaluate the value as: the `kind` attribute of `job`. |
| L412 | Supply `target_document_id` = `job.target_document_id`. Immutable target UUID retained even when the live document relationship disappears. Evaluate the value as: the `target_document_id` attribute of `job`. |
| L413 | Supply `target_epoch` = `job.target_epoch`. Expected document processing epoch used to invalidate obsolete attempts. Evaluate the value as: the `target_epoch` attribute of `job`. |
| L414 | Supply `index_version` = `job.index_version`. UUID of one document's vector-index namespace, separate from its active publication pointer. Evaluate the value as: the `index_version` attribute of `job`. |
| L415 | Supply `lease_token` = `int(job.lease_token or 0)`. Monotonic claim token used to reject stale worker writes. Evaluate the value as: `int(job.lease_token or 0)` — Convert the input to an integer (using the optional numeric base). |
| L416 | Supply `lease_expires_at` = `job.lease_expires_at`.  Evaluate the value as: the `lease_expires_at` attribute of `job`. |
| L417 | Close the expression/container begun at L409; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L418 | Close the expression/container begun at L408; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L419 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L420 | Compute the return value: the current `claims` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `renew_job_lease(session, *, job_id, lease_token, worker_id, lease_seconds) -> bool`

Executes one compare-and-set UPDATE matching ID, running status, owner, token, and unexpired lease. Sets expiry to current UTC time plus duration; returns whether any row was affected. A stale claim returns false.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-renew-job-lease"></a>

#### Line-by-line execution

[Current source: lines 423–444](../../../../Backend/app/jobs/queue.py#L423-L444). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `lease_token` | `int`; required; keyword-only | Monotonic claim token used to reject stale worker writes. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `lease_seconds` | `int`; required; keyword-only | Lease duration in seconds; positive-duration validation is not implicit in this parameter. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 423 | def renew_job_lease(
 424 |     session: Session,
 425 |     *,
 426 |     job_id: UUID,
 427 |     lease_token: int,
 428 |     worker_id: str,
 429 |     lease_seconds: int,
 430 | ) -> bool:
 431 |     """Compare-and-set heartbeat.  False when the claim is no longer ours."""
 432 |     now = utcnow()
 433 |     result = session.execute(
 434 |         update(ProcessingJob)
 435 |         .where(
 436 |             ProcessingJob.id == job_id,
 437 |             ProcessingJob.status == STATUS_RUNNING,
 438 |             ProcessingJob.lease_owner == worker_id,
 439 |             ProcessingJob.lease_token == lease_token,
 440 |             ProcessingJob.lease_expires_at > now,
 441 |         )
 442 |         .values(lease_expires_at=now + timedelta(seconds=lease_seconds))
 443 |     )
 444 |     return bool(result.rowcount)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L423 | Define `renew_job_lease`; bind its arguments when called. The body executes only when invoked. |
| L424 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L425 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L426 | Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. |
| L427 | Declare parameter `lease_token` with annotation `int`. Monotonic claim token used to reject stale worker writes. |
| L428 | Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. |
| L429 | Declare parameter `lease_seconds` with annotation `int`. Lease duration in seconds; positive-duration validation is not implicit in this parameter. |
| L430 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L431 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L432 | Evaluate the right-hand side, then bind/store it in `now`: `utcnow()` — Read the current timezone-aware UTC timestamp. |
| L433 | Evaluate the right-hand side, then bind/store it in `result`: `session.execute` with the arguments detailed below — Execute the SQL statement in the current transaction and return its Result (including rowcount for guarded updates); inputs include `update(ProcessingJob).where(ProcessingJob.id == job_id, ProcessingJob.status == STATUS_RUNNING, ProcessingJob.lease_owner == worker_id, ProcessingJob.lease_token == lease_token, ProcessingJob.lease_expires_at > now).values` with the arguments detailed below — Attach column assignments to the UPDATE/INSERT expression without executing it; first obtain the receiver: `update(ProcessingJob).where` with the arguments detailed below — Add SQL filtering predicates; multiple supplied predicates are combined with AND. |
| L434 | `update(ProcessingJob)` — Construct a SQL UPDATE expression; execution and commit are separate operations. |
| L435 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L436 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.id` equals `job_id`. |
| L437 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.status` equals `STATUS_RUNNING`. |
| L438 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.lease_owner` equals `worker_id`. |
| L439 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.lease_token` equals `lease_token`. |
| L440 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.lease_expires_at` is greater than `now`. |
| L441 | Close the expression/container begun at L434; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L442 | Attach column assignments to the UPDATE/INSERT expression without executing it; apply this method to the result built by the preceding chain. |
| L443 | Close the expression/container begun at L433; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L444 | Compute the return value: `bool(result.rowcount)` — Convert the value's truthiness to True or False. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `update_progress(session, *, job_id, lease_token, worker_id, stage=None, progress_current=None, progress_total=None) -> bool`

Builds values only for non-null supplied fields, then executes the same guarded UPDATE as renewal. Returns true immediately for an empty update, without validating the lease. Null cannot clear an existing field through this function; SQL constraints validate supplied counters/stage.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-update-progress"></a>

#### Line-by-line execution

[Current source: lines 447–479](../../../../Backend/app/jobs/queue.py#L447-L479). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `lease_token` | `int`; required; keyword-only | Monotonic claim token used to reject stale worker writes. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `stage` | `str \| None`; default `None`; keyword-only | Public job stage to record, such as extracting, embedding, indexing, or publishing. |
| `progress_current` | `int \| None`; default `None`; keyword-only | Current completed-work counter; null means do not update it. |
| `progress_total` | `int \| None`; default `None`; keyword-only | Total-work counter; null means do not update it. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 447 | def update_progress(
 448 |     session: Session,
 449 |     *,
 450 |     job_id: UUID,
 451 |     lease_token: int,
 452 |     worker_id: str,
 453 |     stage: str | None = None,
 454 |     progress_current: int | None = None,
 455 |     progress_total: int | None = None,
 456 | ) -> bool:
 457 |     """Guarded stage/progress update (same fencing guard as renewal)."""
 458 |     now = utcnow()
 459 |     values: dict[str, Any] = {}
 460 |     if stage is not None:
 461 |         values["stage"] = stage
 462 |     if progress_current is not None:
 463 |         values["progress_current"] = progress_current
 464 |     if progress_total is not None:
 465 |         values["progress_total"] = progress_total
 466 |     if not values:
 467 |         return True
 468 |     result = session.execute(
 469 |         update(ProcessingJob)
 470 |         .where(
 471 |             ProcessingJob.id == job_id,
 472 |             ProcessingJob.status == STATUS_RUNNING,
 473 |             ProcessingJob.lease_owner == worker_id,
 474 |             ProcessingJob.lease_token == lease_token,
 475 |             ProcessingJob.lease_expires_at > now,
 476 |         )
 477 |         .values(**values)
 478 |     )
 479 |     return bool(result.rowcount)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L447 | Define `update_progress`; bind its arguments when called. The body executes only when invoked. |
| L448 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L449 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L450 | Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. |
| L451 | Declare parameter `lease_token` with annotation `int`. Monotonic claim token used to reject stale worker writes. |
| L452 | Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. |
| L453 | Declare parameter `stage` with annotation `str \| None`. Public job stage to record, such as extracting, embedding, indexing, or publishing. |
| L454 | Declare parameter `progress_current` with annotation `int \| None`. Current completed-work counter; null means do not update it. |
| L455 | Declare parameter `progress_total` with annotation `int \| None`. Total-work counter; null means do not update it. |
| L456 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L457 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L458 | Evaluate the right-hand side, then bind/store it in `now`: `utcnow()` — Read the current timezone-aware UTC timestamp. |
| L459 | Evaluate the right-hand side, then bind/store it in `values`: create an empty dictionary. |
| L460 | Evaluate the branch condition: compare whether `stage` is not the same object as `None`. If truthy, enter L461; otherwise skip this indented block and continue after it. |
| L461 | Evaluate the right-hand side, then bind/store it in `values['stage']`: the current `stage` value. |
| L462 | Evaluate the branch condition: compare whether `progress_current` is not the same object as `None`. If truthy, enter L463; otherwise skip this indented block and continue after it. |
| L463 | Evaluate the right-hand side, then bind/store it in `values['progress_current']`: the current `progress_current` value. |
| L464 | Evaluate the branch condition: compare whether `progress_total` is not the same object as `None`. If truthy, enter L465; otherwise skip this indented block and continue after it. |
| L465 | Evaluate the right-hand side, then bind/store it in `values['progress_total']`: the current `progress_total` value. |
| L466 | Evaluate the branch condition: invert the truthiness of `values`. If truthy, enter L467; otherwise skip this indented block and continue after it. |
| L467 | Compute the return value: `True`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L468 | Evaluate the right-hand side, then bind/store it in `result`: `session.execute` with the arguments detailed below — Execute the SQL statement in the current transaction and return its Result (including rowcount for guarded updates); inputs include `update(ProcessingJob).where(ProcessingJob.id == job_id, ProcessingJob.status == STATUS_RUNNING, ProcessingJob.lease_owner == worker_id, ProcessingJob.lease_token == lease_token, ProcessingJob.lease_expires_at > now).values` with the arguments detailed below — Attach column assignments to the UPDATE/INSERT expression without executing it; first obtain the receiver: `update(ProcessingJob).where` with the arguments detailed below — Add SQL filtering predicates; multiple supplied predicates are combined with AND. |
| L469 | `update(ProcessingJob)` — Construct a SQL UPDATE expression; execution and commit are separate operations. |
| L470 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L471 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.id` equals `job_id`. |
| L472 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.status` equals `STATUS_RUNNING`. |
| L473 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.lease_owner` equals `worker_id`. |
| L474 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.lease_token` equals `lease_token`. |
| L475 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.lease_expires_at` is greater than `now`. |
| L476 | Close the expression/container begun at L469; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L477 | Attach column assignments to the UPDATE/INSERT expression without executing it; apply this method to the result built by the preceding chain. |
| L478 | Close the expression/container begun at L468; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L479 | Compute the return value: `bool(result.rowcount)` — Convert the value's truthiness to True or False. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `complete_job(session, *, job_id, lease_token, worker_id, chunk_count=None) -> bool`

Locks the job row. Missing is false; already-succeeded cleanup is true, and already-succeeded processing is true only if its version is still the document active pointer. Cleanup completion requires only current lease; processing uses `evaluate_publication`. Process success requires an explicit chunk count or `progress_total`, then writes document `Completed`, active version/count/time/Chroma references and clears its error. Both kinds set job succeeded, clear stage/errors/lease owner/expiry, set finish time, and flush. Returns true on success, false for a rejected fence. It does not hard-delete document/project rows or delete provider data; only the job row is explicitly locked by this function.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-complete-job"></a>

#### Line-by-line execution

[Current source: lines 487–561](../../../../Backend/app/jobs/queue.py#L487-L561). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `lease_token` | `int`; required; keyword-only | Monotonic claim token used to reject stale worker writes. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `chunk_count` | `int \| None`; default `None`; keyword-only | Number of chunks to record when publishing a processed document. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 487 | def complete_job(
 488 |     session: Session,
 489 |     *,
 490 |     job_id: UUID,
 491 |     lease_token: int,
 492 |     worker_id: str,
 493 |     chunk_count: int | None = None,
 494 | ) -> bool:
 495 |     """Publish success in the caller's transaction after fencing checks.
 496 | 
 497 |     For ``process_document`` this is the atomic publication: verify the
 498 |     running job + unexpired lease/token + expected epoch + live
 499 |     document/project, then set the document ``Completed`` (active
 500 |     version, chunk count, processed time) and the job ``succeeded``.
 501 |     Returns ``False`` -- writing nothing -- when the claim is stale.
 502 |     Re-completing an already-published version returns ``True`` as a
 503 |     no-op (lost commit acknowledgment).  For ``delete_document`` the
 504 |     job is marked ``succeeded`` without touching the document row (the
 505 |     tombstone/hard-delete ordering belongs to A3).
 506 |     """
 507 |     now = utcnow()
 508 |     job = session.scalar(
 509 |         select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()
 510 |     )
 511 |     if job is None:
 512 |         return False
 513 |     if job.status == STATUS_SUCCEEDED:
 514 |         if job.kind != KIND_PROCESS:
 515 |             return True
 516 |         document = session.get(Document, job.target_document_id)
 517 |         return bool(document is not None and document.active_index_version == job.index_version)
 518 |     document = session.get(Document, job.target_document_id)
 519 |     project = session.get(Project, job.project_id)
 520 |     if job.kind == KIND_DELETE:
 521 |         # Cleanup jobs intentionally run *after* the tombstone, so only
 522 |         # the live lease/token fences completion.  Document/project
 523 |         # liveness and the process-job publication checks do not apply.
 524 |         if not lease_is_current(
 525 |             status=job.status,
 526 |             lease_owner=job.lease_owner,
 527 |             lease_token=job.lease_token,
 528 |             lease_expires_at=job.lease_expires_at,
 529 |             worker_id=worker_id,
 530 |             token=lease_token,
 531 |             now=now,
 532 |         ):
 533 |             return False
 534 |     else:
 535 |         allowed, _reason = evaluate_publication(
 536 |             job, document, project, worker_id=worker_id, lease_token=lease_token, now=now
 537 |         )
 538 |         if not allowed:
 539 |             return False
 540 |     if job.kind == KIND_PROCESS:
 541 |         count = chunk_count if chunk_count is not None else job.progress_total
 542 |         if count is None:
 543 |             raise ValueError(
 544 |                 "complete_job needs chunk_count (or progress_total) for process jobs"
 545 |             )
 546 |         assert document is not None  # evaluate_publication guarantees it
 547 |         document.status = "Completed"
 548 |         document.active_index_version = job.index_version
 549 |         document.chunk_count = int(count)
 550 |         document.processed_at = now
 551 |         document.processing_error = None
 552 |         document.chroma_collection = COLLECTION_NAME
 553 |         document.chroma_document_id = str(job.index_version)
 554 |     job.status = STATUS_SUCCEEDED
 555 |     job.stage = None
 556 |     job.finished_at = now
 557 |     job.last_error_code = None
 558 |     job.last_error_message = None
 559 |     _clear_lease(job)
 560 |     session.flush()
 561 |     return True
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L487 | Define `complete_job`; bind its arguments when called. The body executes only when invoked. |
| L488 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L489 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L490 | Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. |
| L491 | Declare parameter `lease_token` with annotation `int`. Monotonic claim token used to reject stale worker writes. |
| L492 | Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. |
| L493 | Declare parameter `chunk_count` with annotation `int \| None`. Number of chunks to record when publishing a processed document. |
| L494 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L495 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L497 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L498 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L499 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L500 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L501 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L502 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L503 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L504 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L505 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L506 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L507 | Evaluate the right-hand side, then bind/store it in `now`: `utcnow()` — Read the current timezone-aware UTC timestamp. |
| L508 | Evaluate the right-hand side, then bind/store it in `job`: `session.scalar(select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update())` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()` — Request row locks until transaction end; skip_locked=True avoids waiting on rows claimed elsewhere; first obtain the receiver: `select(ProcessingJob).where(ProcessingJob.id == job_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND. |
| L509 | `select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()` — Request row locks until transaction end; skip_locked=True avoids waiting on rows claimed elsewhere; first obtain the receiver: `select(ProcessingJob).where(ProcessingJob.id == job_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L510 | Close the expression/container begun at L508; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L511 | Evaluate the branch condition: compare whether `job` is the same object as `None`. If truthy, enter L512; otherwise skip this indented block and continue after it. |
| L512 | Compute the return value: `False`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L513 | Evaluate the branch condition: compare whether `job.status` equals `STATUS_SUCCEEDED`. If truthy, enter L514; otherwise skip this indented block and continue after it. |
| L514 | Evaluate the branch condition: compare whether `job.kind` differs from `KIND_PROCESS`. If truthy, enter L515; otherwise skip this indented block and continue after it. |
| L515 | Compute the return value: `True`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L516 | Evaluate the right-hand side, then bind/store it in `document`: `session.get(Document, job.target_document_id)` — Look up the mapped object by primary key, using the session identity map when possible, otherwise SQL. |
| L517 | Compute the return value: `bool(document is not None and document.active_index_version == job.index_version)` — Convert the value's truthiness to True or False. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L518 | Evaluate the right-hand side, then bind/store it in `document`: `session.get(Document, job.target_document_id)` — Look up the mapped object by primary key, using the session identity map when possible, otherwise SQL. |
| L519 | Evaluate the right-hand side, then bind/store it in `project`: `session.get(Project, job.project_id)` — Look up the mapped object by primary key, using the session identity map when possible, otherwise SQL. |
| L520 | Evaluate the branch condition: compare whether `job.kind` equals `KIND_DELETE`. If truthy, enter L524; otherwise enter the alternative at L535. |
| L521 | Comment only: Cleanup jobs intentionally run *after* the tombstone, so only. It does not execute; the neighboring code determines behavior. |
| L522 | Comment only: the live lease/token fences completion.  Document/project. It does not execute; the neighboring code determines behavior. |
| L523 | Comment only: liveness and the process-job publication checks do not apply.. It does not execute; the neighboring code determines behavior. |
| L524 | Evaluate the branch condition: invert the truthiness of `lease_is_current(status=job.status, lease_owner=job.lease_owner, lease_token=job.lease_token, lease_expires_at=job.lease_expires_at, worker_id=worker_id, token=lease_token, now=now)`. If truthy, enter L533; otherwise skip this indented block and continue after it. |
| L525 | Supply `status` = `job.status`.  Evaluate the value as: the `status` attribute of `job`. |
| L526 | Supply `lease_owner` = `job.lease_owner`.  Evaluate the value as: the `lease_owner` attribute of `job`. |
| L527 | Supply `lease_token` = `job.lease_token`. Monotonic claim token used to reject stale worker writes. Evaluate the value as: the `lease_token` attribute of `job`. |
| L528 | Supply `lease_expires_at` = `job.lease_expires_at`.  Evaluate the value as: the `lease_expires_at` attribute of `job`. |
| L529 | Supply `worker_id` = `worker_id`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: the current `worker_id` value. |
| L530 | Supply `token` = `lease_token`. Expected claim/generation token compared with persisted state. Evaluate the value as: the current `lease_token` value. |
| L531 | Supply `now` = `now`. Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. Evaluate the value as: the current `now` value. |
| L532 | Close the expression/container begun at L524; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L533 | Compute the return value: `False`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L534 | Enter this alternative only when the associated condition was false (or the associated try/loop completed without its exceptional exit). |
| L535 | Evaluate the right-hand side, then bind/store it in `(allowed, _reason)`: `evaluate_publication(job, document, project, worker_id=worker_id, lease_token=lease_token, now=now)` — Call [evaluate_publication](#walk-evaluate-publication) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L536 | Supply `worker_id` = `worker_id`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: the current `worker_id` value. Supply `lease_token` = `lease_token`. Monotonic claim token used to reject stale worker writes. Evaluate the value as: the current `lease_token` value. Supply `now` = `now`. Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. Evaluate the value as: the current `now` value. |
| L537 | Close the expression/container begun at L535; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L538 | Evaluate the branch condition: invert the truthiness of `allowed`. If truthy, enter L539; otherwise skip this indented block and continue after it. |
| L539 | Compute the return value: `False`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L540 | Evaluate the branch condition: compare whether `job.kind` equals `KIND_PROCESS`. If truthy, enter L541; otherwise skip this indented block and continue after it. |
| L541 | Evaluate the right-hand side, then bind/store it in `count`: check `chunk_count is not None`; when true use the current `chunk_count` value, otherwise the `progress_total` attribute of `job` (only the selected branch is evaluated). |
| L542 | Evaluate the branch condition: compare whether `count` is the same object as `None`. If truthy, enter L543; otherwise skip this indented block and continue after it. |
| L543 | Raise `ValueError('complete_job needs chunk_count (or progress_total) for process jobs')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L544 | Supply positional argument 1 to `ValueError`: `'complete_job needs chunk_count (or progress_total) for process jobs'`. |
| L545 | Close the expression/container begun at L543; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L546 | Check `document is not None`; when false raise AssertionError. Python optimization (-O) removes asserts, so this is not an unconditional validation mechanism. |
| L547 | Evaluate the right-hand side, then bind/store it in `document.status`: `'Completed'`. |
| L548 | Evaluate the right-hand side, then bind/store it in `document.active_index_version`: the `index_version` attribute of `job`. |
| L549 | Evaluate the right-hand side, then bind/store it in `document.chunk_count`: `int(count)` — Convert the input to an integer (using the optional numeric base). |
| L550 | Evaluate the right-hand side, then bind/store it in `document.processed_at`: the current `now` value. |
| L551 | Evaluate the right-hand side, then bind/store it in `document.processing_error`: None (no value). |
| L552 | Evaluate the right-hand side, then bind/store it in `document.chroma_collection`: the current `COLLECTION_NAME` value. |
| L553 | Evaluate the right-hand side, then bind/store it in `document.chroma_document_id`: `str(job.index_version)` — Convert the input to its string representation. |
| L554 | Evaluate the right-hand side, then bind/store it in `job.status`: the current `STATUS_SUCCEEDED` value. |
| L555 | Evaluate the right-hand side, then bind/store it in `job.stage`: None (no value). |
| L556 | Evaluate the right-hand side, then bind/store it in `job.finished_at`: the current `now` value. |
| L557 | Evaluate the right-hand side, then bind/store it in `job.last_error_code`: None (no value). |
| L558 | Evaluate the right-hand side, then bind/store it in `job.last_error_message`: None (no value). |
| L559 | `_clear_lease(job)` — Call [_clear_lease](#walk--clear-lease) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L560 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L561 | Compute the return value: `True`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `fail_job(session, *, job_id, lease_token, worker_id, error_code, error_message, retryable, backoff_base_seconds=5, backoff_cap_seconds=3600) -> bool`

Locks and checks the current lease; missing/stale returns false. Copies diagnostics as supplied. If retryable with attempts remaining, sets retry-wait/no stage/new due time using seeded exponential backoff and clears lease owner/expiry. Otherwise marks failed/finished and, for a live matching-epoch process document, marks it failed with combined code/message. Flushes and returns true. Terminal failure does not clear stage; retryable failure does not reset document status to `Pending`. Message redaction/truncation is not implemented here.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-fail-job"></a>

#### Line-by-line execution

[Current source: lines 564–627](../../../../Backend/app/jobs/queue.py#L564-L627). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `lease_token` | `int`; required; keyword-only | Monotonic claim token used to reject stale worker writes. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `error_code` | `str`; required; keyword-only | Machine-readable failure category stored or exposed by the operation. |
| `error_message` | `str`; required; keyword-only | Human-readable failure detail; truncation alone does not redact sensitive content. |
| `retryable` | `bool`; required; keyword-only | Whether the failure may be retried while the attempt budget remains. |
| `backoff_base_seconds` | `int`; default `DEFAULT_BACKOFF_BASE_SECONDS`; keyword-only | Base retry delay, doubled with successive attempts before capping/jitter. |
| `backoff_cap_seconds` | `int`; default `DEFAULT_BACKOFF_CAP_SECONDS`; keyword-only | Maximum retry-delay bound passed to the backoff calculation. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 564 | def fail_job(
 565 |     session: Session,
 566 |     *,
 567 |     job_id: UUID,
 568 |     lease_token: int,
 569 |     worker_id: str,
 570 |     error_code: str,
 571 |     error_message: str,
 572 |     retryable: bool,
 573 |     backoff_base_seconds: int = DEFAULT_BACKOFF_BASE_SECONDS,
 574 |     backoff_cap_seconds: int = DEFAULT_BACKOFF_CAP_SECONDS,
 575 | ) -> bool:
 576 |     """Move to ``retry_wait`` (bounded backoff) or terminal ``failed``.
 577 | 
 578 |     Guarded by the live lease; returns ``False`` (writing nothing) for
 579 |     a stale holder.  On terminal failure of a process job the document
 580 |     is marked ``Failed`` with the safe error summary -- but only when
 581 |     the document is still live and its epoch still matches, so a stale
 582 |     worker can never clobber a newer epoch's ``Pending`` state.
 583 |     """
 584 |     now = utcnow()
 585 |     job = session.scalar(
 586 |         select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()
 587 |     )
 588 |     if job is None or not lease_is_current(
 589 |         status=job.status,
 590 |         lease_owner=job.lease_owner,
 591 |         lease_token=job.lease_token,
 592 |         lease_expires_at=job.lease_expires_at,
 593 |         worker_id=worker_id,
 594 |         token=lease_token,
 595 |         now=now,
 596 |     ):
 597 |         return False
 598 |     job.last_error_code = error_code
 599 |     job.last_error_message = error_message
 600 |     will_retry = retryable and (job.attempt_count or 0) < (job.max_attempts or 1)
 601 |     if will_retry:
 602 |         job.status = STATUS_RETRY_WAIT
 603 |         job.stage = None
 604 |         job.available_at = now + timedelta(
 605 |             seconds=compute_backoff_seconds(
 606 |                 job.attempt_count or 1,
 607 |                 base_seconds=backoff_base_seconds,
 608 |                 cap_seconds=backoff_cap_seconds,
 609 |                 jitter_seed=str(job.id),
 610 |             )
 611 |         )
 612 |         _clear_lease(job)
 613 |     else:
 614 |         job.status = STATUS_FAILED
 615 |         job.finished_at = now
 616 |         _clear_lease(job)
 617 |         if job.kind == KIND_PROCESS:
 618 |             document = session.get(Document, job.target_document_id)
 619 |             if (
 620 |                 document is not None
 621 |                 and document.deleted_at is None
 622 |                 and document.processing_epoch == job.target_epoch
 623 |             ):
 624 |                 document.status = "Failed"
 625 |                 document.processing_error = f"{error_code}: {error_message}"
 626 |     session.flush()
 627 |     return True
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L564 | Define `fail_job`; bind its arguments when called. The body executes only when invoked. |
| L565 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L566 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L567 | Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. |
| L568 | Declare parameter `lease_token` with annotation `int`. Monotonic claim token used to reject stale worker writes. |
| L569 | Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. |
| L570 | Declare parameter `error_code` with annotation `str`. Machine-readable failure category stored or exposed by the operation. |
| L571 | Declare parameter `error_message` with annotation `str`. Human-readable failure detail; truncation alone does not redact sensitive content. |
| L572 | Declare parameter `retryable` with annotation `bool`. Whether the failure may be retried while the attempt budget remains. |
| L573 | Declare parameter `backoff_base_seconds` with annotation `int`. Base retry delay, doubled with successive attempts before capping/jitter. |
| L574 | Declare parameter `backoff_cap_seconds` with annotation `int`. Maximum retry-delay bound passed to the backoff calculation. |
| L575 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L576 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L578 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L579 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L580 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L581 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L582 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L583 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L584 | Evaluate the right-hand side, then bind/store it in `now`: `utcnow()` — Read the current timezone-aware UTC timestamp. |
| L585 | Evaluate the right-hand side, then bind/store it in `job`: `session.scalar(select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update())` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()` — Request row locks until transaction end; skip_locked=True avoids waiting on rows claimed elsewhere; first obtain the receiver: `select(ProcessingJob).where(ProcessingJob.id == job_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND. |
| L586 | `select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()` — Request row locks until transaction end; skip_locked=True avoids waiting on rows claimed elsewhere; first obtain the receiver: `select(ProcessingJob).where(ProcessingJob.id == job_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L587 | Close the expression/container begun at L585; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L588 | Evaluate the branch condition: evaluate `job is None or not lease_is_current(status=job.status, lease_owner=job.lease_owner, lease_token=job.lease_token, lease_expires_at=job.lease_expires_at, worker_id=worker_id, token=lease_token, now=now)` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L597; otherwise skip this indented block and continue after it. |
| L589 | Supply `status` = `job.status`.  Evaluate the value as: the `status` attribute of `job`. |
| L590 | Supply `lease_owner` = `job.lease_owner`.  Evaluate the value as: the `lease_owner` attribute of `job`. |
| L591 | Supply `lease_token` = `job.lease_token`. Monotonic claim token used to reject stale worker writes. Evaluate the value as: the `lease_token` attribute of `job`. |
| L592 | Supply `lease_expires_at` = `job.lease_expires_at`.  Evaluate the value as: the `lease_expires_at` attribute of `job`. |
| L593 | Supply `worker_id` = `worker_id`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: the current `worker_id` value. |
| L594 | Supply `token` = `lease_token`. Expected claim/generation token compared with persisted state. Evaluate the value as: the current `lease_token` value. |
| L595 | Supply `now` = `now`. Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. Evaluate the value as: the current `now` value. |
| L596 | Close the expression/container begun at L588; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L597 | Compute the return value: `False`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L598 | Evaluate the right-hand side, then bind/store it in `job.last_error_code`: the current `error_code` value. |
| L599 | Evaluate the right-hand side, then bind/store it in `job.last_error_message`: the current `error_message` value. |
| L600 | Evaluate the right-hand side, then bind/store it in `will_retry`: evaluate `retryable and (job.attempt_count or 0) < (job.max_attempts or 1)` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. |
| L601 | Evaluate the branch condition: the current `will_retry` value. If truthy, enter L602; otherwise enter the alternative at L614. |
| L602 | Evaluate the right-hand side, then bind/store it in `job.status`: the current `STATUS_RETRY_WAIT` value. |
| L603 | Evaluate the right-hand side, then bind/store it in `job.stage`: None (no value). |
| L604 | Evaluate the right-hand side, then bind/store it in `job.available_at`: add/concatenate `now` and `timedelta(seconds=compute_backoff_seconds(job.attempt_count or 1, base_seconds=backoff_base_seconds, cap_seconds=backoff_cap_seconds, jitter_seed=str(job.id)))`, following the parentheses/operator precedence shown in `now + timedelta(seconds=compute_backoff_seconds(job.attempt_count or 1, base_seconds=backoff_base_seconds, cap_seconds=backoff_cap_seconds, jitter_seed=str(job.id)))`. |
| L605 | Supply `seconds` = `compute_backoff_seconds(job.attempt_count or 1, base_seconds=backoff_base_seconds, cap_seconds=backoff_cap_seconds, jitter_seed=str(job.id))`.  Evaluate the value as: `compute_backoff_seconds(job.attempt_count or 1, base_seconds=backoff_base_seconds, cap_seconds=backoff_cap_seconds, jitter_seed=str(job.id))` — Call [compute_backoff_seconds](errors.md#walk-compute-backoff-seconds) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L606 | Continue the enclosing expression: evaluate `job.attempt_count or 1` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L607 | Supply `base_seconds` = `backoff_base_seconds`.  Evaluate the value as: the current `backoff_base_seconds` value. |
| L608 | Supply `cap_seconds` = `backoff_cap_seconds`.  Evaluate the value as: the current `backoff_cap_seconds` value. |
| L609 | Supply `jitter_seed` = `str(job.id)`.  Evaluate the value as: `str(job.id)` — Convert the input to its string representation. |
| L610 | Close the expression/container begun at L605; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L611 | Close the expression/container begun at L604; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L612 | `_clear_lease(job)` — Call [_clear_lease](#walk--clear-lease) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L613 | Enter this alternative only when the associated condition was false (or the associated try/loop completed without its exceptional exit). |
| L614 | Evaluate the right-hand side, then bind/store it in `job.status`: the current `STATUS_FAILED` value. |
| L615 | Evaluate the right-hand side, then bind/store it in `job.finished_at`: the current `now` value. |
| L616 | `_clear_lease(job)` — Call [_clear_lease](#walk--clear-lease) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L617 | Evaluate the branch condition: compare whether `job.kind` equals `KIND_PROCESS`. If truthy, enter L618; otherwise skip this indented block and continue after it. |
| L618 | Evaluate the right-hand side, then bind/store it in `document`: `session.get(Document, job.target_document_id)` — Look up the mapped object by primary key, using the session identity map when possible, otherwise SQL. |
| L619 | Evaluate the branch condition: evaluate `document is not None and document.deleted_at is None and (document.processing_epoch == job.target_epoch)` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L624; otherwise skip this indented block and continue after it. |
| L620 | Continue the enclosing expression: evaluate `document is not None and document.deleted_at is None and (document.processing_epoch == job.target_epoch)` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. |
| L621 | Continue the enclosing expression: compare whether `document.deleted_at` is the same object as `None`. |
| L622 | Continue the enclosing expression: compare whether `document.processing_epoch` equals `job.target_epoch`. |
| L623 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L624 | Evaluate the right-hand side, then bind/store it in `document.status`: `'Failed'`. |
| L625 | Evaluate the right-hand side, then bind/store it in `document.processing_error`: format a string by inserting `error_code`, `error_message` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L626 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L627 | Compute the return value: `True`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `cancel_job(session, *, job_id, reason: str) -> bool`

Locks a job, returns false for missing/terminal state, otherwise increments token, records cancellation/reason/finish time, clears lease owner/expiry, and flushes. This worker-side cancellation differs from the request adapter's simpler cancellation in `repositories.documents`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-cancel-job"></a>

#### Line-by-line execution

[Current source: lines 630–649](../../../../Backend/app/jobs/queue.py#L630-L649). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `reason` | `str`; required; keyword-only | Human-readable cancellation/decision reason recorded or returned by this operation. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 630 | def cancel_job(session: Session, *, job_id: UUID, reason: str) -> bool:
 631 |     """Cancel a nonterminal job (deletion/retry invalidation).
 632 | 
 633 |     Bumps ``lease_token`` so any in-flight worker holding the previous
 634 |     token is fenced out, then marks the job ``cancelled``.  Returns
 635 |     ``False`` when the job is already terminal or missing.
 636 |     """
 637 |     job = session.scalar(
 638 |         select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()
 639 |     )
 640 |     if job is None or job.status in TERMINAL_STATUSES:
 641 |         return False
 642 |     job.lease_token = (job.lease_token or 0) + 1
 643 |     job.status = STATUS_CANCELLED
 644 |     job.finished_at = utcnow()
 645 |     job.last_error_code = CANCELLED_MARKER
 646 |     job.last_error_message = reason
 647 |     _clear_lease(job)
 648 |     session.flush()
 649 |     return True
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L630 | Define `cancel_job`; bind its arguments when called. The body executes only when invoked. |
| L631 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L633 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L634 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L635 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L636 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L637 | Evaluate the right-hand side, then bind/store it in `job`: `session.scalar(select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update())` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()` — Request row locks until transaction end; skip_locked=True avoids waiting on rows claimed elsewhere; first obtain the receiver: `select(ProcessingJob).where(ProcessingJob.id == job_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND. |
| L638 | `select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()` — Request row locks until transaction end; skip_locked=True avoids waiting on rows claimed elsewhere; first obtain the receiver: `select(ProcessingJob).where(ProcessingJob.id == job_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L639 | Close the expression/container begun at L637; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L640 | Evaluate the branch condition: evaluate `job is None or job.status in TERMINAL_STATUSES` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L641; otherwise skip this indented block and continue after it. |
| L641 | Compute the return value: `False`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L642 | Evaluate the right-hand side, then bind/store it in `job.lease_token`: add/concatenate `job.lease_token or 0` and `1`, following the parentheses/operator precedence shown in `(job.lease_token or 0) + 1`. |
| L643 | Evaluate the right-hand side, then bind/store it in `job.status`: the current `STATUS_CANCELLED` value. |
| L644 | Evaluate the right-hand side, then bind/store it in `job.finished_at`: `utcnow()` — Read the current timezone-aware UTC timestamp. |
| L645 | Evaluate the right-hand side, then bind/store it in `job.last_error_code`: the current `CANCELLED_MARKER` value. |
| L646 | Evaluate the right-hand side, then bind/store it in `job.last_error_message`: the current `reason` value. |
| L647 | `_clear_lease(job)` — Call [_clear_lease](#walk--clear-lease) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L648 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L649 | Compute the return value: `True`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `load_job_context(session, job_id: UUID) -> JobContext | None`

Loads job and target document by primary key and copies their fields into a context; missing job returns null. Snapshot expectations read **only** `expected_size_bytes` and `expected_sha256`. Upload producers currently store `file_size` and `content_sha256`; live document size/hash are copied to separate `doc_*` fields, not substituted into expectations. Storage ID/name properties do have the fallbacks described above.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-load-job-context"></a>

#### Line-by-line execution

[Current source: lines 657–694](../../../../Backend/app/jobs/queue.py#L657-L694). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `job_id` | `UUID`; required; positional or keyword | Durable processing-job UUID. |

**Declared result:** `JobContext | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 657 | def load_job_context(session: Session, job_id: UUID) -> JobContext | None:
 658 |     """Load a job plus its snapshot/document facts for the worker."""
 659 |     job = session.get(ProcessingJob, job_id)
 660 |     if job is None:
 661 |         return None
 662 |     document = session.get(Document, job.target_document_id)
 663 |     snapshot = dict(job.resource_snapshot or {})
 664 |     return JobContext(
 665 |         job_id=job.id,
 666 |         kind=job.kind,
 667 |         status=job.status,
 668 |         target_document_id=job.target_document_id,
 669 |         target_epoch=job.target_epoch,
 670 |         owner_user_id=job.owner_user_id,
 671 |         project_id=job.project_id,
 672 |         document_id=job.document_id,
 673 |         attempt_count=job.attempt_count or 0,
 674 |         max_attempts=job.max_attempts or 1,
 675 |         lease_token=job.lease_token,
 676 |         index_version=job.index_version,
 677 |         resource_snapshot=snapshot,
 678 |         bucket_id=_snapshot_get(snapshot, "bucket_id"),
 679 |         file_id=_snapshot_get(snapshot, "file_id"),
 680 |         expected_size_bytes=_snapshot_get(snapshot, "expected_size_bytes"),
 681 |         expected_sha256=_snapshot_get(snapshot, "expected_sha256"),
 682 |         file_name=_snapshot_get(snapshot, "file_name"),
 683 |         doc_file_name=document.file_name if document else None,
 684 |         doc_appwrite_file_id=document.appwrite_file_id if document else None,
 685 |         doc_file_size=document.file_size if document else None,
 686 |         doc_content_sha256=document.content_sha256 if document else None,
 687 |         doc_processing_epoch=document.processing_epoch if document else None,
 688 |         doc_status=document.status if document else None,
 689 |         doc_deleted=bool(document is not None and document.deleted_at is not None),
 690 |         doc_exists=document is not None,
 691 |         doc_active_index_version=document.active_index_version if document else None,
 692 |         created_at=job.created_at,
 693 |         updated_at=job.updated_at,
 694 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L657 | Define `load_job_context`; bind its arguments when called. The body executes only when invoked. |
| L658 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L659 | Evaluate the right-hand side, then bind/store it in `job`: `session.get(ProcessingJob, job_id)` — Look up the mapped object by primary key, using the session identity map when possible, otherwise SQL. |
| L660 | Evaluate the branch condition: compare whether `job` is the same object as `None`. If truthy, enter L661; otherwise skip this indented block and continue after it. |
| L661 | Compute the return value: None (no value). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L662 | Evaluate the right-hand side, then bind/store it in `document`: `session.get(Document, job.target_document_id)` — Look up the mapped object by primary key, using the session identity map when possible, otherwise SQL. |
| L663 | Evaluate the right-hand side, then bind/store it in `snapshot`: `dict(job.resource_snapshot or {})` — Build a mapping from the supplied items/keywords; copying a mapping is shallow. |
| L664 | Compute the return value: `JobContext` with the arguments detailed below — Construct `JobContext` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L665 | Supply `job_id` = `job.id`. Durable processing-job UUID. Evaluate the value as: the `id` attribute of `job`. |
| L666 | Supply `kind` = `job.kind`.  Evaluate the value as: the `kind` attribute of `job`. |
| L667 | Supply `status` = `job.status`.  Evaluate the value as: the `status` attribute of `job`. |
| L668 | Supply `target_document_id` = `job.target_document_id`. Immutable target UUID retained even when the live document relationship disappears. Evaluate the value as: the `target_document_id` attribute of `job`. |
| L669 | Supply `target_epoch` = `job.target_epoch`. Expected document processing epoch used to invalidate obsolete attempts. Evaluate the value as: the `target_epoch` attribute of `job`. |
| L670 | Supply `owner_user_id` = `job.owner_user_id`. Internal owner UUID copied into the job's durable ownership snapshot. Evaluate the value as: the `owner_user_id` attribute of `job`. |
| L671 | Supply `project_id` = `job.project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the `project_id` attribute of `job`. |
| L672 | Supply `document_id` = `job.document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the `document_id` attribute of `job`. |
| L673 | Supply `attempt_count` = `job.attempt_count or 0`. Number of attempts already claimed; used to decide retries and calculate delay. Evaluate the value as: evaluate `job.attempt_count or 0` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L674 | Supply `max_attempts` = `job.max_attempts or 1`. Maximum number of claims before retryable failures become terminal. Evaluate the value as: evaluate `job.max_attempts or 1` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L675 | Supply `lease_token` = `job.lease_token`. Monotonic claim token used to reject stale worker writes. Evaluate the value as: the `lease_token` attribute of `job`. |
| L676 | Supply `index_version` = `job.index_version`. UUID of one document's vector-index namespace, separate from its active publication pointer. Evaluate the value as: the `index_version` attribute of `job`. |
| L677 | Supply `resource_snapshot` = `snapshot`. JSON-compatible resource facts copied into a durable job. Evaluate the value as: the current `snapshot` value. |
| L678 | Supply `bucket_id` = `_snapshot_get(snapshot, 'bucket_id')`. Appwrite bucket identifier. Evaluate the value as: `_snapshot_get(snapshot, 'bucket_id')` — Call [_snapshot_get](#walk--snapshot-get) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L679 | Supply `file_id` = `_snapshot_get(snapshot, 'file_id')`. Reserved Appwrite storage-object identifier. Evaluate the value as: `_snapshot_get(snapshot, 'file_id')` — Call [_snapshot_get](#walk--snapshot-get) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L680 | Supply `expected_size_bytes` = `_snapshot_get(snapshot, 'expected_size_bytes')`. Expected storage length in bytes, or null when no expectation is available. Evaluate the value as: `_snapshot_get(snapshot, 'expected_size_bytes')` — Call [_snapshot_get](#walk--snapshot-get) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L681 | Supply `expected_sha256` = `_snapshot_get(snapshot, 'expected_sha256')`.  Evaluate the value as: `_snapshot_get(snapshot, 'expected_sha256')` — Call [_snapshot_get](#walk--snapshot-get) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L682 | Supply `file_name` = `_snapshot_get(snapshot, 'file_name')`. Display PDF filename; immutable IDs establish ownership and evidence identity. Evaluate the value as: `_snapshot_get(snapshot, 'file_name')` — Call [_snapshot_get](#walk--snapshot-get) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L683 | Supply `doc_file_name` = `document.file_name if document else None`.  Evaluate the value as: check `document`; when true use the `file_name` attribute of `document`, otherwise None (no value) (only the selected branch is evaluated). |
| L684 | Supply `doc_appwrite_file_id` = `document.appwrite_file_id if document else None`.  Evaluate the value as: check `document`; when true use the `appwrite_file_id` attribute of `document`, otherwise None (no value) (only the selected branch is evaluated). |
| L685 | Supply `doc_file_size` = `document.file_size if document else None`.  Evaluate the value as: check `document`; when true use the `file_size` attribute of `document`, otherwise None (no value) (only the selected branch is evaluated). |
| L686 | Supply `doc_content_sha256` = `document.content_sha256 if document else None`.  Evaluate the value as: check `document`; when true use the `content_sha256` attribute of `document`, otherwise None (no value) (only the selected branch is evaluated). |
| L687 | Supply `doc_processing_epoch` = `document.processing_epoch if document else None`.  Evaluate the value as: check `document`; when true use the `processing_epoch` attribute of `document`, otherwise None (no value) (only the selected branch is evaluated). |
| L688 | Supply `doc_status` = `document.status if document else None`.  Evaluate the value as: check `document`; when true use the `status` attribute of `document`, otherwise None (no value) (only the selected branch is evaluated). |
| L689 | Supply `doc_deleted` = `bool(document is not None and document.deleted_at is not None)`.  Evaluate the value as: `bool(document is not None and document.deleted_at is not None)` — Convert the value's truthiness to True or False. |
| L690 | Supply `doc_exists` = `document is not None`.  Evaluate the value as: compare whether `document` is not the same object as `None`. |
| L691 | Supply `doc_active_index_version` = `document.active_index_version if document else None`.  Evaluate the value as: check `document`; when true use the `active_index_version` attribute of `document`, otherwise None (no value) (only the selected branch is evaluated). |
| L692 | Supply `created_at` = `job.created_at`.  Evaluate the value as: the `created_at` attribute of `job`. |
| L693 | Supply `updated_at` = `job.updated_at`.  Evaluate the value as: the `updated_at` attribute of `job`. |
| L694 | Close the expression/container begun at L664; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `find_expired_awaiting_upload(session, *, cutoff: datetime, limit: int) -> list[JobContext]`

Locks awaiting-upload rows created at/before cutoff, oldest-first, bounded with `SKIP LOCKED`; converts each surviving row via `load_job_context`. Returns contexts for provider inspection after the transaction ends.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-find-expired-awaiting-upload"></a>

#### Line-by-line execution

[Current source: lines 697–716](../../../../Backend/app/jobs/queue.py#L697-L716). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `cutoff` | `datetime`; required; keyword-only | Inclusive age cutoff used to select old work. |
| `limit` | `int`; required; keyword-only | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |

**Declared result:** `list[JobContext]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 697 | def find_expired_awaiting_upload(
 698 |     session: Session, *, cutoff: datetime, limit: int
 699 | ) -> list[JobContext]:
 700 |     """Jobs still ``awaiting_upload`` past their TTL (reconciliation)."""
 701 |     rows = session.scalars(
 702 |         select(ProcessingJob)
 703 |         .where(
 704 |             ProcessingJob.status == STATUS_AWAITING_UPLOAD,
 705 |             ProcessingJob.created_at <= cutoff,
 706 |         )
 707 |         .order_by(ProcessingJob.created_at)
 708 |         .limit(limit)
 709 |         .with_for_update(skip_locked=True)
 710 |     ).all()
 711 |     contexts = []
 712 |     for row in rows:
 713 |         context = load_job_context(session, row.id)
 714 |         if context is not None:
 715 |             contexts.append(context)
 716 |     return contexts
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L697 | Define `find_expired_awaiting_upload`; bind its arguments when called. The body executes only when invoked. |
| L698 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `cutoff` with annotation `datetime`. Inclusive age cutoff used to select old work. Declare parameter `limit` with annotation `int`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. |
| L699 | Finish/continue the signature; the declared return annotation is `list[JobContext]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L700 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L701 | Evaluate the right-hand side, then bind/store it in `rows`: `session.scalars(select(ProcessingJob).where(ProcessingJob.status == STATUS_AWAITING_UPLOAD, ProcessingJob.created_at <= cutoff).order_by(ProcessingJob.created_at).limit(limit).with_for_update(skip_locked=True)).all` with the arguments detailed below — Materialize all remaining values in this SQL result; first obtain the receiver: `session.scalars` with the arguments detailed below — Execute the SQL expression and expose first-column values through a ScalarResult. |
| L702 | `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L703 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L704 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.status` equals `STATUS_AWAITING_UPLOAD`. |
| L705 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.created_at` is at most `cutoff`. |
| L706 | Close the expression/container begun at L702; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L707 | Set SQL result ordering in the listed priority order; apply this method to the result built by the preceding chain. |
| L708 | Apply a SQL row limit; fetching limit+1 allows continuation detection; apply this method to the result built by the preceding chain. |
| L709 | Request row locks until transaction end; skip_locked=True avoids waiting on rows claimed elsewhere; apply this method to the result built by the preceding chain. |
| L710 | Continue the operation begun at L701: Evaluate the right-hand side, then bind/store it in `rows`: `session.scalars(select(ProcessingJob).where(ProcessingJob.status == STATUS_AWAITING_UPLOAD, ProcessingJob.created_at <= cutoff).order_by(ProcessingJob.created_at).limit(limit).with_for_update(skip_locked=True)).all` with the arguments detailed below — Materialize all remaining values in this SQL result; first obtain the receiver: `session.scalars` with the arguments detailed below — Execute the SQL expression and expose first-column values through a ScalarResult. |
| L711 | Evaluate the right-hand side, then bind/store it in `contexts`: build a list containing no items. |
| L712 | Iterate `rows` (the current `rows` value), assigning each item to `row`. Execute the indented body once per item; an empty iterable skips it. |
| L713 | Evaluate the right-hand side, then bind/store it in `context`: `load_job_context(session, row.id)` — Call [load_job_context](#walk-load-job-context) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L714 | Evaluate the branch condition: compare whether `context` is not the same object as `None`. If truthy, enter L715; otherwise skip this indented block and continue after it. |
| L715 | `contexts.append(context)` — Append one object to the mutable list in place. The return value is not assigned here. |
| L716 | Compute the return value: the current `contexts` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `apply_awaiting_upload_outcome(session, *, job_id, outcome, error_code=None, error_message=None) -> bool`

Locks and rechecks awaiting-upload state; missing/already-transitioned returns false. `queued` clears stage, makes the job due now, and for a live document copies optional `expected_*` snapshot values and sets upload completion time. `failed` records diagnostics/finish time, clears lease, and marks a live matching-epoch document failed. Unknown outcomes raise `ValueError`. Flushes and returns true. No storage inspection occurs inside this function.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-apply-awaiting-upload-outcome"></a>

#### Line-by-line execution

[Current source: lines 719–773](../../../../Backend/app/jobs/queue.py#L719-L773). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `outcome` | `str`; required; keyword-only | Recovery decision to apply after outside-transaction provider inspection. |
| `error_code` | `str \| None`; default `None`; keyword-only | Machine-readable failure category stored or exposed by the operation. |
| `error_message` | `str \| None`; default `None`; keyword-only | Human-readable failure detail; truncation alone does not redact sensitive content. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 719 | def apply_awaiting_upload_outcome(
 720 |     session: Session,
 721 |     *,
 722 |     job_id: UUID,
 723 |     outcome: str,
 724 |     error_code: str | None = None,
 725 |     error_message: str | None = None,
 726 | ) -> bool:
 727 |     """Apply a reconciliation outcome for an ``awaiting_upload`` job.
 728 | 
 729 |     ``outcome="queued"`` sets upload completion on the document (size,
 730 |     fingerprint, ``upload_completed_at``) and queues the job;
 731 |     ``outcome="failed"`` terminally fails job + document with the
 732 |     given classification.  Returns ``False`` when the job already left
 733 |     ``awaiting_upload`` (the normal upload path won the race -- the
 734 |     reconciliation was a no-op, which is also how a lost commit
 735 |     acknowledgment stays safe).
 736 |     """
 737 |     now = utcnow()
 738 |     job = session.scalar(
 739 |         select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()
 740 |     )
 741 |     if job is None or job.status != STATUS_AWAITING_UPLOAD:
 742 |         return False
 743 |     document = session.get(Document, job.target_document_id)
 744 |     snapshot = dict(job.resource_snapshot or {})
 745 |     if outcome == "queued":
 746 |         job.status = STATUS_QUEUED
 747 |         job.available_at = now
 748 |         job.stage = None
 749 |         if document is not None and document.deleted_at is None:
 750 |             if _snapshot_get(snapshot, "expected_size_bytes") is not None:
 751 |                 document.file_size = int(_snapshot_get(snapshot, "expected_size_bytes"))
 752 |             if _snapshot_get(snapshot, "expected_sha256") is not None:
 753 |                 document.content_sha256 = str(
 754 |                     _snapshot_get(snapshot, "expected_sha256")
 755 |                 )
 756 |             document.upload_completed_at = now
 757 |     elif outcome == "failed":
 758 |         job.status = STATUS_FAILED
 759 |         job.finished_at = now
 760 |         job.last_error_code = error_code
 761 |         job.last_error_message = error_message
 762 |         _clear_lease(job)
 763 |         if (
 764 |             document is not None
 765 |             and document.deleted_at is None
 766 |             and document.processing_epoch == job.target_epoch
 767 |         ):
 768 |             document.status = "Failed"
 769 |             document.processing_error = f"{error_code}: {error_message}"
 770 |     else:
 771 |         raise ValueError(f"unknown awaiting-upload outcome: {outcome!r}")
 772 |     session.flush()
 773 |     return True
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L719 | Define `apply_awaiting_upload_outcome`; bind its arguments when called. The body executes only when invoked. |
| L720 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L721 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L722 | Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. |
| L723 | Declare parameter `outcome` with annotation `str`. Recovery decision to apply after outside-transaction provider inspection. |
| L724 | Declare parameter `error_code` with annotation `str \| None`. Machine-readable failure category stored or exposed by the operation. |
| L725 | Declare parameter `error_message` with annotation `str \| None`. Human-readable failure detail; truncation alone does not redact sensitive content. |
| L726 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L727 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L729 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L730 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L731 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L732 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L733 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L734 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L735 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L736 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L737 | Evaluate the right-hand side, then bind/store it in `now`: `utcnow()` — Read the current timezone-aware UTC timestamp. |
| L738 | Evaluate the right-hand side, then bind/store it in `job`: `session.scalar(select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update())` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()` — Request row locks until transaction end; skip_locked=True avoids waiting on rows claimed elsewhere; first obtain the receiver: `select(ProcessingJob).where(ProcessingJob.id == job_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND. |
| L739 | `select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()` — Request row locks until transaction end; skip_locked=True avoids waiting on rows claimed elsewhere; first obtain the receiver: `select(ProcessingJob).where(ProcessingJob.id == job_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L740 | Close the expression/container begun at L738; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L741 | Evaluate the branch condition: evaluate `job is None or job.status != STATUS_AWAITING_UPLOAD` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L742; otherwise skip this indented block and continue after it. |
| L742 | Compute the return value: `False`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L743 | Evaluate the right-hand side, then bind/store it in `document`: `session.get(Document, job.target_document_id)` — Look up the mapped object by primary key, using the session identity map when possible, otherwise SQL. |
| L744 | Evaluate the right-hand side, then bind/store it in `snapshot`: `dict(job.resource_snapshot or {})` — Build a mapping from the supplied items/keywords; copying a mapping is shallow. |
| L745 | Evaluate the branch condition: compare whether `outcome` equals `'queued'`. If truthy, enter L746; otherwise enter the alternative at L757. |
| L746 | Evaluate the right-hand side, then bind/store it in `job.status`: the current `STATUS_QUEUED` value. |
| L747 | Evaluate the right-hand side, then bind/store it in `job.available_at`: the current `now` value. |
| L748 | Evaluate the right-hand side, then bind/store it in `job.stage`: None (no value). |
| L749 | Evaluate the branch condition: evaluate `document is not None and document.deleted_at is None` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L750; otherwise skip this indented block and continue after it. |
| L750 | Evaluate the branch condition: compare whether `_snapshot_get(snapshot, 'expected_size_bytes')` is not the same object as `None`. If truthy, enter L751; otherwise skip this indented block and continue after it. |
| L751 | Evaluate the right-hand side, then bind/store it in `document.file_size`: `int(_snapshot_get(snapshot, 'expected_size_bytes'))` — Convert the input to an integer (using the optional numeric base); inputs include `_snapshot_get(snapshot, 'expected_size_bytes')` — Call [_snapshot_get](#walk--snapshot-get) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L752 | Evaluate the branch condition: compare whether `_snapshot_get(snapshot, 'expected_sha256')` is not the same object as `None`. If truthy, enter L753; otherwise skip this indented block and continue after it. |
| L753 | Evaluate the right-hand side, then bind/store it in `document.content_sha256`: `str(_snapshot_get(snapshot, 'expected_sha256'))` — Convert the input to its string representation; inputs include `_snapshot_get(snapshot, 'expected_sha256')` — Call [_snapshot_get](#walk--snapshot-get) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L754 | `_snapshot_get(snapshot, 'expected_sha256')` — Call [_snapshot_get](#walk--snapshot-get) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L755 | Close the expression/container begun at L753; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L756 | Evaluate the right-hand side, then bind/store it in `document.upload_completed_at`: the current `now` value. |
| L757 | Evaluate the branch condition: compare whether `outcome` equals `'failed'`. If truthy, enter L758; otherwise enter the alternative at L771. |
| L758 | Evaluate the right-hand side, then bind/store it in `job.status`: the current `STATUS_FAILED` value. |
| L759 | Evaluate the right-hand side, then bind/store it in `job.finished_at`: the current `now` value. |
| L760 | Evaluate the right-hand side, then bind/store it in `job.last_error_code`: the current `error_code` value. |
| L761 | Evaluate the right-hand side, then bind/store it in `job.last_error_message`: the current `error_message` value. |
| L762 | `_clear_lease(job)` — Call [_clear_lease](#walk--clear-lease) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L763 | Evaluate the branch condition: evaluate `document is not None and document.deleted_at is None and (document.processing_epoch == job.target_epoch)` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L768; otherwise skip this indented block and continue after it. |
| L764 | Continue the enclosing expression: evaluate `document is not None and document.deleted_at is None and (document.processing_epoch == job.target_epoch)` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. |
| L765 | Continue the enclosing expression: compare whether `document.deleted_at` is the same object as `None`. |
| L766 | Continue the enclosing expression: compare whether `document.processing_epoch` equals `job.target_epoch`. |
| L767 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L768 | Evaluate the right-hand side, then bind/store it in `document.status`: `'Failed'`. |
| L769 | Evaluate the right-hand side, then bind/store it in `document.processing_error`: format a string by inserting `error_code`, `error_message` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L770 | Enter this alternative only when the associated condition was false (or the associated try/loop completed without its exceptional exit). |
| L771 | Raise `ValueError(f'unknown awaiting-upload outcome: {outcome!r}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L772 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L773 | Compute the return value: `True`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `find_expired_leases(session, *, now: datetime, limit: int) -> list[JobContext]`

Selects running jobs with non-null expiry ≤ now, ordered by expiry, bounded/locked using `SKIP LOCKED`; returns copied contexts.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-find-expired-leases"></a>

#### Line-by-line execution

[Current source: lines 776–794](../../../../Backend/app/jobs/queue.py#L776-L794). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `now` | `datetime`; required; keyword-only | Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |
| `limit` | `int`; required; keyword-only | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |

**Declared result:** `list[JobContext]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 776 | def find_expired_leases(session: Session, *, now: datetime, limit: int) -> list[JobContext]:
 777 |     """``running`` jobs whose lease has expired (worker presumably dead)."""
 778 |     rows = session.scalars(
 779 |         select(ProcessingJob)
 780 |         .where(
 781 |             ProcessingJob.status == STATUS_RUNNING,
 782 |             ProcessingJob.lease_expires_at.is_not(None),
 783 |             ProcessingJob.lease_expires_at <= now,
 784 |         )
 785 |         .order_by(ProcessingJob.lease_expires_at)
 786 |         .limit(limit)
 787 |         .with_for_update(skip_locked=True)
 788 |     ).all()
 789 |     contexts = []
 790 |     for row in rows:
 791 |         context = load_job_context(session, row.id)
 792 |         if context is not None:
 793 |             contexts.append(context)
 794 |     return contexts
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L776 | Define `find_expired_leases`; bind its arguments when called. The body executes only when invoked. |
| L777 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L778 | Evaluate the right-hand side, then bind/store it in `rows`: `session.scalars(select(ProcessingJob).where(ProcessingJob.status == STATUS_RUNNING, ProcessingJob.lease_expires_at.is_not(None), ProcessingJob.lease_expires_at <= now).order_by(ProcessingJob.lease_expires_at).limit(limit).with_for_update(skip_locked=True)).all` with the arguments detailed below — Materialize all remaining values in this SQL result; first obtain the receiver: `session.scalars` with the arguments detailed below — Execute the SQL expression and expose first-column values through a ScalarResult. |
| L779 | `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L780 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L781 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.status` equals `STATUS_RUNNING`. |
| L782 | `ProcessingJob.lease_expires_at.is_not(None)` — Build an SQL IS NOT predicate, commonly IS NOT NULL. |
| L783 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.lease_expires_at` is at most `now`. |
| L784 | Close the expression/container begun at L779; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L785 | Set SQL result ordering in the listed priority order; apply this method to the result built by the preceding chain. |
| L786 | Apply a SQL row limit; fetching limit+1 allows continuation detection; apply this method to the result built by the preceding chain. |
| L787 | Request row locks until transaction end; skip_locked=True avoids waiting on rows claimed elsewhere; apply this method to the result built by the preceding chain. |
| L788 | Continue the operation begun at L778: Evaluate the right-hand side, then bind/store it in `rows`: `session.scalars(select(ProcessingJob).where(ProcessingJob.status == STATUS_RUNNING, ProcessingJob.lease_expires_at.is_not(None), ProcessingJob.lease_expires_at <= now).order_by(ProcessingJob.lease_expires_at).limit(limit).with_for_update(skip_locked=True)).all` with the arguments detailed below — Materialize all remaining values in this SQL result; first obtain the receiver: `session.scalars` with the arguments detailed below — Execute the SQL expression and expose first-column values through a ScalarResult. |
| L789 | Evaluate the right-hand side, then bind/store it in `contexts`: build a list containing no items. |
| L790 | Iterate `rows` (the current `rows` value), assigning each item to `row`. Execute the indented body once per item; an empty iterable skips it. |
| L791 | Evaluate the right-hand side, then bind/store it in `context`: `load_job_context(session, row.id)` — Call [load_job_context](#walk-load-job-context) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L792 | Evaluate the branch condition: compare whether `context` is not the same object as `None`. If truthy, enter L793; otherwise skip this indented block and continue after it. |
| L793 | `contexts.append(context)` — Append one object to the mutable list in place. The return value is not assigned here. |
| L794 | Compute the return value: the current `contexts` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `expire_lease(session, *, job_id, now, backoff_base_seconds=5, backoff_cap_seconds=3600) -> str`

Locks/rechecks the job; returns `skipped` if absent, non-running, expiry missing, or renewed beyond `now`. Records `lease_expired`, clears owner/expiry, and either schedules retry-wait with backoff or terminally fails the job and live matching-epoch process document. Flushes and returns the chosen state. Token remains unchanged until the next claim increments it.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-expire-lease"></a>

#### Line-by-line execution

[Current source: lines 797–851](../../../../Backend/app/jobs/queue.py#L797-L851). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `now` | `datetime`; required; keyword-only | Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |
| `backoff_base_seconds` | `int`; default `DEFAULT_BACKOFF_BASE_SECONDS`; keyword-only | Base retry delay, doubled with successive attempts before capping/jitter. |
| `backoff_cap_seconds` | `int`; default `DEFAULT_BACKOFF_CAP_SECONDS`; keyword-only | Maximum retry-delay bound passed to the backoff calculation. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 797 | def expire_lease(
 798 |     session: Session,
 799 |     *,
 800 |     job_id: UUID,
 801 |     now: datetime,
 802 |     backoff_base_seconds: int = DEFAULT_BACKOFF_BASE_SECONDS,
 803 |     backoff_cap_seconds: int = DEFAULT_BACKOFF_CAP_SECONDS,
 804 | ) -> str:
 805 |     """Revoke one expired lease: requeue with backoff or fail.
 806 | 
 807 |     Returns ``"retry_wait"``, ``"failed"``, or ``"skipped"`` (the lease
 808 |     was renewed concurrently -- another worker is alive, leave it).
 809 |     """
 810 |     job = session.scalar(
 811 |         select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()
 812 |     )
 813 |     if (
 814 |         job is None
 815 |         or job.status != STATUS_RUNNING
 816 |         or job.lease_expires_at is None
 817 |         or job.lease_expires_at > now
 818 |     ):
 819 |         return "skipped"
 820 |     job.last_error_code = ERROR_LEASE_EXPIRED
 821 |     job.last_error_message = "worker lease expired without heartbeat"
 822 |     if (job.attempt_count or 0) < (job.max_attempts or 1):
 823 |         job.status = STATUS_RETRY_WAIT
 824 |         job.stage = None
 825 |         job.available_at = now + timedelta(
 826 |             seconds=compute_backoff_seconds(
 827 |                 job.attempt_count or 1,
 828 |                 base_seconds=backoff_base_seconds,
 829 |                 cap_seconds=backoff_cap_seconds,
 830 |                 jitter_seed=str(job.id),
 831 |             )
 832 |         )
 833 |         _clear_lease(job)
 834 |         session.flush()
 835 |         return STATUS_RETRY_WAIT
 836 |     job.status = STATUS_FAILED
 837 |     job.finished_at = now
 838 |     _clear_lease(job)
 839 |     if job.kind == KIND_PROCESS:
 840 |         document = session.get(Document, job.target_document_id)
 841 |         if (
 842 |             document is not None
 843 |             and document.deleted_at is None
 844 |             and document.processing_epoch == job.target_epoch
 845 |         ):
 846 |             document.status = "Failed"
 847 |             document.processing_error = (
 848 |                 f"{ERROR_LEASE_EXPIRED}: worker lease expired without heartbeat"
 849 |             )
 850 |     session.flush()
 851 |     return STATUS_FAILED
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L797 | Define `expire_lease`; bind its arguments when called. The body executes only when invoked. |
| L798 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L799 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L800 | Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. |
| L801 | Declare parameter `now` with annotation `datetime`. Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |
| L802 | Declare parameter `backoff_base_seconds` with annotation `int`. Base retry delay, doubled with successive attempts before capping/jitter. |
| L803 | Declare parameter `backoff_cap_seconds` with annotation `int`. Maximum retry-delay bound passed to the backoff calculation. |
| L804 | Finish/continue the signature; the declared return annotation is `str`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L805 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L807 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L808 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L809 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L810 | Evaluate the right-hand side, then bind/store it in `job`: `session.scalar(select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update())` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()` — Request row locks until transaction end; skip_locked=True avoids waiting on rows claimed elsewhere; first obtain the receiver: `select(ProcessingJob).where(ProcessingJob.id == job_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND. |
| L811 | `select(ProcessingJob).where(ProcessingJob.id == job_id).with_for_update()` — Request row locks until transaction end; skip_locked=True avoids waiting on rows claimed elsewhere; first obtain the receiver: `select(ProcessingJob).where(ProcessingJob.id == job_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L812 | Close the expression/container begun at L810; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L813 | Evaluate the branch condition: evaluate `job is None or job.status != STATUS_RUNNING or job.lease_expires_at is None or (job.lease_expires_at > now)` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L819; otherwise skip this indented block and continue after it. |
| L814 | Continue the enclosing expression: evaluate `job is None or job.status != STATUS_RUNNING or job.lease_expires_at is None or (job.lease_expires_at > now)` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L815 | Continue the enclosing expression: compare whether `job.status` differs from `STATUS_RUNNING`. |
| L816 | Continue the enclosing expression: compare whether `job.lease_expires_at` is the same object as `None`. |
| L817 | Continue the enclosing expression: compare whether `job.lease_expires_at` is greater than `now`. |
| L818 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L819 | Compute the return value: `'skipped'`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L820 | Evaluate the right-hand side, then bind/store it in `job.last_error_code`: the current `ERROR_LEASE_EXPIRED` value. |
| L821 | Evaluate the right-hand side, then bind/store it in `job.last_error_message`: `'worker lease expired without heartbeat'`. |
| L822 | Evaluate the branch condition: compare whether `job.attempt_count or 0` is less than `job.max_attempts or 1`. If truthy, enter L823; otherwise skip this indented block and continue after it. |
| L823 | Evaluate the right-hand side, then bind/store it in `job.status`: the current `STATUS_RETRY_WAIT` value. |
| L824 | Evaluate the right-hand side, then bind/store it in `job.stage`: None (no value). |
| L825 | Evaluate the right-hand side, then bind/store it in `job.available_at`: add/concatenate `now` and `timedelta(seconds=compute_backoff_seconds(job.attempt_count or 1, base_seconds=backoff_base_seconds, cap_seconds=backoff_cap_seconds, jitter_seed=str(job.id)))`, following the parentheses/operator precedence shown in `now + timedelta(seconds=compute_backoff_seconds(job.attempt_count or 1, base_seconds=backoff_base_seconds, cap_seconds=backoff_cap_seconds, jitter_seed=str(job.id)))`. |
| L826 | Supply `seconds` = `compute_backoff_seconds(job.attempt_count or 1, base_seconds=backoff_base_seconds, cap_seconds=backoff_cap_seconds, jitter_seed=str(job.id))`.  Evaluate the value as: `compute_backoff_seconds(job.attempt_count or 1, base_seconds=backoff_base_seconds, cap_seconds=backoff_cap_seconds, jitter_seed=str(job.id))` — Call [compute_backoff_seconds](errors.md#walk-compute-backoff-seconds) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L827 | Continue the enclosing expression: evaluate `job.attempt_count or 1` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L828 | Supply `base_seconds` = `backoff_base_seconds`.  Evaluate the value as: the current `backoff_base_seconds` value. |
| L829 | Supply `cap_seconds` = `backoff_cap_seconds`.  Evaluate the value as: the current `backoff_cap_seconds` value. |
| L830 | Supply `jitter_seed` = `str(job.id)`.  Evaluate the value as: `str(job.id)` — Convert the input to its string representation. |
| L831 | Close the expression/container begun at L826; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L832 | Close the expression/container begun at L825; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L833 | `_clear_lease(job)` — Call [_clear_lease](#walk--clear-lease) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L834 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L835 | Compute the return value: the current `STATUS_RETRY_WAIT` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L836 | Evaluate the right-hand side, then bind/store it in `job.status`: the current `STATUS_FAILED` value. |
| L837 | Evaluate the right-hand side, then bind/store it in `job.finished_at`: the current `now` value. |
| L838 | `_clear_lease(job)` — Call [_clear_lease](#walk--clear-lease) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L839 | Evaluate the branch condition: compare whether `job.kind` equals `KIND_PROCESS`. If truthy, enter L840; otherwise skip this indented block and continue after it. |
| L840 | Evaluate the right-hand side, then bind/store it in `document`: `session.get(Document, job.target_document_id)` — Look up the mapped object by primary key, using the session identity map when possible, otherwise SQL. |
| L841 | Evaluate the branch condition: evaluate `document is not None and document.deleted_at is None and (document.processing_epoch == job.target_epoch)` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L846; otherwise skip this indented block and continue after it. |
| L842 | Continue the enclosing expression: evaluate `document is not None and document.deleted_at is None and (document.processing_epoch == job.target_epoch)` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. |
| L843 | Continue the enclosing expression: compare whether `document.deleted_at` is the same object as `None`. |
| L844 | Continue the enclosing expression: compare whether `document.processing_epoch` equals `job.target_epoch`. |
| L845 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L846 | Evaluate the right-hand side, then bind/store it in `document.status`: `'Failed'`. |
| L847 | Evaluate the right-hand side, then bind/store it in `document.processing_error`: format a string by inserting `ERROR_LEASE_EXPIRED` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L848 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L849 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L850 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L851 | Compute the return value: the current `STATUS_FAILED` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `cancel_jobs_for_deleted_documents(session, *, limit: int, reason="document was deleted") -> int`

Outer-joins target documents and locks bounded oldest queued/running/retry-wait **non-delete** jobs whose document is absent/tombstoned. Increments tokens, cancels/finishes, records reason, clears leases, flushes, and returns count. Awaiting-upload jobs are excluded from this query.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-cancel-jobs-for-deleted-documents"></a>

#### Line-by-line execution

[Current source: lines 854–893](../../../../Backend/app/jobs/queue.py#L854-L893). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `limit` | `int`; required; keyword-only | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |
| `reason` | `str`; default `'document was deleted'`; keyword-only | Human-readable cancellation/decision reason recorded or returned by this operation. |

**Declared result:** `int`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 854 | def cancel_jobs_for_deleted_documents(
 855 |     session: Session, *, limit: int, reason: str = "document was deleted"
 856 | ) -> int:
 857 |     """Cancel nonterminal *processing* jobs whose document is tombstoned/gone.
 858 | 
 859 |     Covers the delete race where A3 tombstoned a document but a process
 860 |     job was queued/retrying/running at the time.  Cancelling bumps the
 861 |     fencing token, so a live holder cannot publish into the deleted
 862 |     scope.
 863 | 
 864 |     ``delete_document`` jobs are deliberately excluded: their whole
 865 |     purpose is to remove the storage object and index versions *after*
 866 |     the row is tombstoned, so treating them as orphans would cancel the
 867 |     only cleanup path and leave the PDF orphaned in storage.
 868 |     """
 869 |     rows = session.scalars(
 870 |         select(ProcessingJob)
 871 |         .outerjoin(Document, Document.id == ProcessingJob.target_document_id)
 872 |         .where(
 873 |             ProcessingJob.kind != KIND_DELETE,
 874 |             ProcessingJob.status.in_(
 875 |                 (STATUS_QUEUED, STATUS_RUNNING, STATUS_RETRY_WAIT)
 876 |             ),
 877 |             (Document.id.is_(None)) | (Document.deleted_at.is_not(None)),
 878 |         )
 879 |         .order_by(ProcessingJob.created_at)
 880 |         .limit(limit)
 881 |         .with_for_update(skip_locked=True, of=ProcessingJob)
 882 |     ).all()
 883 |     count = 0
 884 |     for job in rows:
 885 |         job.lease_token = (job.lease_token or 0) + 1
 886 |         job.status = STATUS_CANCELLED
 887 |         job.finished_at = utcnow()
 888 |         job.last_error_code = CANCELLED_MARKER
 889 |         job.last_error_message = reason
 890 |         _clear_lease(job)
 891 |         count += 1
 892 |     session.flush()
 893 |     return count
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L854 | Define `cancel_jobs_for_deleted_documents`; bind its arguments when called. The body executes only when invoked. |
| L855 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `limit` with annotation `int`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. Declare parameter `reason` with annotation `str`. Human-readable cancellation/decision reason recorded or returned by this operation. |
| L856 | Finish/continue the signature; the declared return annotation is `int`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L857 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L859 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L860 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L861 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L862 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L864 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L865 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L866 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L867 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L868 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L869 | Evaluate the right-hand side, then bind/store it in `rows`: `session.scalars(select(ProcessingJob).outerjoin(Document, Document.id == ProcessingJob.target_document_id).where(ProcessingJob.kind != KIND_DELETE, ProcessingJob.status.in_((STATUS_QUEUED, STATUS_RUNNING, STATUS_RETRY_WAIT)), Document.id.is_(None) \| Document.deleted_at.is_not(None)).order_by(ProcessingJob.created_at).limit(limit).with_for_update(skip_locked=True, of=ProcessingJob)).all` with the arguments detailed below — Materialize all remaining values in this SQL result; first obtain the receiver: `session.scalars` with the arguments detailed below — Execute the SQL expression and expose first-column values through a ScalarResult. |
| L870 | `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L871 | Add a left outer SQL join so unmatched left-side rows can still be selected; apply this method to the result built by the preceding chain. |
| L872 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L873 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.kind` differs from `KIND_DELETE`. |
| L874 | `ProcessingJob.status.in_((STATUS_QUEUED, STATUS_RUNNING, STATUS_RETRY_WAIT))` — Build a SQL membership predicate for the supplied allowed values. |
| L875 | Supply positional argument 1 to `ProcessingJob.status.in_`: build a tuple containing `STATUS_QUEUED`, `STATUS_RUNNING`, `STATUS_RETRY_WAIT`. |
| L876 | Close the expression/container begun at L874; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L877 | Build an SQL IS predicate, commonly IS NULL for a live-row filter. |
| L878 | Close the expression/container begun at L870; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L879 | Set SQL result ordering in the listed priority order; apply this method to the result built by the preceding chain. |
| L880 | Apply a SQL row limit; fetching limit+1 allows continuation detection; apply this method to the result built by the preceding chain. |
| L881 | Request row locks until transaction end; skip_locked=True avoids waiting on rows claimed elsewhere; apply this method to the result built by the preceding chain. |
| L882 | Continue the operation begun at L869: Evaluate the right-hand side, then bind/store it in `rows`: `session.scalars(select(ProcessingJob).outerjoin(Document, Document.id == ProcessingJob.target_document_id).where(ProcessingJob.kind != KIND_DELETE, ProcessingJob.status.in_((STATUS_QUEUED, STATUS_RUNNING, STATUS_RETRY_WAIT)), Document.id.is_(None) \| Document.deleted_at.is_not(None)).order_by(ProcessingJob.created_at).limit(limit).with_for_update(skip_locked=True, of=ProcessingJob)).all` with the arguments detailed below — Materialize all remaining values in this SQL result; first obtain the receiver: `session.scalars` with the arguments detailed below — Execute the SQL expression and expose first-column values through a ScalarResult. |
| L883 | Evaluate the right-hand side, then bind/store it in `count`: `0`. |
| L884 | Iterate `rows` (the current `rows` value), assigning each item to `job`. Execute the indented body once per item; an empty iterable skips it. |
| L885 | Evaluate the right-hand side, then bind/store it in `job.lease_token`: add/concatenate `job.lease_token or 0` and `1`, following the parentheses/operator precedence shown in `(job.lease_token or 0) + 1`. |
| L886 | Evaluate the right-hand side, then bind/store it in `job.status`: the current `STATUS_CANCELLED` value. |
| L887 | Evaluate the right-hand side, then bind/store it in `job.finished_at`: `utcnow()` — Read the current timezone-aware UTC timestamp. |
| L888 | Evaluate the right-hand side, then bind/store it in `job.last_error_code`: the current `CANCELLED_MARKER` value. |
| L889 | Evaluate the right-hand side, then bind/store it in `job.last_error_message`: the current `reason` value. |
| L890 | `_clear_lease(job)` — Call [_clear_lease](#walk--clear-lease) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L891 | Update `count` in place using `1` and the Add operation; the previous target value participates in the calculation. |
| L892 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L893 | Compute the return value: the current `count` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `find_stale_index_versions(session, *, now, grace_seconds, limit) -> list[SweepCandidate]`

Selects bounded process-job rows whose terminal version finished before the grace cutoff or whose superseded-version snapshot key exists and update time is old enough. Collects each selected row's current and superseded versions; skips the document active pointer and any succeeded job's own version; deduplicates by target/version; converts strings to UUIDs and returns candidates. The limit applies to jobs, not resulting version count. Malformed stored version UUIDs propagate errors. No deletion or persisted swept marker occurs; the reconciler rechecks liveness before each provider call.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-find-stale-index-versions"></a>

#### Line-by-line execution

[Current source: lines 896–957](../../../../Backend/app/jobs/queue.py#L896-L957). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `now` | `datetime`; required; keyword-only | Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |
| `grace_seconds` | `int`; required; keyword-only | Minimum age before obsolete index versions are eligible for cleanup. |
| `limit` | `int`; required; keyword-only | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |

**Declared result:** `list[SweepCandidate]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 896 | def find_stale_index_versions(
 897 |     session: Session, *, now: datetime, grace_seconds: int, limit: int
 898 | ) -> list[SweepCandidate]:
 899 |     """Index namespaces eligible for the grace-period sweep.
 900 | 
 901 |     Covers terminal process jobs (their current version, which for
 902 |     failed/cancelled jobs is unpublished, and for succeeded jobs is the
 903 |     active version and therefore excluded) and any job's recorded
 904 |     superseded attempts.  The reconciler re-reads the document's
 905 |     active pointer immediately before deleting (JOB-09), so this list
 906 |     is only a candidate set, never a deletion order.
 907 |     """
 908 |     cutoff = now - timedelta(seconds=grace_seconds)
 909 |     rows = session.scalars(
 910 |         select(ProcessingJob)
 911 |         .where(
 912 |             ProcessingJob.kind == KIND_PROCESS,
 913 |             (
 914 |                 (
 915 |                     ProcessingJob.status.in_(TERMINAL_STATUSES)
 916 |                     & ProcessingJob.index_version.is_not(None)
 917 |                     & ProcessingJob.finished_at.is_not(None)
 918 |                     & (ProcessingJob.finished_at <= cutoff)
 919 |                 )
 920 |                 | (
 921 |                     ProcessingJob.resource_snapshot.op("?")("superseded_index_versions")
 922 |                     & (ProcessingJob.updated_at <= cutoff)
 923 |                 )
 924 |             ),
 925 |         )
 926 |         .order_by(ProcessingJob.updated_at)
 927 |         .limit(limit)
 928 |     ).all()
 929 |     candidates: list[SweepCandidate] = []
 930 |     seen: set[tuple[UUID, str]] = set()
 931 |     for job in rows:
 932 |         document = session.get(Document, job.target_document_id)
 933 |         active = document.active_index_version if document else None
 934 |         versions: list[str] = []
 935 |         if job.index_version is not None:
 936 |             versions.append(str(job.index_version))
 937 |         superseded = (job.resource_snapshot or {}).get("superseded_index_versions") or []
 938 |         versions.extend(str(v) for v in superseded)
 939 |         for version in versions:
 940 |             if active is not None and version == str(active):
 941 |                 continue  # never sweep the active pointer (JOB-11)
 942 |             if job.status == STATUS_SUCCEEDED and version == str(job.index_version):
 943 |                 continue  # succeeded job's version is the active one
 944 |             key = (job.target_document_id, version)
 945 |             if key in seen:
 946 |                 continue
 947 |             seen.add(key)
 948 |             candidates.append(
 949 |                 SweepCandidate(
 950 |                     target_document_id=job.target_document_id,
 951 |                     project_id=job.project_id,
 952 |                     owner_user_id=job.owner_user_id,
 953 |                     index_version=UUID(version),
 954 |                     job_id=job.id,
 955 |                 )
 956 |             )
 957 |     return candidates
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L896 | Define `find_stale_index_versions`; bind its arguments when called. The body executes only when invoked. |
| L897 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `now` with annotation `datetime`. Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. Declare parameter `grace_seconds` with annotation `int`. Minimum age before obsolete index versions are eligible for cleanup. Declare parameter `limit` with annotation `int`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. |
| L898 | Finish/continue the signature; the declared return annotation is `list[SweepCandidate]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L899 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L901 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L902 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L903 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L904 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L905 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L906 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L907 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L908 | Evaluate the right-hand side, then bind/store it in `cutoff`: subtract `now` and `timedelta(seconds=grace_seconds)`, following the parentheses/operator precedence shown in `now - timedelta(seconds=grace_seconds)`. |
| L909 | Evaluate the right-hand side, then bind/store it in `rows`: `session.scalars(select(ProcessingJob).where(ProcessingJob.kind == KIND_PROCESS, ProcessingJob.status.in_(TERMINAL_STATUSES) & ProcessingJob.index_version.is_not(None) & ProcessingJob.finished_at.is_not(None) & (ProcessingJob.finished_at <= cutoff) \| ProcessingJob.resource_snapshot.op('?')('superseded_index_versions') & (ProcessingJob.updated_at <= cutoff)).order_by(ProcessingJob.updated_at).limit(limit)).all` with the arguments detailed below — Materialize all remaining values in this SQL result; first obtain the receiver: `session.scalars` with the arguments detailed below — Execute the SQL expression and expose first-column values through a ScalarResult. |
| L910 | `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L911 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L912 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.kind` equals `KIND_PROCESS`. |
| L913 | Supply positional argument 1 to `session.scalars`: `select(ProcessingJob).where(ProcessingJob.kind == KIND_PROCESS, ProcessingJob.status.in_(TERMINAL_STATUSES) & ProcessingJob.index_version.is_not(None) & ProcessingJob.finished_at.is_not(None) & (ProcessingJob.finished_at <= cutoff) \| ProcessingJob.resource_snapshot.op('?')('superseded_index_versions') & (ProcessingJob.updated_at <= cutoff)).order_by(ProcessingJob.updated_at).limit` with the arguments detailed below — Apply a SQL row limit; fetching limit+1 allows continuation detection; first obtain the receiver: `select(ProcessingJob).where(ProcessingJob.kind == KIND_PROCESS, ProcessingJob.status.in_(TERMINAL_STATUSES) & ProcessingJob.index_version.is_not(None) & ProcessingJob.finished_at.is_not(None) & (ProcessingJob.finished_at <= cutoff) \| ProcessingJob.resource_snapshot.op('?')('superseded_index_versions') & (ProcessingJob.updated_at <= cutoff)).order_by` with the arguments detailed below — Set SQL result ordering in the listed priority order; first obtain the receiver: `select(ProcessingJob).where` with the arguments detailed below — Add SQL filtering predicates; multiple supplied predicates are combined with AND. |
| L914 | Continue the enclosing expression: combine with \| `ProcessingJob.status.in_(TERMINAL_STATUSES) & ProcessingJob.index_version.is_not(None) & ProcessingJob.finished_at.is_not(None) & (ProcessingJob.finished_at <= cutoff)` and `ProcessingJob.resource_snapshot.op('?')('superseded_index_versions') & (ProcessingJob.updated_at <= cutoff)`, following the parentheses/operator precedence shown in `ProcessingJob.status.in_(TERMINAL_STATUSES) & ProcessingJob.index_version.is_not(None) & ProcessingJob.finished_at.is_not(None) & (ProcessingJob.finished_at <= cutoff) \| ProcessingJob.resource_snapshot.op('?')('superseded_index_versions') & (ProcessingJob.updated_at <= cutoff)`. |
| L915 | `ProcessingJob.status.in_(TERMINAL_STATUSES)` — Build a SQL membership predicate for the supplied allowed values. |
| L916 | Build an SQL IS NOT predicate, commonly IS NOT NULL. |
| L917 | Build an SQL IS NOT predicate, commonly IS NOT NULL. |
| L918 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.finished_at` is at most `cutoff`. |
| L919 | Close the expression/container begun at L910; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L920 | Supply positional argument 2 to `select(ProcessingJob).where`: combine with \| `ProcessingJob.status.in_(TERMINAL_STATUSES) & ProcessingJob.index_version.is_not(None) & ProcessingJob.finished_at.is_not(None) & (ProcessingJob.finished_at <= cutoff)` and `ProcessingJob.resource_snapshot.op('?')('superseded_index_versions') & (ProcessingJob.updated_at <= cutoff)`, following the parentheses/operator precedence shown in `ProcessingJob.status.in_(TERMINAL_STATUSES) & ProcessingJob.index_version.is_not(None) & ProcessingJob.finished_at.is_not(None) & (ProcessingJob.finished_at <= cutoff) \| ProcessingJob.resource_snapshot.op('?')('superseded_index_versions') & (ProcessingJob.updated_at <= cutoff)`. |
| L921 | `ProcessingJob.resource_snapshot.op('?')('superseded_index_versions')` — Invoke `ProcessingJob.resource_snapshot.op('?')` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L922 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.updated_at` is at most `cutoff`. |
| L923 | Close the expression/container begun at L910; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L924 | Close the expression/container begun at L910; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L925 | Close the expression/container begun at L910; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L926 | Set SQL result ordering in the listed priority order; apply this method to the result built by the preceding chain. |
| L927 | Apply a SQL row limit; fetching limit+1 allows continuation detection; apply this method to the result built by the preceding chain. |
| L928 | Continue the operation begun at L909: Evaluate the right-hand side, then bind/store it in `rows`: `session.scalars(select(ProcessingJob).where(ProcessingJob.kind == KIND_PROCESS, ProcessingJob.status.in_(TERMINAL_STATUSES) & ProcessingJob.index_version.is_not(None) & ProcessingJob.finished_at.is_not(None) & (ProcessingJob.finished_at <= cutoff) \| ProcessingJob.resource_snapshot.op('?')('superseded_index_versions') & (ProcessingJob.updated_at <= cutoff)).order_by(ProcessingJob.updated_at).limit(limit)).all` with the arguments detailed below — Materialize all remaining values in this SQL result; first obtain the receiver: `session.scalars` with the arguments detailed below — Execute the SQL expression and expose first-column values through a ScalarResult. |
| L929 | Evaluate the right-hand side, then bind/store it in `candidates`: build a list containing no items. |
| L930 | Evaluate the right-hand side, then bind/store it in `seen`: `set()` — Collect unique hashable items into a set. |
| L931 | Iterate `rows` (the current `rows` value), assigning each item to `job`. Execute the indented body once per item; an empty iterable skips it. |
| L932 | Evaluate the right-hand side, then bind/store it in `document`: `session.get(Document, job.target_document_id)` — Look up the mapped object by primary key, using the session identity map when possible, otherwise SQL. |
| L933 | Evaluate the right-hand side, then bind/store it in `active`: check `document`; when true use the `active_index_version` attribute of `document`, otherwise None (no value) (only the selected branch is evaluated). |
| L934 | Evaluate the right-hand side, then bind/store it in `versions`: build a list containing no items. |
| L935 | Evaluate the branch condition: compare whether `job.index_version` is not the same object as `None`. If truthy, enter L936; otherwise skip this indented block and continue after it. |
| L936 | `versions.append(str(job.index_version))` — Append one object to the mutable list in place; inputs include `str(job.index_version)` — Convert the input to its string representation. The return value is not assigned here. |
| L937 | Evaluate the right-hand side, then bind/store it in `superseded`: evaluate `(job.resource_snapshot or {}).get('superseded_index_versions') or []` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L938 | `versions.extend((str(v) for v in superseded))` — Append every item from the supplied iterable to the list in order; inputs include iterate `superseded`, binding each item to `v`; produce `str(v)` into a lazy generator (items computed when consumed). The return value is not assigned here. |
| L939 | Iterate `versions` (the current `versions` value), assigning each item to `version`. Execute the indented body once per item; an empty iterable skips it. |
| L940 | Evaluate the branch condition: evaluate `active is not None and version == str(active)` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L941; otherwise skip this indented block and continue after it. |
| L941 | Skip the rest of this iteration and advance the innermost loop to its next item; active finally/context exits still apply. |
| L942 | Evaluate the branch condition: evaluate `job.status == STATUS_SUCCEEDED and version == str(job.index_version)` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L943; otherwise skip this indented block and continue after it. |
| L943 | Skip the rest of this iteration and advance the innermost loop to its next item; active finally/context exits still apply. |
| L944 | Evaluate the right-hand side, then bind/store it in `key`: build a tuple containing `job.target_document_id`, `version`. |
| L945 | Evaluate the branch condition: compare whether `key` is contained in `seen`. If truthy, enter L946; otherwise skip this indented block and continue after it. |
| L946 | Skip the rest of this iteration and advance the innermost loop to its next item; active finally/context exits still apply. |
| L947 | `seen.add(key)` — Add this identity to the deduplication set; repeated insertion has no further effect. The return value is not assigned here. |
| L948 | `candidates.append` with the arguments detailed below — Append one object to the mutable list in place; inputs include `SweepCandidate` with the arguments detailed below — Construct `SweepCandidate` with the shown fields; its class/model initialization rules apply. The return value is not assigned here. |
| L949 | `SweepCandidate` with the arguments detailed below — Construct `SweepCandidate` with the shown fields; its class/model initialization rules apply. |
| L950 | Supply `target_document_id` = `job.target_document_id`. Immutable target UUID retained even when the live document relationship disappears. Evaluate the value as: the `target_document_id` attribute of `job`. |
| L951 | Supply `project_id` = `job.project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the `project_id` attribute of `job`. |
| L952 | Supply `owner_user_id` = `job.owner_user_id`. Internal owner UUID copied into the job's durable ownership snapshot. Evaluate the value as: the `owner_user_id` attribute of `job`. |
| L953 | Supply `index_version` = `UUID(version)`. UUID of one document's vector-index namespace, separate from its active publication pointer. Evaluate the value as: `UUID(version)` — Parse or construct a UUID; invalid text raises a conversion error. |
| L954 | Supply `job_id` = `job.id`. Durable processing-job UUID. Evaluate the value as: the `id` attribute of `job`. |
| L955 | Close the expression/container begun at L949; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L956 | Close the expression/container begun at L948; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L957 | Compute the return value: the current `candidates` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `get_active_version(session, target_document_id: UUID) -> tuple[bool, UUID | None]`

Returns `(False, None)` for missing/tombstoned document, otherwise `(True, active_index_version)`. Does not check parent project state.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-active-version"></a>

#### Line-by-line execution

[Current source: lines 960–967](../../../../Backend/app/jobs/queue.py#L960-L967). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `target_document_id` | `UUID`; required; positional or keyword | Immutable target UUID retained even when the live document relationship disappears. |

**Declared result:** `tuple[bool, UUID | None]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 960 | def get_active_version(
 961 |     session: Session, target_document_id: UUID
 962 | ) -> tuple[bool, UUID | None]:
 963 |     """Return ``(document_exists_live, active_index_version)``."""
 964 |     document = session.get(Document, target_document_id)
 965 |     if document is None or document.deleted_at is not None:
 966 |         return False, None
 967 |     return True, document.active_index_version
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L960 | Define `get_active_version`; bind its arguments when called. The body executes only when invoked. |
| L961 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `target_document_id` with annotation `UUID`. Immutable target UUID retained even when the live document relationship disappears. |
| L962 | Finish/continue the signature; the declared return annotation is `tuple[bool, UUID \| None]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L963 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L964 | Evaluate the right-hand side, then bind/store it in `document`: `session.get(Document, target_document_id)` — Look up the mapped object by primary key, using the session identity map when possible, otherwise SQL. |
| L965 | Evaluate the branch condition: evaluate `document is None or document.deleted_at is not None` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L966; otherwise skip this indented block and continue after it. |
| L966 | Compute the return value: build a tuple containing `False`, `None`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L967 | Compute the return value: build a tuple containing `True`, `document.active_index_version`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

## Worker transaction facade

### `JobQueueStore.__init__(self, session_factory) -> None`

Stores the supplied session factory; no SQL/provider work.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueuestore---init--"></a>

#### Line-by-line execution

[Current source: lines 985–986](../../../../Backend/app/jobs/queue.py#L985-L986). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `session_factory` | `Any`; required; positional or keyword | Callable that creates database sessions; a null value selects the function's configured default. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 985 |     def __init__(self, session_factory: Any) -> None:
 986 |         self._factory = session_factory
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L985 | Define `JobQueueStore.__init__`; bind its arguments when called. The body executes only when invoked. |
| L986 | Evaluate the right-hand side, then bind/store it in `self._factory`: the current `session_factory` value. |

<!-- END LINE WALKTHROUGH -->

### `JobQueueStore._tx(self, fn) -> Any`

Creates/closes a session, enters `session.begin()`, calls `fn(session)`, and returns its result after successful context exit commits. Exceptions roll back and propagate. All lambda wrappers below pass the newly opened session to their same-name module function.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueuestore--tx"></a>

#### Line-by-line execution

[Current source: lines 989–992](../../../../Backend/app/jobs/queue.py#L989-L992). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `fn` | `Any`; required; positional or keyword | Callback invoked inside a newly opened short transaction. |

**Declared result:** `Any`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 989 |     def _tx(self, fn: Any) -> Any:
 990 |         with self._factory() as session:
 991 |             with session.begin():
 992 |                 return fn(session)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L989 | Define `JobQueueStore._tx`; bind its arguments when called. The body executes only when invoked. |
| L990 | Enter `self._factory()` — Create a new SQLAlchemy session from the stored factory and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L991 | Enter `session.begin()` — Create a transaction context: successful exit commits, exceptional exit rolls back. Context exits run in reverse order, including on return/exception. |
| L992 | Compute the return value: `fn(session)` — Invoke `fn` with the shown inputs and use its result; see the function overview for its role in this flow. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `JobQueueStore.enqueue_job(self, **kwargs) -> ProcessingJob`

Accepts module enqueue keyword arguments excluding `session`; returns its new/existing ORM row after `_tx` commits. Worker factories normally disable expiration on commit so detached scalar attributes remain usable.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueuestore-enqueue-job"></a>

#### Line-by-line execution

[Current source: lines 995–996](../../../../Backend/app/jobs/queue.py#L995-L996). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `kwargs` | `Any`; implicitly supplied/collected; ** keyword extras | Caller-supplied kwargs; each read, transformation, and validation is traced below. |

**Declared result:** `ProcessingJob`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 995 |     def enqueue_job(self, **kwargs: Any) -> ProcessingJob:
 996 |         return self._tx(lambda s: enqueue_job(s, **kwargs))
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L995 | Define `JobQueueStore.enqueue_job`; bind its arguments when called. The body executes only when invoked. |
| L996 | Compute the return value: `self._tx(lambda s: enqueue_job(s, **kwargs))` — Call [JobQueueStore._tx](#walk-jobqueuestore--tx) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `JobQueueStore.find_nonterminal_job(self, **kwargs) -> ProcessingJob | None`

Accepts target/kind keywords, forwards through `_tx`, returns the found row or null after the short transaction.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueuestore-find-nonterminal-job"></a>

#### Line-by-line execution

[Current source: lines 998–999](../../../../Backend/app/jobs/queue.py#L998-L999). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `kwargs` | `Any`; implicitly supplied/collected; ** keyword extras | Caller-supplied kwargs; each read, transformation, and validation is traced below. |

**Declared result:** `ProcessingJob | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 998 |     def find_nonterminal_job(self, **kwargs: Any) -> ProcessingJob | None:
 999 |         return self._tx(lambda s: find_nonterminal_job(s, **kwargs))
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L998 | Define `JobQueueStore.find_nonterminal_job`; bind its arguments when called. The body executes only when invoked. |
| L999 | Compute the return value: `self._tx(lambda s: find_nonterminal_job(s, **kwargs))` — Call [JobQueueStore._tx](#walk-jobqueuestore--tx) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `JobQueueStore.claim_next_jobs(self, *, worker_id, limit, lease_seconds) -> list[JobClaim]`

Forwards worker identity, batch limit, and lease duration through `_tx`; returns claims only after commit, before provider processing.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueuestore-claim-next-jobs"></a>

#### Line-by-line execution

[Current source: lines 1001–1004](../../../../Backend/app/jobs/queue.py#L1001-L1004). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `limit` | `int`; required; keyword-only | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |
| `lease_seconds` | `int`; required; keyword-only | Lease duration in seconds; positive-duration validation is not implicit in this parameter. |

**Declared result:** `list[JobClaim]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
1001 |     def claim_next_jobs(self, *, worker_id: str, limit: int, lease_seconds: int) -> list[JobClaim]:
1002 |         return self._tx(
1003 |             lambda s: claim_next_jobs(s, worker_id=worker_id, limit=limit, lease_seconds=lease_seconds)
1004 |         )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L1001 | Define `JobQueueStore.claim_next_jobs`; bind its arguments when called. The body executes only when invoked. |
| L1002 | Compute the return value: `self._tx(lambda s: claim_next_jobs(s, worker_id=worker_id, limit=limit, lease_seconds=lease_seconds))` — Call [JobQueueStore._tx](#walk-jobqueuestore--tx) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L1003 | Supply `worker_id` = `worker_id`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: the current `worker_id` value. Supply `limit` = `limit`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. Evaluate the value as: the current `limit` value. Supply `lease_seconds` = `lease_seconds`. Lease duration in seconds; positive-duration validation is not implicit in this parameter. Evaluate the value as: the current `lease_seconds` value. |
| L1004 | Close the expression/container begun at L1002; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `JobQueueStore.renew_job_lease(self, *, job_id, lease_token, worker_id, lease_seconds) -> bool`

Forwards exact claim and duration through `_tx`; returns the committed renewal flag.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueuestore-renew-job-lease"></a>

#### Line-by-line execution

[Current source: lines 1006–1013](../../../../Backend/app/jobs/queue.py#L1006-L1013). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `lease_token` | `int`; required; keyword-only | Monotonic claim token used to reject stale worker writes. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `lease_seconds` | `int`; required; keyword-only | Lease duration in seconds; positive-duration validation is not implicit in this parameter. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
1006 |     def renew_job_lease(
1007 |         self, *, job_id: UUID, lease_token: int, worker_id: str, lease_seconds: int
1008 |     ) -> bool:
1009 |         return self._tx(
1010 |             lambda s: renew_job_lease(
1011 |                 s, job_id=job_id, lease_token=lease_token, worker_id=worker_id, lease_seconds=lease_seconds
1012 |             )
1013 |         )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L1006 | Define `JobQueueStore.renew_job_lease`; bind its arguments when called. The body executes only when invoked. |
| L1007 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. Declare parameter `lease_token` with annotation `int`. Monotonic claim token used to reject stale worker writes. Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. Declare parameter `lease_seconds` with annotation `int`. Lease duration in seconds; positive-duration validation is not implicit in this parameter. |
| L1008 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L1009 | Compute the return value: `self._tx(lambda s: renew_job_lease(s, job_id=job_id, lease_token=lease_token, worker_id=worker_id, lease_seconds=lease_seconds))` — Call [JobQueueStore._tx](#walk-jobqueuestore--tx) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L1010 | Call [renew_job_lease](#walk-renew-job-lease) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L1011 | Supply `job_id` = `job_id`. Durable processing-job UUID. Evaluate the value as: the current `job_id` value. Supply `lease_token` = `lease_token`. Monotonic claim token used to reject stale worker writes. Evaluate the value as: the current `lease_token` value. Supply `worker_id` = `worker_id`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: the current `worker_id` value. Supply `lease_seconds` = `lease_seconds`. Lease duration in seconds; positive-duration validation is not implicit in this parameter. Evaluate the value as: the current `lease_seconds` value. |
| L1012 | Close the expression/container begun at L1010; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L1013 | Close the expression/container begun at L1009; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `JobQueueStore.update_progress(self, *, job_id, lease_token, worker_id, stage=None, progress_current=None, progress_total=None) -> bool`

Forwards claim and optional progress values through `_tx`; returns the update guard's boolean.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueuestore-update-progress"></a>

#### Line-by-line execution

[Current source: lines 1015–1035](../../../../Backend/app/jobs/queue.py#L1015-L1035). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `lease_token` | `int`; required; keyword-only | Monotonic claim token used to reject stale worker writes. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `stage` | `str \| None`; default `None`; keyword-only | Public job stage to record, such as extracting, embedding, indexing, or publishing. |
| `progress_current` | `int \| None`; default `None`; keyword-only | Current completed-work counter; null means do not update it. |
| `progress_total` | `int \| None`; default `None`; keyword-only | Total-work counter; null means do not update it. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
1015 |     def update_progress(
1016 |         self,
1017 |         *,
1018 |         job_id: UUID,
1019 |         lease_token: int,
1020 |         worker_id: str,
1021 |         stage: str | None = None,
1022 |         progress_current: int | None = None,
1023 |         progress_total: int | None = None,
1024 |     ) -> bool:
1025 |         return self._tx(
1026 |             lambda s: update_progress(
1027 |                 s,
1028 |                 job_id=job_id,
1029 |                 lease_token=lease_token,
1030 |                 worker_id=worker_id,
1031 |                 stage=stage,
1032 |                 progress_current=progress_current,
1033 |                 progress_total=progress_total,
1034 |             )
1035 |         )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L1015 | Define `JobQueueStore.update_progress`; bind its arguments when called. The body executes only when invoked. |
| L1016 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L1017 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L1018 | Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. |
| L1019 | Declare parameter `lease_token` with annotation `int`. Monotonic claim token used to reject stale worker writes. |
| L1020 | Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. |
| L1021 | Declare parameter `stage` with annotation `str \| None`. Public job stage to record, such as extracting, embedding, indexing, or publishing. |
| L1022 | Declare parameter `progress_current` with annotation `int \| None`. Current completed-work counter; null means do not update it. |
| L1023 | Declare parameter `progress_total` with annotation `int \| None`. Total-work counter; null means do not update it. |
| L1024 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L1025 | Compute the return value: `self._tx` with the arguments detailed below — Call [JobQueueStore._tx](#walk-jobqueuestore--tx) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L1026 | Call [update_progress](#walk-update-progress) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L1027 | Supply positional argument 1 to `update_progress`: the current `s` value. |
| L1028 | Supply `job_id` = `job_id`. Durable processing-job UUID. Evaluate the value as: the current `job_id` value. |
| L1029 | Supply `lease_token` = `lease_token`. Monotonic claim token used to reject stale worker writes. Evaluate the value as: the current `lease_token` value. |
| L1030 | Supply `worker_id` = `worker_id`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: the current `worker_id` value. |
| L1031 | Supply `stage` = `stage`. Public job stage to record, such as extracting, embedding, indexing, or publishing. Evaluate the value as: the current `stage` value. |
| L1032 | Supply `progress_current` = `progress_current`. Current completed-work counter; null means do not update it. Evaluate the value as: the current `progress_current` value. |
| L1033 | Supply `progress_total` = `progress_total`. Total-work counter; null means do not update it. Evaluate the value as: the current `progress_total` value. |
| L1034 | Close the expression/container begun at L1026; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L1035 | Close the expression/container begun at L1025; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `JobQueueStore.complete_job(self, *, job_id, lease_token, worker_id, chunk_count=None) -> bool`

Forwards claim/count through `_tx`; returns completion/idempotency result after the publication transaction commits.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueuestore-complete-job"></a>

#### Line-by-line execution

[Current source: lines 1037–1044](../../../../Backend/app/jobs/queue.py#L1037-L1044). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `lease_token` | `int`; required; keyword-only | Monotonic claim token used to reject stale worker writes. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `chunk_count` | `int \| None`; default `None`; keyword-only | Number of chunks to record when publishing a processed document. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
1037 |     def complete_job(
1038 |         self, *, job_id: UUID, lease_token: int, worker_id: str, chunk_count: int | None = None
1039 |     ) -> bool:
1040 |         return self._tx(
1041 |             lambda s: complete_job(
1042 |                 s, job_id=job_id, lease_token=lease_token, worker_id=worker_id, chunk_count=chunk_count
1043 |             )
1044 |         )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L1037 | Define `JobQueueStore.complete_job`; bind its arguments when called. The body executes only when invoked. |
| L1038 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. Declare parameter `lease_token` with annotation `int`. Monotonic claim token used to reject stale worker writes. Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. Declare parameter `chunk_count` with annotation `int \| None`. Number of chunks to record when publishing a processed document. |
| L1039 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L1040 | Compute the return value: `self._tx(lambda s: complete_job(s, job_id=job_id, lease_token=lease_token, worker_id=worker_id, chunk_count=chunk_count))` — Call [JobQueueStore._tx](#walk-jobqueuestore--tx) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L1041 | Call [complete_job](#walk-complete-job) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L1042 | Supply `job_id` = `job_id`. Durable processing-job UUID. Evaluate the value as: the current `job_id` value. Supply `lease_token` = `lease_token`. Monotonic claim token used to reject stale worker writes. Evaluate the value as: the current `lease_token` value. Supply `worker_id` = `worker_id`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: the current `worker_id` value. Supply `chunk_count` = `chunk_count`. Number of chunks to record when publishing a processed document. Evaluate the value as: the current `chunk_count` value. |
| L1043 | Close the expression/container begun at L1041; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L1044 | Close the expression/container begun at L1040; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `JobQueueStore.fail_job(self, *, job_id, lease_token, worker_id, error_code, error_message, retryable, backoff_base_seconds=5, backoff_cap_seconds=3600) -> bool`

Forwards claim, diagnostics, retry policy, and delay configuration through `_tx`; returns whether failure was persisted.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueuestore-fail-job"></a>

#### Line-by-line execution

[Current source: lines 1046–1070](../../../../Backend/app/jobs/queue.py#L1046-L1070). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `lease_token` | `int`; required; keyword-only | Monotonic claim token used to reject stale worker writes. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `error_code` | `str`; required; keyword-only | Machine-readable failure category stored or exposed by the operation. |
| `error_message` | `str`; required; keyword-only | Human-readable failure detail; truncation alone does not redact sensitive content. |
| `retryable` | `bool`; required; keyword-only | Whether the failure may be retried while the attempt budget remains. |
| `backoff_base_seconds` | `int`; default `DEFAULT_BACKOFF_BASE_SECONDS`; keyword-only | Base retry delay, doubled with successive attempts before capping/jitter. |
| `backoff_cap_seconds` | `int`; default `DEFAULT_BACKOFF_CAP_SECONDS`; keyword-only | Maximum retry-delay bound passed to the backoff calculation. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
1046 |     def fail_job(
1047 |         self,
1048 |         *,
1049 |         job_id: UUID,
1050 |         lease_token: int,
1051 |         worker_id: str,
1052 |         error_code: str,
1053 |         error_message: str,
1054 |         retryable: bool,
1055 |         backoff_base_seconds: int = DEFAULT_BACKOFF_BASE_SECONDS,
1056 |         backoff_cap_seconds: int = DEFAULT_BACKOFF_CAP_SECONDS,
1057 |     ) -> bool:
1058 |         return self._tx(
1059 |             lambda s: fail_job(
1060 |                 s,
1061 |                 job_id=job_id,
1062 |                 lease_token=lease_token,
1063 |                 worker_id=worker_id,
1064 |                 error_code=error_code,
1065 |                 error_message=error_message,
1066 |                 retryable=retryable,
1067 |                 backoff_base_seconds=backoff_base_seconds,
1068 |                 backoff_cap_seconds=backoff_cap_seconds,
1069 |             )
1070 |         )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L1046 | Define `JobQueueStore.fail_job`; bind its arguments when called. The body executes only when invoked. |
| L1047 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L1048 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L1049 | Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. |
| L1050 | Declare parameter `lease_token` with annotation `int`. Monotonic claim token used to reject stale worker writes. |
| L1051 | Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. |
| L1052 | Declare parameter `error_code` with annotation `str`. Machine-readable failure category stored or exposed by the operation. |
| L1053 | Declare parameter `error_message` with annotation `str`. Human-readable failure detail; truncation alone does not redact sensitive content. |
| L1054 | Declare parameter `retryable` with annotation `bool`. Whether the failure may be retried while the attempt budget remains. |
| L1055 | Declare parameter `backoff_base_seconds` with annotation `int`. Base retry delay, doubled with successive attempts before capping/jitter. |
| L1056 | Declare parameter `backoff_cap_seconds` with annotation `int`. Maximum retry-delay bound passed to the backoff calculation. |
| L1057 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L1058 | Compute the return value: `self._tx` with the arguments detailed below — Call [JobQueueStore._tx](#walk-jobqueuestore--tx) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L1059 | Call [fail_job](#walk-fail-job) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L1060 | Supply positional argument 1 to `fail_job`: the current `s` value. |
| L1061 | Supply `job_id` = `job_id`. Durable processing-job UUID. Evaluate the value as: the current `job_id` value. |
| L1062 | Supply `lease_token` = `lease_token`. Monotonic claim token used to reject stale worker writes. Evaluate the value as: the current `lease_token` value. |
| L1063 | Supply `worker_id` = `worker_id`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: the current `worker_id` value. |
| L1064 | Supply `error_code` = `error_code`. Machine-readable failure category stored or exposed by the operation. Evaluate the value as: the current `error_code` value. |
| L1065 | Supply `error_message` = `error_message`. Human-readable failure detail; truncation alone does not redact sensitive content. Evaluate the value as: the current `error_message` value. |
| L1066 | Supply `retryable` = `retryable`. Whether the failure may be retried while the attempt budget remains. Evaluate the value as: the current `retryable` value. |
| L1067 | Supply `backoff_base_seconds` = `backoff_base_seconds`. Base retry delay, doubled with successive attempts before capping/jitter. Evaluate the value as: the current `backoff_base_seconds` value. |
| L1068 | Supply `backoff_cap_seconds` = `backoff_cap_seconds`. Maximum retry-delay bound passed to the backoff calculation. Evaluate the value as: the current `backoff_cap_seconds` value. |
| L1069 | Close the expression/container begun at L1059; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L1070 | Close the expression/container begun at L1058; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `JobQueueStore.cancel_job(self, *, job_id, reason) -> bool`

Forwards job/reason through `_tx`; commits cancellation and returns whether a nonterminal row changed.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueuestore-cancel-job"></a>

#### Line-by-line execution

[Current source: lines 1072–1073](../../../../Backend/app/jobs/queue.py#L1072-L1073). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `reason` | `str`; required; keyword-only | Human-readable cancellation/decision reason recorded or returned by this operation. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
1072 |     def cancel_job(self, *, job_id: UUID, reason: str) -> bool:
1073 |         return self._tx(lambda s: cancel_job(s, job_id=job_id, reason=reason))
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L1072 | Define `JobQueueStore.cancel_job`; bind its arguments when called. The body executes only when invoked. |
| L1073 | Compute the return value: `self._tx(lambda s: cancel_job(s, job_id=job_id, reason=reason))` — Call [JobQueueStore._tx](#walk-jobqueuestore--tx) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `JobQueueStore.load_job_context(self, job_id: UUID) -> JobContext | None`

Opens a read session, calls the module loader, closes the session, and returns copied facts. Unlike `_tx`, it has no explicit begin/commit; closing ends the implicit read transaction.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueuestore-load-job-context"></a>

#### Line-by-line execution

[Current source: lines 1076–1078](../../../../Backend/app/jobs/queue.py#L1076-L1078). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `job_id` | `UUID`; required; positional or keyword | Durable processing-job UUID. |

**Declared result:** `JobContext | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
1076 |     def load_job_context(self, job_id: UUID) -> JobContext | None:
1077 |         with self._factory() as session:
1078 |             return load_job_context(session, job_id)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L1076 | Define `JobQueueStore.load_job_context`; bind its arguments when called. The body executes only when invoked. |
| L1077 | Enter `self._factory()` — Create a new SQLAlchemy session from the stored factory and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L1078 | Compute the return value: `load_job_context(session, job_id)` — Call [load_job_context](#walk-load-job-context) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `JobQueueStore.find_expired_awaiting_upload(self, *, cutoff, limit) -> list[JobContext]`

Forwards cutoff/limit through `_tx`; returns candidates after releasing locks for outside-transaction inspection.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueuestore-find-expired-awaiting-upload"></a>

#### Line-by-line execution

[Current source: lines 1080–1081](../../../../Backend/app/jobs/queue.py#L1080-L1081). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `cutoff` | `datetime`; required; keyword-only | Inclusive age cutoff used to select old work. |
| `limit` | `int`; required; keyword-only | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |

**Declared result:** `list[JobContext]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
1080 |     def find_expired_awaiting_upload(self, *, cutoff: datetime, limit: int) -> list[JobContext]:
1081 |         return self._tx(lambda s: find_expired_awaiting_upload(s, cutoff=cutoff, limit=limit))
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L1080 | Define `JobQueueStore.find_expired_awaiting_upload`; bind its arguments when called. The body executes only when invoked. |
| L1081 | Compute the return value: `self._tx(lambda s: find_expired_awaiting_upload(s, cutoff=cutoff, limit=limit))` — Call [JobQueueStore._tx](#walk-jobqueuestore--tx) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `JobQueueStore.apply_awaiting_upload_outcome(self, *, job_id, outcome, error_code=None, error_message=None) -> bool`

Forwards inspection decision/diagnostics through `_tx`; commits only the still-awaiting row's transition and returns its applied flag.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueuestore-apply-awaiting-upload-outcome"></a>

#### Line-by-line execution

[Current source: lines 1083–1090](../../../../Backend/app/jobs/queue.py#L1083-L1090). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `outcome` | `str`; required; keyword-only | Recovery decision to apply after outside-transaction provider inspection. |
| `error_code` | `str \| None`; default `None`; keyword-only | Machine-readable failure category stored or exposed by the operation. |
| `error_message` | `str \| None`; default `None`; keyword-only | Human-readable failure detail; truncation alone does not redact sensitive content. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
1083 |     def apply_awaiting_upload_outcome(
1084 |         self, *, job_id: UUID, outcome: str, error_code: str | None = None, error_message: str | None = None
1085 |     ) -> bool:
1086 |         return self._tx(
1087 |             lambda s: apply_awaiting_upload_outcome(
1088 |                 s, job_id=job_id, outcome=outcome, error_code=error_code, error_message=error_message
1089 |             )
1090 |         )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L1083 | Define `JobQueueStore.apply_awaiting_upload_outcome`; bind its arguments when called. The body executes only when invoked. |
| L1084 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. Declare parameter `outcome` with annotation `str`. Recovery decision to apply after outside-transaction provider inspection. Declare parameter `error_code` with annotation `str \| None`. Machine-readable failure category stored or exposed by the operation. Declare parameter `error_message` with annotation `str \| None`. Human-readable failure detail; truncation alone does not redact sensitive content. |
| L1085 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L1086 | Compute the return value: `self._tx(lambda s: apply_awaiting_upload_outcome(s, job_id=job_id, outcome=outcome, error_code=error_code, error_message=error_message))` — Call [JobQueueStore._tx](#walk-jobqueuestore--tx) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L1087 | Call [apply_awaiting_upload_outcome](#walk-apply-awaiting-upload-outcome) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L1088 | Supply `job_id` = `job_id`. Durable processing-job UUID. Evaluate the value as: the current `job_id` value. Supply `outcome` = `outcome`. Recovery decision to apply after outside-transaction provider inspection. Evaluate the value as: the current `outcome` value. Supply `error_code` = `error_code`. Machine-readable failure category stored or exposed by the operation. Evaluate the value as: the current `error_code` value. Supply `error_message` = `error_message`. Human-readable failure detail; truncation alone does not redact sensitive content. Evaluate the value as: the current `error_message` value. |
| L1089 | Close the expression/container begun at L1087; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L1090 | Close the expression/container begun at L1086; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `JobQueueStore.find_expired_leases(self, *, now, limit) -> list[JobContext]`

Forwards timestamp/bound through `_tx`, returns contexts after releasing selection locks.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueuestore-find-expired-leases"></a>

#### Line-by-line execution

[Current source: lines 1092–1093](../../../../Backend/app/jobs/queue.py#L1092-L1093). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `now` | `datetime`; required; keyword-only | Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |
| `limit` | `int`; required; keyword-only | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |

**Declared result:** `list[JobContext]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
1092 |     def find_expired_leases(self, *, now: datetime, limit: int) -> list[JobContext]:
1093 |         return self._tx(lambda s: find_expired_leases(s, now=now, limit=limit))
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L1092 | Define `JobQueueStore.find_expired_leases`; bind its arguments when called. The body executes only when invoked. |
| L1093 | Compute the return value: `self._tx(lambda s: find_expired_leases(s, now=now, limit=limit))` — Call [JobQueueStore._tx](#walk-jobqueuestore--tx) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `JobQueueStore.expire_lease(self, *, job_id, now, **backoff) -> str`

Forwards job/time/optional base-cap settings through `_tx`; rechecks the lease and commits its retry/failure transition or returns `skipped`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueuestore-expire-lease"></a>

#### Line-by-line execution

[Current source: lines 1095–1096](../../../../Backend/app/jobs/queue.py#L1095-L1096). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `now` | `datetime`; required; keyword-only | Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |
| `backoff` | `int`; implicitly supplied/collected; ** keyword extras | Caller-supplied backoff; each read, transformation, and validation is traced below. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
1095 |     def expire_lease(self, *, job_id: UUID, now: datetime, **backoff: int) -> str:
1096 |         return self._tx(lambda s: expire_lease(s, job_id=job_id, now=now, **backoff))
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L1095 | Define `JobQueueStore.expire_lease`; bind its arguments when called. The body executes only when invoked. |
| L1096 | Compute the return value: `self._tx(lambda s: expire_lease(s, job_id=job_id, now=now, **backoff))` — Call [JobQueueStore._tx](#walk-jobqueuestore--tx) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `JobQueueStore.cancel_jobs_for_deleted_documents(self, *, limit) -> int`

Forwards limit through `_tx` with the module's default reason; returns committed cancellation count.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueuestore-cancel-jobs-for-deleted-documents"></a>

#### Line-by-line execution

[Current source: lines 1098–1099](../../../../Backend/app/jobs/queue.py#L1098-L1099). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `limit` | `int`; required; keyword-only | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |

**Declared result:** `int`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
1098 |     def cancel_jobs_for_deleted_documents(self, *, limit: int) -> int:
1099 |         return self._tx(lambda s: cancel_jobs_for_deleted_documents(s, limit=limit))
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L1098 | Define `JobQueueStore.cancel_jobs_for_deleted_documents`; bind its arguments when called. The body executes only when invoked. |
| L1099 | Compute the return value: `self._tx(lambda s: cancel_jobs_for_deleted_documents(s, limit=limit))` — Call [JobQueueStore._tx](#walk-jobqueuestore--tx) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `JobQueueStore.find_stale_index_versions(self, *, now, grace_seconds, limit) -> list[SweepCandidate]`

Forwards time/grace/row limit through `_tx`; returns candidates for later provider cleanup.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueuestore-find-stale-index-versions"></a>

#### Line-by-line execution

[Current source: lines 1101–1106](../../../../Backend/app/jobs/queue.py#L1101-L1106). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `now` | `datetime`; required; keyword-only | Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |
| `grace_seconds` | `int`; required; keyword-only | Minimum age before obsolete index versions are eligible for cleanup. |
| `limit` | `int`; required; keyword-only | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |

**Declared result:** `list[SweepCandidate]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
1101 |     def find_stale_index_versions(
1102 |         self, *, now: datetime, grace_seconds: int, limit: int
1103 |     ) -> list[SweepCandidate]:
1104 |         return self._tx(
1105 |             lambda s: find_stale_index_versions(s, now=now, grace_seconds=grace_seconds, limit=limit)
1106 |         )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L1101 | Define `JobQueueStore.find_stale_index_versions`; bind its arguments when called. The body executes only when invoked. |
| L1102 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `now` with annotation `datetime`. Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. Declare parameter `grace_seconds` with annotation `int`. Minimum age before obsolete index versions are eligible for cleanup. Declare parameter `limit` with annotation `int`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. |
| L1103 | Finish/continue the signature; the declared return annotation is `list[SweepCandidate]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L1104 | Compute the return value: `self._tx(lambda s: find_stale_index_versions(s, now=now, grace_seconds=grace_seconds, limit=limit))` — Call [JobQueueStore._tx](#walk-jobqueuestore--tx) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L1105 | Supply `now` = `now`. Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. Evaluate the value as: the current `now` value. Supply `grace_seconds` = `grace_seconds`. Minimum age before obsolete index versions are eligible for cleanup. Evaluate the value as: the current `grace_seconds` value. Supply `limit` = `limit`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. Evaluate the value as: the current `limit` value. |
| L1106 | Close the expression/container begun at L1104; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `JobQueueStore.get_active_version(self, target_document_id) -> tuple[bool, UUID | None]`

Opens/closes a read session and returns the module helper's live/active tuple. No explicit commit or provider delete is part of this call.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-jobqueuestore-get-active-version"></a>

#### Line-by-line execution

[Current source: lines 1108–1110](../../../../Backend/app/jobs/queue.py#L1108-L1110). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `target_document_id` | `UUID`; required; positional or keyword | Immutable target UUID retained even when the live document relationship disappears. |

**Declared result:** `tuple[bool, UUID | None]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
1108 |     def get_active_version(self, target_document_id: UUID) -> tuple[bool, UUID | None]:
1109 |         with self._factory() as session:
1110 |             return get_active_version(session, target_document_id)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L1108 | Define `JobQueueStore.get_active_version`; bind its arguments when called. The body executes only when invoked. |
| L1109 | Enter `self._factory()` — Create a new SQLAlchemy session from the stored factory and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L1110 | Compute the return value: `get_active_version(session, target_document_id)` — Call [get_active_version](#walk-get-active-version) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
