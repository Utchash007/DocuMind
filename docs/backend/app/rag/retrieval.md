# `app/rag/retrieval.py`

[Source](../../../../Backend/app/rag/retrieval.py) · [Backend index](../../README.md)

Scoped hybrid search over `documind_chunks_v2`. `BEST_N=4`; `DENSE_CANDIDATES=10`. `Embedder` accepts text sequences and returns ordered vectors. `NoReadySourcesError` and `IndexUnavailableError` are marker exceptions without local methods, translated by message routes to 409 and 503 respectively.

Frozen dataclass `RetrievedChunk` carries chunk ID/text/page/source and UUID document/version/user/project identities. Its constructor is generated; it does not perform Pydantic validation. The row conversion below supplies the checked values.

## Functions

### `get_chroma_collection()`

**Arguments:** None. **Returns:** Canonical Chroma collection. **Work:** Lazily imports/calls `indexing.default_chroma_collection`, which may contact/create the collection. There is no collection cache in this wrapper.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-chroma-collection"></a>

#### Line-by-line execution

[Current source: lines 70–74](../../../../Backend/app/rag/retrieval.py#L70-L74). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** No return annotation; follow the return/yield lines below. Python supplies None when a non-generator reaches the end without return.

**Numbered source**

```text
  70 | def get_chroma_collection():
  71 |     """Resolve the canonical v2 collection lazily; tests inject a double."""
  72 |     from app.rag.indexing import default_chroma_collection
  73 | 
  74 |     return default_chroma_collection()
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L70 | Define `get_chroma_collection`; bind its arguments when called. The body executes only when invoked. |
| L71 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L72 | Import `default_chroma_collection` from `app.rag.indexing`; inside a function this import is deferred until this path is reached. |
| L74 | Compute the return value: `default_chroma_collection()` — Call [default_chroma_collection](indexing.md#walk-default-chroma-collection) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `default_embedder(texts: Sequence[str]) -> list[list[float]]`

**Arguments:** Ordered query texts. **Returns:** Configured-provider vectors. **Work:** Builds `EmbeddingConfig.from_env()` and `EmbeddingService`, materializes the texts, then calls `embed_texts(..., task="retrieval.query")`. Jina uses its query adapter; HF ignores that hint. Mock vectors require the explicit environment opt-in read by the config.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-default-embedder"></a>

#### Line-by-line execution

[Current source: lines 77–87](../../../../Backend/app/rag/retrieval.py#L77-L87). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `texts` | `Sequence[str]`; required; positional or keyword | Input text sequence; embedding output preserves its order. |

**Declared result:** `list[list[float]]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  77 | def default_embedder(texts: Sequence[str]) -> list[list[float]]:
  78 |     """Embed queries with the configured provider, without silent fallback."""
  79 |     from app.rag.embeddings import (
  80 |         TASK_RETRIEVAL_QUERY,
  81 |         EmbeddingConfig,
  82 |         EmbeddingService,
  83 |     )
  84 | 
  85 |     return EmbeddingService(EmbeddingConfig.from_env()).embed_texts(
  86 |         list(texts), task=TASK_RETRIEVAL_QUERY
  87 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L77 | Define `default_embedder`; bind its arguments when called. The body executes only when invoked. |
| L78 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L79 | Import `TASK_RETRIEVAL_QUERY`, `EmbeddingConfig`, `EmbeddingService` from `app.rag.embeddings`; inside a function this import is deferred until this path is reached. |
| L80 | Continue the operation begun at L79: Import `TASK_RETRIEVAL_QUERY`, `EmbeddingConfig`, `EmbeddingService` from `app.rag.embeddings`; inside a function this import is deferred until this path is reached. |
| L81 | Continue the operation begun at L79: Import `TASK_RETRIEVAL_QUERY`, `EmbeddingConfig`, `EmbeddingService` from `app.rag.embeddings`; inside a function this import is deferred until this path is reached. |
| L82 | Continue the operation begun at L79: Import `TASK_RETRIEVAL_QUERY`, `EmbeddingConfig`, `EmbeddingService` from `app.rag.embeddings`; inside a function this import is deferred until this path is reached. |
| L83 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L85 | Compute the return value: `EmbeddingService(EmbeddingConfig.from_env()).embed_texts(list(texts), task=TASK_RETRIEVAL_QUERY)` — Embed input texts in order using the selected provider/configuration; configured mock mode substitutes deterministic vectors; first obtain the receiver: `EmbeddingService(EmbeddingConfig.from_env())` — Construct `EmbeddingService` with the shown fields; its class/model initialization rules apply; inputs include `list(texts)` — Materialize the iterable in order into a list (or create an empty list). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L86 | `list(texts)` — Materialize the iterable in order into a list (or create an empty list). |
| L87 | Close the expression/container begun at L85; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `build_retrieval_where(*, user_id: UUID, project_id: UUID, authorized_sources) -> dict[str, Any]`

- **Arguments:** Verified internal owner/project IDs and `AuthorizedSource` sequence.
- **Returns:** One fully scoped `$and` clause for one pair, or `$or` of such clauses for several pairs.
- **Work:** Deduplicates and lexically sorts string `(document_id, index_version)` pairs, rejects an empty set with `NoReadySourcesError`, and calls `version_where` with owner/project plus each correlated pair. Independent document/version lists are never combined. Type annotations expect owner/project UUIDs; this function does not separately runtime-validate their presence.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-build-retrieval-where"></a>

#### Line-by-line execution

[Current source: lines 90–119](../../../../Backend/app/rag/retrieval.py#L90-L119). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `authorized_sources` | `Sequence[AuthorizedSource]`; required; keyword-only | Exact authorized document/version pairs; these bound the evidence search. |

**Declared result:** `dict[str, Any]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  90 | def build_retrieval_where(
  91 |     *,
  92 |     user_id: UUID,
  93 |     project_id: UUID,
  94 |     authorized_sources: Sequence[AuthorizedSource],
  95 | ) -> dict[str, Any]:
  96 |     """Build the Chroma ``where`` filter for an exact authorized pair set.
  97 | 
  98 |     Each permitted pair compiles to one ``$and`` clause (via
  99 |     :func:`version_where` — document and version correlated per
 100 |     clause, never emitted as independent lists); several pairs compile
 101 |     to an ``$or`` of those clauses.
 102 |     """
 103 |     pairs = sorted(
 104 |         {(str(source.document_id), str(source.index_version)) for source in authorized_sources}
 105 |     )
 106 |     if not pairs:
 107 |         raise NoReadySourcesError(
 108 |             "No completed documents are available to answer this question."
 109 |         )
 110 |     clauses = [
 111 |         version_where(
 112 |             user_id=user_id,
 113 |             project_id=project_id,
 114 |             document_id=document_id,
 115 |             index_version=index_version,
 116 |         )
 117 |         for document_id, index_version in pairs
 118 |     ]
 119 |     return clauses[0] if len(clauses) == 1 else {"$or": clauses}
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L90 | Define `build_retrieval_where`; bind its arguments when called. The body executes only when invoked. |
| L91 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L92 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L93 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L94 | Declare parameter `authorized_sources` with annotation `Sequence[AuthorizedSource]`. Exact authorized document/version pairs; these bound the evidence search. |
| L95 | Finish/continue the signature; the declared return annotation is `dict[str, Any]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L96 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L98 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L99 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L100 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L101 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L102 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L103 | Evaluate the right-hand side, then bind/store it in `pairs`: `sorted({(str(source.document_id), str(source.index_version)) for source in authorized_sources})` — Create a sorted list using the supplied key/reverse options; equal keys retain input order. |
| L104 | Convert the input to its string representation. |
| L105 | Close the expression/container begun at L103; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L106 | Evaluate the branch condition: invert the truthiness of `pairs`. If truthy, enter L107; otherwise skip this indented block and continue after it. |
| L107 | Raise `NoReadySourcesError('No completed documents are available to answer this question.')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L108 | Supply positional argument 1 to `NoReadySourcesError`: `'No completed documents are available to answer this question.'`. |
| L109 | Close the expression/container begun at L107; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L110 | Evaluate the right-hand side, then bind/store it in `clauses`: iterate `pairs`, binding each item to `(document_id, index_version)`; produce `version_where(user_id=user_id, project_id=project_id, document_id=document_id, index_version=index_version)` into a new list. |
| L111 | `version_where(user_id=user_id, project_id=project_id, document_id=document_id, index_version=index_version)` — Call [version_where](indexing.md#walk-version-where) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L112 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L113 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L114 | Supply `document_id` = `document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `document_id` value. |
| L115 | Supply `index_version` = `index_version`. UUID of one document's vector-index namespace, separate from its active publication pointer. Evaluate the value as: the current `index_version` value. |
| L116 | Close the expression/container begun at L111; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L117 | Contribute build a tuple containing `document_id`, `index_version` to the expression being assembled. |
| L118 | Close the expression/container begun at L110; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L119 | Compute the return value: check `len(clauses) == 1`; when true use look up index/key `0` in `clauses`; a missing key or out-of-range index raises, otherwise build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping (only the selected branch is evaluated). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_chunk_from_row(*, chunk_id, text, metadata, allowed_pairs, user_id, project_id) -> RetrievedChunk | None`

- **Arguments:** Provider row ID/text/metadata, allowed UUID pairs, expected owner/project UUIDs.
- **Returns:** Validated immutable chunk or `None` for a rejected row.
- **Work:** Requires truthy row ID/text/metadata, parses four metadata UUIDs, integer page, source string, and metadata chunk-ID string. Rejects parse failures, foreign owner/project, unauthorized exact pair, empty source/chunk ID, and page <1. Uses the **metadata** chunk ID in the returned object; the separate provider row ID is checked for presence but not equality. It does not verify the canonical encoded-ID format, strip the text/source, or derive ownership from filenames.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--chunk-from-row"></a>

#### Line-by-line execution

[Current source: lines 122–165](../../../../Backend/app/rag/retrieval.py#L122-L165). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `chunk_id` | `str \| None`; required; keyword-only | Caller-supplied chunk id; each read, transformation, and validation is traced below. |
| `text` | `str \| None`; required; keyword-only | Text to split, hash, normalize, or embed as shown by this function's body. |
| `metadata` | `dict[str, Any] \| None`; required; keyword-only | Caller-supplied metadata; each read, transformation, and validation is traced below. |
| `allowed_pairs` | `set[tuple[UUID, UUID]]`; required; keyword-only | Caller-supplied allowed pairs; each read, transformation, and validation is traced below. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |

**Declared result:** `RetrievedChunk | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 122 | def _chunk_from_row(
 123 |     *,
 124 |     chunk_id: str | None,
 125 |     text: str | None,
 126 |     metadata: dict[str, Any] | None,
 127 |     allowed_pairs: set[tuple[UUID, UUID]],
 128 |     user_id: UUID,
 129 |     project_id: UUID,
 130 | ) -> RetrievedChunk | None:
 131 |     """Validate one corpus row against the authorized pairs.
 132 | 
 133 |     Returns ``None`` for rows with missing metadata or for rows outside
 134 |     the authorized (document, version) pairs — including cross-pairings
 135 |     (a document paired with another document's version) and foreign
 136 |     user/project rows that a broken filter might admit.
 137 |     """
 138 |     if not chunk_id or not text or not metadata:
 139 |         return None
 140 |     try:
 141 |         row_user = UUID(str(metadata["user_id"]))
 142 |         row_project = UUID(str(metadata["project_id"]))
 143 |         row_document = UUID(str(metadata["document_id"]))
 144 |         row_version = UUID(str(metadata["index_version"]))
 145 |         page_number = int(metadata["page"])
 146 |         source = str(metadata["source"])
 147 |         metadata_chunk_id = str(metadata["chunk_id"])
 148 |     except (KeyError, TypeError, ValueError):
 149 |         return None
 150 |     if row_user != user_id or row_project != project_id:
 151 |         return None
 152 |     if (row_document, row_version) not in allowed_pairs:
 153 |         return None
 154 |     if not source or not metadata_chunk_id or page_number < 1:
 155 |         return None
 156 |     return RetrievedChunk(
 157 |         chunk_id=metadata_chunk_id,
 158 |         text=text,
 159 |         page_number=page_number,
 160 |         source=source,
 161 |         document_id=row_document,
 162 |         index_version=row_version,
 163 |         user_id=row_user,
 164 |         project_id=row_project,
 165 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L122 | Define `_chunk_from_row`; bind its arguments when called. The body executes only when invoked. |
| L123 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L124 | Declare parameter `chunk_id` with annotation `str \| None`. Caller-supplied chunk id; its uses and transformations are traced below. |
| L125 | Declare parameter `text` with annotation `str \| None`. Text to split, hash, normalize, or embed as shown by this function's body. |
| L126 | Declare parameter `metadata` with annotation `dict[str, Any] \| None`. Caller-supplied metadata; its uses and transformations are traced below. |
| L127 | Declare parameter `allowed_pairs` with annotation `set[tuple[UUID, UUID]]`. Caller-supplied allowed pairs; its uses and transformations are traced below. |
| L128 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L129 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L130 | Finish/continue the signature; the declared return annotation is `RetrievedChunk \| None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L131 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L133 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L134 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L135 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L136 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L137 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L138 | Evaluate the branch condition: evaluate `not chunk_id or not text or (not metadata)` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L139; otherwise skip this indented block and continue after it. |
| L139 | Compute the return value: None (no value). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L140 | Enter the protected block; failures are matched against `(KeyError, TypeError, ValueError)` in order. |
| L141 | Evaluate the right-hand side, then bind/store it in `row_user`: `UUID(str(metadata['user_id']))` — Parse or construct a UUID; invalid text raises a conversion error; inputs include `str(metadata['user_id'])` — Convert the input to its string representation. |
| L142 | Evaluate the right-hand side, then bind/store it in `row_project`: `UUID(str(metadata['project_id']))` — Parse or construct a UUID; invalid text raises a conversion error; inputs include `str(metadata['project_id'])` — Convert the input to its string representation. |
| L143 | Evaluate the right-hand side, then bind/store it in `row_document`: `UUID(str(metadata['document_id']))` — Parse or construct a UUID; invalid text raises a conversion error; inputs include `str(metadata['document_id'])` — Convert the input to its string representation. |
| L144 | Evaluate the right-hand side, then bind/store it in `row_version`: `UUID(str(metadata['index_version']))` — Parse or construct a UUID; invalid text raises a conversion error; inputs include `str(metadata['index_version'])` — Convert the input to its string representation. |
| L145 | Evaluate the right-hand side, then bind/store it in `page_number`: `int(metadata['page'])` — Convert the input to an integer (using the optional numeric base). |
| L146 | Evaluate the right-hand side, then bind/store it in `source`: `str(metadata['source'])` — Convert the input to its string representation. |
| L147 | Evaluate the right-hand side, then bind/store it in `metadata_chunk_id`: `str(metadata['chunk_id'])` — Convert the input to its string representation. |
| L148 | Handle `(KeyError, TypeError, ValueError)`; only a matching error from the associated try enters this body. |
| L149 | Compute the return value: None (no value). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L150 | Evaluate the branch condition: evaluate `row_user != user_id or row_project != project_id` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L151; otherwise skip this indented block and continue after it. |
| L151 | Compute the return value: None (no value). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L152 | Evaluate the branch condition: compare whether `(row_document, row_version)` is absent from `allowed_pairs`. If truthy, enter L153; otherwise skip this indented block and continue after it. |
| L153 | Compute the return value: None (no value). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L154 | Evaluate the branch condition: evaluate `not source or not metadata_chunk_id or page_number < 1` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L155; otherwise skip this indented block and continue after it. |
| L155 | Compute the return value: None (no value). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L156 | Compute the return value: `RetrievedChunk` with the arguments detailed below — Construct `RetrievedChunk` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L157 | Supply `chunk_id` = `metadata_chunk_id`.  Evaluate the value as: the current `metadata_chunk_id` value. |
| L158 | Supply `text` = `text`. Text to split, hash, normalize, or embed as shown by this function's body. Evaluate the value as: the current `text` value. |
| L159 | Supply `page_number` = `page_number`.  Evaluate the value as: the current `page_number` value. |
| L160 | Supply `source` = `source`.  Evaluate the value as: the current `source` value. |
| L161 | Supply `document_id` = `row_document`. Document UUID; filenames do not establish document identity. Evaluate the value as: the current `row_document` value. |
| L162 | Supply `index_version` = `row_version`. UUID of one document's vector-index namespace, separate from its active publication pointer. Evaluate the value as: the current `row_version` value. |
| L163 | Supply `user_id` = `row_user`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `row_user` value. |
| L164 | Supply `project_id` = `row_project`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `row_project` value. |
| L165 | Close the expression/container begun at L156; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `merge_hybrid_scores(*, chunks, bm25_scores: dict[str, float], dense_scores: dict[str, float]) -> list[tuple[RetrievedChunk, float]]`

**Arguments:** Validated chunks, raw sparse scores, dense similarities keyed by chunk ID. **Returns:** All `(chunk, combined_score)` pairs sorted best-first. **Work:** Normalizes BM25 by its maximum when positive, otherwise uses zero; missing branch scores are zero. Combines `0.5 * dense + 0.5 * sparse`, then stable-sorts descending. Does not limit result count or convert distances itself.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-merge-hybrid-scores"></a>

#### Line-by-line execution

[Current source: lines 168–190](../../../../Backend/app/rag/retrieval.py#L168-L190). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `chunks` | `Sequence[RetrievedChunk]`; required; keyword-only | PDF text chunks with the metadata required by this operation. |
| `bm25_scores` | `dict[str, float]`; required; keyword-only | Caller-supplied bm25 scores; each read, transformation, and validation is traced below. |
| `dense_scores` | `dict[str, float]`; required; keyword-only | Caller-supplied dense scores; each read, transformation, and validation is traced below. |

**Declared result:** `list[tuple[RetrievedChunk, float]]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 168 | def merge_hybrid_scores(
 169 |     *,
 170 |     chunks: Sequence[RetrievedChunk],
 171 |     bm25_scores: dict[str, float],
 172 |     dense_scores: dict[str, float],
 173 | ) -> list[tuple[RetrievedChunk, float]]:
 174 |     """Rank chunks with the preserved 0.5/0.5 hybrid merger (best first).
 175 | 
 176 |     ``bm25_scores`` are normalized by their maximum (zero when the
 177 |     maximum is not positive); ``dense_scores`` carry the
 178 |     ``1 / (1 + distance)`` similarity (missing candidates score zero).
 179 |     """
 180 |     max_bm25 = max(bm25_scores.values()) if bm25_scores else 1.0
 181 |     scored: list[tuple[RetrievedChunk, float]] = []
 182 |     for chunk in chunks:
 183 |         dense_sim = dense_scores.get(chunk.chunk_id, 0.0)
 184 |         sparse_sim = (
 185 |             bm25_scores.get(chunk.chunk_id, 0.0) / max_bm25 if max_bm25 > 0 else 0.0
 186 |         )
 187 |         combined = 0.5 * dense_sim + 0.5 * sparse_sim
 188 |         scored.append((chunk, combined))
 189 |     scored.sort(key=lambda item: item[1], reverse=True)
 190 |     return scored
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L168 | Define `merge_hybrid_scores`; bind its arguments when called. The body executes only when invoked. |
| L169 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L170 | Declare parameter `chunks` with annotation `Sequence[RetrievedChunk]`. PDF text chunks with the metadata required by this operation. |
| L171 | Declare parameter `bm25_scores` with annotation `dict[str, float]`. Caller-supplied bm25 scores; its uses and transformations are traced below. |
| L172 | Declare parameter `dense_scores` with annotation `dict[str, float]`. Caller-supplied dense scores; its uses and transformations are traced below. |
| L173 | Finish/continue the signature; the declared return annotation is `list[tuple[RetrievedChunk, float]]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L174 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L176 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L177 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L178 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L179 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L180 | Evaluate the right-hand side, then bind/store it in `max_bm25`: check `bm25_scores`; when true use `max(bm25_scores.values())` — Choose the largest supplied value; nested min/max calls implement the stated bound, otherwise `1.0` (only the selected branch is evaluated). |
| L181 | Evaluate the right-hand side, then bind/store it in `scored`: build a list containing no items. |
| L182 | Iterate `chunks` (the current `chunks` value), assigning each item to `chunk`. Execute the indented body once per item; an empty iterable skips it. |
| L183 | Evaluate the right-hand side, then bind/store it in `dense_sim`: `dense_scores.get(chunk.chunk_id, 0.0)` — Look up `chunk.chunk_id` in `dense_scores`, using `0.0` when the key is absent (an existing null value is not replaced). |
| L184 | Evaluate the right-hand side, then bind/store it in `sparse_sim`: check `max_bm25 > 0`; when true use divide `bm25_scores.get(chunk.chunk_id, 0.0)` and `max_bm25`, following the parentheses/operator precedence shown in `bm25_scores.get(chunk.chunk_id, 0.0) / max_bm25`, otherwise `0.0` (only the selected branch is evaluated). |
| L185 | `bm25_scores.get(chunk.chunk_id, 0.0)` — Look up `chunk.chunk_id` in `bm25_scores`, using `0.0` when the key is absent (an existing null value is not replaced). |
| L186 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L187 | Evaluate the right-hand side, then bind/store it in `combined`: add/concatenate `0.5 * dense_sim` and `0.5 * sparse_sim`, following the parentheses/operator precedence shown in `0.5 * dense_sim + 0.5 * sparse_sim`. |
| L188 | `scored.append((chunk, combined))` — Append one object to the mutable list in place. The return value is not assigned here. |
| L189 | `scored.sort(key=lambda item: item[1], reverse=True)` — Invoke `scored.sort` with the shown inputs and use its result; see the function overview for its role in this flow. The return value is not assigned here. |
| L190 | Compute the return value: the current `scored` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_is_embedding_provider_error(exc: BaseException) -> bool`

**Arguments:** Caught error. **Returns:** Whether it is `EmbeddingProviderError`. **Work:** Imports the type lazily, returns false if that import fails, otherwise uses `isinstance`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--is-embedding-provider-error"></a>

#### Line-by-line execution

[Current source: lines 193–199](../../../../Backend/app/rag/retrieval.py#L193-L199). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `exc` | `BaseException`; required; positional or keyword | Caller-supplied exc; each read, transformation, and validation is traced below. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 193 | def _is_embedding_provider_error(exc: BaseException) -> bool:
 194 |     """True when ``exc`` is A4's embedding-provider failure type."""
 195 |     try:
 196 |         from app.rag.embeddings import EmbeddingProviderError
 197 |     except ImportError:
 198 |         return False
 199 |     return isinstance(exc, EmbeddingProviderError)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L193 | Define `_is_embedding_provider_error`; bind its arguments when called. The body executes only when invoked. |
| L194 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L195 | Enter the protected block; failures are matched against `ImportError` in order. |
| L196 | Import `EmbeddingProviderError` from `app.rag.embeddings`; inside a function this import is deferred until this path is reached. |
| L197 | Handle `ImportError`; only a matching error from the associated try enters this body. |
| L198 | Compute the return value: `False`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L199 | Compute the return value: `isinstance(exc, EmbeddingProviderError)` — Check the runtime type against the supplied class or tuple of classes. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_embed_query(embedder: Embedder, question: str) -> list[float]`

**Arguments:** Embedding callable and question. **Returns:** First vector from `embedder([question])`. **Work:** Converts recognized embedding-provider failures into `IndexUnavailableError` with their cause. Other errors, including an empty/malformed injected result, propagate unchanged; vector validation is the embedder's job.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--embed-query"></a>

#### Line-by-line execution

[Current source: lines 202–211](../../../../Backend/app/rag/retrieval.py#L202-L211). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `embedder` | `Embedder`; required; positional or keyword | Embedding collaborator; the function selects its default only where explicitly shown. |
| `question` | `str`; required; positional or keyword | Current user question, separate from historical messages and PDF evidence. |

**Declared result:** `list[float]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 202 | def _embed_query(embedder: Embedder, question: str) -> list[float]:
 203 |     """Embed the query, mapping provider outages to 503 (retryable)."""
 204 |     try:
 205 |         return embedder([question])[0]
 206 |     except Exception as exc:
 207 |         if _is_embedding_provider_error(exc):
 208 |             raise IndexUnavailableError(
 209 |                 f"embedding provider unavailable: {exc}"
 210 |             ) from exc
 211 |         raise
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L202 | Define `_embed_query`; bind its arguments when called. The body executes only when invoked. |
| L203 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L204 | Enter the protected block; failures are matched against `Exception` in order. |
| L205 | Compute the return value: look up index/key `0` in `embedder([question])`; a missing key or out-of-range index raises. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L206 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L207 | Evaluate the branch condition: `_is_embedding_provider_error(exc)` — Call [_is_embedding_provider_error](#walk--is-embedding-provider-error) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. If truthy, enter L208; otherwise skip this indented block and continue after it. |
| L208 | Raise `IndexUnavailableError(f'embedding provider unavailable: {exc}')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L209 | Supply positional argument 1 to `IndexUnavailableError`: format a string by inserting `exc` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L210 | Contribute the current `exc` value to the expression being assembled. |
| L211 | Re-raise the currently handled exception with its traceback; no replacement result is returned. |

<!-- END LINE WALKTHROUGH -->

### `retrieve_context(*, question: str, user_id: UUID, project_id: UUID, authorized_sources, collection=None, embedder=None, best_n=4) -> list[RetrievedChunk]`

- **Arguments:** Question, authenticated scope, exact authorized-source snapshot, optional collection/embedder collaborators, result slice size.
- **Returns:** Best-ranked validated chunks, normally up to four.
- **Work:** Rejects empty sources, builds one filter and allowed-pair set, resolves collaborators, and loads the scoped corpus with `collection.get(where=where)`. Zips IDs/documents/metadata (unequal arrays truncate to the shortest), validates each row, and fails with `IndexUnavailableError` if none remain. Builds a BM25 corpus from those chunks and scores the question. Embeds the question, then calls `collection.query` with the **same filter** and up to `min(10, valid_chunk_count)` dense candidates. Converts first-query distances to `1 / (1 + distance)`, merges scores, and slices `[:best_n]`.
- **Scope/error details:** Only corpus-validated chunks can appear in the result; unexpected dense IDs cannot add foreign text. Dense score entries themselves are not reparsed as chunks. Collection/query errors and malformed distance payloads are not globally wrapped here. `best_n` is used as a Python slice without positive-bound validation. Supplying missing/wrong-type owner IDs cannot match valid parsed row UUIDs; normal callers provide both explicitly. No SQL writes or prompt history are involved.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-retrieve-context"></a>

#### Line-by-line execution

[Current source: lines 214–292](../../../../Backend/app/rag/retrieval.py#L214-L292). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `question` | `str`; required; keyword-only | Current user question, separate from historical messages and PDF evidence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `authorized_sources` | `Sequence[AuthorizedSource]`; required; keyword-only | Exact authorized document/version pairs; these bound the evidence search. |
| `collection` | `Any \| None`; default `None`; keyword-only | Injected Chroma-compatible collection; null selects the default when implemented. |
| `embedder` | `Embedder \| None`; default `None`; keyword-only | Embedding collaborator; the function selects its default only where explicitly shown. |
| `best_n` | `int`; default `BEST_N`; keyword-only | Caller-supplied best n; each read, transformation, and validation is traced below. |

**Declared result:** `list[RetrievedChunk]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 214 | def retrieve_context(
 215 |     *,
 216 |     question: str,
 217 |     user_id: UUID,
 218 |     project_id: UUID,
 219 |     authorized_sources: Sequence[AuthorizedSource],
 220 |     collection: Any | None = None,
 221 |     embedder: Embedder | None = None,
 222 |     best_n: int = BEST_N,
 223 | ) -> list[RetrievedChunk]:
 224 |     """Retrieve the best ``best_n`` chunks from authorized sources.
 225 | 
 226 |     Both branches (BM25 corpus load and dense query) use the identical
 227 |     exact-pair filter from :func:`build_retrieval_where`, and every
 228 |     corpus row is re-validated against the authorized pairs before
 229 |     scoring.
 230 |     """
 231 |     if not authorized_sources:
 232 |         raise NoReadySourcesError(
 233 |             "No completed documents are available to answer this question."
 234 |         )
 235 |     where = build_retrieval_where(
 236 |         user_id=user_id,
 237 |         project_id=project_id,
 238 |         authorized_sources=authorized_sources,
 239 |     )
 240 |     allowed_pairs = {
 241 |         (source.document_id, source.index_version) for source in authorized_sources
 242 |     }
 243 |     collection = collection or get_chroma_collection()
 244 |     embedder = embedder or default_embedder
 245 | 
 246 |     data = collection.get(where=where)
 247 |     chunks: list[RetrievedChunk] = []
 248 |     for chunk_id, text, metadata in zip(
 249 |         data.get("ids") or [],
 250 |         data.get("documents") or [],
 251 |         data.get("metadatas") or [],
 252 |     ):
 253 |         chunk = _chunk_from_row(
 254 |             chunk_id=chunk_id,
 255 |             text=text,
 256 |             metadata=metadata,
 257 |             allowed_pairs=allowed_pairs,
 258 |             user_id=user_id,
 259 |             project_id=project_id,
 260 |         )
 261 |         if chunk is not None:
 262 |             chunks.append(chunk)
 263 |     if not chunks:
 264 |         raise IndexUnavailableError(
 265 |             "Retrieved no content from the authorized sources yet. "
 266 |             "Please retry shortly."
 267 |         )
 268 | 
 269 |     corpus = [
 270 |         {"id": chunk.chunk_id, "text": chunk.text, "metadata": {"source": chunk.source, "page": chunk.page_number, "chunk_id": chunk.chunk_id}}
 271 |         for chunk in chunks
 272 |     ]
 273 |     bm25 = BM25Retriever(corpus)
 274 |     bm25_scores = bm25.get_scores(question)
 275 | 
 276 |     query_vector = _embed_query(embedder, question)
 277 |     vector_results = collection.query(
 278 |         query_embeddings=[query_vector],
 279 |         n_results=min(DENSE_CANDIDATES, len(chunks)),
 280 |         where=where,
 281 |     )
 282 |     dense_scores: dict[str, float] = {}
 283 |     if vector_results and vector_results.get("ids"):
 284 |         for identifier, distance in zip(
 285 |             vector_results["ids"][0], vector_results["distances"][0]
 286 |         ):
 287 |             dense_scores[identifier] = 1.0 / (1.0 + distance)
 288 | 
 289 |     scored = merge_hybrid_scores(
 290 |         chunks=chunks, bm25_scores=bm25_scores, dense_scores=dense_scores
 291 |     )
 292 |     return [chunk for chunk, _score in scored[:best_n]]
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L214 | Define `retrieve_context`; bind its arguments when called. The body executes only when invoked. |
| L215 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L216 | Declare parameter `question` with annotation `str`. Current user question, separate from historical messages and PDF evidence. |
| L217 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L218 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L219 | Declare parameter `authorized_sources` with annotation `Sequence[AuthorizedSource]`. Exact authorized document/version pairs; these bound the evidence search. |
| L220 | Declare parameter `collection` with annotation `Any \| None`. Injected Chroma-compatible collection; null selects the default when implemented. |
| L221 | Declare parameter `embedder` with annotation `Embedder \| None`. Embedding collaborator; the function selects its default only where explicitly shown. |
| L222 | Declare parameter `best_n` with annotation `int`. Caller-supplied best n; its uses and transformations are traced below. |
| L223 | Finish/continue the signature; the declared return annotation is `list[RetrievedChunk]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L224 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L226 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L227 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L228 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L229 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L230 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L231 | Evaluate the branch condition: invert the truthiness of `authorized_sources`. If truthy, enter L232; otherwise skip this indented block and continue after it. |
| L232 | Raise `NoReadySourcesError('No completed documents are available to answer this question.')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L233 | Supply positional argument 1 to `NoReadySourcesError`: `'No completed documents are available to answer this question.'`. |
| L234 | Close the expression/container begun at L232; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L235 | Evaluate the right-hand side, then bind/store it in `where`: `build_retrieval_where(user_id=user_id, project_id=project_id, authorized_sources=authorized_sources)` — Call [build_retrieval_where](#walk-build-retrieval-where) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L236 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L237 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L238 | Supply `authorized_sources` = `authorized_sources`. Exact authorized document/version pairs; these bound the evidence search. Evaluate the value as: the current `authorized_sources` value. |
| L239 | Close the expression/container begun at L235; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L240 | Evaluate the right-hand side, then bind/store it in `allowed_pairs`: iterate `authorized_sources`, binding each item to `source`; produce `(source.document_id, source.index_version)` into a set of unique values. |
| L241 | Contribute build a tuple containing `source.document_id`, `source.index_version` to the expression being assembled. |
| L242 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L243 | Evaluate the right-hand side, then bind/store it in `collection`: evaluate `collection or get_chroma_collection()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L244 | Evaluate the right-hand side, then bind/store it in `embedder`: evaluate `embedder or default_embedder` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L246 | Evaluate the right-hand side, then bind/store it in `data`: `collection.get(where=where)` — Load Chroma records matching the supplied exact metadata filter and requested fields. |
| L247 | Evaluate the right-hand side, then bind/store it in `chunks`: build a list containing no items. |
| L248 | Iterate `zip(data.get('ids') or [], data.get('documents') or [], data.get('metadatas') or [])` (`zip(data.get('ids') or [], data.get('documents') or [], data.get('metadatas') or [])` — Pair corresponding iterable items in order; ordinary zip stops at the shortest input), assigning each item to `(chunk_id, text, metadata)`. Execute the indented body once per item; an empty iterable skips it. |
| L249 | `data.get('ids')` — Look up `'ids'` in `data`, using None when the key is absent (an existing null value is not replaced). |
| L250 | `data.get('documents')` — Look up `'documents'` in `data`, using None when the key is absent (an existing null value is not replaced). |
| L251 | `data.get('metadatas')` — Look up `'metadatas'` in `data`, using None when the key is absent (an existing null value is not replaced). |
| L252 | Close the expression/container begun at L248; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L253 | Evaluate the right-hand side, then bind/store it in `chunk`: `_chunk_from_row(chunk_id=chunk_id, text=text, metadata=metadata, allowed_pairs=allowed_pairs, user_id=user_id, project_id=project_id)` — Call [_chunk_from_row](#walk--chunk-from-row) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L254 | Supply `chunk_id` = `chunk_id`.  Evaluate the value as: the current `chunk_id` value. |
| L255 | Supply `text` = `text`. Text to split, hash, normalize, or embed as shown by this function's body. Evaluate the value as: the current `text` value. |
| L256 | Supply `metadata` = `metadata`.  Evaluate the value as: the current `metadata` value. |
| L257 | Supply `allowed_pairs` = `allowed_pairs`.  Evaluate the value as: the current `allowed_pairs` value. |
| L258 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L259 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L260 | Close the expression/container begun at L253; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L261 | Evaluate the branch condition: compare whether `chunk` is not the same object as `None`. If truthy, enter L262; otherwise skip this indented block and continue after it. |
| L262 | `chunks.append(chunk)` — Append one object to the mutable list in place. The return value is not assigned here. |
| L263 | Evaluate the branch condition: invert the truthiness of `chunks`. If truthy, enter L264; otherwise skip this indented block and continue after it. |
| L264 | Raise `IndexUnavailableError('Retrieved no content from the authorized sources yet. Please retry shortly.')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L265 | Supply positional argument 1 to `IndexUnavailableError`: `'Retrieved no content from the authorized sources yet. Please retry shortly.'`. |
| L266 | Supply positional argument 1 to `IndexUnavailableError`: `'Retrieved no content from the authorized sources yet. Please retry shortly.'`. |
| L267 | Close the expression/container begun at L264; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L269 | Evaluate the right-hand side, then bind/store it in `corpus`: iterate `chunks`, binding each item to `chunk`; produce `{'id': chunk.chunk_id, 'text': chunk.text, 'metadata': {'source': chunk.source, 'page': chunk.page_number, 'chunk_id': chunk.chunk_id}}` into a new list. |
| L270 | Add mapping entry `'id'`: the `chunk_id` attribute of `chunk`. Add mapping entry `'text'`: the `text` attribute of `chunk`. Add mapping entry `'metadata'`: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. |
| L271 | Contribute the current `chunk` value to the expression being assembled. |
| L272 | Close the expression/container begun at L269; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L273 | Evaluate the right-hand side, then bind/store it in `bm25`: `BM25Retriever(corpus)` — Construct `BM25Retriever` with the shown fields; its class/model initialization rules apply. |
| L274 | Evaluate the right-hand side, then bind/store it in `bm25_scores`: `bm25.get_scores(question)` — Invoke `bm25.get_scores` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L276 | Evaluate the right-hand side, then bind/store it in `query_vector`: `_embed_query(embedder, question)` — Call [_embed_query](#walk--embed-query) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L277 | Evaluate the right-hand side, then bind/store it in `vector_results`: `collection.query(query_embeddings=[query_vector], n_results=min(DENSE_CANDIDATES, len(chunks)), where=where)` — Run a dense Chroma nearest-neighbor query using the supplied vectors, exact metadata filter, and requested result fields. |
| L278 | Supply `query_embeddings` = `[query_vector]`.  Evaluate the value as: build a list containing `query_vector`. |
| L279 | Supply `n_results` = `min(DENSE_CANDIDATES, len(chunks))`.  Evaluate the value as: `min(DENSE_CANDIDATES, len(chunks))` — Choose the smallest supplied value; nested min/max calls implement the stated bound; inputs include `len(chunks)` — Count the items/characters in the supplied container/string. |
| L280 | Supply `where` = `where`.  Evaluate the value as: the current `where` value. |
| L281 | Close the expression/container begun at L277; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L282 | Evaluate the right-hand side, then bind/store it in `dense_scores`: create an empty dictionary. |
| L283 | Evaluate the branch condition: evaluate `vector_results and vector_results.get('ids')` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L284; otherwise skip this indented block and continue after it. |
| L284 | Iterate `zip(vector_results['ids'][0], vector_results['distances'][0])` (`zip(vector_results['ids'][0], vector_results['distances'][0])` — Pair corresponding iterable items in order; ordinary zip stops at the shortest input), assigning each item to `(identifier, distance)`. Execute the indented body once per item; an empty iterable skips it. |
| L285 | Supply positional argument 1 to `zip`: look up index/key `0` in `vector_results['ids']`; a missing key or out-of-range index raises. |
| L286 | Close the expression/container begun at L284; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L287 | Evaluate the right-hand side, then bind/store it in `dense_scores[identifier]`: divide `1.0` and `1.0 + distance`, following the parentheses/operator precedence shown in `1.0 / (1.0 + distance)`. |
| L289 | Evaluate the right-hand side, then bind/store it in `scored`: `merge_hybrid_scores(chunks=chunks, bm25_scores=bm25_scores, dense_scores=dense_scores)` — Call [merge_hybrid_scores](#walk-merge-hybrid-scores) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L290 | Supply `chunks` = `chunks`. PDF text chunks with the metadata required by this operation. Evaluate the value as: the current `chunks` value. Supply `bm25_scores` = `bm25_scores`.  Evaluate the value as: the current `bm25_scores` value. Supply `dense_scores` = `dense_scores`.  Evaluate the value as: the current `dense_scores` value. |
| L291 | Close the expression/container begun at L289; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L292 | Compute the return value: iterate `scored[:best_n]`, binding each item to `(chunk, _score)`; produce `chunk` into a new list. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
