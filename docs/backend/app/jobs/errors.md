# `app/jobs/errors.py`

[Source](../../../../Backend/app/jobs/errors.py) · [Backend index](../../README.md)

Stable job failure categories and deterministic capped retry delays.

| Policy | Codes |
| --- | --- |
| Terminal | `file_too_large`, `page_limit_exceeded`, `pdf_malformed`, `pdf_textless`, `fingerprint_mismatch`, `storage_missing`, `upload_incomplete`, `document_deleted` |
| Retryable | `storage_unavailable`, `embedding_provider_unavailable`, `index_write_failed`, `lease_expired`, `job_timeout`, `unexpected` |

`ALL_ERROR_CODES` is their union; `TERMINAL_ERROR_CODES` contains the first group; `RETRYABLE_ERROR_CODES` is the set difference. Constants are uppercase `ERROR_*` names (`ERROR_EMBEDDING_PROVIDER`, `ERROR_INDEX_WRITE` for those two longer code strings). `ERROR_JOB_TIMEOUT` is defined but not listed in `__all__`.

## Functions

### `JobError.__init__(self, code: str, message: str, *, detail: str | None = None) -> None`

**Arguments:** Known code, diagnostic summary, optional internal detail. **Returns:** `None`. **Work:** Rejects unknown codes with `ValueError`, initializes `Exception`, and stores code/message/detail. It does not itself truncate or redact either string; caller-side classification supplies safe summaries.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-joberror---init--"></a>

#### Line-by-line execution

