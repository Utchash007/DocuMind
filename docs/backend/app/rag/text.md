# `app/rag/text.py`

[Source](../../../../Backend/app/rag/text.py) · [Backend index](../../README.md)

Pure sentence, BM25, and citation-matching utilities. They do not authenticate sources or call external services; callers supply already-scoped chunks.

## Functions

### `split_into_sentences(text: str) -> list[str]`

**Arguments:** Text to segment. **Returns:** Trimmed, nonempty segments. **Work:** Splits with `(?<=[.!?])\s+`, retaining punctuation before the whitespace. This is a punctuation heuristic, not an abbreviation-aware language parser; text without matching boundaries stays one segment.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-split-into-sentences"></a>

#### Line-by-line execution

[Current source: lines 8–10](../../../../Backend/app/rag/text.py#L8-L10). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `text` | `str`; required; positional or keyword | Text to split, hash, normalize, or embed as shown by this function's body. |

**Declared result:** `list[str]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
   8 | def split_into_sentences(text: str) -> list[str]:
   9 |     sentences = re.split(r'(?<=[.!?])\s+', text)
  10 |     return [s.strip() for s in sentences if s.strip()]
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L8 | Define `split_into_sentences`; bind its arguments when called. The body executes only when invoked. |
| L9 | Split only on whitespace immediately following '.', '!', or '?'. The positive lookbehind retains the punctuation in the previous sentence; abbreviations are not specially recognized. |
| L10 | Compute the return value: iterate `sentences`, binding each item to `s` and retain only items satisfying `s.strip()`; produce `s.strip()` into a new list. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `BM25Retriever.__init__(self, corpus: list[dict])`

- **Arguments:** Ordered chunks containing at least `text` and, for later scoring, `id`.
- **Returns:** `None`; initializes the retriever.
- **Work:** Keeps the corpus reference, records its size and average whitespace-token length (1 for an empty corpus), and builds per-document lowercase token counters, token sets, and lengths. For each distinct token computes `idf = log((N - document_frequency + 0.5) / (document_frequency + 0.5) + 1)`. Punctuation remains attached to BM25 tokens; there is no stemming or stop-word removal. Mutating the corpus afterward does not rebuild these statistics.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-bm25retriever---init--"></a>

#### Line-by-line execution

[Current source: lines 14–30](../../../../Backend/app/rag/text.py#L14-L30). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `corpus` | `list[dict]`; required; positional or keyword | Ordered chunk dictionaries; BM25 reads text now and uses chunk IDs when returning scores. |

**Declared result:** No return annotation; follow the return/yield lines below. Python supplies None when a non-generator reaches the end without return.

**Numbered source**

```text
  14 |     def __init__(self, corpus: list[dict]):
  15 |         self.corpus = corpus
  16 |         self.corpus_size = len(corpus)
  17 |         self.avg_doc_len = sum(len(c["text"].split()) for c in corpus) / self.corpus_size if self.corpus_size > 0 else 1
  18 |         self.doc_freqs = []
  19 |         self.idf = {}
  20 |         self.doc_lens = []
  21 |         words_in_docs = []
  22 |         for chunk in corpus:
  23 |             words = chunk["text"].lower().split()
  24 |             self.doc_lens.append(len(words))
  25 |             self.doc_freqs.append(Counter(words))
  26 |             words_in_docs.append(set(words))
  27 |         all_words = set(w for doc in words_in_docs for w in doc)
  28 |         for word in all_words:
  29 |             doc_count = sum(1 for doc_words in words_in_docs if word in doc_words)
  30 |             self.idf[word] = math.log((self.corpus_size - doc_count + 0.5) / (doc_count + 0.5) + 1.0)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L14 | Define `BM25Retriever.__init__`; bind its arguments when called. The body executes only when invoked. |
| L15 | Evaluate the right-hand side, then bind/store it in `self.corpus`: the current `corpus` value. |
| L16 | Evaluate the right-hand side, then bind/store it in `self.corpus_size`: `len(corpus)` — Count the items/characters in the supplied container/string. |
| L17 | For each chunk, count whitespace-separated words; sum those counts and divide by the number of chunks. An empty corpus gets average length 1, avoiding division by zero in later normalization. |
| L18 | Evaluate the right-hand side, then bind/store it in `self.doc_freqs`: build a list containing no items. |
| L19 | Evaluate the right-hand side, then bind/store it in `self.idf`: create an empty dictionary. |
| L20 | Evaluate the right-hand side, then bind/store it in `self.doc_lens`: build a list containing no items. |
| L21 | Evaluate the right-hand side, then bind/store it in `words_in_docs`: build a list containing no items. |
| L22 | Iterate `corpus` (the current `corpus` value), assigning each item to `chunk`. Execute the indented body once per item; an empty iterable skips it. |
| L23 | Evaluate the right-hand side, then bind/store it in `words`: `chunk['text'].lower().split()` — Split the string into components; without an explicit separator, runs of whitespace are collapsed; first obtain the receiver: `chunk['text'].lower()` — Return a lowercased string copy. |
| L24 | `self.doc_lens.append(len(words))` — Append one object to the mutable list in place; inputs include `len(words)` — Count the items/characters in the supplied container/string. The return value is not assigned here. |
| L25 | `self.doc_freqs.append(Counter(words))` — Append one object to the mutable list in place; inputs include `Counter(words)` — Count occurrences of each input item, retaining term frequency for BM25. The return value is not assigned here. |
| L26 | `words_in_docs.append(set(words))` — Append one object to the mutable list in place; inputs include `set(words)` — Collect unique hashable items into a set. The return value is not assigned here. |
| L27 | Evaluate the right-hand side, then bind/store it in `all_words`: `set((w for doc in words_in_docs for w in doc))` — Collect unique hashable items into a set; inputs include iterate `words_in_docs`, binding each item to `doc`; then iterate `doc`, binding each item to `w`; produce `w` into a lazy generator (items computed when consumed). |
| L28 | Iterate `all_words` (the current `all_words` value), assigning each item to `word`. Execute the indented body once per item; an empty iterable skips it. |
| L29 | Evaluate the right-hand side, then bind/store it in `doc_count`: `sum((1 for doc_words in words_in_docs if word in doc_words))` — Accumulate the generated numeric terms into one total; inputs include iterate `words_in_docs`, binding each item to `doc_words` and retain only items satisfying `word in doc_words`; produce `1` into a lazy generator (items computed when consumed). |
| L30 | Compute smoothed inverse document frequency: log(1 + (N - df + 0.5)/(df + 0.5)). Rare words receive larger weights; the 0.5 terms keep the numerator/denominator well behaved at corpus extremes. |

<!-- END LINE WALKTHROUGH -->

### `BM25Retriever.get_scores(self, query: str, k1=1.5, b=0.75) -> dict`

- **Arguments:** Question text, BM25 saturation parameter `k1`, length-normalization parameter `b`.
- **Returns:** Chunk-ID → raw float score for every corpus item, including zero scores. Duplicate IDs overwrite earlier results.
- **Work:** Lowercases/splits query tokens. For each matching token in each document, adds `idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * document_length / average_length))`. Repeated query words contribute repeatedly. No normalization/top-k selection is done here; [retrieval.md](retrieval.md) handles that. An empty corpus returns `{}`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-bm25retriever-get-scores"></a>

#### Line-by-line execution

[Current source: lines 32–46](../../../../Backend/app/rag/text.py#L32-L46). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `query` | `str`; required; positional or keyword | Question/search text whose terms are scored against PDF chunks. |
| `k1` | not annotated; default `1.5`; positional or keyword | BM25 term-frequency saturation constant; larger values delay saturation. |
| `b` | not annotated; default `0.75`; positional or keyword | BM25 document-length normalization weight (default 0.75). |

**Declared result:** `dict`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  32 |     def get_scores(self, query: str, k1=1.5, b=0.75) -> dict:
  33 |         query_words = query.lower().split()
  34 |         scores = {}
  35 |         for i, chunk in enumerate(self.corpus):
  36 |             score = 0.0
  37 |             doc_len = self.doc_lens[i]
  38 |             doc_freq = self.doc_freqs[i]
  39 |             for word in query_words:
  40 |                 if word in doc_freq:
  41 |                     tf = doc_freq[word]
  42 |                     idf = self.idf.get(word, 0.0)
  43 |                     denom = tf + k1 * (1 - b + b * doc_len / self.avg_doc_len)
  44 |                     score += idf * tf * (k1 + 1) / denom
  45 |             scores[chunk["id"]] = score
  46 |         return scores
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L32 | Define `BM25Retriever.get_scores`; bind its arguments when called. The body executes only when invoked. |
| L33 | Evaluate the right-hand side, then bind/store it in `query_words`: `query.lower().split()` — Split the string into components; without an explicit separator, runs of whitespace are collapsed; first obtain the receiver: `query.lower()` — Return a lowercased string copy. |
| L34 | Evaluate the right-hand side, then bind/store it in `scores`: create an empty dictionary. |
| L35 | Iterate `enumerate(self.corpus)` (`enumerate(self.corpus)` — Yield an index and each input item in order; the optional second argument sets the starting index), assigning each item to `(i, chunk)`. Execute the indented body once per item; an empty iterable skips it. |
| L36 | Evaluate the right-hand side, then bind/store it in `score`: `0.0`. |
| L37 | Evaluate the right-hand side, then bind/store it in `doc_len`: look up index/key `i` in `self.doc_lens`; a missing key or out-of-range index raises. |
| L38 | Evaluate the right-hand side, then bind/store it in `doc_freq`: look up index/key `i` in `self.doc_freqs`; a missing key or out-of-range index raises. |
| L39 | Iterate `query_words` (the current `query_words` value), assigning each item to `word`. Execute the indented body once per item; an empty iterable skips it. |
| L40 | Evaluate the branch condition: compare whether `word` is contained in `doc_freq`. If truthy, enter L41; otherwise skip this indented block and continue after it. |
| L41 | Evaluate the right-hand side, then bind/store it in `tf`: look up index/key `word` in `doc_freq`; a missing key or out-of-range index raises. |
| L42 | Evaluate the right-hand side, then bind/store it in `idf`: `self.idf.get(word, 0.0)` — Look up `word` in `self.idf`, using `0.0` when the key is absent (an existing null value is not replaced). |
| L43 | Build BM25's saturation/length denominator. tf is this chunk's word count; doc_len/avg_doc_len adjusts for long/short chunks, b controls that adjustment, and k1 controls term-frequency saturation. |
| L44 | Add this query word's BM25 contribution to the chunk score: inverse document frequency times the saturated term frequency. Repeated words in the query contribute repeatedly because query_words is a list. |
| L45 | Evaluate the right-hand side, then bind/store it in `scores[chunk['id']]`: the current `score` value. |
| L46 | Compute the return value: the current `scores` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `match_citation_to_chunk(chunks: list[dict], sentence: str, filename: str | None = None, page: int | None = None) -> tuple[dict, str] | None`

- **Arguments:** Authorized candidate chunks with `text` and `metadata.source`/`metadata.page`; proposed evidence sentence; optional model filename/page hints.
- **Returns:** The original winning chunk dictionary plus its matched sentence, or `None` if no word overlaps.
- **Work:** Extracts lowercase `\w+` query tokens and their set. For each candidate sentence, computes exact token-sequence equality, fraction of query words shared, and fraction of candidate words shared. Compares the tuple `(exact, overlap, precision, source_hint_matches, page_hint_matches)` lexicographically, accepting only positive overlap and a strictly better score. Thus textual match dominates location hints; equal scores retain the first candidate. Empty/punctuation-only queries return `None`. No minimum confidence beyond positive overlap is required; callers derive final citation identity from the winning chunk.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-match-citation-to-chunk"></a>

#### Line-by-line execution

[Current source: lines 49–70](../../../../Backend/app/rag/text.py#L49-L70). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `chunks` | `list[dict]`; required; positional or keyword | PDF text chunks with the metadata required by this operation. |
| `sentence` | `str`; required; positional or keyword | Model-proposed citation sentence to match to actual retrieved PDF text. |
| `filename` | `str \| None`; default `None`; positional or keyword | Display filename/citation hint, not proof of ownership or document identity. |
| `page` | `int \| None`; default `None`; positional or keyword | One-based page hint used to break citation-matching ties. |

**Declared result:** `tuple[dict, str] | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  49 | def match_citation_to_chunk(
  50 |     chunks: list[dict], sentence: str, filename: str | None = None, page: int | None = None
  51 | ) -> tuple[dict, str] | None:
  52 |     query_tokens = re.findall(r"\w+", sentence.lower())
  53 |     query_words = set(query_tokens)
  54 |     if not query_words:
  55 |         return None
  56 |     best_match = None
  57 |     best_score = (False, 0.0, 0.0, False, False)
  58 |     for chunk in chunks:
  59 |         metadata = chunk["metadata"]
  60 |         for candidate in split_into_sentences(chunk["text"]):
  61 |             candidate_tokens = re.findall(r"\w+", candidate.lower())
  62 |             words = set(candidate_tokens)
  63 |             common_words = len(query_words.intersection(words))
  64 |             overlap = common_words / len(query_words)
  65 |             precision = common_words / len(words) if words else 0.0
  66 |             score = (query_tokens == candidate_tokens, overlap, precision, metadata["source"] == filename, metadata["page"] == page)
  67 |             if overlap > 0 and score > best_score:
  68 |                 best_match = (chunk, candidate)
  69 |                 best_score = score
  70 |     return best_match
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L49 | Define `match_citation_to_chunk`; bind its arguments when called. The body executes only when invoked. |
| L50 | Declare parameter `chunks` with annotation `list[dict]`. PDF text chunks with the metadata required by this operation. Declare parameter `sentence` with annotation `str`. Model-proposed citation sentence to match to actual retrieved PDF text. Declare parameter `filename` with annotation `str \| None`. Display filename/citation hint, not proof of ownership or document identity. Declare parameter `page` with annotation `int \| None`. One-based page hint used to break citation-matching ties. |
| L51 | Finish/continue the signature; the declared return annotation is `tuple[dict, str] \| None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L52 | Evaluate the right-hand side, then bind/store it in `query_tokens`: `re.findall('\\w+', sentence.lower())` — Collect every non-overlapping regular-expression match; inputs include `sentence.lower()` — Return a lowercased string copy. |
| L53 | Evaluate the right-hand side, then bind/store it in `query_words`: `set(query_tokens)` — Collect unique hashable items into a set. |
| L54 | Evaluate the branch condition: invert the truthiness of `query_words`. If truthy, enter L55; otherwise skip this indented block and continue after it. |
| L55 | Compute the return value: None (no value). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L56 | Evaluate the right-hand side, then bind/store it in `best_match`: None (no value). |
| L57 | Evaluate the right-hand side, then bind/store it in `best_score`: build a tuple containing `False`, `0.0`, `0.0`, `False`, `False`. |
| L58 | Iterate `chunks` (the current `chunks` value), assigning each item to `chunk`. Execute the indented body once per item; an empty iterable skips it. |
| L59 | Evaluate the right-hand side, then bind/store it in `metadata`: look up index/key `'metadata'` in `chunk`; a missing key or out-of-range index raises. |
| L60 | Iterate `split_into_sentences(chunk['text'])` (`split_into_sentences(chunk['text'])` — Call [split_into_sentences](#walk-split-into-sentences) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result), assigning each item to `candidate`. Execute the indented body once per item; an empty iterable skips it. |
| L61 | Evaluate the right-hand side, then bind/store it in `candidate_tokens`: `re.findall('\\w+', candidate.lower())` — Collect every non-overlapping regular-expression match; inputs include `candidate.lower()` — Return a lowercased string copy. |
| L62 | Evaluate the right-hand side, then bind/store it in `words`: `set(candidate_tokens)` — Collect unique hashable items into a set. |
| L63 | Evaluate the right-hand side, then bind/store it in `common_words`: `len(query_words.intersection(words))` — Count the items/characters in the supplied container/string; inputs include `query_words.intersection(words)` — Build the set of elements shared by both sets. |
| L64 | Divide distinct shared-token count by the distinct query-token count. The earlier empty-query guard guarantees a nonzero denominator; this measures how much of the proposed citation sentence the candidate covers. |
| L65 | Divide shared tokens by distinct candidate tokens, penalizing candidates containing many unrelated words. Use 0.0 for an empty candidate instead of dividing by zero. |
| L66 | Build a lexicographic ranking tuple: exact token-sequence equality first, then query-token coverage, candidate precision, filename hint, and page hint. Filename/page only break earlier ties; they do not supply the returned citation identity. |
| L67 | Require positive token overlap and a strictly better lexicographic ranking tuple. Only then replace the winner in the indented block; ties preserve the first matching sentence. |
| L68 | Evaluate the right-hand side, then bind/store it in `best_match`: build a tuple containing `chunk`, `candidate`. |
| L69 | Evaluate the right-hand side, then bind/store it in `best_score`: the current `score` value. |
| L70 | Compute the return value: the current `best_match` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
