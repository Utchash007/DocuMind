# `app/jobs/reconcile.py`

[Source](../../../../Backend/app/jobs/reconcile.py) · [Backend index](../../README.md)

Four periodic recovery passes: abandoned uploads, expired leases, deleted-resource processing jobs, and stale index versions. Upload TTL and sweep grace both default to 86,400 seconds. Database reads/updates go through the queue store; provider calls run between those transactions.

## Functions

### `ReconcileReport.add(self, action: str) -> None`

Appends one action to the report's per-instance list. The dataclass also has seven zero-initialized counters: queued/failed uploads, requeued/failed leases, cancelled orphans, swept versions, and skipped active versions. Adding text does not increment counters automatically.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-reconcilereport-add"></a>

#### Line-by-line execution

[Current source: lines 72–73](../../../../Backend/app/jobs/reconcile.py#L72-L73). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `action` | `str`; required; positional or keyword | Caller-supplied action; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  72 |     def add(self, action: str) -> None:
  73 |         self.actions.append(action)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L72 | Define `ReconcileReport.add`; bind its arguments when called. The body executes only when invoked. |
| L73 | `self.actions.append(action)` — Append one object to the mutable list in place. The return value is not assigned here. |

<!-- END LINE WALKTHROUGH -->

### `AwaitingUploadOutcomeError.__init__(self, message: str) -> None`

Initializes the exception and `.message`; signals inspection failure to skip this candidate for now.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-awaitinguploadoutcomeerror---init--"></a>

#### Line-by-line execution

[Current source: lines 79–81](../../../../Backend/app/jobs/reconcile.py#L79-L81). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `message` | `str`; required; positional or keyword | Caller-supplied message; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  79 |     def __init__(self, message: str) -> None:
  80 |         super().__init__(message)
  81 |         self.message = message
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L79 | Define `AwaitingUploadOutcomeError.__init__`; bind its arguments when called. The body executes only when invoked. |
| L80 | `super().__init__(message)` — Initialize the base exception/object with the supplied arguments; first obtain the receiver: `super()` — Resolve the superclass proxy for the current method and instance. The return value is not assigned here. |
| L81 | Evaluate the right-hand side, then bind/store it in `self.message`: the current `message` value. |

<!-- END LINE WALKTHROUGH -->

### `awaiting_upload_outcome(*, info: StorageFileInfo | None, expected_size_bytes: int | None) -> tuple[str, str | None, str | None]`

Returns `(outcome, code, message)`. Missing info fails as `storage_missing`. Completion is accepted if `info.completed` is true **or** counters are considered complete; counters use uploaded ≥ total when total >0, otherwise default true. Thus zero counters with false completion are not rejected on completion alone. A known unequal size fails as `upload_incomplete`; otherwise queues. No MIME, positive-size, or hash check is performed here.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-awaiting-upload-outcome"></a>

#### Line-by-line execution

[Current source: lines 84–121](../../../../Backend/app/jobs/reconcile.py#L84-L121). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `info` | `StorageFileInfo \| None`; required; keyword-only | Inspected storage-file metadata including size and upload-completion counters. |
| `expected_size_bytes` | `int \| None`; required; keyword-only | Expected storage length in bytes, or null when no expectation is available. |

**Declared result:** `tuple[str, str | None, str | None]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  84 | def awaiting_upload_outcome(
  85 |     *,
  86 |     info: StorageFileInfo | None,
  87 |     expected_size_bytes: int | None,
  88 | ) -> tuple[str, str | None, str | None]:
  89 |     """Pure decision: queue vs. fail an expired ``awaiting_upload`` job.
  90 | 
  91 |     Returns ``(outcome, error_code, error_message)`` where ``outcome``
  92 |     is ``"queued"`` or ``"failed"``.  A file counts as complete when
  93 |     chunk completion is satisfied (``chunks_uploaded == chunks_total``
  94 |     whenever a chunked upload is declared, or the ``completed`` flag)
  95 |     *and* its size matches the expected size when one is known.  Byte
  96 |     fingerprint verification happens at processing time (the frozen
  97 |     inspection protocol carries no hash); a mismatch there is a
  98 |     terminal ``fingerprint_mismatch``.
  99 |     """
 100 |     if info is None:
 101 |         return "failed", ERROR_STORAGE_MISSING, "reconciled upload file is missing from storage"
 102 |     chunks_complete = True
 103 |     if info.chunks_total > 0:
 104 |         chunks_complete = info.chunks_uploaded >= info.chunks_total
 105 |     if not info.completed and not chunks_complete:
 106 |         return (
 107 |             "failed",
 108 |             ERROR_UPLOAD_INCOMPLETE,
 109 |             f"reconciled upload is incomplete ({info.chunks_uploaded}/{info.chunks_total} chunks)",
 110 |         )
 111 |     if (
 112 |         expected_size_bytes is not None
 113 |         and info.size is not None
 114 |         and int(info.size) != int(expected_size_bytes)
 115 |     ):
 116 |         return (
 117 |             "failed",
 118 |             ERROR_UPLOAD_INCOMPLETE,
 119 |             f"reconciled upload size {info.size} does not match expected {expected_size_bytes}",
 120 |         )
 121 |     return "queued", None, None
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L84 | Define `awaiting_upload_outcome`; bind its arguments when called. The body executes only when invoked. |
| L85 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L86 | Declare parameter `info` with annotation `StorageFileInfo \| None`. Inspected storage-file metadata including size and upload-completion counters. |
| L87 | Declare parameter `expected_size_bytes` with annotation `int \| None`. Expected storage length in bytes, or null when no expectation is available. |
| L88 | Finish/continue the signature; the declared return annotation is `tuple[str, str \| None, str \| None]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L89 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L91 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L92 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L93 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L94 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L95 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L96 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L97 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L98 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L99 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L100 | Evaluate the branch condition: compare whether `info` is the same object as `None`. If truthy, enter L101; otherwise skip this indented block and continue after it. |
| L101 | Compute the return value: build a tuple containing `'failed'`, `ERROR_STORAGE_MISSING`, `'reconciled upload file is missing from storage'`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L102 | Evaluate the right-hand side, then bind/store it in `chunks_complete`: `True`. |
| L103 | Evaluate the branch condition: compare whether `info.chunks_total` is greater than `0`. If truthy, enter L104; otherwise skip this indented block and continue after it. |
| L104 | Evaluate the right-hand side, then bind/store it in `chunks_complete`: compare whether `info.chunks_uploaded` is at least `info.chunks_total`. |
| L105 | Evaluate the branch condition: evaluate `not info.completed and (not chunks_complete)` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L106; otherwise skip this indented block and continue after it. |
| L106 | Compute the return value: build a tuple containing `'failed'`, `ERROR_UPLOAD_INCOMPLETE`, `f'reconciled upload is incomplete ({info.chunks_uploaded}/{info.chunks_total} chunks)'`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L107 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L108 | Contribute the current `ERROR_UPLOAD_INCOMPLETE` value to the expression being assembled. |
| L109 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L110 | Close the expression/container begun at L106; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L111 | Evaluate the branch condition: evaluate `expected_size_bytes is not None and info.size is not None and (int(info.size) != int(expected_size_bytes))` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L116; otherwise skip this indented block and continue after it. |
| L112 | Continue the enclosing expression: evaluate `expected_size_bytes is not None and info.size is not None and (int(info.size) != int(expected_size_bytes))` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. |
| L113 | Continue the enclosing expression: compare whether `info.size` is not the same object as `None`. |
| L114 | Convert the input to an integer (using the optional numeric base). |
| L115 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L116 | Compute the return value: build a tuple containing `'failed'`, `ERROR_UPLOAD_INCOMPLETE`, `f'reconciled upload size {info.size} does not match expected {expected_size_bytes}'`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L117 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L118 | Contribute the current `ERROR_UPLOAD_INCOMPLETE` value to the expression being assembled. |
| L119 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L120 | Close the expression/container begun at L116; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L121 | Compute the return value: build a tuple containing `'queued'`, `None`, `None`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `lease_expiry_outcome(*, attempt_count: int, max_attempts: int) -> str`

Pure comparison: returns `retry_wait` when attempts remain, otherwise `failed`. The SQL transition is separately implemented in `queue.expire_lease`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-lease-expiry-outcome"></a>

#### Line-by-line execution

[Current source: lines 124–126](../../../../Backend/app/jobs/reconcile.py#L124-L126). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `attempt_count` | `int`; required; keyword-only | Number of attempts already claimed; used to decide retries and calculate delay. |
| `max_attempts` | `int`; required; keyword-only | Maximum number of claims before retryable failures become terminal. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 124 | def lease_expiry_outcome(*, attempt_count: int, max_attempts: int) -> str:
 125 |     """Pure decision: requeue (``retry_wait``) or fail an expired lease."""
 126 |     return "retry_wait" if attempt_count < max_attempts else "failed"
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L124 | Define `lease_expiry_outcome`; bind its arguments when called. The body executes only when invoked. |
| L125 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L126 | Compute the return value: check `attempt_count < max_attempts`; when true use `'retry_wait'`, otherwise `'failed'` (only the selected branch is evaluated). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `sweep_eligible(*, candidate_version, active_version, document_live: bool) -> bool`

Accepts UUID/string versions and document liveness. Returns true if document is absent/tombstoned, active version is null, or string versions differ. It only protects the current active version of a live document; no SQL/provider call occurs here.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-sweep-eligible"></a>

#### Line-by-line execution

[Current source: lines 129–144](../../../../Backend/app/jobs/reconcile.py#L129-L144). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `candidate_version` | `UUID \| str`; required; keyword-only | Caller-supplied candidate version; each read, transformation, and validation is traced below. |
| `active_version` | `UUID \| str \| None`; required; keyword-only | Caller-supplied active version; each read, transformation, and validation is traced below. |
| `document_live` | `bool`; required; keyword-only | Caller-supplied document live; each read, transformation, and validation is traced below. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 129 | def sweep_eligible(
 130 |     *,
 131 |     candidate_version: UUID | str,
 132 |     active_version: UUID | str | None,
 133 |     document_live: bool,
 134 | ) -> bool:
 135 |     """Pure guard: may this namespace be swept right now?
 136 | 
 137 |     Never the active version of a live document (JOB-09/11).  Versions
 138 |     of documents that are gone/tombstoned are always sweepable.
 139 |     """
 140 |     if not document_live:
 141 |         return True
 142 |     if active_version is None:
 143 |         return True
 144 |     return str(candidate_version) != str(active_version)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L129 | Define `sweep_eligible`; bind its arguments when called. The body executes only when invoked. |
| L130 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L131 | Declare parameter `candidate_version` with annotation `UUID \| str`. Caller-supplied candidate version; its uses and transformations are traced below. |
| L132 | Declare parameter `active_version` with annotation `UUID \| str \| None`. Caller-supplied active version; its uses and transformations are traced below. |
| L133 | Declare parameter `document_live` with annotation `bool`. Caller-supplied document live; its uses and transformations are traced below. |
| L134 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L135 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L137 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L138 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L139 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L140 | Evaluate the branch condition: invert the truthiness of `document_live`. If truthy, enter L141; otherwise skip this indented block and continue after it. |
| L141 | Compute the return value: `True`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L142 | Evaluate the branch condition: compare whether `active_version` is the same object as `None`. If truthy, enter L143; otherwise skip this indented block and continue after it. |
| L143 | Compute the return value: `True`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L144 | Compute the return value: compare whether `str(candidate_version)` differs from `str(active_version)`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `Reconciler.__init__(self, store, *, storage=None, index_service=None, awaiting_upload_ttl_seconds=86400, sweep_grace_seconds=86400, batch_size=50, backoff_base_seconds=5, backoff_cap_seconds=3600) -> None`

Stores the queue/provider collaborators and timing/batch settings without validation or I/O. Provider absence is handled per pass.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-reconciler---init--"></a>

#### Line-by-line execution

[Current source: lines 150–169](../../../../Backend/app/jobs/reconcile.py#L150-L169). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `store` | `JobQueueStore`; required; positional or keyword | Queue-store facade used by recovery passes. |
| `storage` | `StoragePort \| None`; default `None`; keyword-only | Storage collaborator for private file creation, inspection, ranged reads, or deletion. |
| `index_service` | `IndexPort \| None`; default `None`; keyword-only | Collaborator for version-scoped vector writes/deletes. |
| `awaiting_upload_ttl_seconds` | `int`; default `DEFAULT_AWAITING_UPLOAD_TTL_SECONDS`; keyword-only | Caller-supplied awaiting upload ttl seconds; each read, transformation, and validation is traced below. |
| `sweep_grace_seconds` | `int`; default `DEFAULT_SWEEP_GRACE_SECONDS`; keyword-only | Caller-supplied sweep grace seconds; each read, transformation, and validation is traced below. |
| `batch_size` | `int`; default `50`; keyword-only | Maximum batch size for the operation; validation/clamping is explicit in the body. |
| `backoff_base_seconds` | `int`; default `5`; keyword-only | Base retry delay, doubled with successive attempts before capping/jitter. |
| `backoff_cap_seconds` | `int`; default `3600`; keyword-only | Maximum retry-delay bound passed to the backoff calculation. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 150 |     def __init__(
 151 |         self,
 152 |         store: JobQueueStore,
 153 |         *,
 154 |         storage: StoragePort | None = None,
 155 |         index_service: IndexPort | None = None,
 156 |         awaiting_upload_ttl_seconds: int = DEFAULT_AWAITING_UPLOAD_TTL_SECONDS,
 157 |         sweep_grace_seconds: int = DEFAULT_SWEEP_GRACE_SECONDS,
 158 |         batch_size: int = 50,
 159 |         backoff_base_seconds: int = 5,
 160 |         backoff_cap_seconds: int = 3600,
 161 |     ) -> None:
 162 |         self.store = store
 163 |         self.storage = storage
 164 |         self.index_service = index_service
 165 |         self.awaiting_upload_ttl_seconds = awaiting_upload_ttl_seconds
 166 |         self.sweep_grace_seconds = sweep_grace_seconds
 167 |         self.batch_size = batch_size
 168 |         self.backoff_base_seconds = backoff_base_seconds
 169 |         self.backoff_cap_seconds = backoff_cap_seconds
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L150 | Define `Reconciler.__init__`; bind its arguments when called. The body executes only when invoked. |
| L151 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L152 | Declare parameter `store` with annotation `JobQueueStore`. Queue-store facade used by recovery passes. |
| L153 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L154 | Declare parameter `storage` with annotation `StoragePort \| None`. Storage collaborator for private file creation, inspection, ranged reads, or deletion. |
| L155 | Declare parameter `index_service` with annotation `IndexPort \| None`. Collaborator for version-scoped vector writes/deletes. |
| L156 | Declare parameter `awaiting_upload_ttl_seconds` with annotation `int`. Caller-supplied awaiting upload ttl seconds; its uses and transformations are traced below. |
| L157 | Declare parameter `sweep_grace_seconds` with annotation `int`. Caller-supplied sweep grace seconds; its uses and transformations are traced below. |
| L158 | Declare parameter `batch_size` with annotation `int`. Maximum batch size for the operation; validation/clamping is explicit in the body. |
| L159 | Declare parameter `backoff_base_seconds` with annotation `int`. Base retry delay, doubled with successive attempts before capping/jitter. |
| L160 | Declare parameter `backoff_cap_seconds` with annotation `int`. Maximum retry-delay bound passed to the backoff calculation. |
| L161 | Finish/continue the signature; the declared return annotation is `None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L162 | Evaluate the right-hand side, then bind/store it in `self.store`: the current `store` value. |
| L163 | Evaluate the right-hand side, then bind/store it in `self.storage`: the current `storage` value. |
| L164 | Evaluate the right-hand side, then bind/store it in `self.index_service`: the current `index_service` value. |
| L165 | Evaluate the right-hand side, then bind/store it in `self.awaiting_upload_ttl_seconds`: the current `awaiting_upload_ttl_seconds` value. |
| L166 | Evaluate the right-hand side, then bind/store it in `self.sweep_grace_seconds`: the current `sweep_grace_seconds` value. |
| L167 | Evaluate the right-hand side, then bind/store it in `self.batch_size`: the current `batch_size` value. |
| L168 | Evaluate the right-hand side, then bind/store it in `self.backoff_base_seconds`: the current `backoff_base_seconds` value. |
| L169 | Evaluate the right-hand side, then bind/store it in `self.backoff_cap_seconds`: the current `backoff_cap_seconds` value. |

<!-- END LINE WALKTHROUGH -->

### `Reconciler.reconcile_awaiting_upload(self, now: datetime) -> ReconcileReport`

Computes TTL cutoff, loads bounded contexts, and inspects each outside SQL. Inspection errors log/skip. Applies the decision in a fresh queue transaction; a false result means another actor already changed the job. Counts successful queue/failure transitions and records action text; after a persisted failure, attempts partial-file deletion. Returns only this pass's report.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-reconciler-reconcile-awaiting-upload"></a>

#### Line-by-line execution

[Current source: lines 172–198](../../../../Backend/app/jobs/reconcile.py#L172-L198). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `now` | `datetime`; required; positional or keyword | Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |

**Declared result:** `ReconcileReport`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 172 |     def reconcile_awaiting_upload(self, now: datetime) -> ReconcileReport:
 173 |         report = ReconcileReport()
 174 |         cutoff = now - timedelta(seconds=self.awaiting_upload_ttl_seconds)
 175 |         candidates = self.store.find_expired_awaiting_upload(cutoff=cutoff, limit=self.batch_size)
 176 |         for context in candidates:
 177 |             try:
 178 |                 outcome, error_code, error_message = self._inspect_awaiting_upload(context)
 179 |             except AwaitingUploadOutcomeError as exc:
 180 |                 log.warning("reconcile awaiting_upload job %s: %s", context.job_id, exc.message)
 181 |                 continue
 182 |             applied = self.store.apply_awaiting_upload_outcome(
 183 |                 job_id=context.job_id,
 184 |                 outcome=outcome,
 185 |                 error_code=error_code,
 186 |                 error_message=error_message,
 187 |             )
 188 |             if not applied:
 189 |                 # The normal upload path won the race; nothing to do.
 190 |                 continue
 191 |             if outcome == "queued":
 192 |                 report.queued_uploads += 1
 193 |                 report.add(f"queued reconciled upload for job {context.job_id}")
 194 |             else:
 195 |                 report.failed_uploads += 1
 196 |                 report.add(f"failed reconciled upload for job {context.job_id}: {error_code}")
 197 |                 self._delete_partial_storage(context)
 198 |         return report
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L172 | Define `Reconciler.reconcile_awaiting_upload`; bind its arguments when called. The body executes only when invoked. |
| L173 | Evaluate the right-hand side, then bind/store it in `report`: `ReconcileReport()` — Construct `ReconcileReport` with the shown fields; its class/model initialization rules apply. |
| L174 | Evaluate the right-hand side, then bind/store it in `cutoff`: subtract `now` and `timedelta(seconds=self.awaiting_upload_ttl_seconds)`, following the parentheses/operator precedence shown in `now - timedelta(seconds=self.awaiting_upload_ttl_seconds)`. |
| L175 | Evaluate the right-hand side, then bind/store it in `candidates`: `self.store.find_expired_awaiting_upload(cutoff=cutoff, limit=self.batch_size)` — Invoke `self.store.find_expired_awaiting_upload` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L176 | Iterate `candidates` (the current `candidates` value), assigning each item to `context`. Execute the indented body once per item; an empty iterable skips it. |
| L177 | Enter the protected block; failures are matched against `AwaitingUploadOutcomeError` in order. |
| L178 | Evaluate the right-hand side, then bind/store it in `(outcome, error_code, error_message)`: `self._inspect_awaiting_upload(context)` — Call [Reconciler._inspect_awaiting_upload](#walk-reconciler--inspect-awaiting-upload) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L179 | Handle `AwaitingUploadOutcomeError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L180 | `log.warning('reconcile awaiting_upload job %s: %s', context.job_id, exc.message)` — Emit a warning log message, substituting the supplied formatting arguments. The return value is not assigned here. |
| L181 | Skip the rest of this iteration and advance the innermost loop to its next item; active finally/context exits still apply. |
| L182 | Evaluate the right-hand side, then bind/store it in `applied`: `self.store.apply_awaiting_upload_outcome(job_id=context.job_id, outcome=outcome, error_code=error_code, error_message=error_message)` — Invoke `self.store.apply_awaiting_upload_outcome` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L183 | Supply `job_id` = `context.job_id`. Durable processing-job UUID. Evaluate the value as: the `job_id` attribute of `context`. |
| L184 | Supply `outcome` = `outcome`. Recovery decision to apply after outside-transaction provider inspection. Evaluate the value as: the current `outcome` value. |
| L185 | Supply `error_code` = `error_code`. Machine-readable failure category stored or exposed by the operation. Evaluate the value as: the current `error_code` value. |
| L186 | Supply `error_message` = `error_message`. Human-readable failure detail; truncation alone does not redact sensitive content. Evaluate the value as: the current `error_message` value. |
| L187 | Close the expression/container begun at L182; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L188 | Evaluate the branch condition: invert the truthiness of `applied`. If truthy, enter L190; otherwise skip this indented block and continue after it. |
| L189 | Comment only: The normal upload path won the race; nothing to do.. It does not execute; the neighboring code determines behavior. |
| L190 | Skip the rest of this iteration and advance the innermost loop to its next item; active finally/context exits still apply. |
| L191 | Evaluate the branch condition: compare whether `outcome` equals `'queued'`. If truthy, enter L192; otherwise enter the alternative at L195. |
| L192 | Update `report.queued_uploads` in place using `1` and the Add operation; the previous target value participates in the calculation. |
| L193 | `report.add(f'queued reconciled upload for job {context.job_id}')` — Append the action description to the reconciliation report; counters are updated separately. The return value is not assigned here. |
| L194 | Enter this alternative only when the associated condition was false (or the associated try/loop completed without its exceptional exit). |
| L195 | Update `report.failed_uploads` in place using `1` and the Add operation; the previous target value participates in the calculation. |
| L196 | `report.add(f'failed reconciled upload for job {context.job_id}: {error_code}')` — Append the action description to the reconciliation report; counters are updated separately. The return value is not assigned here. |
| L197 | `self._delete_partial_storage(context)` — Call [Reconciler._delete_partial_storage](#walk-reconciler--delete-partial-storage) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L198 | Compute the return value: the current `report` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `Reconciler._inspect_awaiting_upload(self, context: JobContext) -> tuple[str, str | None, str | None]`

Resolves context bucket/file references. Missing reference returns a terminal missing-storage decision. Missing adapter raises `AwaitingUploadOutcomeError`. All inspection exceptions—including the real adapter's not-found error—are wrapped as retry-later inspection errors. A returned `None` can reach the pure missing-file decision, but a raised not-found exception does not. Passes only `context.expected_size_bytes` to the pure decision, without fallback to the live document size.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-reconciler--inspect-awaiting-upload"></a>

#### Line-by-line execution

[Current source: lines 200–217](../../../../Backend/app/jobs/reconcile.py#L200-L217). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `context` | `JobContext`; required; positional or keyword | Loaded job facts copied before provider work; see the annotated type and field accesses below. |

**Declared result:** `tuple[str, str | None, str | None]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 200 |     def _inspect_awaiting_upload(
 201 |         self, context: JobContext
 202 |     ) -> tuple[str, str | None, str | None]:
 203 |         bucket_id = context.storage_bucket_id
 204 |         file_id = context.storage_file_id
 205 |         if bucket_id is None or file_id is None:
 206 |             return "failed", ERROR_STORAGE_MISSING, "job has no storage bucket/file reference"
 207 |         if self.storage is None:
 208 |             raise AwaitingUploadOutcomeError("storage adapter is not configured")
 209 |         try:
 210 |             info = self.storage.inspect_storage_file(bucket_id=bucket_id, file_id=file_id)
 211 |         except Exception as exc:
 212 |             raise AwaitingUploadOutcomeError(
 213 |                 f"storage inspection failed: {safe_message(exc)}"
 214 |             ) from exc
 215 |         return awaiting_upload_outcome(
 216 |             info=info, expected_size_bytes=context.expected_size_bytes
 217 |         )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L200 | Define `Reconciler._inspect_awaiting_upload`; bind its arguments when called. The body executes only when invoked. |
| L201 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `context` with annotation `JobContext`. Loaded job facts copied before provider work; see the annotated type and field accesses below. |
| L202 | Finish/continue the signature; the declared return annotation is `tuple[str, str \| None, str \| None]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L203 | Evaluate the right-hand side, then bind/store it in `bucket_id`: the `storage_bucket_id` attribute of `context`. |
| L204 | Evaluate the right-hand side, then bind/store it in `file_id`: the `storage_file_id` attribute of `context`. |
| L205 | Evaluate the branch condition: evaluate `bucket_id is None or file_id is None` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L206; otherwise skip this indented block and continue after it. |
| L206 | Compute the return value: build a tuple containing `'failed'`, `ERROR_STORAGE_MISSING`, `'job has no storage bucket/file reference'`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L207 | Evaluate the branch condition: compare whether `self.storage` is the same object as `None`. If truthy, enter L208; otherwise skip this indented block and continue after it. |
| L208 | Raise `AwaitingUploadOutcomeError('storage adapter is not configured')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L209 | Enter the protected block; failures are matched against `Exception` in order. |
| L210 | Evaluate the right-hand side, then bind/store it in `info`: `self.storage.inspect_storage_file(bucket_id=bucket_id, file_id=file_id)` — Inspect private storage metadata for this bucket/file reference; provider failures propagate through the adapter. |
| L211 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L212 | Raise `AwaitingUploadOutcomeError(f'storage inspection failed: {safe_message(exc)}')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L213 | Call [safe_message](errors.md#walk-safe-message) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L214 | Contribute the current `exc` value to the expression being assembled. |
| L215 | Compute the return value: `awaiting_upload_outcome(info=info, expected_size_bytes=context.expected_size_bytes)` — Call [awaiting_upload_outcome](#walk-awaiting-upload-outcome) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L216 | Supply `info` = `info`. Inspected storage-file metadata including size and upload-completion counters. Evaluate the value as: the current `info` value. Supply `expected_size_bytes` = `context.expected_size_bytes`. Expected storage length in bytes, or null when no expectation is available. Evaluate the value as: the `expected_size_bytes` attribute of `context`. |
| L217 | Close the expression/container begun at L215; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `Reconciler._delete_partial_storage(self, context: JobContext) -> None`

Skips missing references/adapter; otherwise tries idempotent file deletion and logs exceptions. No cleanup job/retry marker is created here. Since the upload job has already become terminal, a failed deletion is not automatically reselected by the awaiting-upload pass.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-reconciler--delete-partial-storage"></a>

#### Line-by-line execution

[Current source: lines 219–232](../../../../Backend/app/jobs/reconcile.py#L219-L232). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `context` | `JobContext`; required; positional or keyword | Loaded job facts copied before provider work; see the annotated type and field accesses below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 219 |     def _delete_partial_storage(self, context: JobContext) -> None:
 220 |         """Best-effort cleanup of an abandoned partial upload."""
 221 |         bucket_id = context.storage_bucket_id
 222 |         file_id = context.storage_file_id
 223 |         if bucket_id is None or file_id is None or self.storage is None:
 224 |             return
 225 |         try:
 226 |             self.storage.delete_storage_file(bucket_id=bucket_id, file_id=file_id)
 227 |         except Exception as exc:  # idempotent cleanup is retried next round
 228 |             log.warning(
 229 |                 "reconcile: partial-storage cleanup for job %s failed: %s",
 230 |                 context.job_id,
 231 |                 safe_message(exc),
 232 |             )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L219 | Define `Reconciler._delete_partial_storage`; bind its arguments when called. The body executes only when invoked. |
| L220 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L221 | Evaluate the right-hand side, then bind/store it in `bucket_id`: the `storage_bucket_id` attribute of `context`. |
| L222 | Evaluate the right-hand side, then bind/store it in `file_id`: the `storage_file_id` attribute of `context`. |
| L223 | Evaluate the branch condition: evaluate `bucket_id is None or file_id is None or self.storage is None` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L224; otherwise skip this indented block and continue after it. |
| L224 | Compute the return value: None. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L225 | Enter the protected block; failures are matched against `Exception` in order. |
| L226 | `self.storage.delete_storage_file(bucket_id=bucket_id, file_id=file_id)` — Delete the private object through the adapter's idempotent not-found handling. The return value is not assigned here. |
| L227 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L228 | `log.warning('reconcile: partial-storage cleanup for job %s failed: %s', context.job_id, safe_message(exc))` — Emit a warning log message, substituting the supplied formatting arguments; inputs include `safe_message(exc)` — Call [safe_message](errors.md#walk-safe-message) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L229 | Supply positional argument 1 to `log.warning`: `'reconcile: partial-storage cleanup for job %s failed: %s'`. |
| L230 | Supply positional argument 2 to `log.warning`: the `job_id` attribute of `context`. |
| L231 | `safe_message(exc)` — Call [safe_message](errors.md#walk-safe-message) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L232 | Close the expression/container begun at L228; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `Reconciler.reconcile_expired_leases(self, now: datetime) -> ReconcileReport`

Loads expired candidates and asks the store to recheck/expire each with configured backoff. Counts/actions only `retry_wait` and `failed`; concurrently renewed `skipped` results add nothing. Returns this pass's report.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-reconciler-reconcile-expired-leases"></a>

#### Line-by-line execution

[Current source: lines 235–251](../../../../Backend/app/jobs/reconcile.py#L235-L251). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `now` | `datetime`; required; positional or keyword | Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |

**Declared result:** `ReconcileReport`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 235 |     def reconcile_expired_leases(self, now: datetime) -> ReconcileReport:
 236 |         report = ReconcileReport()
 237 |         candidates = self.store.find_expired_leases(now=now, limit=self.batch_size)
 238 |         for context in candidates:
 239 |             outcome = self.store.expire_lease(
 240 |                 job_id=context.job_id,
 241 |                 now=now,
 242 |                 backoff_base_seconds=self.backoff_base_seconds,
 243 |                 backoff_cap_seconds=self.backoff_cap_seconds,
 244 |             )
 245 |             if outcome == "retry_wait":
 246 |                 report.requeued_leases += 1
 247 |                 report.add(f"requeued expired lease for job {context.job_id}")
 248 |             elif outcome == "failed":
 249 |                 report.failed_leases += 1
 250 |                 report.add(f"failed expired lease for job {context.job_id}")
 251 |         return report
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L235 | Define `Reconciler.reconcile_expired_leases`; bind its arguments when called. The body executes only when invoked. |
| L236 | Evaluate the right-hand side, then bind/store it in `report`: `ReconcileReport()` — Construct `ReconcileReport` with the shown fields; its class/model initialization rules apply. |
| L237 | Evaluate the right-hand side, then bind/store it in `candidates`: `self.store.find_expired_leases(now=now, limit=self.batch_size)` — Invoke `self.store.find_expired_leases` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L238 | Iterate `candidates` (the current `candidates` value), assigning each item to `context`. Execute the indented body once per item; an empty iterable skips it. |
| L239 | Evaluate the right-hand side, then bind/store it in `outcome`: `self.store.expire_lease(job_id=context.job_id, now=now, backoff_base_seconds=self.backoff_base_seconds, backoff_cap_seconds=self.backoff_cap_seconds)` — Invoke `self.store.expire_lease` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L240 | Supply `job_id` = `context.job_id`. Durable processing-job UUID. Evaluate the value as: the `job_id` attribute of `context`. |
| L241 | Supply `now` = `now`. Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. Evaluate the value as: the current `now` value. |
| L242 | Supply `backoff_base_seconds` = `self.backoff_base_seconds`. Base retry delay, doubled with successive attempts before capping/jitter. Evaluate the value as: the `backoff_base_seconds` attribute of `self`. |
| L243 | Supply `backoff_cap_seconds` = `self.backoff_cap_seconds`. Maximum retry-delay bound passed to the backoff calculation. Evaluate the value as: the `backoff_cap_seconds` attribute of `self`. |
| L244 | Close the expression/container begun at L239; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L245 | Evaluate the branch condition: compare whether `outcome` equals `'retry_wait'`. If truthy, enter L246; otherwise enter the alternative at L248. |
| L246 | Update `report.requeued_leases` in place using `1` and the Add operation; the previous target value participates in the calculation. |
| L247 | `report.add(f'requeued expired lease for job {context.job_id}')` — Append the action description to the reconciliation report; counters are updated separately. The return value is not assigned here. |
| L248 | Evaluate the branch condition: compare whether `outcome` equals `'failed'`. If truthy, enter L249; otherwise skip this indented block and continue after it. |
| L249 | Update `report.failed_leases` in place using `1` and the Add operation; the previous target value participates in the calculation. |
| L250 | `report.add(f'failed expired lease for job {context.job_id}')` — Append the action description to the reconciliation report; counters are updated separately. The return value is not assigned here. |
| L251 | Compute the return value: the current `report` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `Reconciler.reconcile_orphaned_jobs(self) -> ReconcileReport`

Calls bounded `cancel_jobs_for_deleted_documents`, copies its count, and adds one aggregate action if nonzero. The queue query excludes cleanup and awaiting-upload jobs.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-reconciler-reconcile-orphaned-jobs"></a>

#### Line-by-line execution

[Current source: lines 254–260](../../../../Backend/app/jobs/reconcile.py#L254-L260). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |

**Declared result:** `ReconcileReport`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 254 |     def reconcile_orphaned_jobs(self) -> ReconcileReport:
 255 |         report = ReconcileReport()
 256 |         cancelled = self.store.cancel_jobs_for_deleted_documents(limit=self.batch_size)
 257 |         report.cancelled_orphans = cancelled
 258 |         if cancelled:
 259 |             report.add(f"cancelled {cancelled} job(s) for deleted documents")
 260 |         return report
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L254 | Define `Reconciler.reconcile_orphaned_jobs`; bind its arguments when called. The body executes only when invoked. |
| L255 | Evaluate the right-hand side, then bind/store it in `report`: `ReconcileReport()` — Construct `ReconcileReport` with the shown fields; its class/model initialization rules apply. |
| L256 | Evaluate the right-hand side, then bind/store it in `cancelled`: `self.store.cancel_jobs_for_deleted_documents(limit=self.batch_size)` — Invoke `self.store.cancel_jobs_for_deleted_documents` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L257 | Evaluate the right-hand side, then bind/store it in `report.cancelled_orphans`: the current `cancelled` value. |
| L258 | Evaluate the branch condition: the current `cancelled` value. If truthy, enter L259; otherwise skip this indented block and continue after it. |
| L259 | `report.add(f'cancelled {cancelled} job(s) for deleted documents')` — Append the action description to the reconciliation report; counters are updated separately. The return value is not assigned here. |
| L260 | Compute the return value: the current `report` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `Reconciler.sweep_stale_versions(self, now: datetime) -> ReconcileReport`

Returns empty report without an index adapter. Otherwise loads candidates, re-reads document live/active state before each delete, counts protected active versions, and deletes eligible namespaces with owner/project/document/version scope. Provider deletion failures log/continue; successes increment sweep count/action. No swept marker is written, so candidates can be deleted idempotently again on future passes. Read and external deletion are separate operations, not one atomic transaction.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-reconciler-sweep-stale-versions"></a>

#### Line-by-line execution

[Current source: lines 263–304](../../../../Backend/app/jobs/reconcile.py#L263-L304). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `now` | `datetime`; required; positional or keyword | Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |

**Declared result:** `ReconcileReport`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 263 |     def sweep_stale_versions(self, now: datetime) -> ReconcileReport:
 264 |         report = ReconcileReport()
 265 |         if self.index_service is None:
 266 |             return report
 267 |         candidates = self.store.find_stale_index_versions(
 268 |             now=now, grace_seconds=self.sweep_grace_seconds, limit=self.batch_size
 269 |         )
 270 |         for candidate in candidates:
 271 |             # JOB-09: never trust the candidate snapshot -- re-read the
 272 |             # active pointer at delete time.
 273 |             live, active = self.store.get_active_version(candidate.target_document_id)
 274 |             if not sweep_eligible(
 275 |                 candidate_version=candidate.index_version,
 276 |                 active_version=active,
 277 |                 document_live=live,
 278 |             ):
 279 |                 report.skipped_active_versions += 1
 280 |                 report.add(
 281 |                     f"kept active version {candidate.index_version} "
 282 |                     f"for document {candidate.target_document_id}"
 283 |                 )
 284 |                 continue
 285 |             try:
 286 |                 self.index_service.delete_index_version(
 287 |                     user_id=candidate.owner_user_id,
 288 |                     project_id=candidate.project_id,
 289 |                     document_id=candidate.target_document_id,
 290 |                     index_version=candidate.index_version,
 291 |                 )
 292 |             except Exception as exc:
 293 |                 log.warning(
 294 |                     "sweep: delete of version %s failed (retry next round): %s",
 295 |                     candidate.index_version,
 296 |                     safe_message(exc),
 297 |                 )
 298 |                 continue
 299 |             report.swept_versions += 1
 300 |             report.add(
 301 |                 f"swept version {candidate.index_version} "
 302 |                 f"for document {candidate.target_document_id}"
 303 |             )
 304 |         return report
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L263 | Define `Reconciler.sweep_stale_versions`; bind its arguments when called. The body executes only when invoked. |
| L264 | Evaluate the right-hand side, then bind/store it in `report`: `ReconcileReport()` — Construct `ReconcileReport` with the shown fields; its class/model initialization rules apply. |
| L265 | Evaluate the branch condition: compare whether `self.index_service` is the same object as `None`. If truthy, enter L266; otherwise skip this indented block and continue after it. |
| L266 | Compute the return value: the current `report` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L267 | Evaluate the right-hand side, then bind/store it in `candidates`: `self.store.find_stale_index_versions(now=now, grace_seconds=self.sweep_grace_seconds, limit=self.batch_size)` — Invoke `self.store.find_stale_index_versions` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L268 | Supply `now` = `now`. Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. Evaluate the value as: the current `now` value. Supply `grace_seconds` = `self.sweep_grace_seconds`. Minimum age before obsolete index versions are eligible for cleanup. Evaluate the value as: the `sweep_grace_seconds` attribute of `self`. Supply `limit` = `self.batch_size`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. Evaluate the value as: the `batch_size` attribute of `self`. |
| L269 | Close the expression/container begun at L267; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L270 | Iterate `candidates` (the current `candidates` value), assigning each item to `candidate`. Execute the indented body once per item; an empty iterable skips it. |
| L271 | Comment only: JOB-09: never trust the candidate snapshot -- re-read the. It does not execute; the neighboring code determines behavior. |
| L272 | Comment only: active pointer at delete time.. It does not execute; the neighboring code determines behavior. |
| L273 | Evaluate the right-hand side, then bind/store it in `(live, active)`: `self.store.get_active_version(candidate.target_document_id)` — Read whether the document is live and which index version is currently published. |
| L274 | Evaluate the branch condition: invert the truthiness of `sweep_eligible(candidate_version=candidate.index_version, active_version=active, document_live=live)`. If truthy, enter L279; otherwise skip this indented block and continue after it. |
| L275 | Supply `candidate_version` = `candidate.index_version`.  Evaluate the value as: the `index_version` attribute of `candidate`. |
| L276 | Supply `active_version` = `active`.  Evaluate the value as: the current `active` value. |
| L277 | Supply `document_live` = `live`.  Evaluate the value as: the current `live` value. |
| L278 | Close the expression/container begun at L274; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L279 | Update `report.skipped_active_versions` in place using `1` and the Add operation; the previous target value participates in the calculation. |
| L280 | `report.add(f'kept active version {candidate.index_version} for document {candidate.target_document_id}')` — Append the action description to the reconciliation report; counters are updated separately. The return value is not assigned here. |
| L281 | Supply positional argument 1 to `report.add`: format a string by inserting `candidate.index_version`, `candidate.target_document_id` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L282 | Supply positional argument 1 to `report.add`: format a string by inserting `candidate.index_version`, `candidate.target_document_id` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L283 | Close the expression/container begun at L280; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L284 | Skip the rest of this iteration and advance the innermost loop to its next item; active finally/context exits still apply. |
| L285 | Enter the protected block; failures are matched against `Exception` in order. |
| L286 | `self.index_service.delete_index_version` with the arguments detailed below — Delete the exact user/project/document/version namespace from Chroma; this does not change the active SQL pointer. The return value is not assigned here. |
| L287 | Supply `user_id` = `candidate.owner_user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `owner_user_id` attribute of `candidate`. |
| L288 | Supply `project_id` = `candidate.project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the `project_id` attribute of `candidate`. |
| L289 | Supply `document_id` = `candidate.target_document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the `target_document_id` attribute of `candidate`. |
| L290 | Supply `index_version` = `candidate.index_version`. UUID of one document's vector-index namespace, separate from its active publication pointer. Evaluate the value as: the `index_version` attribute of `candidate`. |
| L291 | Close the expression/container begun at L286; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L292 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L293 | `log.warning('sweep: delete of version %s failed (retry next round): %s', candidate.index_version, safe_message(exc))` — Emit a warning log message, substituting the supplied formatting arguments; inputs include `safe_message(exc)` — Call [safe_message](errors.md#walk-safe-message) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L294 | Supply positional argument 1 to `log.warning`: `'sweep: delete of version %s failed (retry next round): %s'`. |
| L295 | Supply positional argument 2 to `log.warning`: the `index_version` attribute of `candidate`. |
| L296 | `safe_message(exc)` — Call [safe_message](errors.md#walk-safe-message) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L297 | Close the expression/container begun at L293; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L298 | Skip the rest of this iteration and advance the innermost loop to its next item; active finally/context exits still apply. |
| L299 | Update `report.swept_versions` in place using `1` and the Add operation; the previous target value participates in the calculation. |
| L300 | `report.add(f'swept version {candidate.index_version} for document {candidate.target_document_id}')` — Append the action description to the reconciliation report; counters are updated separately. The return value is not assigned here. |
| L301 | Supply positional argument 1 to `report.add`: format a string by inserting `candidate.index_version`, `candidate.target_document_id` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L302 | Supply positional argument 1 to `report.add`: format a string by inserting `candidate.index_version`, `candidate.target_document_id` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L303 | Close the expression/container begun at L300; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L304 | Compute the return value: the current `report` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `Reconciler.run_once(self, now: datetime | None = None) -> ReconcileReport`

Uses supplied time or UTC now for all passes. Creates four zero-argument lambdas in upload/lease/orphan/sweep order, invokes them serially, catches/logs whole-pass failures, and sums successful reports' counters/actions. A partial pass that raises before returning may have committed changes without contributing its partial counters. Returns the aggregate report; one failed pass does not prevent later passes.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-reconciler-run-once"></a>

#### Line-by-line execution

[Current source: lines 306–332](../../../../Backend/app/jobs/reconcile.py#L306-L332). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `now` | `datetime \| None`; default `None`; positional or keyword | Timestamp used for expiry/due/grace comparisons; callers normally supply timezone-aware UTC. |

**Declared result:** `ReconcileReport`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 306 |     def run_once(self, now: datetime | None = None) -> ReconcileReport:
 307 |         """Run all four passes; one pass failing never blocks the rest."""
 308 |         from app.db.base import utcnow
 309 | 
 310 |         moment = now or utcnow()
 311 |         total = ReconcileReport()
 312 |         passes = (
 313 |             ("awaiting_upload", lambda: self.reconcile_awaiting_upload(moment)),
 314 |             ("expired_leases", lambda: self.reconcile_expired_leases(moment)),
 315 |             ("orphans", lambda: self.reconcile_orphaned_jobs()),
 316 |             ("sweep", lambda: self.sweep_stale_versions(moment)),
 317 |         )
 318 |         for name, fn in passes:
 319 |             try:
 320 |                 part = fn()
 321 |             except Exception as exc:
 322 |                 log.warning("reconcile pass %s failed: %s", name, safe_message(exc))
 323 |                 continue
 324 |             total.queued_uploads += part.queued_uploads
 325 |             total.failed_uploads += part.failed_uploads
 326 |             total.requeued_leases += part.requeued_leases
 327 |             total.failed_leases += part.failed_leases
 328 |             total.cancelled_orphans += part.cancelled_orphans
 329 |             total.swept_versions += part.swept_versions
 330 |             total.skipped_active_versions += part.skipped_active_versions
 331 |             total.actions.extend(part.actions)
 332 |         return total
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L306 | Define `Reconciler.run_once`; bind its arguments when called. The body executes only when invoked. |
| L307 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L308 | Import `utcnow` from `app.db.base`; inside a function this import is deferred until this path is reached. |
| L310 | Evaluate the right-hand side, then bind/store it in `moment`: evaluate `now or utcnow()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L311 | Evaluate the right-hand side, then bind/store it in `total`: `ReconcileReport()` — Construct `ReconcileReport` with the shown fields; its class/model initialization rules apply. |
| L312 | Evaluate the right-hand side, then bind/store it in `passes`: build a tuple containing `('awaiting_upload', lambda: self.reconcile_awaiting_upload(moment))`, `('expired_leases', lambda: self.reconcile_expired_leases(moment))`, `('orphans', lambda: self.reconcile_orphaned_jobs())`, `('sweep', lambda: self.sweep_stale_versions(moment))`. |
| L313 | Call [Reconciler.reconcile_awaiting_upload](#walk-reconciler-reconcile-awaiting-upload) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L314 | Call [Reconciler.reconcile_expired_leases](#walk-reconciler-reconcile-expired-leases) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L315 | Call [Reconciler.reconcile_orphaned_jobs](#walk-reconciler-reconcile-orphaned-jobs) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L316 | Call [Reconciler.sweep_stale_versions](#walk-reconciler-sweep-stale-versions) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L317 | Close the expression/container begun at L312; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L318 | Iterate `passes` (the current `passes` value), assigning each item to `(name, fn)`. Execute the indented body once per item; an empty iterable skips it. |
| L319 | Enter the protected block; failures are matched against `Exception` in order. |
| L320 | Evaluate the right-hand side, then bind/store it in `part`: `fn()` — Invoke `fn` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L321 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L322 | `log.warning('reconcile pass %s failed: %s', name, safe_message(exc))` — Emit a warning log message, substituting the supplied formatting arguments; inputs include `safe_message(exc)` — Call [safe_message](errors.md#walk-safe-message) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L323 | Skip the rest of this iteration and advance the innermost loop to its next item; active finally/context exits still apply. |
| L324 | Update `total.queued_uploads` in place using `part.queued_uploads` and the Add operation; the previous target value participates in the calculation. |
| L325 | Update `total.failed_uploads` in place using `part.failed_uploads` and the Add operation; the previous target value participates in the calculation. |
| L326 | Update `total.requeued_leases` in place using `part.requeued_leases` and the Add operation; the previous target value participates in the calculation. |
| L327 | Update `total.failed_leases` in place using `part.failed_leases` and the Add operation; the previous target value participates in the calculation. |
| L328 | Update `total.cancelled_orphans` in place using `part.cancelled_orphans` and the Add operation; the previous target value participates in the calculation. |
| L329 | Update `total.swept_versions` in place using `part.swept_versions` and the Add operation; the previous target value participates in the calculation. |
| L330 | Update `total.skipped_active_versions` in place using `part.skipped_active_versions` and the Add operation; the previous target value participates in the calculation. |
| L331 | `total.actions.extend(part.actions)` — Append every item from the supplied iterable to the list in order. The return value is not assigned here. |
| L332 | Compute the return value: the current `total` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