[Current source: lines 85–97](../../../../Backend/app/jobs/errors.py#L85-L97). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `code` | `str`; required; positional or keyword | Caller-supplied code; each read, transformation, and validation is traced below. |
| `message` | `str`; required; positional or keyword | Caller-supplied message; each read, transformation, and validation is traced below. |
| `detail` | `str \| None`; default `None`; keyword-only | Caller-supplied detail; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  85 |     def __init__(
  86 |         self,
  87 |         code: str,
  88 |         message: str,
  89 |         *,
  90 |         detail: str | None = None,
  91 |     ) -> None:
  92 |         if code not in ALL_ERROR_CODES:
  93 |             raise ValueError(f"unknown job error code: {code!r}")
  94 |         super().__init__(message)
  95 |         self.code = code
  96 |         self.message = message
  97 |         self.detail = detail
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L85 | Define `JobError.__init__`; bind its arguments when called. The body executes only when invoked. |
| L86 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L87 | Declare parameter `code` with annotation `str`. Caller-supplied code; its uses and transformations are traced below. |
| L88 | Declare parameter `message` with annotation `str`. Caller-supplied message; its uses and transformations are traced below. |
| L89 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L90 | Declare parameter `detail` with annotation `str \| None`. Caller-supplied detail; its uses and transformations are traced below. |
| L91 | Finish/continue the signature; the declared return annotation is `None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L92 | Evaluate the branch condition: compare whether `code` is absent from `ALL_ERROR_CODES`. If truthy, enter L93; otherwise skip this indented block and continue after it. |
| L93 | Raise `ValueError(f'unknown job error code: {code!r}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L94 | `super().__init__(message)` — Initialize the base exception/object with the supplied arguments; first obtain the receiver: `super()` — Resolve the superclass proxy for the current method and instance. The return value is not assigned here. |
| L95 | Evaluate the right-hand side, then bind/store it in `self.code`: the current `code` value. |
| L96 | Evaluate the right-hand side, then bind/store it in `self.message`: the current `message` value. |
| L97 | Evaluate the right-hand side, then bind/store it in `self.detail`: the current `detail` value. |

<!-- END LINE WALKTHROUGH -->

### `JobError.retryable(self) -> bool` (property)

**Arguments:** Classified error. **Returns:** Whether its code belongs to `RETRYABLE_ERROR_CODES`. **Work:** Set membership prevents callers from independently overriding retryability on this object.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-joberror-retryable"></a>

#### Line-by-line execution

[Current source: lines 99–101](../../../../Backend/app/jobs/errors.py#L99-L101). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  99 |     @property
 100 |     def retryable(self) -> bool:
 101 |         return self.code in RETRYABLE_ERROR_CODES
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L99 | Expose this getter as an attribute; reading the property invokes the body instead of requiring an explicit method call. |
| L100 | Define `JobError.retryable`; bind its arguments when called. The body executes only when invoked. |
| L101 | Compute the return value: compare whether `self.code` is contained in `RETRYABLE_ERROR_CODES`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `JobError.__repr__(self) -> str`

**Arguments:** Error instance. **Returns:** `JobError(code=..., message=...)` using `repr` formatting. **Work:** Exposes code/message for diagnostics and omits `.detail`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-joberror---repr--"></a>

#### Line-by-line execution

[Current source: lines 103–104](../../../../Backend/app/jobs/errors.py#L103-L104). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 103 |     def __repr__(self) -> str:  # pragma: no cover - debugging aid
 104 |         return f"JobError(code={self.code!r}, message={self.message!r})"
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L103 | Define `JobError.__repr__`; bind its arguments when called. The body executes only when invoked. |
| L104 | Compute the return value: format a string by inserting `self.code`, `self.message` into the literal text; !r uses repr, and this formatting does not escape or redact values. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `safe_message(exc: BaseException, *, limit: int = 500) -> str`

**Arguments:** Exception and desired character limit. **Returns:** Single-line flattened/truncated exception text, or exception class name if empty. **Work:** Joins `str(exc).split()` with spaces; if too long, takes `limit-3` characters and appends `...`. It is a formatting helper, **not credential redaction**; supplied exception text still determines content. The limit is not validated.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-safe-message"></a>

#### Line-by-line execution

[Current source: lines 107–116](../../../../Backend/app/jobs/errors.py#L107-L116). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `exc` | `BaseException`; required; positional or keyword | Caller-supplied exc; each read, transformation, and validation is traced below. |
| `limit` | `int`; default `500`; keyword-only | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 107 | def safe_message(exc: BaseException, *, limit: int = 500) -> str:
 108 |     """Bounded, single-line summary of an unexpected exception for logs/DB.
 109 | 
 110 |     Never includes tokens/credentials: callers pass provider exceptions
 111 |     whose ``str()`` may be long; this truncates and flattens whitespace.
 112 |     """
 113 |     text = " ".join(str(exc).split())
 114 |     if len(text) > limit:
 115 |         text = text[: limit - 3] + "..."
 116 |     return text or type(exc).__name__
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L107 | Define `safe_message`; bind its arguments when called. The body executes only when invoked. |
| L108 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L110 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L111 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L112 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L113 | Evaluate the right-hand side, then bind/store it in `text`: `' '.join(str(exc).split())` — Join the supplied string items using `' '` between adjacent items; inputs include `str(exc).split()` — Split the string into components; without an explicit separator, runs of whitespace are collapsed; first obtain the receiver: `str(exc)` — Convert the input to its string representation. |
| L114 | Evaluate the branch condition: compare whether `len(text)` is greater than `limit`. If truthy, enter L115; otherwise skip this indented block and continue after it. |
| L115 | Evaluate the right-hand side, then bind/store it in `text`: add/concatenate `text[:limit - 3]` and `'...'`, following the parentheses/operator precedence shown in `text[:limit - 3] + '...'`. |
| L116 | Compute the return value: evaluate `text or type(exc).__name__` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `compute_backoff_seconds(attempt: int, *, base_seconds=5, cap_seconds=3600, jitter_seed="") -> int`

**Arguments:** Just-finished attempt count, base delay, upper cap, optional stable seed (normally job UUID string). **Returns:** Capped delay in seconds. **Work:** Computes `base * 2**max(0, attempt-1)`. For a nonempty seed, hashes UTF-8 text with SHA-256 and adds `int(first_8_hex_digits, 16) % max(1, base)`, then caps with `min(delay, cap)`. Defaults produce 5, 10, 20… seconds before deterministic jitter. There is no sleep, PRNG state, or runtime validation of custom base/cap values.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-compute-backoff-seconds"></a>

#### Line-by-line execution

[Current source: lines 119–140](../../../../Backend/app/jobs/errors.py#L119-L140). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `attempt` | `int`; required; positional or keyword | Caller-supplied attempt; each read, transformation, and validation is traced below. |
| `base_seconds` | `int`; default `5`; keyword-only | Caller-supplied base seconds; each read, transformation, and validation is traced below. |
| `cap_seconds` | `int`; default `3600`; keyword-only | Caller-supplied cap seconds; each read, transformation, and validation is traced below. |
| `jitter_seed` | `str`; default `''`; keyword-only | Caller-supplied jitter seed; each read, transformation, and validation is traced below. |

**Declared result:** `int`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 119 | def compute_backoff_seconds(
 120 |     attempt: int,
 121 |     *,
 122 |     base_seconds: int = 5,
 123 |     cap_seconds: int = 3600,
 124 |     jitter_seed: str = "",
 125 | ) -> int:
 126 |     """Bounded exponential backoff before the next attempt.
 127 | 
 128 |     ``attempt`` is the just-finished attempt count (1 after the first
 129 |     try): 1 -> base, 2 -> 2*base, 3 -> 4*base, ... capped at ``cap``.
 130 |     A deterministic jitter in ``[0, base)`` derived from ``jitter_seed``
 131 |     (job id) spreads retries from many jobs without ``random`` state,
 132 |     so backoff is reproducible in tests and across processes.
 133 |     """
 134 |     exponent = max(0, attempt - 1)
 135 |     delay = base_seconds * (2**exponent)
 136 |     if jitter_seed:
 137 |         digest = hashlib.sha256(jitter_seed.encode("utf-8")).hexdigest()
 138 |         jitter = int(digest[:8], 16) % max(1, base_seconds)
 139 |         delay += jitter
 140 |     return min(delay, cap_seconds)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L119 | Define `compute_backoff_seconds`; bind its arguments when called. The body executes only when invoked. |
| L120 | Declare parameter `attempt` with annotation `int`. Caller-supplied attempt; its uses and transformations are traced below. |
| L121 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L122 | Declare parameter `base_seconds` with annotation `int`. Caller-supplied base seconds; its uses and transformations are traced below. |
| L123 | Declare parameter `cap_seconds` with annotation `int`. Caller-supplied cap seconds; its uses and transformations are traced below. |
| L124 | Declare parameter `jitter_seed` with annotation `str`. Caller-supplied jitter seed; its uses and transformations are traced below. |
| L125 | Finish/continue the signature; the declared return annotation is `int`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L126 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L128 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L129 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L130 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L131 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L132 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L133 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L134 | Evaluate the right-hand side, then bind/store it in `exponent`: `max(0, attempt - 1)` — Choose the largest supplied value; nested min/max calls implement the stated bound; inputs include subtract `attempt` and `1`, following the parentheses/operator precedence shown in `attempt - 1`. |
| L135 | Evaluate the right-hand side, then bind/store it in `delay`: multiply/repeat `base_seconds` and `2 ** exponent`, following the parentheses/operator precedence shown in `base_seconds * 2 ** exponent`. |
| L136 | Evaluate the branch condition: the current `jitter_seed` value. If truthy, enter L137; otherwise skip this indented block and continue after it. |
| L137 | Evaluate the right-hand side, then bind/store it in `digest`: `hashlib.sha256(jitter_seed.encode('utf-8')).hexdigest()` — Return the accumulated digest as lowercase hexadecimal text; first obtain the receiver: `hashlib.sha256(jitter_seed.encode('utf-8'))` — Create a SHA-256 digest state, optionally seeded with the supplied bytes. |
| L138 | Evaluate the right-hand side, then bind/store it in `jitter`: take the remainder of `int(digest[:8], 16)` and `max(1, base_seconds)`, following the parentheses/operator precedence shown in `int(digest[:8], 16) % max(1, base_seconds)`. |
| L139 | Update `delay` in place using `jitter` and the Add operation; the previous target value participates in the calculation. |
| L140 | Compute the return value: `min(delay, cap_seconds)` — Choose the smallest supplied value; nested min/max calls implement the stated bound. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
