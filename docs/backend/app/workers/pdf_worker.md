# `app/workers/pdf_worker.py`

[Source](../../../../Backend/app/workers/pdf_worker.py) · [Backend index](../../README.md)

Standalone worker entry point: from `Backend/`, run `python -m app.workers.pdf_worker`. `--once` reconciles once and processes one claim batch. The long-running mode processes batches until signalled to stop.

## Configuration

`WorkerConfig` is a mutable dataclass. Defaults: generated worker ID, poll 2s, concurrency 2, lease 120s, 25 MiB/200 pages, attempt timeout 3600s, backoff 5–3600s, upload TTL/sweep grace 86,400s, reconciliation batch 50. `DOCUMIND_WORKER_` environment suffixes map to `ID`, `POLL_INTERVAL_SECONDS`, `CONCURRENCY`, `LEASE_SECONDS`, `MAX_FILE_BYTES`, `MAX_PAGES`, `JOB_TIMEOUT_SECONDS`, `BACKOFF_BASE_SECONDS`, `BACKOFF_CAP_SECONDS`, `AWAITING_UPLOAD_TTL_SECONDS`, `SWEEP_GRACE_SECONDS`. Batch size has no environment lookup here.

## Functions

### `_env_int(env: dict[str, str], name: str, default: int) -> int`

Reads/strips a variable, returns default for blank input, otherwise parses `int`. A `ValueError` logs the variable/raw value/default and returns default. This parser does not impose positivity.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--env-int"></a>

#### Line-by-line execution

