# `app/rag/embeddings.py`

[Source](../../../../Backend/app/rag/embeddings.py) · [Backend index](../../README.md)

Synchronous ordered embedding batches with response validation. HF defaults to `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions); Jina defaults to `jina-embeddings-v5-text-small` (1024 dimensions). Batch size is 16, request timeout 30 seconds. Mock mode directly produces deterministic vectors and bypasses HTTP; it is not an outage fallback.

## Configuration

Frozen dataclass `EmbeddingConfig` stores `provider="hf"`, `model_id`, `timeout_seconds`, `batch_size`, `dim`, `allow_mock=False`, and optional `api_url`. Its generated constructor validates only provider membership through `__post_init__`; other numeric/model values are not validated here. `HttpPost` is a callable shaped like `httpx.post`.

## Functions

### `EmbeddingProviderError.__init__(self, message: str) -> None`

**Arguments:** Diagnostic text. **Returns:** `None`. **Work:** Initializes the exception and `.message`. Class attributes are `code="embedding_provider_unavailable"`, `retryable=True`; the job layer later converts diagnostics into safe failure summaries.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-embeddingprovidererror---init--"></a>

#### Line-by-line execution

[Current source: lines 68–70](../../../../Backend/app/rag/embeddings.py#L68-L70). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `message` | `str`; required; positional or keyword | Caller-supplied message; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  68 |     def __init__(self, message: str) -> None:
  69 |         super().__init__(message)
  70 |         self.message = message
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L68 | Define `EmbeddingProviderError.__init__`; bind its arguments when called. The body executes only when invoked. |
| L69 | `super().__init__(message)` — Initialize the base exception/object with the supplied arguments; first obtain the receiver: `super()` — Resolve the superclass proxy for the current method and instance. The return value is not assigned here. |
| L70 | Evaluate the right-hand side, then bind/store it in `self.message`: the current `message` value. |

<!-- END LINE WALKTHROUGH -->

### `deterministic_fallback_embedding(text: str, *, dim=384) -> list[float]`

**Arguments:** Text and desired vector length. **Returns:** Deterministic pseudo-random vector, normalized to unit length if its magnitude is positive. **Work:** Hashes UTF-8 text with MD5, converts the digest to an integer seed for a private `random.Random`, samples `dim` uniform values in `[-1, 1]`, and divides by Euclidean magnitude. It neither uses nor changes the global PRNG. This helper itself has no opt-in guard and does not provide semantic embeddings; service/worker configuration controls its use.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-deterministic-fallback-embedding"></a>

#### Line-by-line execution

[Current source: lines 73–88](../../../../Backend/app/rag/embeddings.py#L73-L88). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `text` | `str`; required; positional or keyword | Text to split, hash, normalize, or embed as shown by this function's body. |
| `dim` | `int`; default `EMBEDDING_DIM`; keyword-only | Required vector dimension (number of numeric components). |

**Declared result:** `list[float]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  73 | def deterministic_fallback_embedding(text: str, *, dim: int = EMBEDDING_DIM) -> list[float]:
  74 |     """Deterministic pseudo-random unit vector for a text (mock mode only).
  75 | 
  76 |     MD5-seeded PRNG,
  77 |     normalized to unit length.  Test/development use only -- production
  78 |     must never publish this as the index vector.  The ``dim`` keyword
  79 |     exists so test doubles can use smaller vectors; production callers
  80 |     must not pass it.
  81 |     """
  82 |     seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
  83 |     rng = random.Random(seed)
  84 |     vector = [rng.uniform(-1.0, 1.0) for _ in range(dim)]
  85 |     magnitude = math.sqrt(sum(x * x for x in vector))
  86 |     if magnitude > 0:
  87 |         vector = [x / magnitude for x in vector]
  88 |     return vector
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L73 | Define `deterministic_fallback_embedding`; bind its arguments when called. The body executes only when invoked. |
| L74 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L76 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L77 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L78 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L79 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L80 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L81 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L82 | UTF-8 encode the text, hash it with MD5, render the digest as hexadecimal, then parse that hex integer. Identical text gets the same PRNG seed; it contains no learned semantic information. |
| L83 | Evaluate the right-hand side, then bind/store it in `rng`: `random.Random(seed)` — Create an independent pseudo-random generator using the supplied seed. |
| L84 | Evaluate the right-hand side, then bind/store it in `vector`: iterate `range(dim)`, binding each item to `_`; produce `rng.uniform(-1.0, 1.0)` into a new list. |
| L85 | Square each vector component, sum the squares, and take the square root to obtain its Euclidean (L2) length. |
| L86 | Evaluate the branch condition: compare whether `magnitude` is greater than `0`. If truthy, enter L87; otherwise skip this indented block and continue after it. |
| L87 | Normalize every component by the positive L2 magnitude so the mock vector has unit length. The enclosing guard skips this division for a zero vector. |
| L88 | Compute the return value: the current `vector` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `mock_embeddings_allowed_from_env(env: dict[str, str] | None = None) -> bool`

**Arguments:** Optional settings mapping (an empty supplied mapping is respected). **Returns:** Whether `DOCUMIND_ALLOW_MOCK_EMBEDDINGS`, stripped/lowercased, is one of `1`, `true`, `yes`, `on`. **Work:** Reads the mapping or current process environment and checks membership.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-mock-embeddings-allowed-from-env"></a>

#### Line-by-line execution

