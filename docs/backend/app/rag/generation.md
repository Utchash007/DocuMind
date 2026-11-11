# `app/rag/generation.py`

[Source](../../../../Backend/app/rag/generation.py) · [Backend index](../../README.md)

Retrieval → prompt → Groq/Instructor → citation refinement. `MODEL_NAME="openai/gpt-oss-120b"`, `TEMPERATURE=0.0`. Message repositories separately claim/persist turns.

`ModelAnswer` extends `CamelModel` with `answer: str` and `citations: list[ModelCitationLike]`; descriptions instruct grounded text and exact evidence hints, but fields have no nonempty/minimum-count constraints. `GenerationError` is a marker provider error with no custom methods.

## Functions

### `build_llm_messages(*, question: str, history: Sequence[HistoryTurn], context_chunks: Sequence[RetrievedChunk]) -> list[dict[str, str]]`

- **Arguments:** Current question, already-bounded prior context, authorized retrieved chunks.
- **Returns:** Two chat messages: one `system` instruction and one assembled `user` payload.
- **Work:** Rejects a whitespace-only question. Formats nonblank historical messages as `[role] content`, under an explicit context-only/non-evidence heading. Formats evidence with numbered chunk labels, source filenames, one-based pages, and text. Appends the current question once at the end, preserving its supplied text. Empty evidence gets an explicit placeholder. The system prompt requests one JSON object with `answer`/`citations` and each hint's `sentence`/`page`/`filename`, instructing the model to use source evidence only and admit insufficient evidence with an empty citation list.
- **Boundary:** This formatter does not query sources, trim/truncate history, verify claims, or include database writes; callers provide those inputs.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-build-llm-messages"></a>

#### Line-by-line execution

