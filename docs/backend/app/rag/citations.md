# `app/rag/citations.py`

[Source](../../../../Backend/app/rag/citations.py) · [Backend index](../../README.md)

Converts untrusted model evidence hints into source-backed citation DTOs. `RetrievedChunk` is a typing-only import, avoiding a runtime dependency cycle.

`ModelCitationLike` is a Pydantic model with required string `sentence`, required integer `page`, and optional nullable `filename=None`. Field descriptions request exact text and one-based pages, but this hint model does not itself require a nonblank sentence or positive page. Final identity and page come from matched evidence instead.

## Functions

### `refine_citations(*, retrieved_chunks: Sequence[RetrievedChunk], model_citations: Sequence[ModelCitationLike]) -> list[Citation]`

- **Arguments:** The retrieved, already-authorized evidence and structured model hints.
- **Returns:** Verified-shape citations in hint order for hints that find a matching sentence; unmatched hints are omitted. Duplicates are not deduplicated.
- **Work:** Builds matcher dictionaries containing chunk ID, text, source, and page. For each hint, calls `match_citation_to_chunk` with proposed sentence and location hints. Finds the original retrieved chunk by returned ID and creates a `Citation` whose document/version/chunk IDs, filename, and page come from that chunk, and whose text is the matched source sentence. Pydantic validates the resulting DTO.
- **Matching semantics:** [text.md](text.md) describes exact tokens, word overlap, precision, and location tie-breaks; any positive overlap can win, so refinement is a provenance match rather than an entailment proof. With duplicate chunk IDs, the first retrieved object with that ID supplies identity. It never obtains evidence from conversation history, filenames alone, or a new provider query.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-refine-citations"></a>

#### Line-by-line execution

