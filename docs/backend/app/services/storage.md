# `app/services/storage.py`

[Source](../../../../Backend/app/services/storage.py) · [Backend index](../../README.md)

Private Appwrite Storage adapter, PDF byte/range helpers, environment configuration, and an application-local in-memory adapter. Database ownership checks belong to callers; storage uses bucket/file identifiers and a server API key.

## Constants and errors

- Imports the 25 MiB / 200-page budgets. PDF constants are `.pdf`, `application/pdf`, and `%PDF-`; `V2_CHROMA_COLLECTION = "documind_chunks_v2"`.
- `STORAGE_BUCKET_SETTINGS` describes file security enabled, no bucket permissions, PDF-only extension, 25 MiB cap, encryption enabled, antivirus disabled, no compression, transformations disabled. The constant itself does not create or update a remote bucket.
- `APPWRITE_REQUIRED_SCOPES` lists bucket read/write and file create/read/update/delete scopes.
- `StorageError` is the base; `StorageNotFoundError`, `StorageUnavailableError`, `StorageConflictError`, and `RangeNotSatisfiableError` distinguish adapter failures. API handlers translate them to safe HTTP responses. `_wrap` can retain raw provider text internally, so callers should not expose its exception string directly.

## Pure helpers and configuration

### `StorageNotFoundError.__init__(self, bucket_id: str, file_id: str) -> None`

**Arguments:** Missing storage identifiers. **Returns:** `None`. **Work:** Sets an informative exception message and stores both identifiers for handling.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-storagenotfounderror---init--"></a>

#### Line-by-line execution