[Current source: lines 56–118](../../../../Backend/app/rag/generation.py#L56-L118). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `question` | `str`; required; keyword-only | Current user question, separate from historical messages and PDF evidence. |
| `history` | `Sequence[HistoryTurn]`; required; keyword-only | Prior conversation turns used as context; they are not source evidence. |
| `context_chunks` | `Sequence[RetrievedChunk]`; required; keyword-only | Retrieved PDF chunks supplied as the evidence portion of the model prompt. |

**Declared result:** `list[dict[str, str]]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  56 | def build_llm_messages(
  57 |     *,
  58 |     question: str,
  59 |     history: Sequence[HistoryTurn],
  60 |     context_chunks: Sequence[RetrievedChunk],
  61 | ) -> list[dict[str, str]]:
  62 |     """Assemble system + user messages for the structured LLM call.
  63 | 
  64 |     History (prior questions and answers) is explicitly labeled as
  65 |     context only; the retrieved chunks are the only evidence.  The
  66 |     current question is included exactly once, at the end.
  67 |     """
  68 |     if not question.strip():
  69 |         raise ValueError("question must not be blank")
  70 |     history_lines = [
  71 |         f"[{turn.role}] {turn.content}" for turn in history if turn.content.strip()
  72 |     ]
  73 |     history_block = (
  74 |         "Conversation history (context only - not source evidence):\n"
  75 |         + "\n".join(history_lines)
  76 |         + "\n\n"
  77 |         if history_lines
  78 |         else ""
  79 |     )
  80 |     evidence_lines = [
  81 |         (
  82 |             f"[Document Chunk {rank + 1} | Source: {chunk.source} "
  83 |             f"| Page {chunk.page_number}]: {chunk.text}"
  84 |         )
  85 |         for rank, chunk in enumerate(context_chunks)
  86 |     ]
  87 |     evidence_block = "\n\n".join(evidence_lines) if evidence_lines else "(no source evidence retrieved)"
  88 |     user_content = (
  89 |         f"{history_block}"
  90 |         f"Source evidence from authorized documents:\n{evidence_block}\n\n"
  91 |         f"Question: {question}"
  92 |     )
  93 |     return [
  94 |         {
  95 |             "role": "system",
  96 |             "content": (
  97 |                 "You are a meticulous, document-answering assistant. "
  98 |                 "Answer the user's question using ONLY the provided source "
  99 |                 "evidence as evidence. Conversation history, when present, "
 100 |                 "is context for what was discussed and is never itself "
 101 |                 "evidence. For every statement or fact you write, extract "
 102 |                 "the exact supporting sentence from the source evidence "
 103 |                 "(not from history) and specify its page number and exact "
 104 |                 "source filename. Do not make up facts or use external "
 105 |                 "knowledge.\n\n"
 106 |                 "Reply with one JSON object and no other text, using exactly "
 107 |                 'these keys: {"answer": string, "citations": [{"sentence": '
 108 |                 'string, "page": integer, "filename": string}]}. Copy '
 109 |                 "`sentence` verbatim from a single source-evidence chunk; "
 110 |                 "`page` is that chunk's page number; `filename` is that "
 111 |                 "chunk's Source value exactly as written. If the evidence "
 112 |                 "does not answer the question, say so briefly in `answer` "
 113 |                 "and return an empty `citations` list. Never invent "
 114 |                 "sentences, pages, or filenames."
 115 |             ),
 116 |         },
 117 |         {"role": "user", "content": user_content},
 118 |     ]
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L56 | Define `build_llm_messages`; bind its arguments when called. The body executes only when invoked. |
| L57 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L58 | Declare parameter `question` with annotation `str`. Current user question, separate from historical messages and PDF evidence. |
| L59 | Declare parameter `history` with annotation `Sequence[HistoryTurn]`. Prior conversation turns used as context; they are not source evidence. |
| L60 | Declare parameter `context_chunks` with annotation `Sequence[RetrievedChunk]`. Retrieved PDF chunks supplied as the evidence portion of the model prompt. |
| L61 | Finish/continue the signature; the declared return annotation is `list[dict[str, str]]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L62 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L64 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L65 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L66 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L67 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L68 | Evaluate the branch condition: invert the truthiness of `question.strip()`. If truthy, enter L69; otherwise skip this indented block and continue after it. |
| L69 | Raise `ValueError('question must not be blank')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L70 | Evaluate the right-hand side, then bind/store it in `history_lines`: iterate `history`, binding each item to `turn` and retain only items satisfying `turn.content.strip()`; produce `f'[{turn.role}] {turn.content}'` into a new list. |
| L71 | Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed. |
| L72 | Close the expression/container begun at L70; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L73 | Evaluate the right-hand side, then bind/store it in `history_block`: check `history_lines`; when true use add/concatenate `'Conversation history (context only - not source evidence):\n' + '\n'.join(history_lines)` and `'\n\n'`, following the parentheses/operator precedence shown in `'Conversation history (context only - not source evidence):\n' + '\n'.join(history_lines) + '\n\n'`, otherwise `''` (only the selected branch is evaluated). |
| L74 | Continue the enclosing expression: check `history_lines`; when true use add/concatenate `'Conversation history (context only - not source evidence):\n' + '\n'.join(history_lines)` and `'\n\n'`, following the parentheses/operator precedence shown in `'Conversation history (context only - not source evidence):\n' + '\n'.join(history_lines) + '\n\n'`, otherwise `''` (only the selected branch is evaluated). |
| L75 | Join the supplied string items using `'\n'` between adjacent items. |
| L76 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L77 | Contribute the current `history_lines` value to the expression being assembled. |
| L78 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L79 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L80 | Evaluate the right-hand side, then bind/store it in `evidence_lines`: iterate `enumerate(context_chunks)`, binding each item to `(rank, chunk)`; produce `f'[Document Chunk {rank + 1} \| Source: {chunk.source} \| Page {chunk.page_number}]: {chunk.text}'` into a new list. |
| L81 | Continue the operation begun at L80: Evaluate the right-hand side, then bind/store it in `evidence_lines`: iterate `enumerate(context_chunks)`, binding each item to `(rank, chunk)`; produce `f'[Document Chunk {rank + 1} \| Source: {chunk.source} \| Page {chunk.page_number}]: {chunk.text}'` into a new list. |
| L82 | Continue the enclosing expression: add/concatenate `rank` and `1`, following the parentheses/operator precedence shown in `rank + 1`. |
| L83 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L84 | Close the expression/container begun at L80; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L85 | Yield an index and each input item in order; the optional second argument sets the starting index. |
| L86 | Close the expression/container begun at L80; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L87 | Evaluate the right-hand side, then bind/store it in `evidence_block`: check `evidence_lines`; when true use `'\n\n'.join(evidence_lines)` — Join the supplied string items using `'\n\n'` between adjacent items, otherwise `'(no source evidence retrieved)'` (only the selected branch is evaluated). |
| L88 | Evaluate the right-hand side, then bind/store it in `user_content`: format a string by inserting `history_block`, `evidence_block`, `question` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L89 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L90 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L91 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L92 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L93 | Compute the return value: build a list containing `{'role': 'system', 'content': 'You are a meticulous, document-answering assistant. Answer the user\'s question using ONLY the provided source evidence as evidence. Conversation history, when present, is context for what was discussed and is never itself evidence. For every statement or fact you write, extract the exact supporting sentence from the source evidence (not from history) and specify its page number and exact source filename. Do not make up facts or use external knowledge.\n\nReply with one JSON object and no other text, using exactly these keys: {"answer": string, "citations": [{"sentence": string, "page": integer, "filename": string}]}. Copy 'sentence' verbatim from a single source-evidence chunk; 'page' is that chunk\'s page number; 'filename' is that chunk\'s Source value exactly as written. If the evidence does not answer the question, say so briefly in 'answer' and return an empty 'citations' list. Never invent sentences, pages, or filenames.'}`, `{'role': 'user', 'content': user_content}`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L94 | Contribute build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping to the expression being assembled. |
| L95 | Add mapping entry `'role'`: `'system'`. |
| L96 | Add mapping entry `'content'`: `'You are a meticulous, document-answering assistant. Answer the user\'s question using ONLY the provided source evidence as evidence. Conversation history, when present, is context for what was discussed and is never itself evidence. For every statement or fact you write, extract the exact supporting sentence from the source evidence (not from history) and specify its page number and exact source filename. Do not make up facts or use external knowledge.\n\nReply with one JSON object and no other text, using exactly these keys: {"answer": string, "citations": [{"sentence": string, "page": integer, "filename": string}]}. Copy 'sentence' verbatim from a single source-evidence chunk; 'page' is that chunk\'s page number; 'filename' is that chunk\'s Source value exactly as written. If the evidence does not answer the question, say so briefly in 'answer' and return an empty 'citations' list. Never invent sentences, pages, or filenames.'`. |
| L97 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L98 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L99 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L100 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L101 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L102 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L103 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L104 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L105 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L106 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L107 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L108 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L109 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L110 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L111 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L112 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L113 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L114 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L115 | Close the expression/container begun at L94; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L116 | Close the expression/container begun at L94; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L117 | Add mapping entry `'role'`: `'user'`. Add mapping entry `'content'`: the current `user_content` value. |
| L118 | Close the expression/container begun at L93; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `default_groq_client()`

**Arguments:** None. **Returns:** Newly constructed synchronous `Groq` client. **Work:** Lazily imports the SDK, reads `GROQ_API_KEY`, raises `GenerationError` when absent/empty, then constructs the client. It does not issue a chat completion itself or cache clients.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-default-groq-client"></a>

#### Line-by-line execution

[Current source: lines 121–128](../../../../Backend/app/rag/generation.py#L121-L128). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** No return annotation; follow the return/yield lines below. Python supplies None when a non-generator reaches the end without return.

**Numbered source**

```text
 121 | def default_groq_client():
 122 |     """Build the Groq client from the environment per request."""
 123 |     from groq import Groq
 124 | 
 125 |     api_key = os.getenv("GROQ_API_KEY")
 126 |     if not api_key:
 127 |         raise GenerationError("GROQ_API_KEY environment variable is missing.")
 128 |     return Groq(api_key=api_key)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L121 | Define `default_groq_client`; bind its arguments when called. The body executes only when invoked. |
| L122 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L123 | Import `Groq` from `groq`; inside a function this import is deferred until this path is reached. |
| L125 | Evaluate the right-hand side, then bind/store it in `api_key`: `os.getenv('GROQ_API_KEY')` — Read a process environment value, using the supplied fallback if absent. |
| L126 | Evaluate the branch condition: invert the truthiness of `api_key`. If truthy, enter L127; otherwise skip this indented block and continue after it. |
| L127 | Raise `GenerationError('GROQ_API_KEY environment variable is missing.')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L128 | Compute the return value: `Groq(api_key=api_key)` — Construct `Groq` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `generate_answer(*, question: str, history, authorized_sources, user_id=None, project_id=None, collection=None, embedder=None, groq_client=None) -> GeneratedAnswer`

- **Arguments:** Question; bounded history; exact `AuthorizedSource` pairs; owner/project identities (normal callers supply UUIDs); optional collection, embedder, and Groq client for dependency injection.
- **Returns:** Generated answer text plus refined verified citation DTOs.
- **Work:** Imports Instructor, calls `retrieve_context` with scope and collaborators, builds the two-message prompt, and resolves Groq. Uses `instructor.from_groq(..., mode=instructor.Mode.JSON).chat.completions.create` with `ModelAnswer`, the fixed model, zero temperature, and `max_retries=2`. JSON mode lets Instructor/Pydantic validate and retry structured output. Reconstructs the returned citation hints, calls `refine_citations` against only retrieved chunks, and returns `GeneratedAnswer`.
- **Errors/limits:** Completion/setup errors inside the Instructor call become `GenerationError`; retrieval, prompt construction, default-client creation, and later refinement occur outside that `try` and keep their own errors. Optional identity defaults are accepted by the signature, not explicitly validated here; retrieval's row checks reject mismatched/missing owner/project identities. This function does not persist messages, enforce the history budget itself, or prove every answer sentence is supported merely by returning some citations.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-generate-answer"></a>

#### Line-by-line execution

[Current source: lines 131–189](../../../../Backend/app/rag/generation.py#L131-L189). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `question` | `str`; required; keyword-only | Current user question, separate from historical messages and PDF evidence. |
| `history` | `Sequence[HistoryTurn]`; required; keyword-only | Prior conversation turns used as context; they are not source evidence. |
| `authorized_sources` | `Sequence[AuthorizedSource]`; required; keyword-only | Exact authorized document/version pairs; these bound the evidence search. |
| `user_id` | `Any \| None`; default `None`; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `Any \| None`; default `None`; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `collection` | `Any \| None`; default `None`; keyword-only | Injected Chroma-compatible collection; null selects the default when implemented. |
| `embedder` | `Any \| None`; default `None`; keyword-only | Embedding collaborator; the function selects its default only where explicitly shown. |
| `groq_client` | `Any \| None`; default `None`; keyword-only | Optional synchronous Groq client used for structured answer generation. |

**Declared result:** `GeneratedAnswer`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 131 | def generate_answer(
 132 |     *,
 133 |     question: str,
 134 |     history: Sequence[HistoryTurn],
 135 |     authorized_sources: Sequence[AuthorizedSource],
 136 |     user_id: Any | None = None,
 137 |     project_id: Any | None = None,
 138 |     collection: Any | None = None,
 139 |     embedder: Any | None = None,
 140 |     groq_client: Any | None = None,
 141 | ) -> GeneratedAnswer:
 142 |     """Generate a grounded answer with refined citations (no row writes).
 143 | 
 144 |     ``history`` is bounded recent completed context (already excluding
 145 |     the current question, which is added once by the prompt builder).
 146 |     ``authorized_sources`` are the exact permitted
 147 |     ``(document, index_version)`` pairs; retrieval never runs unscoped.
 148 |     """
 149 |     import instructor
 150 | 
 151 |     chunks = retrieve_context(
 152 |         question=question,
 153 |         user_id=user_id,
 154 |         project_id=project_id,
 155 |         authorized_sources=authorized_sources,
 156 |         collection=collection,
 157 |         embedder=embedder,
 158 |     )
 159 |     messages = build_llm_messages(
 160 |         question=question, history=history, context_chunks=chunks
 161 |     )
 162 |     llm = groq_client or default_groq_client()
 163 |     try:
 164 |         structured = (
 165 |             instructor.from_groq(llm, mode=instructor.Mode.JSON)
 166 |             .chat.completions.create(
 167 |                 model=MODEL_NAME,
 168 |                 response_model=ModelAnswer,
 169 |                 messages=messages,
 170 |                 temperature=TEMPERATURE,
 171 |                 max_retries=2,
 172 |             )
 173 |         )
 174 |     except GenerationError:
 175 |         raise
 176 |     except Exception as exc:  # provider outage surfaces as retryable service error
 177 |         raise GenerationError(f"Answer generation failed: {exc}") from exc
 178 |     citations = refine_citations(
 179 |         retrieved_chunks=chunks,
 180 |         model_citations=[
 181 |             ModelCitationLike(
 182 |                 sentence=citation.sentence,
 183 |                 page=citation.page,
 184 |                 filename=citation.filename,
 185 |             )
 186 |             for citation in structured.citations
 187 |         ],
 188 |     )
 189 |     return GeneratedAnswer(answer=structured.answer, citations=citations)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L131 | Define `generate_answer`; bind its arguments when called. The body executes only when invoked. |
| L132 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L133 | Declare parameter `question` with annotation `str`. Current user question, separate from historical messages and PDF evidence. |
| L134 | Declare parameter `history` with annotation `Sequence[HistoryTurn]`. Prior conversation turns used as context; they are not source evidence. |
| L135 | Declare parameter `authorized_sources` with annotation `Sequence[AuthorizedSource]`. Exact authorized document/version pairs; these bound the evidence search. |
| L136 | Declare parameter `user_id` with annotation `Any \| None`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L137 | Declare parameter `project_id` with annotation `Any \| None`. Project UUID used to constrain resource lookup or provider metadata. |
| L138 | Declare parameter `collection` with annotation `Any \| None`. Injected Chroma-compatible collection; null selects the default when implemented. |
| L139 | Declare parameter `embedder` with annotation `Any \| None`. Embedding collaborator; the function selects its default only where explicitly shown. |
| L140 | Declare parameter `groq_client` with annotation `Any \| None`. Optional synchronous Groq client used for structured answer generation. |
| L141 | Finish/continue the signature; the declared return annotation is `GeneratedAnswer`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L142 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L144 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L145 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L146 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L147 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L148 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L149 | Import `instructor` when execution reaches this line; an unavailable dependency raises ImportError. |
| L151 | Evaluate the right-hand side, then bind/store it in `chunks`: `retrieve_context(question=question, user_id=user_id, project_id=project_id, authorized_sources=authorized_sources, collection=collection, embedder=embedder)` — Call [retrieve_context](retrieval.md#walk-retrieve-context) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L152 | Supply `question` = `question`. Current user question, separate from historical messages and PDF evidence. Evaluate the value as: the current `question` value. |
| L153 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L154 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L155 | Supply `authorized_sources` = `authorized_sources`. Exact authorized document/version pairs; these bound the evidence search. Evaluate the value as: the current `authorized_sources` value. |
| L156 | Supply `collection` = `collection`. Injected Chroma-compatible collection; null selects the default when implemented. Evaluate the value as: the current `collection` value. |
| L157 | Supply `embedder` = `embedder`. Embedding collaborator; the function selects its default only where explicitly shown. Evaluate the value as: the current `embedder` value. |
| L158 | Close the expression/container begun at L151; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L159 | Evaluate the right-hand side, then bind/store it in `messages`: `build_llm_messages(question=question, history=history, context_chunks=chunks)` — Call [build_llm_messages](#walk-build-llm-messages) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L160 | Supply `question` = `question`. Current user question, separate from historical messages and PDF evidence. Evaluate the value as: the current `question` value. Supply `history` = `history`. Prior conversation turns used as context; they are not source evidence. Evaluate the value as: the current `history` value. Supply `context_chunks` = `chunks`. Retrieved PDF chunks supplied as the evidence portion of the model prompt. Evaluate the value as: the current `chunks` value. |
| L161 | Close the expression/container begun at L159; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L162 | Evaluate the right-hand side, then bind/store it in `llm`: evaluate `groq_client or default_groq_client()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L163 | Enter the protected block; failures are matched against `GenerationError`, `Exception` in order. |
| L164 | Evaluate the right-hand side, then bind/store it in `structured`: `instructor.from_groq(llm, mode=instructor.Mode.JSON).chat.completions.create` with the arguments detailed below — Invoke `instructor.from_groq(llm, mode=instructor.Mode.JSON).chat.completions.create` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L165 | `instructor.from_groq(llm, mode=instructor.Mode.JSON)` — Wrap the Groq client with Instructor's structured-output validation and configured mode. |
| L166 | Continue the operation begun at L164: Evaluate the right-hand side, then bind/store it in `structured`: `instructor.from_groq(llm, mode=instructor.Mode.JSON).chat.completions.create` with the arguments detailed below — Invoke `instructor.from_groq(llm, mode=instructor.Mode.JSON).chat.completions.create` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L167 | Supply `model` = `MODEL_NAME`.  Evaluate the value as: the current `MODEL_NAME` value. |
| L168 | Supply `response_model` = `ModelAnswer`.  Evaluate the value as: the current `ModelAnswer` value. |
| L169 | Supply `messages` = `messages`.  Evaluate the value as: the current `messages` value. |
| L170 | Supply `temperature` = `TEMPERATURE`.  Evaluate the value as: the current `TEMPERATURE` value. |
| L171 | Supply `max_retries` = `2`.  Evaluate the value as: `2`. |
| L172 | Close the expression/container begun at L165; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L173 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L174 | Handle `GenerationError`; only a matching error from the associated try enters this body. |
| L175 | Re-raise the currently handled exception with its traceback; no replacement result is returned. |
| L176 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L177 | Raise `GenerationError(f'Answer generation failed: {exc}')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L178 | Evaluate the right-hand side, then bind/store it in `citations`: `refine_citations` with the arguments detailed below — Call [refine_citations](citations.md#walk-refine-citations) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L179 | Supply `retrieved_chunks` = `chunks`.  Evaluate the value as: the current `chunks` value. |
| L180 | Supply `model_citations` = `[ModelCitationLike(sentence=citation.sentence, page=citation.page, filename=citation.filename) for citation in structured.citations]`.  Evaluate the value as: iterate `structured.citations`, binding each item to `citation`; produce `ModelCitationLike(sentence=citation.sentence, page=citation.page, filename=citation.filename)` into a new list. |
| L181 | `ModelCitationLike(sentence=citation.sentence, page=citation.page, filename=citation.filename)` — Construct `ModelCitationLike` with the shown fields; its class/model initialization rules apply. |
| L182 | Supply `sentence` = `citation.sentence`. Model-proposed citation sentence to match to actual retrieved PDF text. Evaluate the value as: the `sentence` attribute of `citation`. |
| L183 | Supply `page` = `citation.page`. One-based page hint used to break citation-matching ties. Evaluate the value as: the `page` attribute of `citation`. |
| L184 | Supply `filename` = `citation.filename`. Display filename/citation hint, not proof of ownership or document identity. Evaluate the value as: the `filename` attribute of `citation`. |
| L185 | Close the expression/container begun at L181; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L186 | Contribute the current `citation` value to the expression being assembled. |
| L187 | Close the expression/container begun at L180; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L188 | Close the expression/container begun at L178; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L189 | Compute the return value: `GeneratedAnswer(answer=structured.answer, citations=citations)` — Construct `GeneratedAnswer` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