[Current source: lines 91–94](../../../../Backend/app/rag/embeddings.py#L91-L94). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `env` | `dict[str, str] \| None`; default `None`; positional or keyword | Optional environment mapping; null normally selects process environment. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  91 | def mock_embeddings_allowed_from_env(env: dict[str, str] | None = None) -> bool:
  92 |     """True iff ``DOCUMIND_ALLOW_MOCK_EMBEDDINGS`` is explicitly enabled."""
  93 |     value = (env if env is not None else os.environ).get(MOCK_ENV_VAR, "")
  94 |     return value.strip().lower() in {"1", "true", "yes", "on"}
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L91 | Define `mock_embeddings_allowed_from_env`; bind its arguments when called. The body executes only when invoked. |
| L92 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L93 | Evaluate the right-hand side, then bind/store it in `value`: `(env if env is not None else os.environ).get(MOCK_ENV_VAR, '')` — Look up `MOCK_ENV_VAR` in `env if env is not None else os.environ`, using `''` when the key is absent (an existing null value is not replaced). |
| L94 | Compute the return value: compare whether `value.strip().lower()` is contained in `{'1', 'true', 'yes', 'on'}`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `EmbeddingConfig.__post_init__(self) -> None`

**Arguments:** Newly constructed frozen config. **Returns:** `None`. **Work:** Requires `provider` exactly `hf` or `jina`, raising `ValueError` otherwise. Direct construction does not normalize spelling or automatically switch model/dimension when only the provider is changed; `from_env` selects the coherent defaults.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-embeddingconfig---post-init--"></a>

#### Line-by-line execution

[Current source: lines 109–114](../../../../Backend/app/rag/embeddings.py#L109-L114). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 109 |     def __post_init__(self) -> None:
 110 |         if self.provider not in EMBEDDING_PROVIDERS:
 111 |             raise ValueError(
 112 |                 f"embedding provider must be one of {EMBEDDING_PROVIDERS!r}, "
 113 |                 f"got {self.provider!r}"
 114 |             )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L109 | Define `EmbeddingConfig.__post_init__`; bind its arguments when called. The body executes only when invoked. |
| L110 | Evaluate the branch condition: compare whether `self.provider` is absent from `EMBEDDING_PROVIDERS`. If truthy, enter L111; otherwise skip this indented block and continue after it. |
| L111 | Raise `ValueError(f'embedding provider must be one of {EMBEDDING_PROVIDERS!r}, got {self.provider!r}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L112 | Supply positional argument 1 to `ValueError`: format a string by inserting `EMBEDDING_PROVIDERS`, `self.provider` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L113 | Supply positional argument 1 to `ValueError`: format a string by inserting `EMBEDDING_PROVIDERS`, `self.provider` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L114 | Close the expression/container begun at L111; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `EmbeddingConfig.request_url(self) -> str` (property)

**Arguments:** Config instance. **Returns:** Explicit truthy `api_url`, or the provider URL. **Work:** Jina uses `https://api.jina.ai/v1/embeddings`; HF formats `https://router.huggingface.co/hf-inference/models/{model_id}/pipeline/feature-extraction`. Access performs no HTTP request.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-embeddingconfig-request-url"></a>

#### Line-by-line execution

[Current source: lines 116–120](../../../../Backend/app/rag/embeddings.py#L116-L120). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 116 |     @property
 117 |     def request_url(self) -> str:
 118 |         if self.provider == PROVIDER_JINA:
 119 |             return self.api_url or JINA_API_URL
 120 |         return self.api_url or f"{HF_API_BASE}/{self.model_id}/pipeline/feature-extraction"
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L116 | Expose this getter as an attribute; reading the property invokes the body instead of requiring an explicit method call. |
| L117 | Define `EmbeddingConfig.request_url`; bind its arguments when called. The body executes only when invoked. |
| L118 | Evaluate the branch condition: compare whether `self.provider` equals `PROVIDER_JINA`. If truthy, enter L119; otherwise skip this indented block and continue after it. |
| L119 | Compute the return value: evaluate `self.api_url or JINA_API_URL` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L120 | Compute the return value: evaluate `self.api_url or f'{HF_API_BASE}/{self.model_id}/pipeline/feature-extraction'` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `EmbeddingConfig.from_env(cls, env=None, *, allow_mock: bool | None = None) -> EmbeddingConfig`

**Arguments:** Class, optional settings mapping, optional explicit mock policy. **Returns:** Provider-appropriate frozen config. **Work:** Normalizes `DOCUMIND_EMBEDDING_PROVIDER` (default `hf`), rejects unsupported values, chooses Jina's model override `JINA_EMBEDDING_MODEL` and fixed 1024-d default or HF defaults. An explicit mock boolean wins; otherwise reads the opt-in variable. It does not load credentials or timeout/batch/URL overrides from this mapping.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-embeddingconfig-from-env"></a>

#### Line-by-line execution

[Current source: lines 122–153](../../../../Backend/app/rag/embeddings.py#L122-L153). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `cls` | not annotated; implicitly supplied/collected; positional or keyword | The class being constructed or validated; the classmethod descriptor supplies it. |
| `env` | `dict[str, str] \| None`; default `None`; positional or keyword | Optional environment mapping; null normally selects process environment. |
| `allow_mock` | `bool \| None`; default `None`; keyword-only | Explicit deterministic-vector opt-in, or null to consult configuration where implemented. |

**Declared result:** `'EmbeddingConfig'`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 122 |     @classmethod
 123 |     def from_env(
 124 |         cls,
 125 |         env: dict[str, str] | None = None,
 126 |         *,
 127 |         allow_mock: bool | None = None,
 128 |     ) -> "EmbeddingConfig":
 129 |         """Build from environment; mock mode only via explicit opt-in.
 130 | 
 131 |         ``DOCUMIND_EMBEDDING_PROVIDER`` selects ``hf`` (default) or
 132 |         ``jina``.  Jina reads ``JINA_EMBEDDING_MODEL`` (default
 133 |         ``jina-embeddings-v5-text-small``) and always uses 1024-d
 134 |         vectors.  ``allow_mock=None`` reads
 135 |         ``DOCUMIND_ALLOW_MOCK_EMBEDDINGS``; an explicit boolean wins.
 136 |         """
 137 |         source = env if env is not None else os.environ
 138 |         mock = mock_embeddings_allowed_from_env(source) if allow_mock is None else allow_mock
 139 |         provider = (source.get(EMBEDDING_PROVIDER_ENV_VAR) or PROVIDER_HF).strip().lower()
 140 |         if provider not in EMBEDDING_PROVIDERS:
 141 |             raise ValueError(
 142 |                 f"{EMBEDDING_PROVIDER_ENV_VAR} must be one of "
 143 |                 f"{EMBEDDING_PROVIDERS!r}, got {provider!r}"
 144 |             )
 145 |         if provider == PROVIDER_JINA:
 146 |             model_id = (source.get("JINA_EMBEDDING_MODEL") or JINA_EMBEDDING_MODEL).strip()
 147 |             return cls(
 148 |                 provider=PROVIDER_JINA,
 149 |                 model_id=model_id,
 150 |                 dim=JINA_EMBEDDING_DIM,
 151 |                 allow_mock=mock,
 152 |             )
 153 |         return cls(allow_mock=mock)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L122 | Bind the method to the class so Python supplies cls; decorators are applied bottom-up when the function is defined. |
| L123 | Define `EmbeddingConfig.from_env`; bind its arguments when called. The body executes only when invoked. |
| L124 | Declare parameter `cls` without a type annotation. The class being constructed or validated; the classmethod descriptor supplies it. |
| L125 | Declare parameter `env` with annotation `dict[str, str] \| None`. Optional environment mapping; null normally selects process environment. |
| L126 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L127 | Declare parameter `allow_mock` with annotation `bool \| None`. Explicit deterministic-vector opt-in, or null to consult configuration where implemented. |
| L128 | Finish/continue the signature; the declared return annotation is `'EmbeddingConfig'`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L129 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L131 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L132 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L133 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L134 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L135 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L136 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L137 | Evaluate the right-hand side, then bind/store it in `source`: check `env is not None`; when true use the current `env` value, otherwise the `environ` attribute of `os` (only the selected branch is evaluated). |
| L138 | Evaluate the right-hand side, then bind/store it in `mock`: check `allow_mock is None`; when true use `mock_embeddings_allowed_from_env(source)` — Call [mock_embeddings_allowed_from_env](#walk-mock-embeddings-allowed-from-env) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result, otherwise the current `allow_mock` value (only the selected branch is evaluated). |
| L139 | Evaluate the right-hand side, then bind/store it in `provider`: `(source.get(EMBEDDING_PROVIDER_ENV_VAR) or PROVIDER_HF).strip().lower()` — Return a lowercased string copy; first obtain the receiver: `(source.get(EMBEDDING_PROVIDER_ENV_VAR) or PROVIDER_HF).strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed. |
| L140 | Evaluate the branch condition: compare whether `provider` is absent from `EMBEDDING_PROVIDERS`. If truthy, enter L141; otherwise skip this indented block and continue after it. |
| L141 | Raise `ValueError(f'{EMBEDDING_PROVIDER_ENV_VAR} must be one of {EMBEDDING_PROVIDERS!r}, got {provider!r}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L142 | Supply positional argument 1 to `ValueError`: format a string by inserting `EMBEDDING_PROVIDER_ENV_VAR`, `EMBEDDING_PROVIDERS`, `provider` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L143 | Supply positional argument 1 to `ValueError`: format a string by inserting `EMBEDDING_PROVIDER_ENV_VAR`, `EMBEDDING_PROVIDERS`, `provider` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L144 | Close the expression/container begun at L141; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L145 | Evaluate the branch condition: compare whether `provider` equals `PROVIDER_JINA`. If truthy, enter L146; otherwise skip this indented block and continue after it. |
| L146 | Evaluate the right-hand side, then bind/store it in `model_id`: `(source.get('JINA_EMBEDDING_MODEL') or JINA_EMBEDDING_MODEL).strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed. |
| L147 | Compute the return value: `cls(provider=PROVIDER_JINA, model_id=model_id, dim=JINA_EMBEDDING_DIM, allow_mock=mock)` — Construct `cls` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L148 | Supply `provider` = `PROVIDER_JINA`.  Evaluate the value as: the current `PROVIDER_JINA` value. |
| L149 | Supply `model_id` = `model_id`.  Evaluate the value as: the current `model_id` value. |
| L150 | Supply `dim` = `JINA_EMBEDDING_DIM`. Required vector dimension (number of numeric components). Evaluate the value as: the current `JINA_EMBEDDING_DIM` value. |
| L151 | Supply `allow_mock` = `mock`. Explicit deterministic-vector opt-in, or null to consult configuration where implemented. Evaluate the value as: the current `mock` value. |
| L152 | Close the expression/container begun at L147; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L153 | Compute the return value: `cls(allow_mock=mock)` — Construct `cls` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `EmbeddingService.__init__(self, config=None, *, api_key: str | None = None, http_post=None) -> None`

**Arguments:** Optional config, credential override, injectable HTTP POST callable. **Returns:** `None`. **Work:** Defaults to `EmbeddingConfig()` (not `from_env()`), so callers select environment-based provider/mock mode explicitly. A supplied key, including an empty string, overrides environment lookup. Otherwise reads `JINA_API_KEY` for Jina or `HF_API_KEY` before `HF_TOKEN` for HF. Stores `http_post` or `httpx.post`; no request occurs.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-embeddingservice---init--"></a>

#### Line-by-line execution

[Current source: lines 169–185](../../../../Backend/app/rag/embeddings.py#L169-L185). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `config` | `EmbeddingConfig \| None`; default `None`; positional or keyword | Configuration object consumed by the field accesses below. |
| `api_key` | `str \| None`; default `None`; keyword-only | Server-side provider credential; do not expose it to browser configuration. |
| `http_post` | `HttpPost \| None`; default `None`; keyword-only | Optional HTTP POST callable used at the embedding-provider boundary. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 169 |     def __init__(
 170 |         self,
 171 |         config: EmbeddingConfig | None = None,
 172 |         *,
 173 |         api_key: str | None = None,
 174 |         http_post: HttpPost | None = None,
 175 |     ) -> None:
 176 |         self.config = config or EmbeddingConfig()
 177 |         if api_key is not None:
 178 |             self._api_key = api_key or None
 179 |         elif self.config.provider == PROVIDER_JINA:
 180 |             self._api_key = os.environ.get("JINA_API_KEY") or None
 181 |         else:
 182 |             self._api_key = (
 183 |                 os.environ.get("HF_API_KEY") or os.environ.get("HF_TOKEN") or None
 184 |             )
 185 |         self._http_post: HttpPost = http_post or httpx.post
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L169 | Define `EmbeddingService.__init__`; bind its arguments when called. The body executes only when invoked. |
| L170 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L171 | Declare parameter `config` with annotation `EmbeddingConfig \| None`. Configuration object consumed by the field accesses below. |
| L172 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L173 | Declare parameter `api_key` with annotation `str \| None`. Server-side provider credential; do not expose it to browser configuration. |
| L174 | Declare parameter `http_post` with annotation `HttpPost \| None`. Optional HTTP POST callable used at the embedding-provider boundary. |
| L175 | Finish/continue the signature; the declared return annotation is `None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L176 | Evaluate the right-hand side, then bind/store it in `self.config`: evaluate `config or EmbeddingConfig()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L177 | Evaluate the branch condition: compare whether `api_key` is not the same object as `None`. If truthy, enter L178; otherwise enter the alternative at L179. |
| L178 | Evaluate the right-hand side, then bind/store it in `self._api_key`: evaluate `api_key or None` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L179 | Evaluate the branch condition: compare whether `self.config.provider` equals `PROVIDER_JINA`. If truthy, enter L180; otherwise enter the alternative at L182. |
| L180 | Evaluate the right-hand side, then bind/store it in `self._api_key`: evaluate `os.environ.get('JINA_API_KEY') or None` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L181 | Enter this alternative only when the associated condition was false (or the associated try/loop completed without its exceptional exit). |
| L182 | Evaluate the right-hand side, then bind/store it in `self._api_key`: evaluate `os.environ.get('HF_API_KEY') or os.environ.get('HF_TOKEN') or None` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L183 | `os.environ.get('HF_API_KEY')` — Read a process environment value without changing it, using the supplied fallback if absent. |
| L184 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L185 | Evaluate the right-hand side, then bind/store it in `self._http_post`: evaluate `http_post or httpx.post` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |

<!-- END LINE WALKTHROUGH -->

### `EmbeddingService.allow_mock(self) -> bool` (property)

**Arguments:** Service instance. **Returns:** `config.allow_mock`. **Work:** Directly exposes the configured policy; no environment reread.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-embeddingservice-allow-mock"></a>

#### Line-by-line execution

[Current source: lines 187–189](../../../../Backend/app/rag/embeddings.py#L187-L189). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 187 |     @property
 188 |     def allow_mock(self) -> bool:
 189 |         return self.config.allow_mock
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L187 | Expose this getter as an attribute; reading the property invokes the body instead of requiring an explicit method call. |
| L188 | Define `EmbeddingService.allow_mock`; bind its arguments when called. The body executes only when invoked. |
| L189 | Compute the return value: the `allow_mock` attribute of `self.config`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `EmbeddingService.embed_texts(self, texts: Sequence[str], *, task: str | None = None) -> list[list[float]]`

- **Arguments:** Ordered texts and optional Jina retrieval adapter hint.
- **Returns:** One vector per text in input order; `[]` for empty input.
- **Work:** Materializes the sequence. Mock mode maps each text through the deterministic helper at the configured dimension without HTTP. Otherwise clamps batch size to at least 1, processes batches serially with `_embed_batch`, and concatenates results. A failing batch aborts the call rather than returning earlier partial results. Jina defaults to `retrieval.passage`; question callers supply `retrieval.query`; HF ignores the hint.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-embeddingservice-embed-texts"></a>

#### Line-by-line execution

[Current source: lines 191–220](../../../../Backend/app/rag/embeddings.py#L191-L220). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `texts` | `Sequence[str]`; required; positional or keyword | Input text sequence; embedding output preserves its order. |
| `task` | `str \| None`; default `None`; keyword-only | Jina retrieval adapter hint: passage for documents, query for questions; HF ignores it. |

**Declared result:** `list[list[float]]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 191 |     def embed_texts(
 192 |         self,
 193 |         texts: Sequence[str],
 194 |         *,
 195 |         task: str | None = None,
 196 |     ) -> list[list[float]]:
 197 |         """Embed ``texts`` in batches of ``config.batch_size``.
 198 | 
 199 |         Returns one vector per input, in order.  Raises
 200 |         :class:`EmbeddingProviderError` on any provider failure (unless
 201 |         mock mode is enabled, in which case the provider is not called).
 202 | 
 203 |         ``task`` is a Jina retrieval adapter hint: ``retrieval.passage``
 204 |         (the default) for indexed chunks, ``retrieval.query`` for
 205 |         questions.  Hugging Face ignores it.
 206 |         """
 207 |         items = list(texts)
 208 |         if not items:
 209 |             return []
 210 |         if self.config.allow_mock:
 211 |             return [
 212 |                 deterministic_fallback_embedding(text, dim=self.config.dim) for text in items
 213 |             ]
 214 |         embeddings: list[list[float]] = []
 215 |         batch_size = max(1, self.config.batch_size)
 216 |         for start in range(0, len(items), batch_size):
 217 |             embeddings.extend(
 218 |                 self._embed_batch(items[start : start + batch_size], task=task)
 219 |             )
 220 |         return embeddings
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L191 | Define `EmbeddingService.embed_texts`; bind its arguments when called. The body executes only when invoked. |
| L192 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L193 | Declare parameter `texts` with annotation `Sequence[str]`. Input text sequence; embedding output preserves its order. |
| L194 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L195 | Declare parameter `task` with annotation `str \| None`. Jina retrieval adapter hint: passage for documents, query for questions; HF ignores it. |
| L196 | Finish/continue the signature; the declared return annotation is `list[list[float]]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L197 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L199 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L200 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L201 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L203 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L204 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L205 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L206 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L207 | Evaluate the right-hand side, then bind/store it in `items`: `list(texts)` — Materialize the iterable in order into a list (or create an empty list). |
| L208 | Evaluate the branch condition: invert the truthiness of `items`. If truthy, enter L209; otherwise skip this indented block and continue after it. |
| L209 | Compute the return value: build a list containing no items. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L210 | Evaluate the branch condition: the `allow_mock` attribute of `self.config`. If truthy, enter L211; otherwise skip this indented block and continue after it. |
| L211 | Compute the return value: iterate `items`, binding each item to `text`; produce `deterministic_fallback_embedding(text, dim=self.config.dim)` into a new list. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L212 | `deterministic_fallback_embedding(text, dim=self.config.dim)` — Call [deterministic_fallback_embedding](#walk-deterministic-fallback-embedding) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L213 | Close the expression/container begun at L211; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L214 | Evaluate the right-hand side, then bind/store it in `embeddings`: build a list containing no items. |
| L215 | Evaluate the right-hand side, then bind/store it in `batch_size`: `max(1, self.config.batch_size)` — Choose the largest supplied value; nested min/max calls implement the stated bound. |
| L216 | Iterate `range(0, len(items), batch_size)` (`range(0, len(items), batch_size)` — Generate integer positions from the start up to, but excluding, the stop, using the supplied step; inputs include `len(items)` — Count the items/characters in the supplied container/string), assigning each item to `start`. Execute the indented body once per item; an empty iterable skips it. |
| L217 | `embeddings.extend(self._embed_batch(items[start:start + batch_size], task=task))` — Append every item from the supplied iterable to the list in order; inputs include `self._embed_batch(items[start:start + batch_size], task=task)` — Call [EmbeddingService._embed_batch](#walk-embeddingservice--embed-batch) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L218 | `self._embed_batch(items[start:start + batch_size], task=task)` — Call [EmbeddingService._embed_batch](#walk-embeddingservice--embed-batch) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L219 | Close the expression/container begun at L217; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L220 | Compute the return value: the current `embeddings` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `EmbeddingService._embed_batch(self, batch: list[str], *, task=None) -> list[list[float]]`

**Arguments:** One text batch and task hint. **Returns:** Provider vectors. **Work:** Dispatches to `_embed_jina_batch` for Jina, otherwise `_embed_hf_batch`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-embeddingservice--embed-batch"></a>

#### Line-by-line execution

[Current source: lines 222–227](../../../../Backend/app/rag/embeddings.py#L222-L227). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `batch` | `list[str]`; required; positional or keyword | Caller-supplied batch; each read, transformation, and validation is traced below. |
| `task` | `str \| None`; default `None`; keyword-only | Jina retrieval adapter hint: passage for documents, query for questions; HF ignores it. |

**Declared result:** `list[list[float]]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 222 |     def _embed_batch(
 223 |         self, batch: list[str], *, task: str | None = None
 224 |     ) -> list[list[float]]:
 225 |         if self.config.provider == PROVIDER_JINA:
 226 |             return self._embed_jina_batch(batch, task=task)
 227 |         return self._embed_hf_batch(batch)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L222 | Define `EmbeddingService._embed_batch`; bind its arguments when called. The body executes only when invoked. |
| L223 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `batch` with annotation `list[str]`. Caller-supplied batch; its uses and transformations are traced below. Declare parameter `task` with annotation `str \| None`. Jina retrieval adapter hint: passage for documents, query for questions; HF ignores it. |
| L224 | Finish/continue the signature; the declared return annotation is `list[list[float]]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L225 | Evaluate the branch condition: compare whether `self.config.provider` equals `PROVIDER_JINA`. If truthy, enter L226; otherwise skip this indented block and continue after it. |
| L226 | Compute the return value: `self._embed_jina_batch(batch, task=task)` — Call [EmbeddingService._embed_jina_batch](#walk-embeddingservice--embed-jina-batch) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L227 | Compute the return value: `self._embed_hf_batch(batch)` — Call [EmbeddingService._embed_hf_batch](#walk-embeddingservice--embed-hf-batch) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `EmbeddingService._embed_hf_batch(self, batch: list[str]) -> list[list[float]]`

**Arguments:** Text batch. **Returns:** Validated vectors. **Work:** Posts `{"inputs": batch, "options": {"wait_for_model": true}}`, then validates the response as an exact-length list of configured-dimension vectors.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-embeddingservice--embed-hf-batch"></a>

#### Line-by-line execution

[Current source: lines 229–231](../../../../Backend/app/rag/embeddings.py#L229-L231). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `batch` | `list[str]`; required; positional or keyword | Caller-supplied batch; each read, transformation, and validation is traced below. |

**Declared result:** `list[list[float]]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 229 |     def _embed_hf_batch(self, batch: list[str]) -> list[list[float]]:
 230 |         payload = self._post({"inputs": batch, "options": {"wait_for_model": True}})
 231 |         return self._validate(payload, expected=len(batch))
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L229 | Define `EmbeddingService._embed_hf_batch`; bind its arguments when called. The body executes only when invoked. |
| L230 | Evaluate the right-hand side, then bind/store it in `payload`: `self._post({'inputs': batch, 'options': {'wait_for_model': True}})` — Call [EmbeddingService._post](#walk-embeddingservice--post) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L231 | Compute the return value: `self._validate(payload, expected=len(batch))` — Call [EmbeddingService._validate](#walk-embeddingservice--validate) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `EmbeddingService._embed_jina_batch(self, batch: list[str], *, task=None) -> list[list[float]]`

**Arguments:** Text batch and adapter hint. **Returns:** Ordered validated Jina vectors. **Work:** Requires a configured API key, then posts model/input/task/dimensions with `normalized=True`. Defaults the task to passage mode and sends the result through `_validate_jina`. Missing key raises `EmbeddingProviderError` before HTTP.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-embeddingservice--embed-jina-batch"></a>

#### Line-by-line execution

[Current source: lines 233–249](../../../../Backend/app/rag/embeddings.py#L233-L249). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `batch` | `list[str]`; required; positional or keyword | Caller-supplied batch; each read, transformation, and validation is traced below. |
| `task` | `str \| None`; default `None`; keyword-only | Jina retrieval adapter hint: passage for documents, query for questions; HF ignores it. |

**Declared result:** `list[list[float]]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 233 |     def _embed_jina_batch(
 234 |         self, batch: list[str], *, task: str | None = None
 235 |     ) -> list[list[float]]:
 236 |         if not self._api_key:
 237 |             raise EmbeddingProviderError(
 238 |                 "JINA_API_KEY is not configured for the jina embedding provider"
 239 |             )
 240 |         payload = self._post(
 241 |             {
 242 |                 "model": self.config.model_id,
 243 |                 "input": batch,
 244 |                 "task": task or TASK_RETRIEVAL_PASSAGE,
 245 |                 "dimensions": self.config.dim,
 246 |                 "normalized": True,
 247 |             }
 248 |         )
 249 |         return self._validate_jina(payload, expected=len(batch))
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L233 | Define `EmbeddingService._embed_jina_batch`; bind its arguments when called. The body executes only when invoked. |
| L234 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `batch` with annotation `list[str]`. Caller-supplied batch; its uses and transformations are traced below. Declare parameter `task` with annotation `str \| None`. Jina retrieval adapter hint: passage for documents, query for questions; HF ignores it. |
| L235 | Finish/continue the signature; the declared return annotation is `list[list[float]]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L236 | Evaluate the branch condition: invert the truthiness of `self._api_key`. If truthy, enter L237; otherwise skip this indented block and continue after it. |
| L237 | Raise `EmbeddingProviderError('JINA_API_KEY is not configured for the jina embedding provider')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L238 | Supply positional argument 1 to `EmbeddingProviderError`: `'JINA_API_KEY is not configured for the jina embedding provider'`. |
| L239 | Close the expression/container begun at L237; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L240 | Evaluate the right-hand side, then bind/store it in `payload`: `self._post({'model': self.config.model_id, 'input': batch, 'task': task or TASK_RETRIEVAL_PASSAGE, 'dimensions': self.config.dim, 'normalized': True})` — Call [EmbeddingService._post](#walk-embeddingservice--post) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L241 | Supply positional argument 1 to `self._post`: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. |
| L242 | Add mapping entry `'model'`: the `model_id` attribute of `self.config`. |
| L243 | Add mapping entry `'input'`: the current `batch` value. |
| L244 | Add mapping entry `'task'`: evaluate `task or TASK_RETRIEVAL_PASSAGE` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L245 | Add mapping entry `'dimensions'`: the `dim` attribute of `self.config`. |
| L246 | Add mapping entry `'normalized'`: `True`. |
| L247 | Close the expression/container begun at L241; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L248 | Close the expression/container begun at L240; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L249 | Compute the return value: `self._validate_jina(payload, expected=len(batch))` — Call [EmbeddingService._validate_jina](#walk-embeddingservice--validate-jina) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `EmbeddingService._post(self, payload: dict[str, object]) -> object`

**Arguments:** Provider JSON request body. **Returns:** Parsed response JSON. **Work:** Adds Bearer auth only when a key exists and invokes the configured POST with request URL and timeout. Requires HTTP **200** exactly. Transport errors, other statuses (with up to 300 response-text characters), and JSON decoding failures become `EmbeddingProviderError` with the cause retained. This function does not internally retry.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-embeddingservice--post"></a>

#### Line-by-line execution

[Current source: lines 251–273](../../../../Backend/app/rag/embeddings.py#L251-L273). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `payload` | `dict[str, object]`; required; positional or keyword | Input mapping, DTO, or provider response; the annotated type and body identify its expected shape. |

**Declared result:** `object`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 251 |     def _post(self, payload: dict[str, object]) -> object:
 252 |         headers: dict[str, str] = {}
 253 |         if self._api_key:
 254 |             headers["Authorization"] = f"Bearer {self._api_key}"
 255 |         try:
 256 |             response = self._http_post(
 257 |                 self.config.request_url,
 258 |                 headers=headers,
 259 |                 json=payload,
 260 |                 timeout=self.config.timeout_seconds,
 261 |             )
 262 |         except Exception as exc:
 263 |             raise EmbeddingProviderError(f"embedding provider request failed: {exc}") from exc
 264 |         if response.status_code != 200:
 265 |             detail = str(getattr(response, "text", "") or "").strip()
 266 |             suffix = f": {detail[:300]}" if detail else ""
 267 |             raise EmbeddingProviderError(
 268 |                 f"embedding provider returned HTTP {response.status_code}{suffix}"
 269 |             )
 270 |         try:
 271 |             return response.json()
 272 |         except Exception as exc:
 273 |             raise EmbeddingProviderError(f"embedding provider returned invalid JSON: {exc}") from exc
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L251 | Define `EmbeddingService._post`; bind its arguments when called. The body executes only when invoked. |
| L252 | Evaluate the right-hand side, then bind/store it in `headers`: create an empty dictionary. |
| L253 | Evaluate the branch condition: the `_api_key` attribute of `self`. If truthy, enter L254; otherwise skip this indented block and continue after it. |
| L254 | Evaluate the right-hand side, then bind/store it in `headers['Authorization']`: format a string by inserting `self._api_key` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L255 | Enter the protected block; failures are matched against `Exception` in order. |
| L256 | Evaluate the right-hand side, then bind/store it in `response`: `self._http_post(self.config.request_url, headers=headers, json=payload, timeout=self.config.timeout_seconds)` — Call the injected/default synchronous HTTP POST transport with this URL, JSON, headers, and timeout. |
| L257 | Supply positional argument 1 to `self._http_post`: the `request_url` attribute of `self.config`. |
| L258 | Supply `headers` = `headers`.  Evaluate the value as: the current `headers` value. |
| L259 | Supply `json` = `payload`.  Evaluate the value as: the current `payload` value. |
| L260 | Supply `timeout` = `self.config.timeout_seconds`.  Evaluate the value as: the `timeout_seconds` attribute of `self.config`. |
| L261 | Close the expression/container begun at L256; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L262 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L263 | Raise `EmbeddingProviderError(f'embedding provider request failed: {exc}')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L264 | Evaluate the branch condition: compare whether `response.status_code` differs from `200`. If truthy, enter L265; otherwise skip this indented block and continue after it. |
| L265 | Evaluate the right-hand side, then bind/store it in `detail`: `str(getattr(response, 'text', '') or '').strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed; first obtain the receiver: `str(getattr(response, 'text', '') or '')` — Convert the input to its string representation. |
| L266 | Evaluate the right-hand side, then bind/store it in `suffix`: check `detail`; when true use format a string by inserting `detail[:300]` into the literal text; !r uses repr, and this formatting does not escape or redact values, otherwise `''` (only the selected branch is evaluated). |
| L267 | Raise `EmbeddingProviderError(f'embedding provider returned HTTP {response.status_code}{suffix}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L268 | Supply positional argument 1 to `EmbeddingProviderError`: format a string by inserting `response.status_code`, `suffix` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L269 | Close the expression/container begun at L267; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L270 | Enter the protected block; failures are matched against `Exception` in order. |
| L271 | Compute the return value: `response.json()` — Decode the HTTP response body as JSON; invalid JSON raises. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L272 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L273 | Raise `EmbeddingProviderError(f'embedding provider returned invalid JSON: {exc}')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |

<!-- END LINE WALKTHROUGH -->

### `EmbeddingService._validate_jina(self, payload: object, *, expected: int) -> list[list[float]]`

**Arguments:** OpenAI-shaped provider response and required vector count. **Returns:** Vectors reordered by each entry's `index`. **Work:** Requires an object with an exact-length `data` list of objects. Index defaults to list position; rejects non-integers/booleans/out-of-range positions, occupied duplicate slots, and missing vectors. Passes the ordered embeddings to `_validate` for dimensions/numerics.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-embeddingservice--validate-jina"></a>

#### Line-by-line execution

[Current source: lines 275–307](../../../../Backend/app/rag/embeddings.py#L275-L307). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `payload` | `object`; required; positional or keyword | Input mapping, DTO, or provider response; the annotated type and body identify its expected shape. |
| `expected` | `int`; required; keyword-only | Required number of embedding vectors in the provider result. |

**Declared result:** `list[list[float]]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 275 |     def _validate_jina(self, payload: object, *, expected: int) -> list[list[float]]:
 276 |         """Validate Jina's OpenAI-shaped ``{"data": [{"index", "embedding"}]}``."""
 277 |         if not isinstance(payload, dict):
 278 |             raise EmbeddingProviderError(
 279 |                 f"embedding provider returned {type(payload).__name__}, expected an object"
 280 |             )
 281 |         data = payload.get("data")
 282 |         if not isinstance(data, list) or len(data) != expected:
 283 |             count = len(data) if isinstance(data, list) else "n/a"
 284 |             raise EmbeddingProviderError(
 285 |                 f"embedding provider returned {count} vectors, expected {expected}"
 286 |             )
 287 |         ordered: list[object] = [None] * expected
 288 |         for position, item in enumerate(data):
 289 |             if not isinstance(item, dict):
 290 |                 raise EmbeddingProviderError(
 291 |                     "embedding provider returned a non-object data item"
 292 |                 )
 293 |             index = item.get("index", position)
 294 |             if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < expected:
 295 |                 raise EmbeddingProviderError(
 296 |                     f"embedding provider returned an invalid vector index {index!r}"
 297 |                 )
 298 |             if ordered[index] is not None:
 299 |                 raise EmbeddingProviderError(
 300 |                     f"embedding provider returned duplicate vector index {index}"
 301 |                 )
 302 |             ordered[index] = item.get("embedding")
 303 |         if any(vector is None for vector in ordered):
 304 |             raise EmbeddingProviderError(
 305 |                 "embedding provider returned fewer vectors than requested"
 306 |             )
 307 |         return self._validate(ordered, expected=expected)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L275 | Define `EmbeddingService._validate_jina`; bind its arguments when called. The body executes only when invoked. |
| L276 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L277 | Evaluate the branch condition: invert the truthiness of `isinstance(payload, dict)`. If truthy, enter L278; otherwise skip this indented block and continue after it. |
| L278 | Raise `EmbeddingProviderError(f'embedding provider returned {type(payload).__name__}, expected an object')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L279 | Read the runtime class of the supplied value. |
| L280 | Close the expression/container begun at L278; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L281 | Evaluate the right-hand side, then bind/store it in `data`: `payload.get('data')` — Look up `'data'` in `payload`, using None when the key is absent (an existing null value is not replaced). |
| L282 | Evaluate the branch condition: evaluate `not isinstance(data, list) or len(data) != expected` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L283; otherwise skip this indented block and continue after it. |
| L283 | Evaluate the right-hand side, then bind/store it in `count`: check `isinstance(data, list)`; when true use `len(data)` — Count the items/characters in the supplied container/string, otherwise `'n/a'` (only the selected branch is evaluated). |
| L284 | Raise `EmbeddingProviderError(f'embedding provider returned {count} vectors, expected {expected}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L285 | Supply positional argument 1 to `EmbeddingProviderError`: format a string by inserting `count`, `expected` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L286 | Close the expression/container begun at L284; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L287 | Evaluate the right-hand side, then bind/store it in `ordered`: multiply/repeat `[None]` and `expected`, following the parentheses/operator precedence shown in `[None] * expected`. |
| L288 | Iterate `enumerate(data)` (`enumerate(data)` — Yield an index and each input item in order; the optional second argument sets the starting index), assigning each item to `(position, item)`. Execute the indented body once per item; an empty iterable skips it. |
| L289 | Evaluate the branch condition: invert the truthiness of `isinstance(item, dict)`. If truthy, enter L290; otherwise skip this indented block and continue after it. |
| L290 | Raise `EmbeddingProviderError('embedding provider returned a non-object data item')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L291 | Supply positional argument 1 to `EmbeddingProviderError`: `'embedding provider returned a non-object data item'`. |
| L292 | Close the expression/container begun at L290; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L293 | Evaluate the right-hand side, then bind/store it in `index`: `item.get('index', position)` — Look up `'index'` in `item`, using `position` when the key is absent (an existing null value is not replaced). |
| L294 | Evaluate the branch condition: evaluate `not isinstance(index, int) or isinstance(index, bool) or (not 0 <= index < expected)` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L295; otherwise skip this indented block and continue after it. |
| L295 | Raise `EmbeddingProviderError(f'embedding provider returned an invalid vector index {index!r}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L296 | Supply positional argument 1 to `EmbeddingProviderError`: format a string by inserting `index` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L297 | Close the expression/container begun at L295; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L298 | Evaluate the branch condition: compare whether `ordered[index]` is not the same object as `None`. If truthy, enter L299; otherwise skip this indented block and continue after it. |
| L299 | Raise `EmbeddingProviderError(f'embedding provider returned duplicate vector index {index}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L300 | Supply positional argument 1 to `EmbeddingProviderError`: format a string by inserting `index` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L301 | Close the expression/container begun at L299; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L302 | Evaluate the right-hand side, then bind/store it in `ordered[index]`: `item.get('embedding')` — Look up `'embedding'` in `item`, using None when the key is absent (an existing null value is not replaced). |
| L303 | Evaluate the branch condition: `any((vector is None for vector in ordered))` — Evaluate the iterable lazily, stopping at the first truthy item (True); empty input gives False; inputs include iterate `ordered`, binding each item to `vector`; produce `vector is None` into a lazy generator (items computed when consumed). If truthy, enter L304; otherwise skip this indented block and continue after it. |
| L304 | Raise `EmbeddingProviderError('embedding provider returned fewer vectors than requested')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L305 | Supply positional argument 1 to `EmbeddingProviderError`: `'embedding provider returned fewer vectors than requested'`. |
| L306 | Close the expression/container begun at L304; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L307 | Compute the return value: `self._validate(ordered, expected=expected)` — Call [EmbeddingService._validate](#walk-embeddingservice--validate) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `EmbeddingService._validate(self, payload: object, *, expected: int) -> list[list[float]]`

**Arguments:** Candidate list of vectors and required count. **Returns:** New vectors of finite floats. **Work:** Requires a list with exact count, each vector a list/tuple with `config.dim` entries, converts components with `float`, and requires `math.isfinite` for every value. Numeric strings/booleans can coerce to floats; nonnumeric/nonfinite/wrong-shape values raise `EmbeddingProviderError`. It does not normalize provider vectors or enforce semantic quality.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-embeddingservice--validate"></a>

#### Line-by-line execution

[Current source: lines 309–330](../../../../Backend/app/rag/embeddings.py#L309-L330). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `payload` | `object`; required; positional or keyword | Input mapping, DTO, or provider response; the annotated type and body identify its expected shape. |
| `expected` | `int`; required; keyword-only | Required number of embedding vectors in the provider result. |

**Declared result:** `list[list[float]]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 309 |     def _validate(self, payload: object, *, expected: int) -> list[list[float]]:
 310 |         dim = self.config.dim
 311 |         if not isinstance(payload, list) or len(payload) != expected:
 312 |             raise EmbeddingProviderError(
 313 |                 f"embedding provider returned {type(payload).__name__} "
 314 |                 f"of length {len(payload) if isinstance(payload, list) else 'n/a'}, "
 315 |                 f"expected {expected}"
 316 |             )
 317 |         vectors: list[list[float]] = []
 318 |         for vector in payload:
 319 |             if not isinstance(vector, (list, tuple)) or len(vector) != dim:
 320 |                 raise EmbeddingProviderError(
 321 |                     f"embedding vector must have {dim} dimensions"
 322 |                 )
 323 |             try:
 324 |                 values = [float(component) for component in vector]
 325 |             except (TypeError, ValueError) as exc:
 326 |                 raise EmbeddingProviderError("embedding vector has non-numeric values") from exc
 327 |             if not all(math.isfinite(value) for value in values):
 328 |                 raise EmbeddingProviderError("embedding vector has non-finite values")
 329 |             vectors.append(values)
 330 |         return vectors
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L309 | Define `EmbeddingService._validate`; bind its arguments when called. The body executes only when invoked. |
| L310 | Evaluate the right-hand side, then bind/store it in `dim`: the `dim` attribute of `self.config`. |
| L311 | Evaluate the branch condition: evaluate `not isinstance(payload, list) or len(payload) != expected` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L312; otherwise skip this indented block and continue after it. |
| L312 | Raise `EmbeddingProviderError(f"embedding provider returned {type(payload).__name__} of length {(len(payload) if isinstance(payload, list) else 'n/a')}, expected {expected}")`; stop the normal path and transfer control to the nearest matching exception handler. |
| L313 | Read the runtime class of the supplied value. |
| L314 | Check the runtime type against the supplied class or tuple of classes. |
| L315 | Supply positional argument 1 to `EmbeddingProviderError`: format a string by inserting `type(payload).__name__`, `len(payload) if isinstance(payload, list) else 'n/a'`, `expected` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L316 | Close the expression/container begun at L312; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L317 | Evaluate the right-hand side, then bind/store it in `vectors`: build a list containing no items. |
| L318 | Iterate `payload` (the current `payload` value), assigning each item to `vector`. Execute the indented body once per item; an empty iterable skips it. |
| L319 | Evaluate the branch condition: evaluate `not isinstance(vector, (list, tuple)) or len(vector) != dim` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L320; otherwise skip this indented block and continue after it. |
| L320 | Raise `EmbeddingProviderError(f'embedding vector must have {dim} dimensions')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L321 | Supply positional argument 1 to `EmbeddingProviderError`: format a string by inserting `dim` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L322 | Close the expression/container begun at L320; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L323 | Enter the protected block; failures are matched against `(TypeError, ValueError)` in order. |
| L324 | Evaluate the right-hand side, then bind/store it in `values`: iterate `vector`, binding each item to `component`; produce `float(component)` into a new list. |
| L325 | Handle `(TypeError, ValueError)` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L326 | Raise `EmbeddingProviderError('embedding vector has non-numeric values')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L327 | Evaluate the branch condition: invert the truthiness of `all((math.isfinite(value) for value in values))`. If truthy, enter L328; otherwise skip this indented block and continue after it. |
| L328 | Raise `EmbeddingProviderError('embedding vector has non-finite values')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L329 | `vectors.append(values)` — Append one object to the mutable list in place. The return value is not assigned here. |
| L330 | Compute the return value: the current `vectors` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