[Current source: lines 175–178](../../../../Backend/app/services/storage.py#L175-L178). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; positional or keyword | Appwrite bucket identifier. |
| `file_id` | `str`; required; positional or keyword | Reserved Appwrite storage-object identifier. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 175 |     def __init__(self, bucket_id: str, file_id: str) -> None:
 176 |         super().__init__(f"storage file not found: bucket={bucket_id!r} file={file_id!r}")
 177 |         self.bucket_id = bucket_id
 178 |         self.file_id = file_id
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L175 | Define `StorageNotFoundError.__init__`; bind its arguments when called. The body executes only when invoked. |
| L176 | `super().__init__(f'storage file not found: bucket={bucket_id!r} file={file_id!r}')` — Initialize the base exception/object with the supplied arguments; first obtain the receiver: `super()` — Resolve the superclass proxy for the current method and instance. The return value is not assigned here. |
| L177 | Evaluate the right-hand side, then bind/store it in `self.bucket_id`: the current `bucket_id` value. |
| L178 | Evaluate the right-hand side, then bind/store it in `self.file_id`: the current `file_id` value. |

<!-- END LINE WALKTHROUGH -->

### `RangeNotSatisfiableError.__init__(self, size: int) -> None`

**Arguments:** Full file byte length. **Returns:** `None`. **Work:** Sets the exception message and `.size`, used to generate `Content-Range: bytes */N` for HTTP 416.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-rangenotsatisfiableerror---init--"></a>

#### Line-by-line execution

[Current source: lines 192–194](../../../../Backend/app/services/storage.py#L192-L194). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `size` | `int`; required; positional or keyword | Caller-supplied size; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 192 |     def __init__(self, size: int) -> None:
 193 |         super().__init__(f"range not satisfiable for size {size}")
 194 |         self.size = size
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L192 | Define `RangeNotSatisfiableError.__init__`; bind its arguments when called. The body executes only when invoked. |
| L193 | `super().__init__(f'range not satisfiable for size {size}')` — Initialize the base exception/object with the supplied arguments; first obtain the receiver: `super()` — Resolve the superclass proxy for the current method and instance. The return value is not assigned here. |
| L194 | Evaluate the right-hand side, then bind/store it in `self.size`: the current `size` value. |

<!-- END LINE WALKTHROUGH -->

### `generate_appwrite_file_id() -> str`

**Arguments:** None. **Returns:** 32 lowercase hexadecimal UUID characters. **Work:** Allocates `uuid.uuid4().hex` before reservation so an interrupted upload remains addressable by its durable file ID.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-generate-appwrite-file-id"></a>

#### Line-by-line execution

[Current source: lines 205–213](../../../../Backend/app/services/storage.py#L205-L213). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 205 | def generate_appwrite_file_id() -> str:
 206 |     """Allocate a reserved Appwrite file ID (32 lowercase hex chars).
 207 | 
 208 |     Appwrite custom IDs allow ``a-z0-9-. _`` up to 36 chars and must not
 209 |     start with a special character; a UUID hex string always satisfies
 210 |     this.  The ID is allocated *before* the PostgreSQL reservation so
 211 |     the file is addressable during reconciliation (plan §5.1).
 212 |     """
 213 |     return uuid.uuid4().hex
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L205 | Define `generate_appwrite_file_id`; bind its arguments when called. The body executes only when invoked. |
| L206 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L208 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L209 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L210 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L211 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L212 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L213 | Compute the return value: the `hex` attribute of `uuid.uuid4()`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `sha256_hex(data: bytes) -> str`

**Arguments:** Complete file bytes. **Returns:** Lowercase 64-character SHA-256 digest. **Work:** Calls `hashlib.sha256(data).hexdigest()` without modifying data.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-sha256-hex"></a>

#### Line-by-line execution

[Current source: lines 216–218](../../../../Backend/app/services/storage.py#L216-L218). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `data` | `bytes`; required; positional or keyword | File bytes or input payload consumed by this operation, as specified by the annotation. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 216 | def sha256_hex(data: bytes) -> str:
 217 |     """Content fingerprint stored as ``document.content_sha256``."""
 218 |     return hashlib.sha256(data).hexdigest()
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L216 | Define `sha256_hex`; bind its arguments when called. The body executes only when invoked. |
| L217 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L218 | Compute the return value: `hashlib.sha256(data).hexdigest()` — Return the accumulated digest as lowercase hexadecimal text; first obtain the receiver: `hashlib.sha256(data)` — Create a SHA-256 digest state, optionally seeded with the supplied bytes. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `is_pdf_filename(filename: str) -> bool`

**Arguments:** Candidate basename. **Returns:** Whether it is nonblank, already trimmed, contains none of `/`, `\`, `:`, NUL, and ends case-insensitively in `.pdf` with a preceding basename. **Work:** Applies those string checks; it does not parse file contents or enforce the database's 255-character name limit.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-is-pdf-filename"></a>

#### Line-by-line execution

[Current source: lines 221–232](../../../../Backend/app/services/storage.py#L221-L232). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `filename` | `str`; required; positional or keyword | Display filename/citation hint, not proof of ownership or document identity. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 221 | def is_pdf_filename(filename: str) -> bool:
 222 |     """True when ``filename`` is a bare ``.pdf`` basename."""
 223 |     if not filename or filename.strip() != filename:
 224 |         return False
 225 |     if any(c in filename for c in ("/", "\\", ":", "\x00")):
 226 |         return False
 227 |     if filename != filename.strip():
 228 |         return False
 229 |     # Path(filename).name must equal filename (reject dir components).
 230 |     # Compare without importing pathlib for purity: any separator was
 231 |     # already rejected above, so only the extension check remains.
 232 |     return filename.lower().endswith(PDF_EXTENSION) and len(filename) > len(PDF_EXTENSION)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L221 | Define `is_pdf_filename`; bind its arguments when called. The body executes only when invoked. |
| L222 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L223 | Evaluate the branch condition: evaluate `not filename or filename.strip() != filename` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L224; otherwise skip this indented block and continue after it. |
| L224 | Compute the return value: `False`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L225 | Evaluate the branch condition: `any((c in filename for c in ('/', '\\', ':', '\x00')))` — Evaluate the iterable lazily, stopping at the first truthy item (True); empty input gives False; inputs include iterate `('/', '\\', ':', '\x00')`, binding each item to `c`; produce `c in filename` into a lazy generator (items computed when consumed). If truthy, enter L226; otherwise skip this indented block and continue after it. |
| L226 | Compute the return value: `False`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L227 | Evaluate the branch condition: compare whether `filename` differs from `filename.strip()`. If truthy, enter L228; otherwise skip this indented block and continue after it. |
| L228 | Compute the return value: `False`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L229 | Comment only: Path(filename).name must equal filename (reject dir components).. It does not execute; the neighboring code determines behavior. |
| L230 | Comment only: Compare without importing pathlib for purity: any separator was. It does not execute; the neighboring code determines behavior. |
| L231 | Comment only: already rejected above, so only the extension check remains.. It does not execute; the neighboring code determines behavior. |
| L232 | Compute the return value: evaluate `filename.lower().endswith(PDF_EXTENSION) and len(filename) > len(PDF_EXTENSION)` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `validate_pdf_bytes(data: bytes, filename: str, *, max_size=MAX_PDF_SIZE_BYTES) -> str`

**Arguments:** File bytes, basename, optional byte budget. **Returns:** SHA-256 digest. **Work:** Validates filename, nonempty content, byte count, and leading PDF magic in that order; raises a safe `ValueError` on rejection. Complete parsing/page limits are handled by `rag.pdf`, not this helper.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-validate-pdf-bytes"></a>

#### Line-by-line execution

[Current source: lines 235–256](../../../../Backend/app/services/storage.py#L235-L256). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `data` | `bytes`; required; positional or keyword | File bytes or input payload consumed by this operation, as specified by the annotation. |
| `filename` | `str`; required; positional or keyword | Display filename/citation hint, not proof of ownership or document identity. |
| `max_size` | `int`; default `MAX_PDF_SIZE_BYTES`; keyword-only | Caller-supplied max size; each read, transformation, and validation is traced below. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 235 | def validate_pdf_bytes(data: bytes, filename: str, *, max_size: int = MAX_PDF_SIZE_BYTES) -> str:
 236 |     """Validate staged PDF bytes; return the SHA-256 hex fingerprint.
 237 | 
 238 |     Raises ``ValueError`` with a human-safe message for each rejection
 239 |     (empty, oversized, bad extension, bad magic).  Extractability (at
 240 |     least one text-bearing page via ``process_pdf``) is checked by the
 241 |     document API before reservation so rejected uploads leave no row,
 242 |     job, or storage object (UPL-04).  This helper covers the
 243 |     size/magic/filename half so storage-level callers (A4 worker) can
 244 |     reuse it without the API concern.
 245 |     """
 246 |     if not is_pdf_filename(filename):
 247 |         raise ValueError("Only PDF files are supported.")
 248 |     if not data:
 249 |         raise ValueError("PDF file is empty.")
 250 |     if len(data) > max_size:
 251 |         raise ValueError(
 252 |             f"PDF file exceeds the {max_size}-byte limit."
 253 |         )
 254 |     if not data.startswith(PDF_MAGIC):
 255 |         raise ValueError("Only PDF files are supported.")
 256 |     return sha256_hex(data)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L235 | Define `validate_pdf_bytes`; bind its arguments when called. The body executes only when invoked. |
| L236 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L238 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L239 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L240 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L241 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L242 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L243 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L244 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L245 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L246 | Evaluate the branch condition: invert the truthiness of `is_pdf_filename(filename)`. If truthy, enter L247; otherwise skip this indented block and continue after it. |
| L247 | Raise `ValueError('Only PDF files are supported.')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L248 | Evaluate the branch condition: invert the truthiness of `data`. If truthy, enter L249; otherwise skip this indented block and continue after it. |
| L249 | Raise `ValueError('PDF file is empty.')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L250 | Evaluate the branch condition: compare whether `len(data)` is greater than `max_size`. If truthy, enter L251; otherwise skip this indented block and continue after it. |
| L251 | Raise `ValueError(f'PDF file exceeds the {max_size}-byte limit.')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L252 | Supply positional argument 1 to `ValueError`: format a string by inserting `max_size` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L253 | Close the expression/container begun at L251; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L254 | Evaluate the branch condition: invert the truthiness of `data.startswith(PDF_MAGIC)`. If truthy, enter L255; otherwise skip this indented block and continue after it. |
| L255 | Raise `ValueError('Only PDF files are supported.')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L256 | Compute the return value: `sha256_hex(data)` — Call [sha256_hex](#walk-sha256-hex) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `owner_file_permissions(appwrite_user_id: str) -> list[str]`

**Arguments:** External Appwrite account ID. **Returns:** Read/update/delete permission strings for `user:<id>`. **Work:** Rejects missing/whitespace-only IDs, interpolates the supplied ID into three Appwrite permission expressions. It does not translate internal database UUIDs or trim a nonblank ID.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-owner-file-permissions"></a>

#### Line-by-line execution

[Current source: lines 259–275](../../../../Backend/app/services/storage.py#L259-L275). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `appwrite_user_id` | `str`; required; positional or keyword | Verified external Appwrite identity, distinct from the internal PostgreSQL UUID. |

**Declared result:** `list[str]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 259 | def owner_file_permissions(appwrite_user_id: str) -> list[str]:
 260 |     """Owner-only Appwrite permission strings for one file.
 261 | 
 262 |     ``appwrite_user_id`` is the *external* Appwrite account ID (never
 263 |     the internal ``users.id`` UUID).  Bucket-level permissions stay
 264 |     empty and file-level security is enabled, so direct Appwrite
 265 |     access is restricted to the owner while the server API key
 266 |     mediates all application reads/writes/deletes.
 267 |     """
 268 |     if not appwrite_user_id or not appwrite_user_id.strip():
 269 |         raise ValueError("appwrite_user_id is required for owner permissions")
 270 |     target = f"user:{appwrite_user_id}"
 271 |     return [
 272 |         f'read("{target}")',
 273 |         f'update("{target}")',
 274 |         f'delete("{target}")',
 275 |     ]
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L259 | Define `owner_file_permissions`; bind its arguments when called. The body executes only when invoked. |
| L260 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L262 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L263 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L264 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L265 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L266 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L267 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L268 | Evaluate the branch condition: evaluate `not appwrite_user_id or not appwrite_user_id.strip()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L269; otherwise skip this indented block and continue after it. |
| L269 | Raise `ValueError('appwrite_user_id is required for owner permissions')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L270 | Evaluate the right-hand side, then bind/store it in `target`: format a string by inserting `appwrite_user_id` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L271 | Compute the return value: build a list containing `f'read("{target}")'`, `f'update("{target}")'`, `f'delete("{target}")'`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L272 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L273 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L274 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L275 | Close the expression/container begun at L271; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `make_resource_snapshot(*, bucket_id, file_id, file_name, file_size, content_sha256, chroma_collection=V2_CHROMA_COLLECTION, active_index_version=None) -> dict[str, Any]`

**Arguments:** Trusted storage references, display name, integer byte size, hash, collection name, optional version string. **Returns:** A new JSON-compatible dictionary containing those fields. **Work:** Copies required values and adds `active_index_version` only when non-null. This producer uses `file_size`/`content_sha256`; worker readers also understand alternate expected-size/hash keys. It performs no I/O or validation.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-make-resource-snapshot"></a>

#### Line-by-line execution

[Current source: lines 278–304](../../../../Backend/app/services/storage.py#L278-L304). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |
| `file_name` | `str`; required; keyword-only | Display PDF filename; immutable IDs establish ownership and evidence identity. |
| `file_size` | `int`; required; keyword-only | PDF size in bytes recorded in document metadata or checked during upload. |
| `content_sha256` | `str`; required; keyword-only | Lowercase SHA-256 content fingerprint used for upload identity/integrity expectations. |
| `chroma_collection` | `str`; default `V2_CHROMA_COLLECTION`; keyword-only | Caller-supplied chroma collection; each read, transformation, and validation is traced below. |
| `active_index_version` | `str \| None`; default `None`; keyword-only | Caller-supplied active index version; each read, transformation, and validation is traced below. |

**Declared result:** `dict[str, Any]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 278 | def make_resource_snapshot(
 279 |     *,
 280 |     bucket_id: str,
 281 |     file_id: str,
 282 |     file_name: str,
 283 |     file_size: int,
 284 |     content_sha256: str,
 285 |     chroma_collection: str = V2_CHROMA_COLLECTION,
 286 |     active_index_version: str | None = None,
 287 | ) -> dict[str, Any]:
 288 |     """Immutable ``processing_jobs.resource_snapshot`` for one document.
 289 | 
 290 |     Carries trusted bucket/file/Chroma references so job history and
 291 |     cleanup survive deletion of the document/project rows (plan §3.2).
 292 |     The snapshot is a JSON *object* (DB check ``resource_snapshot_is_object``).
 293 |     """
 294 |     snapshot: dict[str, Any] = {
 295 |         "bucket_id": bucket_id,
 296 |         "file_id": file_id,
 297 |         "file_name": file_name,
 298 |         "file_size": file_size,
 299 |         "content_sha256": content_sha256,
 300 |         "chroma_collection": chroma_collection,
 301 |     }
 302 |     if active_index_version is not None:
 303 |         snapshot["active_index_version"] = active_index_version
 304 |     return snapshot
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L278 | Define `make_resource_snapshot`; bind its arguments when called. The body executes only when invoked. |
| L279 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L280 | Declare parameter `bucket_id` with annotation `str`. Appwrite bucket identifier. |
| L281 | Declare parameter `file_id` with annotation `str`. Reserved Appwrite storage-object identifier. |
| L282 | Declare parameter `file_name` with annotation `str`. Display PDF filename; immutable IDs establish ownership and evidence identity. |
| L283 | Declare parameter `file_size` with annotation `int`. PDF size in bytes recorded in document metadata or checked during upload. |
| L284 | Declare parameter `content_sha256` with annotation `str`. Lowercase SHA-256 content fingerprint used for upload identity/integrity expectations. |
| L285 | Declare parameter `chroma_collection` with annotation `str`. Caller-supplied chroma collection; its uses and transformations are traced below. |
| L286 | Declare parameter `active_index_version` with annotation `str \| None`. Caller-supplied active index version; its uses and transformations are traced below. |
| L287 | Finish/continue the signature; the declared return annotation is `dict[str, Any]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L288 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L290 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L291 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L292 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L293 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L294 | Evaluate the right-hand side, then bind/store it in `snapshot`: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. |
| L295 | Add mapping entry `'bucket_id'`: the current `bucket_id` value. |
| L296 | Add mapping entry `'file_id'`: the current `file_id` value. |
| L297 | Add mapping entry `'file_name'`: the current `file_name` value. |
| L298 | Add mapping entry `'file_size'`: the current `file_size` value. |
| L299 | Add mapping entry `'content_sha256'`: the current `content_sha256` value. |
| L300 | Add mapping entry `'chroma_collection'`: the current `chroma_collection` value. |
| L301 | Close the expression/container begun at L294; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L302 | Evaluate the branch condition: compare whether `active_index_version` is not the same object as `None`. If truthy, enter L303; otherwise skip this indented block and continue after it. |
| L303 | Evaluate the right-hand side, then bind/store it in `snapshot['active_index_version']`: the current `active_index_version` value. |
| L304 | Compute the return value: the current `snapshot` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `apply_range(data: bytes, range_header: str | None, *, mime_type=PDF_MIME_TYPE) -> tuple[bytes, dict[str, str]]`

- **Arguments:** Full file bytes, optional HTTP Range, response MIME.
- **Returns:** Full or sliced bytes and `Accept-Ranges`, `Content-Type`, `Content-Length`; valid slices additionally have `Content-Range`.
- **Work:** Two regular expressions parse one `bytes=start-end`, `bytes=start-`, or `bytes=-suffix` range. Missing/invalid syntax and multiple ranges fall back to the full body. Suffixes clamp to the file start, end positions clamp to its final byte, and inclusive bounds are converted to Python's exclusive-end slicing.
- **Errors:** Valid but impossible ranges (empty file, zero suffix, start after end/outside file) raise `RangeNotSatisfiableError`. The caller chooses HTTP 200/206/416 based on result/error.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-apply-range"></a>

#### Line-by-line execution

[Current source: lines 307–361](../../../../Backend/app/services/storage.py#L307-L361). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `data` | `bytes`; required; positional or keyword | File bytes or input payload consumed by this operation, as specified by the annotation. |
| `range_header` | `str \| None`; required; positional or keyword | Optional HTTP byte-range selector; parsing determines full, partial, or unsatisfiable behavior. |
| `mime_type` | `str`; default `PDF_MIME_TYPE`; keyword-only | Declared storage content type; accepted application uploads use application/pdf. |

**Declared result:** `tuple[bytes, dict[str, str]]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 307 | def apply_range(
 308 |     data: bytes, range_header: str | None, *, mime_type: str = PDF_MIME_TYPE
 309 | ) -> tuple[bytes, dict[str, str]]:
 310 |     """Slice ``data`` per an HTTP ``Range`` header; return ``(bytes, headers)``.
 311 | 
 312 |     * No header / invalid syntax -> full body headers (``200``).
 313 |     * Valid satisfiable range -> sliced body + ``Content-Range`` (``206``).
 314 |     * Valid unsatisfiable range -> raise :class:`RangeNotSatisfiableError` (``416``).
 315 | 
 316 |     Multi-range requests (``bytes=0-4,10-19``) are treated as invalid syntax
 317 |     and fall back to a full download.
 318 |     """
 319 |     size = len(data)
 320 |     headers: dict[str, str] = {
 321 |         "Accept-Ranges": "bytes",
 322 |         "Content-Type": mime_type,
 323 |         "Content-Length": str(size),
 324 |     }
 325 |     if not range_header or not range_header.strip():
 326 |         return data, headers
 327 |     match = _RANGE_RE.match(range_header)
 328 |     if match is None:
 329 |         return data, headers
 330 |     rest = match.group("rest")
 331 |     if "," in rest:  # multipart ranges unsupported -> full download
 332 |         return data, headers
 333 |     single = _RANGE_SINGLE_RE.match(rest.strip())
 334 |     if single is None:
 335 |         return data, headers
 336 |     start_raw = single.group("start")
 337 |     end_raw = single.group("end")
 338 |     if start_raw == "" and end_raw == "":
 339 |         return data, headers
 340 |     if size == 0:
 341 |         raise RangeNotSatisfiableError(size)
 342 | 
 343 |     if start_raw == "":
 344 |         # Suffix range: last N bytes.
 345 |         suffix = int(end_raw)
 346 |         if suffix == 0:
 347 |             raise RangeNotSatisfiableError(size)
 348 |         start = max(size - suffix, 0)
 349 |         end = size - 1
 350 |     else:
 351 |         start = int(start_raw)
 352 |         end = int(end_raw) if end_raw != "" else size - 1
 353 |         if start > end or start >= size:
 354 |             raise RangeNotSatisfiableError(size)
 355 |         if end >= size:
 356 |             end = size - 1
 357 | 
 358 |     sliced = data[start : end + 1]
 359 |     headers["Content-Length"] = str(len(sliced))
 360 |     headers["Content-Range"] = f"bytes {start}-{end}/{size}"
 361 |     return sliced, headers
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L307 | Define `apply_range`; bind its arguments when called. The body executes only when invoked. |
| L308 | Declare parameter `data` with annotation `bytes`. File bytes or input payload consumed by this operation, as specified by the annotation. Declare parameter `range_header` with annotation `str \| None`. Optional HTTP byte-range selector; parsing determines full, partial, or unsatisfiable behavior. Declare parameter `mime_type` with annotation `str`. Declared storage content type; accepted application uploads use application/pdf. |
| L309 | Finish/continue the signature; the declared return annotation is `tuple[bytes, dict[str, str]]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L310 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L312 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L313 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L314 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L316 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L317 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L318 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L319 | Evaluate the right-hand side, then bind/store it in `size`: `len(data)` — Count the items/characters in the supplied container/string. |
| L320 | Evaluate the right-hand side, then bind/store it in `headers`: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. |
| L321 | Add mapping entry `'Accept-Ranges'`: `'bytes'`. |
| L322 | Add mapping entry `'Content-Type'`: the current `mime_type` value. |
| L323 | Add mapping entry `'Content-Length'`: `str(size)` — Convert the input to its string representation. |
| L324 | Close the expression/container begun at L320; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L325 | Evaluate the branch condition: evaluate `not range_header or not range_header.strip()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L326; otherwise skip this indented block and continue after it. |
| L326 | Compute the return value: build a tuple containing `data`, `headers`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L327 | Evaluate the right-hand side, then bind/store it in `match`: `_RANGE_RE.match(range_header)` — Invoke `_RANGE_RE.match` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L328 | Evaluate the branch condition: compare whether `match` is the same object as `None`. If truthy, enter L329; otherwise skip this indented block and continue after it. |
| L329 | Compute the return value: build a tuple containing `data`, `headers`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L330 | Evaluate the right-hand side, then bind/store it in `rest`: `match.group('rest')` — Extract the specified capture group from the matched regular expression. |
| L331 | Evaluate the branch condition: compare whether `','` is contained in `rest`. If truthy, enter L332; otherwise skip this indented block and continue after it. |
| L332 | Compute the return value: build a tuple containing `data`, `headers`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L333 | Evaluate the right-hand side, then bind/store it in `single`: `_RANGE_SINGLE_RE.match(rest.strip())` — Invoke `_RANGE_SINGLE_RE.match` with the shown inputs and use its result; see the function overview for its role in this flow; inputs include `rest.strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed. |
| L334 | Evaluate the branch condition: compare whether `single` is the same object as `None`. If truthy, enter L335; otherwise skip this indented block and continue after it. |
| L335 | Compute the return value: build a tuple containing `data`, `headers`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L336 | Evaluate the right-hand side, then bind/store it in `start_raw`: `single.group('start')` — Extract the specified capture group from the matched regular expression. |
| L337 | Evaluate the right-hand side, then bind/store it in `end_raw`: `single.group('end')` — Extract the specified capture group from the matched regular expression. |
| L338 | Evaluate the branch condition: evaluate `start_raw == '' and end_raw == ''` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L339; otherwise skip this indented block and continue after it. |
| L339 | Compute the return value: build a tuple containing `data`, `headers`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L340 | Evaluate the branch condition: compare whether `size` equals `0`. If truthy, enter L341; otherwise skip this indented block and continue after it. |
| L341 | Raise `RangeNotSatisfiableError(size)`; stop the normal path and transfer control to the nearest matching exception handler. |
| L343 | Evaluate the branch condition: compare whether `start_raw` equals `''`. If truthy, enter L345; otherwise enter the alternative at L351. |
| L344 | Comment only: Suffix range: last N bytes.. It does not execute; the neighboring code determines behavior. |
| L345 | Evaluate the right-hand side, then bind/store it in `suffix`: `int(end_raw)` — Convert the input to an integer (using the optional numeric base). |
| L346 | Evaluate the branch condition: compare whether `suffix` equals `0`. If truthy, enter L347; otherwise skip this indented block and continue after it. |
| L347 | Raise `RangeNotSatisfiableError(size)`; stop the normal path and transfer control to the nearest matching exception handler. |
| L348 | Evaluate the right-hand side, then bind/store it in `start`: `max(size - suffix, 0)` — Choose the largest supplied value; nested min/max calls implement the stated bound; inputs include subtract `size` and `suffix`, following the parentheses/operator precedence shown in `size - suffix`. |
| L349 | Evaluate the right-hand side, then bind/store it in `end`: subtract `size` and `1`, following the parentheses/operator precedence shown in `size - 1`. |
| L350 | Enter this alternative only when the associated condition was false (or the associated try/loop completed without its exceptional exit). |
| L351 | Evaluate the right-hand side, then bind/store it in `start`: `int(start_raw)` — Convert the input to an integer (using the optional numeric base). |
| L352 | Evaluate the right-hand side, then bind/store it in `end`: check `end_raw != ''`; when true use `int(end_raw)` — Convert the input to an integer (using the optional numeric base), otherwise subtract `size` and `1`, following the parentheses/operator precedence shown in `size - 1` (only the selected branch is evaluated). |
| L353 | Evaluate the branch condition: evaluate `start > end or start >= size` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L354; otherwise skip this indented block and continue after it. |
| L354 | Raise `RangeNotSatisfiableError(size)`; stop the normal path and transfer control to the nearest matching exception handler. |
| L355 | Evaluate the branch condition: compare whether `end` is at least `size`. If truthy, enter L356; otherwise skip this indented block and continue after it. |
| L356 | Evaluate the right-hand side, then bind/store it in `end`: subtract `size` and `1`, following the parentheses/operator precedence shown in `size - 1`. |
| L358 | Evaluate the right-hand side, then bind/store it in `sliced`: slice `data` from `start` up to `end + 1` (exclusive stop). |
| L359 | Evaluate the right-hand side, then bind/store it in `headers['Content-Length']`: `str(len(sliced))` — Convert the input to its string representation; inputs include `len(sliced)` — Count the items/characters in the supplied container/string. |
| L360 | Evaluate the right-hand side, then bind/store it in `headers['Content-Range']`: format a string by inserting `start`, `end`, `size` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L361 | Compute the return value: build a tuple containing `sliced`, `headers`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_get_env(*names: str) -> str`

**Arguments:** Environment names in priority order. **Returns:** First nonempty stripped value, or `""`. **Work:** Reads process environment lazily and stops on the first match.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--get-env"></a>

#### Line-by-line execution

[Current source: lines 364–369](../../../../Backend/app/services/storage.py#L364-L369). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `names` | `str`; implicitly supplied/collected; * positional extras | Caller-supplied names; each read, transformation, and validation is traced below. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 364 | def _get_env(*names: str) -> str:
 365 |     for name in names:
 366 |         value = os.environ.get(name, "").strip()
 367 |         if value:
 368 |             return value
 369 |     return ""
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L364 | Define `_get_env`; bind its arguments when called. The body executes only when invoked. |
| L365 | Iterate `names` (the current `names` value), assigning each item to `name`. Execute the indented body once per item; an empty iterable skips it. |
| L366 | Evaluate the right-hand side, then bind/store it in `value`: `os.environ.get(name, '').strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed; first obtain the receiver: `os.environ.get(name, '')` — Read a process environment value without changing it, using the supplied fallback if absent. |
| L367 | Evaluate the branch condition: the current `value` value. If truthy, enter L368; otherwise skip this indented block and continue after it. |
| L368 | Compute the return value: the current `value` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L369 | Compute the return value: `''`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `default_bucket_id() -> str`

**Arguments:** None. **Returns:** `APPWRITE_STORAGE_BUCKET_ID`, falling back to `appwrite_file_key`. **Work:** Uses `_get_env`; raises `RuntimeError` when neither is configured.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-default-bucket-id"></a>

#### Line-by-line execution

[Current source: lines 372–379](../../../../Backend/app/services/storage.py#L372-L379). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 372 | def default_bucket_id() -> str:
 373 |     """Resolve the private PDF bucket ID, or raise ``RuntimeError`` if unset."""
 374 |     bucket = _get_env(APPWRITE_BUCKET_ENV, "appwrite_file_key")
 375 |     if not bucket:
 376 |         raise RuntimeError(
 377 |             f"{APPWRITE_BUCKET_ENV} is required but is not set."
 378 |         )
 379 |     return bucket
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L372 | Define `default_bucket_id`; bind its arguments when called. The body executes only when invoked. |
| L373 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L374 | Evaluate the right-hand side, then bind/store it in `bucket`: `_get_env(APPWRITE_BUCKET_ENV, 'appwrite_file_key')` — Call [_get_env](#walk--get-env) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L375 | Evaluate the branch condition: invert the truthiness of `bucket`. If truthy, enter L376; otherwise skip this indented block and continue after it. |
| L376 | Raise `RuntimeError(f'{APPWRITE_BUCKET_ENV} is required but is not set.')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L377 | Supply positional argument 1 to `RuntimeError`: format a string by inserting `APPWRITE_BUCKET_ENV` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L378 | Close the expression/container begun at L376; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L379 | Compute the return value: the current `bucket` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `storage_config() -> dict[str, str]`

**Arguments:** None. **Returns:** `endpoint`, `project_id`, `api_key`, `bucket_id`. **Work:** Reads standardized variables first, then aliases `appwrite_site_endpoint`, `appwrite_project_id`, `appwrite`, `appwrite_file_key`. Collects missing setting names and raises one `RuntimeError` if any are absent. Unlike auth endpoint lookup, storage has no default endpoint/public-variable fallback.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-storage-config"></a>

#### Line-by-line execution

[Current source: lines 382–412](../../../../Backend/app/services/storage.py#L382-L412). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `dict[str, str]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 382 | def storage_config() -> dict[str, str]:
 383 |     """Resolve endpoint/project/key/bucket or raise ``RuntimeError``.
 384 | 
 385 |     Standardized names take precedence; legacy root-``.env`` names are
 386 |     fallbacks.  Called lazily by :func:`get_storage_adapter`, never at
 387 |     import time, so importing this module never requires credentials.
 388 |     """
 389 |     endpoint = _get_env(APPWRITE_ENDPOINT_ENV, "appwrite_site_endpoint", "APPWRITE_ENDPOINT")
 390 |     project_id = _get_env(APPWRITE_PROJECT_ID_ENV, "appwrite_project_id")
 391 |     api_key = _get_env(APPWRITE_API_KEY_ENV, "appwrite", "APPWRITE_API_KEY")
 392 |     bucket = _get_env(APPWRITE_BUCKET_ENV, "appwrite_file_key")
 393 |     missing = [
 394 |         label
 395 |         for label, value in (
 396 |             (APPWRITE_ENDPOINT_ENV, endpoint),
 397 |             (APPWRITE_PROJECT_ID_ENV, project_id),
 398 |             (APPWRITE_API_KEY_ENV, api_key),
 399 |             (APPWRITE_BUCKET_ENV, bucket),
 400 |         )
 401 |         if not value
 402 |     ]
 403 |     if missing:
 404 |         raise RuntimeError(
 405 |             "Appwrite Storage configuration missing: " + ", ".join(missing)
 406 |         )
 407 |     return {
 408 |         "endpoint": endpoint,
 409 |         "project_id": project_id,
 410 |         "api_key": api_key,
 411 |         "bucket_id": bucket,
 412 |     }
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L382 | Define `storage_config`; bind its arguments when called. The body executes only when invoked. |
| L383 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L385 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L386 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L387 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L388 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L389 | Evaluate the right-hand side, then bind/store it in `endpoint`: `_get_env(APPWRITE_ENDPOINT_ENV, 'appwrite_site_endpoint', 'APPWRITE_ENDPOINT')` — Call [_get_env](#walk--get-env) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L390 | Evaluate the right-hand side, then bind/store it in `project_id`: `_get_env(APPWRITE_PROJECT_ID_ENV, 'appwrite_project_id')` — Call [_get_env](#walk--get-env) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L391 | Evaluate the right-hand side, then bind/store it in `api_key`: `_get_env(APPWRITE_API_KEY_ENV, 'appwrite', 'APPWRITE_API_KEY')` — Call [_get_env](#walk--get-env) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L392 | Evaluate the right-hand side, then bind/store it in `bucket`: `_get_env(APPWRITE_BUCKET_ENV, 'appwrite_file_key')` — Call [_get_env](#walk--get-env) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L393 | Evaluate the right-hand side, then bind/store it in `missing`: iterate `((APPWRITE_ENDPOINT_ENV, endpoint), (APPWRITE_PROJECT_ID_ENV, project_id), (APPWRITE_API_KEY_ENV, api_key), (APPWRITE_BUCKET_ENV, bucket))`, binding each item to `(label, value)` and retain only items satisfying `not value`; produce `label` into a new list. |
| L394 | Contribute the current `label` value to the expression being assembled. |
| L395 | Contribute build a tuple containing `label`, `value` to the expression being assembled. |
| L396 | Contribute build a tuple containing `APPWRITE_ENDPOINT_ENV`, `endpoint` to the expression being assembled. |
| L397 | Contribute build a tuple containing `APPWRITE_PROJECT_ID_ENV`, `project_id` to the expression being assembled. |
| L398 | Contribute build a tuple containing `APPWRITE_API_KEY_ENV`, `api_key` to the expression being assembled. |
| L399 | Contribute build a tuple containing `APPWRITE_BUCKET_ENV`, `bucket` to the expression being assembled. |
| L400 | Close the expression/container begun at L395; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L401 | Contribute invert the truthiness of `value` to the expression being assembled. |
| L402 | Close the expression/container begun at L393; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L403 | Evaluate the branch condition: the current `missing` value. If truthy, enter L404; otherwise skip this indented block and continue after it. |
| L404 | Raise `RuntimeError('Appwrite Storage configuration missing: ' + ', '.join(missing))`; stop the normal path and transfer control to the nearest matching exception handler. |
| L405 | Join the supplied string items using `', '` between adjacent items. |
| L406 | Close the expression/container begun at L404; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L407 | Compute the return value: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L408 | Add mapping entry `'endpoint'`: the current `endpoint` value. |
| L409 | Add mapping entry `'project_id'`: the current `project_id` value. |
| L410 | Add mapping entry `'api_key'`: the current `api_key` value. |
| L411 | Add mapping entry `'bucket_id'`: the current `bucket` value. |
| L412 | Close the expression/container begun at L407; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

## `AppwriteStorageAdapter`

### `AppwriteStorageAdapter.__init__(self, *, endpoint: str, project_id: str, api_key: str, bucket_id: str | None = None) -> None`

**Arguments:** Explicit server connection settings, optional bucket default. **Returns:** `None`. **Work:** Lazily imports SDK classes, stores configuration, resolves a missing bucket, and constructs a configured `Client` plus `Storage` service. Construction itself does not upload or inspect files.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-appwritestorageadapter---init--"></a>

#### Line-by-line execution

[Current source: lines 429–450](../../../../Backend/app/services/storage.py#L429-L450). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `endpoint` | `str`; required; keyword-only | Caller-supplied endpoint; each read, transformation, and validation is traced below. |
| `project_id` | `str`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `api_key` | `str`; required; keyword-only | Server-side provider credential; do not expose it to browser configuration. |
| `bucket_id` | `str \| None`; default `None`; keyword-only | Appwrite bucket identifier. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 429 |     def __init__(
 430 |         self,
 431 |         *,
 432 |         endpoint: str,
 433 |         project_id: str,
 434 |         api_key: str,
 435 |         bucket_id: str | None = None,
 436 |     ) -> None:
 437 |         from appwrite.client import Client
 438 |         from appwrite.services.storage import Storage
 439 | 
 440 |         self.endpoint = endpoint
 441 |         self.project_id = project_id
 442 |         self._api_key = api_key
 443 |         self.bucket_id = bucket_id or default_bucket_id()
 444 |         client = (
 445 |             Client()
 446 |             .set_endpoint(endpoint)
 447 |             .set_project(project_id)
 448 |             .set_key(api_key)
 449 |         )
 450 |         self.storage = Storage(client)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L429 | Define `AppwriteStorageAdapter.__init__`; bind its arguments when called. The body executes only when invoked. |
| L430 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L431 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L432 | Declare parameter `endpoint` with annotation `str`. Caller-supplied endpoint; its uses and transformations are traced below. |
| L433 | Declare parameter `project_id` with annotation `str`. Project UUID used to constrain resource lookup or provider metadata. |
| L434 | Declare parameter `api_key` with annotation `str`. Server-side provider credential; do not expose it to browser configuration. |
| L435 | Declare parameter `bucket_id` with annotation `str \| None`. Appwrite bucket identifier. |
| L436 | Finish/continue the signature; the declared return annotation is `None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L437 | Import `Client` from `appwrite.client`; inside a function this import is deferred until this path is reached. |
| L438 | Import `Storage` from `appwrite.services.storage`; inside a function this import is deferred until this path is reached. |
| L440 | Evaluate the right-hand side, then bind/store it in `self.endpoint`: the current `endpoint` value. |
| L441 | Evaluate the right-hand side, then bind/store it in `self.project_id`: the current `project_id` value. |
| L442 | Evaluate the right-hand side, then bind/store it in `self._api_key`: the current `api_key` value. |
| L443 | Evaluate the right-hand side, then bind/store it in `self.bucket_id`: evaluate `bucket_id or default_bucket_id()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L444 | Evaluate the right-hand side, then bind/store it in `client`: `Client().set_endpoint(endpoint).set_project(project_id).set_key(api_key)` — Configure the server-only Appwrite API key on the client; first obtain the receiver: `Client().set_endpoint(endpoint).set_project(project_id)` — Set the Appwrite project identifier on the client and return the client for chaining; first obtain the receiver: `Client().set_endpoint(endpoint)` — Set the Appwrite service endpoint on the client and return the client for chaining. |
| L445 | `Client()` — Construct `Client` with the shown fields; its class/model initialization rules apply. |
| L446 | Set the Appwrite service endpoint on the client and return the client for chaining; apply this method to the result built by the preceding chain. |
| L447 | Set the Appwrite project identifier on the client and return the client for chaining; apply this method to the result built by the preceding chain. |
| L448 | Configure the server-only Appwrite API key on the client; apply this method to the result built by the preceding chain. |
| L449 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L450 | Evaluate the right-hand side, then bind/store it in `self.storage`: `Storage(client)` — Construct `Storage` with the shown fields; its class/model initialization rules apply. |

<!-- END LINE WALKTHROUGH -->

### `AppwriteStorageAdapter._metadata_to_info(metadata, *, bucket_id, file_id) -> StorageFileInfo`

**Arguments:** Provider metadata dictionary and fallback identifiers; static method. **Returns:** Normalized storage-info DTO. **Work:** Accepts camelCase or snake_case size/MIME/counter keys, coerces counters to integers, and uses provider IDs when available. A positive-size response with zero total chunks is normalized to one uploaded/total chunk. Completion means positive size/total and uploaded ≥ total; malformed numeric metadata can raise conversion errors.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-appwritestorageadapter--metadata-to-info"></a>

#### Line-by-line execution

[Current source: lines 454–480](../../../../Backend/app/services/storage.py#L454-L480). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `metadata` | `dict[str, Any]`; required; positional or keyword | Caller-supplied metadata; each read, transformation, and validation is traced below. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |

**Declared result:** `StorageFileInfo`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 454 |     @staticmethod
 455 |     def _metadata_to_info(
 456 |         metadata: dict[str, Any], *, bucket_id: str, file_id: str
 457 |     ) -> StorageFileInfo:
 458 |         size = int(
 459 |             metadata.get("sizeOriginal", metadata.get("size_original", 0)) or 0
 460 |         )
 461 |         mime = str(metadata.get("mimeType", metadata.get("mime_type", PDF_MIME_TYPE)) or PDF_MIME_TYPE)
 462 |         chunks_total = int(metadata.get("chunksTotal", metadata.get("chunks_total", 0)) or 0)
 463 |         chunks_uploaded = int(
 464 |             metadata.get("chunksUploaded", metadata.get("chunks_uploaded", 0)) or 0
 465 |         )
 466 |         # A single-chunk file reports chunks_total == 1; treat a
 467 |         # zero-counter response with a non-zero size as completed
 468 |         # (defensive against SDK/version drift).
 469 |         if chunks_total == 0 and size > 0:
 470 |             chunks_total = chunks_uploaded = 1
 471 |         completed = size > 0 and chunks_total > 0 and chunks_uploaded >= chunks_total
 472 |         return StorageFileInfo(
 473 |             file_id=str(metadata.get("$id", metadata.get("id", file_id))),
 474 |             bucket_id=str(metadata.get("bucketId", metadata.get("bucket_id", bucket_id))),
 475 |             size=size,
 476 |             mime_type=mime,
 477 |             chunks_uploaded=chunks_uploaded,
 478 |             chunks_total=chunks_total,
 479 |             completed=completed,
 480 |         )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L454 | Expose this function on the class without automatically supplying self or cls. |
| L455 | Define `AppwriteStorageAdapter._metadata_to_info`; bind its arguments when called. The body executes only when invoked. |
| L456 | Declare parameter `metadata` with annotation `dict[str, Any]`. Caller-supplied metadata; its uses and transformations are traced below. Declare parameter `bucket_id` with annotation `str`. Appwrite bucket identifier. Declare parameter `file_id` with annotation `str`. Reserved Appwrite storage-object identifier. |
| L457 | Finish/continue the signature; the declared return annotation is `StorageFileInfo`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L458 | Evaluate the right-hand side, then bind/store it in `size`: `int(metadata.get('sizeOriginal', metadata.get('size_original', 0)) or 0)` — Convert the input to an integer (using the optional numeric base). |
| L459 | `metadata.get('sizeOriginal', metadata.get('size_original', 0))` — Look up `'sizeOriginal'` in `metadata`, using `metadata.get('size_original', 0)` when the key is absent (an existing null value is not replaced); inputs include `metadata.get('size_original', 0)` — Look up `'size_original'` in `metadata`, using `0` when the key is absent (an existing null value is not replaced). |
| L460 | Close the expression/container begun at L458; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L461 | Evaluate the right-hand side, then bind/store it in `mime`: `str(metadata.get('mimeType', metadata.get('mime_type', PDF_MIME_TYPE)) or PDF_MIME_TYPE)` — Convert the input to its string representation. |
| L462 | Evaluate the right-hand side, then bind/store it in `chunks_total`: `int(metadata.get('chunksTotal', metadata.get('chunks_total', 0)) or 0)` — Convert the input to an integer (using the optional numeric base). |
| L463 | Evaluate the right-hand side, then bind/store it in `chunks_uploaded`: `int(metadata.get('chunksUploaded', metadata.get('chunks_uploaded', 0)) or 0)` — Convert the input to an integer (using the optional numeric base). |
| L464 | `metadata.get('chunksUploaded', metadata.get('chunks_uploaded', 0))` — Look up `'chunksUploaded'` in `metadata`, using `metadata.get('chunks_uploaded', 0)` when the key is absent (an existing null value is not replaced); inputs include `metadata.get('chunks_uploaded', 0)` — Look up `'chunks_uploaded'` in `metadata`, using `0` when the key is absent (an existing null value is not replaced). |
| L465 | Close the expression/container begun at L463; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L466 | Comment only: A single-chunk file reports chunks_total == 1; treat a. It does not execute; the neighboring code determines behavior. |
| L467 | Comment only: zero-counter response with a non-zero size as completed. It does not execute; the neighboring code determines behavior. |
| L468 | Comment only: (defensive against SDK/version drift).. It does not execute; the neighboring code determines behavior. |
| L469 | Evaluate the branch condition: evaluate `chunks_total == 0 and size > 0` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L470; otherwise skip this indented block and continue after it. |
| L470 | Evaluate the right-hand side, then bind/store it in `chunks_total`, `chunks_uploaded`: `1`. |
| L471 | Evaluate the right-hand side, then bind/store it in `completed`: evaluate `size > 0 and chunks_total > 0 and (chunks_uploaded >= chunks_total)` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. |
| L472 | Compute the return value: `StorageFileInfo` with the arguments detailed below — Construct `StorageFileInfo` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L473 | Supply `file_id` = `str(metadata.get('$id', metadata.get('id', file_id)))`. Reserved Appwrite storage-object identifier. Evaluate the value as: `str(metadata.get('$id', metadata.get('id', file_id)))` — Convert the input to its string representation; inputs include `metadata.get('$id', metadata.get('id', file_id))` — Look up `'$id'` in `metadata`, using `metadata.get('id', file_id)` when the key is absent (an existing null value is not replaced). |
| L474 | Supply `bucket_id` = `str(metadata.get('bucketId', metadata.get('bucket_id', bucket_id)))`. Appwrite bucket identifier. Evaluate the value as: `str(metadata.get('bucketId', metadata.get('bucket_id', bucket_id)))` — Convert the input to its string representation; inputs include `metadata.get('bucketId', metadata.get('bucket_id', bucket_id))` — Look up `'bucketId'` in `metadata`, using `metadata.get('bucket_id', bucket_id)` when the key is absent (an existing null value is not replaced). |
| L475 | Supply `size` = `size`.  Evaluate the value as: the current `size` value. |
| L476 | Supply `mime_type` = `mime`. Declared storage content type; accepted application uploads use application/pdf. Evaluate the value as: the current `mime` value. |
| L477 | Supply `chunks_uploaded` = `chunks_uploaded`.  Evaluate the value as: the current `chunks_uploaded` value. |
| L478 | Supply `chunks_total` = `chunks_total`.  Evaluate the value as: the current `chunks_total` value. |
| L479 | Supply `completed` = `completed`.  Evaluate the value as: the current `completed` value. |
| L480 | Close the expression/container begun at L472; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `AppwriteStorageAdapter._wrap(self, bucket_id: str, file_id: str, action: Any) -> Any`

**Arguments:** Storage context and zero-argument callable. **Returns:** Whatever `action()` returns. **Work:** Maps SDK 404/not-found text to `StorageNotFoundError`, 409/conflict text to `StorageConflictError`, and other SDK/unexpected errors to `StorageUnavailableError`; existing `StorageError` propagates. Exception causes are retained.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-appwritestorageadapter--wrap"></a>

#### Line-by-line execution

[Current source: lines 482–502](../../../../Backend/app/services/storage.py#L482-L502). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; positional or keyword | Appwrite bucket identifier. |
| `file_id` | `str`; required; positional or keyword | Reserved Appwrite storage-object identifier. |
| `action` | `Any`; required; positional or keyword | Caller-supplied action; each read, transformation, and validation is traced below. |

**Declared result:** `Any`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 482 |     def _wrap(self, bucket_id: str, file_id: str, action: Any) -> Any:
 483 |         from appwrite.exception import AppwriteException
 484 | 
 485 |         try:
 486 |             return action()
 487 |         except AppwriteException as exc:
 488 |             code = int(exc.code or 0)
 489 |             exc_type = str(exc.type or "").lower()
 490 |             if code == 404 or "not_found" in exc_type or "not found" in str(exc.message).lower():
 491 |                 raise StorageNotFoundError(bucket_id, file_id) from exc
 492 |             if code == 409 or "conflict" in exc_type or "already exists" in str(exc.message).lower():
 493 |                 raise StorageConflictError(
 494 |                     f"storage file already exists: bucket={bucket_id!r} file={file_id!r}"
 495 |                 ) from exc
 496 |             raise StorageUnavailableError(
 497 |                 f"storage operation failed ({code}): {exc.message}"
 498 |             ) from exc
 499 |         except StorageError:
 500 |             raise
 501 |         except Exception as exc:  # network, timeout, SDK drift
 502 |             raise StorageUnavailableError(f"storage operation failed: {exc}") from exc
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L482 | Define `AppwriteStorageAdapter._wrap`; bind its arguments when called. The body executes only when invoked. |
| L483 | Import `AppwriteException` from `appwrite.exception`; inside a function this import is deferred until this path is reached. |
| L485 | Enter the protected block; failures are matched against `AppwriteException`, `StorageError`, `Exception` in order. |
| L486 | Compute the return value: `action()` — Invoke `action` with the shown inputs and use its result; see the function overview for its role in this flow. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L487 | Handle `AppwriteException` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L488 | Evaluate the right-hand side, then bind/store it in `code`: `int(exc.code or 0)` — Convert the input to an integer (using the optional numeric base). |
| L489 | Evaluate the right-hand side, then bind/store it in `exc_type`: `str(exc.type or '').lower()` — Return a lowercased string copy; first obtain the receiver: `str(exc.type or '')` — Convert the input to its string representation. |
| L490 | Evaluate the branch condition: evaluate `code == 404 or 'not_found' in exc_type or 'not found' in str(exc.message).lower()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L491; otherwise skip this indented block and continue after it. |
| L491 | Raise `StorageNotFoundError(bucket_id, file_id)`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L492 | Evaluate the branch condition: evaluate `code == 409 or 'conflict' in exc_type or 'already exists' in str(exc.message).lower()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L493; otherwise skip this indented block and continue after it. |
| L493 | Raise `StorageConflictError(f'storage file already exists: bucket={bucket_id!r} file={file_id!r}')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L494 | Supply positional argument 1 to `StorageConflictError`: format a string by inserting `bucket_id`, `file_id` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L495 | Contribute the current `exc` value to the expression being assembled. |
| L496 | Raise `StorageUnavailableError(f'storage operation failed ({code}): {exc.message}')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L497 | Supply positional argument 1 to `StorageUnavailableError`: format a string by inserting `code`, `exc.message` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L498 | Contribute the current `exc` value to the expression being assembled. |
| L499 | Handle `StorageError`; only a matching error from the associated try enters this body. |
| L500 | Re-raise the currently handled exception with its traceback; no replacement result is returned. |
| L501 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L502 | Raise `StorageUnavailableError(f'storage operation failed: {exc}')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |

<!-- END LINE WALKTHROUGH -->

### `AppwriteStorageAdapter.create_storage_file(self, *, bucket_id, file_id, data: bytes, mime_type: str, owner_appwrite_user_id=None, file_name=None) -> StorageFileInfo`

**Arguments:** Private target IDs, bytes/MIME, optional external owner ID and filename. **Returns:** Normalized create metadata. **Work:** Rejects empty bytes, derives permissions if an owner is supplied (otherwise passes `None`), chooses the supplied name or `<file_id>.pdf`, builds `InputFile.from_bytes`, calls the nested `_create` through `_wrap`, then maps metadata. SDK upload/chunking is blocking; callers should finish reservation transactions first.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-appwritestorageadapter-create-storage-file"></a>

#### Line-by-line execution

[Current source: lines 506–544](../../../../Backend/app/services/storage.py#L506-L544). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |
| `data` | `bytes`; required; keyword-only | File bytes or input payload consumed by this operation, as specified by the annotation. |
| `mime_type` | `str`; required; keyword-only | Declared storage content type; accepted application uploads use application/pdf. |
| `owner_appwrite_user_id` | `str \| None`; default `None`; keyword-only | External Appwrite user ID used for private file permissions. |
| `file_name` | `str \| None`; default `None`; keyword-only | Display PDF filename; immutable IDs establish ownership and evidence identity. |

**Declared result:** `StorageFileInfo`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 506 |     def create_storage_file(
 507 |         self,
 508 |         *,
 509 |         bucket_id: str,
 510 |         file_id: str,
 511 |         data: bytes,
 512 |         mime_type: str,
 513 |         owner_appwrite_user_id: str | None = None,
 514 |         file_name: str | None = None,
 515 |     ) -> StorageFileInfo:
 516 |         """Upload with a pre-reserved file ID and owner-only access.
 517 | 
 518 |         ``owner_appwrite_user_id`` (optional, Protocol-compatible) sets
 519 |         file-level ``read/update/delete("user:<external id>")``
 520 |         permissions.  Without it the file is server-only (API key
 521 |         mediates every access); prefer always passing it from the
 522 |         upload handler.  The SDK chunks large files internally; the
 523 |         returned metadata carries the chunk counters inspected by
 524 |         :meth:`inspect_storage_file`.
 525 |         """
 526 |         from appwrite.input_file import InputFile
 527 | 
 528 |         if not data:
 529 |             raise ValueError("data must not be empty")
 530 |         permissions = (
 531 |             owner_file_permissions(owner_appwrite_user_id)
 532 |             if owner_appwrite_user_id is not None
 533 |             else None
 534 |         )
 535 |         filename = file_name or f"{file_id}{PDF_EXTENSION}"
 536 |         input_file = InputFile.from_bytes(data, filename, mime_type)
 537 | 
 538 |         def _create() -> dict[str, Any]:
 539 |             return self.storage.create_file(
 540 |                 bucket_id, file_id, input_file, permissions
 541 |             )
 542 | 
 543 |         metadata = self._wrap(bucket_id, file_id, _create)
 544 |         return self._metadata_to_info(metadata, bucket_id=bucket_id, file_id=file_id)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L506 | Define `AppwriteStorageAdapter.create_storage_file`; bind its arguments when called. The body executes only when invoked. |
| L507 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L508 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L509 | Declare parameter `bucket_id` with annotation `str`. Appwrite bucket identifier. |
| L510 | Declare parameter `file_id` with annotation `str`. Reserved Appwrite storage-object identifier. |
| L511 | Declare parameter `data` with annotation `bytes`. File bytes or input payload consumed by this operation, as specified by the annotation. |
| L512 | Declare parameter `mime_type` with annotation `str`. Declared storage content type; accepted application uploads use application/pdf. |
| L513 | Declare parameter `owner_appwrite_user_id` with annotation `str \| None`. External Appwrite user ID used for private file permissions. |
| L514 | Declare parameter `file_name` with annotation `str \| None`. Display PDF filename; immutable IDs establish ownership and evidence identity. |
| L515 | Finish/continue the signature; the declared return annotation is `StorageFileInfo`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L516 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L518 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L519 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L520 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L521 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L522 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L523 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L524 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L525 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L526 | Import `InputFile` from `appwrite.input_file`; inside a function this import is deferred until this path is reached. |
| L528 | Evaluate the branch condition: invert the truthiness of `data`. If truthy, enter L529; otherwise skip this indented block and continue after it. |
| L529 | Raise `ValueError('data must not be empty')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L530 | Evaluate the right-hand side, then bind/store it in `permissions`: check `owner_appwrite_user_id is not None`; when true use `owner_file_permissions(owner_appwrite_user_id)` — Call [owner_file_permissions](#walk-owner-file-permissions) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result, otherwise None (no value) (only the selected branch is evaluated). |
| L531 | `owner_file_permissions(owner_appwrite_user_id)` — Call [owner_file_permissions](#walk-owner-file-permissions) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L532 | Continue the enclosing expression: compare whether `owner_appwrite_user_id` is not the same object as `None`. |
| L533 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L534 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L535 | Evaluate the right-hand side, then bind/store it in `filename`: evaluate `file_name or f'{file_id}{PDF_EXTENSION}'` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L536 | Evaluate the right-hand side, then bind/store it in `input_file`: `InputFile.from_bytes(data, filename, mime_type)` — Invoke `InputFile.from_bytes` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L538 | Define the local closure [AppwriteStorageAdapter.create_storage_file._create](#walk-appwritestorageadapter-create-storage-file--create); it can capture enclosing locals. Definition does not execute its body. |
| L539 | Compute the return value: `self.storage.create_file(bucket_id, file_id, input_file, permissions)` — Upload bytes to the Appwrite bucket using the reserved file ID and supplied private permissions. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L540 | Supply positional argument 1 to `self.storage.create_file`: the current `bucket_id` value. |
| L541 | Close the expression/container begun at L539; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L543 | Evaluate the right-hand side, then bind/store it in `metadata`: `self._wrap(bucket_id, file_id, _create)` — Call [AppwriteStorageAdapter._wrap](#walk-appwritestorageadapter--wrap) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L544 | Compute the return value: `self._metadata_to_info(metadata, bucket_id=bucket_id, file_id=file_id)` — Call [AppwriteStorageAdapter._metadata_to_info](#walk-appwritestorageadapter--metadata-to-info) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `AppwriteStorageAdapter.create_storage_file._create() -> dict[str, Any]` (nested)

**Arguments:** None explicitly; captures `self`, target IDs, prepared `InputFile`, and permissions. **Returns:** SDK create response. **Work:** Calls `self.storage.create_file(bucket_id, file_id, input_file, permissions)`; `_wrap` handles its exceptions.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-appwritestorageadapter-create-storage-file--create"></a>

#### Line-by-line execution

[Current source: lines 538–541](../../../../Backend/app/services/storage.py#L538-L541). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `dict[str, Any]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 538 |         def _create() -> dict[str, Any]:
 539 |             return self.storage.create_file(
 540 |                 bucket_id, file_id, input_file, permissions
 541 |             )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L538 | Define `AppwriteStorageAdapter.create_storage_file._create`; bind its arguments when called. The body executes only when invoked. |
| L539 | Compute the return value: `self.storage.create_file(bucket_id, file_id, input_file, permissions)` — Upload bytes to the Appwrite bucket using the reserved file ID and supplied private permissions. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L540 | Supply positional argument 1 to `self.storage.create_file`: the current `bucket_id` value. |
| L541 | Close the expression/container begun at L539; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `AppwriteStorageAdapter.inspect_storage_file(self, *, bucket_id, file_id) -> StorageFileInfo`

**Arguments:** Target IDs. **Returns:** Current metadata DTO. **Work:** Calls `storage.get_file` through a zero-argument lambda passed to `_wrap`, then `_metadata_to_info`. It does not read the PDF or compute its fingerprint.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-appwritestorageadapter-inspect-storage-file"></a>

#### Line-by-line execution

[Current source: lines 546–551](../../../../Backend/app/services/storage.py#L546-L551). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |

**Declared result:** `StorageFileInfo`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 546 |     def inspect_storage_file(self, *, bucket_id: str, file_id: str) -> StorageFileInfo:
 547 |         """Return size/fingerprint/chunk completion for reconciliation."""
 548 |         metadata = self._wrap(
 549 |             bucket_id, file_id, lambda: self.storage.get_file(bucket_id, file_id)
 550 |         )
 551 |         return self._metadata_to_info(metadata, bucket_id=bucket_id, file_id=file_id)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L546 | Define `AppwriteStorageAdapter.inspect_storage_file`; bind its arguments when called. The body executes only when invoked. |
| L547 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L548 | Evaluate the right-hand side, then bind/store it in `metadata`: `self._wrap(bucket_id, file_id, lambda: self.storage.get_file(bucket_id, file_id))` — Call [AppwriteStorageAdapter._wrap](#walk-appwritestorageadapter--wrap) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L549 | Read Appwrite file metadata for the exact bucket/file ID. |
| L550 | Close the expression/container begun at L548; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L551 | Compute the return value: `self._metadata_to_info(metadata, bucket_id=bucket_id, file_id=file_id)` — Call [AppwriteStorageAdapter._metadata_to_info](#walk-appwritestorageadapter--metadata-to-info) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `AppwriteStorageAdapter.open_storage_range(self, *, bucket_id, file_id, range_header) -> tuple[bytes, dict[str, str]]`

**Arguments:** Target IDs and optional Range header. **Returns:** Bytes/headers from `apply_range`. **Work:** Downloads the **entire** file with `get_file_download` through `_wrap`, converts bytearray/memoryview to bytes or string to encoded bytes, rejects other result types, and slices locally. The SDK request does not stream just the requested range.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-appwritestorageadapter-open-storage-range"></a>

#### Line-by-line execution

[Current source: lines 553–573](../../../../Backend/app/services/storage.py#L553-L573). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |
| `range_header` | `str \| None`; required; keyword-only | Optional HTTP byte-range selector; parsing determines full, partial, or unsatisfiable behavior. |

**Declared result:** `tuple[bytes, dict[str, str]]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 553 |     def open_storage_range(
 554 |         self, *, bucket_id: str, file_id: str, range_header: str | None
 555 |     ) -> tuple[bytes, dict[str, str]]:
 556 |         """Return (chunk bytes, response headers) for inline PDF serving.
 557 | 
 558 |         Downloads through the server API key (bucket stays private)
 559 |         and slices locally with :func:`apply_range` for byte-range responses.
 560 |         """
 561 |         raw = self._wrap(
 562 |             bucket_id,
 563 |             file_id,
 564 |             lambda: self.storage.get_file_download(bucket_id, file_id),
 565 |         )
 566 |         if isinstance(raw, (bytearray, memoryview)):
 567 |             raw = bytes(raw)
 568 |         if not isinstance(raw, (bytes, str)):
 569 |             raise StorageUnavailableError(
 570 |                 f"unexpected storage download type: {type(raw).__name__}"
 571 |             )
 572 |         data = raw.encode() if isinstance(raw, str) else raw
 573 |         return apply_range(data, range_header)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L553 | Define `AppwriteStorageAdapter.open_storage_range`; bind its arguments when called. The body executes only when invoked. |
| L554 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `bucket_id` with annotation `str`. Appwrite bucket identifier. Declare parameter `file_id` with annotation `str`. Reserved Appwrite storage-object identifier. Declare parameter `range_header` with annotation `str \| None`. Optional HTTP byte-range selector; parsing determines full, partial, or unsatisfiable behavior. |
| L555 | Finish/continue the signature; the declared return annotation is `tuple[bytes, dict[str, str]]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L556 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L558 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L559 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L560 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L561 | Evaluate the right-hand side, then bind/store it in `raw`: `self._wrap(bucket_id, file_id, lambda: self.storage.get_file_download(bucket_id, file_id))` — Call [AppwriteStorageAdapter._wrap](#walk-appwritestorageadapter--wrap) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L562 | Supply positional argument 1 to `self._wrap`: the current `bucket_id` value. |
| L563 | Supply positional argument 2 to `self._wrap`: the current `file_id` value. |
| L564 | Download the complete Appwrite file bytes; application range slicing happens afterward. |
| L565 | Close the expression/container begun at L561; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L566 | Evaluate the branch condition: `isinstance(raw, (bytearray, memoryview))` — Check the runtime type against the supplied class or tuple of classes. If truthy, enter L567; otherwise skip this indented block and continue after it. |
| L567 | Evaluate the right-hand side, then bind/store it in `raw`: `bytes(raw)` — Construct an immutable byte sequence. |
| L568 | Evaluate the branch condition: invert the truthiness of `isinstance(raw, (bytes, str))`. If truthy, enter L569; otherwise skip this indented block and continue after it. |
| L569 | Raise `StorageUnavailableError(f'unexpected storage download type: {type(raw).__name__}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L570 | Read the runtime class of the supplied value. |
| L571 | Close the expression/container begun at L569; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L572 | Evaluate the right-hand side, then bind/store it in `data`: check `isinstance(raw, str)`; when true use `raw.encode()` — Encode the text into bytes with the selected encoding, otherwise the current `raw` value (only the selected branch is evaluated). |
| L573 | Compute the return value: `apply_range(data, range_header)` — Call [apply_range](#walk-apply-range) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `AppwriteStorageAdapter.delete_storage_file(self, *, bucket_id, file_id) -> None`

**Arguments:** Target IDs. **Returns:** `None`. **Work:** Wraps SDK `delete_file`; suppresses `StorageNotFoundError` for idempotency, while other errors propagate.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-appwritestorageadapter-delete-storage-file"></a>

#### Line-by-line execution

[Current source: lines 575–581](../../../../Backend/app/services/storage.py#L575-L581). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 575 |     def delete_storage_file(self, *, bucket_id: str, file_id: str) -> None:
 576 |         """Idempotent delete: already-missing files count as deleted."""
 577 |         try:
 578 |             self._wrap(bucket_id, file_id, lambda: self.storage.delete_file(bucket_id, file_id))
 579 |         except StorageNotFoundError:
 580 |             return None
 581 |         return None
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L575 | Define `AppwriteStorageAdapter.delete_storage_file`; bind its arguments when called. The body executes only when invoked. |
| L576 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L577 | Enter the protected block; failures are matched against `StorageNotFoundError` in order. |
| L578 | `self._wrap(bucket_id, file_id, lambda: self.storage.delete_file(bucket_id, file_id))` — Call [AppwriteStorageAdapter._wrap](#walk-appwritestorageadapter--wrap) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L579 | Handle `StorageNotFoundError`; only a matching error from the associated try enters this body. |
| L580 | Compute the return value: None (no value). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L581 | Compute the return value: None (no value). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

## `InMemoryStorageAdapter`

An existing application-local adapter using `(bucket_id, file_id)` dictionary keys, call recording, and one-shot fault/completion controls. It has no remote persistence or credential enforcement.

### `InMemoryStorageAdapter.__init__(self, *, default_complete=True) -> None`

**Arguments:** Default completion policy for creates. **Returns:** `None`. **Work:** Initializes empty files/calls, four `fail_next_*` exception slots, `incomplete_next_create=False`, and the default policy.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-inmemorystorageadapter---init--"></a>

#### Line-by-line execution

[Current source: lines 605–613](../../../../Backend/app/services/storage.py#L605-L613). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `default_complete` | `bool`; default `True`; keyword-only | Caller-supplied default complete; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 605 |     def __init__(self, *, default_complete: bool = True) -> None:
 606 |         self._files: dict[tuple[str, str], dict[str, Any]] = {}
 607 |         self.calls: list[tuple[str, dict[str, Any]]] = []
 608 |         self.fail_next_create: Exception | None = None
 609 |         self.fail_next_inspect: Exception | None = None
 610 |         self.fail_next_download: Exception | None = None
 611 |         self.fail_next_delete: Exception | None = None
 612 |         self.incomplete_next_create = False
 613 |         self.default_complete = default_complete
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L605 | Define `InMemoryStorageAdapter.__init__`; bind its arguments when called. The body executes only when invoked. |
| L606 | Evaluate the right-hand side, then bind/store it in `self._files`: create an empty dictionary. |
| L607 | Evaluate the right-hand side, then bind/store it in `self.calls`: build a list containing no items. |
| L608 | Evaluate the right-hand side, then bind/store it in `self.fail_next_create`: None (no value). |
| L609 | Evaluate the right-hand side, then bind/store it in `self.fail_next_inspect`: None (no value). |
| L610 | Evaluate the right-hand side, then bind/store it in `self.fail_next_download`: None (no value). |
| L611 | Evaluate the right-hand side, then bind/store it in `self.fail_next_delete`: None (no value). |
| L612 | Evaluate the right-hand side, then bind/store it in `self.incomplete_next_create`: `False`. |
| L613 | Evaluate the right-hand side, then bind/store it in `self.default_complete`: the current `default_complete` value. |

<!-- END LINE WALKTHROUGH -->

### `InMemoryStorageAdapter.seed_file(self, *, bucket_id, file_id, data, mime_type=PDF_MIME_TYPE, permissions=None, complete=True) -> StorageFileInfo`

**Arguments:** Target IDs, bytes, optional MIME/permissions/completion. **Returns:** `_info` for the seeded entry. **Work:** Copies bytes/permissions, creates one total chunk with uploaded count 0/1, and writes/replaces the dictionary entry directly without call recording or duplicate checks.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-inmemorystorageadapter-seed-file"></a>

#### Line-by-line execution

[Current source: lines 617–637](../../../../Backend/app/services/storage.py#L617-L637). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |
| `data` | `bytes`; required; keyword-only | File bytes or input payload consumed by this operation, as specified by the annotation. |
| `mime_type` | `str`; default `PDF_MIME_TYPE`; keyword-only | Declared storage content type; accepted application uploads use application/pdf. |
| `permissions` | `list[str] \| None`; default `None`; keyword-only | Caller-supplied permissions; each read, transformation, and validation is traced below. |
| `complete` | `bool`; default `True`; keyword-only | Caller-supplied complete; each read, transformation, and validation is traced below. |

**Declared result:** `StorageFileInfo`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 617 |     def seed_file(
 618 |         self,
 619 |         *,
 620 |         bucket_id: str,
 621 |         file_id: str,
 622 |         data: bytes,
 623 |         mime_type: str = PDF_MIME_TYPE,
 624 |         permissions: list[str] | None = None,
 625 |         complete: bool = True,
 626 |     ) -> StorageFileInfo:
 627 |         chunks_total = 1
 628 |         chunks_uploaded = 1 if complete else 0
 629 |         self._files[(bucket_id, file_id)] = {
 630 |             "data": bytes(data),
 631 |             "mime_type": mime_type,
 632 |             "permissions": list(permissions) if permissions else [],
 633 |             "file_name": f"{file_id}{PDF_EXTENSION}",
 634 |             "chunks_total": chunks_total,
 635 |             "chunks_uploaded": chunks_uploaded,
 636 |         }
 637 |         return self._info(bucket_id, file_id)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L617 | Define `InMemoryStorageAdapter.seed_file`; bind its arguments when called. The body executes only when invoked. |
| L618 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L619 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L620 | Declare parameter `bucket_id` with annotation `str`. Appwrite bucket identifier. |
| L621 | Declare parameter `file_id` with annotation `str`. Reserved Appwrite storage-object identifier. |
| L622 | Declare parameter `data` with annotation `bytes`. File bytes or input payload consumed by this operation, as specified by the annotation. |
| L623 | Declare parameter `mime_type` with annotation `str`. Declared storage content type; accepted application uploads use application/pdf. |
| L624 | Declare parameter `permissions` with annotation `list[str] \| None`. Caller-supplied permissions; its uses and transformations are traced below. |
| L625 | Declare parameter `complete` with annotation `bool`. Caller-supplied complete; its uses and transformations are traced below. |
| L626 | Finish/continue the signature; the declared return annotation is `StorageFileInfo`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L627 | Evaluate the right-hand side, then bind/store it in `chunks_total`: `1`. |
| L628 | Evaluate the right-hand side, then bind/store it in `chunks_uploaded`: check `complete`; when true use `1`, otherwise `0` (only the selected branch is evaluated). |
| L629 | Evaluate the right-hand side, then bind/store it in `self._files[bucket_id, file_id]`: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. |
| L630 | Add mapping entry `'data'`: `bytes(data)` — Construct an immutable byte sequence. |
| L631 | Add mapping entry `'mime_type'`: the current `mime_type` value. |
| L632 | Add mapping entry `'permissions'`: check `permissions`; when true use `list(permissions)` — Materialize the iterable in order into a list (or create an empty list), otherwise build a list containing no items (only the selected branch is evaluated). |
| L633 | Add mapping entry `'file_name'`: format a string by inserting `file_id`, `PDF_EXTENSION` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L634 | Add mapping entry `'chunks_total'`: the current `chunks_total` value. |
| L635 | Add mapping entry `'chunks_uploaded'`: the current `chunks_uploaded` value. |
| L636 | Close the expression/container begun at L629; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L637 | Compute the return value: `self._info(bucket_id, file_id)` — Call [InMemoryStorageAdapter._info](#walk-inmemorystorageadapter--info) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `InMemoryStorageAdapter.mark_complete(self, *, bucket_id, file_id) -> StorageFileInfo`

**Arguments:** Existing target IDs. **Returns:** Updated metadata. **Work:** Sets uploaded chunks equal to total; missing entry raises `StorageNotFoundError`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-inmemorystorageadapter-mark-complete"></a>

#### Line-by-line execution

[Current source: lines 639–644](../../../../Backend/app/services/storage.py#L639-L644). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |

**Declared result:** `StorageFileInfo`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 639 |     def mark_complete(self, *, bucket_id: str, file_id: str) -> StorageFileInfo:
 640 |         entry = self._files.get((bucket_id, file_id))
 641 |         if entry is None:
 642 |             raise StorageNotFoundError(bucket_id, file_id)
 643 |         entry["chunks_uploaded"] = entry["chunks_total"]
 644 |         return self._info(bucket_id, file_id)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L639 | Define `InMemoryStorageAdapter.mark_complete`; bind its arguments when called. The body executes only when invoked. |
| L640 | Evaluate the right-hand side, then bind/store it in `entry`: `self._files.get((bucket_id, file_id))` — Look up `(bucket_id, file_id)` in `self._files`, using None when the key is absent (an existing null value is not replaced). |
| L641 | Evaluate the branch condition: compare whether `entry` is the same object as `None`. If truthy, enter L642; otherwise skip this indented block and continue after it. |
| L642 | Raise `StorageNotFoundError(bucket_id, file_id)`; stop the normal path and transfer control to the nearest matching exception handler. |
| L643 | Evaluate the right-hand side, then bind/store it in `entry['chunks_uploaded']`: look up index/key `'chunks_total'` in `entry`; a missing key or out-of-range index raises. |
| L644 | Compute the return value: `self._info(bucket_id, file_id)` — Call [InMemoryStorageAdapter._info](#walk-inmemorystorageadapter--info) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `InMemoryStorageAdapter.permissions_for(self, *, bucket_id, file_id) -> list[str]`

**Arguments:** Target IDs. **Returns:** Copy of the entry's permissions. **Work:** Looks up the entry and raises not-found if absent; the copy prevents mutating internal permissions through this result.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-inmemorystorageadapter-permissions-for"></a>

#### Line-by-line execution

[Current source: lines 646–650](../../../../Backend/app/services/storage.py#L646-L650). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |

**Declared result:** `list[str]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 646 |     def permissions_for(self, *, bucket_id: str, file_id: str) -> list[str]:
 647 |         entry = self._files.get((bucket_id, file_id))
 648 |         if entry is None:
 649 |             raise StorageNotFoundError(bucket_id, file_id)
 650 |         return list(entry["permissions"])
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L646 | Define `InMemoryStorageAdapter.permissions_for`; bind its arguments when called. The body executes only when invoked. |
| L647 | Evaluate the right-hand side, then bind/store it in `entry`: `self._files.get((bucket_id, file_id))` — Look up `(bucket_id, file_id)` in `self._files`, using None when the key is absent (an existing null value is not replaced). |
| L648 | Evaluate the branch condition: compare whether `entry` is the same object as `None`. If truthy, enter L649; otherwise skip this indented block and continue after it. |
| L649 | Raise `StorageNotFoundError(bucket_id, file_id)`; stop the normal path and transfer control to the nearest matching exception handler. |
| L650 | Compute the return value: `list(entry['permissions'])` — Materialize the iterable in order into a list (or create an empty list). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `InMemoryStorageAdapter.stored_bytes(self, *, bucket_id, file_id) -> bytes`

**Arguments:** Target IDs. **Returns:** Stored data as immutable bytes. **Work:** Looks up or raises not-found, then applies `bytes()`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-inmemorystorageadapter-stored-bytes"></a>

#### Line-by-line execution

[Current source: lines 652–656](../../../../Backend/app/services/storage.py#L652-L656). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |

**Declared result:** `bytes`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 652 |     def stored_bytes(self, *, bucket_id: str, file_id: str) -> bytes:
 653 |         entry = self._files.get((bucket_id, file_id))
 654 |         if entry is None:
 655 |             raise StorageNotFoundError(bucket_id, file_id)
 656 |         return bytes(entry["data"])
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L652 | Define `InMemoryStorageAdapter.stored_bytes`; bind its arguments when called. The body executes only when invoked. |
| L653 | Evaluate the right-hand side, then bind/store it in `entry`: `self._files.get((bucket_id, file_id))` — Look up `(bucket_id, file_id)` in `self._files`, using None when the key is absent (an existing null value is not replaced). |
| L654 | Evaluate the branch condition: compare whether `entry` is the same object as `None`. If truthy, enter L655; otherwise skip this indented block and continue after it. |
| L655 | Raise `StorageNotFoundError(bucket_id, file_id)`; stop the normal path and transfer control to the nearest matching exception handler. |
| L656 | Compute the return value: `bytes(entry['data'])` — Construct an immutable byte sequence. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `InMemoryStorageAdapter.has_file(self, *, bucket_id, file_id) -> bool`

**Arguments:** Target IDs. **Returns:** Dictionary membership. **Work:** Checks existence only, including incomplete entries.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-inmemorystorageadapter-has-file"></a>

#### Line-by-line execution

[Current source: lines 658–659](../../../../Backend/app/services/storage.py#L658-L659). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 658 |     def has_file(self, *, bucket_id: str, file_id: str) -> bool:
 659 |         return (bucket_id, file_id) in self._files
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L658 | Define `InMemoryStorageAdapter.has_file`; bind its arguments when called. The body executes only when invoked. |
| L659 | Compute the return value: compare whether `(bucket_id, file_id)` is contained in `self._files`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `InMemoryStorageAdapter._info(self, bucket_id, file_id) -> StorageFileInfo`

**Arguments:** Existing dictionary key components. **Returns:** Size/MIME/counter/completion DTO. **Work:** Computes byte length and the same positive-size/total, uploaded ≥ total completion rule. Direct missing lookup raises `KeyError`; public methods generally check first.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-inmemorystorageadapter--info"></a>

#### Line-by-line execution

[Current source: lines 663–676](../../../../Backend/app/services/storage.py#L663-L676). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; positional or keyword | Appwrite bucket identifier. |
| `file_id` | `str`; required; positional or keyword | Reserved Appwrite storage-object identifier. |

**Declared result:** `StorageFileInfo`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 663 |     def _info(self, bucket_id: str, file_id: str) -> StorageFileInfo:
 664 |         entry = self._files[(bucket_id, file_id)]
 665 |         size = len(entry["data"])
 666 |         total = int(entry["chunks_total"])
 667 |         uploaded = int(entry["chunks_uploaded"])
 668 |         return StorageFileInfo(
 669 |             file_id=file_id,
 670 |             bucket_id=bucket_id,
 671 |             size=size,
 672 |             mime_type=str(entry["mime_type"]),
 673 |             chunks_uploaded=uploaded,
 674 |             chunks_total=total,
 675 |             completed=size > 0 and total > 0 and uploaded >= total,
 676 |         )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L663 | Define `InMemoryStorageAdapter._info`; bind its arguments when called. The body executes only when invoked. |
| L664 | Evaluate the right-hand side, then bind/store it in `entry`: look up index/key `(bucket_id, file_id)` in `self._files`; a missing key or out-of-range index raises. |
| L665 | Evaluate the right-hand side, then bind/store it in `size`: `len(entry['data'])` — Count the items/characters in the supplied container/string. |
| L666 | Evaluate the right-hand side, then bind/store it in `total`: `int(entry['chunks_total'])` — Convert the input to an integer (using the optional numeric base). |
| L667 | Evaluate the right-hand side, then bind/store it in `uploaded`: `int(entry['chunks_uploaded'])` — Convert the input to an integer (using the optional numeric base). |
| L668 | Compute the return value: `StorageFileInfo` with the arguments detailed below — Construct `StorageFileInfo` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L669 | Supply `file_id` = `file_id`. Reserved Appwrite storage-object identifier. Evaluate the value as: the current `file_id` value. |
| L670 | Supply `bucket_id` = `bucket_id`. Appwrite bucket identifier. Evaluate the value as: the current `bucket_id` value. |
| L671 | Supply `size` = `size`.  Evaluate the value as: the current `size` value. |
| L672 | Supply `mime_type` = `str(entry['mime_type'])`. Declared storage content type; accepted application uploads use application/pdf. Evaluate the value as: `str(entry['mime_type'])` — Convert the input to its string representation. |
| L673 | Supply `chunks_uploaded` = `uploaded`.  Evaluate the value as: the current `uploaded` value. |
| L674 | Supply `chunks_total` = `total`.  Evaluate the value as: the current `total` value. |
| L675 | Supply `completed` = `size > 0 and total > 0 and (uploaded >= total)`.  Evaluate the value as: evaluate `size > 0 and total > 0 and (uploaded >= total)` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. |
| L676 | Close the expression/container begun at L668; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `InMemoryStorageAdapter.create_storage_file(self, *, bucket_id, file_id, data, mime_type, owner_appwrite_user_id=None, file_name=None) -> StorageFileInfo`

**Arguments:** Same create inputs as the real adapter. **Returns:** Created metadata. **Work:** Records the attempted call; consumes/raises `fail_next_create`; rejects duplicates/empty data; applies and resets `incomplete_next_create`; derives optional permissions and stores copied bytes/name/MIME/one-chunk counters. No actual PDF parsing occurs.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-inmemorystorageadapter-create-storage-file"></a>

#### Line-by-line execution

[Current source: lines 680–727](../../../../Backend/app/services/storage.py#L680-L727). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |
| `data` | `bytes`; required; keyword-only | File bytes or input payload consumed by this operation, as specified by the annotation. |
| `mime_type` | `str`; required; keyword-only | Declared storage content type; accepted application uploads use application/pdf. |
| `owner_appwrite_user_id` | `str \| None`; default `None`; keyword-only | External Appwrite user ID used for private file permissions. |
| `file_name` | `str \| None`; default `None`; keyword-only | Display PDF filename; immutable IDs establish ownership and evidence identity. |

**Declared result:** `StorageFileInfo`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 680 |     def create_storage_file(
 681 |         self,
 682 |         *,
 683 |         bucket_id: str,
 684 |         file_id: str,
 685 |         data: bytes,
 686 |         mime_type: str,
 687 |         owner_appwrite_user_id: str | None = None,
 688 |         file_name: str | None = None,
 689 |     ) -> StorageFileInfo:
 690 |         self.calls.append(
 691 |             (
 692 |                 "create",
 693 |                 {
 694 |                     "bucket_id": bucket_id,
 695 |                     "file_id": file_id,
 696 |                     "size": len(data),
 697 |                     "mime_type": mime_type,
 698 |                     "owner_appwrite_user_id": owner_appwrite_user_id,
 699 |                     "file_name": file_name,
 700 |                 },
 701 |             )
 702 |         )
 703 |         if self.fail_next_create is not None:
 704 |             exc, self.fail_next_create = self.fail_next_create, None
 705 |             raise exc
 706 |         if (bucket_id, file_id) in self._files:
 707 |             raise StorageConflictError(
 708 |                 f"storage file already exists: bucket={bucket_id!r} file={file_id!r}"
 709 |             )
 710 |         if not data:
 711 |             raise ValueError("data must not be empty")
 712 |         complete = self.default_complete and not self.incomplete_next_create
 713 |         self.incomplete_next_create = False
 714 |         permissions = (
 715 |             owner_file_permissions(owner_appwrite_user_id)
 716 |             if owner_appwrite_user_id is not None
 717 |             else []
 718 |         )
 719 |         self._files[(bucket_id, file_id)] = {
 720 |             "data": bytes(data),
 721 |             "mime_type": mime_type,
 722 |             "permissions": permissions,
 723 |             "file_name": file_name or f"{file_id}{PDF_EXTENSION}",
 724 |             "chunks_total": 1,
 725 |             "chunks_uploaded": 1 if complete else 0,
 726 |         }
 727 |         return self._info(bucket_id, file_id)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L680 | Define `InMemoryStorageAdapter.create_storage_file`; bind its arguments when called. The body executes only when invoked. |
| L681 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L682 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L683 | Declare parameter `bucket_id` with annotation `str`. Appwrite bucket identifier. |
| L684 | Declare parameter `file_id` with annotation `str`. Reserved Appwrite storage-object identifier. |
| L685 | Declare parameter `data` with annotation `bytes`. File bytes or input payload consumed by this operation, as specified by the annotation. |
| L686 | Declare parameter `mime_type` with annotation `str`. Declared storage content type; accepted application uploads use application/pdf. |
| L687 | Declare parameter `owner_appwrite_user_id` with annotation `str \| None`. External Appwrite user ID used for private file permissions. |
| L688 | Declare parameter `file_name` with annotation `str \| None`. Display PDF filename; immutable IDs establish ownership and evidence identity. |
| L689 | Finish/continue the signature; the declared return annotation is `StorageFileInfo`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L690 | `self.calls.append` with the arguments detailed below — Append one object to the mutable list in place. The return value is not assigned here. |
| L691 | Supply positional argument 1 to `self.calls.append`: build a tuple containing `'create'`, `{'bucket_id': bucket_id, 'file_id': file_id, 'size': len(data), 'mime_type': mime_type, 'owner_appwrite_user_id': owner_appwrite_user_id, 'file_name': file_name}`. |
| L692 | Supply positional argument 1 to `self.calls.append`: build a tuple containing `'create'`, `{'bucket_id': bucket_id, 'file_id': file_id, 'size': len(data), 'mime_type': mime_type, 'owner_appwrite_user_id': owner_appwrite_user_id, 'file_name': file_name}`. |
| L693 | Supply positional argument 1 to `self.calls.append`: build a tuple containing `'create'`, `{'bucket_id': bucket_id, 'file_id': file_id, 'size': len(data), 'mime_type': mime_type, 'owner_appwrite_user_id': owner_appwrite_user_id, 'file_name': file_name}`. |
| L694 | Add mapping entry `'bucket_id'`: the current `bucket_id` value. |
| L695 | Add mapping entry `'file_id'`: the current `file_id` value. |
| L696 | Add mapping entry `'size'`: `len(data)` — Count the items/characters in the supplied container/string. |
| L697 | Add mapping entry `'mime_type'`: the current `mime_type` value. |
| L698 | Add mapping entry `'owner_appwrite_user_id'`: the current `owner_appwrite_user_id` value. |
| L699 | Add mapping entry `'file_name'`: the current `file_name` value. |
| L700 | Close the expression/container begun at L693; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L701 | Close the expression/container begun at L691; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L702 | Close the expression/container begun at L690; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L703 | Evaluate the branch condition: compare whether `self.fail_next_create` is not the same object as `None`. If truthy, enter L704; otherwise skip this indented block and continue after it. |
| L704 | Evaluate the right-hand side, then bind/store it in `(exc, self.fail_next_create)`: build a tuple containing `self.fail_next_create`, `None`. |
| L705 | Raise `exc`; stop the normal path and transfer control to the nearest matching exception handler. |
| L706 | Evaluate the branch condition: compare whether `(bucket_id, file_id)` is contained in `self._files`. If truthy, enter L707; otherwise skip this indented block and continue after it. |
| L707 | Raise `StorageConflictError(f'storage file already exists: bucket={bucket_id!r} file={file_id!r}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L708 | Supply positional argument 1 to `StorageConflictError`: format a string by inserting `bucket_id`, `file_id` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L709 | Close the expression/container begun at L707; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L710 | Evaluate the branch condition: invert the truthiness of `data`. If truthy, enter L711; otherwise skip this indented block and continue after it. |
| L711 | Raise `ValueError('data must not be empty')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L712 | Evaluate the right-hand side, then bind/store it in `complete`: evaluate `self.default_complete and (not self.incomplete_next_create)` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. |
| L713 | Evaluate the right-hand side, then bind/store it in `self.incomplete_next_create`: `False`. |
| L714 | Evaluate the right-hand side, then bind/store it in `permissions`: check `owner_appwrite_user_id is not None`; when true use `owner_file_permissions(owner_appwrite_user_id)` — Call [owner_file_permissions](#walk-owner-file-permissions) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result, otherwise build a list containing no items (only the selected branch is evaluated). |
| L715 | `owner_file_permissions(owner_appwrite_user_id)` — Call [owner_file_permissions](#walk-owner-file-permissions) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L716 | Continue the enclosing expression: compare whether `owner_appwrite_user_id` is not the same object as `None`. |
| L717 | Contribute build a list containing no items to the expression being assembled. |
| L718 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L719 | Evaluate the right-hand side, then bind/store it in `self._files[bucket_id, file_id]`: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. |
| L720 | Add mapping entry `'data'`: `bytes(data)` — Construct an immutable byte sequence. |
| L721 | Add mapping entry `'mime_type'`: the current `mime_type` value. |
| L722 | Add mapping entry `'permissions'`: the current `permissions` value. |
| L723 | Add mapping entry `'file_name'`: evaluate `file_name or f'{file_id}{PDF_EXTENSION}'` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L724 | Add mapping entry `'chunks_total'`: `1`. |
| L725 | Add mapping entry `'chunks_uploaded'`: check `complete`; when true use `1`, otherwise `0` (only the selected branch is evaluated). |
| L726 | Close the expression/container begun at L719; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L727 | Compute the return value: `self._info(bucket_id, file_id)` — Call [InMemoryStorageAdapter._info](#walk-inmemorystorageadapter--info) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `InMemoryStorageAdapter.inspect_storage_file(self, *, bucket_id, file_id) -> StorageFileInfo`

**Arguments:** Target IDs. **Returns:** `_info` result. **Work:** Records inspection, consumes/raises its one-shot fault, and rejects missing entries.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-inmemorystorageadapter-inspect-storage-file"></a>

#### Line-by-line execution

[Current source: lines 729–736](../../../../Backend/app/services/storage.py#L729-L736). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |

**Declared result:** `StorageFileInfo`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 729 |     def inspect_storage_file(self, *, bucket_id: str, file_id: str) -> StorageFileInfo:
 730 |         self.calls.append(("inspect", {"bucket_id": bucket_id, "file_id": file_id}))
 731 |         if self.fail_next_inspect is not None:
 732 |             exc, self.fail_next_inspect = self.fail_next_inspect, None
 733 |             raise exc
 734 |         if (bucket_id, file_id) not in self._files:
 735 |             raise StorageNotFoundError(bucket_id, file_id)
 736 |         return self._info(bucket_id, file_id)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L729 | Define `InMemoryStorageAdapter.inspect_storage_file`; bind its arguments when called. The body executes only when invoked. |
| L730 | `self.calls.append(('inspect', {'bucket_id': bucket_id, 'file_id': file_id}))` — Append one object to the mutable list in place. The return value is not assigned here. |
| L731 | Evaluate the branch condition: compare whether `self.fail_next_inspect` is not the same object as `None`. If truthy, enter L732; otherwise skip this indented block and continue after it. |
| L732 | Evaluate the right-hand side, then bind/store it in `(exc, self.fail_next_inspect)`: build a tuple containing `self.fail_next_inspect`, `None`. |
| L733 | Raise `exc`; stop the normal path and transfer control to the nearest matching exception handler. |
| L734 | Evaluate the branch condition: compare whether `(bucket_id, file_id)` is absent from `self._files`. If truthy, enter L735; otherwise skip this indented block and continue after it. |
| L735 | Raise `StorageNotFoundError(bucket_id, file_id)`; stop the normal path and transfer control to the nearest matching exception handler. |
| L736 | Compute the return value: `self._info(bucket_id, file_id)` — Call [InMemoryStorageAdapter._info](#walk-inmemorystorageadapter--info) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `InMemoryStorageAdapter.open_storage_range(self, *, bucket_id, file_id, range_header) -> tuple[bytes, dict[str, str]]`

**Arguments:** Target IDs and optional range. **Returns:** Sliced bytes/headers. **Work:** Records download, consumes/raises its fault, rejects missing files, then delegates to `apply_range` with the stored MIME.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-inmemorystorageadapter-open-storage-range"></a>

#### Line-by-line execution

[Current source: lines 738–753](../../../../Backend/app/services/storage.py#L738-L753). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |
| `range_header` | `str \| None`; required; keyword-only | Optional HTTP byte-range selector; parsing determines full, partial, or unsatisfiable behavior. |

**Declared result:** `tuple[bytes, dict[str, str]]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 738 |     def open_storage_range(
 739 |         self, *, bucket_id: str, file_id: str, range_header: str | None
 740 |     ) -> tuple[bytes, dict[str, str]]:
 741 |         self.calls.append(
 742 |             (
 743 |                 "download",
 744 |                 {"bucket_id": bucket_id, "file_id": file_id, "range_header": range_header},
 745 |             )
 746 |         )
 747 |         if self.fail_next_download is not None:
 748 |             exc, self.fail_next_download = self.fail_next_download, None
 749 |             raise exc
 750 |         if (bucket_id, file_id) not in self._files:
 751 |             raise StorageNotFoundError(bucket_id, file_id)
 752 |         entry = self._files[(bucket_id, file_id)]
 753 |         return apply_range(bytes(entry["data"]), range_header, mime_type=str(entry["mime_type"]))
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L738 | Define `InMemoryStorageAdapter.open_storage_range`; bind its arguments when called. The body executes only when invoked. |
| L739 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `bucket_id` with annotation `str`. Appwrite bucket identifier. Declare parameter `file_id` with annotation `str`. Reserved Appwrite storage-object identifier. Declare parameter `range_header` with annotation `str \| None`. Optional HTTP byte-range selector; parsing determines full, partial, or unsatisfiable behavior. |
| L740 | Finish/continue the signature; the declared return annotation is `tuple[bytes, dict[str, str]]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L741 | `self.calls.append(('download', {'bucket_id': bucket_id, 'file_id': file_id, 'range_header': range_header}))` — Append one object to the mutable list in place. The return value is not assigned here. |
| L742 | Supply positional argument 1 to `self.calls.append`: build a tuple containing `'download'`, `{'bucket_id': bucket_id, 'file_id': file_id, 'range_header': range_header}`. |
| L743 | Supply positional argument 1 to `self.calls.append`: build a tuple containing `'download'`, `{'bucket_id': bucket_id, 'file_id': file_id, 'range_header': range_header}`. |
| L744 | Add mapping entry `'bucket_id'`: the current `bucket_id` value. Add mapping entry `'file_id'`: the current `file_id` value. Add mapping entry `'range_header'`: the current `range_header` value. |
| L745 | Close the expression/container begun at L742; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L746 | Close the expression/container begun at L741; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L747 | Evaluate the branch condition: compare whether `self.fail_next_download` is not the same object as `None`. If truthy, enter L748; otherwise skip this indented block and continue after it. |
| L748 | Evaluate the right-hand side, then bind/store it in `(exc, self.fail_next_download)`: build a tuple containing `self.fail_next_download`, `None`. |
| L749 | Raise `exc`; stop the normal path and transfer control to the nearest matching exception handler. |
| L750 | Evaluate the branch condition: compare whether `(bucket_id, file_id)` is absent from `self._files`. If truthy, enter L751; otherwise skip this indented block and continue after it. |
| L751 | Raise `StorageNotFoundError(bucket_id, file_id)`; stop the normal path and transfer control to the nearest matching exception handler. |
| L752 | Evaluate the right-hand side, then bind/store it in `entry`: look up index/key `(bucket_id, file_id)` in `self._files`; a missing key or out-of-range index raises. |
| L753 | Compute the return value: `apply_range(bytes(entry['data']), range_header, mime_type=str(entry['mime_type']))` — Call [apply_range](#walk-apply-range) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result; inputs include `bytes(entry['data'])` — Construct an immutable byte sequence. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `InMemoryStorageAdapter.delete_storage_file(self, *, bucket_id, file_id) -> None`

**Arguments:** Target IDs. **Returns:** `None`. **Work:** Records deletion, consumes/raises its fault, then `pop(..., None)` removes the entry or succeeds if already absent.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-inmemorystorageadapter-delete-storage-file"></a>

#### Line-by-line execution

[Current source: lines 755–761](../../../../Backend/app/services/storage.py#L755-L761). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 755 |     def delete_storage_file(self, *, bucket_id: str, file_id: str) -> None:
 756 |         self.calls.append(("delete", {"bucket_id": bucket_id, "file_id": file_id}))
 757 |         if self.fail_next_delete is not None:
 758 |             exc, self.fail_next_delete = self.fail_next_delete, None
 759 |             raise exc
 760 |         self._files.pop((bucket_id, file_id), None)
 761 |         return None
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L755 | Define `InMemoryStorageAdapter.delete_storage_file`; bind its arguments when called. The body executes only when invoked. |
| L756 | `self.calls.append(('delete', {'bucket_id': bucket_id, 'file_id': file_id}))` — Append one object to the mutable list in place. The return value is not assigned here. |
| L757 | Evaluate the branch condition: compare whether `self.fail_next_delete` is not the same object as `None`. If truthy, enter L758; otherwise skip this indented block and continue after it. |
| L758 | Evaluate the right-hand side, then bind/store it in `(exc, self.fail_next_delete)`: build a tuple containing `self.fail_next_delete`, `None`. |
| L759 | Raise `exc`; stop the normal path and transfer control to the nearest matching exception handler. |
| L760 | `self._files.pop((bucket_id, file_id), None)` — Invoke `self._files.pop` with the shown inputs and use its result; see the function overview for its role in this flow. The return value is not assigned here. |
| L761 | Compute the return value: None (no value). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `get_storage_adapter() -> AppwriteStorageAdapter`

**Arguments:** None. **Returns:** Newly configured real adapter. **Work:** Calls `storage_config()` and constructs the adapter; errors propagate. `StorageAdapterDep` is an optional `Annotated[Any, Depends(get_storage_adapter)]` alias, falling back to `Any` if its import-time typing setup fails.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-storage-adapter"></a>

#### Line-by-line execution

[Current source: lines 769–783](../../../../Backend/app/services/storage.py#L769-L783). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `AppwriteStorageAdapter`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 769 | def get_storage_adapter() -> AppwriteStorageAdapter:
 770 |     """Resolve the real adapter from server env (never at import time).
 771 | 
 772 |     Tests override this FastAPI dependency with
 773 |     :class:`InMemoryStorageAdapter`; A0 wires the real factory only
 774 |     when ``APPWRITE_*`` env is present and fails closed (``RuntimeError``
 775 |     -> ``503`` at the handler) otherwise.
 776 |     """
 777 |     config = storage_config()
 778 |     return AppwriteStorageAdapter(
 779 |         endpoint=config["endpoint"],
 780 |         project_id=config["project_id"],
 781 |         api_key=config["api_key"],
 782 |         bucket_id=config["bucket_id"],
 783 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L769 | Define `get_storage_adapter`; bind its arguments when called. The body executes only when invoked. |
| L770 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L772 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L773 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L774 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L775 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L776 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L777 | Evaluate the right-hand side, then bind/store it in `config`: `storage_config()` — Call [storage_config](#walk-storage-config) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L778 | Compute the return value: `AppwriteStorageAdapter(endpoint=config['endpoint'], project_id=config['project_id'], api_key=config['api_key'], bucket_id=config['bucket_id'])` — Construct `AppwriteStorageAdapter` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L779 | Supply `endpoint` = `config['endpoint']`.  Evaluate the value as: look up index/key `'endpoint'` in `config`; a missing key or out-of-range index raises. |
| L780 | Supply `project_id` = `config['project_id']`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: look up index/key `'project_id'` in `config`; a missing key or out-of-range index raises. |
| L781 | Supply `api_key` = `config['api_key']`. Server-side provider credential; do not expose it to browser configuration. Evaluate the value as: look up index/key `'api_key'` in `config`; a missing key or out-of-range index raises. |
| L782 | Supply `bucket_id` = `config['bucket_id']`. Appwrite bucket identifier. Evaluate the value as: look up index/key `'bucket_id'` in `config`; a missing key or out-of-range index raises. |
| L783 | Close the expression/container begun at L778; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->
