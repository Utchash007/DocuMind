# `app/repositories/conversations.py`

[Source](../../../../Backend/app/repositories/conversations.py) · [Backend index](../../README.md)

Owner-scoped conversation CRUD and chronological message listing. Callers supply short transactions; mutations flush without committing. `NotFoundError` and `CursorError` are marker exceptions translated by routes to 404/422. Pagination bounds are validated at the route, not repeated by these list helpers.

## Functions

### `to_conversation_dto(row: Conversation) -> ConversationDto`

**Arguments:** ORM conversation. **Returns:** DTO with ID/project/title/timestamps. **Work:** Explicitly copies only those five fields.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-to-conversation-dto"></a>

#### Line-by-line execution

[Current source: lines 51–59](../../../../Backend/app/repositories/conversations.py#L51-L59). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `row` | `Conversation`; required; positional or keyword | Loaded ORM row being converted or examined; this helper does not obtain ownership from the row's filename. |

**Declared result:** `ConversationDto`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  51 | def to_conversation_dto(row: Conversation) -> ConversationDto:
  52 |     """Convert an ORM conversation row to its public DTO."""
  53 |     return ConversationDto(
  54 |         id=row.id,
  55 |         project_id=row.project_id,
  56 |         title=row.title,
  57 |         created_at=row.created_at,
  58 |         updated_at=row.updated_at,
  59 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L51 | Define `to_conversation_dto`; bind its arguments when called. The body executes only when invoked. |
| L52 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L53 | Compute the return value: `ConversationDto(id=row.id, project_id=row.project_id, title=row.title, created_at=row.created_at, updated_at=row.updated_at)` — Construct `ConversationDto` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L54 | Supply `id` = `row.id`.  Evaluate the value as: the `id` attribute of `row`. |
| L55 | Supply `project_id` = `row.project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the `project_id` attribute of `row`. |
| L56 | Supply `title` = `row.title`. Conversation title; null/default/blank handling is implemented below. Evaluate the value as: the `title` attribute of `row`. |
| L57 | Supply `created_at` = `row.created_at`.  Evaluate the value as: the `created_at` attribute of `row`. |
| L58 | Supply `updated_at` = `row.updated_at`.  Evaluate the value as: the `updated_at` attribute of `row`. |
| L59 | Close the expression/container begun at L53; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `to_message_dto(row: Message) -> MessageDto`

**Arguments:** ORM message. **Returns:** Public message DTO. **Work:** Converts each stored citation dictionary into a verified `Citation` (preserving null versus empty list), then copies message identity/content/order/metadata/request/reply/status/expiry/time. Excludes generation token. Invalid stored citation records cause Pydantic validation errors rather than being silently repaired.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-to-message-dto"></a>

#### Line-by-line execution

[Current source: lines 62–83](../../../../Backend/app/repositories/conversations.py#L62-L83). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `row` | `Message`; required; positional or keyword | Loaded ORM row being converted or examined; this helper does not obtain ownership from the row's filename. |

**Declared result:** `MessageDto`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  62 | def to_message_dto(row: Message) -> MessageDto:
  63 |     """Convert an ORM message row to its public DTO.
  64 | 
  65 |     Persisted citations are stored as camelCase JSONB (the public wire
  66 |     shape) and validate as :class:`Citation`. The SQL ``metadata`` column is
  67 |     exposed as the public ``metadata`` field.
  68 |     """
  69 |     citations = [Citation(**entry) for entry in row.citations] if row.citations is not None else None
  70 |     return MessageDto(
  71 |         id=row.id,
  72 |         conversation_id=row.conversation_id,
  73 |         role=row.role,
  74 |         content=row.content,
  75 |         position=row.position,
  76 |         citations=citations,
  77 |         message_metadata=row.message_metadata,
  78 |         client_request_id=row.client_request_id,
  79 |         reply_to_message_id=row.reply_to_message_id,
  80 |         generation_status=row.generation_status,
  81 |         generation_expires_at=row.generation_expires_at,
  82 |         created_at=row.created_at,
  83 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L62 | Define `to_message_dto`; bind its arguments when called. The body executes only when invoked. |
| L63 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L65 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L66 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L67 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L68 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L69 | Evaluate the right-hand side, then bind/store it in `citations`: check `row.citations is not None`; when true use iterate `row.citations`, binding each item to `entry`; produce `Citation(**entry)` into a new list, otherwise None (no value) (only the selected branch is evaluated). |
| L70 | Compute the return value: `MessageDto` with the arguments detailed below — Construct `MessageDto` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L71 | Supply `id` = `row.id`.  Evaluate the value as: the `id` attribute of `row`. |
| L72 | Supply `conversation_id` = `row.conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the `conversation_id` attribute of `row`. |
| L73 | Supply `role` = `row.role`.  Evaluate the value as: the `role` attribute of `row`. |
| L74 | Supply `content` = `row.content`. Message text supplied for a persisted conversation turn. Evaluate the value as: the `content` attribute of `row`. |
| L75 | Supply `position` = `row.position`.  Evaluate the value as: the `position` attribute of `row`. |
| L76 | Supply `citations` = `citations`.  Evaluate the value as: the current `citations` value. |
| L77 | Supply `message_metadata` = `row.message_metadata`.  Evaluate the value as: the `message_metadata` attribute of `row`. |
| L78 | Supply `client_request_id` = `row.client_request_id`. Client request UUID used to deduplicate message sends. Evaluate the value as: the `client_request_id` attribute of `row`. |
| L79 | Supply `reply_to_message_id` = `row.reply_to_message_id`.  Evaluate the value as: the `reply_to_message_id` attribute of `row`. |
| L80 | Supply `generation_status` = `row.generation_status`.  Evaluate the value as: the `generation_status` attribute of `row`. |
| L81 | Supply `generation_expires_at` = `row.generation_expires_at`.  Evaluate the value as: the `generation_expires_at` attribute of `row`. |
| L82 | Supply `created_at` = `row.created_at`.  Evaluate the value as: the `created_at` attribute of `row`. |
| L83 | Close the expression/container begun at L70; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `require_owned_project(session, *, user_id, project_id)`

**Arguments:** Session and internal owner/project UUIDs. **Returns:** Live owned project. **Work:** Delegates to `get_owned_project`; `None` raises `NotFoundError`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-require-owned-project"></a>

#### Line-by-line execution

[Current source: lines 86–91](../../../../Backend/app/repositories/conversations.py#L86-L91). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |

**Declared result:** No return annotation; follow the return/yield lines below. Python supplies None when a non-generator reaches the end without return.

**Numbered source**

```text
  86 | def require_owned_project(session: Session, *, user_id: UUID, project_id: UUID):
  87 |     """Return the project or raise :class:`NotFoundError`."""
  88 |     project = get_owned_project(session, user_id=user_id, project_id=project_id)
  89 |     if project is None:
  90 |         raise NotFoundError(f"project not found: {project_id}")
  91 |     return project
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L86 | Define `require_owned_project`; bind its arguments when called. The body executes only when invoked. |
| L87 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L88 | Evaluate the right-hand side, then bind/store it in `project`: `get_owned_project(session, user_id=user_id, project_id=project_id)` — Call [get_owned_project](../db/queries.md#walk-get-owned-project) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L89 | Evaluate the branch condition: compare whether `project` is the same object as `None`. If truthy, enter L90; otherwise skip this indented block and continue after it. |
| L90 | Raise `NotFoundError(f'project not found: {project_id}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L91 | Compute the return value: the current `project` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `require_owned_conversation(session, *, user_id, project_id, conversation_id)`

**Arguments:** Session and exact scope UUIDs. **Returns:** Conversation under the owner's live project. **Work:** Delegates to the joined lookup and raises `NotFoundError` on absence/inaccessibility.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-require-owned-conversation"></a>

#### Line-by-line execution

[Current source: lines 94–110](../../../../Backend/app/repositories/conversations.py#L94-L110). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |

**Declared result:** No return annotation; follow the return/yield lines below. Python supplies None when a non-generator reaches the end without return.

**Numbered source**

```text
  94 | def require_owned_conversation(
  95 |     session: Session, *, user_id: UUID, project_id: UUID, conversation_id: UUID
  96 | ):
  97 |     """Return the conversation or raise :class:`NotFoundError`.
  98 | 
  99 |     Missing and unowned conversations raise the same error (``404``), so
 100 |     callers have no existence oracle.
 101 |     """
 102 |     conversation = get_owned_conversation(
 103 |         session,
 104 |         user_id=user_id,
 105 |         project_id=project_id,
 106 |         conversation_id=conversation_id,
 107 |     )
 108 |     if conversation is None:
 109 |         raise NotFoundError(f"conversation not found: {conversation_id}")
 110 |     return conversation
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L94 | Define `require_owned_conversation`; bind its arguments when called. The body executes only when invoked. |
| L95 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L96 | Finish/continue the signature; no return annotation is declared. |
| L97 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L99 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L100 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L101 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L102 | Evaluate the right-hand side, then bind/store it in `conversation`: `get_owned_conversation(session, user_id=user_id, project_id=project_id, conversation_id=conversation_id)` — Call [get_owned_conversation](../db/queries.md#walk-get-owned-conversation) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L103 | Supply positional argument 1 to `get_owned_conversation`: the current `session` value. |
| L104 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L105 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L106 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L107 | Close the expression/container begun at L102; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L108 | Evaluate the branch condition: compare whether `conversation` is the same object as `None`. If truthy, enter L109; otherwise skip this indented block and continue after it. |
| L109 | Raise `NotFoundError(f'conversation not found: {conversation_id}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L110 | Compute the return value: the current `conversation` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `list_conversations(session, *, user_id, project_id, cursor, limit) -> PaginatedResponse[ConversationDto]`

**Arguments:** Session, owner/project UUIDs, nullable cursor, page size. **Returns:** Converted page plus continuation. **Work:** Authorizes project, orders activity `updated_at DESC, id DESC`, decodes a truthy cursor and applies the strict timestamp/ID boundary, fetches `limit+1`, truncates, and encodes `updatedAt`/`id` from the last returned row when more exist. Empty cursor strings are treated as absent.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-list-conversations"></a>

#### Line-by-line execution

[Current source: lines 113–151](../../../../Backend/app/repositories/conversations.py#L113-L151). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `cursor` | `str \| None`; required; keyword-only | Opaque page continuation token; null starts the first page. |
| `limit` | `int`; required; keyword-only | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |

**Declared result:** `PaginatedResponse[ConversationDto]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 113 | def list_conversations(
 114 |     session: Session,
 115 |     *,
 116 |     user_id: UUID,
 117 |     project_id: UUID,
 118 |     cursor: str | None,
 119 |     limit: int,
 120 | ) -> PaginatedResponse[ConversationDto]:
 121 |     """List a project's conversations newest-activity-first."""
 122 |     require_owned_project(session, user_id=user_id, project_id=project_id)
 123 |     statement = (
 124 |         select(Conversation)
 125 |         .where(Conversation.project_id == project_id)
 126 |         .order_by(Conversation.updated_at.desc(), Conversation.id.desc())
 127 |     )
 128 |     if cursor:
 129 |         payload = _decode(payload_cursor=cursor, kind="conversation")
 130 |         seen_updated_at: datetime = payload["updatedAt"]
 131 |         seen_id: UUID = payload["id"]
 132 |         statement = statement.where(
 133 |             or_(
 134 |                 Conversation.updated_at < seen_updated_at,
 135 |                 (Conversation.updated_at == seen_updated_at)
 136 |                 & (Conversation.id < seen_id),
 137 |             )
 138 |         )
 139 |     statement = statement.limit(limit + 1)
 140 |     rows = list(session.scalars(statement))
 141 |     next_cursor: str | None = None
 142 |     if len(rows) > limit:
 143 |         rows = rows[:limit]
 144 |         last = rows[-1]
 145 |         next_cursor = encode_cursor(
 146 |             {"updatedAt": last.updated_at.isoformat(), "id": str(last.id)}
 147 |         )
 148 |     return PaginatedResponse[ConversationDto](
 149 |         items=[to_conversation_dto(row) for row in rows],
 150 |         next_cursor=next_cursor,
 151 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L113 | Define `list_conversations`; bind its arguments when called. The body executes only when invoked. |
| L114 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L115 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L116 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L117 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L118 | Declare parameter `cursor` with annotation `str \| None`. Opaque page continuation token; null starts the first page. |
| L119 | Declare parameter `limit` with annotation `int`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. |
| L120 | Finish/continue the signature; the declared return annotation is `PaginatedResponse[ConversationDto]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L121 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L122 | `require_owned_project(session, user_id=user_id, project_id=project_id)` — Call [require_owned_project](#walk-require-owned-project) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L123 | Evaluate the right-hand side, then bind/store it in `statement`: `select(Conversation).where(Conversation.project_id == project_id).order_by(Conversation.updated_at.desc(), Conversation.id.desc())` — Set SQL result ordering in the listed priority order; first obtain the receiver: `select(Conversation).where(Conversation.project_id == project_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(Conversation)` — Construct a SQL SELECT expression; building it does not execute SQL; inputs include `Conversation.updated_at.desc()` — Order this SQL expression descending; `Conversation.id.desc()` — Order this SQL expression descending. |
| L124 | `select(Conversation)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L125 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L126 | Set SQL result ordering in the listed priority order; apply this method to the result built by the preceding chain. |
| L127 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L128 | Evaluate the branch condition: the current `cursor` value. If truthy, enter L129; otherwise skip this indented block and continue after it. |
| L129 | Evaluate the right-hand side, then bind/store it in `payload`: `_decode(payload_cursor=cursor, kind='conversation')` — Call [_decode](#walk--decode) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L130 | Evaluate the right-hand side, then bind/store it in `seen_updated_at`: look up index/key `'updatedAt'` in `payload`; a missing key or out-of-range index raises. |
| L131 | Evaluate the right-hand side, then bind/store it in `seen_id`: look up index/key `'id'` in `payload`; a missing key or out-of-range index raises. |
| L132 | Evaluate the right-hand side, then bind/store it in `statement`: `statement.where(or_(Conversation.updated_at < seen_updated_at, (Conversation.updated_at == seen_updated_at) & (Conversation.id < seen_id)))` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; inputs include `or_(Conversation.updated_at < seen_updated_at, (Conversation.updated_at == seen_updated_at) & (Conversation.id < seen_id))` — Combine SQL predicates with OR so at least one condition must hold. |
| L133 | `or_(Conversation.updated_at < seen_updated_at, (Conversation.updated_at == seen_updated_at) & (Conversation.id < seen_id))` — Combine SQL predicates with OR so at least one condition must hold; inputs include combine with & `Conversation.updated_at == seen_updated_at` and `Conversation.id < seen_id`, following the parentheses/operator precedence shown in `(Conversation.updated_at == seen_updated_at) & (Conversation.id < seen_id)`. |
| L134 | Continue the enclosing expression: build a SQL predicate requiring `Conversation.updated_at` is less than `seen_updated_at`. |
| L135 | Continue the enclosing expression: combine with & `Conversation.updated_at == seen_updated_at` and `Conversation.id < seen_id`, following the parentheses/operator precedence shown in `(Conversation.updated_at == seen_updated_at) & (Conversation.id < seen_id)`. |
| L136 | Continue the enclosing expression: build a SQL predicate requiring `Conversation.id` is less than `seen_id`. |
| L137 | Close the expression/container begun at L133; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L138 | Close the expression/container begun at L132; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L139 | Evaluate the right-hand side, then bind/store it in `statement`: `statement.limit(limit + 1)` — Apply a SQL row limit; fetching limit+1 allows continuation detection; inputs include add/concatenate `limit` and `1`, following the parentheses/operator precedence shown in `limit + 1`. |
| L140 | Evaluate the right-hand side, then bind/store it in `rows`: `list(session.scalars(statement))` — Materialize the iterable in order into a list (or create an empty list); inputs include `session.scalars(statement)` — Execute the SQL expression and expose first-column values through a ScalarResult. |
| L141 | Evaluate the right-hand side, then bind/store it in `next_cursor`: None (no value). |
| L142 | Evaluate the branch condition: compare whether `len(rows)` is greater than `limit`. If truthy, enter L143; otherwise skip this indented block and continue after it. |
| L143 | Evaluate the right-hand side, then bind/store it in `rows`: slice `rows` from the beginning up to `limit` (exclusive stop). |
| L144 | Evaluate the right-hand side, then bind/store it in `last`: look up index/key `-1` in `rows`; a missing key or out-of-range index raises. |
| L145 | Evaluate the right-hand side, then bind/store it in `next_cursor`: `encode_cursor({'updatedAt': last.updated_at.isoformat(), 'id': str(last.id)})` — Call [encode_cursor](../schemas/common.md#walk-encode-cursor) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L146 | Add mapping entry `'updatedAt'`: `last.updated_at.isoformat()` — Format the timestamp/date as an ISO-format string for the cursor/payload. Add mapping entry `'id'`: `str(last.id)` — Convert the input to its string representation. |
| L147 | Close the expression/container begun at L145; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L148 | Compute the return value: `PaginatedResponse[ConversationDto](items=[to_conversation_dto(row) for row in rows], next_cursor=next_cursor)` — Construct `PaginatedResponse[ConversationDto]` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L149 | Supply `items` = `[to_conversation_dto(row) for row in rows]`.  Evaluate the value as: iterate `rows`, binding each item to `row`; produce `to_conversation_dto(row)` into a new list. |
| L150 | Supply `next_cursor` = `next_cursor`. Continuation token to include in the returned page envelope, or null at the end. Evaluate the value as: the current `next_cursor` value. |
| L151 | Close the expression/container begun at L148; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `create_conversation(session, *, user_id, project_id, title: str | None) -> ConversationDto`

**Arguments:** Session, owner/project IDs, validated optional title. **Returns:** New DTO. **Work:** Requires project ownership, adds/flushed `Conversation`, then converts it. Does not generate a title automatically.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-create-conversation"></a>

#### Line-by-line execution

[Current source: lines 154–166](../../../../Backend/app/repositories/conversations.py#L154-L166). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `title` | `str \| None`; required; keyword-only | Conversation title; null/default/blank handling is implemented below. |

**Declared result:** `ConversationDto`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 154 | def create_conversation(
 155 |     session: Session,
 156 |     *,
 157 |     user_id: UUID,
 158 |     project_id: UUID,
 159 |     title: str | None,
 160 | ) -> ConversationDto:
 161 |     """Create a conversation in an owned project."""
 162 |     require_owned_project(session, user_id=user_id, project_id=project_id)
 163 |     row = Conversation(project_id=project_id, title=title)
 164 |     session.add(row)
 165 |     session.flush()
 166 |     return to_conversation_dto(row)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L154 | Define `create_conversation`; bind its arguments when called. The body executes only when invoked. |
| L155 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L156 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L157 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L158 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L159 | Declare parameter `title` with annotation `str \| None`. Conversation title; null/default/blank handling is implemented below. |
| L160 | Finish/continue the signature; the declared return annotation is `ConversationDto`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L161 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L162 | `require_owned_project(session, user_id=user_id, project_id=project_id)` — Call [require_owned_project](#walk-require-owned-project) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L163 | Evaluate the right-hand side, then bind/store it in `row`: `Conversation(project_id=project_id, title=title)` — Construct `Conversation` with the shown fields; its class/model initialization rules apply. |
| L164 | `session.add(row)` — Attach the ORM object to this session for insertion/update tracking; this does not commit it. The return value is not assigned here. |
| L165 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L166 | Compute the return value: `to_conversation_dto(row)` — Call [to_conversation_dto](#walk-to-conversation-dto) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `get_conversation(session, *, user_id, project_id, conversation_id) -> ConversationDto`

**Arguments:** Session and scope UUIDs. **Returns:** Owned DTO. **Work:** Calls `require_owned_conversation`, then conversion.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-conversation"></a>

#### Line-by-line execution

[Current source: lines 169–183](../../../../Backend/app/repositories/conversations.py#L169-L183). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |

**Declared result:** `ConversationDto`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 169 | def get_conversation(
 170 |     session: Session,
 171 |     *,
 172 |     user_id: UUID,
 173 |     project_id: UUID,
 174 |     conversation_id: UUID,
 175 | ) -> ConversationDto:
 176 |     """Read one owned conversation."""
 177 |     row = require_owned_conversation(
 178 |         session,
 179 |         user_id=user_id,
 180 |         project_id=project_id,
 181 |         conversation_id=conversation_id,
 182 |     )
 183 |     return to_conversation_dto(row)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L169 | Define `get_conversation`; bind its arguments when called. The body executes only when invoked. |
| L170 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L171 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L172 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L173 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L174 | Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L175 | Finish/continue the signature; the declared return annotation is `ConversationDto`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L176 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L177 | Evaluate the right-hand side, then bind/store it in `row`: `require_owned_conversation(session, user_id=user_id, project_id=project_id, conversation_id=conversation_id)` — Call [require_owned_conversation](#walk-require-owned-conversation) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L178 | Supply positional argument 1 to `require_owned_conversation`: the current `session` value. |
| L179 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L180 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L181 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L182 | Close the expression/container begun at L177; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L183 | Compute the return value: `to_conversation_dto(row)` — Call [to_conversation_dto](#walk-to-conversation-dto) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `rename_conversation(session, *, user_id, project_id, conversation_id, title: str) -> ConversationDto`

**Arguments:** Session, scope UUIDs, validated title. **Returns:** Updated DTO. **Work:** Authorizes row, assigns title, flushes (ORM update timestamp applies), and converts. Validation/commit belong to request model/caller.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-rename-conversation"></a>

#### Line-by-line execution

[Current source: lines 186–203](../../../../Backend/app/repositories/conversations.py#L186-L203). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |
| `title` | `str`; required; keyword-only | Conversation title; null/default/blank handling is implemented below. |

**Declared result:** `ConversationDto`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 186 | def rename_conversation(
 187 |     session: Session,
 188 |     *,
 189 |     user_id: UUID,
 190 |     project_id: UUID,
 191 |     conversation_id: UUID,
 192 |     title: str,
 193 | ) -> ConversationDto:
 194 |     """Rename an owned conversation (bumps ``updated_at`` via ORM onupdate)."""
 195 |     row = require_owned_conversation(
 196 |         session,
 197 |         user_id=user_id,
 198 |         project_id=project_id,
 199 |         conversation_id=conversation_id,
 200 |     )
 201 |     row.title = title
 202 |     session.flush()
 203 |     return to_conversation_dto(row)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L186 | Define `rename_conversation`; bind its arguments when called. The body executes only when invoked. |
| L187 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L188 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L189 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L190 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L191 | Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L192 | Declare parameter `title` with annotation `str`. Conversation title; null/default/blank handling is implemented below. |
| L193 | Finish/continue the signature; the declared return annotation is `ConversationDto`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L194 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L195 | Evaluate the right-hand side, then bind/store it in `row`: `require_owned_conversation(session, user_id=user_id, project_id=project_id, conversation_id=conversation_id)` — Call [require_owned_conversation](#walk-require-owned-conversation) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L196 | Supply positional argument 1 to `require_owned_conversation`: the current `session` value. |
| L197 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L198 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L199 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L200 | Close the expression/container begun at L195; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L201 | Evaluate the right-hand side, then bind/store it in `row.title`: the current `title` value. |
| L202 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L203 | Compute the return value: `to_conversation_dto(row)` — Call [to_conversation_dto](#walk-to-conversation-dto) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `delete_conversation(session, *, user_id, project_id, conversation_id) -> UUID`

**Arguments:** Session and scope UUIDs. **Returns:** Deleted conversation ID. **Work:** Loads owned row, captures ID, calls `session.delete`, flushes cascaded message/reply deletion. No external cleanup job is needed; a later answer persistence cannot find the deleted user turn.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-delete-conversation"></a>

#### Line-by-line execution

[Current source: lines 206–232](../../../../Backend/app/repositories/conversations.py#L206-L232). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |

**Declared result:** `UUID`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 206 | def delete_conversation(
 207 |     session: Session,
 208 |     *,
 209 |     user_id: UUID,
 210 |     project_id: UUID,
 211 |     conversation_id: UUID,
 212 | ) -> UUID:
 213 |     """Delete an owned conversation and its messages in one transaction.
 214 | 
 215 |     Messages cascade from the SQL ``ON DELETE CASCADE`` on
 216 |     ``messages.conversation_id`` (and assistant replies cascade from their
 217 |     user message), so no per-message cleanup is needed.
 218 | 
 219 |     In-flight generations are invalidated by the same delete: a late
 220 |     provider response cannot find the user turn and fails the persist
 221 |     guard in :mod:`app.repositories.messages`.
 222 |     """
 223 |     row = require_owned_conversation(
 224 |         session,
 225 |         user_id=user_id,
 226 |         project_id=project_id,
 227 |         conversation_id=conversation_id,
 228 |     )
 229 |     deleted_id = row.id
 230 |     session.delete(row)
 231 |     session.flush()
 232 |     return deleted_id
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L206 | Define `delete_conversation`; bind its arguments when called. The body executes only when invoked. |
| L207 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L208 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L209 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L210 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L211 | Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L212 | Finish/continue the signature; the declared return annotation is `UUID`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L213 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L215 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L216 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L217 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L219 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L220 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L221 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L222 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L223 | Evaluate the right-hand side, then bind/store it in `row`: `require_owned_conversation(session, user_id=user_id, project_id=project_id, conversation_id=conversation_id)` — Call [require_owned_conversation](#walk-require-owned-conversation) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L224 | Supply positional argument 1 to `require_owned_conversation`: the current `session` value. |
| L225 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L226 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L227 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L228 | Close the expression/container begun at L223; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L229 | Evaluate the right-hand side, then bind/store it in `deleted_id`: the `id` attribute of `row`. |
| L230 | `session.delete(row)` — Mark the ORM row for deletion when the session flushes; mapped cascades also apply. The return value is not assigned here. |
| L231 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L232 | Compute the return value: the current `deleted_id` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `list_messages(session, *, user_id, project_id, conversation_id, cursor, limit) -> PaginatedResponse[MessageDto]`

**Arguments:** Session, exact scope, optional cursor, page size. **Returns:** All-state messages in ascending position order and continuation. **Work:** Authorizes conversation, filters positions greater than the cursor, fetches one extra, converts via `to_message_dto`, and encodes the last returned position when needed. This public history includes failed/cancelled/active messages; prompt history is filtered separately.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-list-messages"></a>

#### Line-by-line execution

[Current source: lines 235–273](../../../../Backend/app/repositories/conversations.py#L235-L273). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |
| `cursor` | `str \| None`; required; keyword-only | Opaque page continuation token; null starts the first page. |
| `limit` | `int`; required; keyword-only | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |

**Declared result:** `PaginatedResponse[MessageDto]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 235 | def list_messages(
 236 |     session: Session,
 237 |     *,
 238 |     user_id: UUID,
 239 |     project_id: UUID,
 240 |     conversation_id: UUID,
 241 |     cursor: str | None,
 242 |     limit: int,
 243 | ) -> PaginatedResponse[MessageDto]:
 244 |     """List a conversation's history chronologically by ``position``.
 245 | 
 246 |     Stable positions make pages immune to inserts mid-traversal (no
 247 |     duplicates or skips).  The cursor is the last returned position; the
 248 |     next page contains ``position > cursor`` in ascending order.
 249 |     """
 250 |     require_owned_conversation(
 251 |         session,
 252 |         user_id=user_id,
 253 |         project_id=project_id,
 254 |         conversation_id=conversation_id,
 255 |     )
 256 |     statement = (
 257 |         select(Message)
 258 |         .where(Message.conversation_id == conversation_id)
 259 |         .order_by(Message.position.asc())
 260 |     )
 261 |     if cursor:
 262 |         payload = _decode(payload_cursor=cursor, kind="message")
 263 |         statement = statement.where(Message.position > payload["position"])
 264 |     statement = statement.limit(limit + 1)
 265 |     rows = list(session.scalars(statement))
 266 |     next_cursor: str | None = None
 267 |     if len(rows) > limit:
 268 |         rows = rows[:limit]
 269 |         next_cursor = encode_cursor({"position": rows[-1].position})
 270 |     return PaginatedResponse[MessageDto](
 271 |         items=[to_message_dto(row) for row in rows],
 272 |         next_cursor=next_cursor,
 273 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L235 | Define `list_messages`; bind its arguments when called. The body executes only when invoked. |
| L236 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L237 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L238 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L239 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L240 | Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L241 | Declare parameter `cursor` with annotation `str \| None`. Opaque page continuation token; null starts the first page. |
| L242 | Declare parameter `limit` with annotation `int`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. |
| L243 | Finish/continue the signature; the declared return annotation is `PaginatedResponse[MessageDto]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L244 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L246 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L247 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L248 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L249 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L250 | `require_owned_conversation(session, user_id=user_id, project_id=project_id, conversation_id=conversation_id)` — Call [require_owned_conversation](#walk-require-owned-conversation) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L251 | Supply positional argument 1 to `require_owned_conversation`: the current `session` value. |
| L252 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L253 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L254 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L255 | Close the expression/container begun at L250; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L256 | Evaluate the right-hand side, then bind/store it in `statement`: `select(Message).where(Message.conversation_id == conversation_id).order_by(Message.position.asc())` — Set SQL result ordering in the listed priority order; first obtain the receiver: `select(Message).where(Message.conversation_id == conversation_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL; inputs include `Message.position.asc()` — Order this SQL expression ascending. |
| L257 | `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L258 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L259 | Set SQL result ordering in the listed priority order; apply this method to the result built by the preceding chain. |
| L260 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L261 | Evaluate the branch condition: the current `cursor` value. If truthy, enter L262; otherwise skip this indented block and continue after it. |
| L262 | Evaluate the right-hand side, then bind/store it in `payload`: `_decode(payload_cursor=cursor, kind='message')` — Call [_decode](#walk--decode) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L263 | Evaluate the right-hand side, then bind/store it in `statement`: `statement.where(Message.position > payload['position'])` — Add SQL filtering predicates; multiple supplied predicates are combined with AND. |
| L264 | Evaluate the right-hand side, then bind/store it in `statement`: `statement.limit(limit + 1)` — Apply a SQL row limit; fetching limit+1 allows continuation detection; inputs include add/concatenate `limit` and `1`, following the parentheses/operator precedence shown in `limit + 1`. |
| L265 | Evaluate the right-hand side, then bind/store it in `rows`: `list(session.scalars(statement))` — Materialize the iterable in order into a list (or create an empty list); inputs include `session.scalars(statement)` — Execute the SQL expression and expose first-column values through a ScalarResult. |
| L266 | Evaluate the right-hand side, then bind/store it in `next_cursor`: None (no value). |
| L267 | Evaluate the branch condition: compare whether `len(rows)` is greater than `limit`. If truthy, enter L268; otherwise skip this indented block and continue after it. |
| L268 | Evaluate the right-hand side, then bind/store it in `rows`: slice `rows` from the beginning up to `limit` (exclusive stop). |
| L269 | Evaluate the right-hand side, then bind/store it in `next_cursor`: `encode_cursor({'position': rows[-1].position})` — Call [encode_cursor](../schemas/common.md#walk-encode-cursor) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L270 | Compute the return value: `PaginatedResponse[MessageDto](items=[to_message_dto(row) for row in rows], next_cursor=next_cursor)` — Construct `PaginatedResponse[MessageDto]` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L271 | Supply `items` = `[to_message_dto(row) for row in rows]`.  Evaluate the value as: iterate `rows`, binding each item to `row`; produce `to_message_dto(row)` into a new list. |
| L272 | Supply `next_cursor` = `next_cursor`. Continuation token to include in the returned page envelope, or null at the end. Evaluate the value as: the current `next_cursor` value. |
| L273 | Close the expression/container begun at L270; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `_decode(*, payload_cursor: str, kind: str) -> dict`

**Arguments:** Encoded cursor and list kind. **Returns:** Typed `{"updatedAt": datetime, "id": UUID}` for `conversation`, otherwise `{"position": int}`. **Work:** Decodes the object, parses fields, rejects a timezone-naive conversation time or position <1, and wraps parse failures as `CursorError`. Position uses `int(...)` coercion rather than strict JSON integer checking.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--decode"></a>

#### Line-by-line execution

[Current source: lines 276–297](../../../../Backend/app/repositories/conversations.py#L276-L297). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `payload_cursor` | `str`; required; keyword-only | Caller-supplied payload cursor; each read, transformation, and validation is traced below. |
| `kind` | `str`; required; keyword-only | Caller-supplied kind; each read, transformation, and validation is traced below. |

**Declared result:** `dict`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 276 | def _decode(*, payload_cursor: str, kind: str) -> dict:
 277 |     """Decode and validate a cursor payload for the given list kind."""
 278 |     try:
 279 |         payload = decode_cursor(payload_cursor)
 280 |     except ValueError as exc:
 281 |         raise CursorError("cursor is invalid") from exc
 282 |     if kind == "conversation":
 283 |         try:
 284 |             updated_at = datetime.fromisoformat(str(payload["updatedAt"]))
 285 |             rid = UUID(str(payload["id"]))
 286 |         except (KeyError, ValueError, TypeError) as exc:
 287 |             raise CursorError("cursor is invalid") from exc
 288 |         if updated_at.tzinfo is None:
 289 |             raise CursorError("cursor is invalid")
 290 |         return {"updatedAt": updated_at, "id": rid}
 291 |     try:
 292 |         position = int(payload["position"])
 293 |     except (KeyError, ValueError, TypeError) as exc:
 294 |         raise CursorError("cursor is invalid") from exc
 295 |     if position < 1:
 296 |         raise CursorError("cursor is invalid")
 297 |     return {"position": position}
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L276 | Define `_decode`; bind its arguments when called. The body executes only when invoked. |
| L277 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L278 | Enter the protected block; failures are matched against `ValueError` in order. |
| L279 | Evaluate the right-hand side, then bind/store it in `payload`: `decode_cursor(payload_cursor)` — Call [decode_cursor](../schemas/common.md#walk-decode-cursor) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L280 | Handle `ValueError` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L281 | Raise `CursorError('cursor is invalid')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L282 | Evaluate the branch condition: compare whether `kind` equals `'conversation'`. If truthy, enter L283; otherwise skip this indented block and continue after it. |
| L283 | Enter the protected block; failures are matched against `(KeyError, ValueError, TypeError)` in order. |
| L284 | Evaluate the right-hand side, then bind/store it in `updated_at`: `datetime.fromisoformat(str(payload['updatedAt']))` — Parse an ISO-format timestamp; invalid text raises ValueError; inputs include `str(payload['updatedAt'])` — Convert the input to its string representation. |
| L285 | Evaluate the right-hand side, then bind/store it in `rid`: `UUID(str(payload['id']))` — Parse or construct a UUID; invalid text raises a conversion error; inputs include `str(payload['id'])` — Convert the input to its string representation. |
| L286 | Handle `(KeyError, ValueError, TypeError)` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L287 | Raise `CursorError('cursor is invalid')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L288 | Evaluate the branch condition: compare whether `updated_at.tzinfo` is the same object as `None`. If truthy, enter L289; otherwise skip this indented block and continue after it. |
| L289 | Raise `CursorError('cursor is invalid')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L290 | Compute the return value: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L291 | Enter the protected block; failures are matched against `(KeyError, ValueError, TypeError)` in order. |
| L292 | Evaluate the right-hand side, then bind/store it in `position`: `int(payload['position'])` — Convert the input to an integer (using the optional numeric base). |
| L293 | Handle `(KeyError, ValueError, TypeError)` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L294 | Raise `CursorError('cursor is invalid')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L295 | Evaluate the branch condition: compare whether `position` is less than `1`. If truthy, enter L296; otherwise skip this indented block and continue after it. |
| L296 | Raise `CursorError('cursor is invalid')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L297 | Compute the return value: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