[Current source: lines 42–87](../../../../Backend/app/rag/citations.py#L42-L87). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `retrieved_chunks` | `Sequence[RetrievedChunk]`; required; keyword-only | Caller-supplied retrieved chunks; each read, transformation, and validation is traced below. |
| `model_citations` | `Sequence[ModelCitationLike]`; required; keyword-only | Caller-supplied model citations; each read, transformation, and validation is traced below. |

**Declared result:** `list[Citation]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  42 | def refine_citations(
  43 |     *,
  44 |     retrieved_chunks: Sequence[RetrievedChunk],
  45 |     model_citations: Sequence[ModelCitationLike],
  46 | ) -> list[Citation]:
  47 |     """Refine model citations against retrieved chunks.
  48 | 
  49 |     Returns v2 citations whose identity, page, and exact supporting
  50 |     text all come from the matched chunk.  Model citations with no
  51 |     overlapping sentence in any retrieved chunk are dropped.
  52 |     """
  53 |     matching_chunks = [
  54 |         {
  55 |             "id": chunk.chunk_id,
  56 |             "text": chunk.text,
  57 |             "metadata": {
  58 |                 "source": chunk.source,
  59 |                 "page": chunk.page_number,
  60 |                 "chunk_id": chunk.chunk_id,
  61 |             },
  62 |         }
  63 |         for chunk in retrieved_chunks
  64 |     ]
  65 |     refined: list[Citation] = []
  66 |     for model_citation in model_citations:
  67 |         match = match_citation_to_chunk(
  68 |             matching_chunks,
  69 |             model_citation.sentence,
  70 |             model_citation.filename,
  71 |             model_citation.page,
  72 |         )
  73 |         if match is None:
  74 |             continue
  75 |         chunk, exact_sentence = match
  76 |         retrieved = next(c for c in retrieved_chunks if c.chunk_id == chunk["id"])
  77 |         refined.append(
  78 |             Citation(
  79 |                 document_id=retrieved.document_id,
  80 |                 file_name=retrieved.source,
  81 |                 page_number=retrieved.page_number,
  82 |                 chunk_id=retrieved.chunk_id,
  83 |                 text=exact_sentence,
  84 |                 index_version=retrieved.index_version,
  85 |             )
  86 |         )
  87 |     return refined
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L42 | Define `refine_citations`; bind its arguments when called. The body executes only when invoked. |
| L43 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L44 | Declare parameter `retrieved_chunks` with annotation `Sequence[RetrievedChunk]`. Caller-supplied retrieved chunks; its uses and transformations are traced below. |
| L45 | Declare parameter `model_citations` with annotation `Sequence[ModelCitationLike]`. Caller-supplied model citations; its uses and transformations are traced below. |
| L46 | Finish/continue the signature; the declared return annotation is `list[Citation]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L47 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L49 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L50 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L51 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L52 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L53 | Evaluate the right-hand side, then bind/store it in `matching_chunks`: iterate `retrieved_chunks`, binding each item to `chunk`; produce `{'id': chunk.chunk_id, 'text': chunk.text, 'metadata': {'source': chunk.source, 'page': chunk.page_number, 'chunk_id': chunk.chunk_id}}` into a new list. |
| L54 | Contribute build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping to the expression being assembled. |
| L55 | Add mapping entry `'id'`: the `chunk_id` attribute of `chunk`. |
| L56 | Add mapping entry `'text'`: the `text` attribute of `chunk`. |
| L57 | Add mapping entry `'metadata'`: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. |
| L58 | Add mapping entry `'source'`: the `source` attribute of `chunk`. |
| L59 | Add mapping entry `'page'`: the `page_number` attribute of `chunk`. |
| L60 | Add mapping entry `'chunk_id'`: the `chunk_id` attribute of `chunk`. |
| L61 | Close the expression/container begun at L57; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L62 | Close the expression/container begun at L54; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L63 | Contribute the current `chunk` value to the expression being assembled. |
| L64 | Close the expression/container begun at L53; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L65 | Evaluate the right-hand side, then bind/store it in `refined`: build a list containing no items. |
| L66 | Iterate `model_citations` (the current `model_citations` value), assigning each item to `model_citation`. Execute the indented body once per item; an empty iterable skips it. |
| L67 | Evaluate the right-hand side, then bind/store it in `match`: `match_citation_to_chunk(matching_chunks, model_citation.sentence, model_citation.filename, model_citation.page)` — Call [match_citation_to_chunk](text.md#walk-match-citation-to-chunk) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L68 | Supply positional argument 1 to `match_citation_to_chunk`: the current `matching_chunks` value. |
| L69 | Supply positional argument 2 to `match_citation_to_chunk`: the `sentence` attribute of `model_citation`. |
| L70 | Supply positional argument 3 to `match_citation_to_chunk`: the `filename` attribute of `model_citation`. |
| L71 | Supply positional argument 4 to `match_citation_to_chunk`: the `page` attribute of `model_citation`. |
| L72 | Close the expression/container begun at L67; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L73 | Evaluate the branch condition: compare whether `match` is the same object as `None`. If truthy, enter L74; otherwise skip this indented block and continue after it. |
| L74 | Skip the rest of this iteration and advance the innermost loop to its next item; active finally/context exits still apply. |
| L75 | Evaluate the right-hand side, then bind/store it in `(chunk, exact_sentence)`: the current `match` value. |
| L76 | Evaluate the right-hand side, then bind/store it in `retrieved`: `next((c for c in retrieved_chunks if c.chunk_id == chunk['id']))` — Consume the next iterator result, using the optional fallback on exhaustion; inputs include iterate `retrieved_chunks`, binding each item to `c` and retain only items satisfying `c.chunk_id == chunk['id']`; produce `c` into a lazy generator (items computed when consumed). |
| L77 | `refined.append` with the arguments detailed below — Append one object to the mutable list in place; inputs include `Citation` with the arguments detailed below — Construct `Citation` with the shown fields; its class/model initialization rules apply. The return value is not assigned here. |
| L78 | `Citation` with the arguments detailed below — Construct `Citation` with the shown fields; its class/model initialization rules apply. |
| L79 | Supply `document_id` = `retrieved.document_id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the `document_id` attribute of `retrieved`. |
| L80 | Supply `file_name` = `retrieved.source`. Display PDF filename; immutable IDs establish ownership and evidence identity. Evaluate the value as: the `source` attribute of `retrieved`. |
| L81 | Supply `page_number` = `retrieved.page_number`.  Evaluate the value as: the `page_number` attribute of `retrieved`. |
| L82 | Supply `chunk_id` = `retrieved.chunk_id`.  Evaluate the value as: the `chunk_id` attribute of `retrieved`. |
| L83 | Supply `text` = `exact_sentence`. Text to split, hash, normalize, or embed as shown by this function's body. Evaluate the value as: the current `exact_sentence` value. |
| L84 | Supply `index_version` = `retrieved.index_version`. UUID of one document's vector-index namespace, separate from its active publication pointer. Evaluate the value as: the `index_version` attribute of `retrieved`. |
| L85 | Close the expression/container begun at L78; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L86 | Close the expression/container begun at L77; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L87 | Compute the return value: the current `refined` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
