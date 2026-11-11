# `app/schemas/common.py`

[Source](../../../../Backend/app/schemas/common.py) · [Backend index](../../README.md)

Shared Pydantic models, wire enums, verified citations, and opaque pagination cursors. Alias serialization must be requested (`model_dump(by_alias=True)` or FastAPI response serialization); Python fields remain snake_case.

## Models and enums

| Definition | Fields / behavior |
| --- | --- |
| `CamelModel` | `to_camel` aliases, population by either name, ORM attribute loading, extra fields ignored |
| `RequestModel` | Same naming/ORM configuration, but unknown request fields forbidden |
| `DocumentStatus` | `Pending`, `Processing`, `Completed`, `Failed` |
| `MessageRole` | `user`, `assistant`, `system` |
| `GenerationStatus` | `pending`, `generating`, `completed`, `failed`, `cancelled` |
| `JobKind` | `process_document`, `delete_document` |
| `JobStatus` | `awaiting_upload`, `queued`, `running`, `retry_wait`, `succeeded`, `failed`, `cancelled` |
| `JobStage` | `uploading`, `extracting`, `chunking`, `embedding`, `indexing`, `publishing`, `deleting` |
| `ErrorCode` | `unauthenticated`, `onboarding_required`, `forbidden`, `not_found`, `validation_error`, `conflict`, `duplicate_request_conflict`, `active_turn_in_progress`, `invalid_state`, `no_ready_sources`, `processing_in_progress`, `service_unavailable`, `internal_error` |
| `ApiError` | Stable `code`, nonempty `message`, optional UUIDs for job/message/document/project/conversation |
| `ErrorEnvelope` | `detail: ApiError`; framework request-validation errors may instead contain FastAPI's detail array |
| `Citation` | Required `document_id`, `file_name`, one-based `page_number`, `chunk_id`, `text`, and UUID `index_version`; string fields must be nonblank |
| `CursorPageParams` | Optional `cursor`, `limit=50` constrained to 1–200 |
| `PaginatedResponse[T]` | `items: list[T]`, optional `next_cursor=None` |

Pydantic supplies constructors/serialization for these classes; only the explicitly implemented functions below belong to this file.

## Functions

### `to_camel(name: str) -> str`

- **Arguments:** A Python field name.
- **Returns:** Its generated alias, for example `appwrite_user_id` → `appwriteUserId`.
- **Work:** Splits on underscores, retains the first segment, and capitalizes the first character of each nonempty remaining segment. A name without underscores is unchanged. Leading/repeated underscores are not preserved by this algorithm (`_id` becomes `Id`).

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-to-camel"></a>

#### Line-by-line execution

