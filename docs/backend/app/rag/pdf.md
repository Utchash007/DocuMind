# `app/rag/pdf.py`

[Source](../../../../Backend/app/rag/pdf.py) · [Backend index](../../README.md)

Blocking pypdf extraction shared by upload preflight and the durable worker. Defaults are 25 MiB, 200 pages, and an approximately 800-character chunk target. Each chunk stays on one PDF page. Preflight labels are temporary; published chunks carry document/version identity.

## Error types

`PdfError` has `code="pdf_malformed"` and `retryable=False`. Subclasses inherit its constructor and retry policy: `PdfMalformedError` (`pdf_malformed`), `PdfTextlessError` (`pdf_textless`), `PdfPageLimitError` (`page_limit_exceeded`), and `PdfFileTooLargeError` (`file_too_large`).

## Functions

### `PdfError.__init__(self, message: str, *, pages_extracted: int = 0) -> None`

**Arguments:** Diagnostic text and count of successfully extracted pages before failure. **Returns:** `None`. **Work:** Initializes `Exception`, stores `.message` and `.pages_extracted`. The counter is explicitly supplied on mid-document extraction failure; other errors retain zero.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-pdferror---init--"></a>

#### Line-by-line execution

[Current source: lines 36–39](../../../../Backend/app/rag/pdf.py#L36-L39). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `message` | `str`; required; positional or keyword | Caller-supplied message; each read, transformation, and validation is traced below. |
| `pages_extracted` | `int`; default `0`; keyword-only | Caller-supplied pages extracted; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  36 |     def __init__(self, message: str, *, pages_extracted: int = 0) -> None:
  37 |         super().__init__(message)
  38 |         self.message = message
  39 |         self.pages_extracted = pages_extracted
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L36 | Define `PdfError.__init__`; bind its arguments when called. The body executes only when invoked. |
| L37 | `super().__init__(message)` — Initialize the base exception/object with the supplied arguments; first obtain the receiver: `super()` — Resolve the superclass proxy for the current method and instance. The return value is not assigned here. |
| L38 | Evaluate the right-hand side, then bind/store it in `self.message`: the current `message` value. |
| L39 | Evaluate the right-hand side, then bind/store it in `self.pages_extracted`: the current `pages_extracted` value. |

<!-- END LINE WALKTHROUGH -->

### `chunk_id_for(document_id, index_version, page_number: int, sub_index: int) -> str`

**Arguments:** UUID/string document and version, each nullable; one-based page; zero-based within-page chunk index. **Returns:** `{document}:{version}:p{page}:c{sub}` when both identities exist, otherwise `preflight:p{page}:c{sub}` when both are absent. **Work:** Formats the deterministic label and rejects exactly one missing identity with `ValueError`. It does not independently validate UUID syntax or number ranges.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-chunk-id-for"></a>

#### Line-by-line execution

[Current source: lines 66–83](../../../../Backend/app/rag/pdf.py#L66-L83). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `document_id` | `UUID \| str \| None`; required; positional or keyword | Document UUID; filenames do not establish document identity. |
| `index_version` | `UUID \| str \| None`; required; positional or keyword | UUID of one document's vector-index namespace, separate from its active publication pointer. |
| `page_number` | `int`; required; positional or keyword | Caller-supplied page number; each read, transformation, and validation is traced below. |
| `sub_index` | `int`; required; positional or keyword | Caller-supplied sub index; each read, transformation, and validation is traced below. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  66 | def chunk_id_for(
  67 |     document_id: UUID | str | None,
  68 |     index_version: UUID | str | None,
  69 |     page_number: int,
  70 |     sub_index: int,
  71 | ) -> str:
  72 |     """Deterministic chunk ID: document/version/page/chunk.
  73 | 
  74 |     With a document and version: ``{doc}:{version}:p{page}:c{sub}``.  An
  75 |     expired worker can only ever write into its obsolete
  76 |     ``index_version`` namespace, and re-running the same attempt
  77 |     regenerates the same IDs (idempotent upserts).
  78 |     """
  79 |     if document_id is not None and index_version is not None:
  80 |         return f"{document_id}:{index_version}:p{page_number}:c{sub_index}"
  81 |     if document_id is not None or index_version is not None:
  82 |         raise ValueError("document_id and index_version must be supplied together")
  83 |     return f"preflight:p{page_number}:c{sub_index}"
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L66 | Define `chunk_id_for`; bind its arguments when called. The body executes only when invoked. |
| L67 | Declare parameter `document_id` with annotation `UUID \| str \| None`. Document UUID; filenames do not establish document identity. |
| L68 | Declare parameter `index_version` with annotation `UUID \| str \| None`. UUID of one document's vector-index namespace, separate from its active publication pointer. |
| L69 | Declare parameter `page_number` with annotation `int`. Caller-supplied page number; its uses and transformations are traced below. |
| L70 | Declare parameter `sub_index` with annotation `int`. Caller-supplied sub index; its uses and transformations are traced below. |
| L71 | Finish/continue the signature; the declared return annotation is `str`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L72 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L74 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L75 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L76 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L77 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L78 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L79 | Evaluate the branch condition: evaluate `document_id is not None and index_version is not None` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L80; otherwise skip this indented block and continue after it. |
| L80 | Compute the return value: format a string by inserting `document_id`, `index_version`, `page_number`, `sub_index` into the literal text; !r uses repr, and this formatting does not escape or redact values. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L81 | Evaluate the branch condition: evaluate `document_id is not None or index_version is not None` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L82; otherwise skip this indented block and continue after it. |
| L82 | Raise `ValueError('document_id and index_version must be supplied together')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L83 | Compute the return value: format a string by inserting `page_number`, `sub_index` into the literal text; !r uses repr, and this formatting does not escape or redact values. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `chunk_page_text(text: str, *, page_number: int, file_name: str, document_id, index_version, target_chars=800) -> list[PdfChunk]`

- **Arguments:** One page's text, page number, display filename, optional paired identities, target length.
- **Returns:** Ordered page-bound `PdfChunk` objects, or `[]` for whitespace-only input.
- **Work:** Collapses all whitespace to single spaces, splits sentences with `split_into_sentences`, and appends whole sentences until their summed character lengths reach/exceed the target. Emits a chunk using `chunk_id_for`, resets its accumulator, and emits any remaining sentences at page end. Sub-index starts at zero per page. Joining spaces are not counted toward the accumulator, and a long sentence is not split; the target is not a hard maximum. `PdfChunk` validates its page and string fields.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-chunk-page-text"></a>

#### Line-by-line execution

[Current source: lines 86–136](../../../../Backend/app/rag/pdf.py#L86-L136). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `text` | `str`; required; positional or keyword | Text to split, hash, normalize, or embed as shown by this function's body. |
| `page_number` | `int`; required; keyword-only | Caller-supplied page number; each read, transformation, and validation is traced below. |
| `file_name` | `str`; required; keyword-only | Display PDF filename; immutable IDs establish ownership and evidence identity. |
| `document_id` | `UUID \| str \| None`; required; keyword-only | Document UUID; filenames do not establish document identity. |
| `index_version` | `UUID \| str \| None`; required; keyword-only | UUID of one document's vector-index namespace, separate from its active publication pointer. |
| `target_chars` | `int`; default `MAX_CHUNK_TARGET`; keyword-only | Caller-supplied target chars; each read, transformation, and validation is traced below. |

**Declared result:** `list[PdfChunk]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  86 | def chunk_page_text(
  87 |     text: str,
  88 |     *,
  89 |     page_number: int,
  90 |     file_name: str,
  91 |     document_id: UUID | str | None,
  92 |     index_version: UUID | str | None,
  93 |     target_chars: int = MAX_CHUNK_TARGET,
  94 | ) -> list[PdfChunk]:
  95 |     """Group one page's sentences into ~``target_chars`` chunks.
  96 | 
  97 |     Append sentences until the running length reaches the target, then
  98 |     flush; flush leftovers at the end of the page.  Chunks never span
  99 |     pages because this function only ever sees one page of text.
 100 |     """
 101 |     cleaned = re.sub(r"\s+", " ", text).strip()
 102 |     if not cleaned:
 103 |         return []
 104 |     chunks: list[PdfChunk] = []
 105 |     current: list[str] = []
 106 |     current_len = 0
 107 |     sub_index = 0
 108 |     for sentence in split_into_sentences(cleaned):
 109 |         current.append(sentence)
 110 |         current_len += len(sentence)
 111 |         if current_len >= target_chars:
 112 |             chunks.append(
 113 |                 PdfChunk(
 114 |                     chunk_id=chunk_id_for(
 115 |                         document_id, index_version, page_number, sub_index
 116 |                     ),
 117 |                     text=" ".join(current),
 118 |                     page_number=page_number,
 119 |                     source=file_name,
 120 |                 )
 121 |             )
 122 |             current = []
 123 |             current_len = 0
 124 |             sub_index += 1
 125 |     if current:
 126 |         chunks.append(
 127 |             PdfChunk(
 128 |                 chunk_id=chunk_id_for(
 129 |                     document_id, index_version, page_number, sub_index
 130 |                 ),
 131 |                 text=" ".join(current),
 132 |                 page_number=page_number,
 133 |                 source=file_name,
 134 |             )
 135 |         )
 136 |     return chunks
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L86 | Define `chunk_page_text`; bind its arguments when called. The body executes only when invoked. |
| L87 | Declare parameter `text` with annotation `str`. Text to split, hash, normalize, or embed as shown by this function's body. |
| L88 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L89 | Declare parameter `page_number` with annotation `int`. Caller-supplied page number; its uses and transformations are traced below. |
| L90 | Declare parameter `file_name` with annotation `str`. Display PDF filename; immutable IDs establish ownership and evidence identity. |
| L91 | Declare parameter `document_id` with annotation `UUID \| str \| None`. Document UUID; filenames do not establish document identity. |
| L92 | Declare parameter `index_version` with annotation `UUID \| str \| None`. UUID of one document's vector-index namespace, separate from its active publication pointer. |
| L93 | Declare parameter `target_chars` with annotation `int`. Caller-supplied target chars; its uses and transformations are traced below. |
| L94 | Finish/continue the signature; the declared return annotation is `list[PdfChunk]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L95 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L97 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L98 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L99 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L100 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L101 | Evaluate the right-hand side, then bind/store it in `cleaned`: `re.sub('\\s+', ' ', text).strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed; first obtain the receiver: `re.sub('\\s+', ' ', text)` — Invoke `re.sub` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L102 | Evaluate the branch condition: invert the truthiness of `cleaned`. If truthy, enter L103; otherwise skip this indented block and continue after it. |
| L103 | Compute the return value: build a list containing no items. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L104 | Evaluate the right-hand side, then bind/store it in `chunks`: build a list containing no items. |
| L105 | Evaluate the right-hand side, then bind/store it in `current`: build a list containing no items. |
| L106 | Evaluate the right-hand side, then bind/store it in `current_len`: `0`. |
| L107 | Evaluate the right-hand side, then bind/store it in `sub_index`: `0`. |
| L108 | Iterate `split_into_sentences(cleaned)` (`split_into_sentences(cleaned)` — Call [split_into_sentences](text.md#walk-split-into-sentences) with the shown arguments; the linked walkthrough explains its validation, work, and return value), assigning each item to `sentence`. Execute the indented body once per item; an empty iterable skips it. |
| L109 | `current.append(sentence)` — Append one object to the mutable list in place. The return value is not assigned here. |
| L110 | Update `current_len` in place using `len(sentence)` and the Add operation; the previous target value participates in the calculation. |
| L111 | Evaluate the branch condition: compare whether `current_len` is at least `target_chars`. If truthy, enter L112; otherwise skip this indented block and continue after it. |
| L112 | `chunks.append` with the arguments detailed below — Append one object to the mutable list in place; inputs include `PdfChunk(chunk_id=chunk_id_for(document_id, index_version, page_number, sub_index), text=' '.join(current), page_number=page_number, source=file_name)` — Construct `PdfChunk` with the shown fields; its class/model initialization rules apply. The return value is not assigned here. |
| L113 | `PdfChunk(chunk_id=chunk_id_for(document_id, index_version, page_number, sub_index), text=' '.join(current), page_number=page_number, source=file_name)` — Construct `PdfChunk` with the shown fields; its class/model initialization rules apply. |
| L114 | Supply `chunk_id` = `chunk_id_for(document_id, index_version, page_number, sub_index)`.  Evaluate the value as: `chunk_id_for(document_id, index_version, page_number, sub_index)` — Call [chunk_id_for](#walk-chunk-id-for) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L115 | Supply positional argument 1 to `chunk_id_for`: the current `document_id` value. |
| L116 | Close the expression/container begun at L114; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L117 | Supply `text` = `' '.join(current)`. Text to split, hash, normalize, or embed as shown by this function's body. Evaluate the value as: `' '.join(current)` — Join the supplied string items using `' '` between adjacent items. |
| L118 | Supply `page_number` = `page_number`.  Evaluate the value as: the current `page_number` value. |
| L119 | Supply `source` = `file_name`.  Evaluate the value as: the current `file_name` value. |
| L120 | Close the expression/container begun at L113; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L121 | Close the expression/container begun at L112; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L122 | Evaluate the right-hand side, then bind/store it in `current`: build a list containing no items. |
| L123 | Evaluate the right-hand side, then bind/store it in `current_len`: `0`. |
| L124 | Update `sub_index` in place using `1` and the Add operation; the previous target value participates in the calculation. |
| L125 | Evaluate the branch condition: the current `current` value. If truthy, enter L126; otherwise skip this indented block and continue after it. |
| L126 | `chunks.append` with the arguments detailed below — Append one object to the mutable list in place; inputs include `PdfChunk(chunk_id=chunk_id_for(document_id, index_version, page_number, sub_index), text=' '.join(current), page_number=page_number, source=file_name)` — Construct `PdfChunk` with the shown fields; its class/model initialization rules apply. The return value is not assigned here. |
| L127 | `PdfChunk(chunk_id=chunk_id_for(document_id, index_version, page_number, sub_index), text=' '.join(current), page_number=page_number, source=file_name)` — Construct `PdfChunk` with the shown fields; its class/model initialization rules apply. |
| L128 | Supply `chunk_id` = `chunk_id_for(document_id, index_version, page_number, sub_index)`.  Evaluate the value as: `chunk_id_for(document_id, index_version, page_number, sub_index)` — Call [chunk_id_for](#walk-chunk-id-for) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L129 | Supply positional argument 1 to `chunk_id_for`: the current `document_id` value. |
| L130 | Close the expression/container begun at L128; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L131 | Supply `text` = `' '.join(current)`. Text to split, hash, normalize, or embed as shown by this function's body. Evaluate the value as: `' '.join(current)` — Join the supplied string items using `' '` between adjacent items. |
| L132 | Supply `page_number` = `page_number`.  Evaluate the value as: the current `page_number` value. |
| L133 | Supply `source` = `file_name`.  Evaluate the value as: the current `file_name` value. |
| L134 | Close the expression/container begun at L127; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L135 | Close the expression/container begun at L126; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L136 | Compute the return value: the current `chunks` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `extract_pdf_chunks(pdf_path: Path, *, file_name: str, document_id=None, index_version=None, max_pages=200, max_file_bytes=26214400, target_chars=800) -> list[PdfChunk]`

- **Arguments:** Local PDF path, display filename, paired optional identities, page/byte budgets, chunk target.
- **Returns:** All extracted chunks in page order only after the entire document succeeds.
- **Work:** Stats the file, rejects excessive/zero byte length, constructs `pypdf.PdfReader`, materializes its pages, and enforces page count. For each page, calls `extract_text()`, treats `None` as empty text, increments the successful-page counter, and extends the result with `chunk_page_text`. Textless individual pages are allowed if some page yields text. No chunks after complete parsing raises `PdfTextlessError`; no OCR is attempted.
- **Errors:** File-stat/open/initial parse problems become `PdfMalformedError`; page extraction exceptions include the failing page and completed-page count. Size/page overflow uses the dedicated error classes. Partial accumulated chunks are never returned. Chunk-model/identity validation errors propagate. This function reads but does not create/delete the input file or write an index.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-extract-pdf-chunks"></a>

#### Line-by-line execution

[Current source: lines 139–203](../../../../Backend/app/rag/pdf.py#L139-L203). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `pdf_path` | `Path`; required; positional or keyword | Caller-supplied pdf path; each read, transformation, and validation is traced below. |
| `file_name` | `str`; required; keyword-only | Display PDF filename; immutable IDs establish ownership and evidence identity. |
| `document_id` | `UUID \| str \| None`; default `None`; keyword-only | Document UUID; filenames do not establish document identity. |
| `index_version` | `UUID \| str \| None`; default `None`; keyword-only | UUID of one document's vector-index namespace, separate from its active publication pointer. |
| `max_pages` | `int`; default `DEFAULT_MAX_PDF_PAGES`; keyword-only | Maximum PDF pages accepted by extraction. |
| `max_file_bytes` | `int`; default `DEFAULT_MAX_PDF_BYTES`; keyword-only | Maximum PDF byte count accepted by this component. |
| `target_chars` | `int`; default `MAX_CHUNK_TARGET`; keyword-only | Caller-supplied target chars; each read, transformation, and validation is traced below. |

**Declared result:** `list[PdfChunk]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 139 | def extract_pdf_chunks(
 140 |     pdf_path: Path,
 141 |     *,
 142 |     file_name: str,
 143 |     document_id: UUID | str | None = None,
 144 |     index_version: UUID | str | None = None,
 145 |     max_pages: int = DEFAULT_MAX_PDF_PAGES,
 146 |     max_file_bytes: int = DEFAULT_MAX_PDF_BYTES,
 147 |     target_chars: int = MAX_CHUNK_TARGET,
 148 | ) -> list[PdfChunk]:
 149 |     """Extract page-bound chunks from ``pdf_path`` (blocking, sync).
 150 | 
 151 |     Raises :class:`PdfMalformedError` (unparseable or partially parsed),
 152 |     :class:`PdfTextlessError` (no text at all),
 153 |     :class:`PdfPageLimitError`, or :class:`PdfFileTooLargeError` -- all
 154 |     terminal job failures.  Never returns a partial extraction.
 155 |     """
 156 |     path = Path(pdf_path)
 157 |     try:
 158 |         size = path.stat().st_size
 159 |     except OSError as exc:
 160 |         raise PdfMalformedError(f"PDF is not readable: {exc}") from exc
 161 |     if size > max_file_bytes:
 162 |         raise PdfFileTooLargeError(
 163 |             f"PDF is {size} bytes, exceeding the {max_file_bytes}-byte limit"
 164 |         )
 165 |     if size == 0:
 166 |         raise PdfMalformedError("PDF file is empty")
 167 |     try:
 168 |         reader = pypdf.PdfReader(str(path))
 169 |         pages = list(reader.pages)
 170 |     except Exception as exc:  # pypdf raises several exception types
 171 |         raise PdfMalformedError(f"PDF could not be parsed: {exc}") from exc
 172 |     if len(pages) > max_pages:
 173 |         raise PdfPageLimitError(
 174 |             f"PDF has {len(pages)} pages, exceeding the {max_pages}-page limit"
 175 |         )
 176 |     chunks: list[PdfChunk] = []
 177 |     pages_extracted = 0
 178 |     for page_index, page in enumerate(pages):
 179 |         page_number = page_index + 1
 180 |         try:
 181 |             text = page.extract_text() or ""
 182 |         except Exception as exc:
 183 |             raise PdfMalformedError(
 184 |                 f"PDF parsing failed on page {page_number} after "
 185 |                 f"{pages_extracted} page(s): {exc}",
 186 |                 pages_extracted=pages_extracted,
 187 |             ) from exc
 188 |         pages_extracted += 1
 189 |         chunks.extend(
 190 |             chunk_page_text(
 191 |                 text,
 192 |                 page_number=page_number,
 193 |                 file_name=file_name,
 194 |                 document_id=document_id,
 195 |                 index_version=index_version,
 196 |                 target_chars=target_chars,
 197 |             )
 198 |         )
 199 |     if not chunks:
 200 |         raise PdfTextlessError(
 201 |             f"PDF contains no extractable text ({len(pages)} page(s) parsed)"
 202 |         )
 203 |     return chunks
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L139 | Define `extract_pdf_chunks`; bind its arguments when called. The body executes only when invoked. |
| L140 | Declare parameter `pdf_path` with annotation `Path`. Caller-supplied pdf path; its uses and transformations are traced below. |
| L141 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L142 | Declare parameter `file_name` with annotation `str`. Display PDF filename; immutable IDs establish ownership and evidence identity. |
| L143 | Declare parameter `document_id` with annotation `UUID \| str \| None`. Document UUID; filenames do not establish document identity. |
| L144 | Declare parameter `index_version` with annotation `UUID \| str \| None`. UUID of one document's vector-index namespace, separate from its active publication pointer. |
| L145 | Declare parameter `max_pages` with annotation `int`. Maximum PDF pages accepted by extraction. |
| L146 | Declare parameter `max_file_bytes` with annotation `int`. Maximum PDF byte count accepted by this component. |
| L147 | Declare parameter `target_chars` with annotation `int`. Caller-supplied target chars; its uses and transformations are traced below. |
| L148 | Finish/continue the signature; the declared return annotation is `list[PdfChunk]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L149 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L151 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L152 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L153 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L154 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L155 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L156 | Evaluate the right-hand side, then bind/store it in `path`: `Path(pdf_path)` — Construct a filesystem path value (in FastAPI annotations, Path instead declares path-parameter metadata). |
| L157 | Enter the protected block; failures are matched against `OSError` in order. |
| L158 | Evaluate the right-hand side, then bind/store it in `size`: the `st_size` attribute of `path.stat()`. |
| L159 | Handle `OSError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L160 | Raise `PdfMalformedError(f'PDF is not readable: {exc}')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L161 | Evaluate the branch condition: compare whether `size` is greater than `max_file_bytes`. If truthy, enter L162; otherwise skip this indented block and continue after it. |
| L162 | Raise `PdfFileTooLargeError(f'PDF is {size} bytes, exceeding the {max_file_bytes}-byte limit')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L163 | Supply positional argument 1 to `PdfFileTooLargeError`: format a string by inserting `size`, `max_file_bytes` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L164 | Close the expression/container begun at L162; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L165 | Evaluate the branch condition: compare whether `size` equals `0`. If truthy, enter L166; otherwise skip this indented block and continue after it. |
| L166 | Raise `PdfMalformedError('PDF file is empty')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L167 | Enter the protected block; failures are matched against `Exception` in order. |
| L168 | Evaluate the right-hand side, then bind/store it in `reader`: `pypdf.PdfReader(str(path))` — Construct `pypdf.PdfReader` with the shown fields; its class/model initialization rules apply; inputs include `str(path)` — Convert the input to its string representation. |
| L169 | Evaluate the right-hand side, then bind/store it in `pages`: `list(reader.pages)` — Materialize the iterable in order into a list (or create an empty list). |
| L170 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L171 | Raise `PdfMalformedError(f'PDF could not be parsed: {exc}')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L172 | Evaluate the branch condition: compare whether `len(pages)` is greater than `max_pages`. If truthy, enter L173; otherwise skip this indented block and continue after it. |
| L173 | Raise `PdfPageLimitError(f'PDF has {len(pages)} pages, exceeding the {max_pages}-page limit')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L174 | Count the items/characters in the supplied container/string. |
| L175 | Close the expression/container begun at L173; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L176 | Evaluate the right-hand side, then bind/store it in `chunks`: build a list containing no items. |
| L177 | Evaluate the right-hand side, then bind/store it in `pages_extracted`: `0`. |
| L178 | Iterate `enumerate(pages)` (`enumerate(pages)` — Yield an index and each input item in order; the optional second argument sets the starting index), assigning each item to `(page_index, page)`. Execute the indented body once per item; an empty iterable skips it. |
| L179 | Evaluate the right-hand side, then bind/store it in `page_number`: add/concatenate `page_index` and `1`, following the parentheses/operator precedence shown in `page_index + 1`. |
| L180 | Enter the protected block; failures are matched against `Exception` in order. |
| L181 | Evaluate the right-hand side, then bind/store it in `text`: evaluate `page.extract_text() or ''` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L182 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L183 | Raise `PdfMalformedError(f'PDF parsing failed on page {page_number} after {pages_extracted} page(s): {exc}', pages_extracted=pages_extracted)`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L184 | Supply positional argument 1 to `PdfMalformedError`: format a string by inserting `page_number`, `pages_extracted`, `exc` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L185 | Supply positional argument 1 to `PdfMalformedError`: format a string by inserting `page_number`, `pages_extracted`, `exc` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L186 | Supply `pages_extracted` = `pages_extracted`.  Evaluate the value as: the current `pages_extracted` value. |
| L187 | Contribute the current `exc` value to the expression being assembled. |
| L188 | Update `pages_extracted` in place using `1` and the Add operation; the previous target value participates in the calculation. |
| L189 | `chunks.extend` with the arguments detailed below — Append every item from the supplied iterable to the list in order; inputs include `chunk_page_text(text, page_number=page_number, file_name=file_name, document_id=document_id, index_version=index_version, target_chars=target_chars)` — Call [chunk_page_text](#walk-chunk-page-text) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L190 | `chunk_page_text(text, page_number=page_number, file_name=file_name, document_id=document_id, index_version=index_version, target_chars=target_chars)` — Call [chunk_page_text](#walk-chunk-page-text) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L191 | Supply positional argument 1 to `chunk_page_text`: the current `text` value. |
| L192 | Supply `page_number` = `page_number`.  Evaluate the value as: the current `page_number` value. |
| L193 | Supply `file_name` = `file_name`. Display PDF filename; immutable IDs establish ownership and evidence identity. Evaluate the value as: the current `file_name` value. |
| L194 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L195 | Supply `index_version` = `index_version`. UUID of one document's vector-index namespace, separate from its active publication pointer. Evaluate the value as: the current `index_version` value. |
| L196 | Supply `target_chars` = `target_chars`.  Evaluate the value as: the current `target_chars` value. |
| L197 | Close the expression/container begun at L190; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L198 | Close the expression/container begun at L189; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L199 | Evaluate the branch condition: invert the truthiness of `chunks`. If truthy, enter L200; otherwise skip this indented block and continue after it. |
| L200 | Raise `PdfTextlessError(f'PDF contains no extractable text ({len(pages)} page(s) parsed)')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L201 | Count the items/characters in the supplied container/string. |
| L202 | Close the expression/container begun at L200; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L203 | Compute the return value: the current `chunks` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `PdfExtractionService.__init__(self, *, max_pages=200, max_file_bytes=26214400) -> None`

**Arguments:** Extraction budgets for this facade. **Returns:** `None`. **Work:** Stores the values; construction performs no parsing and does not validate/clamp limits. Worker configuration applies its own public-budget checks.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-pdfextractionservice---init--"></a>

#### Line-by-line execution

[Current source: lines 214–216](../../../../Backend/app/rag/pdf.py#L214-L216). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `max_pages` | `int`; default `DEFAULT_MAX_PDF_PAGES`; keyword-only | Maximum PDF pages accepted by extraction. |
| `max_file_bytes` | `int`; default `DEFAULT_MAX_PDF_BYTES`; keyword-only | Maximum PDF byte count accepted by this component. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 214 |     def __init__(self, *, max_pages: int = DEFAULT_MAX_PDF_PAGES, max_file_bytes: int = DEFAULT_MAX_PDF_BYTES) -> None:
 215 |         self.max_pages = max_pages
 216 |         self.max_file_bytes = max_file_bytes
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L214 | Define `PdfExtractionService.__init__`; bind its arguments when called. The body executes only when invoked. |
| L215 | Evaluate the right-hand side, then bind/store it in `self.max_pages`: the current `max_pages` value. |
| L216 | Evaluate the right-hand side, then bind/store it in `self.max_file_bytes`: the current `max_file_bytes` value. |

<!-- END LINE WALKTHROUGH -->

### `PdfExtractionService.extract_pdf_chunks(self, pdf_path: Path, *, file_name: str, document_id=None, index_version=None) -> list[PdfChunk]`

**Arguments:** Local path, display filename, paired optional identities. **Returns:** Complete extracted chunks. **Work:** Delegates to the module function with the facade's stored budgets and the default chunk target; errors propagate unchanged.

`split_into_sentences` is imported/re-exported, with its implementation documented in [text.md](text.md).

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-pdfextractionservice-extract-pdf-chunks"></a>

#### Line-by-line execution

[Current source: lines 218–233](../../../../Backend/app/rag/pdf.py#L218-L233). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `pdf_path` | `Path`; required; positional or keyword | Caller-supplied pdf path; each read, transformation, and validation is traced below. |
| `file_name` | `str`; required; keyword-only | Display PDF filename; immutable IDs establish ownership and evidence identity. |
| `document_id` | `UUID \| str \| None`; default `None`; keyword-only | Document UUID; filenames do not establish document identity. |
| `index_version` | `UUID \| str \| None`; default `None`; keyword-only | UUID of one document's vector-index namespace, separate from its active publication pointer. |

**Declared result:** `list[PdfChunk]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 218 |     def extract_pdf_chunks(
 219 |         self,
 220 |         pdf_path: Path,
 221 |         *,
 222 |         file_name: str,
 223 |         document_id: UUID | str | None = None,
 224 |         index_version: UUID | str | None = None,
 225 |     ) -> list[PdfChunk]:
 226 |         return extract_pdf_chunks(
 227 |             pdf_path,
 228 |             file_name=file_name,
 229 |             document_id=document_id,
 230 |             index_version=index_version,
 231 |             max_pages=self.max_pages,
 232 |             max_file_bytes=self.max_file_bytes,
 233 |         )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L218 | Define `PdfExtractionService.extract_pdf_chunks`; bind its arguments when called. The body executes only when invoked. |
| L219 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L220 | Declare parameter `pdf_path` with annotation `Path`. Caller-supplied pdf path; its uses and transformations are traced below. |
| L221 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L222 | Declare parameter `file_name` with annotation `str`. Display PDF filename; immutable IDs establish ownership and evidence identity. |
| L223 | Declare parameter `document_id` with annotation `UUID \| str \| None`. Document UUID; filenames do not establish document identity. |
| L224 | Declare parameter `index_version` with annotation `UUID \| str \| None`. UUID of one document's vector-index namespace, separate from its active publication pointer. |
| L225 | Finish/continue the signature; the declared return annotation is `list[PdfChunk]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L226 | Compute the return value: `extract_pdf_chunks` with the arguments detailed below — Call [extract_pdf_chunks](#walk-extract-pdf-chunks) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L227 | Supply positional argument 1 to `extract_pdf_chunks`: the current `pdf_path` value. |
| L228 | Supply `file_name` = `file_name`. Display PDF filename; immutable IDs establish ownership and evidence identity. Evaluate the value as: the current `file_name` value. |
| L229 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L230 | Supply `index_version` = `index_version`. UUID of one document's vector-index namespace, separate from its active publication pointer. Evaluate the value as: the current `index_version` value. |
| L231 | Supply `max_pages` = `self.max_pages`. Maximum PDF pages accepted by extraction. Evaluate the value as: the `max_pages` attribute of `self`. |
| L232 | Supply `max_file_bytes` = `self.max_file_bytes`. Maximum PDF byte count accepted by this component. Evaluate the value as: the `max_file_bytes` attribute of `self`. |
| L233 | Close the expression/container begun at L226; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->
