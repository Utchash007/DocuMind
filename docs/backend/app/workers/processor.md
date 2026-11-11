# `app/workers/processor.py`

[Source](../../../../Backend/app/workers/processor.py) · [Backend index](../../README.md)

Executes already-committed job claims using injected queue, storage, extraction, embedding, and indexing services. Outcomes are `succeeded`, `retry_wait`, `failed`, `stale`, `lease_lost`, or `cancelled`. `ProcessOutcome` is a frozen dataclass of job UUID, kind, status, and optional detail. The database job remains authoritative.

`ProcessorConfig` is frozen: required worker ID; defaults lease 120s, 25 MiB, 200 pages, embedding batches 16, attempt budget 3600s, backoff 5–3600s. Its generated constructor performs no budget validation; the entry-point config does.

## Functions

### `_kind_str(kind: Any) -> str`

Returns `str(kind.value)` when that attribute exists, otherwise `str(kind)`, normalizing enum/string inputs.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--kind-str"></a>

#### Line-by-line execution

[Current source: lines 74–75](../../../../Backend/app/workers/processor.py#L74-L75). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `kind` | `Any`; required; positional or keyword | Caller-supplied kind; each read, transformation, and validation is traced below. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  74 | def _kind_str(kind: Any) -> str:
  75 |     return str(getattr(kind, "value", kind))
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L74 | Define `_kind_str`; bind its arguments when called. The body executes only when invoked. |
| L75 | Compute the return value: `str(getattr(kind, 'value', kind))` — Convert the input to its string representation; inputs include `getattr(kind, 'value', kind)` — Read the named attribute, using the supplied default only if the attribute is absent. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `ProcessorConfig.heartbeat_interval_seconds(self) -> int`

Property returning `max(1, min(30, lease_seconds // 3))`: roughly three renewals per lease, capped at 30 seconds and floored at one.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-processorconfig-heartbeat-interval-seconds"></a>

#### Line-by-line execution

[Current source: lines 91–93](../../../../Backend/app/workers/processor.py#L91-L93). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |

**Declared result:** `int`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  91 |     @property
  92 |     def heartbeat_interval_seconds(self) -> int:
  93 |         return max(1, min(30, self.lease_seconds // 3))
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L91 | Expose this getter as an attribute; reading the property invokes the body instead of requiring an explicit method call. |
| L92 | Define `ProcessorConfig.heartbeat_interval_seconds`; bind its arguments when called. The body executes only when invoked. |
| L93 | Compute the return value: `max(1, min(30, self.lease_seconds // 3))` — Choose the largest supplied value; nested min/max calls implement the stated bound; inputs include `min(30, self.lease_seconds // 3)` — Choose the smallest supplied value; nested min/max calls implement the stated bound. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_Heartbeat.__init__(self, queue, *, job_id, lease_token, worker_id, lease_seconds, interval_seconds) -> None`

Stores exact claim identity and renewal settings, creates separate lost/stop events, and initializes thread to null. Does not renew or start a thread yet.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--heartbeat---init--"></a>

#### Line-by-line execution

[Current source: lines 107–125](../../../../Backend/app/workers/processor.py#L107-L125). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `queue` | `QueuePort`; required; positional or keyword | Queue collaborator for short claim, lease, progress, and terminal-state operations. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `lease_token` | `int`; required; keyword-only | Monotonic claim token used to reject stale worker writes. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `lease_seconds` | `int`; required; keyword-only | Lease duration in seconds; positive-duration validation is not implicit in this parameter. |
| `interval_seconds` | `int`; required; keyword-only | Caller-supplied interval seconds; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 107 |     def __init__(
 108 |         self,
 109 |         queue: QueuePort,
 110 |         *,
 111 |         job_id: UUID,
 112 |         lease_token: int,
 113 |         worker_id: str,
 114 |         lease_seconds: int,
 115 |         interval_seconds: int,
 116 |     ) -> None:
 117 |         self._queue = queue
 118 |         self._job_id = job_id
 119 |         self._token = lease_token
 120 |         self._worker_id = worker_id
 121 |         self._lease_seconds = lease_seconds
 122 |         self._interval = interval_seconds
 123 |         self.lost = threading.Event()
 124 |         self._stop = threading.Event()
 125 |         self._thread: threading.Thread | None = None
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L107 | Define `_Heartbeat.__init__`; bind its arguments when called. The body executes only when invoked. |
| L108 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L109 | Declare parameter `queue` with annotation `QueuePort`. Queue collaborator for short claim, lease, progress, and terminal-state operations. |
| L110 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L111 | Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. |
| L112 | Declare parameter `lease_token` with annotation `int`. Monotonic claim token used to reject stale worker writes. |
| L113 | Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. |
| L114 | Declare parameter `lease_seconds` with annotation `int`. Lease duration in seconds; positive-duration validation is not implicit in this parameter. |
| L115 | Declare parameter `interval_seconds` with annotation `int`. Caller-supplied interval seconds; its uses and transformations are traced below. |
| L116 | Finish/continue the signature; the declared return annotation is `None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L117 | Evaluate the right-hand side, then bind/store it in `self._queue`: the current `queue` value. |
| L118 | Evaluate the right-hand side, then bind/store it in `self._job_id`: the current `job_id` value. |
| L119 | Evaluate the right-hand side, then bind/store it in `self._token`: the current `lease_token` value. |
| L120 | Evaluate the right-hand side, then bind/store it in `self._worker_id`: the current `worker_id` value. |
| L121 | Evaluate the right-hand side, then bind/store it in `self._lease_seconds`: the current `lease_seconds` value. |
| L122 | Evaluate the right-hand side, then bind/store it in `self._interval`: the current `interval_seconds` value. |
| L123 | Evaluate the right-hand side, then bind/store it in `self.lost`: `threading.Event()` — Create an initially unset synchronization event shared by cooperating threads. |
| L124 | Evaluate the right-hand side, then bind/store it in `self._stop`: `threading.Event()` — Create an initially unset synchronization event shared by cooperating threads. |
| L125 | Evaluate the right-hand side, then bind/store it in `self._thread`: None (no value). |

<!-- END LINE WALKTHROUGH -->

### `_Heartbeat.start(self) -> None`

Creates and starts a daemon `lease-heartbeat` thread targeting `_run`. There is no repeated-start guard.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--heartbeat-start"></a>

#### Line-by-line execution

[Current source: lines 127–129](../../../../Backend/app/workers/processor.py#L127-L129). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 127 |     def start(self) -> None:
 128 |         self._thread = threading.Thread(target=self._run, name="lease-heartbeat", daemon=True)
 129 |         self._thread.start()
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L127 | Define `_Heartbeat.start`; bind its arguments when called. The body executes only when invoked. |
| L128 | Evaluate the right-hand side, then bind/store it in `self._thread`: `threading.Thread(target=self._run, name='lease-heartbeat', daemon=True)` — Construct a thread with the given target; it starts only when start() is called. |
| L129 | `self._thread.start()` — Start `self._thread` so its configured target runs on the background thread. The return value is not assigned here. |

<!-- END LINE WALKTHROUGH -->

### `_Heartbeat.stop(self) -> None`

Sets the stop event and joins the existing thread for at most two seconds. A blocked renewal may outlive that join timeout.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--heartbeat-stop"></a>

#### Line-by-line execution

[Current source: lines 131–134](../../../../Backend/app/workers/processor.py#L131-L134). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 131 |     def stop(self) -> None:
 132 |         self._stop.set()
 133 |         if self._thread is not None:
 134 |             self._thread.join(timeout=2.0)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L131 | Define `_Heartbeat.stop`; bind its arguments when called. The body executes only when invoked. |
| L132 | `self._stop.set()` — Signal the `self._stop` event so waiting/cooperating code observes the request. The return value is not assigned here. |
| L133 | Evaluate the branch condition: compare whether `self._thread` is not the same object as `None`. If truthy, enter L134; otherwise skip this indented block and continue after it. |
| L134 | `self._thread.join(timeout=2.0)` — Wait for the heartbeat thread to finish, bounded by the supplied join timeout. The return value is not assigned here. |

<!-- END LINE WALKTHROUGH -->

### `_Heartbeat._run(self) -> None`

Waits for the interval unless stopped, then renews the exact claim. Database exceptions log and retry next interval without immediately marking lease lost. A false renewal sets the lost event and exits. This signals cooperative stopping; it cannot interrupt an in-progress provider call.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--heartbeat--run"></a>

#### Line-by-line execution

[Current source: lines 136–150](../../../../Backend/app/workers/processor.py#L136-L150). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 136 |     def _run(self) -> None:
 137 |         while not self._stop.wait(self._interval):
 138 |             try:
 139 |                 renewed = self._queue.renew_job_lease(
 140 |                     job_id=self._job_id,
 141 |                     lease_token=self._token,
 142 |                     worker_id=self._worker_id,
 143 |                     lease_seconds=self._lease_seconds,
 144 |                 )
 145 |             except Exception as exc:  # transient DB errors do not kill the job
 146 |                 log.warning("heartbeat for job %s failed: %s", self._job_id, safe_message(exc))
 147 |                 continue
 148 |             if not renewed:
 149 |                 self.lost.set()
 150 |                 return
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L136 | Define `_Heartbeat._run`; bind its arguments when called. The body executes only when invoked. |
| L137 | Re-evaluate `not self._stop.wait(self._interval)` before every iteration; run the body while truthy and leave when false or when a break executes. |
| L138 | Enter the protected block; failures are matched against `Exception` in order. |
| L139 | Evaluate the right-hand side, then bind/store it in `renewed`: `self._queue.renew_job_lease(job_id=self._job_id, lease_token=self._token, worker_id=self._worker_id, lease_seconds=self._lease_seconds)` — Renew only the matching running, owned, token-current, unexpired lease; a stale claim returns false. |
| L140 | Supply `job_id` = `self._job_id`. Durable processing-job UUID. Evaluate the value as: the `_job_id` attribute of `self`. |
| L141 | Supply `lease_token` = `self._token`. Monotonic claim token used to reject stale worker writes. Evaluate the value as: the `_token` attribute of `self`. |
| L142 | Supply `worker_id` = `self._worker_id`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: the `_worker_id` attribute of `self`. |
| L143 | Supply `lease_seconds` = `self._lease_seconds`. Lease duration in seconds; positive-duration validation is not implicit in this parameter. Evaluate the value as: the `_lease_seconds` attribute of `self`. |
| L144 | Close the expression/container begun at L139; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L145 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L146 | `log.warning('heartbeat for job %s failed: %s', self._job_id, safe_message(exc))` — Emit a warning log message, substituting the supplied formatting arguments; inputs include `safe_message(exc)` — Call [safe_message](../jobs/errors.md#walk-safe-message) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L147 | Skip the rest of this iteration and advance the innermost loop to its next item; active finally/context exits still apply. |
| L148 | Evaluate the branch condition: invert the truthiness of `renewed`. If truthy, enter L149; otherwise skip this indented block and continue after it. |
| L149 | `self.lost.set()` — Signal the `self.lost` event so waiting/cooperating code observes the request. The return value is not assigned here. |
| L150 | Compute the return value: None. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `DocumentProcessor.__init__(self, *, queue, storage, embedder=None, index_service=None, extractor=None, config) -> None`

Stores collaborators/config and creates a default `PdfExtractionService` with configured page/byte budgets if not supplied. Construction does not process a job.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-documentprocessor---init--"></a>

#### Line-by-line execution

[Current source: lines 156–173](../../../../Backend/app/workers/processor.py#L156-L173). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `queue` | `QueuePort`; required; keyword-only | Queue collaborator for short claim, lease, progress, and terminal-state operations. |
| `storage` | `StoragePort`; required; keyword-only | Storage collaborator for private file creation, inspection, ranged reads, or deletion. |
| `embedder` | `EmbedderPort \| None`; default `None`; keyword-only | Embedding collaborator; the function selects its default only where explicitly shown. |
| `index_service` | `IndexPort \| None`; default `None`; keyword-only | Collaborator for version-scoped vector writes/deletes. |
| `extractor` | `PdfExtractionService \| None`; default `None`; keyword-only | Caller-supplied extractor; each read, transformation, and validation is traced below. |
| `config` | `ProcessorConfig`; required; keyword-only | Configuration object consumed by the field accesses below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 156 |     def __init__(
 157 |         self,
 158 |         *,
 159 |         queue: QueuePort,
 160 |         storage: StoragePort,
 161 |         embedder: EmbedderPort | None = None,
 162 |         index_service: IndexPort | None = None,
 163 |         extractor: PdfExtractionService | None = None,
 164 |         config: ProcessorConfig,
 165 |     ) -> None:
 166 |         self.queue = queue
 167 |         self.storage = storage
 168 |         self.embedder = embedder
 169 |         self.index_service = index_service
 170 |         self.extractor = extractor or PdfExtractionService(
 171 |             max_pages=config.max_pages, max_file_bytes=config.max_file_bytes
 172 |         )
 173 |         self.config = config
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L156 | Define `DocumentProcessor.__init__`; bind its arguments when called. The body executes only when invoked. |
| L157 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L158 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L159 | Declare parameter `queue` with annotation `QueuePort`. Queue collaborator for short claim, lease, progress, and terminal-state operations. |
| L160 | Declare parameter `storage` with annotation `StoragePort`. Storage collaborator for private file creation, inspection, ranged reads, or deletion. |
| L161 | Declare parameter `embedder` with annotation `EmbedderPort \| None`. Embedding collaborator; the function selects its default only where explicitly shown. |
| L162 | Declare parameter `index_service` with annotation `IndexPort \| None`. Collaborator for version-scoped vector writes/deletes. |
| L163 | Declare parameter `extractor` with annotation `PdfExtractionService \| None`. Caller-supplied extractor; its uses and transformations are traced below. |
| L164 | Declare parameter `config` with annotation `ProcessorConfig`. Configuration object consumed by the field accesses below. |
| L165 | Finish/continue the signature; the declared return annotation is `None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L166 | Evaluate the right-hand side, then bind/store it in `self.queue`: the current `queue` value. |
| L167 | Evaluate the right-hand side, then bind/store it in `self.storage`: the current `storage` value. |
| L168 | Evaluate the right-hand side, then bind/store it in `self.embedder`: the current `embedder` value. |
| L169 | Evaluate the right-hand side, then bind/store it in `self.index_service`: the current `index_service` value. |
| L170 | Evaluate the right-hand side, then bind/store it in `self.extractor`: evaluate `extractor or PdfExtractionService(max_pages=config.max_pages, max_file_bytes=config.max_file_bytes)` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L171 | Supply `max_pages` = `config.max_pages`. Maximum PDF pages accepted by extraction. Evaluate the value as: the `max_pages` attribute of `config`. Supply `max_file_bytes` = `config.max_file_bytes`. Maximum PDF byte count accepted by this component. Evaluate the value as: the `max_file_bytes` attribute of `config`. |
| L172 | Close the expression/container begun at L170; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L173 | Evaluate the right-hand side, then bind/store it in `self.config`: the current `config` value. |

<!-- END LINE WALKTHROUGH -->

### `DocumentProcessor.process(self, claim: JobClaim) -> ProcessOutcome`

Normalizes kind and loads detached job context. Missing/non-running/token-mismatched context returns stale. Dispatches delete kind to `_process_delete`, every other kind to `_process_document`. Catches classified job/embedding/index/PDF errors and unexpected exceptions, then calls `_fail`. These exception handlers pass `context=None` even if a context was loaded, affecting the returned retry-status estimate described below.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-documentprocessor-process"></a>

#### Line-by-line execution

[Current source: lines 176–200](../../../../Backend/app/workers/processor.py#L176-L200). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `claim` | `JobClaim`; required; positional or keyword | Committed job/turn claim carrying the identity and fencing fields required by later operations. |

**Declared result:** `ProcessOutcome`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 176 |     def process(self, claim: JobClaim) -> ProcessOutcome:
 177 |         kind = _kind_str(claim.kind)
 178 |         context = None
 179 |         try:
 180 |             context = self.queue.load_job_context(claim.job_id)
 181 |             if (
 182 |                 context is None
 183 |                 or context.status != "running"
 184 |                 or context.lease_token != claim.lease_token
 185 |             ):
 186 |                 return ProcessOutcome(claim.job_id, kind, OUTCOME_STALE, "claim no longer current")
 187 |             if kind == KIND_DELETE:
 188 |                 return self._process_delete(claim, context)
 189 |             return self._process_document(claim, context)
 190 |         except JobError as exc:
 191 |             return self._fail(claim, exc.code, exc.message, exc.retryable, context=None)
 192 |         except EmbeddingProviderError as exc:
 193 |             return self._fail(claim, ERROR_EMBEDDING_PROVIDER, exc.message, True, context=None)
 194 |         except IndexWriteError as exc:
 195 |             return self._fail(claim, ERROR_INDEX_WRITE, exc.message, True, context=None)
 196 |         except PdfError as exc:
 197 |             return self._fail(claim, exc.code, exc.message, False, context=None)
 198 |         except Exception as exc:  # never let one job kill the worker loop
 199 |             log.exception("unexpected processor error for job %s", claim.job_id)
 200 |             return self._fail(claim, ERROR_UNEXPECTED, safe_message(exc), True, context=None)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L176 | Define `DocumentProcessor.process`; bind its arguments when called. The body executes only when invoked. |
| L177 | Evaluate the right-hand side, then bind/store it in `kind`: `_kind_str(claim.kind)` — Call [_kind_str](#walk--kind-str) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L178 | Evaluate the right-hand side, then bind/store it in `context`: None (no value). |
| L179 | Enter the protected block; failures are matched against `JobError`, `EmbeddingProviderError`, `IndexWriteError`, `PdfError`, `Exception` in order. |
| L180 | Evaluate the right-hand side, then bind/store it in `context`: `self.queue.load_job_context(claim.job_id)` — Invoke `self.queue.load_job_context` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L181 | Evaluate the branch condition: evaluate `context is None or context.status != 'running' or context.lease_token != claim.lease_token` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L186; otherwise skip this indented block and continue after it. |
| L182 | Continue the enclosing expression: evaluate `context is None or context.status != 'running' or context.lease_token != claim.lease_token` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L183 | Continue the enclosing expression: compare whether `context.status` differs from `'running'`. |
| L184 | Continue the enclosing expression: compare whether `context.lease_token` differs from `claim.lease_token`. |
| L185 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L186 | Compute the return value: `ProcessOutcome(claim.job_id, kind, OUTCOME_STALE, 'claim no longer current')` — Construct `ProcessOutcome` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L187 | Evaluate the branch condition: compare whether `kind` equals `KIND_DELETE`. If truthy, enter L188; otherwise skip this indented block and continue after it. |
| L188 | Compute the return value: `self._process_delete(claim, context)` — Call [DocumentProcessor._process_delete](#walk-documentprocessor--process-delete) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L189 | Compute the return value: `self._process_document(claim, context)` — Call [DocumentProcessor._process_document](#walk-documentprocessor--process-document) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L190 | Handle `JobError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L191 | Compute the return value: `self._fail(claim, exc.code, exc.message, exc.retryable, context=None)` — Call [DocumentProcessor._fail](#walk-documentprocessor--fail) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L192 | Handle `EmbeddingProviderError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L193 | Compute the return value: `self._fail(claim, ERROR_EMBEDDING_PROVIDER, exc.message, True, context=None)` — Call [DocumentProcessor._fail](#walk-documentprocessor--fail) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L194 | Handle `IndexWriteError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L195 | Compute the return value: `self._fail(claim, ERROR_INDEX_WRITE, exc.message, True, context=None)` — Call [DocumentProcessor._fail](#walk-documentprocessor--fail) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L196 | Handle `PdfError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L197 | Compute the return value: `self._fail(claim, exc.code, exc.message, False, context=None)` — Call [DocumentProcessor._fail](#walk-documentprocessor--fail) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L198 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L199 | `log.exception('unexpected processor error for job %s', claim.job_id)` — Emit an error log including the current exception traceback. The return value is not assigned here. |
| L200 | Compute the return value: `self._fail(claim, ERROR_UNEXPECTED, safe_message(exc), True, context=None)` — Call [DocumentProcessor._fail](#walk-documentprocessor--fail) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result; inputs include `safe_message(exc)` — Call [safe_message](../jobs/errors.md#walk-safe-message) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `DocumentProcessor._process_document(self, claim, context) -> ProcessOutcome`

Starts monotonic timing and a heartbeat. Checks timeout/document liveness, downloads a temporary PDF, then checks timeout/lease and extracts owned versioned chunks; always unlinks the temporary file after that stage. Records chunking progress, checks time, embeds in batches, records embedding completion, checks time again, requires an index adapter, and writes the namespace. Written-count mismatch fails the job. Records indexing/publishing progress, rechecks lease/document liveness, and calls fenced queue completion with chunk count. Returns succeeded, stale publication, cancelled, timeout failure, or lease-lost as appropriate. Always stops heartbeat. Time/lease checks occur at explicit boundaries, not continuously or inside provider calls; no timeout check follows indexing.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-documentprocessor--process-document"></a>

#### Line-by-line execution

[Current source: lines 203–273](../../../../Backend/app/workers/processor.py#L203-L273). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `claim` | `JobClaim`; required; positional or keyword | Committed job/turn claim carrying the identity and fencing fields required by later operations. |
| `context` | `Any`; required; positional or keyword | Loaded job facts copied before provider work; see the annotated type and field accesses below. |

**Declared result:** `ProcessOutcome`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 203 |     def _process_document(self, claim: JobClaim, context: Any) -> ProcessOutcome:
 204 |         started = time.monotonic()
 205 |         heartbeat = self._start_heartbeat(claim)
 206 |         try:
 207 |             if self._timed_out(started, claim):
 208 |                 return self._fail(claim, ERROR_JOB_TIMEOUT, "job exceeded its time budget", True, context)
 209 |             if self._still_live(context.target_document_id) is False:
 210 |                 return self._cancel(claim, "document was deleted during processing")
 211 |             pdf_path = self._download_pdf(context)
 212 |             try:
 213 |                 if self._timed_out(started, claim):
 214 |                     return self._fail(claim, ERROR_JOB_TIMEOUT, "job exceeded its time budget", True, context)
 215 |                 if heartbeat.lost.is_set():
 216 |                     return self._lease_lost(claim, heartbeat)
 217 |                 chunks = self.extractor.extract_pdf_chunks(
 218 |                     pdf_path,
 219 |                     file_name=context.storage_file_name or context.file_id or "document.pdf",
 220 |                     document_id=context.target_document_id,
 221 |                     index_version=context.index_version,
 222 |                 )
 223 |             finally:
 224 |                 pdf_path.unlink(missing_ok=True)
 225 |             if heartbeat.lost.is_set():
 226 |                 return self._lease_lost(claim, heartbeat)
 227 |             if not self._progress(claim, stage="chunking", current=0, total=len(chunks)):
 228 |                 return self._lease_lost(claim, heartbeat)
 229 |             if self._timed_out(started, claim):
 230 |                 return self._fail(claim, ERROR_JOB_TIMEOUT, "job exceeded its time budget", True, context)
 231 |             embeddings = self._embed(claim, heartbeat, chunks)
 232 |             if isinstance(embeddings, ProcessOutcome):
 233 |                 return embeddings
 234 |             if not self._progress(claim, stage="embedding", current=len(chunks), total=len(chunks)):
 235 |                 return self._lease_lost(claim, heartbeat)
 236 |             if self._timed_out(started, claim):
 237 |                 return self._fail(claim, ERROR_JOB_TIMEOUT, "job exceeded its time budget", True, context)
 238 |             if self.index_service is None:
 239 |                 raise JobError(ERROR_UNEXPECTED, "index service is not configured")
 240 |             if not self._progress(claim, stage="indexing", current=0, total=len(chunks)):
 241 |                 return self._lease_lost(claim, heartbeat)
 242 |             written = self.index_service.publish_index_version(
 243 |                 user_id=context.owner_user_id,
 244 |                 project_id=context.project_id,
 245 |                 document_id=context.target_document_id,
 246 |                 index_version=context.index_version,
 247 |                 chunks=chunks,
 248 |                 embeddings=embeddings,
 249 |             )
 250 |             if written != len(chunks):
 251 |                 raise JobError(
 252 |                     ERROR_INDEX_WRITE,
 253 |                     f"index wrote {written} of {len(chunks)} chunks",
 254 |                 )
 255 |             if not self._progress(claim, stage="indexing", current=written, total=len(chunks)):
 256 |                 return self._lease_lost(claim, heartbeat)
 257 |             if heartbeat.lost.is_set():
 258 |                 return self._lease_lost(claim, heartbeat)
 259 |             if not self._progress(claim, stage="publishing", current=written, total=len(chunks)):
 260 |                 return self._lease_lost(claim, heartbeat)
 261 |             if self._still_live(context.target_document_id) is False:
 262 |                 return self._cancel(claim, "document was deleted during processing")
 263 |             published = self.queue.complete_job(
 264 |                 job_id=claim.job_id,
 265 |                 lease_token=int(claim.lease_token),
 266 |                 worker_id=self.config.worker_id,
 267 |                 chunk_count=len(chunks),
 268 |             )
 269 |             if not published:
 270 |                 return ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_STALE, "publication fenced out")
 271 |             return ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_SUCCEEDED)
 272 |         finally:
 273 |             heartbeat.stop()
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L203 | Define `DocumentProcessor._process_document`; bind its arguments when called. The body executes only when invoked. |
| L204 | Evaluate the right-hand side, then bind/store it in `started`: `time.monotonic()` — Read the monotonic clock for elapsed-time comparisons, unaffected by wall-clock adjustments. |
| L205 | Evaluate the right-hand side, then bind/store it in `heartbeat`: `self._start_heartbeat(claim)` — Call [DocumentProcessor._start_heartbeat](#walk-documentprocessor--start-heartbeat) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L206 | Enter the protected block. The finally block runs regardless of return or failure. |
| L207 | Evaluate the branch condition: `self._timed_out(started, claim)` — Call [DocumentProcessor._timed_out](#walk-documentprocessor--timed-out) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. If truthy, enter L208; otherwise skip this indented block and continue after it. |
| L208 | Compute the return value: `self._fail(claim, ERROR_JOB_TIMEOUT, 'job exceeded its time budget', True, context)` — Call [DocumentProcessor._fail](#walk-documentprocessor--fail) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L209 | Evaluate the branch condition: compare whether `self._still_live(context.target_document_id)` is the same object as `False`. If truthy, enter L210; otherwise skip this indented block and continue after it. |
| L210 | Compute the return value: `self._cancel(claim, 'document was deleted during processing')` — Call [DocumentProcessor._cancel](#walk-documentprocessor--cancel) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L211 | Evaluate the right-hand side, then bind/store it in `pdf_path`: `self._download_pdf(context)` — Call [DocumentProcessor._download_pdf](#walk-documentprocessor--download-pdf) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L212 | Enter the protected block. The finally block runs regardless of return or failure. |
| L213 | Evaluate the branch condition: `self._timed_out(started, claim)` — Call [DocumentProcessor._timed_out](#walk-documentprocessor--timed-out) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. If truthy, enter L214; otherwise skip this indented block and continue after it. |
| L214 | Compute the return value: `self._fail(claim, ERROR_JOB_TIMEOUT, 'job exceeded its time budget', True, context)` — Call [DocumentProcessor._fail](#walk-documentprocessor--fail) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L215 | Evaluate the branch condition: `heartbeat.lost.is_set()` — Read whether the synchronization event has been signalled. If truthy, enter L216; otherwise skip this indented block and continue after it. |
| L216 | Compute the return value: `self._lease_lost(claim, heartbeat)` — Call [DocumentProcessor._lease_lost](#walk-documentprocessor--lease-lost) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L217 | Evaluate the right-hand side, then bind/store it in `chunks`: `self.extractor.extract_pdf_chunks` with the arguments detailed below — Invoke `self.extractor.extract_pdf_chunks` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L218 | Supply positional argument 1 to `self.extractor.extract_pdf_chunks`: the current `pdf_path` value. |
| L219 | Supply `file_name` = `context.storage_file_name or context.file_id or 'document.pdf'`. Display PDF filename; immutable IDs establish ownership and evidence identity. Evaluate the value as: evaluate `context.storage_file_name or context.file_id or 'document.pdf'` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L220 | Supply `document_id` = `context.target_document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the `target_document_id` attribute of `context`. |
| L221 | Supply `index_version` = `context.index_version`. UUID of one document's vector-index namespace, separate from its active publication pointer. Evaluate the value as: the `index_version` attribute of `context`. |
| L222 | Close the expression/container begun at L217; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L223 | Enter unconditional cleanup after the protected work, including on exception, return, break, or continue. |
| L224 | `pdf_path.unlink(missing_ok=True)` — Remove the local file; missing_ok=True makes an already absent file harmless. The return value is not assigned here. |
| L225 | Evaluate the branch condition: `heartbeat.lost.is_set()` — Read whether the synchronization event has been signalled. If truthy, enter L226; otherwise skip this indented block and continue after it. |
| L226 | Compute the return value: `self._lease_lost(claim, heartbeat)` — Call [DocumentProcessor._lease_lost](#walk-documentprocessor--lease-lost) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L227 | Evaluate the branch condition: invert the truthiness of `self._progress(claim, stage='chunking', current=0, total=len(chunks))`. If truthy, enter L228; otherwise skip this indented block and continue after it. |
| L228 | Compute the return value: `self._lease_lost(claim, heartbeat)` — Call [DocumentProcessor._lease_lost](#walk-documentprocessor--lease-lost) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L229 | Evaluate the branch condition: `self._timed_out(started, claim)` — Call [DocumentProcessor._timed_out](#walk-documentprocessor--timed-out) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. If truthy, enter L230; otherwise skip this indented block and continue after it. |
| L230 | Compute the return value: `self._fail(claim, ERROR_JOB_TIMEOUT, 'job exceeded its time budget', True, context)` — Call [DocumentProcessor._fail](#walk-documentprocessor--fail) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L231 | Evaluate the right-hand side, then bind/store it in `embeddings`: `self._embed(claim, heartbeat, chunks)` — Call [DocumentProcessor._embed](#walk-documentprocessor--embed) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L232 | Evaluate the branch condition: `isinstance(embeddings, ProcessOutcome)` — Check the runtime type against the supplied class or tuple of classes. If truthy, enter L233; otherwise skip this indented block and continue after it. |
| L233 | Compute the return value: the current `embeddings` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L234 | Evaluate the branch condition: invert the truthiness of `self._progress(claim, stage='embedding', current=len(chunks), total=len(chunks))`. If truthy, enter L235; otherwise skip this indented block and continue after it. |
| L235 | Compute the return value: `self._lease_lost(claim, heartbeat)` — Call [DocumentProcessor._lease_lost](#walk-documentprocessor--lease-lost) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L236 | Evaluate the branch condition: `self._timed_out(started, claim)` — Call [DocumentProcessor._timed_out](#walk-documentprocessor--timed-out) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. If truthy, enter L237; otherwise skip this indented block and continue after it. |
| L237 | Compute the return value: `self._fail(claim, ERROR_JOB_TIMEOUT, 'job exceeded its time budget', True, context)` — Call [DocumentProcessor._fail](#walk-documentprocessor--fail) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L238 | Evaluate the branch condition: compare whether `self.index_service` is the same object as `None`. If truthy, enter L239; otherwise skip this indented block and continue after it. |
| L239 | Raise `JobError(ERROR_UNEXPECTED, 'index service is not configured')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L240 | Evaluate the branch condition: invert the truthiness of `self._progress(claim, stage='indexing', current=0, total=len(chunks))`. If truthy, enter L241; otherwise skip this indented block and continue after it. |
| L241 | Compute the return value: `self._lease_lost(claim, heartbeat)` — Call [DocumentProcessor._lease_lost](#walk-documentprocessor--lease-lost) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L242 | Evaluate the right-hand side, then bind/store it in `written`: `self.index_service.publish_index_version` with the arguments detailed below — Invoke `self.index_service.publish_index_version` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L243 | Supply `user_id` = `context.owner_user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `owner_user_id` attribute of `context`. |
| L244 | Supply `project_id` = `context.project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the `project_id` attribute of `context`. |
| L245 | Supply `document_id` = `context.target_document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the `target_document_id` attribute of `context`. |
| L246 | Supply `index_version` = `context.index_version`. UUID of one document's vector-index namespace, separate from its active publication pointer. Evaluate the value as: the `index_version` attribute of `context`. |
| L247 | Supply `chunks` = `chunks`. PDF text chunks with the metadata required by this operation. Evaluate the value as: the current `chunks` value. |
| L248 | Supply `embeddings` = `embeddings`. Per-chunk numeric vectors supplied for indexing. Evaluate the value as: the current `embeddings` value. |
| L249 | Close the expression/container begun at L242; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L250 | Evaluate the branch condition: compare whether `written` differs from `len(chunks)`. If truthy, enter L251; otherwise skip this indented block and continue after it. |
| L251 | Raise `JobError(ERROR_INDEX_WRITE, f'index wrote {written} of {len(chunks)} chunks')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L252 | Supply positional argument 1 to `JobError`: the current `ERROR_INDEX_WRITE` value. |
| L253 | Count the items/characters in the supplied container/string. |
| L254 | Close the expression/container begun at L251; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L255 | Evaluate the branch condition: invert the truthiness of `self._progress(claim, stage='indexing', current=written, total=len(chunks))`. If truthy, enter L256; otherwise skip this indented block and continue after it. |
| L256 | Compute the return value: `self._lease_lost(claim, heartbeat)` — Call [DocumentProcessor._lease_lost](#walk-documentprocessor--lease-lost) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L257 | Evaluate the branch condition: `heartbeat.lost.is_set()` — Read whether the synchronization event has been signalled. If truthy, enter L258; otherwise skip this indented block and continue after it. |
| L258 | Compute the return value: `self._lease_lost(claim, heartbeat)` — Call [DocumentProcessor._lease_lost](#walk-documentprocessor--lease-lost) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L259 | Evaluate the branch condition: invert the truthiness of `self._progress(claim, stage='publishing', current=written, total=len(chunks))`. If truthy, enter L260; otherwise skip this indented block and continue after it. |
| L260 | Compute the return value: `self._lease_lost(claim, heartbeat)` — Call [DocumentProcessor._lease_lost](#walk-documentprocessor--lease-lost) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L261 | Evaluate the branch condition: compare whether `self._still_live(context.target_document_id)` is the same object as `False`. If truthy, enter L262; otherwise skip this indented block and continue after it. |
| L262 | Compute the return value: `self._cancel(claim, 'document was deleted during processing')` — Call [DocumentProcessor._cancel](#walk-documentprocessor--cancel) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L263 | Evaluate the right-hand side, then bind/store it in `published`: `self.queue.complete_job(job_id=claim.job_id, lease_token=int(claim.lease_token), worker_id=self.config.worker_id, chunk_count=len(chunks))` — Attempt the queue's fenced completion/publication and return whether it succeeded or was already published. |
| L264 | Supply `job_id` = `claim.job_id`. Durable processing-job UUID. Evaluate the value as: the `job_id` attribute of `claim`. |
| L265 | Supply `lease_token` = `int(claim.lease_token)`. Monotonic claim token used to reject stale worker writes. Evaluate the value as: `int(claim.lease_token)` — Convert the input to an integer (using the optional numeric base). |
| L266 | Supply `worker_id` = `self.config.worker_id`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: the `worker_id` attribute of `self.config`. |
| L267 | Supply `chunk_count` = `len(chunks)`. Number of chunks to record when publishing a processed document. Evaluate the value as: `len(chunks)` — Count the items/characters in the supplied container/string. |
| L268 | Close the expression/container begun at L263; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L269 | Evaluate the branch condition: invert the truthiness of `published`. If truthy, enter L270; otherwise skip this indented block and continue after it. |
| L270 | Compute the return value: `ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_STALE, 'publication fenced out')` — Construct `ProcessOutcome` with the shown fields; its class/model initialization rules apply; inputs include `_kind_str(claim.kind)` — Call [_kind_str](#walk--kind-str) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L271 | Compute the return value: `ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_SUCCEEDED)` — Construct `ProcessOutcome` with the shown fields; its class/model initialization rules apply; inputs include `_kind_str(claim.kind)` — Call [_kind_str](#walk--kind-str) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L272 | Enter unconditional cleanup after the protected work, including on exception, return, break, or continue. |
| L273 | `heartbeat.stop()` — Invoke `heartbeat.stop` with the shown inputs and use its result; see the function overview for its role in this flow. The return value is not assigned here. |

<!-- END LINE WALKTHROUGH -->

### `DocumentProcessor._download_pdf(self, context) -> Path`

Requires bucket/file references, inspects storage, and wraps inspection/read errors as retryable storage failures. Uses reported size or context expected size and rejects a known oversized file before creating a temporary PDF. Repeatedly requests ranges, hashes/writes returned pieces, and enforces cumulative byte budget; a known short read fails. With a known size, each request extends to its final byte, not a fixed 1 MiB boundary; only unknown-size requests use `DOWNLOAD_CHUNK_BYTES`. The real storage adapter downloads the whole provider file before local slicing. Flushes/closes the handle; on any exception closes/unlinks. Checks SHA-256 **only when `context.expected_sha256` is truthy**, unlinking on mismatch; returns path for the caller to parse/delete. It does not fall back to `doc_content_sha256`, independently check completion counters, or compare actual length with the upload producer's alternate snapshot keys.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-documentprocessor--download-pdf"></a>

#### Line-by-line execution

[Current source: lines 275–338](../../../../Backend/app/workers/processor.py#L275-L338). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `context` | `Any`; required; positional or keyword | Loaded job facts copied before provider work; see the annotated type and field accesses below. |

**Declared result:** `Path`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 275 |     def _download_pdf(self, context: Any) -> Path:
 276 |         bucket_id = context.storage_bucket_id
 277 |         file_id = context.storage_file_id
 278 |         if bucket_id is None or file_id is None:
 279 |             raise JobError(ERROR_STORAGE_UNAVAILABLE, "job has no storage bucket/file reference")
 280 |         try:
 281 |             info = self.storage.inspect_storage_file(bucket_id=bucket_id, file_id=file_id)
 282 |         except Exception as exc:
 283 |             raise JobError(
 284 |                 ERROR_STORAGE_UNAVAILABLE, f"storage inspection failed: {safe_message(exc)}"
 285 |             ) from exc
 286 |         size = int(info.size) if info.size is not None else context.expected_size_bytes
 287 |         if size is not None and size > self.config.max_file_bytes:
 288 |             raise JobError(
 289 |                 ERROR_FILE_TOO_LARGE,
 290 |                 f"stored PDF is {size} bytes, exceeding the {self.config.max_file_bytes}-byte limit",
 291 |             )
 292 |         handle = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
 293 |         path = Path(handle.name)
 294 |         digest = hashlib.sha256()
 295 |         downloaded = 0
 296 |         expected = size
 297 |         try:
 298 |             while expected is None or downloaded < expected:
 299 |                 start = downloaded
 300 |                 end = expected - 1 if expected is not None else start + DOWNLOAD_CHUNK_BYTES - 1
 301 |                 try:
 302 |                     chunk_bytes, _headers = self.storage.open_storage_range(
 303 |                         bucket_id=bucket_id,
 304 |                         file_id=file_id,
 305 |                         range_header=f"bytes={start}-{end}",
 306 |                     )
 307 |                 except Exception as exc:
 308 |                     raise JobError(
 309 |                         ERROR_STORAGE_UNAVAILABLE,
 310 |                         f"storage read failed: {safe_message(exc)}",
 311 |                     ) from exc
 312 |                 if not chunk_bytes:
 313 |                     if expected is not None and downloaded < expected:
 314 |                         raise JobError(
 315 |                             ERROR_STORAGE_UNAVAILABLE,
 316 |                             f"storage returned a short read ({downloaded} of {expected} bytes)",
 317 |                         )
 318 |                     break
 319 |                 piece = chunk_bytes[: (expected - downloaded)] if expected is not None else chunk_bytes
 320 |                 downloaded += len(piece)
 321 |                 if downloaded > self.config.max_file_bytes:
 322 |                     raise JobError(
 323 |                         ERROR_FILE_TOO_LARGE,
 324 |                         f"downloaded PDF exceeds the {self.config.max_file_bytes}-byte limit",
 325 |                     )
 326 |                 digest.update(piece)
 327 |                 handle.write(piece)
 328 |             handle.flush()
 329 |         except BaseException:
 330 |             handle.close()
 331 |             path.unlink(missing_ok=True)
 332 |             raise
 333 |         handle.close()
 334 |         expected_sha = context.expected_sha256
 335 |         if expected_sha and digest.hexdigest() != str(expected_sha).lower():
 336 |             path.unlink(missing_ok=True)
 337 |             raise JobError(ERROR_FINGERPRINT_MISMATCH, "downloaded PDF does not match the expected fingerprint")
 338 |         return path
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L275 | Define `DocumentProcessor._download_pdf`; bind its arguments when called. The body executes only when invoked. |
| L276 | Evaluate the right-hand side, then bind/store it in `bucket_id`: the `storage_bucket_id` attribute of `context`. |
| L277 | Evaluate the right-hand side, then bind/store it in `file_id`: the `storage_file_id` attribute of `context`. |
| L278 | Evaluate the branch condition: evaluate `bucket_id is None or file_id is None` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L279; otherwise skip this indented block and continue after it. |
| L279 | Raise `JobError(ERROR_STORAGE_UNAVAILABLE, 'job has no storage bucket/file reference')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L280 | Enter the protected block; failures are matched against `Exception` in order. |
| L281 | Evaluate the right-hand side, then bind/store it in `info`: `self.storage.inspect_storage_file(bucket_id=bucket_id, file_id=file_id)` — Inspect private storage metadata for this bucket/file reference; provider failures propagate through the adapter. |
| L282 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L283 | Raise `JobError(ERROR_STORAGE_UNAVAILABLE, f'storage inspection failed: {safe_message(exc)}')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L284 | Call [safe_message](../jobs/errors.md#walk-safe-message) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L285 | Contribute the current `exc` value to the expression being assembled. |
| L286 | Evaluate the right-hand side, then bind/store it in `size`: check `info.size is not None`; when true use `int(info.size)` — Convert the input to an integer (using the optional numeric base), otherwise the `expected_size_bytes` attribute of `context` (only the selected branch is evaluated). |
| L287 | Evaluate the branch condition: evaluate `size is not None and size > self.config.max_file_bytes` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L288; otherwise skip this indented block and continue after it. |
| L288 | Raise `JobError(ERROR_FILE_TOO_LARGE, f'stored PDF is {size} bytes, exceeding the {self.config.max_file_bytes}-byte limit')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L289 | Supply positional argument 1 to `JobError`: the current `ERROR_FILE_TOO_LARGE` value. |
| L290 | Supply positional argument 2 to `JobError`: format a string by inserting `size`, `self.config.max_file_bytes` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L291 | Close the expression/container begun at L288; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L292 | Evaluate the right-hand side, then bind/store it in `handle`: `tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)` — Create a temporary disk file; delete=False leaves removal to explicit cleanup. |
| L293 | Evaluate the right-hand side, then bind/store it in `path`: `Path(handle.name)` — Construct a filesystem path value (in FastAPI annotations, Path instead declares path-parameter metadata). |
| L294 | Evaluate the right-hand side, then bind/store it in `digest`: `hashlib.sha256()` — Create a SHA-256 digest state, optionally seeded with the supplied bytes. |
| L295 | Evaluate the right-hand side, then bind/store it in `downloaded`: `0`. |
| L296 | Evaluate the right-hand side, then bind/store it in `expected`: the current `size` value. |
| L297 | Enter the protected block; failures are matched against `BaseException` in order. |
| L298 | Re-evaluate `expected is None or downloaded < expected` before every iteration; run the body while truthy and leave when false or when a break executes. |
| L299 | Evaluate the right-hand side, then bind/store it in `start`: the current `downloaded` value. |
| L300 | Evaluate the right-hand side, then bind/store it in `end`: check `expected is not None`; when true use subtract `expected` and `1`, following the parentheses/operator precedence shown in `expected - 1`, otherwise subtract `start + DOWNLOAD_CHUNK_BYTES` and `1`, following the parentheses/operator precedence shown in `start + DOWNLOAD_CHUNK_BYTES - 1` (only the selected branch is evaluated). |
| L301 | Enter the protected block; failures are matched against `Exception` in order. |
| L302 | Evaluate the right-hand side, then bind/store it in `(chunk_bytes, _headers)`: `self.storage.open_storage_range(bucket_id=bucket_id, file_id=file_id, range_header=f'bytes={start}-{end}')` — Read the selected private file range and its HTTP content headers through the storage adapter. |
| L303 | Supply `bucket_id` = `bucket_id`. Appwrite bucket identifier. Evaluate the value as: the current `bucket_id` value. |
| L304 | Supply `file_id` = `file_id`. Reserved Appwrite storage-object identifier. Evaluate the value as: the current `file_id` value. |
| L305 | Supply `range_header` = `f'bytes={start}-{end}'`. Optional HTTP byte-range selector; parsing determines full, partial, or unsatisfiable behavior. Evaluate the value as: format a string by inserting `start`, `end` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L306 | Close the expression/container begun at L302; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L307 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L308 | Raise `JobError(ERROR_STORAGE_UNAVAILABLE, f'storage read failed: {safe_message(exc)}')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L309 | Supply positional argument 1 to `JobError`: the current `ERROR_STORAGE_UNAVAILABLE` value. |
| L310 | Call [safe_message](../jobs/errors.md#walk-safe-message) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L311 | Contribute the current `exc` value to the expression being assembled. |
| L312 | Evaluate the branch condition: invert the truthiness of `chunk_bytes`. If truthy, enter L313; otherwise skip this indented block and continue after it. |
| L313 | Evaluate the branch condition: evaluate `expected is not None and downloaded < expected` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L314; otherwise skip this indented block and continue after it. |
| L314 | Raise `JobError(ERROR_STORAGE_UNAVAILABLE, f'storage returned a short read ({downloaded} of {expected} bytes)')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L315 | Supply positional argument 1 to `JobError`: the current `ERROR_STORAGE_UNAVAILABLE` value. |
| L316 | Supply positional argument 2 to `JobError`: format a string by inserting `downloaded`, `expected` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L317 | Close the expression/container begun at L314; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L318 | Exit the innermost loop immediately and continue after it; active cleanup still applies. |
| L319 | Evaluate the right-hand side, then bind/store it in `piece`: check `expected is not None`; when true use slice `chunk_bytes` from the beginning up to `expected - downloaded` (exclusive stop), otherwise the current `chunk_bytes` value (only the selected branch is evaluated). |
| L320 | Update `downloaded` in place using `len(piece)` and the Add operation; the previous target value participates in the calculation. |
| L321 | Evaluate the branch condition: compare whether `downloaded` is greater than `self.config.max_file_bytes`. If truthy, enter L322; otherwise skip this indented block and continue after it. |
| L322 | Raise `JobError(ERROR_FILE_TOO_LARGE, f'downloaded PDF exceeds the {self.config.max_file_bytes}-byte limit')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L323 | Supply positional argument 1 to `JobError`: the current `ERROR_FILE_TOO_LARGE` value. |
| L324 | Supply positional argument 2 to `JobError`: format a string by inserting `self.config.max_file_bytes` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L325 | Close the expression/container begun at L322; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L326 | `digest.update(piece)` — Feed the bytes into the running digest state without finalizing it. The return value is not assigned here. |
| L327 | `handle.write(piece)` — Write supplied bytes/text to the open file handle. The return value is not assigned here. |
| L328 | `handle.flush()` — Flush buffered file bytes to the underlying file handle; this is not a database commit. The return value is not assigned here. |
| L329 | Handle `BaseException`; only a matching error from the associated try enters this body. |
| L330 | `handle.close()` — Close the resource and release its associated handle. The return value is not assigned here. |
| L331 | `path.unlink(missing_ok=True)` — Remove the local file; missing_ok=True makes an already absent file harmless. The return value is not assigned here. |
| L332 | Re-raise the currently handled exception with its traceback; no replacement result is returned. |
| L333 | `handle.close()` — Close the resource and release its associated handle. The return value is not assigned here. |
| L334 | Evaluate the right-hand side, then bind/store it in `expected_sha`: the `expected_sha256` attribute of `context`. |
| L335 | Evaluate the branch condition: evaluate `expected_sha and digest.hexdigest() != str(expected_sha).lower()` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L336; otherwise skip this indented block and continue after it. |
| L336 | `path.unlink(missing_ok=True)` — Remove the local file; missing_ok=True makes an already absent file harmless. The return value is not assigned here. |
| L337 | Raise `JobError(ERROR_FINGERPRINT_MISMATCH, 'downloaded PDF does not match the expected fingerprint')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L338 | Compute the return value: the current `path` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `DocumentProcessor._embed(self, claim, heartbeat, chunks) -> list[list[float]] | ProcessOutcome`

Requires an embedder, extracts texts, clamps configured batch size to ≥1, and iterates serial batches. Checks heartbeat before each, calls provider, requires exactly one result per input, extends vectors, and writes guarded progress. Returns lease-lost on heartbeat/progress failure, otherwise all vectors. Vector dimension/finiteness validation belongs to the embedder; the attempt timeout is not checked inside this loop.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-documentprocessor--embed"></a>

#### Line-by-line execution

[Current source: lines 340–358](../../../../Backend/app/workers/processor.py#L340-L358). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `claim` | `JobClaim`; required; positional or keyword | Committed job/turn claim carrying the identity and fencing fields required by later operations. |
| `heartbeat` | `_Heartbeat`; required; positional or keyword | Lease-renewal helper whose lost event tells processing code to stop cooperatively. |
| `chunks` | `Sequence[Any]`; required; positional or keyword | PDF text chunks with the metadata required by this operation. |

**Declared result:** `list[list[float]] | ProcessOutcome`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 340 |     def _embed(
 341 |         self, claim: JobClaim, heartbeat: _Heartbeat, chunks: Sequence[Any]
 342 |     ) -> list[list[float]] | ProcessOutcome:
 343 |         if self.embedder is None:
 344 |             raise JobError(ERROR_UNEXPECTED, "embedding service is not configured")
 345 |         texts = [chunk.text for chunk in chunks]
 346 |         embeddings: list[list[float]] = []
 347 |         batch_size = max(1, self.config.embed_batch_size)
 348 |         for start in range(0, len(texts), batch_size):
 349 |             if heartbeat.lost.is_set():
 350 |                 return self._lease_lost(claim, heartbeat)
 351 |             batch = texts[start : start + batch_size]
 352 |             batch_embeddings = self.embedder.embed_texts(batch)
 353 |             if len(batch_embeddings) != len(batch):
 354 |                 raise JobError(ERROR_UNEXPECTED, "embedding provider returned a mismatched count")
 355 |             embeddings.extend(batch_embeddings)
 356 |             if not self._progress(claim, stage="embedding", current=len(embeddings), total=len(texts)):
 357 |                 return self._lease_lost(claim, heartbeat)
 358 |         return embeddings
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L340 | Define `DocumentProcessor._embed`; bind its arguments when called. The body executes only when invoked. |
| L341 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `claim` with annotation `JobClaim`. Committed job/turn claim carrying the identity and fencing fields required by later operations. Declare parameter `heartbeat` with annotation `_Heartbeat`. Lease-renewal helper whose lost event tells processing code to stop cooperatively. Declare parameter `chunks` with annotation `Sequence[Any]`. PDF text chunks with the metadata required by this operation. |
| L342 | Finish/continue the signature; the declared return annotation is `list[list[float]] \| ProcessOutcome`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L343 | Evaluate the branch condition: compare whether `self.embedder` is the same object as `None`. If truthy, enter L344; otherwise skip this indented block and continue after it. |
| L344 | Raise `JobError(ERROR_UNEXPECTED, 'embedding service is not configured')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L345 | Evaluate the right-hand side, then bind/store it in `texts`: iterate `chunks`, binding each item to `chunk`; produce `chunk.text` into a new list. |
| L346 | Evaluate the right-hand side, then bind/store it in `embeddings`: build a list containing no items. |
| L347 | Evaluate the right-hand side, then bind/store it in `batch_size`: `max(1, self.config.embed_batch_size)` — Choose the largest supplied value; nested min/max calls implement the stated bound. |
| L348 | Iterate `range(0, len(texts), batch_size)` (`range(0, len(texts), batch_size)` — Generate integer positions from the start up to, but excluding, the stop, using the supplied step; inputs include `len(texts)` — Count the items/characters in the supplied container/string), assigning each item to `start`. Execute the indented body once per item; an empty iterable skips it. |
| L349 | Evaluate the branch condition: `heartbeat.lost.is_set()` — Read whether the synchronization event has been signalled. If truthy, enter L350; otherwise skip this indented block and continue after it. |
| L350 | Compute the return value: `self._lease_lost(claim, heartbeat)` — Call [DocumentProcessor._lease_lost](#walk-documentprocessor--lease-lost) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L351 | Evaluate the right-hand side, then bind/store it in `batch`: slice `texts` from `start` up to `start + batch_size` (exclusive stop). |
| L352 | Evaluate the right-hand side, then bind/store it in `batch_embeddings`: `self.embedder.embed_texts(batch)` — Embed input texts in order using the selected provider/configuration; configured mock mode substitutes deterministic vectors. |
| L353 | Evaluate the branch condition: compare whether `len(batch_embeddings)` differs from `len(batch)`. If truthy, enter L354; otherwise skip this indented block and continue after it. |
| L354 | Raise `JobError(ERROR_UNEXPECTED, 'embedding provider returned a mismatched count')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L355 | `embeddings.extend(batch_embeddings)` — Append every item from the supplied iterable to the list in order. The return value is not assigned here. |
| L356 | Evaluate the branch condition: invert the truthiness of `self._progress(claim, stage='embedding', current=len(embeddings), total=len(texts))`. If truthy, enter L357; otherwise skip this indented block and continue after it. |
| L357 | Compute the return value: `self._lease_lost(claim, heartbeat)` — Call [DocumentProcessor._lease_lost](#walk-documentprocessor--lease-lost) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L358 | Compute the return value: the current `embeddings` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `DocumentProcessor._process_delete(self, claim, context) -> ProcessOutcome`

Starts heartbeat and builds insertion-ordered unique versions from snapshot `index_versions`, snapshot active version, live document active version, and context job version. With an index adapter, deletes each exact owned namespace and records progress, checking heartbeat before each version. Deletes storage when references exist, writes final progress, and calls fenced completion. Missing optional index adapter skips its work; missing storage references skip storage deletion. Returns success/stale/lease-lost or propagates provider errors to `process`; always stops heartbeat. It does not hard-delete SQL rows, enumerate all historical process jobs, or enforce an attempt-timeout check on this path.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-documentprocessor--process-delete"></a>

#### Line-by-line execution

[Current source: lines 361–415](../../../../Backend/app/workers/processor.py#L361-L415). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `claim` | `JobClaim`; required; positional or keyword | Committed job/turn claim carrying the identity and fencing fields required by later operations. |
| `context` | `Any`; required; positional or keyword | Loaded job facts copied before provider work; see the annotated type and field accesses below. |

**Declared result:** `ProcessOutcome`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 361 |     def _process_delete(self, claim: JobClaim, context: Any) -> ProcessOutcome:
 362 |         heartbeat = self._start_heartbeat(claim)
 363 |         try:
 364 |             snapshot = context.resource_snapshot or {}
 365 |             seen: list[str] = []
 366 |             for version in snapshot.get("index_versions") or []:
 367 |                 if str(version) not in seen:
 368 |                     seen.append(str(version))
 369 |             if snapshot.get("active_index_version"):
 370 |                 version = str(snapshot["active_index_version"])
 371 |                 if version not in seen:
 372 |                     seen.append(version)
 373 |             if context.doc_active_index_version is not None:
 374 |                 version = str(context.doc_active_index_version)
 375 |                 if version not in seen:
 376 |                     seen.append(version)
 377 |             if context.index_version is not None:
 378 |                 version = str(context.index_version)
 379 |                 if version not in seen:
 380 |                     seen.append(version)
 381 |             total = max(1, len(seen) + 1)
 382 |             if self.index_service is not None:
 383 |                 for position, version in enumerate(seen, start=1):
 384 |                     if heartbeat.lost.is_set():
 385 |                         return self._lease_lost(claim, heartbeat)
 386 |                     self.index_service.delete_index_version(
 387 |                         user_id=context.owner_user_id,
 388 |                         project_id=context.project_id,
 389 |                         document_id=context.target_document_id,
 390 |                         index_version=version,
 391 |                     )
 392 |                     if not self._progress(claim, stage="deleting", current=position, total=total):
 393 |                         return self._lease_lost(claim, heartbeat)
 394 |             bucket_id = context.storage_bucket_id
 395 |             file_id = context.storage_file_id
 396 |             if bucket_id is not None and file_id is not None:
 397 |                 try:
 398 |                     self.storage.delete_storage_file(bucket_id=bucket_id, file_id=file_id)
 399 |                 except Exception as exc:
 400 |                     raise JobError(
 401 |                         ERROR_STORAGE_UNAVAILABLE,
 402 |                         f"storage delete failed: {safe_message(exc)}",
 403 |                     ) from exc
 404 |             if not self._progress(claim, stage="deleting", current=total, total=total):
 405 |                 return self._lease_lost(claim, heartbeat)
 406 |             published = self.queue.complete_job(
 407 |                 job_id=claim.job_id,
 408 |                 lease_token=int(claim.lease_token),
 409 |                 worker_id=self.config.worker_id,
 410 |             )
 411 |             if not published:
 412 |                 return ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_STALE, "completion fenced out")
 413 |             return ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_SUCCEEDED)
 414 |         finally:
 415 |             heartbeat.stop()
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L361 | Define `DocumentProcessor._process_delete`; bind its arguments when called. The body executes only when invoked. |
| L362 | Evaluate the right-hand side, then bind/store it in `heartbeat`: `self._start_heartbeat(claim)` — Call [DocumentProcessor._start_heartbeat](#walk-documentprocessor--start-heartbeat) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L363 | Enter the protected block. The finally block runs regardless of return or failure. |
| L364 | Evaluate the right-hand side, then bind/store it in `snapshot`: evaluate `context.resource_snapshot or {}` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L365 | Evaluate the right-hand side, then bind/store it in `seen`: build a list containing no items. |
| L366 | Iterate `snapshot.get('index_versions') or []` (evaluate `snapshot.get('index_versions') or []` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool), assigning each item to `version`. Execute the indented body once per item; an empty iterable skips it. |
| L367 | Evaluate the branch condition: compare whether `str(version)` is absent from `seen`. If truthy, enter L368; otherwise skip this indented block and continue after it. |
| L368 | `seen.append(str(version))` — Append one object to the mutable list in place; inputs include `str(version)` — Convert the input to its string representation. The return value is not assigned here. |
| L369 | Evaluate the branch condition: `snapshot.get('active_index_version')` — Look up `'active_index_version'` in `snapshot`, using None when the key is absent (an existing null value is not replaced). If truthy, enter L370; otherwise skip this indented block and continue after it. |
| L370 | Evaluate the right-hand side, then bind/store it in `version`: `str(snapshot['active_index_version'])` — Convert the input to its string representation. |
| L371 | Evaluate the branch condition: compare whether `version` is absent from `seen`. If truthy, enter L372; otherwise skip this indented block and continue after it. |
| L372 | `seen.append(version)` — Append one object to the mutable list in place. The return value is not assigned here. |
| L373 | Evaluate the branch condition: compare whether `context.doc_active_index_version` is not the same object as `None`. If truthy, enter L374; otherwise skip this indented block and continue after it. |
| L374 | Evaluate the right-hand side, then bind/store it in `version`: `str(context.doc_active_index_version)` — Convert the input to its string representation. |
| L375 | Evaluate the branch condition: compare whether `version` is absent from `seen`. If truthy, enter L376; otherwise skip this indented block and continue after it. |
| L376 | `seen.append(version)` — Append one object to the mutable list in place. The return value is not assigned here. |
| L377 | Evaluate the branch condition: compare whether `context.index_version` is not the same object as `None`. If truthy, enter L378; otherwise skip this indented block and continue after it. |
| L378 | Evaluate the right-hand side, then bind/store it in `version`: `str(context.index_version)` — Convert the input to its string representation. |
| L379 | Evaluate the branch condition: compare whether `version` is absent from `seen`. If truthy, enter L380; otherwise skip this indented block and continue after it. |
| L380 | `seen.append(version)` — Append one object to the mutable list in place. The return value is not assigned here. |
| L381 | Evaluate the right-hand side, then bind/store it in `total`: `max(1, len(seen) + 1)` — Choose the largest supplied value; nested min/max calls implement the stated bound; inputs include add/concatenate `len(seen)` and `1`, following the parentheses/operator precedence shown in `len(seen) + 1`. |
| L382 | Evaluate the branch condition: compare whether `self.index_service` is not the same object as `None`. If truthy, enter L383; otherwise skip this indented block and continue after it. |
| L383 | Iterate `enumerate(seen, start=1)` (`enumerate(seen, start=1)` — Yield an index and each input item in order; the optional second argument sets the starting index), assigning each item to `(position, version)`. Execute the indented body once per item; an empty iterable skips it. |
| L384 | Evaluate the branch condition: `heartbeat.lost.is_set()` — Read whether the synchronization event has been signalled. If truthy, enter L385; otherwise skip this indented block and continue after it. |
| L385 | Compute the return value: `self._lease_lost(claim, heartbeat)` — Call [DocumentProcessor._lease_lost](#walk-documentprocessor--lease-lost) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L386 | `self.index_service.delete_index_version` with the arguments detailed below — Delete the exact user/project/document/version namespace from Chroma; this does not change the active SQL pointer. The return value is not assigned here. |
| L387 | Supply `user_id` = `context.owner_user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `owner_user_id` attribute of `context`. |
| L388 | Supply `project_id` = `context.project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the `project_id` attribute of `context`. |
| L389 | Supply `document_id` = `context.target_document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the `target_document_id` attribute of `context`. |
| L390 | Supply `index_version` = `version`. UUID of one document's vector-index namespace, separate from its active publication pointer. Evaluate the value as: the current `version` value. |
| L391 | Close the expression/container begun at L386; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L392 | Evaluate the branch condition: invert the truthiness of `self._progress(claim, stage='deleting', current=position, total=total)`. If truthy, enter L393; otherwise skip this indented block and continue after it. |
| L393 | Compute the return value: `self._lease_lost(claim, heartbeat)` — Call [DocumentProcessor._lease_lost](#walk-documentprocessor--lease-lost) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L394 | Evaluate the right-hand side, then bind/store it in `bucket_id`: the `storage_bucket_id` attribute of `context`. |
| L395 | Evaluate the right-hand side, then bind/store it in `file_id`: the `storage_file_id` attribute of `context`. |
| L396 | Evaluate the branch condition: evaluate `bucket_id is not None and file_id is not None` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L397; otherwise skip this indented block and continue after it. |
| L397 | Enter the protected block; failures are matched against `Exception` in order. |
| L398 | `self.storage.delete_storage_file(bucket_id=bucket_id, file_id=file_id)` — Delete the private object through the adapter's idempotent not-found handling. The return value is not assigned here. |
| L399 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L400 | Raise `JobError(ERROR_STORAGE_UNAVAILABLE, f'storage delete failed: {safe_message(exc)}')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L401 | Supply positional argument 1 to `JobError`: the current `ERROR_STORAGE_UNAVAILABLE` value. |
| L402 | Call [safe_message](../jobs/errors.md#walk-safe-message) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L403 | Contribute the current `exc` value to the expression being assembled. |
| L404 | Evaluate the branch condition: invert the truthiness of `self._progress(claim, stage='deleting', current=total, total=total)`. If truthy, enter L405; otherwise skip this indented block and continue after it. |
| L405 | Compute the return value: `self._lease_lost(claim, heartbeat)` — Call [DocumentProcessor._lease_lost](#walk-documentprocessor--lease-lost) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L406 | Evaluate the right-hand side, then bind/store it in `published`: `self.queue.complete_job(job_id=claim.job_id, lease_token=int(claim.lease_token), worker_id=self.config.worker_id)` — Attempt the queue's fenced completion/publication and return whether it succeeded or was already published. |
| L407 | Supply `job_id` = `claim.job_id`. Durable processing-job UUID. Evaluate the value as: the `job_id` attribute of `claim`. |
| L408 | Supply `lease_token` = `int(claim.lease_token)`. Monotonic claim token used to reject stale worker writes. Evaluate the value as: `int(claim.lease_token)` — Convert the input to an integer (using the optional numeric base). |
| L409 | Supply `worker_id` = `self.config.worker_id`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: the `worker_id` attribute of `self.config`. |
| L410 | Close the expression/container begun at L406; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L411 | Evaluate the branch condition: invert the truthiness of `published`. If truthy, enter L412; otherwise skip this indented block and continue after it. |
| L412 | Compute the return value: `ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_STALE, 'completion fenced out')` — Construct `ProcessOutcome` with the shown fields; its class/model initialization rules apply; inputs include `_kind_str(claim.kind)` — Call [_kind_str](#walk--kind-str) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L413 | Compute the return value: `ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_SUCCEEDED)` — Construct `ProcessOutcome` with the shown fields; its class/model initialization rules apply; inputs include `_kind_str(claim.kind)` — Call [_kind_str](#walk--kind-str) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L414 | Enter unconditional cleanup after the protected work, including on exception, return, break, or continue. |
| L415 | `heartbeat.stop()` — Invoke `heartbeat.stop` with the shown inputs and use its result; see the function overview for its role in this flow. The return value is not assigned here. |

<!-- END LINE WALKTHROUGH -->

### `DocumentProcessor._start_heartbeat(self, claim) -> _Heartbeat`

Builds heartbeat using claim ID/integer token, configured worker/lease/interval; starts and returns it.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-documentprocessor--start-heartbeat"></a>

#### Line-by-line execution

[Current source: lines 418–428](../../../../Backend/app/workers/processor.py#L418-L428). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `claim` | `JobClaim`; required; positional or keyword | Committed job/turn claim carrying the identity and fencing fields required by later operations. |

**Declared result:** `_Heartbeat`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 418 |     def _start_heartbeat(self, claim: JobClaim) -> _Heartbeat:
 419 |         heartbeat = _Heartbeat(
 420 |             self.queue,
 421 |             job_id=claim.job_id,
 422 |             lease_token=int(claim.lease_token),
 423 |             worker_id=self.config.worker_id,
 424 |             lease_seconds=self.config.lease_seconds,
 425 |             interval_seconds=self.config.heartbeat_interval_seconds,
 426 |         )
 427 |         heartbeat.start()
 428 |         return heartbeat
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L418 | Define `DocumentProcessor._start_heartbeat`; bind its arguments when called. The body executes only when invoked. |
| L419 | Evaluate the right-hand side, then bind/store it in `heartbeat`: `_Heartbeat` with the arguments detailed below — Invoke `_Heartbeat` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L420 | Supply positional argument 1 to `_Heartbeat`: the `queue` attribute of `self`. |
| L421 | Supply `job_id` = `claim.job_id`. Durable processing-job UUID. Evaluate the value as: the `job_id` attribute of `claim`. |
| L422 | Supply `lease_token` = `int(claim.lease_token)`. Monotonic claim token used to reject stale worker writes. Evaluate the value as: `int(claim.lease_token)` — Convert the input to an integer (using the optional numeric base). |
| L423 | Supply `worker_id` = `self.config.worker_id`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: the `worker_id` attribute of `self.config`. |
| L424 | Supply `lease_seconds` = `self.config.lease_seconds`. Lease duration in seconds; positive-duration validation is not implicit in this parameter. Evaluate the value as: the `lease_seconds` attribute of `self.config`. |
| L425 | Supply `interval_seconds` = `self.config.heartbeat_interval_seconds`.  Evaluate the value as: the `heartbeat_interval_seconds` attribute of `self.config`. |
| L426 | Close the expression/container begun at L419; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L427 | `heartbeat.start()` — Start `heartbeat` so its configured target runs on the background thread. The return value is not assigned here. |
| L428 | Compute the return value: the current `heartbeat` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `DocumentProcessor._progress(self, claim, *, stage, current, total) -> bool`

Forwards exact claim identity and progress values to the queue. Returns its truth value; exceptions log and return false so the caller stops publication work.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-documentprocessor--progress"></a>

#### Line-by-line execution

[Current source: lines 430–446](../../../../Backend/app/workers/processor.py#L430-L446). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `claim` | `JobClaim`; required; positional or keyword | Committed job/turn claim carrying the identity and fencing fields required by later operations. |
| `stage` | `str`; required; keyword-only | Public job stage to record, such as extracting, embedding, indexing, or publishing. |
| `current` | `int \| None`; required; keyword-only | Caller-supplied current; each read, transformation, and validation is traced below. |
| `total` | `int \| None`; required; keyword-only | Caller-supplied total; each read, transformation, and validation is traced below. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 430 |     def _progress(
 431 |         self, claim: JobClaim, *, stage: str, current: int | None, total: int | None
 432 |     ) -> bool:
 433 |         try:
 434 |             return bool(
 435 |                 self.queue.update_progress(
 436 |                     job_id=claim.job_id,
 437 |                     lease_token=int(claim.lease_token),
 438 |                     worker_id=self.config.worker_id,
 439 |                     stage=stage,
 440 |                     progress_current=current,
 441 |                     progress_total=total,
 442 |                 )
 443 |             )
 444 |         except Exception as exc:
 445 |             log.warning("progress write for job %s failed: %s", claim.job_id, safe_message(exc))
 446 |             return False
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L430 | Define `DocumentProcessor._progress`; bind its arguments when called. The body executes only when invoked. |
| L431 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `claim` with annotation `JobClaim`. Committed job/turn claim carrying the identity and fencing fields required by later operations. Declare parameter `stage` with annotation `str`. Public job stage to record, such as extracting, embedding, indexing, or publishing. Declare parameter `current` with annotation `int \| None`. Caller-supplied current; its uses and transformations are traced below. Declare parameter `total` with annotation `int \| None`. Caller-supplied total; its uses and transformations are traced below. |
| L432 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L433 | Enter the protected block; failures are matched against `Exception` in order. |
| L434 | Compute the return value: `bool` with the arguments detailed below — Convert the value's truthiness to True or False; inputs include `self.queue.update_progress` with the arguments detailed below — Apply the supplied progress fields through the queue's exact lease guard. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L435 | `self.queue.update_progress` with the arguments detailed below — Apply the supplied progress fields through the queue's exact lease guard. |
| L436 | Supply `job_id` = `claim.job_id`. Durable processing-job UUID. Evaluate the value as: the `job_id` attribute of `claim`. |
| L437 | Supply `lease_token` = `int(claim.lease_token)`. Monotonic claim token used to reject stale worker writes. Evaluate the value as: `int(claim.lease_token)` — Convert the input to an integer (using the optional numeric base). |
| L438 | Supply `worker_id` = `self.config.worker_id`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: the `worker_id` attribute of `self.config`. |
| L439 | Supply `stage` = `stage`. Public job stage to record, such as extracting, embedding, indexing, or publishing. Evaluate the value as: the current `stage` value. |
| L440 | Supply `progress_current` = `current`. Current completed-work counter; null means do not update it. Evaluate the value as: the current `current` value. |
| L441 | Supply `progress_total` = `total`. Total-work counter; null means do not update it. Evaluate the value as: the current `total` value. |
| L442 | Close the expression/container begun at L435; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L443 | Close the expression/container begun at L434; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L444 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L445 | `log.warning('progress write for job %s failed: %s', claim.job_id, safe_message(exc))` — Emit a warning log message, substituting the supplied formatting arguments; inputs include `safe_message(exc)` — Call [safe_message](../jobs/errors.md#walk-safe-message) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L446 | Compute the return value: `False`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `DocumentProcessor._lease_lost(self, claim, heartbeat) -> ProcessOutcome`

Logs guard failure if the heartbeat has not itself marked loss, then returns a lease-lost outcome. Does not change job state or set the heartbeat event.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-documentprocessor--lease-lost"></a>

#### Line-by-line execution

[Current source: lines 448–451](../../../../Backend/app/workers/processor.py#L448-L451). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `claim` | `JobClaim`; required; positional or keyword | Committed job/turn claim carrying the identity and fencing fields required by later operations. |
| `heartbeat` | `_Heartbeat`; required; positional or keyword | Lease-renewal helper whose lost event tells processing code to stop cooperatively. |

**Declared result:** `ProcessOutcome`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 448 |     def _lease_lost(self, claim: JobClaim, heartbeat: _Heartbeat) -> ProcessOutcome:
 449 |         if not heartbeat.lost.is_set():
 450 |             log.info("stopping job %s (lease/progress guard failed)", claim.job_id)
 451 |         return ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_LEASE_LOST, "lease no longer current")
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L448 | Define `DocumentProcessor._lease_lost`; bind its arguments when called. The body executes only when invoked. |
| L449 | Evaluate the branch condition: invert the truthiness of `heartbeat.lost.is_set()`. If truthy, enter L450; otherwise skip this indented block and continue after it. |
| L450 | `log.info('stopping job %s (lease/progress guard failed)', claim.job_id)` — Emit an informational log message with the supplied resource/status values. The return value is not assigned here. |
| L451 | Compute the return value: `ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_LEASE_LOST, 'lease no longer current')` — Construct `ProcessOutcome` with the shown fields; its class/model initialization rules apply; inputs include `_kind_str(claim.kind)` — Call [_kind_str](#walk--kind-str) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `DocumentProcessor._still_live(self, target_document_id) -> bool | None`

Uses optional queue `get_active_version`; returns its liveness flag, or null when unavailable/exceptional. Callers cancel only for explicit false; unknown proceeds to later database publication checks.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-documentprocessor--still-live"></a>

#### Line-by-line execution

[Current source: lines 453–462](../../../../Backend/app/workers/processor.py#L453-L462). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `target_document_id` | `UUID`; required; positional or keyword | Immutable target UUID retained even when the live document relationship disappears. |

**Declared result:** `bool | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 453 |     def _still_live(self, target_document_id: UUID) -> bool | None:
 454 |         """Re-check liveness cheaply; None = unknown (assume live)."""
 455 |         checker = getattr(self.queue, "get_active_version", None)
 456 |         if checker is None:
 457 |             return None
 458 |         try:
 459 |             live, _active = checker(target_document_id)
 460 |         except Exception:
 461 |             return None
 462 |         return bool(live)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L453 | Define `DocumentProcessor._still_live`; bind its arguments when called. The body executes only when invoked. |
| L454 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L455 | Evaluate the right-hand side, then bind/store it in `checker`: `getattr(self.queue, 'get_active_version', None)` — Read the named attribute, using the supplied default only if the attribute is absent. |
| L456 | Evaluate the branch condition: compare whether `checker` is the same object as `None`. If truthy, enter L457; otherwise skip this indented block and continue after it. |
| L457 | Compute the return value: None (no value). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L458 | Enter the protected block; failures are matched against `Exception` in order. |
| L459 | Evaluate the right-hand side, then bind/store it in `(live, _active)`: `checker(target_document_id)` — Invoke `checker` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L460 | Handle `Exception`; only a matching error from the associated try enters this body. |
| L461 | Compute the return value: None (no value). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L462 | Compute the return value: `bool(live)` — Convert the value's truthiness to True or False. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `DocumentProcessor._timed_out(self, started: float, claim) -> bool`

Compares monotonic elapsed time to configured budget, logs/returns true only when exceeded. Does not stop threads or persist failure itself; `claim` supplies log context.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-documentprocessor--timed-out"></a>

#### Line-by-line execution

[Current source: lines 464–468](../../../../Backend/app/workers/processor.py#L464-L468). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `started` | `float`; required; positional or keyword | Caller-supplied started; each read, transformation, and validation is traced below. |
| `claim` | `JobClaim`; required; positional or keyword | Committed job/turn claim carrying the identity and fencing fields required by later operations. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 464 |     def _timed_out(self, started: float, claim: JobClaim) -> bool:
 465 |         if time.monotonic() - started <= self.config.job_timeout_seconds:
 466 |             return False
 467 |         log.warning("job %s exceeded %ss budget", claim.job_id, self.config.job_timeout_seconds)
 468 |         return True
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L464 | Define `DocumentProcessor._timed_out`; bind its arguments when called. The body executes only when invoked. |
| L465 | Evaluate the branch condition: compare whether `time.monotonic() - started` is at most `self.config.job_timeout_seconds`. If truthy, enter L466; otherwise skip this indented block and continue after it. |
| L466 | Compute the return value: `False`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L467 | `log.warning('job %s exceeded %ss budget', claim.job_id, self.config.job_timeout_seconds)` — Emit a warning log message, substituting the supplied formatting arguments. The return value is not assigned here. |
| L468 | Compute the return value: `True`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `DocumentProcessor._cancel(self, claim, reason) -> ProcessOutcome`

Best-effort calls optional queue cancellation, swallowing errors, then returns cancelled regardless of whether the database update succeeded.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-documentprocessor--cancel"></a>

#### Line-by-line execution

[Current source: lines 470–477](../../../../Backend/app/workers/processor.py#L470-L477). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `claim` | `JobClaim`; required; positional or keyword | Committed job/turn claim carrying the identity and fencing fields required by later operations. |
| `reason` | `str`; required; positional or keyword | Human-readable cancellation/decision reason recorded or returned by this operation. |

**Declared result:** `ProcessOutcome`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 470 |     def _cancel(self, claim: JobClaim, reason: str) -> ProcessOutcome:
 471 |         cancel = getattr(self.queue, "cancel_job", None)
 472 |         if cancel is not None:
 473 |             try:
 474 |                 cancel(job_id=claim.job_id, reason=reason)
 475 |             except Exception:
 476 |                 pass
 477 |         return ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_CANCELLED, reason)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L470 | Define `DocumentProcessor._cancel`; bind its arguments when called. The body executes only when invoked. |
| L471 | Evaluate the right-hand side, then bind/store it in `cancel`: `getattr(self.queue, 'cancel_job', None)` — Read the named attribute, using the supplied default only if the attribute is absent. |
| L472 | Evaluate the branch condition: compare whether `cancel` is not the same object as `None`. If truthy, enter L473; otherwise skip this indented block and continue after it. |
| L473 | Enter the protected block; failures are matched against `Exception` in order. |
| L474 | `cancel(job_id=claim.job_id, reason=reason)` — Invoke `cancel` with the shown inputs and use its result; see the function overview for its role in this flow. The return value is not assigned here. |
| L475 | Handle `Exception`; only a matching error from the associated try enters this body. |
| L476 | Do nothing; this explicitly empty branch continues execution (here it can intentionally ignore a caught exception). |
| L477 | Compute the return value: `ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_CANCELLED, reason)` — Construct `ProcessOutcome` with the shown fields; its class/model initialization rules apply; inputs include `_kind_str(claim.kind)` — Call [_kind_str](#walk--kind-str) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `DocumentProcessor._fail(self, claim, error_code, error_message, retryable, context) -> ProcessOutcome`

Calls guarded queue failure with diagnostics truncated to 500 characters and configured backoff. Exceptions/false guard return stale. Otherwise estimates retry-wait versus failed using retryable and, when supplied, context attempt counts. With `context=None`, an exhausted retryable job can be reported as retry-wait even though the queue terminally failed it. Outcome detail retains the original message; this formatting does not redact credentials.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-documentprocessor--fail"></a>

#### Line-by-line execution

[Current source: lines 479–509](../../../../Backend/app/workers/processor.py#L479-L509). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `claim` | `JobClaim`; required; positional or keyword | Committed job/turn claim carrying the identity and fencing fields required by later operations. |
| `error_code` | `str`; required; positional or keyword | Machine-readable failure category stored or exposed by the operation. |
| `error_message` | `str`; required; positional or keyword | Human-readable failure detail; truncation alone does not redact sensitive content. |
| `retryable` | `bool`; required; positional or keyword | Whether the failure may be retried while the attempt budget remains. |
| `context` | `Any \| None`; required; positional or keyword | Loaded job facts copied before provider work; see the annotated type and field accesses below. |

**Declared result:** `ProcessOutcome`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 479 |     def _fail(
 480 |         self,
 481 |         claim: JobClaim,
 482 |         error_code: str,
 483 |         error_message: str,
 484 |         retryable: bool,
 485 |         context: Any | None,
 486 |     ) -> ProcessOutcome:
 487 |         try:
 488 |             applied = self.queue.fail_job(
 489 |                 job_id=claim.job_id,
 490 |                 lease_token=int(claim.lease_token),
 491 |                 worker_id=self.config.worker_id,
 492 |                 error_code=error_code,
 493 |                 error_message=error_message[:500],
 494 |                 retryable=retryable,
 495 |                 backoff_base_seconds=self.config.backoff_base_seconds,
 496 |                 backoff_cap_seconds=self.config.backoff_cap_seconds,
 497 |             )
 498 |         except Exception as exc:
 499 |             log.warning("fail write for job %s failed: %s", claim.job_id, safe_message(exc))
 500 |             return ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_STALE, "fail write failed")
 501 |         if not applied:
 502 |             return ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_STALE, "fail fenced out")
 503 |         will_retry = retryable
 504 |         if context is not None:
 505 |             will_retry = retryable and context.attempt_count < context.max_attempts
 506 |         status = OUTCOME_RETRY_WAIT if will_retry else OUTCOME_FAILED
 507 |         return ProcessOutcome(
 508 |             claim.job_id, _kind_str(claim.kind), status, f"{error_code}: {error_message}"
 509 |         )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L479 | Define `DocumentProcessor._fail`; bind its arguments when called. The body executes only when invoked. |
| L480 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L481 | Declare parameter `claim` with annotation `JobClaim`. Committed job/turn claim carrying the identity and fencing fields required by later operations. |
| L482 | Declare parameter `error_code` with annotation `str`. Machine-readable failure category stored or exposed by the operation. |
| L483 | Declare parameter `error_message` with annotation `str`. Human-readable failure detail; truncation alone does not redact sensitive content. |
| L484 | Declare parameter `retryable` with annotation `bool`. Whether the failure may be retried while the attempt budget remains. |
| L485 | Declare parameter `context` with annotation `Any \| None`. Loaded job facts copied before provider work; see the annotated type and field accesses below. |
| L486 | Finish/continue the signature; the declared return annotation is `ProcessOutcome`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L487 | Enter the protected block; failures are matched against `Exception` in order. |
| L488 | Evaluate the right-hand side, then bind/store it in `applied`: `self.queue.fail_job` with the arguments detailed below — Persist guarded diagnostics and select retry-wait versus terminal failure using the remaining attempt budget. |
| L489 | Supply `job_id` = `claim.job_id`. Durable processing-job UUID. Evaluate the value as: the `job_id` attribute of `claim`. |
| L490 | Supply `lease_token` = `int(claim.lease_token)`. Monotonic claim token used to reject stale worker writes. Evaluate the value as: `int(claim.lease_token)` — Convert the input to an integer (using the optional numeric base). |
| L491 | Supply `worker_id` = `self.config.worker_id`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: the `worker_id` attribute of `self.config`. |
| L492 | Supply `error_code` = `error_code`. Machine-readable failure category stored or exposed by the operation. Evaluate the value as: the current `error_code` value. |
| L493 | Supply `error_message` = `error_message[:500]`. Human-readable failure detail; truncation alone does not redact sensitive content. Evaluate the value as: slice `error_message` from the beginning up to `500` (exclusive stop). |
| L494 | Supply `retryable` = `retryable`. Whether the failure may be retried while the attempt budget remains. Evaluate the value as: the current `retryable` value. |
| L495 | Supply `backoff_base_seconds` = `self.config.backoff_base_seconds`. Base retry delay, doubled with successive attempts before capping/jitter. Evaluate the value as: the `backoff_base_seconds` attribute of `self.config`. |
| L496 | Supply `backoff_cap_seconds` = `self.config.backoff_cap_seconds`. Maximum retry-delay bound passed to the backoff calculation. Evaluate the value as: the `backoff_cap_seconds` attribute of `self.config`. |
| L497 | Close the expression/container begun at L488; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L498 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L499 | `log.warning('fail write for job %s failed: %s', claim.job_id, safe_message(exc))` — Emit a warning log message, substituting the supplied formatting arguments; inputs include `safe_message(exc)` — Call [safe_message](../jobs/errors.md#walk-safe-message) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L500 | Compute the return value: `ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_STALE, 'fail write failed')` — Construct `ProcessOutcome` with the shown fields; its class/model initialization rules apply; inputs include `_kind_str(claim.kind)` — Call [_kind_str](#walk--kind-str) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L501 | Evaluate the branch condition: invert the truthiness of `applied`. If truthy, enter L502; otherwise skip this indented block and continue after it. |
| L502 | Compute the return value: `ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_STALE, 'fail fenced out')` — Construct `ProcessOutcome` with the shown fields; its class/model initialization rules apply; inputs include `_kind_str(claim.kind)` — Call [_kind_str](#walk--kind-str) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L503 | Evaluate the right-hand side, then bind/store it in `will_retry`: the current `retryable` value. |
| L504 | Evaluate the branch condition: compare whether `context` is not the same object as `None`. If truthy, enter L505; otherwise skip this indented block and continue after it. |
| L505 | Evaluate the right-hand side, then bind/store it in `will_retry`: evaluate `retryable and context.attempt_count < context.max_attempts` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. |
| L506 | Evaluate the right-hand side, then bind/store it in `status`: check `will_retry`; when true use the current `OUTCOME_RETRY_WAIT` value, otherwise the current `OUTCOME_FAILED` value (only the selected branch is evaluated). |
| L507 | Compute the return value: `ProcessOutcome(claim.job_id, _kind_str(claim.kind), status, f'{error_code}: {error_message}')` — Construct `ProcessOutcome` with the shown fields; its class/model initialization rules apply; inputs include `_kind_str(claim.kind)` — Call [_kind_str](#walk--kind-str) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L508 | Call [_kind_str](#walk--kind-str) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L509 | Close the expression/container begun at L507; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->
