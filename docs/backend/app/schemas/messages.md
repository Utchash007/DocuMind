# `app/schemas/messages.py`

[Source](../../../../Backend/app/schemas/messages.py) · [Backend index](../../README.md)

Defines message/turn request and response DTOs. `MAX_QUESTION_LENGTH = 8000`.

| Model | Fields / behavior |
| --- | --- |
| `Message` | `id`, `conversation_id`, role, content, position, created timestamp; optional verified citations, `client_request_id`, `reply_to_message_id`, generation status/expiry, and metadata |
| `MessageCreateRequest` | Required 1–8000-character `content` and UUID `client_request_id`; forbids unknown fields |
| `TurnResponse` | Persisted `user_message` and `assistant_message` |
| `MessageRetryRequest` | Optional UUID `client_request_id`; when supplied the repository requires it to match the existing turn |
| `MessageCancelResponse` | Authoritative `user_message` and boolean `cancelled` |

`Message.message_metadata` has the explicit wire alias **`metadata`**, matching the SQL column despite the different ORM attribute name. The generation fencing token is excluded. Citation arrays validate every item as a complete verified `Citation`; unresolved historical records are unsupported.

## Functions

### `MessageCreateRequest._content(cls, value: str) -> str`

- **Arguments:** Model class and field-bounded question text.
- **Returns:** The **original** string, including leading/trailing whitespace.
- **Work:** Uses `value.strip()` only to detect whitespace-only input, raising `ValueError` when blank. Preserving the original value matters because request-key replay compares exact content.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-messagecreaterequest--content"></a>

#### Line-by-line execution

[Current source: lines 59–64](../../../../Backend/app/schemas/messages.py#L59-L64). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `cls` | not annotated; implicitly supplied/collected; positional or keyword | The class being constructed or validated; the classmethod descriptor supplies it. |
| `value` | `str`; required; positional or keyword | Input value being normalized, validated, or compared by this helper. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  59 |     @field_validator("content")
  60 |     @classmethod
  61 |     def _content(cls, value: str) -> str:
  62 |         if not value.strip():
  63 |             raise ValueError("content must not be blank")
  64 |         return value
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L59 | Register this Pydantic validator for `field_validator('content')`; it runs in the declared validation phase and returns the accepted/transformed value or raises. |
| L60 | Bind the method to the class so Python supplies cls; decorators are applied bottom-up when the function is defined. |
| L61 | Define `MessageCreateRequest._content`; bind its arguments when called. The body executes only when invoked. |
| L62 | Evaluate the branch condition: invert the truthiness of `value.strip()`. If truthy, enter L63; otherwise skip this indented block and continue after it. |
| L63 | Raise `ValueError('content must not be blank')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L64 | Compute the return value: the current `value` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