[Current source: lines 30–40](../../../../Backend/app/schemas/common.py#L30-L40). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `name` | `str`; required; positional or keyword | Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  30 | def to_camel(name: str) -> str:
  31 |     """Convert a snake_case attribute name to camelCase (``_id`` aware).
  32 | 
  33 |     ``user_id`` -> ``userId``, ``appwrite_user_id`` -> ``appwriteUserId``,
  34 |     ``id`` -> ``id``.  Single leading underscores are preserved so private
  35 |     validator helpers are never accidentally exposed as public fields.
  36 |     """
  37 |     head, *tail = name.split("_")
  38 |     if not tail:
  39 |         return name
  40 |     return head + "".join(part[:1].upper() + part[1:] for part in tail if part)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L30 | Define `to_camel`; bind its arguments when called. The body executes only when invoked. |
| L31 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L33 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L34 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L35 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L36 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L37 | Split on underscores, bind the first segment to head, and collect remaining segments in tail. Leading underscores produce an empty head; this implementation does not actually preserve a leading underscore despite its old docstring. |
| L38 | Evaluate the branch condition: invert the truthiness of `tail`. If truthy, enter L39; otherwise skip this indented block and continue after it. |
| L39 | Compute the return value: the current `name` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L40 | Compute the return value: add/concatenate `head` and `''.join((part[:1].upper() + part[1:] for part in tail if part))`, following the parentheses/operator precedence shown in `head + ''.join((part[:1].upper() + part[1:] for part in tail if part))`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `Citation._strip(cls, value: str) -> str`

- **Arguments:** Pydantic class and a validated `file_name`, `chunk_id`, or `text` string.
- **Returns:** The whitespace-trimmed string.
- **Work:** A classmethod field validator strips surrounding whitespace and raises `ValueError` if nothing remains. It validates shape; evidence ownership is enforced by retrieval/refinement, not by this model alone.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-citation--strip"></a>

#### Line-by-line execution

[Current source: lines 178–184](../../../../Backend/app/schemas/common.py#L178-L184). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `cls` | not annotated; implicitly supplied/collected; positional or keyword | The class being constructed or validated; the classmethod descriptor supplies it. |
| `value` | `str`; required; positional or keyword | Input value being normalized, validated, or compared by this helper. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 178 |     @field_validator("file_name", "chunk_id", "text")
 179 |     @classmethod
 180 |     def _strip(cls, value: str) -> str:
 181 |         stripped = value.strip()
 182 |         if not stripped:
 183 |             raise ValueError("value must not be blank")
 184 |         return stripped
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L178 | Register this Pydantic validator for `field_validator('file_name', 'chunk_id', 'text')`; it runs in the declared validation phase and returns the accepted/transformed value or raises. |
| L179 | Bind the method to the class so Python supplies cls; decorators are applied bottom-up when the function is defined. |
| L180 | Define `Citation._strip`; bind its arguments when called. The body executes only when invoked. |
| L181 | Evaluate the right-hand side, then bind/store it in `stripped`: `value.strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed. |
| L182 | Evaluate the branch condition: invert the truthiness of `stripped`. If truthy, enter L183; otherwise skip this indented block and continue after it. |
| L183 | Raise `ValueError('value must not be blank')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L184 | Compute the return value: the current `stripped` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `encode_cursor(payload: dict[str, Any]) -> str`

- **Arguments:** A JSON-serializable server cursor object.
- **Returns:** An unpadded base64url ASCII string.
- **Work:** Serializes sorted keys with compact JSON separators, encodes UTF-8 bytes, base64url-encodes them, and removes trailing `=`. Serialization errors propagate. This is encoding, not signing or encryption; repositories validate decoded fields and scope their SQL independently.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-encode-cursor"></a>

#### Line-by-line execution

[Current source: lines 211–214](../../../../Backend/app/schemas/common.py#L211-L214). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `payload` | `dict[str, Any]`; required; positional or keyword | Input mapping, DTO, or provider response; the annotated type and body identify its expected shape. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 211 | def encode_cursor(payload: dict[str, Any]) -> str:
 212 |     """Encode a server-side cursor payload as an opaque base64url string."""
 213 |     raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
 214 |     return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L211 | Define `encode_cursor`; bind its arguments when called. The body executes only when invoked. |
| L212 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L213 | Evaluate the right-hand side, then bind/store it in `raw`: `json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')` — Encode the text into bytes with the selected encoding; first obtain the receiver: `json.dumps(payload, separators=(',', ':'), sort_keys=True)` — Serialize the supplied value to JSON text using the specified formatting options. |
| L214 | Compute the return value: `base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')` — Remove matching trailing characters (not a whole substring); first obtain the receiver: `base64.urlsafe_b64encode(raw).decode('ascii')` — Decode bytes into text with the selected encoding; first obtain the receiver: `base64.urlsafe_b64encode(raw)` — Encode bytes with URL-safe base64; this is reversible encoding, not encryption or signing. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `decode_cursor(cursor: str) -> dict[str, Any]`

- **Arguments:** The opaque string received from a previous page.
- **Returns:** The decoded JSON dictionary.
- **Work:** Rejects blank input, trims it, restores base64 padding, decodes ASCII/base64/UTF-8, and parses JSON. Rejects arrays/scalars and wraps decoding/parsing errors in `ValueError("invalid cursor")`. Per-list timestamp/UUID/position checks happen in repository cursor helpers.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-decode-cursor"></a>

#### Line-by-line execution

[Current source: lines 217–233](../../../../Backend/app/schemas/common.py#L217-L233). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `cursor` | `str`; required; positional or keyword | Opaque page continuation token; null starts the first page. |

**Declared result:** `dict[str, Any]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 217 | def decode_cursor(cursor: str) -> dict[str, Any]:
 218 |     """Decode a cursor produced by :func:`encode_cursor`.
 219 | 
 220 |     Raises :class:`ValueError` for malformed or non-object payloads so
 221 |     handlers can convert bad cursors into a ``422 validation_error``.
 222 |     """
 223 |     if not cursor or not cursor.strip():
 224 |         raise ValueError("cursor must not be blank")
 225 |     padded = cursor.strip() + "=" * (-len(cursor.strip()) % 4)
 226 |     try:
 227 |         decoded = base64.urlsafe_b64decode(padded.encode("ascii"))
 228 |         payload = json.loads(decoded.decode("utf-8"))
 229 |     except Exception as exc:  # binascii/unicode/json errors
 230 |         raise ValueError("invalid cursor") from exc
 231 |     if not isinstance(payload, dict):
 232 |         raise ValueError("invalid cursor")
 233 |     return payload
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L217 | Define `decode_cursor`; bind its arguments when called. The body executes only when invoked. |
| L218 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L220 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L221 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L222 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L223 | Evaluate the branch condition: evaluate `not cursor or not cursor.strip()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L224; otherwise skip this indented block and continue after it. |
| L224 | Raise `ValueError('cursor must not be blank')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L225 | Trim surrounding whitespace, compute how many base64 padding characters restore a multiple-of-four length, and append 0–3 '=' characters before decoding. |
| L226 | Enter the protected block; failures are matched against `Exception` in order. |
| L227 | Evaluate the right-hand side, then bind/store it in `decoded`: `base64.urlsafe_b64decode(padded.encode('ascii'))` — Decode URL-safe base64 to bytes; this does not authenticate the cursor; inputs include `padded.encode('ascii')` — Encode the text into bytes with the selected encoding. |
| L228 | Evaluate the right-hand side, then bind/store it in `payload`: `json.loads(decoded.decode('utf-8'))` — Parse JSON text/bytes into Python values; malformed JSON raises a decoding error; inputs include `decoded.decode('utf-8')` — Decode bytes into text with the selected encoding. |
| L229 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L230 | Raise `ValueError('invalid cursor')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L231 | Evaluate the branch condition: invert the truthiness of `isinstance(payload, dict)`. If truthy, enter L232; otherwise skip this indented block and continue after it. |
| L232 | Raise `ValueError('invalid cursor')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L233 | Compute the return value: the current `payload` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
