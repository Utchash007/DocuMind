# `app/api/messages.py`

[Source](../../../../Backend/app/api/messages.py) · [Backend index](../../README.md)

Router prefix `/projects/{project_id}/conversations/{conversation_id}/messages`. Uses the conversation module's onboarded `PrincipalDep` and short-transaction factory. Successful send/retry returns complete persisted JSON, not a token stream. `AnswerGeneratorDep` injects a callable returning `GeneratedAnswer`.

## Functions

### `get_answer_generator_dep() -> Callable[..., GeneratedAnswer]`

**Arguments:** None. **Returns:** Nested `_generate` callable. **Work:** Imports `app.rag.generation` and creates the adapter closure; does not call providers yet.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-answer-generator-dep"></a>

#### Line-by-line execution

[Current source: lines 65–92](../../../../Backend/app/api/messages.py#L65-L92). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `Callable[..., GeneratedAnswer]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  65 | def get_answer_generator_dep() -> Callable[..., GeneratedAnswer]:
  66 |     """Return the production answer generator (Groq/Instructor).
  67 | 
  68 |     Tests override this dependency with a deterministic fake.  Handlers
  69 |     pass ``user_id``/``project_id`` alongside the frozen
  70 |     ``(question, history, authorized_sources)`` triple so retrieval is
  71 |     always scoped; the generator itself performs no row writes.
  72 |     """
  73 |     from app.rag import generation as generation_mod
  74 | 
  75 |     def _generate(
  76 |         *,
  77 |         question: str,
  78 |         history,
  79 |         authorized_sources,
  80 |         user_id=None,
  81 |         project_id=None,
  82 |         **_kwargs,
  83 |     ) -> GeneratedAnswer:
  84 |         return generation_mod.generate_answer(
  85 |             question=question,
  86 |             history=history,
  87 |             authorized_sources=authorized_sources,
  88 |             user_id=user_id,
  89 |             project_id=project_id,
  90 |         )
  91 | 
  92 |     return _generate
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L65 | Define `get_answer_generator_dep`; bind its arguments when called. The body executes only when invoked. |
| L66 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L68 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L69 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L70 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L71 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L72 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L73 | Import `generation` as `generation_mod` from `app.rag`; inside a function this import is deferred until this path is reached. |
| L75 | Define the local closure [get_answer_generator_dep._generate](#walk-get-answer-generator-dep--generate); it can capture enclosing locals. Definition does not execute its body. |
| L76 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L77 | Declare parameter `question` with annotation `str`. Current user question, separate from historical messages and PDF evidence. |
| L78 | Declare parameter `history` without a type annotation. Prior conversation turns used as context; they are not source evidence. |
| L79 | Declare parameter `authorized_sources` without a type annotation. Exact authorized document/version pairs; these bound the evidence search. |
| L80 | Declare parameter `user_id` without a type annotation. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L81 | Declare parameter `project_id` without a type annotation. Project UUID used to constrain resource lookup or provider metadata. |
| L82 | Declare parameter `_kwargs` without a type annotation. Caller-supplied  kwargs; its uses and transformations are traced below. |
| L83 | Finish/continue the signature; the declared return annotation is `GeneratedAnswer`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L84 | Compute the return value: `generation_mod.generate_answer(question=question, history=history, authorized_sources=authorized_sources, user_id=user_id, project_id=project_id)` — Call [generation_mod.generate_answer](../rag/generation.md#walk-generate-answer) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L85 | Supply `question` = `question`. Current user question, separate from historical messages and PDF evidence. Evaluate the value as: the current `question` value. |
| L86 | Supply `history` = `history`. Prior conversation turns used as context; they are not source evidence. Evaluate the value as: the current `history` value. |
| L87 | Supply `authorized_sources` = `authorized_sources`. Exact authorized document/version pairs; these bound the evidence search. Evaluate the value as: the current `authorized_sources` value. |
| L88 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L89 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L90 | Close the expression/container begun at L84; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L92 | Compute the return value: the current `_generate` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `get_answer_generator_dep._generate(*, question: str, history, authorized_sources, user_id=None, project_id=None, **_kwargs) -> GeneratedAnswer` (nested)

**Arguments:** Question, history, exact evidence pairs, optional owner/project IDs, ignored extra kwargs. **Returns:** `generation_mod.generate_answer(...)`. **Work:** Forwards the five named inputs; the underlying generator enforces required scope even though this adapter accepts `None` defaults.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-answer-generator-dep--generate"></a>

#### Line-by-line execution

[Current source: lines 75–90](../../../../Backend/app/api/messages.py#L75-L90). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `question` | `str`; required; keyword-only | Current user question, separate from historical messages and PDF evidence. |
| `history` | not annotated; required; keyword-only | Prior conversation turns used as context; they are not source evidence. |
| `authorized_sources` | not annotated; required; keyword-only | Exact authorized document/version pairs; these bound the evidence search. |
| `user_id` | not annotated; default `None`; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | not annotated; default `None`; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `_kwargs` | not annotated; implicitly supplied/collected; ** keyword extras | Caller-supplied  kwargs; each read, transformation, and validation is traced below. |

**Declared result:** `GeneratedAnswer`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  75 |     def _generate(
  76 |         *,
  77 |         question: str,
  78 |         history,
  79 |         authorized_sources,
  80 |         user_id=None,
  81 |         project_id=None,
  82 |         **_kwargs,
  83 |     ) -> GeneratedAnswer:
  84 |         return generation_mod.generate_answer(
  85 |             question=question,
  86 |             history=history,
  87 |             authorized_sources=authorized_sources,
  88 |             user_id=user_id,
  89 |             project_id=project_id,
  90 |         )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L75 | Define `get_answer_generator_dep._generate`; bind its arguments when called. The body executes only when invoked. |
| L76 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L77 | Declare parameter `question` with annotation `str`. Current user question, separate from historical messages and PDF evidence. |
| L78 | Declare parameter `history` without a type annotation. Prior conversation turns used as context; they are not source evidence. |
| L79 | Declare parameter `authorized_sources` without a type annotation. Exact authorized document/version pairs; these bound the evidence search. |
| L80 | Declare parameter `user_id` without a type annotation. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L81 | Declare parameter `project_id` without a type annotation. Project UUID used to constrain resource lookup or provider metadata. |
| L82 | Declare parameter `_kwargs` without a type annotation. Caller-supplied  kwargs; its uses and transformations are traced below. |
| L83 | Finish/continue the signature; the declared return annotation is `GeneratedAnswer`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L84 | Compute the return value: `generation_mod.generate_answer(question=question, history=history, authorized_sources=authorized_sources, user_id=user_id, project_id=project_id)` — Call [generation_mod.generate_answer](../rag/generation.md#walk-generate-answer) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L85 | Supply `question` = `question`. Current user question, separate from historical messages and PDF evidence. Evaluate the value as: the current `question` value. |
| L86 | Supply `history` = `history`. Prior conversation turns used as context; they are not source evidence. Evaluate the value as: the current `history` value. |
| L87 | Supply `authorized_sources` = `authorized_sources`. Exact authorized document/version pairs; these bound the evidence search. Evaluate the value as: the current `authorized_sources` value. |
| L88 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L89 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L90 | Close the expression/container begun at L84; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `list_messages(project_id, conversation_id, principal, factory, cursor=None, limit=50) -> PaginatedResponse[MessageDto]`

**Route:** Collection GET (200). **Arguments:** Path UUIDs, principal/factory, optional cursor and 1–200 limit. **Returns:** Chronological persisted page. **Work:** Calls `conversations_repo.list_messages` inside a transaction; maps not-found to 404, cursor errors to 422.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-list-messages"></a>

#### Line-by-line execution

[Current source: lines 98–123](../../../../Backend/app/api/messages.py#L98-L123). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project_id` | `Annotated[UUID, Path()]`; required; positional or keyword | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `Annotated[UUID, Path()]`; required; positional or keyword | Conversation UUID identifying the owned chat and ordered message sequence. |
| `principal` | `PrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `factory` | `SessionFactoryDep`; required; positional or keyword | Session factory used to open a short database unit of work. |
| `cursor` | `Annotated[str \| None, Query(description='Opaque nextCursor from the previous page')]`; default `None`; positional or keyword | Opaque page continuation token; null starts the first page. |
| `limit` | `Annotated[int, Query(ge=1, le=200, description='Bounded page size (1-200)')]`; default `50`; positional or keyword | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |

**Declared result:** `PaginatedResponse[MessageDto]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  98 | @router.get("", response_model=PaginatedResponse[MessageDto], response_model_by_alias=True)
  99 | def list_messages(
 100 |     project_id: Annotated[UUID, Path()],
 101 |     conversation_id: Annotated[UUID, Path()],
 102 |     principal: PrincipalDep,
 103 |     factory: SessionFactoryDep,
 104 |     cursor: Annotated[str | None, Query(description="Opaque nextCursor from the previous page")] = None,
 105 |     limit: Annotated[int, Query(ge=1, le=200, description="Bounded page size (1-200)")] = 50,
 106 | ) -> PaginatedResponse[MessageDto]:
 107 |     """Paginated history in chronological (``position``) order."""
 108 |     from app.db.session import request_transaction
 109 | 
 110 |     try:
 111 |         with request_transaction(factory) as session:
 112 |             return conversations_repo.list_messages(
 113 |                 session,
 114 |                 user_id=principal.id,
 115 |                 project_id=project_id,
 116 |                 conversation_id=conversation_id,
 117 |                 cursor=cursor,
 118 |                 limit=limit,
 119 |             )
 120 |     except NotFoundError as exc:
 121 |         raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc
 122 |     except CursorError as exc:
 123 |         raise api_error(422, ErrorCode.VALIDATION_ERROR, str(exc)) from exc
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L98 | Register the handler with FastAPI using `router.get('', response_model=PaginatedResponse[MessageDto], response_model_by_alias=True)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L99 | Define `list_messages`; bind its arguments when called. The body executes only when invoked. |
| L100 | Declare parameter `project_id` with annotation `Annotated[UUID, Path()]`. Project UUID used to constrain resource lookup or provider metadata. |
| L101 | Declare parameter `conversation_id` with annotation `Annotated[UUID, Path()]`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L102 | Declare parameter `principal` with annotation `PrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L103 | Declare parameter `factory` with annotation `SessionFactoryDep`. Session factory used to open a short database unit of work. |
| L104 | Declare parameter `cursor` with annotation `Annotated[str \| None, Query(description='Opaque nextCursor from the previous page')]`. Opaque page continuation token; null starts the first page. |
| L105 | Declare parameter `limit` with annotation `Annotated[int, Query(ge=1, le=200, description='Bounded page size (1-200)')]`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. |
| L106 | Finish/continue the signature; the declared return annotation is `PaginatedResponse[MessageDto]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L107 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L108 | Import `request_transaction` from `app.db.session`; inside a function this import is deferred until this path is reached. |
| L110 | Enter the protected block; failures are matched against `NotFoundError`, `CursorError` in order. |
| L111 | Enter `request_transaction(factory)` — Open a short session/transaction context that commits on success, rolls back on exception, and closes the session and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L112 | Compute the return value: `conversations_repo.list_messages(session, user_id=principal.id, project_id=project_id, conversation_id=conversation_id, cursor=cursor, limit=limit)` — Call [conversations_repo.list_messages](../repositories/conversations.md#walk-list-messages) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L113 | Supply positional argument 1 to `conversations_repo.list_messages`: the current `session` value. |
| L114 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. |
| L115 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L116 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L117 | Supply `cursor` = `cursor`. Opaque page continuation token; null starts the first page. Evaluate the value as: the current `cursor` value. |
| L118 | Supply `limit` = `limit`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. Evaluate the value as: the current `limit` value. |
| L119 | Close the expression/container begun at L112; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L120 | Handle `NotFoundError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L121 | Raise `api_error(404, ErrorCode.NOT_FOUND, str(exc))`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L122 | Handle `CursorError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L123 | Raise `api_error(422, ErrorCode.VALIDATION_ERROR, str(exc))`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |

<!-- END LINE WALKTHROUGH -->

### `post_message(project_id, conversation_id, body, principal, factory, answer_generator) -> TurnResponse`

**Route:** Collection POST (200). **Arguments:** Path IDs, `MessageCreateRequest` (`content`, `clientRequestId`), principal/factory, generator. **Returns:** Original replay or newly persisted pair. **Work:** Calls `_claim_tx`, returns `replay_result` immediately for completed duplicates, otherwise calls `_run_claimed_turn` using the committed claim. User row exists before provider work.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-post-message"></a>

#### Line-by-line execution

[Current source: lines 126–160](../../../../Backend/app/api/messages.py#L126-L160). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project_id` | `Annotated[UUID, Path()]`; required; positional or keyword | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `Annotated[UUID, Path()]`; required; positional or keyword | Conversation UUID identifying the owned chat and ordered message sequence. |
| `body` | `MessageCreateRequest`; required; positional or keyword | Validated request-body DTO supplied by FastAPI. |
| `principal` | `PrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `factory` | `SessionFactoryDep`; required; positional or keyword | Session factory used to open a short database unit of work. |
| `answer_generator` | `AnswerGeneratorDep`; required; positional or keyword | Caller-supplied answer generator; each read, transformation, and validation is traced below. |

**Declared result:** `TurnResponse`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 126 | @router.post("", response_model=TurnResponse, response_model_by_alias=True)
 127 | def post_message(
 128 |     project_id: Annotated[UUID, Path()],
 129 |     conversation_id: Annotated[UUID, Path()],
 130 |     body: MessageCreateRequest,
 131 |     principal: PrincipalDep,
 132 |     factory: SessionFactoryDep,
 133 |     answer_generator: AnswerGeneratorDep,
 134 | ) -> TurnResponse:
 135 |     """Submit ``{content, clientRequestId}`` and return the persisted turn.
 136 | 
 137 |     The user message is persisted before any provider call; the
 138 |     assistant row is persisted (and returned) only when the generation
 139 |     claim is still current and the source snapshot is still valid.
 140 |     A duplicate of a completed request returns the original result.
 141 |     """
 142 |     claim = _claim_tx(
 143 |         factory=factory,
 144 |         project_id=project_id,
 145 |         conversation_id=conversation_id,
 146 |         user_id=principal.id,
 147 |         content=body.content,
 148 |         client_request_id=body.client_request_id,
 149 |     )
 150 |     if claim.is_replay:
 151 |         assert claim.replay_result is not None
 152 |         return claim.replay_result
 153 |     return _run_claimed_turn(
 154 |         user_id=principal.id,
 155 |         project_id=project_id,
 156 |         conversation_id=conversation_id,
 157 |         claim=claim,
 158 |         factory=factory,
 159 |         answer_generator=answer_generator,
 160 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L126 | Register the handler with FastAPI using `router.post('', response_model=TurnResponse, response_model_by_alias=True)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L127 | Define `post_message`; bind its arguments when called. The body executes only when invoked. |
| L128 | Declare parameter `project_id` with annotation `Annotated[UUID, Path()]`. Project UUID used to constrain resource lookup or provider metadata. |
| L129 | Declare parameter `conversation_id` with annotation `Annotated[UUID, Path()]`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L130 | Declare parameter `body` with annotation `MessageCreateRequest`. Validated request-body DTO supplied by FastAPI. |
| L131 | Declare parameter `principal` with annotation `PrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L132 | Declare parameter `factory` with annotation `SessionFactoryDep`. Session factory used to open a short database unit of work. |
| L133 | Declare parameter `answer_generator` with annotation `AnswerGeneratorDep`. Caller-supplied answer generator; its uses and transformations are traced below. |
| L134 | Finish/continue the signature; the declared return annotation is `TurnResponse`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L135 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L137 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L138 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L139 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L140 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L141 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L142 | Evaluate the right-hand side, then bind/store it in `claim`: `_claim_tx` with the arguments detailed below — Call [_claim_tx](#walk--claim-tx) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L143 | Supply `factory` = `factory`. Session factory used to open a short database unit of work. Evaluate the value as: the current `factory` value. |
| L144 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L145 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L146 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. |
| L147 | Supply `content` = `body.content`. Message text supplied for a persisted conversation turn. Evaluate the value as: the `content` attribute of `body`. |
| L148 | Supply `client_request_id` = `body.client_request_id`. Client request UUID used to deduplicate message sends. Evaluate the value as: the `client_request_id` attribute of `body`. |
| L149 | Close the expression/container begun at L142; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L150 | Evaluate the branch condition: the `is_replay` attribute of `claim`. If truthy, enter L151; otherwise skip this indented block and continue after it. |
| L151 | Check `claim.replay_result is not None`; when false raise AssertionError. Python optimization (-O) removes asserts, so this is not an unconditional validation mechanism. |
| L152 | Compute the return value: the `replay_result` attribute of `claim`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L153 | Compute the return value: `_run_claimed_turn` with the arguments detailed below — Call [_run_claimed_turn](#walk--run-claimed-turn) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L154 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. |
| L155 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L156 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L157 | Supply `claim` = `claim`. Committed job/turn claim carrying the identity and fencing fields required by later operations. Evaluate the value as: the current `claim` value. |
| L158 | Supply `factory` = `factory`. Session factory used to open a short database unit of work. Evaluate the value as: the current `factory` value. |
| L159 | Supply `answer_generator` = `answer_generator`.  Evaluate the value as: the current `answer_generator` value. |
| L160 | Close the expression/container begun at L153; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `retry_message(project_id, conversation_id, message_id, body, principal, factory, answer_generator) -> TurnResponse`

**Route:** `POST /{message_id}/retry` (200). **Arguments:** Scope/turn UUIDs, `MessageRetryRequest` body (its key is optional), principal/factory/generator. **Returns:** Result for the reactivated original user row. **Work:** Calls `reclaim_turn_for_retry` in a committed transaction, maps missing→404 and key conflict/active/ineligible→409 with resource IDs, then delegates generation/persistence to `_run_claimed_turn`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-retry-message"></a>

#### Line-by-line execution

[Current source: lines 163–222](../../../../Backend/app/api/messages.py#L163-L222). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project_id` | `Annotated[UUID, Path()]`; required; positional or keyword | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `Annotated[UUID, Path()]`; required; positional or keyword | Conversation UUID identifying the owned chat and ordered message sequence. |
| `message_id` | `Annotated[UUID, Path()]`; required; positional or keyword | Persisted message UUID identifying the turn being read, retried, or cancelled. |
| `body` | `MessageRetryRequest`; required; positional or keyword | Validated request-body DTO supplied by FastAPI. |
| `principal` | `PrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `factory` | `SessionFactoryDep`; required; positional or keyword | Session factory used to open a short database unit of work. |
| `answer_generator` | `AnswerGeneratorDep`; required; positional or keyword | Caller-supplied answer generator; each read, transformation, and validation is traced below. |

**Declared result:** `TurnResponse`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 163 | @router.post("/{message_id}/retry", response_model=TurnResponse, response_model_by_alias=True)
 164 | def retry_message(
 165 |     project_id: Annotated[UUID, Path()],
 166 |     conversation_id: Annotated[UUID, Path()],
 167 |     message_id: Annotated[UUID, Path()],
 168 |     body: MessageRetryRequest,
 169 |     principal: PrincipalDep,
 170 |     factory: SessionFactoryDep,
 171 |     answer_generator: AnswerGeneratorDep,
 172 | ) -> TurnResponse:
 173 |     """Retry the latest failed/interrupted user turn (no new user row)."""
 174 |     from app.db.session import request_transaction
 175 | 
 176 |     try:
 177 |         with request_transaction(factory) as session:
 178 |             claim = lifecycle.reclaim_turn_for_retry(
 179 |                 session,
 180 |                 user_id=principal.id,
 181 |                 project_id=project_id,
 182 |                 conversation_id=conversation_id,
 183 |                 message_id=message_id,
 184 |                 client_request_id=body.client_request_id,
 185 |             )
 186 |     except NotFoundError as exc:
 187 |         raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc
 188 |     except DuplicateRequestConflict as exc:
 189 |         raise api_error(
 190 |             409,
 191 |             ErrorCode.DUPLICATE_REQUEST_CONFLICT,
 192 |             str(exc),
 193 |             message_id=exc.message_id,
 194 |             conversation_id=exc.conversation_id,
 195 |             project_id=project_id,
 196 |         ) from exc
 197 |     except ActiveTurnInProgress as exc:
 198 |         raise api_error(
 199 |             409,
 200 |             ErrorCode.ACTIVE_TURN_IN_PROGRESS,
 201 |             str(exc),
 202 |             message_id=exc.active_message_id,
 203 |             conversation_id=exc.conversation_id,
 204 |             project_id=project_id,
 205 |         ) from exc
 206 |     except InvalidStateError as exc:
 207 |         raise api_error(
 208 |             409,
 209 |             ErrorCode.INVALID_STATE,
 210 |             str(exc),
 211 |             message_id=message_id,
 212 |             conversation_id=conversation_id,
 213 |             project_id=project_id,
 214 |         ) from exc
 215 |     return _run_claimed_turn(
 216 |         user_id=principal.id,
 217 |         project_id=project_id,
 218 |         conversation_id=conversation_id,
 219 |         claim=claim,
 220 |         factory=factory,
 221 |         answer_generator=answer_generator,
 222 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L163 | Register the handler with FastAPI using `router.post('/{message_id}/retry', response_model=TurnResponse, response_model_by_alias=True)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L164 | Define `retry_message`; bind its arguments when called. The body executes only when invoked. |
| L165 | Declare parameter `project_id` with annotation `Annotated[UUID, Path()]`. Project UUID used to constrain resource lookup or provider metadata. |
| L166 | Declare parameter `conversation_id` with annotation `Annotated[UUID, Path()]`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L167 | Declare parameter `message_id` with annotation `Annotated[UUID, Path()]`. Persisted message UUID identifying the turn being read, retried, or cancelled. |
| L168 | Declare parameter `body` with annotation `MessageRetryRequest`. Validated request-body DTO supplied by FastAPI. |
| L169 | Declare parameter `principal` with annotation `PrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L170 | Declare parameter `factory` with annotation `SessionFactoryDep`. Session factory used to open a short database unit of work. |
| L171 | Declare parameter `answer_generator` with annotation `AnswerGeneratorDep`. Caller-supplied answer generator; its uses and transformations are traced below. |
| L172 | Finish/continue the signature; the declared return annotation is `TurnResponse`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L173 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L174 | Import `request_transaction` from `app.db.session`; inside a function this import is deferred until this path is reached. |
| L176 | Enter the protected block; failures are matched against `NotFoundError`, `DuplicateRequestConflict`, `ActiveTurnInProgress`, `InvalidStateError` in order. |
| L177 | Enter `request_transaction(factory)` — Open a short session/transaction context that commits on success, rolls back on exception, and closes the session and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L178 | Evaluate the right-hand side, then bind/store it in `claim`: `lifecycle.reclaim_turn_for_retry` with the arguments detailed below — Call [lifecycle.reclaim_turn_for_retry](../repositories/messages.md#walk-reclaim-turn-for-retry) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L179 | Supply positional argument 1 to `lifecycle.reclaim_turn_for_retry`: the current `session` value. |
| L180 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. |
| L181 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L182 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L183 | Supply `message_id` = `message_id`. Persisted message UUID identifying the turn being read, retried, or cancelled. Evaluate the value as: the current `message_id` value. |
| L184 | Supply `client_request_id` = `body.client_request_id`. Client request UUID used to deduplicate message sends. Evaluate the value as: the `client_request_id` attribute of `body`. |
| L185 | Close the expression/container begun at L178; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L186 | Handle `NotFoundError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L187 | Raise `api_error(404, ErrorCode.NOT_FOUND, str(exc))`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L188 | Handle `DuplicateRequestConflict` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L189 | Raise `api_error(409, ErrorCode.DUPLICATE_REQUEST_CONFLICT, str(exc), message_id=exc.message_id, conversation_id=exc.conversation_id, project_id=project_id)`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L190 | Supply positional argument 1 to `api_error`: `409`. |
| L191 | Supply positional argument 2 to `api_error`: the `DUPLICATE_REQUEST_CONFLICT` attribute of `ErrorCode`. |
| L192 | `str(exc)` — Convert the input to its string representation. |
| L193 | Supply `message_id` = `exc.message_id`. Persisted message UUID identifying the turn being read, retried, or cancelled. Evaluate the value as: the `message_id` attribute of `exc`. |
| L194 | Supply `conversation_id` = `exc.conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the `conversation_id` attribute of `exc`. |
| L195 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L196 | Contribute the current `exc` value to the expression being assembled. |
| L197 | Handle `ActiveTurnInProgress` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L198 | Raise `api_error(409, ErrorCode.ACTIVE_TURN_IN_PROGRESS, str(exc), message_id=exc.active_message_id, conversation_id=exc.conversation_id, project_id=project_id)`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L199 | Supply positional argument 1 to `api_error`: `409`. |
| L200 | Supply positional argument 2 to `api_error`: the `ACTIVE_TURN_IN_PROGRESS` attribute of `ErrorCode`. |
| L201 | `str(exc)` — Convert the input to its string representation. |
| L202 | Supply `message_id` = `exc.active_message_id`. Persisted message UUID identifying the turn being read, retried, or cancelled. Evaluate the value as: the `active_message_id` attribute of `exc`. |
| L203 | Supply `conversation_id` = `exc.conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the `conversation_id` attribute of `exc`. |
| L204 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L205 | Contribute the current `exc` value to the expression being assembled. |
| L206 | Handle `InvalidStateError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L207 | Raise `api_error(409, ErrorCode.INVALID_STATE, str(exc), message_id=message_id, conversation_id=conversation_id, project_id=project_id)`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L208 | Supply positional argument 1 to `api_error`: `409`. |
| L209 | Supply positional argument 2 to `api_error`: the `INVALID_STATE` attribute of `ErrorCode`. |
| L210 | `str(exc)` — Convert the input to its string representation. |
| L211 | Supply `message_id` = `message_id`. Persisted message UUID identifying the turn being read, retried, or cancelled. Evaluate the value as: the current `message_id` value. |
| L212 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L213 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L214 | Contribute the current `exc` value to the expression being assembled. |
| L215 | Compute the return value: `_run_claimed_turn` with the arguments detailed below — Call [_run_claimed_turn](#walk--run-claimed-turn) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L216 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. |
| L217 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L218 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L219 | Supply `claim` = `claim`. Committed job/turn claim carrying the identity and fencing fields required by later operations. Evaluate the value as: the current `claim` value. |
| L220 | Supply `factory` = `factory`. Session factory used to open a short database unit of work. Evaluate the value as: the current `factory` value. |
| L221 | Supply `answer_generator` = `answer_generator`.  Evaluate the value as: the current `answer_generator` value. |
| L222 | Close the expression/container begun at L215; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `cancel_message(project_id, conversation_id, message_id, principal, factory) -> MessageCancelResponse`

**Route:** `POST /{message_id}/cancel` (200). **Arguments:** Scope/turn UUIDs and principal/factory. **Returns:** Authoritative user DTO and cancellation boolean. **Work:** Calls `cancel_turn` in a transaction; maps missing→404, ineligible→409, then builds the response after commit. Cancellation invalidates persistence eligibility, not the network request itself.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-cancel-message"></a>

#### Line-by-line execution

[Current source: lines 225–256](../../../../Backend/app/api/messages.py#L225-L256). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project_id` | `Annotated[UUID, Path()]`; required; positional or keyword | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `Annotated[UUID, Path()]`; required; positional or keyword | Conversation UUID identifying the owned chat and ordered message sequence. |
| `message_id` | `Annotated[UUID, Path()]`; required; positional or keyword | Persisted message UUID identifying the turn being read, retried, or cancelled. |
| `principal` | `PrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `factory` | `SessionFactoryDep`; required; positional or keyword | Session factory used to open a short database unit of work. |

**Declared result:** `MessageCancelResponse`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 225 | @router.post("/{message_id}/cancel", response_model=MessageCancelResponse, response_model_by_alias=True)
 226 | def cancel_message(
 227 |     project_id: Annotated[UUID, Path()],
 228 |     conversation_id: Annotated[UUID, Path()],
 229 |     message_id: Annotated[UUID, Path()],
 230 |     principal: PrincipalDep,
 231 |     factory: SessionFactoryDep,
 232 | ) -> MessageCancelResponse:
 233 |     """Cancel the active turn; a late provider response cannot commit."""
 234 |     from app.db.session import request_transaction
 235 | 
 236 |     try:
 237 |         with request_transaction(factory) as session:
 238 |             message, cancelled = lifecycle.cancel_turn(
 239 |                 session,
 240 |                 user_id=principal.id,
 241 |                 project_id=project_id,
 242 |                 conversation_id=conversation_id,
 243 |                 message_id=message_id,
 244 |             )
 245 |     except NotFoundError as exc:
 246 |         raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc
 247 |     except InvalidStateError as exc:
 248 |         raise api_error(
 249 |             409,
 250 |             ErrorCode.INVALID_STATE,
 251 |             str(exc),
 252 |             message_id=message_id,
 253 |             conversation_id=conversation_id,
 254 |             project_id=project_id,
 255 |         ) from exc
 256 |     return MessageCancelResponse(user_message=message, cancelled=cancelled)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L225 | Register the handler with FastAPI using `router.post('/{message_id}/cancel', response_model=MessageCancelResponse, response_model_by_alias=True)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L226 | Define `cancel_message`; bind its arguments when called. The body executes only when invoked. |
| L227 | Declare parameter `project_id` with annotation `Annotated[UUID, Path()]`. Project UUID used to constrain resource lookup or provider metadata. |
| L228 | Declare parameter `conversation_id` with annotation `Annotated[UUID, Path()]`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L229 | Declare parameter `message_id` with annotation `Annotated[UUID, Path()]`. Persisted message UUID identifying the turn being read, retried, or cancelled. |
| L230 | Declare parameter `principal` with annotation `PrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L231 | Declare parameter `factory` with annotation `SessionFactoryDep`. Session factory used to open a short database unit of work. |
| L232 | Finish/continue the signature; the declared return annotation is `MessageCancelResponse`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L233 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L234 | Import `request_transaction` from `app.db.session`; inside a function this import is deferred until this path is reached. |
| L236 | Enter the protected block; failures are matched against `NotFoundError`, `InvalidStateError` in order. |
| L237 | Enter `request_transaction(factory)` — Open a short session/transaction context that commits on success, rolls back on exception, and closes the session and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L238 | Evaluate the right-hand side, then bind/store it in `(message, cancelled)`: `lifecycle.cancel_turn(session, user_id=principal.id, project_id=project_id, conversation_id=conversation_id, message_id=message_id)` — Call [lifecycle.cancel_turn](../repositories/messages.md#walk-cancel-turn) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L239 | Supply positional argument 1 to `lifecycle.cancel_turn`: the current `session` value. |
| L240 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. |
| L241 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L242 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L243 | Supply `message_id` = `message_id`. Persisted message UUID identifying the turn being read, retried, or cancelled. Evaluate the value as: the current `message_id` value. |
| L244 | Close the expression/container begun at L238; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L245 | Handle `NotFoundError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L246 | Raise `api_error(404, ErrorCode.NOT_FOUND, str(exc))`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L247 | Handle `InvalidStateError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L248 | Raise `api_error(409, ErrorCode.INVALID_STATE, str(exc), message_id=message_id, conversation_id=conversation_id, project_id=project_id)`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L249 | Supply positional argument 1 to `api_error`: `409`. |
| L250 | Supply positional argument 2 to `api_error`: the `INVALID_STATE` attribute of `ErrorCode`. |
| L251 | `str(exc)` — Convert the input to its string representation. |
| L252 | Supply `message_id` = `message_id`. Persisted message UUID identifying the turn being read, retried, or cancelled. Evaluate the value as: the current `message_id` value. |
| L253 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L254 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L255 | Contribute the current `exc` value to the expression being assembled. |
| L256 | Compute the return value: `MessageCancelResponse(user_message=message, cancelled=cancelled)` — Construct `MessageCancelResponse` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_claim_tx(*, factory, project_id, conversation_id, user_id, content: str, client_request_id: UUID)`

- **Arguments:** Transaction factory, authenticated scope UUIDs, exact question, request key.
- **Returns:** `lifecycle.Claim` after transaction completion.
- **Work:** Calls `claim_new_turn` inside `request_transaction`. Maps not-found→404; duplicate content conflict→409 `duplicate_request_conflict`; active turn→409 `active_turn_in_progress`; invalid retry/cancelled replay→409 `invalid_state`; completed replay missing its assistant→500 `internal_error`. Other database errors propagate.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--claim-tx"></a>

#### Line-by-line execution

[Current source: lines 264–324](../../../../Backend/app/api/messages.py#L264-L324). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `factory` | not annotated; required; keyword-only | Session factory used to open a short database unit of work. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `content` | `str`; required; keyword-only | Message text supplied for a persisted conversation turn. |
| `client_request_id` | `UUID`; required; keyword-only | Client request UUID used to deduplicate message sends. |

**Declared result:** No return annotation; follow the return/yield lines below. Python supplies None when a non-generator reaches the end without return.

**Numbered source**

```text
 264 | def _claim_tx(
 265 |     *,
 266 |     factory,
 267 |     project_id: UUID,
 268 |     conversation_id: UUID,
 269 |     user_id: UUID,
 270 |     content: str,
 271 |     client_request_id: UUID,
 272 | ):
 273 |     """tx1: claim (insert/reuse the user row)."""
 274 |     from app.db.session import request_transaction
 275 | 
 276 |     try:
 277 |         with request_transaction(factory) as session:
 278 |             return lifecycle.claim_new_turn(
 279 |                 session,
 280 |                 user_id=user_id,
 281 |                 project_id=project_id,
 282 |                 conversation_id=conversation_id,
 283 |                 content=content,
 284 |                 client_request_id=client_request_id,
 285 |             )
 286 |     except NotFoundError as exc:
 287 |         raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc
 288 |     except DuplicateRequestConflict as exc:
 289 |         raise api_error(
 290 |             409,
 291 |             ErrorCode.DUPLICATE_REQUEST_CONFLICT,
 292 |             str(exc),
 293 |             message_id=exc.message_id,
 294 |             conversation_id=exc.conversation_id,
 295 |             project_id=project_id,
 296 |         ) from exc
 297 |     except ActiveTurnInProgress as exc:
 298 |         raise api_error(
 299 |             409,
 300 |             ErrorCode.ACTIVE_TURN_IN_PROGRESS,
 301 |             str(exc),
 302 |             message_id=exc.active_message_id,
 303 |             conversation_id=exc.conversation_id,
 304 |             project_id=project_id,
 305 |         ) from exc
 306 |     except InvalidStateError as exc:
 307 |         raise api_error(
 308 |             409,
 309 |             ErrorCode.INVALID_STATE,
 310 |             str(exc),
 311 |             conversation_id=conversation_id,
 312 |             project_id=project_id,
 313 |         ) from exc
 314 |     except ClaimLostError as exc:
 315 |         # A completed duplicate whose assistant row is missing is an
 316 |         # integrity violation (unreachable while persist creates both
 317 |         # rows atomically); surface it as an unexpected failure.
 318 |         raise api_error(
 319 |             500,
 320 |             ErrorCode.INTERNAL_ERROR,
 321 |             "This turn could not be reconciled; please retry.",
 322 |             conversation_id=conversation_id,
 323 |             project_id=project_id,
 324 |         ) from exc
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L264 | Define `_claim_tx`; bind its arguments when called. The body executes only when invoked. |
| L265 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L266 | Declare parameter `factory` without a type annotation. Session factory used to open a short database unit of work. |
| L267 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L268 | Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L269 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L270 | Declare parameter `content` with annotation `str`. Message text supplied for a persisted conversation turn. |
| L271 | Declare parameter `client_request_id` with annotation `UUID`. Client request UUID used to deduplicate message sends. |
| L272 | Finish/continue the signature; no return annotation is declared. |
| L273 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L274 | Import `request_transaction` from `app.db.session`; inside a function this import is deferred until this path is reached. |
| L276 | Enter the protected block; failures are matched against `NotFoundError`, `DuplicateRequestConflict`, `ActiveTurnInProgress`, `InvalidStateError`, `ClaimLostError` in order. |
| L277 | Enter `request_transaction(factory)` — Open a short session/transaction context that commits on success, rolls back on exception, and closes the session and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L278 | Compute the return value: `lifecycle.claim_new_turn` with the arguments detailed below — Call [lifecycle.claim_new_turn](../repositories/messages.md#walk-claim-new-turn) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L279 | Supply positional argument 1 to `lifecycle.claim_new_turn`: the current `session` value. |
| L280 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L281 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L282 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L283 | Supply `content` = `content`. Message text supplied for a persisted conversation turn. Evaluate the value as: the current `content` value. |
| L284 | Supply `client_request_id` = `client_request_id`. Client request UUID used to deduplicate message sends. Evaluate the value as: the current `client_request_id` value. |
| L285 | Close the expression/container begun at L278; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L286 | Handle `NotFoundError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L287 | Raise `api_error(404, ErrorCode.NOT_FOUND, str(exc))`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L288 | Handle `DuplicateRequestConflict` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L289 | Raise `api_error(409, ErrorCode.DUPLICATE_REQUEST_CONFLICT, str(exc), message_id=exc.message_id, conversation_id=exc.conversation_id, project_id=project_id)`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L290 | Supply positional argument 1 to `api_error`: `409`. |
| L291 | Supply positional argument 2 to `api_error`: the `DUPLICATE_REQUEST_CONFLICT` attribute of `ErrorCode`. |
| L292 | `str(exc)` — Convert the input to its string representation. |
| L293 | Supply `message_id` = `exc.message_id`. Persisted message UUID identifying the turn being read, retried, or cancelled. Evaluate the value as: the `message_id` attribute of `exc`. |
| L294 | Supply `conversation_id` = `exc.conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the `conversation_id` attribute of `exc`. |
| L295 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L296 | Contribute the current `exc` value to the expression being assembled. |
| L297 | Handle `ActiveTurnInProgress` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L298 | Raise `api_error(409, ErrorCode.ACTIVE_TURN_IN_PROGRESS, str(exc), message_id=exc.active_message_id, conversation_id=exc.conversation_id, project_id=project_id)`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L299 | Supply positional argument 1 to `api_error`: `409`. |
| L300 | Supply positional argument 2 to `api_error`: the `ACTIVE_TURN_IN_PROGRESS` attribute of `ErrorCode`. |
| L301 | `str(exc)` — Convert the input to its string representation. |
| L302 | Supply `message_id` = `exc.active_message_id`. Persisted message UUID identifying the turn being read, retried, or cancelled. Evaluate the value as: the `active_message_id` attribute of `exc`. |
| L303 | Supply `conversation_id` = `exc.conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the `conversation_id` attribute of `exc`. |
| L304 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L305 | Contribute the current `exc` value to the expression being assembled. |
| L306 | Handle `InvalidStateError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L307 | Raise `api_error(409, ErrorCode.INVALID_STATE, str(exc), conversation_id=conversation_id, project_id=project_id)`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L308 | Supply positional argument 1 to `api_error`: `409`. |
| L309 | Supply positional argument 2 to `api_error`: the `INVALID_STATE` attribute of `ErrorCode`. |
| L310 | `str(exc)` — Convert the input to its string representation. |
| L311 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L312 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L313 | Contribute the current `exc` value to the expression being assembled. |
| L314 | Handle `ClaimLostError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L315 | Comment only: A completed duplicate whose assistant row is missing is an. It does not execute; the neighboring code determines behavior. |
| L316 | Comment only: integrity violation (unreachable while persist creates both. It does not execute; the neighboring code determines behavior. |
| L317 | Comment only: rows atomically); surface it as an unexpected failure.. It does not execute; the neighboring code determines behavior. |
| L318 | Raise `api_error(500, ErrorCode.INTERNAL_ERROR, 'This turn could not be reconciled; please retry.', conversation_id=conversation_id, project_id=project_id)`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L319 | Supply positional argument 1 to `api_error`: `500`. |
| L320 | Supply positional argument 2 to `api_error`: the `INTERNAL_ERROR` attribute of `ErrorCode`. |
| L321 | Supply positional argument 3 to `api_error`: `'This turn could not be reconciled; please retry.'`. |
| L322 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L323 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L324 | Contribute the current `exc` value to the expression being assembled. |

<!-- END LINE WALKTHROUGH -->

### `_run_claimed_turn(*, user_id, project_id, conversation_id, claim, factory, answer_generator) -> TurnResponse`

- **Arguments:** Authenticated scope, committed non-replay claim, factory, provider callable.
- **Returns:** Persisted pair after the final transaction commits.
- **Work:** Requires a token. In a short transaction resolves authorized sources and records them on the claim/message. An empty set triggers best-effort failure plus 409; lost project scope becomes 404. In a separate transaction loads bounded history; failure marks the turn and returns 500. Measures `perf_counter()` around provider execution **outside SQL transactions**, passing question/history/pairs and owner/project IDs. Finally calls `persist_assistant_answer` in a fresh transaction with model name and integer elapsed milliseconds.
- **Provider errors:** Empty ready sources→409; index/generation availability failures→503; unexpected failures→500. Each attempts `_mark_failed` while preserving the user message. Immediate error envelopes use fixed/specific messages; some stored diagnostics include the supplied exception string.
- **Claim loss:** A snapshot mismatch rolls back persistence, then marks failure separately. Reads authoritative turn status: unavailable scope→404; otherwise→409, with a cancellation-specific explanation when appropriate. Discarded provider output is not returned as a successful answer.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--run-claimed-turn"></a>

#### Line-by-line execution

[Current source: lines 327–515](../../../../Backend/app/api/messages.py#L327-L515). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |
| `claim` | not annotated; required; keyword-only | Committed job/turn claim carrying the identity and fencing fields required by later operations. |
| `factory` | not annotated; required; keyword-only | Session factory used to open a short database unit of work. |
| `answer_generator` | `Callable[..., GeneratedAnswer]`; required; keyword-only | Caller-supplied answer generator; each read, transformation, and validation is traced below. |

**Declared result:** `TurnResponse`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 327 | def _run_claimed_turn(
 328 |     *,
 329 |     user_id: UUID,
 330 |     project_id: UUID,
 331 |     conversation_id: UUID,
 332 |     claim,
 333 |     factory,
 334 |     answer_generator: Callable[..., GeneratedAnswer],
 335 | ) -> TurnResponse:
 336 |     """tx2 (snapshot) -> providers -> tx3 (guarded persist)."""
 337 |     from app.db.session import request_transaction
 338 | 
 339 |     assert claim.generation_token is not None
 340 |     # tx2: resolve authorized sources and record the snapshot. The user
 341 |     # row (inserted in tx1) survives an empty ready set: the turn is
 342 |     # failed and the error is useful â€” never an unscoped search.
 343 |     try:
 344 |         with request_transaction(factory) as session:
 345 |             snapshot = lifecycle.resolve_authorized_sources(
 346 |                 session, user_id=user_id, project_id=project_id
 347 |             )
 348 |             claim.snapshot = snapshot
 349 |             lifecycle.record_snapshot(
 350 |                 session,
 351 |                 user_message_id=claim.user_message_id,
 352 |                 snapshot=snapshot,
 353 |             )
 354 |     except NoReadySourcesError as exc:
 355 |         _mark_failed(
 356 |             factory=factory,
 357 |             user_message_id=claim.user_message_id,
 358 |             generation_token=claim.generation_token,
 359 |             error_code=ErrorCode.NO_READY_SOURCES.value,
 360 |             error_message=str(exc),
 361 |         )
 362 |         raise api_error(
 363 |             409,
 364 |             ErrorCode.NO_READY_SOURCES,
 365 |             str(exc),
 366 |             message_id=claim.user_message_id,
 367 |             conversation_id=conversation_id,
 368 |             project_id=project_id,
 369 |         ) from exc
 370 |     except NotFoundError as exc:
 371 |         raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc
 372 | 
 373 |     # Bounded recent completed history (current question added once by
 374 |     # the prompt builder; failed/cancelled turns excluded).
 375 |     try:
 376 |         with request_transaction(factory) as session:
 377 |             history = lifecycle.load_history_turns(
 378 |                 session, conversation_id=conversation_id
 379 |             )
 380 |     except Exception as exc:  # unexpected DB failure: fail the turn, stay retryable
 381 |         _mark_failed(
 382 |             factory=factory,
 383 |             user_message_id=claim.user_message_id,
 384 |             generation_token=claim.generation_token,
 385 |             error_code=ErrorCode.INTERNAL_ERROR.value,
 386 |             error_message=f"History load failed: {exc}",
 387 |         )
 388 |         raise api_error(
 389 |             500,
 390 |             ErrorCode.INTERNAL_ERROR,
 391 |             "Failed to prepare the answer.",
 392 |             message_id=claim.user_message_id,
 393 |             conversation_id=conversation_id,
 394 |             project_id=project_id,
 395 |         ) from exc
 396 | 
 397 |     started = time.perf_counter()
 398 |     try:
 399 |         generated = answer_generator(
 400 |             question=claim.content,
 401 |             history=history,
 402 |             authorized_sources=claim.snapshot,
 403 |             user_id=user_id,
 404 |             project_id=project_id,
 405 |         )
 406 |     except (NoReadySourcesError, RetrievalNoReadySources) as exc:
 407 |         _mark_failed(
 408 |             factory=factory,
 409 |             user_message_id=claim.user_message_id,
 410 |             generation_token=claim.generation_token,
 411 |             error_code=ErrorCode.NO_READY_SOURCES.value,
 412 |             error_message=str(exc),
 413 |         )
 414 |         raise api_error(
 415 |             409,
 416 |             ErrorCode.NO_READY_SOURCES,
 417 |             str(exc),
 418 |             message_id=claim.user_message_id,
 419 |             conversation_id=conversation_id,
 420 |             project_id=project_id,
 421 |         ) from exc
 422 |     except (IndexUnavailableError, GenerationError) as exc:
 423 |         _mark_failed(
 424 |             factory=factory,
 425 |             user_message_id=claim.user_message_id,
 426 |             generation_token=claim.generation_token,
 427 |             error_code=ErrorCode.SERVICE_UNAVAILABLE.value,
 428 |             error_message=str(exc),
 429 |         )
 430 |         raise api_error(
 431 |             503,
 432 |             ErrorCode.SERVICE_UNAVAILABLE,
 433 |             "Answer generation is temporarily unavailable. Please retry.",
 434 |             message_id=claim.user_message_id,
 435 |             conversation_id=conversation_id,
 436 |             project_id=project_id,
 437 |         ) from exc
 438 |     except Exception as exc:  # defensive: never leak a provider payload
 439 |         _mark_failed(
 440 |             factory=factory,
 441 |             user_message_id=claim.user_message_id,
 442 |             generation_token=claim.generation_token,
 443 |             error_code=ErrorCode.INTERNAL_ERROR.value,
 444 |             error_message=f"Answer generation failed: {exc}",
 445 |         )
 446 |         raise api_error(
 447 |             500,
 448 |             ErrorCode.INTERNAL_ERROR,
 449 |             "Answer generation failed.",
 450 |             message_id=claim.user_message_id,
 451 |             conversation_id=conversation_id,
 452 |             project_id=project_id,
 453 |         ) from exc
 454 |     latency_ms = int((time.perf_counter() - started) * 1000)
 455 | 
 456 |     # tx3: persist guarded by token, snapshot, and scope liveness.
 457 |     try:
 458 |         with request_transaction(factory) as session:
 459 |             return lifecycle.persist_assistant_answer(
 460 |                 session,
 461 |                 user_id=user_id,
 462 |                 project_id=project_id,
 463 |                 conversation_id=conversation_id,
 464 |                 user_message_id=claim.user_message_id,
 465 |                 generation_token=claim.generation_token,
 466 |                 snapshot=claim.snapshot,
 467 |                 answer=generated.answer,
 468 |                 citations=generated.citations,
 469 |                 model=MODEL_NAME,
 470 |                 latency_ms=latency_ms,
 471 |             )
 472 |     except ClaimLostError as exc:
 473 |         if isinstance(exc, SnapshotMismatchError):
 474 |             # The persist transaction rolled back; mark the turn failed
 475 |             # in its own token-guarded transaction so the client can
 476 |             # retry with fresh sources (the answer is discarded).
 477 |             _mark_failed(
 478 |                 factory=factory,
 479 |                 user_message_id=claim.user_message_id,
 480 |                 generation_token=claim.generation_token,
 481 |                 error_code=exc.code,
 482 |                 error_message=str(exc),
 483 |             )
 484 |         try:
 485 |             with request_transaction(factory) as session:
 486 |                 status = lifecycle.get_turn_status(
 487 |                     session,
 488 |                     user_id=user_id,
 489 |                     project_id=project_id,
 490 |                     conversation_id=conversation_id,
 491 |                     message_id=claim.user_message_id,
 492 |                 ).generation_status
 493 |         except NotFoundError:
 494 |             status = None
 495 |         if status is None:
 496 |             raise api_error(
 497 |                 404,
 498 |                 ErrorCode.NOT_FOUND,
 499 |                 "The conversation is no longer available.",
 500 |                 conversation_id=conversation_id,
 501 |                 project_id=project_id,
 502 |             ) from exc
 503 |         message = (
 504 |             "This turn was cancelled and its answer was discarded."
 505 |             if status == "cancelled"
 506 |             else "This turn can no longer be answered; please retry."
 507 |         )
 508 |         raise api_error(
 509 |             409,
 510 |             ErrorCode.INVALID_STATE,
 511 |             message,
 512 |             message_id=claim.user_message_id,
 513 |             conversation_id=conversation_id,
 514 |             project_id=project_id,
 515 |         ) from exc
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L327 | Define `_run_claimed_turn`; bind its arguments when called. The body executes only when invoked. |
| L328 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L329 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L330 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L331 | Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L332 | Declare parameter `claim` without a type annotation. Committed job/turn claim carrying the identity and fencing fields required by later operations. |
| L333 | Declare parameter `factory` without a type annotation. Session factory used to open a short database unit of work. |
| L334 | Declare parameter `answer_generator` with annotation `Callable[..., GeneratedAnswer]`. Caller-supplied answer generator; its uses and transformations are traced below. |
| L335 | Finish/continue the signature; the declared return annotation is `TurnResponse`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L336 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L337 | Import `request_transaction` from `app.db.session`; inside a function this import is deferred until this path is reached. |
| L339 | Check `claim.generation_token is not None`; when false raise AssertionError. Python optimization (-O) removes asserts, so this is not an unconditional validation mechanism. |
| L340 | Comment only: tx2: resolve authorized sources and record the snapshot. The user. It does not execute; the neighboring code determines behavior. |
| L341 | Comment only: row (inserted in tx1) survives an empty ready set: the turn is. It does not execute; the neighboring code determines behavior. |
| L342 | Comment only: failed and the error is useful â€” never an unscoped search.. It does not execute; the neighboring code determines behavior. |
| L343 | Enter the protected block; failures are matched against `NoReadySourcesError`, `NotFoundError` in order. |
| L344 | Enter `request_transaction(factory)` — Open a short session/transaction context that commits on success, rolls back on exception, and closes the session and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L345 | Evaluate the right-hand side, then bind/store it in `snapshot`: `lifecycle.resolve_authorized_sources(session, user_id=user_id, project_id=project_id)` — Call [lifecycle.resolve_authorized_sources](../repositories/messages.md#walk-resolve-authorized-sources) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L346 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L347 | Close the expression/container begun at L345; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L348 | Evaluate the right-hand side, then bind/store it in `claim.snapshot`: the current `snapshot` value. |
| L349 | `lifecycle.record_snapshot(session, user_message_id=claim.user_message_id, snapshot=snapshot)` — Call [lifecycle.record_snapshot](../repositories/messages.md#walk-record-snapshot) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L350 | Supply positional argument 1 to `lifecycle.record_snapshot`: the current `session` value. |
| L351 | Supply `user_message_id` = `claim.user_message_id`.  Evaluate the value as: the `user_message_id` attribute of `claim`. |
| L352 | Supply `snapshot` = `snapshot`.  Evaluate the value as: the current `snapshot` value. |
| L353 | Close the expression/container begun at L349; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L354 | Handle `NoReadySourcesError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L355 | `_mark_failed` with the arguments detailed below — Call [_mark_failed](#walk--mark-failed) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L356 | Supply `factory` = `factory`. Session factory used to open a short database unit of work. Evaluate the value as: the current `factory` value. |
| L357 | Supply `user_message_id` = `claim.user_message_id`.  Evaluate the value as: the `user_message_id` attribute of `claim`. |
| L358 | Supply `generation_token` = `claim.generation_token`. Generation claim token used to fence a late answer. Evaluate the value as: the `generation_token` attribute of `claim`. |
| L359 | Supply `error_code` = `ErrorCode.NO_READY_SOURCES.value`. Machine-readable failure category stored or exposed by the operation. Evaluate the value as: the `value` attribute of `ErrorCode.NO_READY_SOURCES`. |
| L360 | Supply `error_message` = `str(exc)`. Human-readable failure detail; truncation alone does not redact sensitive content. Evaluate the value as: `str(exc)` — Convert the input to its string representation. |
| L361 | Close the expression/container begun at L355; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L362 | Raise `api_error(409, ErrorCode.NO_READY_SOURCES, str(exc), message_id=claim.user_message_id, conversation_id=conversation_id, project_id=project_id)`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L363 | Supply positional argument 1 to `api_error`: `409`. |
| L364 | Supply positional argument 2 to `api_error`: the `NO_READY_SOURCES` attribute of `ErrorCode`. |
| L365 | `str(exc)` — Convert the input to its string representation. |
| L366 | Supply `message_id` = `claim.user_message_id`. Persisted message UUID identifying the turn being read, retried, or cancelled. Evaluate the value as: the `user_message_id` attribute of `claim`. |
| L367 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L368 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L369 | Contribute the current `exc` value to the expression being assembled. |
| L370 | Handle `NotFoundError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L371 | Raise `api_error(404, ErrorCode.NOT_FOUND, str(exc))`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L373 | Comment only: Bounded recent completed history (current question added once by. It does not execute; the neighboring code determines behavior. |
| L374 | Comment only: the prompt builder; failed/cancelled turns excluded).. It does not execute; the neighboring code determines behavior. |
| L375 | Enter the protected block; failures are matched against `Exception` in order. |
| L376 | Enter `request_transaction(factory)` — Open a short session/transaction context that commits on success, rolls back on exception, and closes the session and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L377 | Evaluate the right-hand side, then bind/store it in `history`: `lifecycle.load_history_turns(session, conversation_id=conversation_id)` — Call [lifecycle.load_history_turns](../repositories/messages.md#walk-load-history-turns) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L378 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L379 | Close the expression/container begun at L377; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L380 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L381 | `_mark_failed` with the arguments detailed below — Call [_mark_failed](#walk--mark-failed) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L382 | Supply `factory` = `factory`. Session factory used to open a short database unit of work. Evaluate the value as: the current `factory` value. |
| L383 | Supply `user_message_id` = `claim.user_message_id`.  Evaluate the value as: the `user_message_id` attribute of `claim`. |
| L384 | Supply `generation_token` = `claim.generation_token`. Generation claim token used to fence a late answer. Evaluate the value as: the `generation_token` attribute of `claim`. |
| L385 | Supply `error_code` = `ErrorCode.INTERNAL_ERROR.value`. Machine-readable failure category stored or exposed by the operation. Evaluate the value as: the `value` attribute of `ErrorCode.INTERNAL_ERROR`. |
| L386 | Supply `error_message` = `f'History load failed: {exc}'`. Human-readable failure detail; truncation alone does not redact sensitive content. Evaluate the value as: format a string by inserting `exc` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L387 | Close the expression/container begun at L381; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L388 | Raise `api_error(500, ErrorCode.INTERNAL_ERROR, 'Failed to prepare the answer.', message_id=claim.user_message_id, conversation_id=conversation_id, project_id=project_id)`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L389 | Supply positional argument 1 to `api_error`: `500`. |
| L390 | Supply positional argument 2 to `api_error`: the `INTERNAL_ERROR` attribute of `ErrorCode`. |
| L391 | Supply positional argument 3 to `api_error`: `'Failed to prepare the answer.'`. |
| L392 | Supply `message_id` = `claim.user_message_id`. Persisted message UUID identifying the turn being read, retried, or cancelled. Evaluate the value as: the `user_message_id` attribute of `claim`. |
| L393 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L394 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L395 | Contribute the current `exc` value to the expression being assembled. |
| L397 | Evaluate the right-hand side, then bind/store it in `started`: `time.perf_counter()` — Read a high-resolution monotonic timer for elapsed-duration measurement. |
| L398 | Enter the protected block; failures are matched against `(NoReadySourcesError, RetrievalNoReadySources)`, `(IndexUnavailableError, GenerationError)`, `Exception` in order. |
| L399 | Evaluate the right-hand side, then bind/store it in `generated`: `answer_generator(question=claim.content, history=history, authorized_sources=claim.snapshot, user_id=user_id, project_id=project_id)` — Invoke the injected/default answer generator with question, bounded history, and exact authorized source pairs. |
| L400 | Supply `question` = `claim.content`. Current user question, separate from historical messages and PDF evidence. Evaluate the value as: the `content` attribute of `claim`. |
| L401 | Supply `history` = `history`. Prior conversation turns used as context; they are not source evidence. Evaluate the value as: the current `history` value. |
| L402 | Supply `authorized_sources` = `claim.snapshot`. Exact authorized document/version pairs; these bound the evidence search. Evaluate the value as: the `snapshot` attribute of `claim`. |
| L403 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L404 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L405 | Close the expression/container begun at L399; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L406 | Handle `(NoReadySourcesError, RetrievalNoReadySources)` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L407 | `_mark_failed` with the arguments detailed below — Call [_mark_failed](#walk--mark-failed) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L408 | Supply `factory` = `factory`. Session factory used to open a short database unit of work. Evaluate the value as: the current `factory` value. |
| L409 | Supply `user_message_id` = `claim.user_message_id`.  Evaluate the value as: the `user_message_id` attribute of `claim`. |
| L410 | Supply `generation_token` = `claim.generation_token`. Generation claim token used to fence a late answer. Evaluate the value as: the `generation_token` attribute of `claim`. |
| L411 | Supply `error_code` = `ErrorCode.NO_READY_SOURCES.value`. Machine-readable failure category stored or exposed by the operation. Evaluate the value as: the `value` attribute of `ErrorCode.NO_READY_SOURCES`. |
| L412 | Supply `error_message` = `str(exc)`. Human-readable failure detail; truncation alone does not redact sensitive content. Evaluate the value as: `str(exc)` — Convert the input to its string representation. |
| L413 | Close the expression/container begun at L407; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L414 | Raise `api_error(409, ErrorCode.NO_READY_SOURCES, str(exc), message_id=claim.user_message_id, conversation_id=conversation_id, project_id=project_id)`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L415 | Supply positional argument 1 to `api_error`: `409`. |
| L416 | Supply positional argument 2 to `api_error`: the `NO_READY_SOURCES` attribute of `ErrorCode`. |
| L417 | `str(exc)` — Convert the input to its string representation. |
| L418 | Supply `message_id` = `claim.user_message_id`. Persisted message UUID identifying the turn being read, retried, or cancelled. Evaluate the value as: the `user_message_id` attribute of `claim`. |
| L419 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L420 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L421 | Contribute the current `exc` value to the expression being assembled. |
| L422 | Handle `(IndexUnavailableError, GenerationError)` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L423 | `_mark_failed` with the arguments detailed below — Call [_mark_failed](#walk--mark-failed) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L424 | Supply `factory` = `factory`. Session factory used to open a short database unit of work. Evaluate the value as: the current `factory` value. |
| L425 | Supply `user_message_id` = `claim.user_message_id`.  Evaluate the value as: the `user_message_id` attribute of `claim`. |
| L426 | Supply `generation_token` = `claim.generation_token`. Generation claim token used to fence a late answer. Evaluate the value as: the `generation_token` attribute of `claim`. |
| L427 | Supply `error_code` = `ErrorCode.SERVICE_UNAVAILABLE.value`. Machine-readable failure category stored or exposed by the operation. Evaluate the value as: the `value` attribute of `ErrorCode.SERVICE_UNAVAILABLE`. |
| L428 | Supply `error_message` = `str(exc)`. Human-readable failure detail; truncation alone does not redact sensitive content. Evaluate the value as: `str(exc)` — Convert the input to its string representation. |
| L429 | Close the expression/container begun at L423; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L430 | Raise `api_error(503, ErrorCode.SERVICE_UNAVAILABLE, 'Answer generation is temporarily unavailable. Please retry.', message_id=claim.user_message_id, conversation_id=conversation_id, project_id=project_id)`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L431 | Supply positional argument 1 to `api_error`: `503`. |
| L432 | Supply positional argument 2 to `api_error`: the `SERVICE_UNAVAILABLE` attribute of `ErrorCode`. |
| L433 | Supply positional argument 3 to `api_error`: `'Answer generation is temporarily unavailable. Please retry.'`. |
| L434 | Supply `message_id` = `claim.user_message_id`. Persisted message UUID identifying the turn being read, retried, or cancelled. Evaluate the value as: the `user_message_id` attribute of `claim`. |
| L435 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L436 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L437 | Contribute the current `exc` value to the expression being assembled. |
| L438 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L439 | `_mark_failed` with the arguments detailed below — Call [_mark_failed](#walk--mark-failed) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L440 | Supply `factory` = `factory`. Session factory used to open a short database unit of work. Evaluate the value as: the current `factory` value. |
| L441 | Supply `user_message_id` = `claim.user_message_id`.  Evaluate the value as: the `user_message_id` attribute of `claim`. |
| L442 | Supply `generation_token` = `claim.generation_token`. Generation claim token used to fence a late answer. Evaluate the value as: the `generation_token` attribute of `claim`. |
| L443 | Supply `error_code` = `ErrorCode.INTERNAL_ERROR.value`. Machine-readable failure category stored or exposed by the operation. Evaluate the value as: the `value` attribute of `ErrorCode.INTERNAL_ERROR`. |
| L444 | Supply `error_message` = `f'Answer generation failed: {exc}'`. Human-readable failure detail; truncation alone does not redact sensitive content. Evaluate the value as: format a string by inserting `exc` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L445 | Close the expression/container begun at L439; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L446 | Raise `api_error(500, ErrorCode.INTERNAL_ERROR, 'Answer generation failed.', message_id=claim.user_message_id, conversation_id=conversation_id, project_id=project_id)`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L447 | Supply positional argument 1 to `api_error`: `500`. |
| L448 | Supply positional argument 2 to `api_error`: the `INTERNAL_ERROR` attribute of `ErrorCode`. |
| L449 | Supply positional argument 3 to `api_error`: `'Answer generation failed.'`. |
| L450 | Supply `message_id` = `claim.user_message_id`. Persisted message UUID identifying the turn being read, retried, or cancelled. Evaluate the value as: the `user_message_id` attribute of `claim`. |
| L451 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L452 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L453 | Contribute the current `exc` value to the expression being assembled. |
| L454 | Evaluate the right-hand side, then bind/store it in `latency_ms`: `int((time.perf_counter() - started) * 1000)` — Convert the input to an integer (using the optional numeric base); inputs include multiply/repeat `time.perf_counter() - started` and `1000`, following the parentheses/operator precedence shown in `(time.perf_counter() - started) * 1000`. |
| L456 | Comment only: tx3: persist guarded by token, snapshot, and scope liveness.. It does not execute; the neighboring code determines behavior. |
| L457 | Enter the protected block; failures are matched against `ClaimLostError` in order. |
| L458 | Enter `request_transaction(factory)` — Open a short session/transaction context that commits on success, rolls back on exception, and closes the session and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L459 | Compute the return value: `lifecycle.persist_assistant_answer` with the arguments detailed below — Call [lifecycle.persist_assistant_answer](../repositories/messages.md#walk-persist-assistant-answer) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L460 | Supply positional argument 1 to `lifecycle.persist_assistant_answer`: the current `session` value. |
| L461 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L462 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L463 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L464 | Supply `user_message_id` = `claim.user_message_id`.  Evaluate the value as: the `user_message_id` attribute of `claim`. |
| L465 | Supply `generation_token` = `claim.generation_token`. Generation claim token used to fence a late answer. Evaluate the value as: the `generation_token` attribute of `claim`. |
| L466 | Supply `snapshot` = `claim.snapshot`.  Evaluate the value as: the `snapshot` attribute of `claim`. |
| L467 | Supply `answer` = `generated.answer`.  Evaluate the value as: the `answer` attribute of `generated`. |
| L468 | Supply `citations` = `generated.citations`.  Evaluate the value as: the `citations` attribute of `generated`. |
| L469 | Supply `model` = `MODEL_NAME`.  Evaluate the value as: the current `MODEL_NAME` value. |
| L470 | Supply `latency_ms` = `latency_ms`.  Evaluate the value as: the current `latency_ms` value. |
| L471 | Close the expression/container begun at L459; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L472 | Handle `ClaimLostError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L473 | Evaluate the branch condition: `isinstance(exc, SnapshotMismatchError)` — Check the runtime type against the supplied class or tuple of classes. If truthy, enter L477; otherwise skip this indented block and continue after it. |
| L474 | Comment only: The persist transaction rolled back; mark the turn failed. It does not execute; the neighboring code determines behavior. |
| L475 | Comment only: in its own token-guarded transaction so the client can. It does not execute; the neighboring code determines behavior. |
| L476 | Comment only: retry with fresh sources (the answer is discarded).. It does not execute; the neighboring code determines behavior. |
| L477 | `_mark_failed(factory=factory, user_message_id=claim.user_message_id, generation_token=claim.generation_token, error_code=exc.code, error_message=str(exc))` — Call [_mark_failed](#walk--mark-failed) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L478 | Supply `factory` = `factory`. Session factory used to open a short database unit of work. Evaluate the value as: the current `factory` value. |
| L479 | Supply `user_message_id` = `claim.user_message_id`.  Evaluate the value as: the `user_message_id` attribute of `claim`. |
| L480 | Supply `generation_token` = `claim.generation_token`. Generation claim token used to fence a late answer. Evaluate the value as: the `generation_token` attribute of `claim`. |
| L481 | Supply `error_code` = `exc.code`. Machine-readable failure category stored or exposed by the operation. Evaluate the value as: the `code` attribute of `exc`. |
| L482 | Supply `error_message` = `str(exc)`. Human-readable failure detail; truncation alone does not redact sensitive content. Evaluate the value as: `str(exc)` — Convert the input to its string representation. |
| L483 | Close the expression/container begun at L477; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L484 | Enter the protected block; failures are matched against `NotFoundError` in order. |
| L485 | Enter `request_transaction(factory)` — Open a short session/transaction context that commits on success, rolls back on exception, and closes the session and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L486 | Evaluate the right-hand side, then bind/store it in `status`: the `generation_status` attribute of `lifecycle.get_turn_status(session, user_id=user_id, project_id=project_id, conversation_id=conversation_id, message_id=claim.user_message_id)`. |
| L487 | Supply positional argument 1 to `lifecycle.get_turn_status`: the current `session` value. |
| L488 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L489 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L490 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L491 | Supply `message_id` = `claim.user_message_id`. Persisted message UUID identifying the turn being read, retried, or cancelled. Evaluate the value as: the `user_message_id` attribute of `claim`. |
| L492 | Continue the operation begun at L486: Evaluate the right-hand side, then bind/store it in `status`: the `generation_status` attribute of `lifecycle.get_turn_status(session, user_id=user_id, project_id=project_id, conversation_id=conversation_id, message_id=claim.user_message_id)`. |
| L493 | Handle `NotFoundError`; only a matching error from the associated try enters this body. |
| L494 | Evaluate the right-hand side, then bind/store it in `status`: None (no value). |
| L495 | Evaluate the branch condition: compare whether `status` is the same object as `None`. If truthy, enter L496; otherwise skip this indented block and continue after it. |
| L496 | Raise `api_error(404, ErrorCode.NOT_FOUND, 'The conversation is no longer available.', conversation_id=conversation_id, project_id=project_id)`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L497 | Supply positional argument 1 to `api_error`: `404`. |
| L498 | Supply positional argument 2 to `api_error`: the `NOT_FOUND` attribute of `ErrorCode`. |
| L499 | Supply positional argument 3 to `api_error`: `'The conversation is no longer available.'`. |
| L500 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L501 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L502 | Contribute the current `exc` value to the expression being assembled. |
| L503 | Evaluate the right-hand side, then bind/store it in `message`: check `status == 'cancelled'`; when true use `'This turn was cancelled and its answer was discarded.'`, otherwise `'This turn can no longer be answered; please retry.'` (only the selected branch is evaluated). |
| L504 | Continue the enclosing expression: check `status == 'cancelled'`; when true use `'This turn was cancelled and its answer was discarded.'`, otherwise `'This turn can no longer be answered; please retry.'` (only the selected branch is evaluated). |
| L505 | Continue the enclosing expression: compare whether `status` equals `'cancelled'`. |
| L506 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |
| L507 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L508 | Raise `api_error(409, ErrorCode.INVALID_STATE, message, message_id=claim.user_message_id, conversation_id=conversation_id, project_id=project_id)`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L509 | Supply positional argument 1 to `api_error`: `409`. |
| L510 | Supply positional argument 2 to `api_error`: the `INVALID_STATE` attribute of `ErrorCode`. |
| L511 | Supply positional argument 3 to `api_error`: the current `message` value. |
| L512 | Supply `message_id` = `claim.user_message_id`. Persisted message UUID identifying the turn being read, retried, or cancelled. Evaluate the value as: the `user_message_id` attribute of `claim`. |
| L513 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L514 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L515 | Contribute the current `exc` value to the expression being assembled. |

<!-- END LINE WALKTHROUGH -->

### `_mark_failed(*, factory, user_message_id: UUID, generation_token: UUID, error_code: str, error_message: str) -> bool`

**Arguments:** Transaction factory, turn/token IDs, diagnostic. **Returns:** Whether `mark_turn_failed` updated the current claim; false on stale claim or any failure writing the diagnostic. **Work:** Uses its own short transaction and catches exceptions so cleanup failure does not mask the original request error.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--mark-failed"></a>

#### Line-by-line execution

[Current source: lines 518–532](../../../../Backend/app/api/messages.py#L518-L532). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `factory` | not annotated; required; keyword-only | Session factory used to open a short database unit of work. |
| `user_message_id` | `UUID`; required; keyword-only | Caller-supplied user message id; each read, transformation, and validation is traced below. |
| `generation_token` | `UUID`; required; keyword-only | Generation claim token used to fence a late answer. |
| `error_code` | `str`; required; keyword-only | Machine-readable failure category stored or exposed by the operation. |
| `error_message` | `str`; required; keyword-only | Human-readable failure detail; truncation alone does not redact sensitive content. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 518 | def _mark_failed(*, factory, user_message_id: UUID, generation_token: UUID, error_code: str, error_message: str) -> bool:
 519 |     """Best-effort failure mark (own transaction, token-guarded)."""
 520 |     from app.db.session import request_transaction
 521 | 
 522 |     try:
 523 |         with request_transaction(factory) as session:
 524 |             return lifecycle.mark_turn_failed(
 525 |                 session,
 526 |                 user_message_id=user_message_id,
 527 |                 generation_token=generation_token,
 528 |                 error_code=error_code,
 529 |                 error_message=error_message,
 530 |             )
 531 |     except Exception:  # never mask the real error with a cleanup failure
 532 |         return False
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L518 | Define `_mark_failed`; bind its arguments when called. The body executes only when invoked. |
| L519 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L520 | Import `request_transaction` from `app.db.session`; inside a function this import is deferred until this path is reached. |
| L522 | Enter the protected block; failures are matched against `Exception` in order. |
| L523 | Enter `request_transaction(factory)` — Open a short session/transaction context that commits on success, rolls back on exception, and closes the session and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L524 | Compute the return value: `lifecycle.mark_turn_failed(session, user_message_id=user_message_id, generation_token=generation_token, error_code=error_code, error_message=error_message)` — Call [lifecycle.mark_turn_failed](../repositories/messages.md#walk-mark-turn-failed) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L525 | Supply positional argument 1 to `lifecycle.mark_turn_failed`: the current `session` value. |
| L526 | Supply `user_message_id` = `user_message_id`.  Evaluate the value as: the current `user_message_id` value. |
| L527 | Supply `generation_token` = `generation_token`. Generation claim token used to fence a late answer. Evaluate the value as: the current `generation_token` value. |
| L528 | Supply `error_code` = `error_code`. Machine-readable failure category stored or exposed by the operation. Evaluate the value as: the current `error_code` value. |
| L529 | Supply `error_message` = `error_message`. Human-readable failure detail; truncation alone does not redact sensitive content. Evaluate the value as: the current `error_message` value. |
| L530 | Close the expression/container begun at L524; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L531 | Handle `Exception`; only a matching error from the associated try enters this body. |
| L532 | Compute the return value: `False`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
