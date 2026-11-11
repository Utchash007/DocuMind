# `app/auth/errors.py`

[Source](../../../../Backend/app/auth/errors.py) · [Backend index](../../README.md)

Constructs consistent FastAPI `HTTPException` objects. Callers **raise** the returned object; these helpers do not raise it themselves. The `detail` object is `ApiError.model_dump(by_alias=True)` and includes optional resource fields as null.

## Functions

### `_error(status_code: int, code: ErrorCode, message: str) -> HTTPException`

**Arguments:** HTTP status, stable machine code, nonempty safe message. **Returns:** Configured `HTTPException`. **Work:** Validates an `ApiError`, serializes its aliases, and places it in `detail`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--error"></a>

#### Line-by-line execution

[Current source: lines 18–24](../../../../Backend/app/auth/errors.py#L18-L24). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `status_code` | `int`; required; positional or keyword | Caller-supplied status code; each read, transformation, and validation is traced below. |
| `code` | `ErrorCode`; required; positional or keyword | Caller-supplied code; each read, transformation, and validation is traced below. |
| `message` | `str`; required; positional or keyword | Caller-supplied message; each read, transformation, and validation is traced below. |

**Declared result:** `HTTPException`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  18 | def _error(
  19 |     status_code: int,
  20 |     code: ErrorCode,
  21 |     message: str,
  22 | ) -> HTTPException:
  23 |     error = ApiError(code=code, message=message)
  24 |     return HTTPException(status_code=status_code, detail=error.model_dump(by_alias=True))
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L18 | Define `_error`; bind its arguments when called. The body executes only when invoked. |
| L19 | Declare parameter `status_code` with annotation `int`. Caller-supplied status code; its uses and transformations are traced below. |
| L20 | Declare parameter `code` with annotation `ErrorCode`. Caller-supplied code; its uses and transformations are traced below. |
| L21 | Declare parameter `message` with annotation `str`. Caller-supplied message; its uses and transformations are traced below. |
| L22 | Finish/continue the signature; the declared return annotation is `HTTPException`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L23 | Evaluate the right-hand side, then bind/store it in `error`: `ApiError(code=code, message=message)` — Construct `ApiError` with the supplied diagnostic fields; the surrounding raise determines propagation. |
| L24 | Compute the return value: `HTTPException(status_code=status_code, detail=error.model_dump(by_alias=True))` — Construct a FastAPI exception carrying the chosen status and response detail; raising it ends the handler. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `unauthenticated(message="Sign in to access NoteMind.") -> HTTPException`

**Arguments:** Optional human-readable message. **Returns:** HTTP 401 / `unauthenticated`. **Work:** Delegates to `_error` with the authentication-required status/code.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-unauthenticated"></a>

#### Line-by-line execution

[Current source: lines 27–28](../../../../Backend/app/auth/errors.py#L27-L28). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `message` | `str`; default `'Sign in to access NoteMind.'`; positional or keyword | Caller-supplied message; each read, transformation, and validation is traced below. |

**Declared result:** `HTTPException`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  27 | def unauthenticated(message: str = "Sign in to access NoteMind.") -> HTTPException:
  28 |     return _error(401, ErrorCode.UNAUTHENTICATED, message)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L27 | Define `unauthenticated`; bind its arguments when called. The body executes only when invoked. |
| L28 | Compute the return value: `_error(401, ErrorCode.UNAUTHENTICATED, message)` — Call [_error](#walk--error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `onboarding_required(message="Complete your profile to continue.") -> HTTPException`

**Arguments:** Optional profile-completion message. **Returns:** HTTP 403 / `onboarding_required`. **Work:** Builds the error through `_error`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-onboarding-required"></a>

#### Line-by-line execution

[Current source: lines 31–34](../../../../Backend/app/auth/errors.py#L31-L34). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `message` | `str`; default `'Complete your profile to continue.'`; positional or keyword | Caller-supplied message; each read, transformation, and validation is traced below. |

**Declared result:** `HTTPException`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  31 | def onboarding_required(
  32 |     message: str = "Complete your profile to continue.",
  33 | ) -> HTTPException:
  34 |     return _error(403, ErrorCode.ONBOARDING_REQUIRED, message)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L31 | Define `onboarding_required`; bind its arguments when called. The body executes only when invoked. |
| L32 | Declare parameter `message` with annotation `str`. Caller-supplied message; its uses and transformations are traced below. |
| L33 | Finish/continue the signature; the declared return annotation is `HTTPException`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L34 | Compute the return value: `_error(403, ErrorCode.ONBOARDING_REQUIRED, message)` — Call [_error](#walk--error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `forbidden(message="You do not have access to this resource.") -> HTTPException`

**Arguments:** Optional access-denial message. **Returns:** HTTP 403 / `forbidden`. **Work:** Delegates to `_error`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-forbidden"></a>

#### Line-by-line execution

[Current source: lines 37–38](../../../../Backend/app/auth/errors.py#L37-L38). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `message` | `str`; default `'You do not have access to this resource.'`; positional or keyword | Caller-supplied message; each read, transformation, and validation is traced below. |

**Declared result:** `HTTPException`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  37 | def forbidden(message: str = "You do not have access to this resource.") -> HTTPException:
  38 |     return _error(403, ErrorCode.FORBIDDEN, message)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L37 | Define `forbidden`; bind its arguments when called. The body executes only when invoked. |
| L38 | Compute the return value: `_error(403, ErrorCode.FORBIDDEN, message)` — Call [_error](#walk--error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `not_found(message="The requested resource does not exist.") -> HTTPException`

**Arguments:** Optional missing-resource message. **Returns:** HTTP 404 / `not_found`. **Work:** Delegates to `_error`, allowing inaccessible resources to use the same response as absent ones.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-not-found"></a>

#### Line-by-line execution

[Current source: lines 41–42](../../../../Backend/app/auth/errors.py#L41-L42). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `message` | `str`; default `'The requested resource does not exist.'`; positional or keyword | Caller-supplied message; each read, transformation, and validation is traced below. |

**Declared result:** `HTTPException`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  41 | def not_found(message: str = "The requested resource does not exist.") -> HTTPException:
  42 |     return _error(404, ErrorCode.NOT_FOUND, message)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L41 | Define `not_found`; bind its arguments when called. The body executes only when invoked. |
| L42 | Compute the return value: `_error(404, ErrorCode.NOT_FOUND, message)` — Call [_error](#walk--error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `conflict(message: str) -> HTTPException`

**Arguments:** Required conflict explanation. **Returns:** HTTP 409 / `conflict`. **Work:** Delegates to `_error`; used for identity/email collisions without merging accounts.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-conflict"></a>

#### Line-by-line execution

[Current source: lines 45–46](../../../../Backend/app/auth/errors.py#L45-L46). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `message` | `str`; required; positional or keyword | Caller-supplied message; each read, transformation, and validation is traced below. |

**Declared result:** `HTTPException`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  45 | def conflict(message: str) -> HTTPException:
  46 |     return _error(409, ErrorCode.CONFLICT, message)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L45 | Define `conflict`; bind its arguments when called. The body executes only when invoked. |
| L46 | Compute the return value: `_error(409, ErrorCode.CONFLICT, message)` — Call [_error](#walk--error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `service_unavailable(message="Identity verification is temporarily unavailable. Please try again.") -> HTTPException`

**Arguments:** Optional safe outage explanation. **Returns:** HTTP 503 / `service_unavailable`. **Work:** Delegates to `_error` so provider/configuration failures fail closed with a retryable HTTP status.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-service-unavailable"></a>

#### Line-by-line execution

[Current source: lines 49–52](../../../../Backend/app/auth/errors.py#L49-L52). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `message` | `str`; default `'Identity verification is temporarily unavailable. Please try again.'`; positional or keyword | Caller-supplied message; each read, transformation, and validation is traced below. |

**Declared result:** `HTTPException`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  49 | def service_unavailable(
  50 |     message: str = "Identity verification is temporarily unavailable. Please try again.",
  51 | ) -> HTTPException:
  52 |     return _error(503, ErrorCode.SERVICE_UNAVAILABLE, message)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L49 | Define `service_unavailable`; bind its arguments when called. The body executes only when invoked. |
| L50 | Declare parameter `message` with annotation `str`. Caller-supplied message; its uses and transformations are traced below. |
| L51 | Finish/continue the signature; the declared return annotation is `HTTPException`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L52 | Compute the return value: `_error(503, ErrorCode.SERVICE_UNAVAILABLE, message)` — Call [_error](#walk--error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
