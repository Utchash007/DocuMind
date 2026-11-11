# `app/api/conversations.py`

[Source](../../../../Backend/app/api/conversations.py) · [Backend index](../../README.md)

`RouterDep` and `router` reference the same router at `/projects/{project_id}/conversations`. This module also supplies `PrincipalDep`, `SessionFactoryDep`, and `api_error` to message routes. Handlers use `request_transaction(factory)` to commit/rollback and close before returning.

## Functions

### `api_error(status_code: int, code: ErrorCode, message: str, **ids: object) -> HTTPException`

**Arguments:** HTTP status, machine code, message, optional resource IDs. **Returns:** Exception for callers to raise. **Work:** Constructs `ApiError`, dumps aliases in JSON mode, and puts it in FastAPI's `detail` envelope.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-api-error"></a>

#### Line-by-line execution

[Current source: lines 42–52](../../../../Backend/app/api/conversations.py#L42-L52). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `status_code` | `int`; required; positional or keyword | Caller-supplied status code; each read, transformation, and validation is traced below. |
| `code` | `ErrorCode`; required; positional or keyword | Caller-supplied code; each read, transformation, and validation is traced below. |
| `message` | `str`; required; positional or keyword | Caller-supplied message; each read, transformation, and validation is traced below. |
| `ids` | `object`; implicitly supplied/collected; ** keyword extras | Caller-supplied ids; each read, transformation, and validation is traced below. |

**Declared result:** `HTTPException`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  42 | def api_error(
  43 |     status_code: int,
  44 |     code: ErrorCode,
  45 |     message: str,
  46 |     **ids: object,
  47 | ) -> HTTPException:
  48 |     """Build an ``{"detail": ApiError}`` HTTP error (frozen envelope)."""
  49 |     payload = ApiError(code=code, message=message, **ids).model_dump(  # type: ignore[arg-type]
  50 |         by_alias=True, mode="json"
  51 |     )
  52 |     return HTTPException(status_code=status_code, detail=payload)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L42 | Define `api_error`; bind its arguments when called. The body executes only when invoked. |
| L43 | Declare parameter `status_code` with annotation `int`. Caller-supplied status code; its uses and transformations are traced below. |
| L44 | Declare parameter `code` with annotation `ErrorCode`. Caller-supplied code; its uses and transformations are traced below. |
| L45 | Declare parameter `message` with annotation `str`. Caller-supplied message; its uses and transformations are traced below. |
| L46 | Declare parameter `ids` with annotation `object`. Caller-supplied ids; its uses and transformations are traced below. |
| L47 | Finish/continue the signature; the declared return annotation is `HTTPException`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L48 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L49 | Evaluate the right-hand side, then bind/store it in `payload`: `ApiError(code=code, message=message, **ids).model_dump(by_alias=True, mode='json')` — Serialize Pydantic fields into a dictionary; by_alias=True uses wire names and mode='json' converts JSON-compatible values; first obtain the receiver: `ApiError(code=code, message=message, **ids)` — Construct `ApiError` with the supplied diagnostic fields; the surrounding raise determines propagation. |
| L50 | Supply `by_alias` = `True`.  Evaluate the value as: `True`. Supply `mode` = `'json'`.  Evaluate the value as: `'json'`. |
| L51 | Close the expression/container begun at L49; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L52 | Compute the return value: `HTTPException(status_code=status_code, detail=payload)` — Construct a FastAPI exception carrying the chosen status and response detail; raising it ends the handler. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `get_current_principal(request: Request) -> AuthenticatedUser`

**Arguments:** HTTP request. **Returns:** Verified, onboarded principal. **Work:** Reads/strips Authorization, lazily imports the real principal resolver, and invokes it. Existing HTTP errors propagate; other exceptions become safe 503. Missing/false onboarding becomes 403. This is wired production identity verification, despite the obsolete integration notes formerly in the header.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-current-principal"></a>

#### Line-by-line execution

[Current source: lines 55–76](../../../../Backend/app/api/conversations.py#L55-L76). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `request` | `Request`; required; positional or keyword | FastAPI/Starlette request object providing headers and request context. |

**Declared result:** `AuthenticatedUser`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  55 | def get_current_principal(request: Request) -> AuthenticatedUser:
  56 |     """Verify the Appwrite principal and require completed onboarding."""
  57 |     authorization = request.headers.get("Authorization", "").strip()
  58 |     from app.auth.principal import get_principal_resolver
  59 | 
  60 |     try:
  61 |         user = get_principal_resolver().resolve_principal(authorization)
  62 |     except HTTPException:
  63 |         raise
  64 |     except Exception as exc:  # provider outage fails closed (retryable)
  65 |         raise api_error(
  66 |             503,
  67 |             ErrorCode.SERVICE_UNAVAILABLE,
  68 |             "Identity verification is temporarily unavailable.",
  69 |         ) from exc
  70 |     if not bool(getattr(user, "onboarding_completed", False)):
  71 |         raise api_error(
  72 |             403,
  73 |             ErrorCode.ONBOARDING_REQUIRED,
  74 |             "Complete your profile before using the workspace.",
  75 |         )
  76 |     return user
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L55 | Define `get_current_principal`; bind its arguments when called. The body executes only when invoked. |
| L56 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L57 | Evaluate the right-hand side, then bind/store it in `authorization`: `request.headers.get('Authorization', '').strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed; first obtain the receiver: `request.headers.get('Authorization', '')` — Look up `'Authorization'` in `request.headers`, using `''` when the key is absent (an existing null value is not replaced). |
| L58 | Import `get_principal_resolver` from `app.auth.principal`; inside a function this import is deferred until this path is reached. |
| L60 | Enter the protected block; failures are matched against `HTTPException`, `Exception` in order. |
| L61 | Evaluate the right-hand side, then bind/store it in `user`: `get_principal_resolver().resolve_principal(authorization)` — Invoke `get_principal_resolver().resolve_principal` with the shown inputs and use its result; see the function overview for its role in this flow; first obtain the receiver: `get_principal_resolver()` — Call [get_principal_resolver](../auth/principal.md#walk-get-principal-resolver) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L62 | Handle `HTTPException`; only a matching error from the associated try enters this body. |
| L63 | Re-raise the currently handled exception with its traceback; no replacement result is returned. |
| L64 | Handle `Exception` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L65 | Raise `api_error(503, ErrorCode.SERVICE_UNAVAILABLE, 'Identity verification is temporarily unavailable.')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L66 | Supply positional argument 1 to `api_error`: `503`. |
| L67 | Supply positional argument 2 to `api_error`: the `SERVICE_UNAVAILABLE` attribute of `ErrorCode`. |
| L68 | Supply positional argument 3 to `api_error`: `'Identity verification is temporarily unavailable.'`. |
| L69 | Contribute the current `exc` value to the expression being assembled. |
| L70 | Evaluate the branch condition: invert the truthiness of `bool(getattr(user, 'onboarding_completed', False))`. If truthy, enter L71; otherwise skip this indented block and continue after it. |
| L71 | Raise `api_error(403, ErrorCode.ONBOARDING_REQUIRED, 'Complete your profile before using the workspace.')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L72 | Supply positional argument 1 to `api_error`: `403`. |
| L73 | Supply positional argument 2 to `api_error`: the `ONBOARDING_REQUIRED` attribute of `ErrorCode`. |
| L74 | Supply positional argument 3 to `api_error`: `'Complete your profile before using the workspace.'`. |
| L75 | Close the expression/container begun at L71; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L76 | Compute the return value: the current `user` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `get_session_factory_dep() -> sessionmaker`

**Arguments:** None. **Returns:** Lazy application session factory. **Work:** Calls `get_session_factory()`; each route later opens its own short transaction.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-session-factory-dep"></a>

#### Line-by-line execution

[Current source: lines 79–81](../../../../Backend/app/api/conversations.py#L79-L81). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `sessionmaker`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  79 | def get_session_factory_dep() -> sessionmaker:
  80 |     """Return the production session factory for short request transactions."""
  81 |     return get_session_factory()
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L79 | Define `get_session_factory_dep`; bind its arguments when called. The body executes only when invoked. |
| L80 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L81 | Compute the return value: `get_session_factory()` — Call [get_session_factory](../db/session.md#walk-get-session-factory) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `list_conversations(project_id, principal, factory, cursor=None, limit=50) -> PaginatedResponse[ConversationDto]`

**Route:** Collection GET (200). **Arguments:** Project path UUID, injected principal/factory, optional cursor, bounded 1–200 limit. **Returns:** Activity-ordered page. **Work:** Calls repository listing in a transaction with the principal's internal owner ID; translates `NotFoundError` to 404 and `CursorError` to 422.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-list-conversations"></a>

#### Line-by-line execution

[Current source: lines 93–116](../../../../Backend/app/api/conversations.py#L93-L116). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project_id` | `Annotated[UUID, Path()]`; required; positional or keyword | Project UUID used to constrain resource lookup or provider metadata. |
| `principal` | `PrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `factory` | `SessionFactoryDep`; required; positional or keyword | Session factory used to open a short database unit of work. |
| `cursor` | `Annotated[str \| None, Query(description='Opaque nextCursor from the previous page')]`; default `None`; positional or keyword | Opaque page continuation token; null starts the first page. |
| `limit` | `Annotated[int, Query(ge=1, le=200, description='Bounded page size (1-200)')]`; default `50`; positional or keyword | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |

**Declared result:** `PaginatedResponse[ConversationDto]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  93 | @router.get("", response_model=PaginatedResponse[ConversationDto], response_model_by_alias=True)
  94 | def list_conversations(
  95 |     project_id: Annotated[UUID, Path()],
  96 |     principal: PrincipalDep,
  97 |     factory: SessionFactoryDep,
  98 |     cursor: Annotated[str | None, Query(description="Opaque nextCursor from the previous page")] = None,
  99 |     limit: Annotated[int, Query(ge=1, le=200, description="Bounded page size (1-200)")] = 50,
 100 | ) -> PaginatedResponse[ConversationDto]:
 101 |     """List a project's conversations newest-activity-first (``{items, nextCursor}``)."""
 102 |     from app.db.session import request_transaction
 103 | 
 104 |     try:
 105 |         with request_transaction(factory) as session:
 106 |             return repo.list_conversations(
 107 |                 session,
 108 |                 user_id=principal.id,
 109 |                 project_id=project_id,
 110 |                 cursor=cursor,
 111 |                 limit=limit,
 112 |             )
 113 |     except repo.NotFoundError as exc:
 114 |         raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc
 115 |     except CursorError as exc:
 116 |         raise api_error(422, ErrorCode.VALIDATION_ERROR, str(exc)) from exc
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L93 | Register the handler with FastAPI using `router.get('', response_model=PaginatedResponse[ConversationDto], response_model_by_alias=True)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L94 | Define `list_conversations`; bind its arguments when called. The body executes only when invoked. |
| L95 | Declare parameter `project_id` with annotation `Annotated[UUID, Path()]`. Project UUID used to constrain resource lookup or provider metadata. |
| L96 | Declare parameter `principal` with annotation `PrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L97 | Declare parameter `factory` with annotation `SessionFactoryDep`. Session factory used to open a short database unit of work. |
| L98 | Declare parameter `cursor` with annotation `Annotated[str \| None, Query(description='Opaque nextCursor from the previous page')]`. Opaque page continuation token; null starts the first page. |
| L99 | Declare parameter `limit` with annotation `Annotated[int, Query(ge=1, le=200, description='Bounded page size (1-200)')]`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. |
| L100 | Finish/continue the signature; the declared return annotation is `PaginatedResponse[ConversationDto]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L101 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L102 | Import `request_transaction` from `app.db.session`; inside a function this import is deferred until this path is reached. |
| L104 | Enter the protected block; failures are matched against `repo.NotFoundError`, `CursorError` in order. |
| L105 | Enter `request_transaction(factory)` — Open a short session/transaction context that commits on success, rolls back on exception, and closes the session and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L106 | Compute the return value: `repo.list_conversations(session, user_id=principal.id, project_id=project_id, cursor=cursor, limit=limit)` — Call [repo.list_conversations](../repositories/conversations.md#walk-list-conversations) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L107 | Supply positional argument 1 to `repo.list_conversations`: the current `session` value. |
| L108 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. |
| L109 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L110 | Supply `cursor` = `cursor`. Opaque page continuation token; null starts the first page. Evaluate the value as: the current `cursor` value. |
| L111 | Supply `limit` = `limit`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. Evaluate the value as: the current `limit` value. |
| L112 | Close the expression/container begun at L106; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L113 | Handle `repo.NotFoundError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L114 | Raise `api_error(404, ErrorCode.NOT_FOUND, str(exc))`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L115 | Handle `CursorError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L116 | Raise `api_error(422, ErrorCode.VALIDATION_ERROR, str(exc))`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |

<!-- END LINE WALKTHROUGH -->

### `create_conversation(project_id, body, principal, factory) -> ConversationDto`

**Route:** Collection POST (201). **Arguments:** Project UUID, `ConversationCreateRequest`, principal/factory. **Returns:** Committed conversation DTO. **Work:** Passes optional title to repository creation within a transaction; missing/foreign project becomes 404.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-create-conversation"></a>

#### Line-by-line execution

[Current source: lines 119–138](../../../../Backend/app/api/conversations.py#L119-L138). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project_id` | `Annotated[UUID, Path()]`; required; positional or keyword | Project UUID used to constrain resource lookup or provider metadata. |
| `body` | `ConversationCreateRequest`; required; positional or keyword | Validated request-body DTO supplied by FastAPI. |
| `principal` | `PrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `factory` | `SessionFactoryDep`; required; positional or keyword | Session factory used to open a short database unit of work. |

**Declared result:** `ConversationDto`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 119 | @router.post("", response_model=ConversationDto, status_code=201, response_model_by_alias=True)
 120 | def create_conversation(
 121 |     project_id: Annotated[UUID, Path()],
 122 |     body: ConversationCreateRequest,
 123 |     principal: PrincipalDep,
 124 |     factory: SessionFactoryDep,
 125 | ) -> ConversationDto:
 126 |     """Create an independent conversation (``201`` with the persisted row)."""
 127 |     from app.db.session import request_transaction
 128 | 
 129 |     try:
 130 |         with request_transaction(factory) as session:
 131 |             return repo.create_conversation(
 132 |                 session,
 133 |                 user_id=principal.id,
 134 |                 project_id=project_id,
 135 |                 title=body.title,
 136 |             )
 137 |     except repo.NotFoundError as exc:
 138 |         raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L119 | Register the handler with FastAPI using `router.post('', response_model=ConversationDto, status_code=201, response_model_by_alias=True)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L120 | Define `create_conversation`; bind its arguments when called. The body executes only when invoked. |
| L121 | Declare parameter `project_id` with annotation `Annotated[UUID, Path()]`. Project UUID used to constrain resource lookup or provider metadata. |
| L122 | Declare parameter `body` with annotation `ConversationCreateRequest`. Validated request-body DTO supplied by FastAPI. |
| L123 | Declare parameter `principal` with annotation `PrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L124 | Declare parameter `factory` with annotation `SessionFactoryDep`. Session factory used to open a short database unit of work. |
| L125 | Finish/continue the signature; the declared return annotation is `ConversationDto`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L126 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L127 | Import `request_transaction` from `app.db.session`; inside a function this import is deferred until this path is reached. |
| L129 | Enter the protected block; failures are matched against `repo.NotFoundError` in order. |
| L130 | Enter `request_transaction(factory)` — Open a short session/transaction context that commits on success, rolls back on exception, and closes the session and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L131 | Compute the return value: `repo.create_conversation(session, user_id=principal.id, project_id=project_id, title=body.title)` — Call [repo.create_conversation](../repositories/conversations.md#walk-create-conversation) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L132 | Supply positional argument 1 to `repo.create_conversation`: the current `session` value. |
| L133 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. |
| L134 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L135 | Supply `title` = `body.title`. Conversation title; null/default/blank handling is implemented below. Evaluate the value as: the `title` attribute of `body`. |
| L136 | Close the expression/container begun at L131; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L137 | Handle `repo.NotFoundError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L138 | Raise `api_error(404, ErrorCode.NOT_FOUND, str(exc))`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |

<!-- END LINE WALKTHROUGH -->

### `get_conversation(project_id, conversation_id, principal, factory) -> ConversationDto`

**Route:** Item GET (200). **Arguments:** Both path UUIDs, principal/factory. **Returns:** Owned DTO. **Work:** Performs repository read in a transaction and maps missing/inaccessible scope to 404.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-conversation"></a>

#### Line-by-line execution

[Current source: lines 141–160](../../../../Backend/app/api/conversations.py#L141-L160). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project_id` | `Annotated[UUID, Path()]`; required; positional or keyword | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `Annotated[UUID, Path()]`; required; positional or keyword | Conversation UUID identifying the owned chat and ordered message sequence. |
| `principal` | `PrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `factory` | `SessionFactoryDep`; required; positional or keyword | Session factory used to open a short database unit of work. |

**Declared result:** `ConversationDto`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 141 | @router.get("/{conversation_id}", response_model=ConversationDto, response_model_by_alias=True)
 142 | def get_conversation(
 143 |     project_id: Annotated[UUID, Path()],
 144 |     conversation_id: Annotated[UUID, Path()],
 145 |     principal: PrincipalDep,
 146 |     factory: SessionFactoryDep,
 147 | ) -> ConversationDto:
 148 |     """Read one owned conversation."""
 149 |     from app.db.session import request_transaction
 150 | 
 151 |     try:
 152 |         with request_transaction(factory) as session:
 153 |             return repo.get_conversation(
 154 |                 session,
 155 |                 user_id=principal.id,
 156 |                 project_id=project_id,
 157 |                 conversation_id=conversation_id,
 158 |             )
 159 |     except repo.NotFoundError as exc:
 160 |         raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L141 | Register the handler with FastAPI using `router.get('/{conversation_id}', response_model=ConversationDto, response_model_by_alias=True)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L142 | Define `get_conversation`; bind its arguments when called. The body executes only when invoked. |
| L143 | Declare parameter `project_id` with annotation `Annotated[UUID, Path()]`. Project UUID used to constrain resource lookup or provider metadata. |
| L144 | Declare parameter `conversation_id` with annotation `Annotated[UUID, Path()]`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L145 | Declare parameter `principal` with annotation `PrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L146 | Declare parameter `factory` with annotation `SessionFactoryDep`. Session factory used to open a short database unit of work. |
| L147 | Finish/continue the signature; the declared return annotation is `ConversationDto`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L148 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L149 | Import `request_transaction` from `app.db.session`; inside a function this import is deferred until this path is reached. |
| L151 | Enter the protected block; failures are matched against `repo.NotFoundError` in order. |
| L152 | Enter `request_transaction(factory)` — Open a short session/transaction context that commits on success, rolls back on exception, and closes the session and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L153 | Compute the return value: `repo.get_conversation(session, user_id=principal.id, project_id=project_id, conversation_id=conversation_id)` — Call [repo.get_conversation](../repositories/conversations.md#walk-get-conversation) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L154 | Supply positional argument 1 to `repo.get_conversation`: the current `session` value. |
| L155 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. |
| L156 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L157 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L158 | Close the expression/container begun at L153; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L159 | Handle `repo.NotFoundError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L160 | Raise `api_error(404, ErrorCode.NOT_FOUND, str(exc))`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |

<!-- END LINE WALKTHROUGH -->

### `rename_conversation(project_id, conversation_id, body, principal, factory) -> ConversationDto`

**Route:** Item PATCH (200). **Arguments:** Path UUIDs, validated `ConversationUpdateRequest`, principal/factory. **Returns:** Committed renamed DTO. **Work:** Passes `body.title` and authenticated scope to repository rename, commits on context exit, maps not-found to 404.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-rename-conversation"></a>

#### Line-by-line execution

[Current source: lines 163–184](../../../../Backend/app/api/conversations.py#L163-L184). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project_id` | `Annotated[UUID, Path()]`; required; positional or keyword | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `Annotated[UUID, Path()]`; required; positional or keyword | Conversation UUID identifying the owned chat and ordered message sequence. |
| `body` | `ConversationUpdateRequest`; required; positional or keyword | Validated request-body DTO supplied by FastAPI. |
| `principal` | `PrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `factory` | `SessionFactoryDep`; required; positional or keyword | Session factory used to open a short database unit of work. |

**Declared result:** `ConversationDto`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 163 | @router.patch("/{conversation_id}", response_model=ConversationDto, response_model_by_alias=True)
 164 | def rename_conversation(
 165 |     project_id: Annotated[UUID, Path()],
 166 |     conversation_id: Annotated[UUID, Path()],
 167 |     body: ConversationUpdateRequest,
 168 |     principal: PrincipalDep,
 169 |     factory: SessionFactoryDep,
 170 | ) -> ConversationDto:
 171 |     """Rename an owned conversation."""
 172 |     from app.db.session import request_transaction
 173 | 
 174 |     try:
 175 |         with request_transaction(factory) as session:
 176 |             return repo.rename_conversation(
 177 |                 session,
 178 |                 user_id=principal.id,
 179 |                 project_id=project_id,
 180 |                 conversation_id=conversation_id,
 181 |                 title=body.title,
 182 |             )
 183 |     except repo.NotFoundError as exc:
 184 |         raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L163 | Register the handler with FastAPI using `router.patch('/{conversation_id}', response_model=ConversationDto, response_model_by_alias=True)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L164 | Define `rename_conversation`; bind its arguments when called. The body executes only when invoked. |
| L165 | Declare parameter `project_id` with annotation `Annotated[UUID, Path()]`. Project UUID used to constrain resource lookup or provider metadata. |
| L166 | Declare parameter `conversation_id` with annotation `Annotated[UUID, Path()]`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L167 | Declare parameter `body` with annotation `ConversationUpdateRequest`. Validated request-body DTO supplied by FastAPI. |
| L168 | Declare parameter `principal` with annotation `PrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L169 | Declare parameter `factory` with annotation `SessionFactoryDep`. Session factory used to open a short database unit of work. |
| L170 | Finish/continue the signature; the declared return annotation is `ConversationDto`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L171 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L172 | Import `request_transaction` from `app.db.session`; inside a function this import is deferred until this path is reached. |
| L174 | Enter the protected block; failures are matched against `repo.NotFoundError` in order. |
| L175 | Enter `request_transaction(factory)` — Open a short session/transaction context that commits on success, rolls back on exception, and closes the session and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L176 | Compute the return value: `repo.rename_conversation(session, user_id=principal.id, project_id=project_id, conversation_id=conversation_id, title=body.title)` — Call [repo.rename_conversation](../repositories/conversations.md#walk-rename-conversation) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L177 | Supply positional argument 1 to `repo.rename_conversation`: the current `session` value. |
| L178 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. |
| L179 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L180 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L181 | Supply `title` = `body.title`. Conversation title; null/default/blank handling is implemented below. Evaluate the value as: the `title` attribute of `body`. |
| L182 | Close the expression/container begun at L176; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L183 | Handle `repo.NotFoundError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L184 | Raise `api_error(404, ErrorCode.NOT_FOUND, str(exc))`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |

<!-- END LINE WALKTHROUGH -->

### `delete_conversation(project_id, conversation_id, principal, factory) -> ConversationDeleteAccepted`

**Route:** Item DELETE (200). **Arguments:** Path UUIDs and principal/factory. **Returns:** `{conversationId, accepted: true}`. **Work:** Deletes conversation/messages through the repository in a transaction, then builds acceptance after commit; not-found becomes 404. There is no queued deletion stage.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-delete-conversation"></a>

#### Line-by-line execution

[Current source: lines 187–207](../../../../Backend/app/api/conversations.py#L187-L207). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project_id` | `Annotated[UUID, Path()]`; required; positional or keyword | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `Annotated[UUID, Path()]`; required; positional or keyword | Conversation UUID identifying the owned chat and ordered message sequence. |
| `principal` | `PrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `factory` | `SessionFactoryDep`; required; positional or keyword | Session factory used to open a short database unit of work. |

**Declared result:** `ConversationDeleteAccepted`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 187 | @router.delete("/{conversation_id}", response_model=ConversationDeleteAccepted, response_model_by_alias=True)
 188 | def delete_conversation(
 189 |     project_id: Annotated[UUID, Path()],
 190 |     conversation_id: Annotated[UUID, Path()],
 191 |     principal: PrincipalDep,
 192 |     factory: SessionFactoryDep,
 193 | ) -> ConversationDeleteAccepted:
 194 |     """Delete a conversation and its messages synchronously (``200``)."""
 195 |     from app.db.session import request_transaction
 196 | 
 197 |     try:
 198 |         with request_transaction(factory) as session:
 199 |             deleted_id = repo.delete_conversation(
 200 |                 session,
 201 |                 user_id=principal.id,
 202 |                 project_id=project_id,
 203 |                 conversation_id=conversation_id,
 204 |             )
 205 |     except repo.NotFoundError as exc:
 206 |         raise api_error(404, ErrorCode.NOT_FOUND, str(exc)) from exc
 207 |     return ConversationDeleteAccepted(conversation_id=deleted_id, accepted=True)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L187 | Register the handler with FastAPI using `router.delete('/{conversation_id}', response_model=ConversationDeleteAccepted, response_model_by_alias=True)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L188 | Define `delete_conversation`; bind its arguments when called. The body executes only when invoked. |
| L189 | Declare parameter `project_id` with annotation `Annotated[UUID, Path()]`. Project UUID used to constrain resource lookup or provider metadata. |
| L190 | Declare parameter `conversation_id` with annotation `Annotated[UUID, Path()]`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L191 | Declare parameter `principal` with annotation `PrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L192 | Declare parameter `factory` with annotation `SessionFactoryDep`. Session factory used to open a short database unit of work. |
| L193 | Finish/continue the signature; the declared return annotation is `ConversationDeleteAccepted`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L194 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L195 | Import `request_transaction` from `app.db.session`; inside a function this import is deferred until this path is reached. |
| L197 | Enter the protected block; failures are matched against `repo.NotFoundError` in order. |
| L198 | Enter `request_transaction(factory)` — Open a short session/transaction context that commits on success, rolls back on exception, and closes the session and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L199 | Evaluate the right-hand side, then bind/store it in `deleted_id`: `repo.delete_conversation(session, user_id=principal.id, project_id=project_id, conversation_id=conversation_id)` — Call [repo.delete_conversation](../repositories/conversations.md#walk-delete-conversation) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L200 | Supply positional argument 1 to `repo.delete_conversation`: the current `session` value. |
| L201 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. |
| L202 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L203 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L204 | Close the expression/container begun at L199; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L205 | Handle `repo.NotFoundError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L206 | Raise `api_error(404, ErrorCode.NOT_FOUND, str(exc))`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L207 | Compute the return value: `ConversationDeleteAccepted(conversation_id=deleted_id, accepted=True)` — Construct `ConversationDeleteAccepted` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
