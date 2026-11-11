# `app/api/documents.py`

[Source](../../../../Backend/app/api/documents.py) · [Backend index](../../README.md)

Synchronous PDF/document/job routes, tagged `documents` and `jobs`. Every route requires the shared onboarded principal and a request session. `P` below means `/projects/{project_id}/documents`.

## Helpers

### `_validation_error(message: str, *, project_id=None, document_id=None) -> None`

**Arguments:** Safe validation message and optional scope UUIDs. **Returns:** Never normally. **Work:** Delegates to `raise_api_error` with HTTP 422 / `validation_error`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--validation-error"></a>

#### Line-by-line execution

[Current source: lines 111–123](../../../../Backend/app/api/documents.py#L111-L123). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `message` | `str`; required; positional or keyword | Caller-supplied message; each read, transformation, and validation is traced below. |
| `project_id` | `UUID \| None`; default `None`; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID \| None`; default `None`; keyword-only | Document UUID; filenames do not establish document identity. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 111 | def _validation_error(
 112 |     message: str,
 113 |     *,
 114 |     project_id: UUID | None = None,
 115 |     document_id: UUID | None = None,
 116 | ) -> None:
 117 |     raise_api_error(
 118 |         422,
 119 |         ErrorCode.VALIDATION_ERROR,
 120 |         message,
 121 |         project_id=project_id,
 122 |         document_id=document_id,
 123 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L111 | Define `_validation_error`; bind its arguments when called. The body executes only when invoked. |
| L112 | Declare parameter `message` with annotation `str`. Caller-supplied message; its uses and transformations are traced below. |
| L113 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L114 | Declare parameter `project_id` with annotation `UUID \| None`. Project UUID used to constrain resource lookup or provider metadata. |
| L115 | Declare parameter `document_id` with annotation `UUID \| None`. Document UUID; filenames do not establish document identity. |
| L116 | Finish/continue the signature; the declared return annotation is `None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L117 | `raise_api_error(422, ErrorCode.VALIDATION_ERROR, message, project_id=project_id, document_id=document_id)` — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L118 | Supply positional argument 1 to `raise_api_error`: `422`. |
| L119 | Supply positional argument 2 to `raise_api_error`: the `VALIDATION_ERROR` attribute of `ErrorCode`. |
| L120 | Supply positional argument 3 to `raise_api_error`: the current `message` value. |
| L121 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L122 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L123 | Close the expression/container begun at L117; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `_resolve_upload_request_id(raw: str | None, *, project_id: UUID) -> UUID`

**Arguments:** Optional `Idempotency-Key` header and project context. **Returns:** Parsed UUID or fresh UUID when absent/blank. **Work:** Strips/parses input; invalid types/formats raise a scoped 422.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--resolve-upload-request-id"></a>

#### Line-by-line execution

[Current source: lines 126–136](../../../../Backend/app/api/documents.py#L126-L136). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `raw` | `str \| None`; required; positional or keyword | Caller-supplied raw; each read, transformation, and validation is traced below. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |

**Declared result:** `UUID`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 126 | def _resolve_upload_request_id(raw: str | None, *, project_id: UUID) -> UUID:
 127 |     if raw is None or not raw.strip():
 128 |         return uuid.uuid4()
 129 |     try:
 130 |         return UUID(raw.strip())
 131 |     except (ValueError, AttributeError, TypeError):
 132 |         _validation_error(
 133 |             "Idempotency-Key must be a UUID.",
 134 |             project_id=project_id,
 135 |         )
 136 |         raise AssertionError("unreachable")  # pragma: no cover
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L126 | Define `_resolve_upload_request_id`; bind its arguments when called. The body executes only when invoked. |
| L127 | Evaluate the branch condition: evaluate `raw is None or not raw.strip()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L128; otherwise skip this indented block and continue after it. |
| L128 | Compute the return value: `uuid.uuid4()` — Generate a new random UUID. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L129 | Enter the protected block; failures are matched against `(ValueError, AttributeError, TypeError)` in order. |
| L130 | Compute the return value: `UUID(raw.strip())` — Parse or construct a UUID; invalid text raises a conversion error; inputs include `raw.strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L131 | Handle `(ValueError, AttributeError, TypeError)`; only a matching error from the associated try enters this body. |
| L132 | `_validation_error('Idempotency-Key must be a UUID.', project_id=project_id)` — Call [_validation_error](#walk--validation-error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L133 | Supply positional argument 1 to `_validation_error`: `'Idempotency-Key must be a UUID.'`. |
| L134 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L135 | Close the expression/container begun at L132; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L136 | Raise `AssertionError('unreachable')`; stop the normal path and transfer control to the nearest matching exception handler. |

<!-- END LINE WALKTHROUGH -->

### `_read_bounded_upload(file: UploadFile, *, project_id: UUID) -> tuple[bytes, str]`

**Arguments:** Multipart file and project error context. **Returns:** `(data, filename)`. **Work:** Validates a bare PDF filename, attempts to seek to start, reads at most `MAX_PDF_SIZE_BYTES+1`, and rejects empty/oversized content with 422. It does not close the framework-owned upload stream; magic/hash/parsing follow separately.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--read-bounded-upload"></a>

#### Line-by-line execution

[Current source: lines 139–160](../../../../Backend/app/api/documents.py#L139-L160). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `file` | `UploadFile`; required; positional or keyword | Uploaded PDF wrapper whose filename and bounded byte stream are inspected. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |

**Declared result:** `tuple[bytes, str]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 139 | def _read_bounded_upload(file: UploadFile, *, project_id: UUID) -> tuple[bytes, str]:
 140 |     filename = file.filename or ""
 141 |     if not is_pdf_filename(filename):
 142 |         _validation_error("Only PDF files are supported.", project_id=project_id)
 143 |         raise AssertionError("unreachable")  # pragma: no cover
 144 |     # Read with a hard bound so an oversized multipart body is
 145 |     # rejected without buffering unbounded bytes.
 146 |     try:
 147 |         file.file.seek(0)
 148 |     except Exception:
 149 |         pass
 150 |     data = file.file.read(MAX_PDF_SIZE_BYTES + 1)
 151 |     if not data:
 152 |         _validation_error("PDF file is empty.", project_id=project_id)
 153 |         raise AssertionError("unreachable")  # pragma: no cover
 154 |     if len(data) > MAX_PDF_SIZE_BYTES:
 155 |         _validation_error(
 156 |             f"PDF file exceeds the {MAX_PDF_SIZE_BYTES}-byte limit.",
 157 |             project_id=project_id,
 158 |         )
 159 |         raise AssertionError("unreachable")  # pragma: no cover
 160 |     return data, filename
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L139 | Define `_read_bounded_upload`; bind its arguments when called. The body executes only when invoked. |
| L140 | Evaluate the right-hand side, then bind/store it in `filename`: evaluate `file.filename or ''` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L141 | Evaluate the branch condition: invert the truthiness of `is_pdf_filename(filename)`. If truthy, enter L142; otherwise skip this indented block and continue after it. |
| L142 | `_validation_error('Only PDF files are supported.', project_id=project_id)` — Call [_validation_error](#walk--validation-error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L143 | Raise `AssertionError('unreachable')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L144 | Comment only: Read with a hard bound so an oversized multipart body is. It does not execute; the neighboring code determines behavior. |
| L145 | Comment only: rejected without buffering unbounded bytes.. It does not execute; the neighboring code determines behavior. |
| L146 | Enter the protected block; failures are matched against `Exception` in order. |
| L147 | `file.file.seek(0)` — Move the file/stream cursor to the specified byte offset so later reads start there. The return value is not assigned here. |
| L148 | Handle `Exception`; only a matching error from the associated try enters this body. |
| L149 | Do nothing; this explicitly empty branch continues execution (here it can intentionally ignore a caught exception). |
| L150 | Evaluate the right-hand side, then bind/store it in `data`: `file.file.read(MAX_PDF_SIZE_BYTES + 1)` — Read bytes from the open file/stream, bounded by the requested size when one is supplied; inputs include add/concatenate `MAX_PDF_SIZE_BYTES` and `1`, following the parentheses/operator precedence shown in `MAX_PDF_SIZE_BYTES + 1`. |
| L151 | Evaluate the branch condition: invert the truthiness of `data`. If truthy, enter L152; otherwise skip this indented block and continue after it. |
| L152 | `_validation_error('PDF file is empty.', project_id=project_id)` — Call [_validation_error](#walk--validation-error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L153 | Raise `AssertionError('unreachable')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L154 | Evaluate the branch condition: compare whether `len(data)` is greater than `MAX_PDF_SIZE_BYTES`. If truthy, enter L155; otherwise skip this indented block and continue after it. |
| L155 | `_validation_error(f'PDF file exceeds the {MAX_PDF_SIZE_BYTES}-byte limit.', project_id=project_id)` — Call [_validation_error](#walk--validation-error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L156 | Supply positional argument 1 to `_validation_error`: format a string by inserting `MAX_PDF_SIZE_BYTES` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L157 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L158 | Close the expression/container begun at L155; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L159 | Raise `AssertionError('unreachable')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L160 | Compute the return value: build a tuple containing `data`, `filename`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_check_extractable(data: bytes, filename: str, *, project_id: UUID) -> None`

**Arguments:** Bounded bytes, filename, project context. **Returns:** `None` after complete extraction succeeds. **Work:** Writes a named temporary `.pdf`, closes it, calls the shared `extract_pdf_chunks`, and discards preflight chunks. `PdfError` becomes 422. A `finally` block unlinks the temporary file even on parsing failure; other filesystem errors propagate.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--check-extractable"></a>

#### Line-by-line execution

[Current source: lines 163–177](../../../../Backend/app/api/documents.py#L163-L177). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `data` | `bytes`; required; positional or keyword | File bytes or input payload consumed by this operation, as specified by the annotation. |
| `filename` | `str`; required; positional or keyword | Display filename/citation hint, not proof of ownership or document identity. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 163 | def _check_extractable(data: bytes, filename: str, *, project_id: UUID) -> None:
 164 |     """Reject invalid, textless or over-budget PDFs before reservation."""
 165 |     from app.rag.pdf import PdfError, extract_pdf_chunks
 166 | 
 167 |     staged: Path | None = None
 168 |     try:
 169 |         with NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
 170 |             staged = Path(tmp.name)
 171 |             tmp.write(data)
 172 |         extract_pdf_chunks(staged, file_name=filename)
 173 |     except PdfError as exc:
 174 |         _validation_error(str(exc), project_id=project_id)
 175 |     finally:
 176 |         if staged is not None:
 177 |             staged.unlink(missing_ok=True)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L163 | Define `_check_extractable`; bind its arguments when called. The body executes only when invoked. |
| L164 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L165 | Import `PdfError`, `extract_pdf_chunks` from `app.rag.pdf`; inside a function this import is deferred until this path is reached. |
| L167 | Evaluate the right-hand side, then bind/store it in `staged`: None (no value). |
| L168 | Enter the protected block; failures are matched against `PdfError` in order. The finally block runs regardless of return or failure. |
| L169 | Enter `NamedTemporaryFile(suffix='.pdf', delete=False)` — Construct `NamedTemporaryFile` with the shown fields; its class/model initialization rules apply and bind its entered value to `tmp`. Context exits run in reverse order, including on return/exception. |
| L170 | Evaluate the right-hand side, then bind/store it in `staged`: `Path(tmp.name)` — Construct a filesystem path value (in FastAPI annotations, Path instead declares path-parameter metadata). |
| L171 | `tmp.write(data)` — Write supplied bytes/text to the open file handle. The return value is not assigned here. |
| L172 | `extract_pdf_chunks(staged, file_name=filename)` — Call [extract_pdf_chunks](../rag/pdf.md#walk-extract-pdf-chunks) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L173 | Handle `PdfError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L174 | `_validation_error(str(exc), project_id=project_id)` — Call [_validation_error](#walk--validation-error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result; inputs include `str(exc)` — Convert the input to its string representation. The return value is not assigned here. |
| L175 | Enter unconditional cleanup after the protected work, including on exception, return, break, or continue. |
| L176 | Evaluate the branch condition: compare whether `staged` is not the same object as `None`. If truthy, enter L177; otherwise skip this indented block and continue after it. |
| L177 | `staged.unlink(missing_ok=True)` — Remove the local file; missing_ok=True makes an already absent file harmless. The return value is not assigned here. |

<!-- END LINE WALKTHROUGH -->

## Route functions

### `list_documents(project_id, principal, session, cursor=None, limit=50) -> PaginatedResponse[DocumentDto]`

**Route:** `GET P` (200). **Arguments:** Project UUID, principal/session, query cursor, 1–200 limit. **Returns:** Converted document rows plus next cursor. **Work:** `list_owned_documents` checks live ownership and performs pagination; the route maps every row to its public DTO.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-list-documents"></a>

#### Line-by-line execution

[Current source: lines 185–203](../../../../Backend/app/api/documents.py#L185-L203). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project_id` | `UUID`; required; positional or keyword | Project UUID used to constrain resource lookup or provider metadata. |
| `principal` | `OnboardedPrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `session` | `SessionDep`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `cursor` | `Annotated[str \| None, Query()]`; default `None`; positional or keyword | Opaque page continuation token; null starts the first page. |
| `limit` | `Annotated[int, Query(ge=1, le=200)]`; default `50`; positional or keyword | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |

**Declared result:** `PaginatedResponse[DocumentDto]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 185 | @router.get(
 186 |     "/projects/{project_id}/documents", response_model=PaginatedResponse[DocumentDto]
 187 | )
 188 | def list_documents(
 189 |     project_id: UUID,
 190 |     principal: OnboardedPrincipalDep,
 191 |     session: SessionDep,
 192 |     cursor: Annotated[str | None, Query()] = None,
 193 |     limit: Annotated[int, Query(ge=1, le=200)] = 50,
 194 | ) -> PaginatedResponse[DocumentDto]:
 195 |     """GET .../documents -> paginated owner-scoped listing (forged project -> 404)."""
 196 |     # list_owned_documents re-verifies ownership (project -> user).
 197 |     rows, next_cursor = list_owned_documents(
 198 |         session, user_id=principal.id, project_id=project_id, cursor=cursor, limit=limit
 199 |     )
 200 |     return PaginatedResponse[DocumentDto](
 201 |         items=[document_to_dto(row) for row in rows],
 202 |         next_cursor=next_cursor,
 203 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L185 | Register the handler with FastAPI using `router.get('/projects/{project_id}/documents', response_model=PaginatedResponse[DocumentDto])`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L186 | Register the handler with FastAPI using `router.get('/projects/{project_id}/documents', response_model=PaginatedResponse[DocumentDto])`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L187 | Register the handler with FastAPI using `router.get('/projects/{project_id}/documents', response_model=PaginatedResponse[DocumentDto])`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L188 | Define `list_documents`; bind its arguments when called. The body executes only when invoked. |
| L189 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L190 | Declare parameter `principal` with annotation `OnboardedPrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L191 | Declare parameter `session` with annotation `SessionDep`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L192 | Declare parameter `cursor` with annotation `Annotated[str \| None, Query()]`. Opaque page continuation token; null starts the first page. |
| L193 | Declare parameter `limit` with annotation `Annotated[int, Query(ge=1, le=200)]`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. |
| L194 | Finish/continue the signature; the declared return annotation is `PaginatedResponse[DocumentDto]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L195 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L196 | Comment only: list_owned_documents re-verifies ownership (project -> user).. It does not execute; the neighboring code determines behavior. |
| L197 | Evaluate the right-hand side, then bind/store it in `(rows, next_cursor)`: `list_owned_documents(session, user_id=principal.id, project_id=project_id, cursor=cursor, limit=limit)` — Call [list_owned_documents](../repositories/documents.md#walk-list-owned-documents) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L198 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. Supply `cursor` = `cursor`. Opaque page continuation token; null starts the first page. Evaluate the value as: the current `cursor` value. Supply `limit` = `limit`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. Evaluate the value as: the current `limit` value. |
| L199 | Close the expression/container begun at L197; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L200 | Compute the return value: `PaginatedResponse[DocumentDto](items=[document_to_dto(row) for row in rows], next_cursor=next_cursor)` — Construct `PaginatedResponse[DocumentDto]` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L201 | Supply `items` = `[document_to_dto(row) for row in rows]`.  Evaluate the value as: iterate `rows`, binding each item to `row`; produce `document_to_dto(row)` into a new list. |
| L202 | Supply `next_cursor` = `next_cursor`. Continuation token to include in the returned page envelope, or null at the end. Evaluate the value as: the current `next_cursor` value. |
| L203 | Close the expression/container begun at L200; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `upload_document(project_id, file, principal, session, storage, job_queue, idempotency_key=None) -> UploadAcceptance`

- **Route/arguments:** `POST P` (202); project UUID, multipart `UploadFile`, principal/session, storage and queue dependencies, optional request UUID header.
- **Returns:** Current persisted document/job DTO pair; duplicate keys can replay an existing pair.
- **Work:** (1) Verify project ownership. (2) Bound/read, validate magic/hash/name/size, completely parse within the 200-page budget. (3) Resolve request key and allocate document/storage IDs, require bucket config. (4) Reserve document/job and commit; content conflict rolls back and raises 409 with the existing document ID. (5) Return immediately on duplicate without uploading again. (6) Upload privately with the external owner ID and original filename. (7) Inspect the created file. (8) If completion checks pass, queue and commit, then return.
- **Current completion detail:** The inspection response is assigned to `inspected`, but the actual completion/size/chunk-counter expression reads the earlier create result **`info`**. An incomplete create result therefore stays `awaiting_upload` even if inspection is complete. Completion requires its size equal uploaded bytes and, when total chunks > 0, exact uploaded/total equality.
- **Errors/state:** Invalid PDFs fail before reservation. Storage-create exceptions and handled inspect failures become 503 carrying durable document/job IDs; their reservation remains for reconciliation. A returned 202 may still be `awaiting_upload`, and never by itself means indexing finished. Storage create/inspect occur after reservation commit.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-upload-document"></a>

#### Line-by-line execution

[Current source: lines 211–367](../../../../Backend/app/api/documents.py#L211-L367). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project_id` | `UUID`; required; positional or keyword | Project UUID used to constrain resource lookup or provider metadata. |
| `file` | `Annotated[UploadFile, File()]`; required; positional or keyword | Uploaded PDF wrapper whose filename and bounded byte stream are inspected. |
| `principal` | `OnboardedPrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `session` | `SessionDep`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `storage` | `Annotated[object, Depends(get_storage_adapter)]`; required; positional or keyword | Storage collaborator for private file creation, inspection, ranged reads, or deletion. |
| `job_queue` | `Annotated[DirectJobQueue, Depends(get_job_queue)]`; required; positional or keyword | Caller-supplied job queue; each read, transformation, and validation is traced below. |
| `idempotency_key` | `Annotated[str \| None, Header(alias='Idempotency-Key')]`; default `None`; positional or keyword | Caller-supplied idempotency key; each read, transformation, and validation is traced below. |

**Declared result:** `UploadAcceptance`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 211 | @router.post(
 212 |     "/projects/{project_id}/documents",
 213 |     response_model=UploadAcceptance,
 214 |     status_code=202,
 215 | )
 216 | def upload_document(
 217 |     project_id: UUID,
 218 |     file: Annotated[UploadFile, File()],
 219 |     principal: OnboardedPrincipalDep,
 220 |     session: SessionDep,
 221 |     storage: Annotated[object, Depends(get_storage_adapter)],
 222 |     job_queue: Annotated[DirectJobQueue, Depends(get_job_queue)],
 223 |     idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
 224 | ) -> UploadAcceptance:
 225 |     """POST .../documents -> 202 {document, job} (see module docstring)."""
 226 |     # 1. Ownership (404 for foreign/forged projects).
 227 |     get_owned_project_or_404(session, user_id=principal.id, project_id=project_id)
 228 | 
 229 |     # 2. Validate/stage + fingerprint (no row/job/storage writes yet).
 230 |     data, file_name = _read_bounded_upload(file, project_id=project_id)
 231 |     try:
 232 |         content_sha256 = validate_pdf_bytes(data, file_name)
 233 |     except ValueError as exc:
 234 |         _validation_error(str(exc), project_id=project_id)
 235 |         raise AssertionError("unreachable")  # pragma: no cover
 236 |     _check_extractable(data, file_name, project_id=project_id)
 237 | 
 238 |     upload_request_id = _resolve_upload_request_id(idempotency_key, project_id=project_id)
 239 |     document_id = uuid.uuid4()
 240 |     appwrite_file_id = generate_appwrite_file_id()
 241 | 
 242 |     try:
 243 |         bucket_id = default_bucket_id()
 244 |     except RuntimeError:
 245 |         raise_api_error(
 246 |             503,
 247 |             ErrorCode.SERVICE_UNAVAILABLE,
 248 |             "Storage is not configured.",
 249 |             project_id=project_id,
 250 |         )
 251 |         raise AssertionError("unreachable")  # pragma: no cover
 252 | 
 253 |     # 3. Reservation transaction (Pending + awaiting_upload).
 254 |     try:
 255 |         document, job, is_duplicate = reserve_upload(
 256 |             session,
 257 |             owner_user_id=principal.id,
 258 |             project_id=project_id,
 259 |             document_id=document_id,
 260 |             appwrite_file_id=appwrite_file_id,
 261 |             file_name=file_name,
 262 |             file_size=len(data),
 263 |             mime_type=PDF_MIME_TYPE,
 264 |             upload_request_id=upload_request_id,
 265 |             content_sha256=content_sha256,
 266 |             bucket_id=bucket_id,
 267 |             job_queue=job_queue,
 268 |         )
 269 |     except DocumentConflictError as exc:
 270 |         session.rollback()
 271 |         raise_api_error(
 272 |             409,
 273 |             ErrorCode.DUPLICATE_REQUEST_CONFLICT,
 274 |             "This request key was already used with different content.",
 275 |             project_id=project_id,
 276 |             document_id=exc.document.id,
 277 |         )
 278 |         raise AssertionError("unreachable")  # pragma: no cover
 279 | 
 280 |     session.commit()
 281 |     # Re-fetch identities for the response (detached after commit is
 282 |     # safe with expire_on_commit=False, but re-read keeps it explicit).
 283 |     if is_duplicate:
 284 |         # Same key + same content: return the original pair, never
 285 |         # reset a running/completed job, never touch storage again.
 286 |         return UploadAcceptance(
 287 |             document=document_to_dto(document), job=job_to_dto(job)
 288 |         )
 289 | 
 290 |     # 4. Storage create with the reserved ID (outside any transaction).
 291 |     try:
 292 |         info = storage.create_storage_file(  # type: ignore[attr-defined]
 293 |             bucket_id=bucket_id,
 294 |             file_id=appwrite_file_id,
 295 |             data=data,
 296 |             mime_type=PDF_MIME_TYPE,
 297 |             owner_appwrite_user_id=principal.appwrite_user_id,
 298 |             file_name=file_name,
 299 |         )
 300 |     except StorageUnavailableError:
 301 |         raise_api_error(
 302 |             503,
 303 |             ErrorCode.SERVICE_UNAVAILABLE,
 304 |             "Storage upload failed; the document is pending reconciliation.",
 305 |             project_id=project_id,
 306 |             document_id=document.id,
 307 |             job_id=job.id,
 308 |         )
 309 |         raise AssertionError("unreachable")  # pragma: no cover
 310 |     except Exception:
 311 |         raise_api_error(
 312 |             503,
 313 |             ErrorCode.SERVICE_UNAVAILABLE,
 314 |             "Storage upload failed; the document is pending reconciliation.",
 315 |             project_id=project_id,
 316 |             document_id=document.id,
 317 |             job_id=job.id,
 318 |         )
 319 |         raise AssertionError("unreachable")  # pragma: no cover
 320 | 
 321 |     # 5. Completion inspection -> conditional queue (second transaction).
 322 |     try:
 323 |         inspected = storage.inspect_storage_file(  # type: ignore[attr-defined]
 324 |             bucket_id=bucket_id, file_id=appwrite_file_id
 325 |         )
 326 |     except StorageNotFoundError:
 327 |         raise_api_error(
 328 |             503,
 329 |             ErrorCode.SERVICE_UNAVAILABLE,
 330 |             "Storage upload was not found after create; the document is pending reconciliation.",
 331 |             project_id=project_id,
 332 |             document_id=document.id,
 333 |             job_id=job.id,
 334 |         )
 335 |         raise AssertionError("unreachable")  # pragma: no cover
 336 |     except StorageUnavailableError:
 337 |         raise_api_error(
 338 |             503,
 339 |             ErrorCode.SERVICE_UNAVAILABLE,
 340 |             "Storage inspection failed; the document is pending reconciliation.",
 341 |             project_id=project_id,
 342 |             document_id=document.id,
 343 |             job_id=job.id,
 344 |         )
 345 |         raise AssertionError("unreachable")  # pragma: no cover
 346 | 
 347 |     complete = (
 348 |         getattr(info, "completed", False)
 349 |         and int(getattr(info, "size", 0)) == len(data)
 350 |         and not (
 351 |             int(getattr(info, "chunks_total", 0)) > 0
 352 |             and int(getattr(info, "chunks_uploaded", 0))
 353 |             != int(getattr(info, "chunks_total", 0))
 354 |         )
 355 |     )
 356 |     if complete:
 357 |         try:
 358 |             confirm_upload_completion(session, document=document, job=job)
 359 |         except Exception:
 360 |             session.rollback()
 361 |             raise
 362 |         session.commit()
 363 | 
 364 |     # 6. 202 with current states (queued when complete, else awaiting_upload).
 365 |     return UploadAcceptance(
 366 |         document=document_to_dto(document), job=job_to_dto(job)
 367 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L211 | Register the handler with FastAPI using `router.post('/projects/{project_id}/documents', response_model=UploadAcceptance, status_code=202)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L212 | Register the handler with FastAPI using `router.post('/projects/{project_id}/documents', response_model=UploadAcceptance, status_code=202)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L213 | Register the handler with FastAPI using `router.post('/projects/{project_id}/documents', response_model=UploadAcceptance, status_code=202)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L214 | Register the handler with FastAPI using `router.post('/projects/{project_id}/documents', response_model=UploadAcceptance, status_code=202)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L215 | Register the handler with FastAPI using `router.post('/projects/{project_id}/documents', response_model=UploadAcceptance, status_code=202)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L216 | Define `upload_document`; bind its arguments when called. The body executes only when invoked. |
| L217 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L218 | Declare parameter `file` with annotation `Annotated[UploadFile, File()]`. Uploaded PDF wrapper whose filename and bounded byte stream are inspected. |
| L219 | Declare parameter `principal` with annotation `OnboardedPrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L220 | Declare parameter `session` with annotation `SessionDep`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L221 | Declare parameter `storage` with annotation `Annotated[object, Depends(get_storage_adapter)]`. Storage collaborator for private file creation, inspection, ranged reads, or deletion. |
| L222 | Declare parameter `job_queue` with annotation `Annotated[DirectJobQueue, Depends(get_job_queue)]`. Caller-supplied job queue; its uses and transformations are traced below. |
| L223 | Declare parameter `idempotency_key` with annotation `Annotated[str \| None, Header(alias='Idempotency-Key')]`. Caller-supplied idempotency key; its uses and transformations are traced below. |
| L224 | Finish/continue the signature; the declared return annotation is `UploadAcceptance`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L225 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L226 | Comment only: 1. Ownership (404 for foreign/forged projects).. It does not execute; the neighboring code determines behavior. |
| L227 | `get_owned_project_or_404(session, user_id=principal.id, project_id=project_id)` — Call [get_owned_project_or_404](../repositories/projects.md#walk-get-owned-project-or-404) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L229 | Comment only: 2. Validate/stage + fingerprint (no row/job/storage writes yet).. It does not execute; the neighboring code determines behavior. |
| L230 | Evaluate the right-hand side, then bind/store it in `(data, file_name)`: `_read_bounded_upload(file, project_id=project_id)` — Call [_read_bounded_upload](#walk--read-bounded-upload) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L231 | Enter the protected block; failures are matched against `ValueError` in order. |
| L232 | Evaluate the right-hand side, then bind/store it in `content_sha256`: `validate_pdf_bytes(data, file_name)` — Call [validate_pdf_bytes](../services/storage.md#walk-validate-pdf-bytes) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L233 | Handle `ValueError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L234 | `_validation_error(str(exc), project_id=project_id)` — Call [_validation_error](#walk--validation-error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result; inputs include `str(exc)` — Convert the input to its string representation. The return value is not assigned here. |
| L235 | Raise `AssertionError('unreachable')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L236 | `_check_extractable(data, file_name, project_id=project_id)` — Call [_check_extractable](#walk--check-extractable) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L238 | Evaluate the right-hand side, then bind/store it in `upload_request_id`: `_resolve_upload_request_id(idempotency_key, project_id=project_id)` — Call [_resolve_upload_request_id](#walk--resolve-upload-request-id) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L239 | Evaluate the right-hand side, then bind/store it in `document_id`: `uuid.uuid4()` — Generate a new random UUID. |
| L240 | Evaluate the right-hand side, then bind/store it in `appwrite_file_id`: `generate_appwrite_file_id()` — Call [generate_appwrite_file_id](../services/storage.md#walk-generate-appwrite-file-id) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L242 | Enter the protected block; failures are matched against `RuntimeError` in order. |
| L243 | Evaluate the right-hand side, then bind/store it in `bucket_id`: `default_bucket_id()` — Call [default_bucket_id](../services/storage.md#walk-default-bucket-id) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L244 | Handle `RuntimeError`; only a matching error from the associated try enters this body. |
| L245 | `raise_api_error(503, ErrorCode.SERVICE_UNAVAILABLE, 'Storage is not configured.', project_id=project_id)` — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L246 | Supply positional argument 1 to `raise_api_error`: `503`. |
| L247 | Supply positional argument 2 to `raise_api_error`: the `SERVICE_UNAVAILABLE` attribute of `ErrorCode`. |
| L248 | Supply positional argument 3 to `raise_api_error`: `'Storage is not configured.'`. |
| L249 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L250 | Close the expression/container begun at L245; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L251 | Raise `AssertionError('unreachable')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L253 | Comment only: 3. Reservation transaction (Pending + awaiting_upload).. It does not execute; the neighboring code determines behavior. |
| L254 | Enter the protected block; failures are matched against `DocumentConflictError` in order. |
| L255 | Evaluate the right-hand side, then bind/store it in `(document, job, is_duplicate)`: `reserve_upload` with the arguments detailed below — Call [reserve_upload](../repositories/documents.md#walk-reserve-upload) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L256 | Supply positional argument 1 to `reserve_upload`: the current `session` value. |
| L257 | Supply `owner_user_id` = `principal.id`. Internal owner UUID copied into the job's durable ownership snapshot. Evaluate the value as: the `id` attribute of `principal`. |
| L258 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L259 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L260 | Supply `appwrite_file_id` = `appwrite_file_id`.  Evaluate the value as: the current `appwrite_file_id` value. |
| L261 | Supply `file_name` = `file_name`. Display PDF filename; immutable IDs establish ownership and evidence identity. Evaluate the value as: the current `file_name` value. |
| L262 | Supply `file_size` = `len(data)`. PDF size in bytes recorded in document metadata or checked during upload. Evaluate the value as: `len(data)` — Count the items/characters in the supplied container/string. |
| L263 | Supply `mime_type` = `PDF_MIME_TYPE`. Declared storage content type; accepted application uploads use application/pdf. Evaluate the value as: the current `PDF_MIME_TYPE` value. |
| L264 | Supply `upload_request_id` = `upload_request_id`. Upload request UUID used for per-project idempotency. Evaluate the value as: the current `upload_request_id` value. |
| L265 | Supply `content_sha256` = `content_sha256`. Lowercase SHA-256 content fingerprint used for upload identity/integrity expectations. Evaluate the value as: the current `content_sha256` value. |
| L266 | Supply `bucket_id` = `bucket_id`. Appwrite bucket identifier. Evaluate the value as: the current `bucket_id` value. |
| L267 | Supply `job_queue` = `job_queue`.  Evaluate the value as: the current `job_queue` value. |
| L268 | Close the expression/container begun at L255; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L269 | Handle `DocumentConflictError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L270 | `session.rollback()` — Roll back the active transaction and discard its uncommitted database changes. The return value is not assigned here. |
| L271 | `raise_api_error` with the arguments detailed below — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L272 | Supply positional argument 1 to `raise_api_error`: `409`. |
| L273 | Supply positional argument 2 to `raise_api_error`: the `DUPLICATE_REQUEST_CONFLICT` attribute of `ErrorCode`. |
| L274 | Supply positional argument 3 to `raise_api_error`: `'This request key was already used with different content.'`. |
| L275 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L276 | Supply `document_id` = `exc.document.id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the `id` attribute of `exc.document`. |
| L277 | Close the expression/container begun at L271; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L278 | Raise `AssertionError('unreachable')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L280 | `session.commit()` — Flush pending changes and commit this transaction; subsequent failures cannot undo that completed transaction. The return value is not assigned here. |
| L281 | Comment only: Re-fetch identities for the response (detached after commit is. It does not execute; the neighboring code determines behavior. |
| L282 | Comment only: safe with expire_on_commit=False, but re-read keeps it explicit).. It does not execute; the neighboring code determines behavior. |
| L283 | Evaluate the branch condition: the current `is_duplicate` value. If truthy, enter L286; otherwise skip this indented block and continue after it. |
| L284 | Comment only: Same key + same content: return the original pair, never. It does not execute; the neighboring code determines behavior. |
| L285 | Comment only: reset a running/completed job, never touch storage again.. It does not execute; the neighboring code determines behavior. |
| L286 | Compute the return value: `UploadAcceptance(document=document_to_dto(document), job=job_to_dto(job))` — Construct `UploadAcceptance` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L287 | Supply `document` = `document_to_dto(document)`.  Evaluate the value as: `document_to_dto(document)` — Call [document_to_dto](../repositories/documents.md#walk-document-to-dto) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Supply `job` = `job_to_dto(job)`.  Evaluate the value as: `job_to_dto(job)` — Call [job_to_dto](../repositories/documents.md#walk-job-to-dto) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L288 | Close the expression/container begun at L286; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L290 | Comment only: 4. Storage create with the reserved ID (outside any transaction).. It does not execute; the neighboring code determines behavior. |
| L291 | Enter the protected block; failures are matched against `StorageUnavailableError`, `Exception` in order. |
| L292 | Evaluate the right-hand side, then bind/store it in `info`: `storage.create_storage_file` with the arguments detailed below — Create the private PDF at the reserved storage reference outside a database transaction. |
| L293 | Supply `bucket_id` = `bucket_id`. Appwrite bucket identifier. Evaluate the value as: the current `bucket_id` value. |
| L294 | Supply `file_id` = `appwrite_file_id`. Reserved Appwrite storage-object identifier. Evaluate the value as: the current `appwrite_file_id` value. |
| L295 | Supply `data` = `data`. File bytes or input payload consumed by this operation, as specified by the annotation. Evaluate the value as: the current `data` value. |
| L296 | Supply `mime_type` = `PDF_MIME_TYPE`. Declared storage content type; accepted application uploads use application/pdf. Evaluate the value as: the current `PDF_MIME_TYPE` value. |
| L297 | Supply `owner_appwrite_user_id` = `principal.appwrite_user_id`. External Appwrite user ID used for private file permissions. Evaluate the value as: the `appwrite_user_id` attribute of `principal`. |
| L298 | Supply `file_name` = `file_name`. Display PDF filename; immutable IDs establish ownership and evidence identity. Evaluate the value as: the current `file_name` value. |
| L299 | Close the expression/container begun at L292; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L300 | Handle `StorageUnavailableError`; only a matching error from the associated try enters this body. |
| L301 | `raise_api_error` with the arguments detailed below — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L302 | Supply positional argument 1 to `raise_api_error`: `503`. |
| L303 | Supply positional argument 2 to `raise_api_error`: the `SERVICE_UNAVAILABLE` attribute of `ErrorCode`. |
| L304 | Supply positional argument 3 to `raise_api_error`: `'Storage upload failed; the document is pending reconciliation.'`. |
| L305 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L306 | Supply `document_id` = `document.id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the `id` attribute of `document`. |
| L307 | Supply `job_id` = `job.id`. Durable processing-job UUID. Evaluate the value as: the `id` attribute of `job`. |
| L308 | Close the expression/container begun at L301; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L309 | Raise `AssertionError('unreachable')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L310 | Handle `Exception`; only a matching error from the associated try enters this body. |
| L311 | `raise_api_error` with the arguments detailed below — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L312 | Supply positional argument 1 to `raise_api_error`: `503`. |
| L313 | Supply positional argument 2 to `raise_api_error`: the `SERVICE_UNAVAILABLE` attribute of `ErrorCode`. |
| L314 | Supply positional argument 3 to `raise_api_error`: `'Storage upload failed; the document is pending reconciliation.'`. |
| L315 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L316 | Supply `document_id` = `document.id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the `id` attribute of `document`. |
| L317 | Supply `job_id` = `job.id`. Durable processing-job UUID. Evaluate the value as: the `id` attribute of `job`. |
| L318 | Close the expression/container begun at L311; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L319 | Raise `AssertionError('unreachable')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L321 | Comment only: 5. Completion inspection -> conditional queue (second transaction).. It does not execute; the neighboring code determines behavior. |
| L322 | Enter the protected block; failures are matched against `StorageNotFoundError`, `StorageUnavailableError` in order. |
| L323 | Evaluate the right-hand side, then bind/store it in `inspected`: `storage.inspect_storage_file(bucket_id=bucket_id, file_id=appwrite_file_id)` — Inspect private storage metadata for this bucket/file reference; provider failures propagate through the adapter. |
| L324 | Supply `bucket_id` = `bucket_id`. Appwrite bucket identifier. Evaluate the value as: the current `bucket_id` value. Supply `file_id` = `appwrite_file_id`. Reserved Appwrite storage-object identifier. Evaluate the value as: the current `appwrite_file_id` value. |
| L325 | Close the expression/container begun at L323; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L326 | Handle `StorageNotFoundError`; only a matching error from the associated try enters this body. |
| L327 | `raise_api_error` with the arguments detailed below — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L328 | Supply positional argument 1 to `raise_api_error`: `503`. |
| L329 | Supply positional argument 2 to `raise_api_error`: the `SERVICE_UNAVAILABLE` attribute of `ErrorCode`. |
| L330 | Supply positional argument 3 to `raise_api_error`: `'Storage upload was not found after create; the document is pending reconciliation.'`. |
| L331 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L332 | Supply `document_id` = `document.id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the `id` attribute of `document`. |
| L333 | Supply `job_id` = `job.id`. Durable processing-job UUID. Evaluate the value as: the `id` attribute of `job`. |
| L334 | Close the expression/container begun at L327; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L335 | Raise `AssertionError('unreachable')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L336 | Handle `StorageUnavailableError`; only a matching error from the associated try enters this body. |
| L337 | `raise_api_error` with the arguments detailed below — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L338 | Supply positional argument 1 to `raise_api_error`: `503`. |
| L339 | Supply positional argument 2 to `raise_api_error`: the `SERVICE_UNAVAILABLE` attribute of `ErrorCode`. |
| L340 | Supply positional argument 3 to `raise_api_error`: `'Storage inspection failed; the document is pending reconciliation.'`. |
| L341 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L342 | Supply `document_id` = `document.id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the `id` attribute of `document`. |
| L343 | Supply `job_id` = `job.id`. Durable processing-job UUID. Evaluate the value as: the `id` attribute of `job`. |
| L344 | Close the expression/container begun at L337; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L345 | Raise `AssertionError('unreachable')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L347 | Evaluate the right-hand side, then bind/store it in `complete`: evaluate `getattr(info, 'completed', False) and int(getattr(info, 'size', 0)) == len(data) and (not (int(getattr(info, 'chunks_total', 0)) > 0 and int(getattr(info, 'chunks_uploaded', 0)) != int(getattr(info, 'chunks_total', 0))))` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. |
| L348 | `getattr(info, 'completed', False)` — Read the named attribute, using the supplied default only if the attribute is absent. |
| L349 | Convert the input to an integer (using the optional numeric base). |
| L350 | Contribute invert the truthiness of `int(getattr(info, 'chunks_total', 0)) > 0 and int(getattr(info, 'chunks_uploaded', 0)) != int(getattr(info, 'chunks_total', 0))` to the expression being assembled. |
| L351 | `int(getattr(info, 'chunks_total', 0))` — Convert the input to an integer (using the optional numeric base); inputs include `getattr(info, 'chunks_total', 0)` — Read the named attribute, using the supplied default only if the attribute is absent. |
| L352 | Convert the input to an integer (using the optional numeric base). |
| L353 | Convert the input to an integer (using the optional numeric base). |
| L354 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L355 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L356 | Evaluate the branch condition: the current `complete` value. If truthy, enter L357; otherwise skip this indented block and continue after it. |
| L357 | Enter the protected block; failures are matched against `Exception` in order. |
| L358 | `confirm_upload_completion(session, document=document, job=job)` — Call [confirm_upload_completion](../repositories/documents.md#walk-confirm-upload-completion) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L359 | Handle `Exception`; only a matching error from the associated try enters this body. |
| L360 | `session.rollback()` — Roll back the active transaction and discard its uncommitted database changes. The return value is not assigned here. |
| L361 | Re-raise the currently handled exception with its traceback; no replacement result is returned. |
| L362 | `session.commit()` — Flush pending changes and commit this transaction; subsequent failures cannot undo that completed transaction. The return value is not assigned here. |
| L364 | Comment only: 6. 202 with current states (queued when complete, else awaiting_upload).. It does not execute; the neighboring code determines behavior. |
| L365 | Compute the return value: `UploadAcceptance(document=document_to_dto(document), job=job_to_dto(job))` — Construct `UploadAcceptance` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L366 | Supply `document` = `document_to_dto(document)`.  Evaluate the value as: `document_to_dto(document)` — Call [document_to_dto](../repositories/documents.md#walk-document-to-dto) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Supply `job` = `job_to_dto(job)`.  Evaluate the value as: `job_to_dto(job)` — Call [job_to_dto](../repositories/documents.md#walk-job-to-dto) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L367 | Close the expression/container begun at L365; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `read_document(project_id, document_id, principal, session) -> DocumentDto`

**Route:** `GET P/{document_id}` (200). **Arguments:** Path UUIDs, principal/session. **Returns:** Public document DTO. **Work:** Joins ownership through the exact live project/document; absent/foreign/tombstoned scope becomes 404, otherwise converts the ORM row.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-read-document"></a>

#### Line-by-line execution

[Current source: lines 375–391](../../../../Backend/app/api/documents.py#L375-L391). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project_id` | `UUID`; required; positional or keyword | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID`; required; positional or keyword | Document UUID; filenames do not establish document identity. |
| `principal` | `OnboardedPrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `session` | `SessionDep`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |

**Declared result:** `DocumentDto`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 375 | @router.get(
 376 |     "/projects/{project_id}/documents/{document_id}", response_model=DocumentDto
 377 | )
 378 | def read_document(
 379 |     project_id: UUID,
 380 |     document_id: UUID,
 381 |     principal: OnboardedPrincipalDep,
 382 |     session: SessionDep,
 383 | ) -> DocumentDto:
 384 |     """GET .../documents/{id} -> owner-scoped read."""
 385 |     document = get_owned_document_or_404(
 386 |         session,
 387 |         user_id=principal.id,
 388 |         project_id=project_id,
 389 |         document_id=document_id,
 390 |     )
 391 |     return document_to_dto(document)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L375 | Register the handler with FastAPI using `router.get('/projects/{project_id}/documents/{document_id}', response_model=DocumentDto)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L376 | Register the handler with FastAPI using `router.get('/projects/{project_id}/documents/{document_id}', response_model=DocumentDto)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L377 | Register the handler with FastAPI using `router.get('/projects/{project_id}/documents/{document_id}', response_model=DocumentDto)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L378 | Define `read_document`; bind its arguments when called. The body executes only when invoked. |
| L379 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L380 | Declare parameter `document_id` with annotation `UUID`. Document UUID; filenames do not establish document identity. |
| L381 | Declare parameter `principal` with annotation `OnboardedPrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L382 | Declare parameter `session` with annotation `SessionDep`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L383 | Finish/continue the signature; the declared return annotation is `DocumentDto`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L384 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L385 | Evaluate the right-hand side, then bind/store it in `document`: `get_owned_document_or_404(session, user_id=principal.id, project_id=project_id, document_id=document_id)` — Call [get_owned_document_or_404](../repositories/projects.md#walk-get-owned-document-or-404) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L386 | Supply positional argument 1 to `get_owned_document_or_404`: the current `session` value. |
| L387 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. |
| L388 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L389 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L390 | Close the expression/container begun at L385; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L391 | Compute the return value: `document_to_dto(document)` — Call [document_to_dto](../repositories/documents.md#walk-document-to-dto) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `delete_document(project_id, document_id, principal, session, job_queue) -> DocumentDeleteAccepted`

**Route:** `DELETE P/{document_id}` (202). **Arguments:** Scope UUIDs, principal/session, queue. **Returns:** Project/document/cleanup-job IDs and accepted flag. **Work:** Looks up ownership including tombstones (missing → 404, already deleting → 409); resolves bucket (missing → 503); tombstones and enqueues cleanup in the same transaction; rolls back mutation failures and commits success. No provider delete is performed inline.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-delete-document"></a>

#### Line-by-line execution

[Current source: lines 394–463](../../../../Backend/app/api/documents.py#L394-L463). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project_id` | `UUID`; required; positional or keyword | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID`; required; positional or keyword | Document UUID; filenames do not establish document identity. |
| `principal` | `OnboardedPrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `session` | `SessionDep`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `job_queue` | `Annotated[DirectJobQueue, Depends(get_job_queue)]`; required; positional or keyword | Caller-supplied job queue; each read, transformation, and validation is traced below. |

**Declared result:** `DocumentDeleteAccepted`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 394 | @router.delete(
 395 |     "/projects/{project_id}/documents/{document_id}",
 396 |     response_model=DocumentDeleteAccepted,
 397 |     status_code=202,
 398 | )
 399 | def delete_document(
 400 |     project_id: UUID,
 401 |     document_id: UUID,
 402 |     principal: OnboardedPrincipalDep,
 403 |     session: SessionDep,
 404 |     job_queue: Annotated[DirectJobQueue, Depends(get_job_queue)],
 405 | ) -> DocumentDeleteAccepted:
 406 |     """DELETE .../documents/{id} -> 202 {projectId, documentId, jobId}."""
 407 |     from app.db.queries import get_owned_document as _query_doc
 408 | 
 409 |     # Distinguish "already deleting" (409) from "never owned" (404).
 410 |     existing = _query_doc(
 411 |         session,
 412 |         user_id=principal.id,
 413 |         project_id=project_id,
 414 |         document_id=document_id,
 415 |         include_deleted=True,
 416 |     )
 417 |     if existing is None:
 418 |         raise_api_error(
 419 |             404,
 420 |             ErrorCode.NOT_FOUND,
 421 |             "Document not found.",
 422 |             project_id=project_id,
 423 |             document_id=document_id,
 424 |         )
 425 |     if existing.deleted_at is not None:
 426 |         session.rollback()
 427 |         raise_api_error(
 428 |             409,
 429 |             ErrorCode.CONFLICT,
 430 |             "Document is already being deleted.",
 431 |             project_id=project_id,
 432 |             document_id=document_id,
 433 |         )
 434 |     document = existing
 435 | 
 436 |     try:
 437 |         bucket_id = default_bucket_id()
 438 |     except RuntimeError:
 439 |         session.rollback()
 440 |         raise_api_error(
 441 |             503,
 442 |             ErrorCode.SERVICE_UNAVAILABLE,
 443 |             "Storage is not configured.",
 444 |             project_id=project_id,
 445 |             document_id=document_id,
 446 |         )
 447 |         raise AssertionError("unreachable")  # pragma: no cover
 448 | 
 449 |     try:
 450 |         tombstone_document(session, document)
 451 |         delete_job = enqueue_document_delete(
 452 |             session,
 453 |             document=document,
 454 |             bucket_id=bucket_id,
 455 |             job_queue=job_queue,
 456 |         )
 457 |     except Exception:
 458 |         session.rollback()
 459 |         raise
 460 |     session.commit()
 461 |     return DocumentDeleteAccepted(
 462 |         project_id=project_id, document_id=document.id, job_id=delete_job.id
 463 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L394 | Register the handler with FastAPI using `router.delete('/projects/{project_id}/documents/{document_id}', response_model=DocumentDeleteAccepted, status_code=202)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L395 | Register the handler with FastAPI using `router.delete('/projects/{project_id}/documents/{document_id}', response_model=DocumentDeleteAccepted, status_code=202)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L396 | Register the handler with FastAPI using `router.delete('/projects/{project_id}/documents/{document_id}', response_model=DocumentDeleteAccepted, status_code=202)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L397 | Register the handler with FastAPI using `router.delete('/projects/{project_id}/documents/{document_id}', response_model=DocumentDeleteAccepted, status_code=202)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L398 | Register the handler with FastAPI using `router.delete('/projects/{project_id}/documents/{document_id}', response_model=DocumentDeleteAccepted, status_code=202)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L399 | Define `delete_document`; bind its arguments when called. The body executes only when invoked. |
| L400 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L401 | Declare parameter `document_id` with annotation `UUID`. Document UUID; filenames do not establish document identity. |
| L402 | Declare parameter `principal` with annotation `OnboardedPrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L403 | Declare parameter `session` with annotation `SessionDep`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L404 | Declare parameter `job_queue` with annotation `Annotated[DirectJobQueue, Depends(get_job_queue)]`. Caller-supplied job queue; its uses and transformations are traced below. |
| L405 | Finish/continue the signature; the declared return annotation is `DocumentDeleteAccepted`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L406 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L407 | Import `get_owned_document` as `_query_doc` from `app.db.queries`; inside a function this import is deferred until this path is reached. |
| L409 | Comment only: Distinguish "already deleting" (409) from "never owned" (404).. It does not execute; the neighboring code determines behavior. |
| L410 | Evaluate the right-hand side, then bind/store it in `existing`: `_query_doc(session, user_id=principal.id, project_id=project_id, document_id=document_id, include_deleted=True)` — Call [_query_doc](../db/queries.md#walk-get-owned-document) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L411 | Supply positional argument 1 to `_query_doc`: the current `session` value. |
| L412 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. |
| L413 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L414 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L415 | Supply `include_deleted` = `True`. Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. Evaluate the value as: `True`. |
| L416 | Close the expression/container begun at L410; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L417 | Evaluate the branch condition: compare whether `existing` is the same object as `None`. If truthy, enter L418; otherwise skip this indented block and continue after it. |
| L418 | `raise_api_error(404, ErrorCode.NOT_FOUND, 'Document not found.', project_id=project_id, document_id=document_id)` — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L419 | Supply positional argument 1 to `raise_api_error`: `404`. |
| L420 | Supply positional argument 2 to `raise_api_error`: the `NOT_FOUND` attribute of `ErrorCode`. |
| L421 | Supply positional argument 3 to `raise_api_error`: `'Document not found.'`. |
| L422 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L423 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L424 | Close the expression/container begun at L418; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L425 | Evaluate the branch condition: compare whether `existing.deleted_at` is not the same object as `None`. If truthy, enter L426; otherwise skip this indented block and continue after it. |
| L426 | `session.rollback()` — Roll back the active transaction and discard its uncommitted database changes. The return value is not assigned here. |
| L427 | `raise_api_error(409, ErrorCode.CONFLICT, 'Document is already being deleted.', project_id=project_id, document_id=document_id)` — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L428 | Supply positional argument 1 to `raise_api_error`: `409`. |
| L429 | Supply positional argument 2 to `raise_api_error`: the `CONFLICT` attribute of `ErrorCode`. |
| L430 | Supply positional argument 3 to `raise_api_error`: `'Document is already being deleted.'`. |
| L431 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L432 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L433 | Close the expression/container begun at L427; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L434 | Evaluate the right-hand side, then bind/store it in `document`: the current `existing` value. |
| L436 | Enter the protected block; failures are matched against `RuntimeError` in order. |
| L437 | Evaluate the right-hand side, then bind/store it in `bucket_id`: `default_bucket_id()` — Call [default_bucket_id](../services/storage.md#walk-default-bucket-id) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L438 | Handle `RuntimeError`; only a matching error from the associated try enters this body. |
| L439 | `session.rollback()` — Roll back the active transaction and discard its uncommitted database changes. The return value is not assigned here. |
| L440 | `raise_api_error(503, ErrorCode.SERVICE_UNAVAILABLE, 'Storage is not configured.', project_id=project_id, document_id=document_id)` — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L441 | Supply positional argument 1 to `raise_api_error`: `503`. |
| L442 | Supply positional argument 2 to `raise_api_error`: the `SERVICE_UNAVAILABLE` attribute of `ErrorCode`. |
| L443 | Supply positional argument 3 to `raise_api_error`: `'Storage is not configured.'`. |
| L444 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L445 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L446 | Close the expression/container begun at L440; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L447 | Raise `AssertionError('unreachable')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L449 | Enter the protected block; failures are matched against `Exception` in order. |
| L450 | `tombstone_document(session, document)` — Call [tombstone_document](../repositories/documents.md#walk-tombstone-document) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L451 | Evaluate the right-hand side, then bind/store it in `delete_job`: `enqueue_document_delete(session, document=document, bucket_id=bucket_id, job_queue=job_queue)` — Call [enqueue_document_delete](../repositories/documents.md#walk-enqueue-document-delete) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L452 | Supply positional argument 1 to `enqueue_document_delete`: the current `session` value. |
| L453 | Supply `document` = `document`.  Evaluate the value as: the current `document` value. |
| L454 | Supply `bucket_id` = `bucket_id`. Appwrite bucket identifier. Evaluate the value as: the current `bucket_id` value. |
| L455 | Supply `job_queue` = `job_queue`.  Evaluate the value as: the current `job_queue` value. |
| L456 | Close the expression/container begun at L451; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L457 | Handle `Exception`; only a matching error from the associated try enters this body. |
| L458 | `session.rollback()` — Roll back the active transaction and discard its uncommitted database changes. The return value is not assigned here. |
| L459 | Re-raise the currently handled exception with its traceback; no replacement result is returned. |
| L460 | `session.commit()` — Flush pending changes and commit this transaction; subsequent failures cannot undo that completed transaction. The return value is not assigned here. |
| L461 | Compute the return value: `DocumentDeleteAccepted(project_id=project_id, document_id=document.id, job_id=delete_job.id)` — Construct `DocumentDeleteAccepted` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L462 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. Supply `document_id` = `document.id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the `id` attribute of `document`. Supply `job_id` = `delete_job.id`. Durable processing-job UUID. Evaluate the value as: the `id` attribute of `delete_job`. |
| L463 | Close the expression/container begun at L461; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `download_document_file(project_id, document_id, request: Request, principal, session, storage) -> Response`

- **Route/arguments:** `GET P/{document_id}/file`; scope UUIDs, HTTP request carrying optional Range, principal/session, storage adapter.
- **Returns:** Full PDF 200, byte-range 206, or empty 416 with `Content-Range: bytes */size`.
- **Work:** Verifies live ownership, resolves the bucket, reads request Range, and downloads through the adapter. Maps missing/unavailable storage to safe 503. Normalizes header names, builds inline disposition, and chooses 206 only if a content-range header exists. Adds content type/length and accept-ranges.
- **Transaction detail:** Unlike upload, the current function does not explicitly commit/end the ownership-read session before the storage call; the request dependency closes it afterward.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-download-document-file"></a>

#### Line-by-line execution

[Current source: lines 466–554](../../../../Backend/app/api/documents.py#L466-L554). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project_id` | `UUID`; required; positional or keyword | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID`; required; positional or keyword | Document UUID; filenames do not establish document identity. |
| `request` | `Request`; required; positional or keyword | FastAPI/Starlette request object providing headers and request context. |
| `principal` | `OnboardedPrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `session` | `SessionDep`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `storage` | `Annotated[object, Depends(get_storage_adapter)]`; required; positional or keyword | Storage collaborator for private file creation, inspection, ranged reads, or deletion. |

**Declared result:** `Response`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 466 | @router.get("/projects/{project_id}/documents/{document_id}/file")
 467 | def download_document_file(
 468 |     project_id: UUID,
 469 |     document_id: UUID,
 470 |     request: Request,
 471 |     principal: OnboardedPrincipalDep,
 472 |     session: SessionDep,
 473 |     storage: Annotated[object, Depends(get_storage_adapter)],
 474 | ) -> Response:
 475 |     """GET .../documents/{id}/file -> authorized inline PDF (Range support).
 476 | 
 477 |     Returns ``200`` full / ``206`` byte range,
 478 |     ``application/pdf``, inline disposition, ``Accept-Ranges``.
 479 |     Owner-only: the bucket is private and reads go through the
 480 |     server API key after the ``document -> project -> user`` check.
 481 |     """
 482 |     document = get_owned_document_or_404(
 483 |         session,
 484 |         user_id=principal.id,
 485 |         project_id=project_id,
 486 |         document_id=document_id,
 487 |     )
 488 |     try:
 489 |         bucket_id = default_bucket_id()
 490 |     except RuntimeError:
 491 |         raise_api_error(
 492 |             503,
 493 |             ErrorCode.SERVICE_UNAVAILABLE,
 494 |             "Storage is not configured.",
 495 |             project_id=project_id,
 496 |             document_id=document_id,
 497 |         )
 498 |         raise AssertionError("unreachable")  # pragma: no cover
 499 | 
 500 |     range_header = request.headers.get("Range")
 501 |     try:
 502 |         chunk, headers = storage.open_storage_range(  # type: ignore[attr-defined]
 503 |             bucket_id=bucket_id,
 504 |             file_id=document.appwrite_file_id,
 505 |             range_header=range_header,
 506 |         )
 507 |     except RangeNotSatisfiableError as exc:
 508 |         return Response(
 509 |             status_code=416,
 510 |             headers={
 511 |                 "Accept-Ranges": "bytes",
 512 |                 "Content-Range": f"bytes */{exc.size}",
 513 |                 "Content-Type": "application/pdf",
 514 |             },
 515 |         )
 516 |     except StorageNotFoundError:
 517 |         raise_api_error(
 518 |             503,
 519 |             ErrorCode.SERVICE_UNAVAILABLE,
 520 |             "Stored PDF is unavailable.",
 521 |             project_id=project_id,
 522 |             document_id=document_id,
 523 |         )
 524 |         raise AssertionError("unreachable")  # pragma: no cover
 525 |     except StorageUnavailableError:
 526 |         raise_api_error(
 527 |             503,
 528 |             ErrorCode.SERVICE_UNAVAILABLE,
 529 |             "Stored PDF is unavailable.",
 530 |             project_id=project_id,
 531 |             document_id=document_id,
 532 |         )
 533 |         raise AssertionError("unreachable")  # pragma: no cover
 534 | 
 535 |     disposition = _inline_disposition(document.file_name)
 536 |     # Adapter headers are lowercase-insensitive; normalize for clients.
 537 |     normalized = {str(k).lower(): str(v) for k, v in dict(headers).items()}
 538 |     content_type = normalized.get("content-type", "application/pdf")
 539 |     content_length = normalized.get("content-length", str(len(chunk)))
 540 |     content_range = normalized.get("content-range")
 541 |     response_headers: dict[str, str] = {
 542 |         "Content-Type": content_type,
 543 |         "Content-Disposition": disposition,
 544 |         "Accept-Ranges": "bytes",
 545 |         "Content-Length": content_length,
 546 |     }
 547 |     if content_range is not None:
 548 |         response_headers["Content-Range"] = content_range
 549 |         status_code = 206
 550 |     else:
 551 |         status_code = 200
 552 |     return Response(
 553 |         content=chunk, status_code=status_code, headers=response_headers
 554 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L466 | Register the handler with FastAPI using `router.get('/projects/{project_id}/documents/{document_id}/file')`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L467 | Define `download_document_file`; bind its arguments when called. The body executes only when invoked. |
| L468 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L469 | Declare parameter `document_id` with annotation `UUID`. Document UUID; filenames do not establish document identity. |
| L470 | Declare parameter `request` with annotation `Request`. FastAPI/Starlette request object providing headers and request context. |
| L471 | Declare parameter `principal` with annotation `OnboardedPrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L472 | Declare parameter `session` with annotation `SessionDep`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L473 | Declare parameter `storage` with annotation `Annotated[object, Depends(get_storage_adapter)]`. Storage collaborator for private file creation, inspection, ranged reads, or deletion. |
| L474 | Finish/continue the signature; the declared return annotation is `Response`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L475 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L477 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L478 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L479 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L480 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L481 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L482 | Evaluate the right-hand side, then bind/store it in `document`: `get_owned_document_or_404(session, user_id=principal.id, project_id=project_id, document_id=document_id)` — Call [get_owned_document_or_404](../repositories/projects.md#walk-get-owned-document-or-404) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L483 | Supply positional argument 1 to `get_owned_document_or_404`: the current `session` value. |
| L484 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. |
| L485 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L486 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L487 | Close the expression/container begun at L482; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L488 | Enter the protected block; failures are matched against `RuntimeError` in order. |
| L489 | Evaluate the right-hand side, then bind/store it in `bucket_id`: `default_bucket_id()` — Call [default_bucket_id](../services/storage.md#walk-default-bucket-id) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L490 | Handle `RuntimeError`; only a matching error from the associated try enters this body. |
| L491 | `raise_api_error(503, ErrorCode.SERVICE_UNAVAILABLE, 'Storage is not configured.', project_id=project_id, document_id=document_id)` — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L492 | Supply positional argument 1 to `raise_api_error`: `503`. |
| L493 | Supply positional argument 2 to `raise_api_error`: the `SERVICE_UNAVAILABLE` attribute of `ErrorCode`. |
| L494 | Supply positional argument 3 to `raise_api_error`: `'Storage is not configured.'`. |
| L495 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L496 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L497 | Close the expression/container begun at L491; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L498 | Raise `AssertionError('unreachable')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L500 | Evaluate the right-hand side, then bind/store it in `range_header`: `request.headers.get('Range')` — Look up `'Range'` in `request.headers`, using None when the key is absent (an existing null value is not replaced). |
| L501 | Enter the protected block; failures are matched against `RangeNotSatisfiableError`, `StorageNotFoundError`, `StorageUnavailableError` in order. |
| L502 | Evaluate the right-hand side, then bind/store it in `(chunk, headers)`: `storage.open_storage_range(bucket_id=bucket_id, file_id=document.appwrite_file_id, range_header=range_header)` — Read the selected private file range and its HTTP content headers through the storage adapter. |
| L503 | Supply `bucket_id` = `bucket_id`. Appwrite bucket identifier. Evaluate the value as: the current `bucket_id` value. |
| L504 | Supply `file_id` = `document.appwrite_file_id`. Reserved Appwrite storage-object identifier. Evaluate the value as: the `appwrite_file_id` attribute of `document`. |
| L505 | Supply `range_header` = `range_header`. Optional HTTP byte-range selector; parsing determines full, partial, or unsatisfiable behavior. Evaluate the value as: the current `range_header` value. |
| L506 | Close the expression/container begun at L502; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L507 | Handle `RangeNotSatisfiableError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L508 | Compute the return value: `Response(status_code=416, headers={'Accept-Ranges': 'bytes', 'Content-Range': f'bytes */{exc.size}', 'Content-Type': 'application/pdf'})` — Construct `Response` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L509 | Supply `status_code` = `416`.  Evaluate the value as: `416`. |
| L510 | Supply `headers` = `{'Accept-Ranges': 'bytes', 'Content-Range': f'bytes */{exc.size}', 'Content-Type': 'application/pdf'}`.  Evaluate the value as: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. |
| L511 | Add mapping entry `'Accept-Ranges'`: `'bytes'`. |
| L512 | Add mapping entry `'Content-Range'`: format a string by inserting `exc.size` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L513 | Add mapping entry `'Content-Type'`: `'application/pdf'`. |
| L514 | Close the expression/container begun at L510; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L515 | Close the expression/container begun at L508; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L516 | Handle `StorageNotFoundError`; only a matching error from the associated try enters this body. |
| L517 | `raise_api_error(503, ErrorCode.SERVICE_UNAVAILABLE, 'Stored PDF is unavailable.', project_id=project_id, document_id=document_id)` — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L518 | Supply positional argument 1 to `raise_api_error`: `503`. |
| L519 | Supply positional argument 2 to `raise_api_error`: the `SERVICE_UNAVAILABLE` attribute of `ErrorCode`. |
| L520 | Supply positional argument 3 to `raise_api_error`: `'Stored PDF is unavailable.'`. |
| L521 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L522 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L523 | Close the expression/container begun at L517; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L524 | Raise `AssertionError('unreachable')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L525 | Handle `StorageUnavailableError`; only a matching error from the associated try enters this body. |
| L526 | `raise_api_error(503, ErrorCode.SERVICE_UNAVAILABLE, 'Stored PDF is unavailable.', project_id=project_id, document_id=document_id)` — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L527 | Supply positional argument 1 to `raise_api_error`: `503`. |
| L528 | Supply positional argument 2 to `raise_api_error`: the `SERVICE_UNAVAILABLE` attribute of `ErrorCode`. |
| L529 | Supply positional argument 3 to `raise_api_error`: `'Stored PDF is unavailable.'`. |
| L530 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L531 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L532 | Close the expression/container begun at L526; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L533 | Raise `AssertionError('unreachable')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L535 | Evaluate the right-hand side, then bind/store it in `disposition`: `_inline_disposition(document.file_name)` — Call [_inline_disposition](#walk--inline-disposition) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L536 | Comment only: Adapter headers are lowercase-insensitive; normalize for clients.. It does not execute; the neighboring code determines behavior. |
| L537 | Evaluate the right-hand side, then bind/store it in `normalized`: iterate `dict(headers).items()`, binding each item to `(k, v)`; produce `str(k).lower()` → `str(v)` into a new mapping. |
| L538 | Evaluate the right-hand side, then bind/store it in `content_type`: `normalized.get('content-type', 'application/pdf')` — Look up `'content-type'` in `normalized`, using `'application/pdf'` when the key is absent (an existing null value is not replaced). |
| L539 | Evaluate the right-hand side, then bind/store it in `content_length`: `normalized.get('content-length', str(len(chunk)))` — Look up `'content-length'` in `normalized`, using `str(len(chunk))` when the key is absent (an existing null value is not replaced); inputs include `str(len(chunk))` — Convert the input to its string representation. |
| L540 | Evaluate the right-hand side, then bind/store it in `content_range`: `normalized.get('content-range')` — Look up `'content-range'` in `normalized`, using None when the key is absent (an existing null value is not replaced). |
| L541 | Evaluate the right-hand side, then bind/store it in `response_headers`: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. |
| L542 | Add mapping entry `'Content-Type'`: the current `content_type` value. |
| L543 | Add mapping entry `'Content-Disposition'`: the current `disposition` value. |
| L544 | Add mapping entry `'Accept-Ranges'`: `'bytes'`. |
| L545 | Add mapping entry `'Content-Length'`: the current `content_length` value. |
| L546 | Close the expression/container begun at L541; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L547 | Evaluate the branch condition: compare whether `content_range` is not the same object as `None`. If truthy, enter L548; otherwise enter the alternative at L551. |
| L548 | Evaluate the right-hand side, then bind/store it in `response_headers['Content-Range']`: the current `content_range` value. |
| L549 | Evaluate the right-hand side, then bind/store it in `status_code`: `206`. |
| L550 | Enter this alternative only when the associated condition was false (or the associated try/loop completed without its exceptional exit). |
| L551 | Evaluate the right-hand side, then bind/store it in `status_code`: `200`. |
| L552 | Compute the return value: `Response(content=chunk, status_code=status_code, headers=response_headers)` — Construct `Response` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L553 | Supply `content` = `chunk`. Message text supplied for a persisted conversation turn. Evaluate the value as: the current `chunk` value. Supply `status_code` = `status_code`.  Evaluate the value as: the current `status_code` value. Supply `headers` = `response_headers`.  Evaluate the value as: the current `response_headers` value. |
| L554 | Close the expression/container begun at L552; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `retry_document(project_id, document_id, principal, session, job_queue) -> UploadAcceptance`

**Route:** `POST P/{document_id}/retry` (202). **Arguments:** Scope UUIDs, principal/session, queue. **Returns:** Document and fresh queued-job DTOs. **Work:** Loads owned live document, rejects any active process job first (409 `processing_in_progress` with job ID), then rejects a non-`Failed` document (409 `invalid_state`). Requires bucket config, calls `prepare_document_retry` to advance epoch/reset/enqueue, rolls back errors, commits success. It reuses stored bytes rather than uploading again.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-retry-document"></a>

#### Line-by-line execution

[Current source: lines 557–631](../../../../Backend/app/api/documents.py#L557-L631). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project_id` | `UUID`; required; positional or keyword | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID`; required; positional or keyword | Document UUID; filenames do not establish document identity. |
| `principal` | `OnboardedPrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `session` | `SessionDep`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `job_queue` | `Annotated[DirectJobQueue, Depends(get_job_queue)]`; required; positional or keyword | Caller-supplied job queue; each read, transformation, and validation is traced below. |

**Declared result:** `UploadAcceptance`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 557 | @router.post(
 558 |     "/projects/{project_id}/documents/{document_id}/retry",
 559 |     response_model=UploadAcceptance,
 560 |     status_code=202,
 561 | )
 562 | def retry_document(
 563 |     project_id: UUID,
 564 |     document_id: UUID,
 565 |     principal: OnboardedPrincipalDep,
 566 |     session: SessionDep,
 567 |     job_queue: Annotated[DirectJobQueue, Depends(get_job_queue)],
 568 | ) -> UploadAcceptance:
 569 |     """POST .../documents/{id}/retry -> 202 with a new queued job.
 570 | 
 571 |     Eligible only when the document is ``Failed`` and no nonterminal
 572 |     job exists; otherwise ``409 invalid_state`` /
 573 |     ``409 processing_in_progress``.  The failed job stays terminal;
 574 |     ``processing_epoch`` advances (see :func:`prepare_document_retry`).
 575 |     """
 576 |     document = get_owned_document_or_404(
 577 |         session,
 578 |         user_id=principal.id,
 579 |         project_id=project_id,
 580 |         document_id=document_id,
 581 |     )
 582 |     active = nonterminal_process_job(session, target_document_id=document.id)
 583 |     if active is not None:
 584 |         session.rollback()
 585 |         raise_api_error(
 586 |             409,
 587 |             ErrorCode.PROCESSING_IN_PROGRESS,
 588 |             "Document processing is still in progress.",
 589 |             project_id=project_id,
 590 |             document_id=document_id,
 591 |             job_id=active.id,
 592 |         )
 593 |         raise AssertionError("unreachable")  # pragma: no cover
 594 |     if document.status != "Failed":
 595 |         session.rollback()
 596 |         raise_api_error(
 597 |             409,
 598 |             ErrorCode.INVALID_STATE,
 599 |             "Only failed documents can be retried.",
 600 |             project_id=project_id,
 601 |             document_id=document_id,
 602 |         )
 603 |         raise AssertionError("unreachable")  # pragma: no cover
 604 | 
 605 |     try:
 606 |         bucket_id = default_bucket_id()
 607 |     except RuntimeError:
 608 |         session.rollback()
 609 |         raise_api_error(
 610 |             503,
 611 |             ErrorCode.SERVICE_UNAVAILABLE,
 612 |             "Storage is not configured.",
 613 |             project_id=project_id,
 614 |             document_id=document_id,
 615 |         )
 616 |         raise AssertionError("unreachable")  # pragma: no cover
 617 | 
 618 |     try:
 619 |         document, job = prepare_document_retry(
 620 |             session,
 621 |             document=document,
 622 |             bucket_id=bucket_id,
 623 |             job_queue=job_queue,
 624 |         )
 625 |     except Exception:
 626 |         session.rollback()
 627 |         raise
 628 |     session.commit()
 629 |     return UploadAcceptance(
 630 |         document=document_to_dto(document), job=job_to_dto(job)
 631 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L557 | Register the handler with FastAPI using `router.post('/projects/{project_id}/documents/{document_id}/retry', response_model=UploadAcceptance, status_code=202)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L558 | Register the handler with FastAPI using `router.post('/projects/{project_id}/documents/{document_id}/retry', response_model=UploadAcceptance, status_code=202)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L559 | Register the handler with FastAPI using `router.post('/projects/{project_id}/documents/{document_id}/retry', response_model=UploadAcceptance, status_code=202)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L560 | Register the handler with FastAPI using `router.post('/projects/{project_id}/documents/{document_id}/retry', response_model=UploadAcceptance, status_code=202)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L561 | Register the handler with FastAPI using `router.post('/projects/{project_id}/documents/{document_id}/retry', response_model=UploadAcceptance, status_code=202)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L562 | Define `retry_document`; bind its arguments when called. The body executes only when invoked. |
| L563 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L564 | Declare parameter `document_id` with annotation `UUID`. Document UUID; filenames do not establish document identity. |
| L565 | Declare parameter `principal` with annotation `OnboardedPrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L566 | Declare parameter `session` with annotation `SessionDep`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L567 | Declare parameter `job_queue` with annotation `Annotated[DirectJobQueue, Depends(get_job_queue)]`. Caller-supplied job queue; its uses and transformations are traced below. |
| L568 | Finish/continue the signature; the declared return annotation is `UploadAcceptance`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L569 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L571 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L572 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L573 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L574 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L575 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L576 | Evaluate the right-hand side, then bind/store it in `document`: `get_owned_document_or_404(session, user_id=principal.id, project_id=project_id, document_id=document_id)` — Call [get_owned_document_or_404](../repositories/projects.md#walk-get-owned-document-or-404) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L577 | Supply positional argument 1 to `get_owned_document_or_404`: the current `session` value. |
| L578 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. |
| L579 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L580 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L581 | Close the expression/container begun at L576; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L582 | Evaluate the right-hand side, then bind/store it in `active`: `nonterminal_process_job(session, target_document_id=document.id)` — Call [nonterminal_process_job](../repositories/documents.md#walk-nonterminal-process-job) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L583 | Evaluate the branch condition: compare whether `active` is not the same object as `None`. If truthy, enter L584; otherwise skip this indented block and continue after it. |
| L584 | `session.rollback()` — Roll back the active transaction and discard its uncommitted database changes. The return value is not assigned here. |
| L585 | `raise_api_error` with the arguments detailed below — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L586 | Supply positional argument 1 to `raise_api_error`: `409`. |
| L587 | Supply positional argument 2 to `raise_api_error`: the `PROCESSING_IN_PROGRESS` attribute of `ErrorCode`. |
| L588 | Supply positional argument 3 to `raise_api_error`: `'Document processing is still in progress.'`. |
| L589 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L590 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L591 | Supply `job_id` = `active.id`. Durable processing-job UUID. Evaluate the value as: the `id` attribute of `active`. |
| L592 | Close the expression/container begun at L585; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L593 | Raise `AssertionError('unreachable')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L594 | Evaluate the branch condition: compare whether `document.status` differs from `'Failed'`. If truthy, enter L595; otherwise skip this indented block and continue after it. |
| L595 | `session.rollback()` — Roll back the active transaction and discard its uncommitted database changes. The return value is not assigned here. |
| L596 | `raise_api_error(409, ErrorCode.INVALID_STATE, 'Only failed documents can be retried.', project_id=project_id, document_id=document_id)` — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L597 | Supply positional argument 1 to `raise_api_error`: `409`. |
| L598 | Supply positional argument 2 to `raise_api_error`: the `INVALID_STATE` attribute of `ErrorCode`. |
| L599 | Supply positional argument 3 to `raise_api_error`: `'Only failed documents can be retried.'`. |
| L600 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L601 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L602 | Close the expression/container begun at L596; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L603 | Raise `AssertionError('unreachable')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L605 | Enter the protected block; failures are matched against `RuntimeError` in order. |
| L606 | Evaluate the right-hand side, then bind/store it in `bucket_id`: `default_bucket_id()` — Call [default_bucket_id](../services/storage.md#walk-default-bucket-id) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L607 | Handle `RuntimeError`; only a matching error from the associated try enters this body. |
| L608 | `session.rollback()` — Roll back the active transaction and discard its uncommitted database changes. The return value is not assigned here. |
| L609 | `raise_api_error(503, ErrorCode.SERVICE_UNAVAILABLE, 'Storage is not configured.', project_id=project_id, document_id=document_id)` — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L610 | Supply positional argument 1 to `raise_api_error`: `503`. |
| L611 | Supply positional argument 2 to `raise_api_error`: the `SERVICE_UNAVAILABLE` attribute of `ErrorCode`. |
| L612 | Supply positional argument 3 to `raise_api_error`: `'Storage is not configured.'`. |
| L613 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L614 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L615 | Close the expression/container begun at L609; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L616 | Raise `AssertionError('unreachable')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L618 | Enter the protected block; failures are matched against `Exception` in order. |
| L619 | Evaluate the right-hand side, then bind/store it in `(document, job)`: `prepare_document_retry(session, document=document, bucket_id=bucket_id, job_queue=job_queue)` — Call [prepare_document_retry](../repositories/documents.md#walk-prepare-document-retry) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L620 | Supply positional argument 1 to `prepare_document_retry`: the current `session` value. |
| L621 | Supply `document` = `document`.  Evaluate the value as: the current `document` value. |
| L622 | Supply `bucket_id` = `bucket_id`. Appwrite bucket identifier. Evaluate the value as: the current `bucket_id` value. |
| L623 | Supply `job_queue` = `job_queue`.  Evaluate the value as: the current `job_queue` value. |
| L624 | Close the expression/container begun at L619; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L625 | Handle `Exception`; only a matching error from the associated try enters this body. |
| L626 | `session.rollback()` — Roll back the active transaction and discard its uncommitted database changes. The return value is not assigned here. |
| L627 | Re-raise the currently handled exception with its traceback; no replacement result is returned. |
| L628 | `session.commit()` — Flush pending changes and commit this transaction; subsequent failures cannot undo that completed transaction. The return value is not assigned here. |
| L629 | Compute the return value: `UploadAcceptance(document=document_to_dto(document), job=job_to_dto(job))` — Construct `UploadAcceptance` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L630 | Supply `document` = `document_to_dto(document)`.  Evaluate the value as: `document_to_dto(document)` — Call [document_to_dto](../repositories/documents.md#walk-document-to-dto) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Supply `job` = `job_to_dto(job)`.  Evaluate the value as: `job_to_dto(job)` — Call [job_to_dto](../repositories/documents.md#walk-job-to-dto) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L631 | Close the expression/container begun at L629; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `read_job(job_id: UUID, principal, session) -> ProcessingJobDto`

**Route:** `GET /jobs/{job_id}` (200). **Arguments:** Job UUID, principal/session. **Returns:** Public job state. **Work:** Matches immutable owner snapshot with `get_owned_job_or_404`; job status remains readable after project/document removal, without exposing resource snapshots or lease credentials.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-read-job"></a>

#### Line-by-line execution

[Current source: lines 639–647](../../../../Backend/app/api/documents.py#L639-L647). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `job_id` | `UUID`; required; positional or keyword | Durable processing-job UUID. |
| `principal` | `OnboardedPrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `session` | `SessionDep`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |

**Declared result:** `ProcessingJobDto`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 639 | @router.get("/jobs/{job_id}", response_model=ProcessingJobDto)
 640 | def read_job(
 641 |     job_id: UUID,
 642 |     principal: OnboardedPrincipalDep,
 643 |     session: SessionDep,
 644 | ) -> ProcessingJobDto:
 645 |     """GET /jobs/{jobId} -> owner-scoped status incl. tombstones."""
 646 |     job = get_owned_job_or_404(session, user_id=principal.id, job_id=job_id)
 647 |     return job_to_dto(job)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L639 | Register the handler with FastAPI using `router.get('/jobs/{job_id}', response_model=ProcessingJobDto)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L640 | Define `read_job`; bind its arguments when called. The body executes only when invoked. |
| L641 | Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. |
| L642 | Declare parameter `principal` with annotation `OnboardedPrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L643 | Declare parameter `session` with annotation `SessionDep`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L644 | Finish/continue the signature; the declared return annotation is `ProcessingJobDto`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L645 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L646 | Evaluate the right-hand side, then bind/store it in `job`: `get_owned_job_or_404(session, user_id=principal.id, job_id=job_id)` — Call [get_owned_job_or_404](../repositories/projects.md#walk-get-owned-job-or-404) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L647 | Compute the return value: `job_to_dto(job)` — Call [job_to_dto](../repositories/documents.md#walk-job-to-dto) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_inline_disposition(filename: str) -> str`

**Arguments:** Display filename. **Returns:** Inline Content-Disposition value. **Work:** Builds a stripped ASCII fallback (or `document.pdf`), escapes backslashes/quotes, and if ASCII conversion changed the name, appends an RFC 5987 `filename*=UTF-8''...` encoding of the original.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--inline-disposition"></a>

#### Line-by-line execution

[Current source: lines 650–657](../../../../Backend/app/api/documents.py#L650-L657). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `filename` | `str`; required; positional or keyword | Display filename/citation hint, not proof of ownership or document identity. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 650 | def _inline_disposition(filename: str) -> str:
 651 |     """``inline; filename="..."`` with RFC 5987 fallback for unicode."""
 652 |     ascii_name = filename.encode("ascii", "ignore").decode("ascii").strip() or "document.pdf"
 653 |     escaped = ascii_name.replace("\\", "\\\\").replace('"', '\\"')
 654 |     if ascii_name != filename:
 655 |         encoded = _rfc5987_encode(filename)
 656 |         return f"inline; filename=\"{escaped}\"; filename*=UTF-8''{encoded}"
 657 |     return f'inline; filename="{escaped}"'
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L650 | Define `_inline_disposition`; bind its arguments when called. The body executes only when invoked. |
| L651 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L652 | Evaluate the right-hand side, then bind/store it in `ascii_name`: evaluate `filename.encode('ascii', 'ignore').decode('ascii').strip() or 'document.pdf'` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L653 | Evaluate the right-hand side, then bind/store it in `escaped`: `ascii_name.replace('\\', '\\\\').replace('"', '\\"')` — Return a value with the specified replacements applied; first obtain the receiver: `ascii_name.replace('\\', '\\\\')` — Return a value with the specified replacements applied. |
| L654 | Evaluate the branch condition: compare whether `ascii_name` differs from `filename`. If truthy, enter L655; otherwise skip this indented block and continue after it. |
| L655 | Evaluate the right-hand side, then bind/store it in `encoded`: `_rfc5987_encode(filename)` — Call [_rfc5987_encode](#walk--rfc5987-encode) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L656 | Compute the return value: format a string by inserting `escaped`, `encoded` into the literal text; !r uses repr, and this formatting does not escape or redact values. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L657 | Compute the return value: format a string by inserting `escaped` into the literal text; !r uses repr, and this formatting does not escape or redact values. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_rfc5987_encode(value: str) -> str`

**Arguments:** Unicode filename. **Returns:** Percent-encoded string. **Work:** Calls `urllib.parse.quote(value, safe="")` so non-unreserved characters, including path separators, are escaped.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--rfc5987-encode"></a>

#### Line-by-line execution

[Current source: lines 660–663](../../../../Backend/app/api/documents.py#L660-L663). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `value` | `str`; required; positional or keyword | Input value being normalized, validated, or compared by this helper. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 660 | def _rfc5987_encode(value: str) -> str:
 661 |     from urllib.parse import quote
 662 | 
 663 |     return quote(value, safe="")
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L660 | Define `_rfc5987_encode`; bind its arguments when called. The body executes only when invoked. |
| L661 | Import `quote` from `urllib.parse`; inside a function this import is deferred until this path is reached. |
| L663 | Compute the return value: `quote(value, safe='')` — Percent-encode the supplied string for a URL/header parameter using the specified safe-character set. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
