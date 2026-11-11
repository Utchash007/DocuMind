# `app/rag/indexing.py`

[Source](../../../../Backend/app/rag/indexing.py) · [Backend index](../../README.md)

Versioned Chroma writes/deletes. `COLLECTION_NAME="documind_chunks_v2"`; default write batch size is 100. Each record carries `user_id`, `project_id`, `document_id`, `index_version`, `source`, `page`, and `chunk_id`. Database publication of an active version happens separately in [jobs/queue.md](../jobs/queue.md).

## Functions and collection protocol

### `IndexWriteError.__init__(self, message: str) -> None`

**Arguments:** Internal diagnostic. **Returns:** `None`. **Work:** Initializes the exception and `.message`; class policy is `code="index_write_failed"`, `retryable=True`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-indexwriteerror---init--"></a>

#### Line-by-line execution

[Current source: lines 63–65](../../../../Backend/app/rag/indexing.py#L63-L65). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `message` | `str`; required; positional or keyword | Caller-supplied message; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  63 |     def __init__(self, message: str) -> None:
  64 |         super().__init__(message)
  65 |         self.message = message
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L63 | Define `IndexWriteError.__init__`; bind its arguments when called. The body executes only when invoked. |
| L64 | `super().__init__(message)` — Initialize the base exception/object with the supplied arguments; first obtain the receiver: `super()` — Resolve the superclass proxy for the current method and instance. The return value is not assigned here. |
| L65 | Evaluate the right-hand side, then bind/store it in `self.message`: the current `message` value. |

<!-- END LINE WALKTHROUGH -->

### `chunk_id_for(document_id, index_version, page_number: int, sub_index: int) -> str`

**Arguments:** Paired UUID/string identities or two nulls, page number, within-page index. **Returns:** Canonical owned/preflight chunk label. **Work:** Lazily imports and delegates to [pdf.chunk_id_for](pdf.md); partial identity raises `ValueError` there.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-chunk-id-for"></a>

#### Line-by-line execution

[Current source: lines 68–77](../../../../Backend/app/rag/indexing.py#L68-L77). Line numbers below are file line numbers, not a separate example.

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
  68 | def chunk_id_for(
  69 |     document_id: UUID | str | None,
  70 |     index_version: UUID | str | None,
  71 |     page_number: int,
  72 |     sub_index: int,
  73 | ) -> str:
  74 |     """Re-export of the canonical chunk-ID builder (see ``app.rag.pdf``)."""
  75 |     from app.rag.pdf import chunk_id_for as _build
  76 | 
  77 |     return _build(document_id, index_version, page_number, sub_index)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L68 | Define `chunk_id_for`; bind its arguments when called. The body executes only when invoked. |
| L69 | Declare parameter `document_id` with annotation `UUID \| str \| None`. Document UUID; filenames do not establish document identity. |
| L70 | Declare parameter `index_version` with annotation `UUID \| str \| None`. UUID of one document's vector-index namespace, separate from its active publication pointer. |
| L71 | Declare parameter `page_number` with annotation `int`. Caller-supplied page number; its uses and transformations are traced below. |
| L72 | Declare parameter `sub_index` with annotation `int`. Caller-supplied sub index; its uses and transformations are traced below. |
| L73 | Finish/continue the signature; the declared return annotation is `str`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L74 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L75 | Import `chunk_id_for` as `_build` from `app.rag.pdf`; inside a function this import is deferred until this path is reached. |
| L77 | Compute the return value: `_build(document_id, index_version, page_number, sub_index)` — Call [_build](pdf.md#walk-chunk-id-for) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `build_metadata(*, user_id, project_id, document_id, index_version, chunk: PdfChunk) -> dict[str, Any]`

**Arguments:** Four UUID/string scope identities and the chunk. **Returns:** A dictionary containing exactly the seven metadata keys. **Work:** Converts identities to strings and page to `int`, copying source label and chunk ID. It does not verify that a supplied chunk ID encodes the same scope; extraction/caller code constructs that identity.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-build-metadata"></a>

#### Line-by-line execution

[Current source: lines 80–97](../../../../Backend/app/rag/indexing.py#L80-L97). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `user_id` | `UUID \| str`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID \| str`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID \| str`; required; keyword-only | Document UUID; filenames do not establish document identity. |
| `index_version` | `UUID \| str`; required; keyword-only | UUID of one document's vector-index namespace, separate from its active publication pointer. |
| `chunk` | `PdfChunk`; required; keyword-only | Caller-supplied chunk; each read, transformation, and validation is traced below. |

**Declared result:** `dict[str, Any]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  80 | def build_metadata(
  81 |     *,
  82 |     user_id: UUID | str,
  83 |     project_id: UUID | str,
  84 |     document_id: UUID | str,
  85 |     index_version: UUID | str,
  86 |     chunk: PdfChunk,
  87 | ) -> dict[str, Any]:
  88 |     """Canonical v2 metadata for one chunk (exactly the 7 frozen keys)."""
  89 |     return {
  90 |         "user_id": str(user_id),
  91 |         "project_id": str(project_id),
  92 |         "document_id": str(document_id),
  93 |         "index_version": str(index_version),
  94 |         "source": chunk.source,
  95 |         "page": int(chunk.page_number),
  96 |         "chunk_id": chunk.chunk_id,
  97 |     }
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L80 | Define `build_metadata`; bind its arguments when called. The body executes only when invoked. |
| L81 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L82 | Declare parameter `user_id` with annotation `UUID \| str`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L83 | Declare parameter `project_id` with annotation `UUID \| str`. Project UUID used to constrain resource lookup or provider metadata. |
| L84 | Declare parameter `document_id` with annotation `UUID \| str`. Document UUID; filenames do not establish document identity. |
| L85 | Declare parameter `index_version` with annotation `UUID \| str`. UUID of one document's vector-index namespace, separate from its active publication pointer. |
| L86 | Declare parameter `chunk` with annotation `PdfChunk`. Caller-supplied chunk; its uses and transformations are traced below. |
| L87 | Finish/continue the signature; the declared return annotation is `dict[str, Any]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L88 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L89 | Compute the return value: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L90 | Add mapping entry `'user_id'`: `str(user_id)` — Convert the input to its string representation. |
| L91 | Add mapping entry `'project_id'`: `str(project_id)` — Convert the input to its string representation. |
| L92 | Add mapping entry `'document_id'`: `str(document_id)` — Convert the input to its string representation. |
| L93 | Add mapping entry `'index_version'`: `str(index_version)` — Convert the input to its string representation. |
| L94 | Add mapping entry `'source'`: the `source` attribute of `chunk`. |
| L95 | Add mapping entry `'page'`: `int(chunk.page_number)` — Convert the input to an integer (using the optional numeric base). |
| L96 | Add mapping entry `'chunk_id'`: the `chunk_id` attribute of `chunk`. |
| L97 | Close the expression/container begun at L89; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `version_where(*, user_id=None, project_id=None, document_id=None, index_version=None) -> dict[str, Any]`

**Arguments:** Any supplied subset of the four UUID/string scope fields. **Returns:** One direct equality clause, or `$and` containing multiple clauses. **Work:** Adds non-null values in owner/project/document/version order and rejects an empty scope with `ValueError`. Despite the name, the helper permits partial scopes; deletion callers supply document and version and normally owner/project as well.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-version-where"></a>

#### Line-by-line execution

[Current source: lines 100–121](../../../../Backend/app/rag/indexing.py#L100-L121). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `user_id` | `UUID \| str \| None`; default `None`; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID \| str \| None`; default `None`; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID \| str \| None`; default `None`; keyword-only | Document UUID; filenames do not establish document identity. |
| `index_version` | `UUID \| str \| None`; default `None`; keyword-only | UUID of one document's vector-index namespace, separate from its active publication pointer. |

**Declared result:** `dict[str, Any]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 100 | def version_where(
 101 |     *,
 102 |     user_id: UUID | str | None = None,
 103 |     project_id: UUID | str | None = None,
 104 |     document_id: UUID | str | None = None,
 105 |     index_version: UUID | str | None = None,
 106 | ) -> dict[str, Any]:
 107 |     """Chroma ``where`` filter for an exact (document, version) scope."""
 108 |     clauses: list[dict[str, str]] = []
 109 |     if user_id is not None:
 110 |         clauses.append({"user_id": str(user_id)})
 111 |     if project_id is not None:
 112 |         clauses.append({"project_id": str(project_id)})
 113 |     if document_id is not None:
 114 |         clauses.append({"document_id": str(document_id)})
 115 |     if index_version is not None:
 116 |         clauses.append({"index_version": str(index_version)})
 117 |     if not clauses:
 118 |         raise ValueError("version_where requires at least one scope clause")
 119 |     if len(clauses) == 1:
 120 |         return clauses[0]
 121 |     return {"$and": clauses}
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L100 | Define `version_where`; bind its arguments when called. The body executes only when invoked. |
| L101 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L102 | Declare parameter `user_id` with annotation `UUID \| str \| None`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L103 | Declare parameter `project_id` with annotation `UUID \| str \| None`. Project UUID used to constrain resource lookup or provider metadata. |
| L104 | Declare parameter `document_id` with annotation `UUID \| str \| None`. Document UUID; filenames do not establish document identity. |
| L105 | Declare parameter `index_version` with annotation `UUID \| str \| None`. UUID of one document's vector-index namespace, separate from its active publication pointer. |
| L106 | Finish/continue the signature; the declared return annotation is `dict[str, Any]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L107 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L108 | Evaluate the right-hand side, then bind/store it in `clauses`: build a list containing no items. |
| L109 | Evaluate the branch condition: compare whether `user_id` is not the same object as `None`. If truthy, enter L110; otherwise skip this indented block and continue after it. |
| L110 | `clauses.append({'user_id': str(user_id)})` — Append one object to the mutable list in place. The return value is not assigned here. |
| L111 | Evaluate the branch condition: compare whether `project_id` is not the same object as `None`. If truthy, enter L112; otherwise skip this indented block and continue after it. |
| L112 | `clauses.append({'project_id': str(project_id)})` — Append one object to the mutable list in place. The return value is not assigned here. |
| L113 | Evaluate the branch condition: compare whether `document_id` is not the same object as `None`. If truthy, enter L114; otherwise skip this indented block and continue after it. |
| L114 | `clauses.append({'document_id': str(document_id)})` — Append one object to the mutable list in place. The return value is not assigned here. |
| L115 | Evaluate the branch condition: compare whether `index_version` is not the same object as `None`. If truthy, enter L116; otherwise skip this indented block and continue after it. |
| L116 | `clauses.append({'index_version': str(index_version)})` — Append one object to the mutable list in place. The return value is not assigned here. |
| L117 | Evaluate the branch condition: invert the truthiness of `clauses`. If truthy, enter L118; otherwise skip this indented block and continue after it. |
| L118 | Raise `ValueError('version_where requires at least one scope clause')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L119 | Evaluate the branch condition: compare whether `len(clauses)` equals `1`. If truthy, enter L120; otherwise skip this indented block and continue after it. |
| L120 | Compute the return value: look up index/key `0` in `clauses`; a missing key or out-of-range index raises. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L121 | Compute the return value: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `ChromaCollection.upsert(self, *, ids, embeddings, documents, metadatas) -> None`

**Arguments:** Parallel sequences of chunk IDs, vectors, texts, and metadata. **Returns:** Contractually `None`. **Work:** Protocol declaration (`...`) only; a concrete Chroma client performs idempotent insertion/replacement. The declaration itself has no provider behavior.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-chromacollection-upsert"></a>

#### Line-by-line execution

[Current source: lines 127–135](../../../../Backend/app/rag/indexing.py#L127-L135). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `ids` | `Sequence[str]`; required; keyword-only | Caller-supplied ids; each read, transformation, and validation is traced below. |
| `embeddings` | `Sequence[Sequence[float]]`; required; keyword-only | Per-chunk numeric vectors supplied for indexing. |
| `documents` | `Sequence[str]`; required; keyword-only | Caller-supplied documents; each read, transformation, and validation is traced below. |
| `metadatas` | `Sequence[dict[str, Any]]`; required; keyword-only | Caller-supplied metadatas; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 127 |     def upsert(
 128 |         self,
 129 |         *,
 130 |         ids: Sequence[str],
 131 |         embeddings: Sequence[Sequence[float]],
 132 |         documents: Sequence[str],
 133 |         metadatas: Sequence[dict[str, Any]],
 134 |     ) -> None:
 135 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L127 | Define `ChromaCollection.upsert`; bind its arguments when called. The body executes only when invoked. |
| L128 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L129 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L130 | Declare parameter `ids` with annotation `Sequence[str]`. Caller-supplied ids; its uses and transformations are traced below. |
| L131 | Declare parameter `embeddings` with annotation `Sequence[Sequence[float]]`. Per-chunk numeric vectors supplied for indexing. |
| L132 | Declare parameter `documents` with annotation `Sequence[str]`. Caller-supplied documents; its uses and transformations are traced below. |
| L133 | Declare parameter `metadatas` with annotation `Sequence[dict[str, Any]]`. Caller-supplied metadatas; its uses and transformations are traced below. |
| L134 | Finish/continue the signature; the declared return annotation is `None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L135 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `ChromaCollection.delete(self, *, where=None, ids=None) -> None`

**Arguments:** Optional metadata filter and/or ID sequence. **Returns:** Contractually `None`. **Work:** Protocol declaration only; this service uses metadata-filter deletion. Missing records count as successful deletion under the concrete provider's normal behavior.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-chromacollection-delete"></a>

#### Line-by-line execution

[Current source: lines 137–138](../../../../Backend/app/rag/indexing.py#L137-L138). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `where` | `dict[str, Any] \| None`; default `None`; keyword-only | Caller-supplied where; each read, transformation, and validation is traced below. |
| `ids` | `Sequence[str] \| None`; default `None`; keyword-only | Caller-supplied ids; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 137 |     def delete(self, *, where: dict[str, Any] | None = None, ids: Sequence[str] | None = None) -> None:
 138 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L137 | Define `ChromaCollection.delete`; bind its arguments when called. The body executes only when invoked. |
| L138 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `default_chroma_collection()`

**Arguments:** None. **Returns:** Chroma collection object. **Work:** Lazily imports `chromadb`, constructs `CloudClient` from `CHROMA_API_KEY`, `CHROMA_TENANT`, `CHROMA_DATABASE`, and calls `get_or_create_collection`. This function can contact/create the collection when called; importing its module alone does not. `CHROMA_HOST` is not used.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-default-chroma-collection"></a>

#### Line-by-line execution

[Current source: lines 141–155](../../../../Backend/app/rag/indexing.py#L141-L155). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** No return annotation; follow the return/yield lines below. Python supplies None when a non-generator reaches the end without return.

**Numbered source**

```text
 141 | def default_chroma_collection():
 142 |     """Build the production ``documind_chunks_v2`` collection.
 143 | 
 144 |     Uses ``CHROMA_API_KEY`` / ``CHROMA_TENANT`` / ``CHROMA_DATABASE``.
 145 |     Constructed lazily so importing this
 146 |     module never touches the network or requires credentials.
 147 |     """
 148 |     import chromadb
 149 | 
 150 |     client = chromadb.CloudClient(
 151 |         api_key=os.environ.get("CHROMA_API_KEY"),
 152 |         tenant=os.environ.get("CHROMA_TENANT"),
 153 |         database=os.environ.get("CHROMA_DATABASE"),
 154 |     )
 155 |     return client.get_or_create_collection(name=COLLECTION_NAME)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L141 | Define `default_chroma_collection`; bind its arguments when called. The body executes only when invoked. |
| L142 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L144 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L145 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L146 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L147 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L148 | Import `chromadb` when execution reaches this line; an unavailable dependency raises ImportError. |
| L150 | Evaluate the right-hand side, then bind/store it in `client`: `chromadb.CloudClient(api_key=os.environ.get('CHROMA_API_KEY'), tenant=os.environ.get('CHROMA_TENANT'), database=os.environ.get('CHROMA_DATABASE'))` — Construct `chromadb.CloudClient` with the shown fields; its class/model initialization rules apply. |
| L151 | Supply `api_key` = `os.environ.get('CHROMA_API_KEY')`. Server-side provider credential; do not expose it to browser configuration. Evaluate the value as: `os.environ.get('CHROMA_API_KEY')` — Read a process environment value without changing it, using the supplied fallback if absent. |
| L152 | Supply `tenant` = `os.environ.get('CHROMA_TENANT')`.  Evaluate the value as: `os.environ.get('CHROMA_TENANT')` — Read a process environment value without changing it, using the supplied fallback if absent. |
| L153 | Supply `database` = `os.environ.get('CHROMA_DATABASE')`.  Evaluate the value as: `os.environ.get('CHROMA_DATABASE')` — Read a process environment value without changing it, using the supplied fallback if absent. |
| L154 | Close the expression/container begun at L150; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L155 | Compute the return value: `client.get_or_create_collection(name=COLLECTION_NAME)` — Invoke `client.get_or_create_collection` with the shown inputs and use its result; see the function overview for its role in this flow. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

## `IndexService`

### `IndexService.__init__(self, collection_factory=None, *, batch_size=100, embedder=None) -> None`

**Arguments:** Optional zero-argument collection factory, write batch size, optional embedding collaborator. **Returns:** `None`. **Work:** Stores the factory/default and embedder, clamps batch size to at least 1. No collection connection is opened at construction.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-indexservice---init--"></a>

#### Line-by-line execution

[Current source: lines 171–180](../../../../Backend/app/rag/indexing.py#L171-L180). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `collection_factory` | `Callable[[], ChromaCollection] \| None`; default `None`; positional or keyword | Caller-supplied collection factory; each read, transformation, and validation is traced below. |
| `batch_size` | `int`; default `INDEX_BATCH_SIZE`; keyword-only | Maximum batch size for the operation; validation/clamping is explicit in the body. |
| `embedder` | `Any \| None`; default `None`; keyword-only | Embedding collaborator; the function selects its default only where explicitly shown. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 171 |     def __init__(
 172 |         self,
 173 |         collection_factory: Callable[[], ChromaCollection] | None = None,
 174 |         *,
 175 |         batch_size: int = INDEX_BATCH_SIZE,
 176 |         embedder: Any | None = None,
 177 |     ) -> None:
 178 |         self._factory = collection_factory or default_chroma_collection
 179 |         self.batch_size = max(1, batch_size)
 180 |         self._embedder = embedder
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L171 | Define `IndexService.__init__`; bind its arguments when called. The body executes only when invoked. |
| L172 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L173 | Declare parameter `collection_factory` with annotation `Callable[[], ChromaCollection] \| None`. Caller-supplied collection factory; its uses and transformations are traced below. |
| L174 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L175 | Declare parameter `batch_size` with annotation `int`. Maximum batch size for the operation; validation/clamping is explicit in the body. |
| L176 | Declare parameter `embedder` with annotation `Any \| None`. Embedding collaborator; the function selects its default only where explicitly shown. |
| L177 | Finish/continue the signature; the declared return annotation is `None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L178 | Evaluate the right-hand side, then bind/store it in `self._factory`: evaluate `collection_factory or default_chroma_collection` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L179 | Evaluate the right-hand side, then bind/store it in `self.batch_size`: `max(1, batch_size)` — Choose the largest supplied value; nested min/max calls implement the stated bound. |
| L180 | Evaluate the right-hand side, then bind/store it in `self._embedder`: the current `embedder` value. |

<!-- END LINE WALKTHROUGH -->

### `IndexService.publish_index_version(self, *, user_id, project_id, document_id, index_version, chunks, embeddings=None) -> int`

- **Arguments:** Four scope identities, ordered `PdfChunk` sequence, optional corresponding vector sequence.
- **Returns:** Number of upserted records after every batch succeeds. The concrete method returns this count even though the shared `PdfPipeline` protocol declares `None`.
- **Work:** Materializes chunks and rejects an empty version. If vectors are absent, requires an injected embedder and calls `embed_texts`; embedding failures become `IndexWriteError`. Requires matching chunk/vector counts before opening the collection. For each batch, builds ID/text/metadata arrays and calls `upsert` with corresponding vectors, accumulating record count.
- **Errors/side effects:** Factory/upsert failures become `IndexWriteError`; successful earlier batches remain in this version namespace if a later batch fails. It does not roll back provider writes or change PostgreSQL's active pointer. Vector dimension/finiteness validation belongs to the embedder; supplied vectors are only count-checked here.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-indexservice-publish-index-version"></a>

#### Line-by-line execution

[Current source: lines 182–247](../../../../Backend/app/rag/indexing.py#L182-L247). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `user_id` | `UUID \| str`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID \| str`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID \| str`; required; keyword-only | Document UUID; filenames do not establish document identity. |
| `index_version` | `UUID \| str`; required; keyword-only | UUID of one document's vector-index namespace, separate from its active publication pointer. |
| `chunks` | `Sequence[PdfChunk]`; required; keyword-only | PDF text chunks with the metadata required by this operation. |
| `embeddings` | `Sequence[Sequence[float]] \| None`; default `None`; keyword-only | Per-chunk numeric vectors supplied for indexing. |

**Declared result:** `int`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 182 |     def publish_index_version(
 183 |         self,
 184 |         *,
 185 |         user_id: UUID | str,
 186 |         project_id: UUID | str,
 187 |         document_id: UUID | str,
 188 |         index_version: UUID | str,
 189 |         chunks: Sequence[PdfChunk],
 190 |         embeddings: Sequence[Sequence[float]] | None = None,
 191 |     ) -> int:
 192 |         """Write ``chunks`` into the ``index_version`` namespace.
 193 | 
 194 |         ``embeddings`` must be the output of
 195 |         ``EmbeddingService.embed_texts`` for the chunk texts, in order.
 196 |         When omitted, the service's injected ``embedder`` computes
 197 |         them (the frozen protocol shape); with neither, this raises --
 198 |         production must never index without vectors.  Returns the
 199 |         number of records written.
 200 |         """
 201 |         items = list(chunks)
 202 |         if not items:
 203 |             raise IndexWriteError("refusing to publish an empty index version")
 204 |         if embeddings is None:
 205 |             if self._embedder is None:
 206 |                 raise IndexWriteError(
 207 |                     "embeddings are required: pass embeddings or an embedder"
 208 |                 )
 209 |             try:
 210 |                 embeddings = self._embedder.embed_texts([chunk.text for chunk in items])
 211 |             except Exception as exc:
 212 |                 raise IndexWriteError(f"index-time embedding failed: {exc}") from exc
 213 |         vectors = list(embeddings)
 214 |         if len(vectors) != len(items):
 215 |             raise IndexWriteError(
 216 |                 f"chunk/vector count mismatch: {len(items)} chunks, {len(vectors)} vectors"
 217 |             )
 218 |         collection = self._collection()
 219 |         written = 0
 220 |         for start in range(0, len(items), self.batch_size):
 221 |             batch = items[start : start + self.batch_size]
 222 |             batch_vectors = vectors[start : start + self.batch_size]
 223 |             ids = [chunk.chunk_id for chunk in batch]
 224 |             documents = [chunk.text for chunk in batch]
 225 |             metadatas = [
 226 |                 build_metadata(
 227 |                     user_id=user_id,
 228 |                     project_id=project_id,
 229 |                     document_id=document_id,
 230 |                     index_version=index_version,
 231 |                     chunk=chunk,
 232 |                 )
 233 |                 for chunk in batch
 234 |             ]
 235 |             try:
 236 |                 collection.upsert(
 237 |                     ids=ids,
 238 |                     embeddings=batch_vectors,
 239 |                     documents=documents,
 240 |                     metadatas=metadatas,
 241 |                 )
 242 |             except IndexWriteError:
 243 |                 raise
 244 |             except Exception as exc:
 245 |                 raise IndexWriteError(f"chroma upsert failed: {exc}") from exc
 246 |             written += len(batch)
 247 |         return written
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L182 | Define `IndexService.publish_index_version`; bind its arguments when called. The body executes only when invoked. |
| L183 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L184 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L185 | Declare parameter `user_id` with annotation `UUID \| str`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L186 | Declare parameter `project_id` with annotation `UUID \| str`. Project UUID used to constrain resource lookup or provider metadata. |
| L187 | Declare parameter `document_id` with annotation `UUID \| str`. Document UUID; filenames do not establish document identity. |
| L188 | Declare parameter `index_version` with annotation `UUID \| str`. UUID of one document's vector-index namespace, separate from its active publication pointer. |
| L189 | Declare parameter `chunks` with annotation `Sequence[PdfChunk]`. PDF text chunks with the metadata required by this operation. |
| L190 | Declare parameter `embeddings` with annotation `Sequence[Sequence[float]] \| None`. Per-chunk numeric vectors supplied for indexing. |
| L191 | Finish/continue the signature; the declared return annotation is `int`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L192 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L194 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L195 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L196 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L197 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L198 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L199 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L200 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L201 | Evaluate the right-hand side, then bind/store it in `items`: `list(chunks)` — Materialize the iterable in order into a list (or create an empty list). |
| L202 | Evaluate the branch condition: invert the truthiness of `items`. If truthy, enter L203; otherwise skip this indented block and continue after it. |
| L203 | Raise `IndexWriteError('refusing to publish an empty index version')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L204 | Evaluate the branch condition: compare whether `embeddings` is the same object as `None`. If truthy, enter L205; otherwise skip this indented block and continue after it. |
| L205 | Evaluate the branch condition: compare whether `self._embedder` is the same object as `None`. If truthy, enter L206; otherwise skip this indented block and continue after it. |
| L206 | Raise `IndexWriteError('embeddings are required: pass embeddings or an embedder')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L207 | Supply positional argument 1 to `IndexWriteError`: `'embeddings are required: pass embeddings or an embedder'`. |
| L208 | Close the expression/container begun at L206; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L209 | Enter the protected block; failures are matched against `Exception` in order. |
| L210 | Evaluate the right-hand side, then bind/store it in `embeddings`: `self._embedder.embed_texts([chunk.text for chunk in items])` — Embed input texts in order using the selected provider/configuration; configured mock mode substitutes deterministic vectors; inputs include iterate `items`, binding each item to `chunk`; produce `chunk.text` into a new list. |
| L211 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L212 | Raise `IndexWriteError(f'index-time embedding failed: {exc}')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L213 | Evaluate the right-hand side, then bind/store it in `vectors`: `list(embeddings)` — Materialize the iterable in order into a list (or create an empty list). |
| L214 | Evaluate the branch condition: compare whether `len(vectors)` differs from `len(items)`. If truthy, enter L215; otherwise skip this indented block and continue after it. |
| L215 | Raise `IndexWriteError(f'chunk/vector count mismatch: {len(items)} chunks, {len(vectors)} vectors')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L216 | Count the items/characters in the supplied container/string. |
| L217 | Close the expression/container begun at L215; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L218 | Evaluate the right-hand side, then bind/store it in `collection`: `self._collection()` — Call [IndexService._collection](#walk-indexservice--collection) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L219 | Evaluate the right-hand side, then bind/store it in `written`: `0`. |
| L220 | Iterate `range(0, len(items), self.batch_size)` (`range(0, len(items), self.batch_size)` — Generate integer positions from the start up to, but excluding, the stop, using the supplied step; inputs include `len(items)` — Count the items/characters in the supplied container/string), assigning each item to `start`. Execute the indented body once per item; an empty iterable skips it. |
| L221 | Evaluate the right-hand side, then bind/store it in `batch`: slice `items` from `start` up to `start + self.batch_size` (exclusive stop). |
| L222 | Evaluate the right-hand side, then bind/store it in `batch_vectors`: slice `vectors` from `start` up to `start + self.batch_size` (exclusive stop). |
| L223 | Evaluate the right-hand side, then bind/store it in `ids`: iterate `batch`, binding each item to `chunk`; produce `chunk.chunk_id` into a new list. |
| L224 | Evaluate the right-hand side, then bind/store it in `documents`: iterate `batch`, binding each item to `chunk`; produce `chunk.text` into a new list. |
| L225 | Evaluate the right-hand side, then bind/store it in `metadatas`: iterate `batch`, binding each item to `chunk`; produce `build_metadata(user_id=user_id, project_id=project_id, document_id=document_id, index_version=index_version, chunk=chunk)` into a new list. |
| L226 | `build_metadata(user_id=user_id, project_id=project_id, document_id=document_id, index_version=index_version, chunk=chunk)` — Call [build_metadata](#walk-build-metadata) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L227 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L228 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L229 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L230 | Supply `index_version` = `index_version`. UUID of one document's vector-index namespace, separate from its active publication pointer. Evaluate the value as: the current `index_version` value. |
| L231 | Supply `chunk` = `chunk`.  Evaluate the value as: the current `chunk` value. |
| L232 | Close the expression/container begun at L226; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L233 | Contribute the current `chunk` value to the expression being assembled. |
| L234 | Close the expression/container begun at L225; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L235 | Enter the protected block; failures are matched against `IndexWriteError`, `Exception` in order. |
| L236 | `collection.upsert(ids=ids, embeddings=batch_vectors, documents=documents, metadatas=metadatas)` — Write the supplied IDs, vectors, text, and metadata into the Chroma collection; matching IDs are replaced. The return value is not assigned here. |
| L237 | Supply `ids` = `ids`.  Evaluate the value as: the current `ids` value. |
| L238 | Supply `embeddings` = `batch_vectors`. Per-chunk numeric vectors supplied for indexing. Evaluate the value as: the current `batch_vectors` value. |
| L239 | Supply `documents` = `documents`.  Evaluate the value as: the current `documents` value. |
| L240 | Supply `metadatas` = `metadatas`.  Evaluate the value as: the current `metadatas` value. |
| L241 | Close the expression/container begun at L236; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L242 | Handle `IndexWriteError`; only a matching error from the associated try enters this body. |
| L243 | Re-raise the currently handled exception with its traceback; no replacement result is returned. |
| L244 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L245 | Raise `IndexWriteError(f'chroma upsert failed: {exc}')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L246 | Update `written` in place using `len(batch)` and the Add operation; the previous target value participates in the calculation. |
| L247 | Compute the return value: the current `written` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `IndexService.delete_index_version(self, *, user_id=None, project_id=None, document_id, index_version) -> None`

**Arguments:** Required document/version IDs, optional owner/project scope. **Returns:** `None`. **Work:** Opens a collection and deletes with `version_where` combining supplied scope. Preserves `IndexWriteError`; wraps other provider/filter exceptions as that error. No special not-found exception is suppressed; idempotency relies on delete's normal success for an empty match.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-indexservice-delete-index-version"></a>

#### Line-by-line execution

[Current source: lines 249–271](../../../../Backend/app/rag/indexing.py#L249-L271). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `user_id` | `UUID \| str \| None`; default `None`; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID \| str \| None`; default `None`; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID \| str`; required; keyword-only | Document UUID; filenames do not establish document identity. |
| `index_version` | `UUID \| str`; required; keyword-only | UUID of one document's vector-index namespace, separate from its active publication pointer. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 249 |     def delete_index_version(
 250 |         self,
 251 |         *,
 252 |         user_id: UUID | str | None = None,
 253 |         project_id: UUID | str | None = None,
 254 |         document_id: UUID | str,
 255 |         index_version: UUID | str,
 256 |     ) -> None:
 257 |         """Idempotently delete one (document, version) namespace."""
 258 |         collection = self._collection()
 259 |         try:
 260 |             collection.delete(
 261 |                 where=version_where(
 262 |                     user_id=user_id,
 263 |                     project_id=project_id,
 264 |                     document_id=document_id,
 265 |                     index_version=index_version,
 266 |                 )
 267 |             )
 268 |         except IndexWriteError:
 269 |             raise
 270 |         except Exception as exc:
 271 |             raise IndexWriteError(f"chroma namespace delete failed: {exc}") from exc
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L249 | Define `IndexService.delete_index_version`; bind its arguments when called. The body executes only when invoked. |
| L250 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L251 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L252 | Declare parameter `user_id` with annotation `UUID \| str \| None`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L253 | Declare parameter `project_id` with annotation `UUID \| str \| None`. Project UUID used to constrain resource lookup or provider metadata. |
| L254 | Declare parameter `document_id` with annotation `UUID \| str`. Document UUID; filenames do not establish document identity. |
| L255 | Declare parameter `index_version` with annotation `UUID \| str`. UUID of one document's vector-index namespace, separate from its active publication pointer. |
| L256 | Finish/continue the signature; the declared return annotation is `None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L257 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L258 | Evaluate the right-hand side, then bind/store it in `collection`: `self._collection()` — Call [IndexService._collection](#walk-indexservice--collection) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L259 | Enter the protected block; failures are matched against `IndexWriteError`, `Exception` in order. |
| L260 | `collection.delete(where=version_where(user_id=user_id, project_id=project_id, document_id=document_id, index_version=index_version))` — Invoke `collection.delete` with the shown inputs and use its result; see the function overview for its role in this flow. The return value is not assigned here. |
| L261 | Supply `where` = `version_where(user_id=user_id, project_id=project_id, document_id=document_id, index_version=index_version)`.  Evaluate the value as: `version_where(user_id=user_id, project_id=project_id, document_id=document_id, index_version=index_version)` — Call [version_where](#walk-version-where) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L262 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L263 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L264 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L265 | Supply `index_version` = `index_version`. UUID of one document's vector-index namespace, separate from its active publication pointer. Evaluate the value as: the current `index_version` value. |
| L266 | Close the expression/container begun at L261; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L267 | Close the expression/container begun at L260; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L268 | Handle `IndexWriteError`; only a matching error from the associated try enters this body. |
| L269 | Re-raise the currently handled exception with its traceback; no replacement result is returned. |
| L270 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L271 | Raise `IndexWriteError(f'chroma namespace delete failed: {exc}')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |

<!-- END LINE WALKTHROUGH -->

### `IndexService.delete_all_versions(self, *, user_id=None, project_id=None, document_id, index_versions) -> int`

**Arguments:** Optional owner/project IDs, document ID, explicit known-version sequence. **Returns:** Count of successful delete calls (including repeated version values). **Work:** Calls `delete_index_version` serially for each input; stops on the first exception. It does not enumerate versions in Chroma or PostgreSQL.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-indexservice-delete-all-versions"></a>

#### Line-by-line execution

[Current source: lines 273–291](../../../../Backend/app/rag/indexing.py#L273-L291). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `user_id` | `UUID \| str \| None`; default `None`; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID \| str \| None`; default `None`; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID \| str`; required; keyword-only | Document UUID; filenames do not establish document identity. |
| `index_versions` | `Sequence[UUID \| str]`; required; keyword-only | Caller-supplied index versions; each read, transformation, and validation is traced below. |

**Declared result:** `int`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 273 |     def delete_all_versions(
 274 |         self,
 275 |         *,
 276 |         user_id: UUID | str | None = None,
 277 |         project_id: UUID | str | None = None,
 278 |         document_id: UUID | str,
 279 |         index_versions: Sequence[UUID | str],
 280 |     ) -> int:
 281 |         """Delete every known version of a document; returns attempts."""
 282 |         attempts = 0
 283 |         for version in index_versions:
 284 |             self.delete_index_version(
 285 |                 user_id=user_id,
 286 |                 project_id=project_id,
 287 |                 document_id=document_id,
 288 |                 index_version=version,
 289 |             )
 290 |             attempts += 1
 291 |         return attempts
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L273 | Define `IndexService.delete_all_versions`; bind its arguments when called. The body executes only when invoked. |
| L274 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L275 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L276 | Declare parameter `user_id` with annotation `UUID \| str \| None`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L277 | Declare parameter `project_id` with annotation `UUID \| str \| None`. Project UUID used to constrain resource lookup or provider metadata. |
| L278 | Declare parameter `document_id` with annotation `UUID \| str`. Document UUID; filenames do not establish document identity. |
| L279 | Declare parameter `index_versions` with annotation `Sequence[UUID \| str]`. Caller-supplied index versions; its uses and transformations are traced below. |
| L280 | Finish/continue the signature; the declared return annotation is `int`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L281 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L282 | Evaluate the right-hand side, then bind/store it in `attempts`: `0`. |
| L283 | Iterate `index_versions` (the current `index_versions` value), assigning each item to `version`. Execute the indented body once per item; an empty iterable skips it. |
| L284 | `self.delete_index_version(user_id=user_id, project_id=project_id, document_id=document_id, index_version=version)` — Delete the exact user/project/document/version namespace from Chroma; this does not change the active SQL pointer. The return value is not assigned here. |
| L285 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L286 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L287 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L288 | Supply `index_version` = `version`. UUID of one document's vector-index namespace, separate from its active publication pointer. Evaluate the value as: the current `version` value. |
| L289 | Close the expression/container begun at L284; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L290 | Update `attempts` in place using `1` and the Add operation; the previous target value participates in the calculation. |
| L291 | Compute the return value: the current `attempts` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `IndexService._collection(self) -> ChromaCollection`

**Arguments:** Service instance. **Returns:** Result of its configured factory. **Work:** Calls the factory each time (no collection cache), propagates `IndexWriteError`, wraps other failures as `IndexWriteError("chroma collection unavailable: ...")`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-indexservice--collection"></a>

#### Line-by-line execution

[Current source: lines 293–299](../../../../Backend/app/rag/indexing.py#L293-L299). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |

**Declared result:** `ChromaCollection`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 293 |     def _collection(self) -> ChromaCollection:
 294 |         try:
 295 |             return self._factory()
 296 |         except IndexWriteError:
 297 |             raise
 298 |         except Exception as exc:
 299 |             raise IndexWriteError(f"chroma collection unavailable: {exc}") from exc
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L293 | Define `IndexService._collection`; bind its arguments when called. The body executes only when invoked. |
| L294 | Enter the protected block; failures are matched against `IndexWriteError`, `Exception` in order. |
| L295 | Compute the return value: `self._factory()` — Create a new SQLAlchemy session from the stored factory. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L296 | Handle `IndexWriteError`; only a matching error from the associated try enters this body. |
| L297 | Re-raise the currently handled exception with its traceback; no replacement result is returned. |
| L298 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L299 | Raise `IndexWriteError(f'chroma collection unavailable: {exc}')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |

<!-- END LINE WALKTHROUGH -->
