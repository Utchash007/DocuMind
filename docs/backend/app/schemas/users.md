# `app/schemas/users.py`

[Source](../../../../Backend/app/schemas/users.py) · [Backend index](../../README.md)

Defines the public profile and internal principal shapes. All models inherit camelCase serialization from [common.md](common.md).

| Model | Fields |
| --- | --- |
| `ApplicationUser` | UUID `id`, `email`, optional `name`/`date_of_birth`, `onboarding_completed`, `created_at`, `updated_at`; excludes the external Appwrite ID |
| `ProfileUpdateRequest` | Required `name` (1–150 characters) and `date_of_birth`; unknown fields rejected |
| `AuthenticatedUser` | Internal UUID `id`, external `appwrite_user_id`, normalized `email`, `onboarding_completed`; server-side principal, not the `/me` response |

## Functions

### `derive_onboarding_completed(name: str | None, date_of_birth: date | None) -> bool`

- **Arguments:** Optional display name and date of birth.
- **Returns:** `True` only when the name is nonblank after trimming and the date exists and is not after `date.today()`.
- **Work:** Short-circuits the presence/content/date comparisons and converts the result to `bool`. Does not mutate the name or write a user. Uses the server's current date.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-derive-onboarding-completed"></a>

#### Line-by-line execution

[Current source: lines 13–26](../../../../Backend/app/schemas/users.py#L13-L26). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `name` | `str \| None`; required; positional or keyword | Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. |
| `date_of_birth` | `date \| None`; required; positional or keyword | Profile birth date validated against the current date before onboarding completion. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  13 | def derive_onboarding_completed(name: str | None, date_of_birth: date | None) -> bool:
  14 |     """Server-side onboarding derivation: both required fields present.
  15 | 
  16 |     ``onboarding_completed`` is never client-settable; the backend sets it
  17 |     only when name (non-blank after trim) and date of birth (not in the
  18 |     future) are both present, mirroring the DB CHECK
  19 |     ``onboarding_requires_profile``.
  20 |     """
  21 |     return bool(
  22 |         name is not None
  23 |         and name.strip() != ""
  24 |         and date_of_birth is not None
  25 |         and date_of_birth <= date.today()
  26 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L13 | Define `derive_onboarding_completed`; bind its arguments when called. The body executes only when invoked. |
| L14 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L16 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L17 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L18 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L19 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L20 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L21 | Compute the return value: `bool(name is not None and name.strip() != '' and (date_of_birth is not None) and (date_of_birth <= date.today()))` — Convert the value's truthiness to True or False. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L22 | Continue the enclosing expression: evaluate `name is not None and name.strip() != '' and (date_of_birth is not None) and (date_of_birth <= date.today())` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. |
| L23 | Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed. |
| L24 | Continue the enclosing expression: compare whether `date_of_birth` is not the same object as `None`. |
| L25 | Read the current local calendar date for date-of-birth validation. |
| L26 | Close the expression/container begun at L21; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `ProfileUpdateRequest._strip_name(cls, value: str) -> str`

- **Arguments:** Pydantic class and field-constrained name string.
- **Returns:** Trimmed name.
- **Work:** Strips surrounding whitespace and rejects an empty result with `ValueError`. The field enforces the 150-character input maximum.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-profileupdaterequest--strip-name"></a>

#### Line-by-line execution

[Current source: lines 52–58](../../../../Backend/app/schemas/users.py#L52-L58). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `cls` | not annotated; implicitly supplied/collected; positional or keyword | The class being constructed or validated; the classmethod descriptor supplies it. |
| `value` | `str`; required; positional or keyword | Input value being normalized, validated, or compared by this helper. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  52 |     @field_validator("name")
  53 |     @classmethod
  54 |     def _strip_name(cls, value: str) -> str:
  55 |         stripped = value.strip()
  56 |         if not stripped:
  57 |             raise ValueError("name must not be blank")
  58 |         return stripped
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L52 | Register this Pydantic validator for `field_validator('name')`; it runs in the declared validation phase and returns the accepted/transformed value or raises. |
| L53 | Bind the method to the class so Python supplies cls; decorators are applied bottom-up when the function is defined. |
| L54 | Define `ProfileUpdateRequest._strip_name`; bind its arguments when called. The body executes only when invoked. |
| L55 | Evaluate the right-hand side, then bind/store it in `stripped`: `value.strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed. |
| L56 | Evaluate the branch condition: invert the truthiness of `stripped`. If truthy, enter L57; otherwise skip this indented block and continue after it. |
| L57 | Raise `ValueError('name must not be blank')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L58 | Compute the return value: the current `stripped` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `ProfileUpdateRequest._dob_not_future(cls, value: date) -> date`

- **Arguments:** Pydantic class and parsed date.
- **Returns:** The same date if it is today or earlier.
- **Work:** Compares with `date.today()`; a future value raises `ValueError`, surfaced as request validation failure by FastAPI.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-profileupdaterequest--dob-not-future"></a>

#### Line-by-line execution

[Current source: lines 60–65](../../../../Backend/app/schemas/users.py#L60-L65). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `cls` | not annotated; implicitly supplied/collected; positional or keyword | The class being constructed or validated; the classmethod descriptor supplies it. |
| `value` | `date`; required; positional or keyword | Input value being normalized, validated, or compared by this helper. |

**Declared result:** `date`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  60 |     @field_validator("date_of_birth")
  61 |     @classmethod
  62 |     def _dob_not_future(cls, value: date) -> date:
  63 |         if value > date.today():
  64 |             raise ValueError("date_of_birth must not be in the future")
  65 |         return value
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L60 | Register this Pydantic validator for `field_validator('date_of_birth')`; it runs in the declared validation phase and returns the accepted/transformed value or raises. |
| L61 | Bind the method to the class so Python supplies cls; decorators are applied bottom-up when the function is defined. |
| L62 | Define `ProfileUpdateRequest._dob_not_future`; bind its arguments when called. The body executes only when invoked. |
| L63 | Evaluate the branch condition: compare whether `value` is greater than `date.today()`. If truthy, enter L64; otherwise skip this indented block and continue after it. |
| L64 | Raise `ValueError('date_of_birth must not be in the future')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L65 | Compute the return value: the current `value` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
