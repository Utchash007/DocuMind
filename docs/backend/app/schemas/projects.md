# `app/schemas/projects.py`

[Source](../../../../Backend/app/schemas/projects.py) · [Backend index](../../README.md)

## Models

- `Project`: `id`, `name`, optional `description` and `deleted_at`, creation/update timestamps. No public owner field.
- `ProjectCreateRequest`: required 1–255-character name, optional description capped at 10,000 input characters; forbids unknown fields.
- `ProjectUpdateRequest`: optional name (1–255 when a string) and nullable description. Unlike creation, its description field has no explicit maximum. The API inspects `model_fields_set` to distinguish omitted fields from explicit nulls.
- `ProjectDeleteAccepted`: `project_id` and `accepted=True`, used for asynchronous cleanup acceptance.

## Functions

### `_strip(value: str) -> str`

**Arguments:** Text to normalize. **Returns:** Trimmed nonblank text. **Work:** Calls `strip()` and raises `ValueError` for whitespace-only input.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--strip"></a>

#### Line-by-line execution

[Current source: lines 13–17](../../../../Backend/app/schemas/projects.py#L13-L17). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `value` | `str`; required; positional or keyword | Input value being normalized, validated, or compared by this helper. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  13 | def _strip(value: str) -> str:
  14 |     stripped = value.strip()
  15 |     if not stripped:
  16 |         raise ValueError("value must not be blank")
  17 |     return stripped
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L13 | Define `_strip`; bind its arguments when called. The body executes only when invoked. |
| L14 | Evaluate the right-hand side, then bind/store it in `stripped`: `value.strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed. |
| L15 | Evaluate the branch condition: invert the truthiness of `stripped`. If truthy, enter L16; otherwise skip this indented block and continue after it. |
| L16 | Raise `ValueError('value must not be blank')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L17 | Compute the return value: the current `stripped` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `ProjectCreateRequest._name(cls, value: str) -> str`

**Arguments:** Model class and name. **Returns:** Validated trimmed name. **Work:** Calls `_strip`, checks the resulting length is at most 255, and raises `ValueError` otherwise; Pydantic field bounds also apply before this validator.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-projectcreaterequest--name"></a>

#### Line-by-line execution

[Current source: lines 33–39](../../../../Backend/app/schemas/projects.py#L33-L39). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `cls` | not annotated; implicitly supplied/collected; positional or keyword | The class being constructed or validated; the classmethod descriptor supplies it. |
| `value` | `str`; required; positional or keyword | Input value being normalized, validated, or compared by this helper. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  33 |     @field_validator("name")
  34 |     @classmethod
  35 |     def _name(cls, value: str) -> str:
  36 |         checked = _strip(value)
  37 |         if len(checked) > 255:
  38 |             raise ValueError("name must be at most 255 characters")
  39 |         return checked
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L33 | Register this Pydantic validator for `field_validator('name')`; it runs in the declared validation phase and returns the accepted/transformed value or raises. |
| L34 | Bind the method to the class so Python supplies cls; decorators are applied bottom-up when the function is defined. |
| L35 | Define `ProjectCreateRequest._name`; bind its arguments when called. The body executes only when invoked. |
| L36 | Evaluate the right-hand side, then bind/store it in `checked`: `_strip(value)` — Call [_strip](#walk--strip) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L37 | Evaluate the branch condition: compare whether `len(checked)` is greater than `255`. If truthy, enter L38; otherwise skip this indented block and continue after it. |
| L38 | Raise `ValueError('name must be at most 255 characters')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L39 | Compute the return value: the current `checked` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `ProjectCreateRequest._description(cls, value: str | None) -> str | None`

**Arguments:** Model class and nullable description. **Returns:** `None` for null/blank, otherwise trimmed description. **Work:** Preserves `None`, strips strings, and normalizes an empty result to `None`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-projectcreaterequest--description"></a>

#### Line-by-line execution

[Current source: lines 41–48](../../../../Backend/app/schemas/projects.py#L41-L48). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `cls` | not annotated; implicitly supplied/collected; positional or keyword | The class being constructed or validated; the classmethod descriptor supplies it. |
| `value` | `str \| None`; required; positional or keyword | Input value being normalized, validated, or compared by this helper. |

**Declared result:** `str | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  41 |     @field_validator("description")
  42 |     @classmethod
  43 |     def _description(cls, value: str | None) -> str | None:
  44 |         if value is None:
  45 |             return None
  46 |         stripped = value.strip()
  47 |         # A blank description is normalized to "no description".
  48 |         return stripped or None
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L41 | Register this Pydantic validator for `field_validator('description')`; it runs in the declared validation phase and returns the accepted/transformed value or raises. |
| L42 | Bind the method to the class so Python supplies cls; decorators are applied bottom-up when the function is defined. |
| L43 | Define `ProjectCreateRequest._description`; bind its arguments when called. The body executes only when invoked. |
| L44 | Evaluate the branch condition: compare whether `value` is the same object as `None`. If truthy, enter L45; otherwise skip this indented block and continue after it. |
| L45 | Compute the return value: None (no value). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L46 | Evaluate the right-hand side, then bind/store it in `stripped`: `value.strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed. |
| L47 | Comment only: A blank description is normalized to "no description".. It does not execute; the neighboring code determines behavior. |
| L48 | Compute the return value: evaluate `stripped or None` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `ProjectUpdateRequest._name(cls, value: str | None) -> str | None`

**Arguments:** Model class and nullable patch name. **Returns:** `None` unchanged or a validated trimmed name. **Work:** Short-circuits null, then uses `_strip` and the 255-character bound. The route separately rejects explicitly null names.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-projectupdaterequest--name"></a>

#### Line-by-line execution

[Current source: lines 57–65](../../../../Backend/app/schemas/projects.py#L57-L65). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `cls` | not annotated; implicitly supplied/collected; positional or keyword | The class being constructed or validated; the classmethod descriptor supplies it. |
| `value` | `str \| None`; required; positional or keyword | Input value being normalized, validated, or compared by this helper. |

**Declared result:** `str | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  57 |     @field_validator("name")
  58 |     @classmethod
  59 |     def _name(cls, value: str | None) -> str | None:
  60 |         if value is None:
  61 |             return None
  62 |         checked = _strip(value)
  63 |         if len(checked) > 255:
  64 |             raise ValueError("name must be at most 255 characters")
  65 |         return checked
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L57 | Register this Pydantic validator for `field_validator('name')`; it runs in the declared validation phase and returns the accepted/transformed value or raises. |
| L58 | Bind the method to the class so Python supplies cls; decorators are applied bottom-up when the function is defined. |
| L59 | Define `ProjectUpdateRequest._name`; bind its arguments when called. The body executes only when invoked. |
| L60 | Evaluate the branch condition: compare whether `value` is the same object as `None`. If truthy, enter L61; otherwise skip this indented block and continue after it. |
| L61 | Compute the return value: None (no value). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L62 | Evaluate the right-hand side, then bind/store it in `checked`: `_strip(value)` — Call [_strip](#walk--strip) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L63 | Evaluate the branch condition: compare whether `len(checked)` is greater than `255`. If truthy, enter L64; otherwise skip this indented block and continue after it. |
| L64 | Raise `ValueError('name must be at most 255 characters')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L65 | Compute the return value: the current `checked` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `ProjectUpdateRequest._description(cls, value: str | None) -> str | None`

**Arguments:** Model class and nullable patch description. **Returns:** Null or trimmed nonblank text. **Work:** Normalizes whitespace-only text to `None`; no length check is implemented here.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-projectupdaterequest--description"></a>

#### Line-by-line execution

[Current source: lines 67–72](../../../../Backend/app/schemas/projects.py#L67-L72). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `cls` | not annotated; implicitly supplied/collected; positional or keyword | The class being constructed or validated; the classmethod descriptor supplies it. |
| `value` | `str \| None`; required; positional or keyword | Input value being normalized, validated, or compared by this helper. |

**Declared result:** `str | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  67 |     @field_validator("description")
  68 |     @classmethod
  69 |     def _description(cls, value: str | None) -> str | None:
  70 |         if value is None:
  71 |             return None
  72 |         return value.strip() or None
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L67 | Register this Pydantic validator for `field_validator('description')`; it runs in the declared validation phase and returns the accepted/transformed value or raises. |
| L68 | Bind the method to the class so Python supplies cls; decorators are applied bottom-up when the function is defined. |
| L69 | Define `ProjectUpdateRequest._description`; bind its arguments when called. The body executes only when invoked. |
| L70 | Evaluate the branch condition: compare whether `value` is the same object as `None`. If truthy, enter L71; otherwise skip this indented block and continue after it. |
| L71 | Compute the return value: None (no value). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L72 | Compute the return value: evaluate `value.strip() or None` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `ProjectUpdateRequest.has_changes(self) -> bool`

**Arguments:** The request instance. **Returns:** Whether `name` or `description` is non-`None`. **Work:** Checks values, not field presence. Consequently an explicit null/blank description alone returns `False`; the API's `model_fields_set` handling is what permits clearing descriptions.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-projectupdaterequest-has-changes"></a>

#### Line-by-line execution

[Current source: lines 74–76](../../../../Backend/app/schemas/projects.py#L74-L76). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  74 |     def has_changes(self) -> bool:
  75 |         """True when the PATCH body carries at least one field."""
  76 |         return self.name is not None or self.description is not None
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L74 | Define `ProjectUpdateRequest.has_changes`; bind its arguments when called. The body executes only when invoked. |
| L75 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L76 | Compute the return value: evaluate `self.name is not None or self.description is not None` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
