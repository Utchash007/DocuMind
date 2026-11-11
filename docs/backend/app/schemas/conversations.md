# `app/schemas/conversations.py`

[Source](../../../../Backend/app/schemas/conversations.py) · [Backend index](../../README.md)

## Models

- `Conversation`: UUID `id` and `project_id`, nullable `title`, creation/update timestamps.
- `ConversationCreateRequest`: optional nullable `title`; non-null strings have 1–255-character field bounds.
- `ConversationUpdateRequest`: required 1–255-character title; rename-only request.
- `ConversationDeleteAccepted`: UUID `conversation_id`, `accepted=True`; deletion and cascading message removal are synchronous (HTTP 200).

Both request models reject unknown fields.

## Functions

### `_strip_title(value: str) -> str`

**Arguments:** A title string. **Returns:** Trimmed title. **Work:** Rejects a blank result or a result longer than 255 characters with `ValueError`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--strip-title"></a>

#### Line-by-line execution

[Current source: lines 21–27](../../../../Backend/app/schemas/conversations.py#L21-L27). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `value` | `str`; required; positional or keyword | Input value being normalized, validated, or compared by this helper. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  21 | def _strip_title(value: str) -> str:
  22 |     stripped = value.strip()
  23 |     if not stripped:
  24 |         raise ValueError("title must not be blank")
  25 |     if len(stripped) > 255:
  26 |         raise ValueError("title must be at most 255 characters")
  27 |     return stripped
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L21 | Define `_strip_title`; bind its arguments when called. The body executes only when invoked. |
| L22 | Evaluate the right-hand side, then bind/store it in `stripped`: `value.strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed. |
| L23 | Evaluate the branch condition: invert the truthiness of `stripped`. If truthy, enter L24; otherwise skip this indented block and continue after it. |
| L24 | Raise `ValueError('title must not be blank')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L25 | Evaluate the branch condition: compare whether `len(stripped)` is greater than `255`. If truthy, enter L26; otherwise skip this indented block and continue after it. |
| L26 | Raise `ValueError('title must be at most 255 characters')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L27 | Compute the return value: the current `stripped` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `ConversationCreateRequest._title(cls, value: str | None) -> str | None`

**Arguments:** Pydantic class and optional title. **Returns:** `None` unchanged or the normalized title. **Work:** Delegates non-null values to `_strip_title`; does not invent a default title.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-conversationcreaterequest--title"></a>

#### Line-by-line execution

[Current source: lines 33–36](../../../../Backend/app/schemas/conversations.py#L33-L36). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `cls` | not annotated; implicitly supplied/collected; positional or keyword | The class being constructed or validated; the classmethod descriptor supplies it. |
| `value` | `str \| None`; required; positional or keyword | Input value being normalized, validated, or compared by this helper. |

**Declared result:** `str | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  33 |     @field_validator("title")
  34 |     @classmethod
  35 |     def _title(cls, value: str | None) -> str | None:
  36 |         return None if value is None else _strip_title(value)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L33 | Register this Pydantic validator for `field_validator('title')`; it runs in the declared validation phase and returns the accepted/transformed value or raises. |
| L34 | Bind the method to the class so Python supplies cls; decorators are applied bottom-up when the function is defined. |
| L35 | Define `ConversationCreateRequest._title`; bind its arguments when called. The body executes only when invoked. |
| L36 | Compute the return value: check `value is None`; when true use None (no value), otherwise `_strip_title(value)` — Call [_strip_title](#walk--strip-title) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result (only the selected branch is evaluated). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `ConversationUpdateRequest._title(cls, value: str) -> str`

**Arguments:** Pydantic class and required title. **Returns:** Validated trimmed title. **Work:** Delegates to `_strip_title`; validation errors prevent the rename from reaching the repository.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-conversationupdaterequest--title"></a>

#### Line-by-line execution

[Current source: lines 44–47](../../../../Backend/app/schemas/conversations.py#L44-L47). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `cls` | not annotated; implicitly supplied/collected; positional or keyword | The class being constructed or validated; the classmethod descriptor supplies it. |
| `value` | `str`; required; positional or keyword | Input value being normalized, validated, or compared by this helper. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  44 |     @field_validator("title")
  45 |     @classmethod
  46 |     def _title(cls, value: str) -> str:
  47 |         return _strip_title(value)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L44 | Register this Pydantic validator for `field_validator('title')`; it runs in the declared validation phase and returns the accepted/transformed value or raises. |
| L45 | Bind the method to the class so Python supplies cls; decorators are applied bottom-up when the function is defined. |
| L46 | Define `ConversationUpdateRequest._title`; bind its arguments when called. The body executes only when invoked. |
| L47 | Compute the return value: `_strip_title(value)` — Call [_strip_title](#walk--strip-title) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