[Current source: lines 121–129](../../../../Backend/app/workers/pdf_worker.py#L121-L129). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `env` | `dict[str, str]`; required; positional or keyword | Optional environment mapping; null normally selects process environment. |
| `name` | `str`; required; positional or keyword | Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. |
| `default` | `int`; required; positional or keyword | Fallback returned when the selected input is absent or cannot be parsed where explicitly handled. |

**Declared result:** `int`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 121 | def _env_int(env: dict[str, str], name: str, default: int) -> int:
 122 |     raw = env.get(name, "").strip()
 123 |     if not raw:
 124 |         return default
 125 |     try:
 126 |         return int(raw)
 127 |     except ValueError:
 128 |         log.warning("invalid integer for %s=%r; using default %s", name, raw, default)
 129 |         return default
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L121 | Define `_env_int`; bind its arguments when called. The body executes only when invoked. |
| L122 | Evaluate the right-hand side, then bind/store it in `raw`: `env.get(name, '').strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed; first obtain the receiver: `env.get(name, '')` — Look up `name` in `env`, using `''` when the key is absent (an existing null value is not replaced). |
| L123 | Evaluate the branch condition: invert the truthiness of `raw`. If truthy, enter L124; otherwise skip this indented block and continue after it. |
| L124 | Compute the return value: the current `default` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L125 | Enter the protected block; failures are matched against `ValueError` in order. |
| L126 | Compute the return value: `int(raw)` — Convert the input to an integer (using the optional numeric base). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L127 | Handle `ValueError`; only a matching error from the associated try enters this body. |
| L128 | `log.warning('invalid integer for %s=%r; using default %s', name, raw, default)` — Emit a warning log message, substituting the supplied formatting arguments. The return value is not assigned here. |
| L129 | Compute the return value: the current `default` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_default_worker_id() -> str`

Returns `worker-{hostname}-{pid}-{six UUID hex characters}` using hostname, current PID, and fresh UUID; no external registration occurs.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--default-worker-id"></a>

#### Line-by-line execution

[Current source: lines 132–133](../../../../Backend/app/workers/pdf_worker.py#L132-L133). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 132 | def _default_worker_id() -> str:
 133 |     return f"worker-{socket.gethostname()}-{os.getpid()}-{uuid.uuid4().hex[:6]}"
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L132 | Define `_default_worker_id`; bind its arguments when called. The body executes only when invoked. |
| L133 | Compute the return value: format a string by inserting `socket.gethostname()`, `os.getpid()`, `uuid.uuid4().hex[:6]` into the literal text; !r uses repr, and this formatting does not escape or redact values. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `WorkerConfig.__post_init__(self) -> None`

Rejects byte/page limits below public 25 MiB/200-page budgets. Clamps concurrency to ≥1, poll interval to ≥0, and lease to ≥5 seconds; other values are not clamped. Larger worker PDF limits do not change API/bucket limits.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-workerconfig---post-init--"></a>

#### Line-by-line execution

[Current source: lines 153–158](../../../../Backend/app/workers/pdf_worker.py#L153-L158). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 153 |     def __post_init__(self) -> None:
 154 |         if self.max_file_bytes < DEFAULT_MAX_PDF_BYTES or self.max_pages < DEFAULT_MAX_PDF_PAGES:
 155 |             raise ValueError("Worker PDF limits must cover the API's 25 MiB / 200-page budget.")
 156 |         self.concurrency = max(1, self.concurrency)
 157 |         self.poll_interval_seconds = max(0, self.poll_interval_seconds)
 158 |         self.lease_seconds = max(5, self.lease_seconds)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L153 | Define `WorkerConfig.__post_init__`; bind its arguments when called. The body executes only when invoked. |
| L154 | Evaluate the branch condition: evaluate `self.max_file_bytes < DEFAULT_MAX_PDF_BYTES or self.max_pages < DEFAULT_MAX_PDF_PAGES` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L155; otherwise skip this indented block and continue after it. |
| L155 | Raise `ValueError("Worker PDF limits must cover the API's 25 MiB / 200-page budget.")`; stop the normal path and transfer control to the nearest matching exception handler. |
| L156 | Evaluate the right-hand side, then bind/store it in `self.concurrency`: `max(1, self.concurrency)` — Choose the largest supplied value; nested min/max calls implement the stated bound. |
| L157 | Evaluate the right-hand side, then bind/store it in `self.poll_interval_seconds`: `max(0, self.poll_interval_seconds)` — Choose the largest supplied value; nested min/max calls implement the stated bound. |
| L158 | Evaluate the right-hand side, then bind/store it in `self.lease_seconds`: `max(5, self.lease_seconds)` — Choose the largest supplied value; nested min/max calls implement the stated bound. |

<!-- END LINE WALKTHROUGH -->

### `WorkerConfig.from_env(cls, env=None, **overrides) -> WorkerConfig`

Reads supplied mapping or process environment, resolves worker ID and integer defaults, applies only non-null keyword overrides, then constructs the dataclass so post-init validation runs. Unknown override names fail constructor argument validation. Returns the resulting config.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-workerconfig-from-env"></a>

#### Line-by-line execution

[Current source: lines 160–181](../../../../Backend/app/workers/pdf_worker.py#L160-L181). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `cls` | not annotated; implicitly supplied/collected; positional or keyword | The class being constructed or validated; the classmethod descriptor supplies it. |
| `env` | `dict[str, str] \| None`; default `None`; positional or keyword | Optional environment mapping; null normally selects process environment. |
| `overrides` | `Any`; implicitly supplied/collected; ** keyword extras | Caller-supplied overrides; each read, transformation, and validation is traced below. |

**Declared result:** `'WorkerConfig'`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 160 |     @classmethod
 161 |     def from_env(cls, env: dict[str, str] | None = None, **overrides: Any) -> "WorkerConfig":
 162 |         source = env if env is not None else os.environ
 163 |         values: dict[str, Any] = dict(
 164 |             worker_id=source.get("DOCUMIND_WORKER_ID", "").strip() or _default_worker_id(),
 165 |             poll_interval_seconds=_env_int(source, "DOCUMIND_WORKER_POLL_INTERVAL_SECONDS", 2),
 166 |             concurrency=_env_int(source, "DOCUMIND_WORKER_CONCURRENCY", 2),
 167 |             lease_seconds=_env_int(source, "DOCUMIND_WORKER_LEASE_SECONDS", 120),
 168 |             max_file_bytes=_env_int(source, "DOCUMIND_WORKER_MAX_FILE_BYTES", DEFAULT_MAX_PDF_BYTES),
 169 |             max_pages=_env_int(source, "DOCUMIND_WORKER_MAX_PAGES", DEFAULT_MAX_PDF_PAGES),
 170 |             job_timeout_seconds=_env_int(source, "DOCUMIND_WORKER_JOB_TIMEOUT_SECONDS", 3600),
 171 |             backoff_base_seconds=_env_int(source, "DOCUMIND_WORKER_BACKOFF_BASE_SECONDS", 5),
 172 |             backoff_cap_seconds=_env_int(source, "DOCUMIND_WORKER_BACKOFF_CAP_SECONDS", 3600),
 173 |             awaiting_upload_ttl_seconds=_env_int(
 174 |                 source, "DOCUMIND_WORKER_AWAITING_UPLOAD_TTL_SECONDS", DEFAULT_AWAITING_UPLOAD_TTL_SECONDS
 175 |             ),
 176 |             sweep_grace_seconds=_env_int(
 177 |                 source, "DOCUMIND_WORKER_SWEEP_GRACE_SECONDS", DEFAULT_SWEEP_GRACE_SECONDS
 178 |             ),
 179 |         )
 180 |         values.update({k: v for k, v in overrides.items() if v is not None})
 181 |         return cls(**values)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L160 | Bind the method to the class so Python supplies cls; decorators are applied bottom-up when the function is defined. |
| L161 | Define `WorkerConfig.from_env`; bind its arguments when called. The body executes only when invoked. |
| L162 | Evaluate the right-hand side, then bind/store it in `source`: check `env is not None`; when true use the current `env` value, otherwise the `environ` attribute of `os` (only the selected branch is evaluated). |
| L163 | Evaluate the right-hand side, then bind/store it in `values`: `dict` with the arguments detailed below — Build a mapping from the supplied items/keywords; copying a mapping is shallow. |
| L164 | Supply `worker_id` = `source.get('DOCUMIND_WORKER_ID', '').strip() or _default_worker_id()`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: evaluate `source.get('DOCUMIND_WORKER_ID', '').strip() or _default_worker_id()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L165 | Supply `poll_interval_seconds` = `_env_int(source, 'DOCUMIND_WORKER_POLL_INTERVAL_SECONDS', 2)`.  Evaluate the value as: `_env_int(source, 'DOCUMIND_WORKER_POLL_INTERVAL_SECONDS', 2)` — Call [_env_int](#walk--env-int) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L166 | Supply `concurrency` = `_env_int(source, 'DOCUMIND_WORKER_CONCURRENCY', 2)`.  Evaluate the value as: `_env_int(source, 'DOCUMIND_WORKER_CONCURRENCY', 2)` — Call [_env_int](#walk--env-int) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L167 | Supply `lease_seconds` = `_env_int(source, 'DOCUMIND_WORKER_LEASE_SECONDS', 120)`. Lease duration in seconds; positive-duration validation is not implicit in this parameter. Evaluate the value as: `_env_int(source, 'DOCUMIND_WORKER_LEASE_SECONDS', 120)` — Call [_env_int](#walk--env-int) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L168 | Supply `max_file_bytes` = `_env_int(source, 'DOCUMIND_WORKER_MAX_FILE_BYTES', DEFAULT_MAX_PDF_BYTES)`. Maximum PDF byte count accepted by this component. Evaluate the value as: `_env_int(source, 'DOCUMIND_WORKER_MAX_FILE_BYTES', DEFAULT_MAX_PDF_BYTES)` — Call [_env_int](#walk--env-int) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L169 | Supply `max_pages` = `_env_int(source, 'DOCUMIND_WORKER_MAX_PAGES', DEFAULT_MAX_PDF_PAGES)`. Maximum PDF pages accepted by extraction. Evaluate the value as: `_env_int(source, 'DOCUMIND_WORKER_MAX_PAGES', DEFAULT_MAX_PDF_PAGES)` — Call [_env_int](#walk--env-int) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L170 | Supply `job_timeout_seconds` = `_env_int(source, 'DOCUMIND_WORKER_JOB_TIMEOUT_SECONDS', 3600)`.  Evaluate the value as: `_env_int(source, 'DOCUMIND_WORKER_JOB_TIMEOUT_SECONDS', 3600)` — Call [_env_int](#walk--env-int) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L171 | Supply `backoff_base_seconds` = `_env_int(source, 'DOCUMIND_WORKER_BACKOFF_BASE_SECONDS', 5)`. Base retry delay, doubled with successive attempts before capping/jitter. Evaluate the value as: `_env_int(source, 'DOCUMIND_WORKER_BACKOFF_BASE_SECONDS', 5)` — Call [_env_int](#walk--env-int) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L172 | Supply `backoff_cap_seconds` = `_env_int(source, 'DOCUMIND_WORKER_BACKOFF_CAP_SECONDS', 3600)`. Maximum retry-delay bound passed to the backoff calculation. Evaluate the value as: `_env_int(source, 'DOCUMIND_WORKER_BACKOFF_CAP_SECONDS', 3600)` — Call [_env_int](#walk--env-int) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L173 | Supply `awaiting_upload_ttl_seconds` = `_env_int(source, 'DOCUMIND_WORKER_AWAITING_UPLOAD_TTL_SECONDS', DEFAULT_AWAITING_UPLOAD_TTL_SECONDS)`.  Evaluate the value as: `_env_int(source, 'DOCUMIND_WORKER_AWAITING_UPLOAD_TTL_SECONDS', DEFAULT_AWAITING_UPLOAD_TTL_SECONDS)` — Call [_env_int](#walk--env-int) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L174 | Supply positional argument 1 to `_env_int`: the current `source` value. |
| L175 | Close the expression/container begun at L173; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L176 | Supply `sweep_grace_seconds` = `_env_int(source, 'DOCUMIND_WORKER_SWEEP_GRACE_SECONDS', DEFAULT_SWEEP_GRACE_SECONDS)`.  Evaluate the value as: `_env_int(source, 'DOCUMIND_WORKER_SWEEP_GRACE_SECONDS', DEFAULT_SWEEP_GRACE_SECONDS)` — Call [_env_int](#walk--env-int) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L177 | Supply positional argument 1 to `_env_int`: the current `source` value. |
| L178 | Close the expression/container begun at L176; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L179 | Close the expression/container begun at L163; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L180 | Copy only non-null explicit overrides over environment-derived settings. False and zero are retained because the filter checks identity with None, not truthiness. |
| L181 | Compute the return value: `cls(**values)` — Construct `cls` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `WorkerConfig.processor_config(self) -> ProcessorConfig`

Copies worker/lease/PDF/timeout/backoff settings into the frozen per-job config. Embedding batch size retains `ProcessorConfig`'s default 16; poll/concurrency/reconciliation options remain worker-level.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-workerconfig-processor-config"></a>

#### Line-by-line execution

[Current source: lines 183–192](../../../../Backend/app/workers/pdf_worker.py#L183-L192). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |

**Declared result:** `ProcessorConfig`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 183 |     def processor_config(self) -> ProcessorConfig:
 184 |         return ProcessorConfig(
 185 |             worker_id=self.worker_id,
 186 |             lease_seconds=self.lease_seconds,
 187 |             max_file_bytes=self.max_file_bytes,
 188 |             max_pages=self.max_pages,
 189 |             job_timeout_seconds=self.job_timeout_seconds,
 190 |             backoff_base_seconds=self.backoff_base_seconds,
 191 |             backoff_cap_seconds=self.backoff_cap_seconds,
 192 |         )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L183 | Define `WorkerConfig.processor_config`; bind its arguments when called. The body executes only when invoked. |
| L184 | Compute the return value: `ProcessorConfig` with the arguments detailed below — Construct `ProcessorConfig` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L185 | Supply `worker_id` = `self.worker_id`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: the `worker_id` attribute of `self`. |
| L186 | Supply `lease_seconds` = `self.lease_seconds`. Lease duration in seconds; positive-duration validation is not implicit in this parameter. Evaluate the value as: the `lease_seconds` attribute of `self`. |
| L187 | Supply `max_file_bytes` = `self.max_file_bytes`. Maximum PDF byte count accepted by this component. Evaluate the value as: the `max_file_bytes` attribute of `self`. |
| L188 | Supply `max_pages` = `self.max_pages`. Maximum PDF pages accepted by extraction. Evaluate the value as: the `max_pages` attribute of `self`. |
| L189 | Supply `job_timeout_seconds` = `self.job_timeout_seconds`.  Evaluate the value as: the `job_timeout_seconds` attribute of `self`. |
| L190 | Supply `backoff_base_seconds` = `self.backoff_base_seconds`. Base retry delay, doubled with successive attempts before capping/jitter. Evaluate the value as: the `backoff_base_seconds` attribute of `self`. |
| L191 | Supply `backoff_cap_seconds` = `self.backoff_cap_seconds`. Maximum retry-delay bound passed to the backoff calculation. Evaluate the value as: the `backoff_cap_seconds` attribute of `self`. |
| L192 | Close the expression/container begun at L184; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `build_storage_adapter() -> StoragePort`

Lazily imports/calls `get_storage_adapter`, returning the configured Appwrite implementation. Import failure becomes `RuntimeError`; current runtime error text still refers to the historical adapter handoff. Missing environment settings propagate from the real factory. This function is already wired, despite old header claims that integration was pending.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-build-storage-adapter"></a>

#### Line-by-line execution

[Current source: lines 195–207](../../../../Backend/app/workers/pdf_worker.py#L195-L207). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `StoragePort`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 195 | def build_storage_adapter() -> StoragePort:
 196 |     """Lazily load the configured Appwrite storage adapter."""
 197 |     try:
 198 |         from app.services.storage import get_storage_adapter  # type: ignore[import-not-found]
 199 |     except ImportError as exc:
 200 |         raise RuntimeError(
 201 |             "A3 storage adapter (app.services.storage) "
 202 |             "is not available; the worker cannot process uploads until "
 203 |             "it lands (see docs/v2-contracts.md section 6)."
 204 |         ) from exc
 205 |     # Resolves endpoint/project/api_key/bucket from the environment
 206 |     # (raises RuntimeError if unconfigured — fail fast, as before).
 207 |     return get_storage_adapter()  # type: ignore[return-value]
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L195 | Define `build_storage_adapter`; bind its arguments when called. The body executes only when invoked. |
| L196 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L197 | Enter the protected block; failures are matched against `ImportError` in order. |
| L198 | Import `get_storage_adapter` from `app.services.storage`; inside a function this import is deferred until this path is reached. |
| L199 | Handle `ImportError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L200 | Raise `RuntimeError('A3 storage adapter (app.services.storage) is not available; the worker cannot process uploads until it lands (see docs/v2-contracts.md section 6).')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L201 | Supply positional argument 1 to `RuntimeError`: `'A3 storage adapter (app.services.storage) is not available; the worker cannot process uploads until it lands (see docs/v2-contracts.md section 6).'`. |
| L202 | Supply positional argument 1 to `RuntimeError`: `'A3 storage adapter (app.services.storage) is not available; the worker cannot process uploads until it lands (see docs/v2-contracts.md section 6).'`. |
| L203 | Supply positional argument 1 to `RuntimeError`: `'A3 storage adapter (app.services.storage) is not available; the worker cannot process uploads until it lands (see docs/v2-contracts.md section 6).'`. |
| L204 | Contribute the current `exc` value to the expression being assembled. |
| L205 | Comment only: Resolves endpoint/project/api_key/bucket from the environment. It does not execute; the neighboring code determines behavior. |
| L206 | Comment only: (raises RuntimeError if unconfigured — fail fast, as before).. It does not execute; the neighboring code determines behavior. |
| L207 | Compute the return value: `get_storage_adapter()` — Call [get_storage_adapter](../services/storage.md#walk-get-storage-adapter) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `build_default_dependencies(config: WorkerConfig) -> tuple[JobQueueStore, StoragePort, EmbedderPort, IndexPort]`

Reads embedding configuration, requires a nonblank Jina key when Jina is selected (even with mock mode), lazily creates a worker session factory/queue store, resolves storage, logs explicit mock mode, and constructs embedding/index services. Returns four collaborators; the `config` parameter is currently unused. Most provider connectivity is exercised when operations run, not proved by construction. HF key remains optional in its embedding service.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-build-default-dependencies"></a>

#### Line-by-line execution

[Current source: lines 210–232](../../../../Backend/app/workers/pdf_worker.py#L210-L232). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `config` | `WorkerConfig`; required; positional or keyword | Configuration object consumed by the field accesses below. |

**Declared result:** `tuple[JobQueueStore, StoragePort, EmbedderPort, IndexPort]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 210 | def build_default_dependencies(
 211 |     config: WorkerConfig,
 212 | ) -> tuple[JobQueueStore, StoragePort, EmbedderPort, IndexPort]:
 213 |     """Production wiring: PG queue, private storage, embeddings, Chroma."""
 214 |     embedding_config = EmbeddingConfig.from_env()
 215 |     if embedding_config.provider == PROVIDER_JINA and not (
 216 |         os.environ.get("JINA_API_KEY") or ""
 217 |     ).strip():
 218 |         raise RuntimeError(
 219 |             "JINA_API_KEY is required when DOCUMIND_EMBEDDING_PROVIDER=jina"
 220 |         )
 221 |     from app.db.session import make_worker_session_factory
 222 | 
 223 |     store = JobQueueStore(make_worker_session_factory())
 224 |     storage = build_storage_adapter()
 225 |     if embedding_config.allow_mock:
 226 |         log.warning(
 227 |             "DOCUMIND_ALLOW_MOCK_EMBEDDINGS is enabled: documents will be indexed "
 228 |             "with deterministic mock vectors (test/development only).",
 229 |         )
 230 |     embedder = EmbeddingService(embedding_config)
 231 |     index_service = IndexService()
 232 |     return store, storage, embedder, index_service
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L210 | Define `build_default_dependencies`; bind its arguments when called. The body executes only when invoked. |
| L211 | Declare parameter `config` with annotation `WorkerConfig`. Configuration object consumed by the field accesses below. |
| L212 | Finish/continue the signature; the declared return annotation is `tuple[JobQueueStore, StoragePort, EmbedderPort, IndexPort]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L213 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L214 | Evaluate the right-hand side, then bind/store it in `embedding_config`: `EmbeddingConfig.from_env()` — Invoke `EmbeddingConfig.from_env` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L215 | Evaluate the branch condition: evaluate `embedding_config.provider == PROVIDER_JINA and (not (os.environ.get('JINA_API_KEY') or '').strip())` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L218; otherwise skip this indented block and continue after it. |
| L216 | `os.environ.get('JINA_API_KEY')` — Read a process environment value without changing it, using the supplied fallback if absent. |
| L217 | Continue the operation begun at L215: Evaluate the branch condition: evaluate `embedding_config.provider == PROVIDER_JINA and (not (os.environ.get('JINA_API_KEY') or '').strip())` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L218; otherwise skip this indented block and continue after it. |
| L218 | Raise `RuntimeError('JINA_API_KEY is required when DOCUMIND_EMBEDDING_PROVIDER=jina')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L219 | Supply positional argument 1 to `RuntimeError`: `'JINA_API_KEY is required when DOCUMIND_EMBEDDING_PROVIDER=jina'`. |
| L220 | Close the expression/container begun at L218; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L221 | Import `make_worker_session_factory` from `app.db.session`; inside a function this import is deferred until this path is reached. |
| L223 | Evaluate the right-hand side, then bind/store it in `store`: `JobQueueStore(make_worker_session_factory())` — Construct `JobQueueStore` with the shown fields; its class/model initialization rules apply; inputs include `make_worker_session_factory()` — Call [make_worker_session_factory](../db/session.md#walk-make-worker-session-factory) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L224 | Evaluate the right-hand side, then bind/store it in `storage`: `build_storage_adapter()` — Call [build_storage_adapter](#walk-build-storage-adapter) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L225 | Evaluate the branch condition: the `allow_mock` attribute of `embedding_config`. If truthy, enter L226; otherwise skip this indented block and continue after it. |
| L226 | `log.warning('DOCUMIND_ALLOW_MOCK_EMBEDDINGS is enabled: documents will be indexed with deterministic mock vectors (test/development only).')` — Emit a warning log message, substituting the supplied formatting arguments. The return value is not assigned here. |
| L227 | Supply positional argument 1 to `log.warning`: `'DOCUMIND_ALLOW_MOCK_EMBEDDINGS is enabled: documents will be indexed with deterministic mock vectors (test/development only).'`. |
| L228 | Supply positional argument 1 to `log.warning`: `'DOCUMIND_ALLOW_MOCK_EMBEDDINGS is enabled: documents will be indexed with deterministic mock vectors (test/development only).'`. |
| L229 | Close the expression/container begun at L226; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L230 | Evaluate the right-hand side, then bind/store it in `embedder`: `EmbeddingService(embedding_config)` — Construct `EmbeddingService` with the shown fields; its class/model initialization rules apply. |
| L231 | Evaluate the right-hand side, then bind/store it in `index_service`: `IndexService()` — Construct `IndexService` with the shown fields; its class/model initialization rules apply. |
| L232 | Compute the return value: build a tuple containing `store`, `storage`, `embedder`, `index_service`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `run_worker_once(config, *, queue, storage, embedder=None, index_service=None, reconciler=None, processor=None) -> tuple[ReconcileReport, list[ProcessOutcome]]`

Builds a reconciler when omitted, runs it, then claims up to configured concurrency with the lease settings. No claims returns `(report, [])`. Builds a processor if needed; one claim/concurrency one processes serially, otherwise a bounded `ThreadPoolExecutor` submits all claims and collects outcomes in completion order. Future exceptions log and omit that outcome; exceptions from a supplied serial processor propagate. Claim/reconciler exceptions can propagate to the outer polling loop. Returns report/outcomes after the batch finishes; it does not poll or sleep itself.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-run-worker-once"></a>

#### Line-by-line execution

[Current source: lines 235–289](../../../../Backend/app/workers/pdf_worker.py#L235-L289). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `config` | `WorkerConfig`; required; positional or keyword | Configuration object consumed by the field accesses below. |
| `queue` | `QueuePort`; required; keyword-only | Queue collaborator for short claim, lease, progress, and terminal-state operations. |
| `storage` | `StoragePort`; required; keyword-only | Storage collaborator for private file creation, inspection, ranged reads, or deletion. |
| `embedder` | `EmbedderPort \| None`; default `None`; keyword-only | Embedding collaborator; the function selects its default only where explicitly shown. |
| `index_service` | `IndexPort \| None`; default `None`; keyword-only | Collaborator for version-scoped vector writes/deletes. |
| `reconciler` | `Reconciler \| None`; default `None`; keyword-only | Caller-supplied reconciler; each read, transformation, and validation is traced below. |
| `processor` | `DocumentProcessor \| None`; default `None`; keyword-only | Caller-supplied processor; each read, transformation, and validation is traced below. |

**Declared result:** `tuple[ReconcileReport, list[ProcessOutcome]]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 235 | def run_worker_once(
 236 |     config: WorkerConfig,
 237 |     *,
 238 |     queue: QueuePort,
 239 |     storage: StoragePort,
 240 |     embedder: EmbedderPort | None = None,
 241 |     index_service: IndexPort | None = None,
 242 |     reconciler: Reconciler | None = None,
 243 |     processor: DocumentProcessor | None = None,
 244 | ) -> tuple[ReconcileReport, list[ProcessOutcome]]:
 245 |     """One loop iteration: reconcile, claim one batch, process it.
 246 | 
 247 |     Returned for tests, manual runs, and the ``--once`` flag.  Each
 248 |     reconciliation pass and each job is isolated: failures are logged
 249 |     and retried on a later iteration, never fatal to the loop.
 250 |     """
 251 |     if reconciler is None:
 252 |         reconciler = Reconciler(
 253 |             queue,  # type: ignore[arg-type]
 254 |             storage=storage,
 255 |             index_service=index_service,
 256 |             awaiting_upload_ttl_seconds=config.awaiting_upload_ttl_seconds,
 257 |             sweep_grace_seconds=config.sweep_grace_seconds,
 258 |             batch_size=config.batch_size,
 259 |             backoff_base_seconds=config.backoff_base_seconds,
 260 |             backoff_cap_seconds=config.backoff_cap_seconds,
 261 |         )
 262 |     report = reconciler.run_once()
 263 |     claims = queue.claim_next_jobs(
 264 |         worker_id=config.worker_id, limit=config.concurrency, lease_seconds=config.lease_seconds
 265 |     )
 266 |     if not claims:
 267 |         return report, []
 268 |     if processor is None:
 269 |         processor = DocumentProcessor(
 270 |             queue=queue,
 271 |             storage=storage,
 272 |             embedder=embedder,
 273 |             index_service=index_service,
 274 |             config=config.processor_config(),
 275 |         )
 276 |     outcomes: list[ProcessOutcome] = []
 277 |     if config.concurrency <= 1 or len(claims) <= 1:
 278 |         for claim in claims:
 279 |             outcomes.append(processor.process(claim))
 280 |         return report, outcomes
 281 |     with ThreadPoolExecutor(max_workers=config.concurrency, thread_name_prefix="pdf-job") as pool:
 282 |         futures = {pool.submit(processor.process, claim): claim for claim in claims}
 283 |         for future in as_completed(futures):
 284 |             claim = futures[future]
 285 |             try:
 286 |                 outcomes.append(future.result())
 287 |             except Exception:
 288 |                 log.exception("worker crashed processing job %s", claim.job_id)
 289 |     return report, outcomes
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L235 | Define `run_worker_once`; bind its arguments when called. The body executes only when invoked. |
| L236 | Declare parameter `config` with annotation `WorkerConfig`. Configuration object consumed by the field accesses below. |
| L237 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L238 | Declare parameter `queue` with annotation `QueuePort`. Queue collaborator for short claim, lease, progress, and terminal-state operations. |
| L239 | Declare parameter `storage` with annotation `StoragePort`. Storage collaborator for private file creation, inspection, ranged reads, or deletion. |
| L240 | Declare parameter `embedder` with annotation `EmbedderPort \| None`. Embedding collaborator; the function selects its default only where explicitly shown. |
| L241 | Declare parameter `index_service` with annotation `IndexPort \| None`. Collaborator for version-scoped vector writes/deletes. |
| L242 | Declare parameter `reconciler` with annotation `Reconciler \| None`. Caller-supplied reconciler; its uses and transformations are traced below. |
| L243 | Declare parameter `processor` with annotation `DocumentProcessor \| None`. Caller-supplied processor; its uses and transformations are traced below. |
| L244 | Finish/continue the signature; the declared return annotation is `tuple[ReconcileReport, list[ProcessOutcome]]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L245 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L247 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L248 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L249 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L250 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L251 | Evaluate the branch condition: compare whether `reconciler` is the same object as `None`. If truthy, enter L252; otherwise skip this indented block and continue after it. |
| L252 | Evaluate the right-hand side, then bind/store it in `reconciler`: `Reconciler` with the arguments detailed below — Construct `Reconciler` with the shown fields; its class/model initialization rules apply. |
| L253 | Supply positional argument 1 to `Reconciler`: the current `queue` value. |
| L254 | Supply `storage` = `storage`. Storage collaborator for private file creation, inspection, ranged reads, or deletion. Evaluate the value as: the current `storage` value. |
| L255 | Supply `index_service` = `index_service`. Collaborator for version-scoped vector writes/deletes. Evaluate the value as: the current `index_service` value. |
| L256 | Supply `awaiting_upload_ttl_seconds` = `config.awaiting_upload_ttl_seconds`.  Evaluate the value as: the `awaiting_upload_ttl_seconds` attribute of `config`. |
| L257 | Supply `sweep_grace_seconds` = `config.sweep_grace_seconds`.  Evaluate the value as: the `sweep_grace_seconds` attribute of `config`. |
| L258 | Supply `batch_size` = `config.batch_size`. Maximum batch size for the operation; validation/clamping is explicit in the body. Evaluate the value as: the `batch_size` attribute of `config`. |
| L259 | Supply `backoff_base_seconds` = `config.backoff_base_seconds`. Base retry delay, doubled with successive attempts before capping/jitter. Evaluate the value as: the `backoff_base_seconds` attribute of `config`. |
| L260 | Supply `backoff_cap_seconds` = `config.backoff_cap_seconds`. Maximum retry-delay bound passed to the backoff calculation. Evaluate the value as: the `backoff_cap_seconds` attribute of `config`. |
| L261 | Close the expression/container begun at L252; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L262 | Evaluate the right-hand side, then bind/store it in `report`: `reconciler.run_once()` — Invoke `reconciler.run_once` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L263 | Evaluate the right-hand side, then bind/store it in `claims`: `queue.claim_next_jobs(worker_id=config.worker_id, limit=config.concurrency, lease_seconds=config.lease_seconds)` — Lock/claim a due batch, advance attempt/token, and establish per-attempt index versions within a short transaction. |
| L264 | Supply `worker_id` = `config.worker_id`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: the `worker_id` attribute of `config`. Supply `limit` = `config.concurrency`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. Evaluate the value as: the `concurrency` attribute of `config`. Supply `lease_seconds` = `config.lease_seconds`. Lease duration in seconds; positive-duration validation is not implicit in this parameter. Evaluate the value as: the `lease_seconds` attribute of `config`. |
| L265 | Close the expression/container begun at L263; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L266 | Evaluate the branch condition: invert the truthiness of `claims`. If truthy, enter L267; otherwise skip this indented block and continue after it. |
| L267 | Compute the return value: build a tuple containing `report`, `[]`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L268 | Evaluate the branch condition: compare whether `processor` is the same object as `None`. If truthy, enter L269; otherwise skip this indented block and continue after it. |
| L269 | Evaluate the right-hand side, then bind/store it in `processor`: `DocumentProcessor(queue=queue, storage=storage, embedder=embedder, index_service=index_service, config=config.processor_config())` — Construct `DocumentProcessor` with the shown fields; its class/model initialization rules apply. |
| L270 | Supply `queue` = `queue`. Queue collaborator for short claim, lease, progress, and terminal-state operations. Evaluate the value as: the current `queue` value. |
| L271 | Supply `storage` = `storage`. Storage collaborator for private file creation, inspection, ranged reads, or deletion. Evaluate the value as: the current `storage` value. |
| L272 | Supply `embedder` = `embedder`. Embedding collaborator; the function selects its default only where explicitly shown. Evaluate the value as: the current `embedder` value. |
| L273 | Supply `index_service` = `index_service`. Collaborator for version-scoped vector writes/deletes. Evaluate the value as: the current `index_service` value. |
| L274 | Supply `config` = `config.processor_config()`. Configuration object consumed by the field accesses below. Evaluate the value as: `config.processor_config()` — Invoke `config.processor_config` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L275 | Close the expression/container begun at L269; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L276 | Evaluate the right-hand side, then bind/store it in `outcomes`: build a list containing no items. |
| L277 | Evaluate the branch condition: evaluate `config.concurrency <= 1 or len(claims) <= 1` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L278; otherwise skip this indented block and continue after it. |
| L278 | Iterate `claims` (the current `claims` value), assigning each item to `claim`. Execute the indented body once per item; an empty iterable skips it. |
| L279 | `outcomes.append(processor.process(claim))` — Append one object to the mutable list in place; inputs include `processor.process(claim)` — Invoke `processor.process` with the shown inputs and use its result; see the function overview for its role in this flow. The return value is not assigned here. |
| L280 | Compute the return value: build a tuple containing `report`, `outcomes`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L281 | Enter `ThreadPoolExecutor(max_workers=config.concurrency, thread_name_prefix='pdf-job')` — Create a bounded worker-thread pool; exiting its context waits for submitted work and bind its entered value to `pool`. Context exits run in reverse order, including on return/exception. |
| L282 | Evaluate the right-hand side, then bind/store it in `futures`: iterate `claims`, binding each item to `claim`; produce `pool.submit(processor.process, claim)` → `claim` into a new mapping. |
| L283 | Iterate `as_completed(futures)` (`as_completed(futures)` — Yield submitted futures as each finishes, rather than in submission order), assigning each item to `future`. Execute the indented body once per item; an empty iterable skips it. |
| L284 | Evaluate the right-hand side, then bind/store it in `claim`: look up index/key `future` in `futures`; a missing key or out-of-range index raises. |
| L285 | Enter the protected block; failures are matched against `Exception` in order. |
| L286 | `outcomes.append(future.result())` — Append one object to the mutable list in place; inputs include `future.result()` — Read the Future's result, waiting if necessary; a worker exception is re-raised here. The return value is not assigned here. |
| L287 | Handle `Exception`; only a matching error from the associated try enters this body. |
| L288 | `log.exception('worker crashed processing job %s', claim.job_id)` — Emit an error log including the current exception traceback. The return value is not assigned here. |
| L289 | Compute the return value: build a tuple containing `report`, `outcomes`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `run_worker(config, *, queue, storage, embedder=None, index_service=None, stop_event=None) -> None`

Creates/reuses a stop event and constructs shared reconciler/processor. Logs startup, repeats `run_worker_once`, catches whole-iteration failures, logs all outcomes and up to 20 reconciliation actions. Waits interruptibly for poll interval only when no outcomes occurred; successful/busy batches proceed immediately. Checks stop between batches, so in-flight jobs finish before exit. It does not install signal handlers itself.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-run-worker"></a>

#### Line-by-line execution

[Current source: lines 292–353](../../../../Backend/app/workers/pdf_worker.py#L292-L353). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `config` | `WorkerConfig`; required; positional or keyword | Configuration object consumed by the field accesses below. |
| `queue` | `QueuePort`; required; keyword-only | Queue collaborator for short claim, lease, progress, and terminal-state operations. |
| `storage` | `StoragePort`; required; keyword-only | Storage collaborator for private file creation, inspection, ranged reads, or deletion. |
| `embedder` | `EmbedderPort \| None`; default `None`; keyword-only | Embedding collaborator; the function selects its default only where explicitly shown. |
| `index_service` | `IndexPort \| None`; default `None`; keyword-only | Collaborator for version-scoped vector writes/deletes. |
| `stop_event` | `threading.Event \| None`; default `None`; keyword-only | Shared shutdown event; the worker checks it between batches and during idle waits. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 292 | def run_worker(
 293 |     config: WorkerConfig,
 294 |     *,
 295 |     queue: QueuePort,
 296 |     storage: StoragePort,
 297 |     embedder: EmbedderPort | None = None,
 298 |     index_service: IndexPort | None = None,
 299 |     stop_event: threading.Event | None = None,
 300 | ) -> None:
 301 |     """Poll loop.  ``SIGTERM``/``SIGINT`` stop after in-flight jobs."""
 302 |     stop = stop_event or threading.Event()
 303 |     reconciler = Reconciler(
 304 |         queue,  # type: ignore[arg-type]
 305 |         storage=storage,
 306 |         index_service=index_service,
 307 |         awaiting_upload_ttl_seconds=config.awaiting_upload_ttl_seconds,
 308 |         sweep_grace_seconds=config.sweep_grace_seconds,
 309 |         batch_size=config.batch_size,
 310 |         backoff_base_seconds=config.backoff_base_seconds,
 311 |         backoff_cap_seconds=config.backoff_cap_seconds,
 312 |     )
 313 |     processor = DocumentProcessor(
 314 |         queue=queue,
 315 |         storage=storage,
 316 |         embedder=embedder,
 317 |         index_service=index_service,
 318 |         config=config.processor_config(),
 319 |     )
 320 |     log.info(
 321 |         "worker %s starting (poll=%ss concurrency=%s lease=%ss)",
 322 |         config.worker_id,
 323 |         config.poll_interval_seconds,
 324 |         config.concurrency,
 325 |         config.lease_seconds,
 326 |     )
 327 |     while not stop.is_set():
 328 |         try:
 329 |             report, outcomes = run_worker_once(
 330 |                 config,
 331 |                 queue=queue,
 332 |                 storage=storage,
 333 |                 embedder=embedder,
 334 |                 index_service=index_service,
 335 |                 reconciler=reconciler,
 336 |                 processor=processor,
 337 |             )
 338 |         except Exception:
 339 |             log.exception("worker iteration failed; will retry next poll")
 340 |             report, outcomes = ReconcileReport(), []
 341 |         for outcome in outcomes:
 342 |             log.info(
 343 |                 "job %s -> %s (%s)",
 344 |                 outcome.job_id,
 345 |                 outcome.status,
 346 |                 outcome.detail or outcome.kind,
 347 |             )
 348 |         if report.actions:
 349 |             for action in report.actions[:20]:
 350 |                 log.info("reconcile: %s", action)
 351 |         if not outcomes and not stop.is_set():
 352 |             stop.wait(config.poll_interval_seconds)
 353 |     log.info("worker %s stopped", config.worker_id)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L292 | Define `run_worker`; bind its arguments when called. The body executes only when invoked. |
| L293 | Declare parameter `config` with annotation `WorkerConfig`. Configuration object consumed by the field accesses below. |
| L294 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L295 | Declare parameter `queue` with annotation `QueuePort`. Queue collaborator for short claim, lease, progress, and terminal-state operations. |
| L296 | Declare parameter `storage` with annotation `StoragePort`. Storage collaborator for private file creation, inspection, ranged reads, or deletion. |
| L297 | Declare parameter `embedder` with annotation `EmbedderPort \| None`. Embedding collaborator; the function selects its default only where explicitly shown. |
| L298 | Declare parameter `index_service` with annotation `IndexPort \| None`. Collaborator for version-scoped vector writes/deletes. |
| L299 | Declare parameter `stop_event` with annotation `threading.Event \| None`. Shared shutdown event; the worker checks it between batches and during idle waits. |
| L300 | Finish/continue the signature; the declared return annotation is `None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L301 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L302 | Evaluate the right-hand side, then bind/store it in `stop`: evaluate `stop_event or threading.Event()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L303 | Evaluate the right-hand side, then bind/store it in `reconciler`: `Reconciler` with the arguments detailed below — Construct `Reconciler` with the shown fields; its class/model initialization rules apply. |
| L304 | Supply positional argument 1 to `Reconciler`: the current `queue` value. |
| L305 | Supply `storage` = `storage`. Storage collaborator for private file creation, inspection, ranged reads, or deletion. Evaluate the value as: the current `storage` value. |
| L306 | Supply `index_service` = `index_service`. Collaborator for version-scoped vector writes/deletes. Evaluate the value as: the current `index_service` value. |
| L307 | Supply `awaiting_upload_ttl_seconds` = `config.awaiting_upload_ttl_seconds`.  Evaluate the value as: the `awaiting_upload_ttl_seconds` attribute of `config`. |
| L308 | Supply `sweep_grace_seconds` = `config.sweep_grace_seconds`.  Evaluate the value as: the `sweep_grace_seconds` attribute of `config`. |
| L309 | Supply `batch_size` = `config.batch_size`. Maximum batch size for the operation; validation/clamping is explicit in the body. Evaluate the value as: the `batch_size` attribute of `config`. |
| L310 | Supply `backoff_base_seconds` = `config.backoff_base_seconds`. Base retry delay, doubled with successive attempts before capping/jitter. Evaluate the value as: the `backoff_base_seconds` attribute of `config`. |
| L311 | Supply `backoff_cap_seconds` = `config.backoff_cap_seconds`. Maximum retry-delay bound passed to the backoff calculation. Evaluate the value as: the `backoff_cap_seconds` attribute of `config`. |
| L312 | Close the expression/container begun at L303; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L313 | Evaluate the right-hand side, then bind/store it in `processor`: `DocumentProcessor(queue=queue, storage=storage, embedder=embedder, index_service=index_service, config=config.processor_config())` — Construct `DocumentProcessor` with the shown fields; its class/model initialization rules apply. |
| L314 | Supply `queue` = `queue`. Queue collaborator for short claim, lease, progress, and terminal-state operations. Evaluate the value as: the current `queue` value. |
| L315 | Supply `storage` = `storage`. Storage collaborator for private file creation, inspection, ranged reads, or deletion. Evaluate the value as: the current `storage` value. |
| L316 | Supply `embedder` = `embedder`. Embedding collaborator; the function selects its default only where explicitly shown. Evaluate the value as: the current `embedder` value. |
| L317 | Supply `index_service` = `index_service`. Collaborator for version-scoped vector writes/deletes. Evaluate the value as: the current `index_service` value. |
| L318 | Supply `config` = `config.processor_config()`. Configuration object consumed by the field accesses below. Evaluate the value as: `config.processor_config()` — Invoke `config.processor_config` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L319 | Close the expression/container begun at L313; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L320 | `log.info('worker %s starting (poll=%ss concurrency=%s lease=%ss)', config.worker_id, config.poll_interval_seconds, config.concurrency, config.lease_seconds)` — Emit an informational log message with the supplied resource/status values. The return value is not assigned here. |
| L321 | Supply positional argument 1 to `log.info`: `'worker %s starting (poll=%ss concurrency=%s lease=%ss)'`. |
| L322 | Supply positional argument 2 to `log.info`: the `worker_id` attribute of `config`. |
| L323 | Supply positional argument 3 to `log.info`: the `poll_interval_seconds` attribute of `config`. |
| L324 | Supply positional argument 4 to `log.info`: the `concurrency` attribute of `config`. |
| L325 | Supply positional argument 5 to `log.info`: the `lease_seconds` attribute of `config`. |
| L326 | Close the expression/container begun at L320; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L327 | Re-evaluate `not stop.is_set()` before every iteration; run the body while truthy and leave when false or when a break executes. |
| L328 | Enter the protected block; failures are matched against `Exception` in order. |
| L329 | Evaluate the right-hand side, then bind/store it in `(report, outcomes)`: `run_worker_once(config, queue=queue, storage=storage, embedder=embedder, index_service=index_service, reconciler=reconciler, processor=processor)` — Call [run_worker_once](#walk-run-worker-once) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L330 | Supply positional argument 1 to `run_worker_once`: the current `config` value. |
| L331 | Supply `queue` = `queue`. Queue collaborator for short claim, lease, progress, and terminal-state operations. Evaluate the value as: the current `queue` value. |
| L332 | Supply `storage` = `storage`. Storage collaborator for private file creation, inspection, ranged reads, or deletion. Evaluate the value as: the current `storage` value. |
| L333 | Supply `embedder` = `embedder`. Embedding collaborator; the function selects its default only where explicitly shown. Evaluate the value as: the current `embedder` value. |
| L334 | Supply `index_service` = `index_service`. Collaborator for version-scoped vector writes/deletes. Evaluate the value as: the current `index_service` value. |
| L335 | Supply `reconciler` = `reconciler`.  Evaluate the value as: the current `reconciler` value. |
| L336 | Supply `processor` = `processor`.  Evaluate the value as: the current `processor` value. |
| L337 | Close the expression/container begun at L329; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L338 | Handle `Exception`; only a matching error from the associated try enters this body. |
| L339 | `log.exception('worker iteration failed; will retry next poll')` — Emit an error log including the current exception traceback. The return value is not assigned here. |
| L340 | Evaluate the right-hand side, then bind/store it in `(report, outcomes)`: build a tuple containing `ReconcileReport()`, `[]`. |
| L341 | Iterate `outcomes` (the current `outcomes` value), assigning each item to `outcome`. Execute the indented body once per item; an empty iterable skips it. |
| L342 | `log.info('job %s -> %s (%s)', outcome.job_id, outcome.status, outcome.detail or outcome.kind)` — Emit an informational log message with the supplied resource/status values. The return value is not assigned here. |
| L343 | Supply positional argument 1 to `log.info`: `'job %s -> %s (%s)'`. |
| L344 | Supply positional argument 2 to `log.info`: the `job_id` attribute of `outcome`. |
| L345 | Supply positional argument 3 to `log.info`: the `status` attribute of `outcome`. |
| L346 | Continue the enclosing expression: evaluate `outcome.detail or outcome.kind` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L347 | Close the expression/container begun at L342; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L348 | Evaluate the branch condition: the `actions` attribute of `report`. If truthy, enter L349; otherwise skip this indented block and continue after it. |
| L349 | Iterate `report.actions[:20]` (slice `report.actions` from the beginning up to `20` (exclusive stop)), assigning each item to `action`. Execute the indented body once per item; an empty iterable skips it. |
| L350 | `log.info('reconcile: %s', action)` — Emit an informational log message with the supplied resource/status values. The return value is not assigned here. |
| L351 | Evaluate the branch condition: evaluate `not outcomes and (not stop.is_set())` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L352; otherwise skip this indented block and continue after it. |
| L352 | `stop.wait(config.poll_interval_seconds)` — Wait on `stop` for the supplied timeout; return early if it is signalled. The return value is not assigned here. |
| L353 | `log.info('worker %s stopped', config.worker_id)` — Emit an informational log message with the supplied resource/status values. The return value is not assigned here. |

<!-- END LINE WALKTHROUGH -->

### `main(argv: Sequence[str] | None = None) -> int`

Parses optional `--worker-id`, `--poll-interval`, `--concurrency`, `--lease-seconds`, and `--once`; null argv uses process arguments. Configures INFO logging, loads repository-root application environment, creates config/dependencies. Once mode prints per-job outcomes/action count and returns 0 even if outcomes contain failures. Otherwise installs SIGTERM/SIGINT handlers when allowed, runs the polling loop, and returns 0. Argument parsing can exit; configuration/startup errors propagate. `Sequence` is used in a postponed annotation but is not imported in the current module, so runtime annotation introspection needs care. The `__main__` guard exits with `sys.exit(main())`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-main"></a>

#### Line-by-line execution

[Current source: lines 356–401](../../../../Backend/app/workers/pdf_worker.py#L356-L401). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `argv` | `Sequence[str] \| None`; default `None`; positional or keyword | CLI argument sequence; null lets argparse read process arguments. |

**Declared result:** `int`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 356 | def main(argv: Sequence[str] | None = None) -> int:
 357 |     parser = argparse.ArgumentParser(prog="pdf_worker", description="DocuMind PDF job worker")
 358 |     parser.add_argument("--worker-id", default=None)
 359 |     parser.add_argument("--poll-interval", type=int, default=None)
 360 |     parser.add_argument("--concurrency", type=int, default=None)
 361 |     parser.add_argument("--lease-seconds", type=int, default=None)
 362 |     parser.add_argument("--once", action="store_true", help="one reconcile + one claim batch, then exit")
 363 |     args = parser.parse_args(argv)
 364 |     logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
 365 | 
 366 |     # Local-dev parity with app/main.py: load the repository-root .env
 367 |     # without overriding variables already set in the process environment.
 368 |     from app.config import load_application_env
 369 | 
 370 |     load_application_env()
 371 | 
 372 |     config = WorkerConfig.from_env(
 373 |         worker_id=args.worker_id,
 374 |         poll_interval_seconds=args.poll_interval,
 375 |         concurrency=args.concurrency,
 376 |         lease_seconds=args.lease_seconds,
 377 |     )
 378 |     store, storage, embedder, index_service = build_default_dependencies(config)
 379 | 
 380 |     if args.once:
 381 |         report, outcomes = run_worker_once(
 382 |             config, queue=store, storage=storage, embedder=embedder, index_service=index_service
 383 |         )
 384 |         for outcome in outcomes:
 385 |             print(f"job {outcome.job_id} -> {outcome.status} ({outcome.detail})")
 386 |         print(f"reconciled: {len(report.actions)} action(s)")
 387 |         return 0
 388 | 
 389 |     stop = threading.Event()
 390 | 
 391 |     def _request_stop(signum: int, _frame: Any) -> None:
 392 |         log.info("received signal %s; stopping after in-flight jobs", signum)
 393 |         stop.set()
 394 | 
 395 |     try:
 396 |         signal.signal(signal.SIGTERM, _request_stop)
 397 |         signal.signal(signal.SIGINT, _request_stop)
 398 |     except (ValueError, OSError):  # not the main thread (tests, embedded)
 399 |         pass
 400 |     run_worker(config, queue=store, storage=storage, embedder=embedder, index_service=index_service, stop_event=stop)
 401 |     return 0
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L356 | Define `main`; bind its arguments when called. The body executes only when invoked. |
| L357 | Evaluate the right-hand side, then bind/store it in `parser`: `argparse.ArgumentParser(prog='pdf_worker', description='DocuMind PDF job worker')` — Construct `argparse.ArgumentParser` with the shown fields; its class/model initialization rules apply. |
| L358 | `parser.add_argument('--worker-id', default=None)` — Register a CLI option, conversion/default, or boolean action with argparse. The return value is not assigned here. |
| L359 | `parser.add_argument('--poll-interval', type=int, default=None)` — Register a CLI option, conversion/default, or boolean action with argparse. The return value is not assigned here. |
| L360 | `parser.add_argument('--concurrency', type=int, default=None)` — Register a CLI option, conversion/default, or boolean action with argparse. The return value is not assigned here. |
| L361 | `parser.add_argument('--lease-seconds', type=int, default=None)` — Register a CLI option, conversion/default, or boolean action with argparse. The return value is not assigned here. |
| L362 | `parser.add_argument('--once', action='store_true', help='one reconcile + one claim batch, then exit')` — Register a CLI option, conversion/default, or boolean action with argparse. The return value is not assigned here. |
| L363 | Evaluate the right-hand side, then bind/store it in `args`: `parser.parse_args(argv)` — Parse command-line arguments into the namespace; invalid arguments print usage and exit. |
| L364 | `logging.basicConfig(level=logging.INFO, format='%(levelname)s %(name)s %(message)s')` — Invoke `logging.basicConfig` with the shown inputs and use its result; see the function overview for its role in this flow. The return value is not assigned here. |
| L366 | Comment only: Local-dev parity with app/main.py: load the repository-root .env. It does not execute; the neighboring code determines behavior. |
| L367 | Comment only: without overriding variables already set in the process environment.. It does not execute; the neighboring code determines behavior. |
| L368 | Import `load_application_env` from `app.config`; inside a function this import is deferred until this path is reached. |
| L370 | `load_application_env()` — Call [load_application_env](../config.md#walk-load-application-env) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L372 | Evaluate the right-hand side, then bind/store it in `config`: `WorkerConfig.from_env(worker_id=args.worker_id, poll_interval_seconds=args.poll_interval, concurrency=args.concurrency, lease_seconds=args.lease_seconds)` — Call [WorkerConfig.from_env](#walk-workerconfig-from-env) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L373 | Supply `worker_id` = `args.worker_id`. Worker identity that must match the stored lease owner for guarded writes. Evaluate the value as: the `worker_id` attribute of `args`. |
| L374 | Supply `poll_interval_seconds` = `args.poll_interval`.  Evaluate the value as: the `poll_interval` attribute of `args`. |
| L375 | Supply `concurrency` = `args.concurrency`.  Evaluate the value as: the `concurrency` attribute of `args`. |
| L376 | Supply `lease_seconds` = `args.lease_seconds`. Lease duration in seconds; positive-duration validation is not implicit in this parameter. Evaluate the value as: the `lease_seconds` attribute of `args`. |
| L377 | Close the expression/container begun at L372; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L378 | Evaluate the right-hand side, then bind/store it in `(store, storage, embedder, index_service)`: `build_default_dependencies(config)` — Call [build_default_dependencies](#walk-build-default-dependencies) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L380 | Evaluate the branch condition: the `once` attribute of `args`. If truthy, enter L381; otherwise skip this indented block and continue after it. |
| L381 | Evaluate the right-hand side, then bind/store it in `(report, outcomes)`: `run_worker_once(config, queue=store, storage=storage, embedder=embedder, index_service=index_service)` — Call [run_worker_once](#walk-run-worker-once) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L382 | Supply `queue` = `store`. Queue collaborator for short claim, lease, progress, and terminal-state operations. Evaluate the value as: the current `store` value. Supply `storage` = `storage`. Storage collaborator for private file creation, inspection, ranged reads, or deletion. Evaluate the value as: the current `storage` value. Supply `embedder` = `embedder`. Embedding collaborator; the function selects its default only where explicitly shown. Evaluate the value as: the current `embedder` value. Supply `index_service` = `index_service`. Collaborator for version-scoped vector writes/deletes. Evaluate the value as: the current `index_service` value. |
| L383 | Close the expression/container begun at L381; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L384 | Iterate `outcomes` (the current `outcomes` value), assigning each item to `outcome`. Execute the indented body once per item; an empty iterable skips it. |
| L385 | `print(f'job {outcome.job_id} -> {outcome.status} ({outcome.detail})')` — Write the formatted diagnostic to standard output. The return value is not assigned here. |
| L386 | `print(f'reconciled: {len(report.actions)} action(s)')` — Write the formatted diagnostic to standard output. The return value is not assigned here. |
| L387 | Compute the return value: `0`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L389 | Evaluate the right-hand side, then bind/store it in `stop`: `threading.Event()` — Create an initially unset synchronization event shared by cooperating threads. |
| L391 | Define the local closure [main._request_stop](#walk-main--request-stop); it can capture enclosing locals. Definition does not execute its body. |
| L392 | `log.info('received signal %s; stopping after in-flight jobs', signum)` — Emit an informational log message with the supplied resource/status values. The return value is not assigned here. |
| L393 | `stop.set()` — Signal the `stop` event so waiting/cooperating code observes the request. The return value is not assigned here. |
| L395 | Enter the protected block; failures are matched against `(ValueError, OSError)` in order. |
| L396 | `signal.signal(signal.SIGTERM, _request_stop)` — Register the supplied handler for the signal; registration may fail outside the main thread. The return value is not assigned here. |
| L397 | `signal.signal(signal.SIGINT, _request_stop)` — Register the supplied handler for the signal; registration may fail outside the main thread. The return value is not assigned here. |
| L398 | Handle `(ValueError, OSError)`; only a matching error from the associated try enters this body. |
| L399 | Do nothing; this explicitly empty branch continues execution (here it can intentionally ignore a caught exception). |
| L400 | `run_worker(config, queue=store, storage=storage, embedder=embedder, index_service=index_service, stop_event=stop)` — Call [run_worker](#walk-run-worker) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L401 | Compute the return value: `0`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `main._request_stop(signum: int, _frame: Any) -> None`

Nested signal handler capturing the local stop event. Logs signal number and sets the event; ignores the frame. It requests shutdown after the active batch rather than terminating provider calls immediately.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-main--request-stop"></a>

#### Line-by-line execution

[Current source: lines 391–393](../../../../Backend/app/workers/pdf_worker.py#L391-L393). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `signum` | `int`; required; positional or keyword | Caller-supplied signum; each read, transformation, and validation is traced below. |
| `_frame` | `Any`; required; positional or keyword | Caller-supplied  frame; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 391 |     def _request_stop(signum: int, _frame: Any) -> None:
 392 |         log.info("received signal %s; stopping after in-flight jobs", signum)
 393 |         stop.set()
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L391 | Define `main._request_stop`; bind its arguments when called. The body executes only when invoked. |
| L392 | `log.info('received signal %s; stopping after in-flight jobs', signum)` — Emit an informational log message with the supplied resource/status values. The return value is not assigned here. |
| L393 | `stop.set()` — Signal the `stop` event so waiting/cooperating code observes the request. The return value is not assigned here. |

<!-- END LINE WALKTHROUGH -->
