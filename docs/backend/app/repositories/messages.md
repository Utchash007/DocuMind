# `app/repositories/messages.py`

[Source](../../../../Backend/app/repositories/messages.py) · [Backend index](../../README.md)

Database half of claim → context → generation → persistence. Callers own all transaction commits. `GENERATION_LEASE_SECONDS=300`; prompt history defaults to 20 messages / 12,000 characters. Active statuses are `pending`/`generating`; terminal statuses are `completed`/`failed`/`cancelled`.

`Claim` is a dataclass containing user-message/conversation IDs and content, optional generation token/expiry/request key, a fresh per-instance source-snapshot list, and replay flag/result. Its constructor is dataclass-generated. `InvalidStateError`, `NoReadySourcesError`, and `ClaimLostError` have no custom methods; `SnapshotMismatchError` extends claim loss with a diagnostic code.

## Errors

### `DuplicateRequestConflict.__init__(self, *, message_id: UUID, conversation_id: UUID) -> None`

**Arguments:** Original turn and conversation IDs. **Returns:** `None`. **Work:** Sets a fixed same-key/different-content message and stores the IDs for HTTP error context.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-duplicaterequestconflict---init--"></a>

#### Line-by-line execution

[Current source: lines 70–73](../../../../Backend/app/repositories/messages.py#L70-L73). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `message_id` | `UUID`; required; keyword-only | Persisted message UUID identifying the turn being read, retried, or cancelled. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  70 |     def __init__(self, *, message_id: UUID, conversation_id: UUID) -> None:
  71 |         super().__init__("This request key was already used with different content.")
  72 |         self.message_id = message_id
  73 |         self.conversation_id = conversation_id
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L70 | Define `DuplicateRequestConflict.__init__`; bind its arguments when called. The body executes only when invoked. |
| L71 | `super().__init__('This request key was already used with different content.')` — Initialize the base exception/object with the supplied arguments; first obtain the receiver: `super()` — Resolve the superclass proxy for the current method and instance. The return value is not assigned here. |
| L72 | Evaluate the right-hand side, then bind/store it in `self.message_id`: the current `message_id` value. |
| L73 | Evaluate the right-hand side, then bind/store it in `self.conversation_id`: the current `conversation_id` value. |

<!-- END LINE WALKTHROUGH -->

### `ActiveTurnInProgress.__init__(self, *, active_message_id: UUID, conversation_id: UUID) -> None`

**Arguments:** Current active user turn and conversation IDs. **Returns:** `None`. **Work:** Sets a fixed in-progress message and exposes both IDs.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-activeturninprogress---init--"></a>

#### Line-by-line execution

[Current source: lines 79–82](../../../../Backend/app/repositories/messages.py#L79-L82). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `active_message_id` | `UUID`; required; keyword-only | Caller-supplied active message id; each read, transformation, and validation is traced below. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  79 |     def __init__(self, *, active_message_id: UUID, conversation_id: UUID) -> None:
  80 |         super().__init__("Another message is being answered in this conversation.")
  81 |         self.active_message_id = active_message_id
  82 |         self.conversation_id = conversation_id
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L79 | Define `ActiveTurnInProgress.__init__`; bind its arguments when called. The body executes only when invoked. |
| L80 | `super().__init__('Another message is being answered in this conversation.')` — Initialize the base exception/object with the supplied arguments; first obtain the receiver: `super()` — Resolve the superclass proxy for the current method and instance. The return value is not assigned here. |
| L81 | Evaluate the right-hand side, then bind/store it in `self.active_message_id`: the current `active_message_id` value. |
| L82 | Evaluate the right-hand side, then bind/store it in `self.conversation_id`: the current `conversation_id` value. |

<!-- END LINE WALKTHROUGH -->

### `SnapshotMismatchError.__init__(self, code: str, message: str) -> None`

**Arguments:** Snapshot failure code/message. **Returns:** `None`. **Work:** Initializes the parent exception and stores `.code`, allowing the route to mark failure after its persistence transaction rolls back.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-snapshotmismatcherror---init--"></a>

#### Line-by-line execution

[Current source: lines 105–107](../../../../Backend/app/repositories/messages.py#L105-L107). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `code` | `str`; required; positional or keyword | Caller-supplied code; each read, transformation, and validation is traced below. |
| `message` | `str`; required; positional or keyword | Caller-supplied message; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 105 |     def __init__(self, code: str, message: str) -> None:
 106 |         super().__init__(message)
 107 |         self.code = code
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L105 | Define `SnapshotMismatchError.__init__`; bind its arguments when called. The body executes only when invoked. |
| L106 | `super().__init__(message)` — Initialize the base exception/object with the supplied arguments; first obtain the receiver: `super()` — Resolve the superclass proxy for the current method and instance. The return value is not assigned here. |
| L107 | Evaluate the right-hand side, then bind/store it in `self.code`: the current `code` value. |

<!-- END LINE WALKTHROUGH -->

## Claim and replay

### `claim_new_turn(session, *, user_id, project_id, conversation_id, content: str, client_request_id: UUID) -> Claim`

**Arguments:** Session, authenticated scope, validated exact question, request key. **Returns:** Fresh/reclaimed claim or completed replay. **Work:** Authorizes conversation, settles expired turns, and looks up a keyed user message. Delegates an existing row to `_handle_duplicate`; otherwise rejects an unexpired active turn and calls `_insert_user_turn`. SQL unique indexes backstop request/active-turn constraints; this function does not catch arbitrary uniqueness failures.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-claim-new-turn"></a>

#### Line-by-line execution

[Current source: lines 138–189](../../../../Backend/app/repositories/messages.py#L138-L189). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |
| `content` | `str`; required; keyword-only | Message text supplied for a persisted conversation turn. |
| `client_request_id` | `UUID`; required; keyword-only | Client request UUID used to deduplicate message sends. |

**Declared result:** `Claim`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 138 | def claim_new_turn(
 139 |     session: Session,
 140 |     *,
 141 |     user_id: UUID,
 142 |     project_id: UUID,
 143 |     conversation_id: UUID,
 144 |     content: str,
 145 |     client_request_id: UUID,
 146 | ) -> Claim:
 147 |     """Insert or reuse the user row for a new message submission.
 148 | 
 149 |     Must run inside a short transaction.  Raises :class:`NotFoundError`
 150 |     for missing/unowned scopes, :class:`DuplicateRequestConflict` for
 151 |     same-key/different-content, and :class:`ActiveTurnInProgress` when an
 152 |     unexpired turn is already generating.
 153 |     """
 154 |     conversation = _owned_conversation(
 155 |         session,
 156 |         user_id=user_id,
 157 |         project_id=project_id,
 158 |         conversation_id=conversation_id,
 159 |     )
 160 |     _settle_expired_turns(session, conversation_id=conversation.id)
 161 | 
 162 |     existing = session.scalar(
 163 |         select(Message).where(
 164 |             Message.conversation_id == conversation.id,
 165 |             Message.role == "user",
 166 |             Message.client_request_id == client_request_id,
 167 |         )
 168 |     )
 169 |     if existing is not None:
 170 |         return _handle_duplicate(
 171 |             session,
 172 |             existing=existing,
 173 |             content=content,
 174 |             conversation_id=conversation.id,
 175 |         )
 176 | 
 177 |     active = _active_turn(session, conversation_id=conversation.id)
 178 |     if active is not None:
 179 |         raise ActiveTurnInProgress(
 180 |             active_message_id=active.id, conversation_id=conversation.id
 181 |         )
 182 | 
 183 |     claim = _insert_user_turn(
 184 |         session,
 185 |         conversation_id=conversation.id,
 186 |         content=content,
 187 |         client_request_id=client_request_id,
 188 |     )
 189 |     return claim
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L138 | Define `claim_new_turn`; bind its arguments when called. The body executes only when invoked. |
| L139 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L140 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L141 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L142 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L143 | Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L144 | Declare parameter `content` with annotation `str`. Message text supplied for a persisted conversation turn. |
| L145 | Declare parameter `client_request_id` with annotation `UUID`. Client request UUID used to deduplicate message sends. |
| L146 | Finish/continue the signature; the declared return annotation is `Claim`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L147 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L149 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L150 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L151 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L152 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L153 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L154 | Evaluate the right-hand side, then bind/store it in `conversation`: `_owned_conversation(session, user_id=user_id, project_id=project_id, conversation_id=conversation_id)` — Call [_owned_conversation](#walk--owned-conversation) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L155 | Supply positional argument 1 to `_owned_conversation`: the current `session` value. |
| L156 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L157 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L158 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L159 | Close the expression/container begun at L154; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L160 | `_settle_expired_turns(session, conversation_id=conversation.id)` — Call [_settle_expired_turns](#walk--settle-expired-turns) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L162 | Evaluate the right-hand side, then bind/store it in `existing`: `session.scalar(select(Message).where(Message.conversation_id == conversation.id, Message.role == 'user', Message.client_request_id == client_request_id))` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(Message).where(Message.conversation_id == conversation.id, Message.role == 'user', Message.client_request_id == client_request_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L163 | `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L164 | Continue the enclosing expression: build a SQL predicate requiring `Message.conversation_id` equals `conversation.id`. |
| L165 | Continue the enclosing expression: build a SQL predicate requiring `Message.role` equals `'user'`. |
| L166 | Continue the enclosing expression: build a SQL predicate requiring `Message.client_request_id` equals `client_request_id`. |
| L167 | Close the expression/container begun at L163; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L168 | Close the expression/container begun at L162; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L169 | Evaluate the branch condition: compare whether `existing` is not the same object as `None`. If truthy, enter L170; otherwise skip this indented block and continue after it. |
| L170 | Compute the return value: `_handle_duplicate(session, existing=existing, content=content, conversation_id=conversation.id)` — Call [_handle_duplicate](#walk--handle-duplicate) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L171 | Supply positional argument 1 to `_handle_duplicate`: the current `session` value. |
| L172 | Supply `existing` = `existing`.  Evaluate the value as: the current `existing` value. |
| L173 | Supply `content` = `content`. Message text supplied for a persisted conversation turn. Evaluate the value as: the current `content` value. |
| L174 | Supply `conversation_id` = `conversation.id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the `id` attribute of `conversation`. |
| L175 | Close the expression/container begun at L170; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L177 | Evaluate the right-hand side, then bind/store it in `active`: `_active_turn(session, conversation_id=conversation.id)` — Call [_active_turn](#walk--active-turn) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L178 | Evaluate the branch condition: compare whether `active` is not the same object as `None`. If truthy, enter L179; otherwise skip this indented block and continue after it. |
| L179 | Raise `ActiveTurnInProgress(active_message_id=active.id, conversation_id=conversation.id)`; stop the normal path and transfer control to the nearest matching exception handler. |
| L180 | Supply `active_message_id` = `active.id`.  Evaluate the value as: the `id` attribute of `active`. Supply `conversation_id` = `conversation.id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the `id` attribute of `conversation`. |
| L181 | Close the expression/container begun at L179; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L183 | Evaluate the right-hand side, then bind/store it in `claim`: `_insert_user_turn(session, conversation_id=conversation.id, content=content, client_request_id=client_request_id)` — Call [_insert_user_turn](#walk--insert-user-turn) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L184 | Supply positional argument 1 to `_insert_user_turn`: the current `session` value. |
| L185 | Supply `conversation_id` = `conversation.id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the `id` attribute of `conversation`. |
| L186 | Supply `content` = `content`. Message text supplied for a persisted conversation turn. Evaluate the value as: the current `content` value. |
| L187 | Supply `client_request_id` = `client_request_id`. Client request UUID used to deduplicate message sends. Evaluate the value as: the current `client_request_id` value. |
| L188 | Close the expression/container begun at L183; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L189 | Compute the return value: the current `claim` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `reclaim_turn_for_retry(session, *, user_id, project_id, conversation_id, message_id, client_request_id: UUID | None) -> Claim`

**Arguments:** Session, owner/project/conversation/message UUIDs, optional original request key. **Returns:** Claim on the same user-message row. **Work:** Authorizes, settles expiry, selects the target user turn in this conversation, raises not-found on a miss, rejects a supplied mismatched key, then applies `_retry_failed_turn`. No second user row is added.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-reclaim-turn-for-retry"></a>

#### Line-by-line execution

[Current source: lines 192–234](../../../../Backend/app/repositories/messages.py#L192-L234). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |
| `message_id` | `UUID`; required; keyword-only | Persisted message UUID identifying the turn being read, retried, or cancelled. |
| `client_request_id` | `UUID \| None`; required; keyword-only | Client request UUID used to deduplicate message sends. |

**Declared result:** `Claim`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 192 | def reclaim_turn_for_retry(
 193 |     session: Session,
 194 |     *,
 195 |     user_id: UUID,
 196 |     project_id: UUID,
 197 |     conversation_id: UUID,
 198 |     message_id: UUID,
 199 |     client_request_id: UUID | None,
 200 | ) -> Claim:
 201 |     """Re-claim the latest eligible failed/interrupted user turn.
 202 | 
 203 |     Retrying never appends a second user message or a second assistant
 204 |     reply (the partial unique ``reply_to_message_id`` index enforces
 205 |     exactly one reply).  Only the most recent user turn is eligible, and
 206 |     only when it is ``failed`` or an expired active turn; an older turn
 207 |     is rejected so its answer cannot be inserted into later history.
 208 | 
 209 |     A ``client_request_id`` sent with the retry must match the original
 210 |     turn's key (idempotent retry); a mismatch raises
 211 |     :class:`DuplicateRequestConflict`.
 212 |     """
 213 |     conversation = _owned_conversation(
 214 |         session,
 215 |         user_id=user_id,
 216 |         project_id=project_id,
 217 |         conversation_id=conversation_id,
 218 |     )
 219 |     _settle_expired_turns(session, conversation_id=conversation.id)
 220 | 
 221 |     message = session.scalar(
 222 |         select(Message).where(
 223 |             Message.id == message_id,
 224 |             Message.conversation_id == conversation.id,
 225 |             Message.role == "user",
 226 |         )
 227 |     )
 228 |     if message is None:
 229 |         raise NotFoundError(f"message not found: {message_id}")
 230 |     if client_request_id is not None and client_request_id != message.client_request_id:
 231 |         raise DuplicateRequestConflict(
 232 |             message_id=message.id, conversation_id=conversation.id
 233 |         )
 234 |     return _retry_failed_turn(session, message=message, conversation_id=conversation.id)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L192 | Define `reclaim_turn_for_retry`; bind its arguments when called. The body executes only when invoked. |
| L193 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L194 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L195 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L196 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L197 | Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L198 | Declare parameter `message_id` with annotation `UUID`. Persisted message UUID identifying the turn being read, retried, or cancelled. |
| L199 | Declare parameter `client_request_id` with annotation `UUID \| None`. Client request UUID used to deduplicate message sends. |
| L200 | Finish/continue the signature; the declared return annotation is `Claim`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L201 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L203 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L204 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L205 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L206 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L207 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L209 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L210 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L211 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L212 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L213 | Evaluate the right-hand side, then bind/store it in `conversation`: `_owned_conversation(session, user_id=user_id, project_id=project_id, conversation_id=conversation_id)` — Call [_owned_conversation](#walk--owned-conversation) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L214 | Supply positional argument 1 to `_owned_conversation`: the current `session` value. |
| L215 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L216 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L217 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L218 | Close the expression/container begun at L213; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L219 | `_settle_expired_turns(session, conversation_id=conversation.id)` — Call [_settle_expired_turns](#walk--settle-expired-turns) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L221 | Evaluate the right-hand side, then bind/store it in `message`: `session.scalar(select(Message).where(Message.id == message_id, Message.conversation_id == conversation.id, Message.role == 'user'))` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(Message).where(Message.id == message_id, Message.conversation_id == conversation.id, Message.role == 'user')` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L222 | `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L223 | Continue the enclosing expression: build a SQL predicate requiring `Message.id` equals `message_id`. |
| L224 | Continue the enclosing expression: build a SQL predicate requiring `Message.conversation_id` equals `conversation.id`. |
| L225 | Continue the enclosing expression: build a SQL predicate requiring `Message.role` equals `'user'`. |
| L226 | Close the expression/container begun at L222; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L227 | Close the expression/container begun at L221; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L228 | Evaluate the branch condition: compare whether `message` is the same object as `None`. If truthy, enter L229; otherwise skip this indented block and continue after it. |
| L229 | Raise `NotFoundError(f'message not found: {message_id}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L230 | Evaluate the branch condition: evaluate `client_request_id is not None and client_request_id != message.client_request_id` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L231; otherwise skip this indented block and continue after it. |
| L231 | Raise `DuplicateRequestConflict(message_id=message.id, conversation_id=conversation.id)`; stop the normal path and transfer control to the nearest matching exception handler. |
| L232 | Supply `message_id` = `message.id`. Persisted message UUID identifying the turn being read, retried, or cancelled. Evaluate the value as: the `id` attribute of `message`. Supply `conversation_id` = `conversation.id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the `id` attribute of `conversation`. |
| L233 | Close the expression/container begun at L231; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L234 | Compute the return value: `_retry_failed_turn(session, message=message, conversation_id=conversation.id)` — Call [_retry_failed_turn](#walk--retry-failed-turn) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_retry_failed_turn(session, *, message: Message, conversation_id: UUID) -> Claim`

**Arguments:** Session, candidate user row, conversation ID. **Returns:** Reactivated claim. **Work:** Finds the latest user position; rejects older rows, active rows, non-failed rows (including cancelled/completed), and any competing unexpired active turn. Then `_reactivate` assigns a new claim. Both explicit retry and same-key resend share this eligibility.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--retry-failed-turn"></a>

#### Line-by-line execution

[Current source: lines 237–269](../../../../Backend/app/repositories/messages.py#L237-L269). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `message` | `Message`; required; keyword-only | Caller-supplied message; each read, transformation, and validation is traced below. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |

**Declared result:** `Claim`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 237 | def _retry_failed_turn(
 238 |     session: Session, *, message: Message, conversation_id: UUID
 239 | ) -> Claim:
 240 |     """Apply identical eligibility to explicit retry and same-key resend."""
 241 |     latest = session.scalar(
 242 |         select(Message.position)
 243 |         .where(
 244 |             Message.conversation_id == conversation_id,
 245 |             Message.role == "user",
 246 |         )
 247 |         .order_by(Message.position.desc())
 248 |         .limit(1)
 249 |     )
 250 |     if latest is None or message.position != latest:
 251 |         raise InvalidStateError("Only the latest turn can be retried.")
 252 |     if message.generation_status in ACTIVE_STATUSES:
 253 |         raise ActiveTurnInProgress(
 254 |             active_message_id=message.id, conversation_id=conversation_id
 255 |         )
 256 |     if message.generation_status != "failed":
 257 |         raise InvalidStateError(
 258 |             "Only a failed or interrupted turn can be retried.",
 259 |         )
 260 |     active = _active_turn(session, conversation_id=conversation_id)
 261 |     if active is not None:
 262 |         raise ActiveTurnInProgress(
 263 |             active_message_id=active.id, conversation_id=conversation_id
 264 |         )
 265 |     return _reactivate(
 266 |         session,
 267 |         message=message,
 268 |         conversation_id=conversation_id,
 269 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L237 | Define `_retry_failed_turn`; bind its arguments when called. The body executes only when invoked. |
| L238 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `message` with annotation `Message`. Caller-supplied message; its uses and transformations are traced below. Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L239 | Finish/continue the signature; the declared return annotation is `Claim`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L240 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L241 | Evaluate the right-hand side, then bind/store it in `latest`: `session.scalar(select(Message.position).where(Message.conversation_id == conversation_id, Message.role == 'user').order_by(Message.position.desc()).limit(1))` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(Message.position).where(Message.conversation_id == conversation_id, Message.role == 'user').order_by(Message.position.desc()).limit(1)` — Apply a SQL row limit; fetching limit+1 allows continuation detection; first obtain the receiver: `select(Message.position).where(Message.conversation_id == conversation_id, Message.role == 'user').order_by(Message.position.desc())` — Set SQL result ordering in the listed priority order. |
| L242 | `select(Message.position)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L243 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L244 | Continue the enclosing expression: build a SQL predicate requiring `Message.conversation_id` equals `conversation_id`. |
| L245 | Continue the enclosing expression: build a SQL predicate requiring `Message.role` equals `'user'`. |
| L246 | Close the expression/container begun at L242; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L247 | Set SQL result ordering in the listed priority order; apply this method to the result built by the preceding chain. |
| L248 | Apply a SQL row limit; fetching limit+1 allows continuation detection; apply this method to the result built by the preceding chain. |
| L249 | Close the expression/container begun at L241; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L250 | Evaluate the branch condition: evaluate `latest is None or message.position != latest` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L251; otherwise skip this indented block and continue after it. |
| L251 | Raise `InvalidStateError('Only the latest turn can be retried.')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L252 | Evaluate the branch condition: compare whether `message.generation_status` is contained in `ACTIVE_STATUSES`. If truthy, enter L253; otherwise skip this indented block and continue after it. |
| L253 | Raise `ActiveTurnInProgress(active_message_id=message.id, conversation_id=conversation_id)`; stop the normal path and transfer control to the nearest matching exception handler. |
| L254 | Supply `active_message_id` = `message.id`.  Evaluate the value as: the `id` attribute of `message`. Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L255 | Close the expression/container begun at L253; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L256 | Evaluate the branch condition: compare whether `message.generation_status` differs from `'failed'`. If truthy, enter L257; otherwise skip this indented block and continue after it. |
| L257 | Raise `InvalidStateError('Only a failed or interrupted turn can be retried.')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L258 | Supply positional argument 1 to `InvalidStateError`: `'Only a failed or interrupted turn can be retried.'`. |
| L259 | Close the expression/container begun at L257; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L260 | Evaluate the right-hand side, then bind/store it in `active`: `_active_turn(session, conversation_id=conversation_id)` — Call [_active_turn](#walk--active-turn) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L261 | Evaluate the branch condition: compare whether `active` is not the same object as `None`. If truthy, enter L262; otherwise skip this indented block and continue after it. |
| L262 | Raise `ActiveTurnInProgress(active_message_id=active.id, conversation_id=conversation_id)`; stop the normal path and transfer control to the nearest matching exception handler. |
| L263 | Supply `active_message_id` = `active.id`.  Evaluate the value as: the `id` attribute of `active`. Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L264 | Close the expression/container begun at L262; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L265 | Compute the return value: `_reactivate(session, message=message, conversation_id=conversation_id)` — Call [_reactivate](#walk--reactivate) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L266 | Supply positional argument 1 to `_reactivate`: the current `session` value. |
| L267 | Supply `message` = `message`.  Evaluate the value as: the current `message` value. |
| L268 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L269 | Close the expression/container begun at L265; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `_handle_duplicate(session, *, existing: Message, content: str, conversation_id: UUID) -> Claim`

**Arguments:** Session, keyed stored row, incoming exact text, conversation ID. **Returns:** Original completed pair as replay, or eligible failed-turn reclaim. **Work:** Compares exact content first. Completed loads its assistant; active raises `ActiveTurnInProgress`; failed delegates eligibility; all other statuses raise `InvalidStateError`. It never reruns generation for completed replay.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--handle-duplicate"></a>

#### Line-by-line execution

[Current source: lines 272–304](../../../../Backend/app/repositories/messages.py#L272-L304). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `existing` | `Message`; required; keyword-only | Caller-supplied existing; each read, transformation, and validation is traced below. |
| `content` | `str`; required; keyword-only | Message text supplied for a persisted conversation turn. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |

**Declared result:** `Claim`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 272 | def _handle_duplicate(
 273 |     session: Session,
 274 |     *,
 275 |     existing: Message,
 276 |     content: str,
 277 |     conversation_id: UUID,
 278 | ) -> Claim:
 279 |     if existing.content != content:
 280 |         raise DuplicateRequestConflict(
 281 |             message_id=existing.id, conversation_id=conversation_id
 282 |         )
 283 |     status = existing.generation_status
 284 |     if status == "completed":
 285 |         return Claim(
 286 |             user_message_id=existing.id,
 287 |             conversation_id=conversation_id,
 288 |             content=existing.content,
 289 |             client_request_id=existing.client_request_id,
 290 |             is_replay=True,
 291 |             replay_result=_load_completed_turn(
 292 |                 session,
 293 |                 user_message=existing,
 294 |                 conversation_id=conversation_id,
 295 |             ),
 296 |         )
 297 |     if status in ACTIVE_STATUSES:
 298 |         raise ActiveTurnInProgress(
 299 |             active_message_id=existing.id, conversation_id=conversation_id
 300 |         )
 301 |     if status == "failed":
 302 |         # Same-key resend of a failed turn re-claims it (same as retry).
 303 |         return _retry_failed_turn(session, message=existing, conversation_id=conversation_id)
 304 |     raise InvalidStateError("This turn was cancelled; submit a new request.")
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L272 | Define `_handle_duplicate`; bind its arguments when called. The body executes only when invoked. |
| L273 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L274 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L275 | Declare parameter `existing` with annotation `Message`. Caller-supplied existing; its uses and transformations are traced below. |
| L276 | Declare parameter `content` with annotation `str`. Message text supplied for a persisted conversation turn. |
| L277 | Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L278 | Finish/continue the signature; the declared return annotation is `Claim`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L279 | Evaluate the branch condition: compare whether `existing.content` differs from `content`. If truthy, enter L280; otherwise skip this indented block and continue after it. |
| L280 | Raise `DuplicateRequestConflict(message_id=existing.id, conversation_id=conversation_id)`; stop the normal path and transfer control to the nearest matching exception handler. |
| L281 | Supply `message_id` = `existing.id`. Persisted message UUID identifying the turn being read, retried, or cancelled. Evaluate the value as: the `id` attribute of `existing`. Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L282 | Close the expression/container begun at L280; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L283 | Evaluate the right-hand side, then bind/store it in `status`: the `generation_status` attribute of `existing`. |
| L284 | Evaluate the branch condition: compare whether `status` equals `'completed'`. If truthy, enter L285; otherwise skip this indented block and continue after it. |
| L285 | Compute the return value: `Claim` with the arguments detailed below — Construct `Claim` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L286 | Supply `user_message_id` = `existing.id`.  Evaluate the value as: the `id` attribute of `existing`. |
| L287 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L288 | Supply `content` = `existing.content`. Message text supplied for a persisted conversation turn. Evaluate the value as: the `content` attribute of `existing`. |
| L289 | Supply `client_request_id` = `existing.client_request_id`. Client request UUID used to deduplicate message sends. Evaluate the value as: the `client_request_id` attribute of `existing`. |
| L290 | Supply `is_replay` = `True`.  Evaluate the value as: `True`. |
| L291 | Supply `replay_result` = `_load_completed_turn(session, user_message=existing, conversation_id=conversation_id)`.  Evaluate the value as: `_load_completed_turn(session, user_message=existing, conversation_id=conversation_id)` — Call [_load_completed_turn](#walk--load-completed-turn) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L292 | Supply positional argument 1 to `_load_completed_turn`: the current `session` value. |
| L293 | Supply `user_message` = `existing`.  Evaluate the value as: the current `existing` value. |
| L294 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L295 | Close the expression/container begun at L291; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L296 | Close the expression/container begun at L285; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L297 | Evaluate the branch condition: compare whether `status` is contained in `ACTIVE_STATUSES`. If truthy, enter L298; otherwise skip this indented block and continue after it. |
| L298 | Raise `ActiveTurnInProgress(active_message_id=existing.id, conversation_id=conversation_id)`; stop the normal path and transfer control to the nearest matching exception handler. |
| L299 | Supply `active_message_id` = `existing.id`.  Evaluate the value as: the `id` attribute of `existing`. Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L300 | Close the expression/container begun at L298; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L301 | Evaluate the branch condition: compare whether `status` equals `'failed'`. If truthy, enter L303; otherwise skip this indented block and continue after it. |
| L302 | Comment only: Same-key resend of a failed turn re-claims it (same as retry).. It does not execute; the neighboring code determines behavior. |
| L303 | Compute the return value: `_retry_failed_turn(session, message=existing, conversation_id=conversation_id)` — Call [_retry_failed_turn](#walk--retry-failed-turn) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L304 | Raise `InvalidStateError('This turn was cancelled; submit a new request.')`; stop the normal path and transfer control to the nearest matching exception handler. |

<!-- END LINE WALKTHROUGH -->

### `_insert_user_turn(session, *, conversation_id, content, client_request_id) -> Claim`

**Arguments:** Session, conversation UUID, content, UUID request key. **Returns:** Claim populated with inserted row ID/token/expiry. **Work:** Generates a UUID token and UTC-now+300-second expiry, obtains the next position under a conversation-row lock, inserts a `generating` user message, and flushes. Source snapshot is filled later.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--insert-user-turn"></a>

#### Line-by-line execution

[Current source: lines 307–337](../../../../Backend/app/repositories/messages.py#L307-L337). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |
| `content` | `str`; required; keyword-only | Message text supplied for a persisted conversation turn. |
| `client_request_id` | `UUID`; required; keyword-only | Client request UUID used to deduplicate message sends. |

**Declared result:** `Claim`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 307 | def _insert_user_turn(
 308 |     session: Session,
 309 |     *,
 310 |     conversation_id: UUID,
 311 |     content: str,
 312 |     client_request_id: UUID,
 313 | ) -> Claim:
 314 |     now = utcnow()
 315 |     token = uuid.uuid4()
 316 |     expires_at = now + timedelta(seconds=GENERATION_LEASE_SECONDS)
 317 |     position = next_message_position(session, conversation_id=conversation_id)
 318 |     row = Message(
 319 |         conversation_id=conversation_id,
 320 |         role="user",
 321 |         content=content,
 322 |         position=position,
 323 |         client_request_id=client_request_id,
 324 |         generation_status="generating",
 325 |         generation_token=token,
 326 |         generation_expires_at=expires_at,
 327 |     )
 328 |     session.add(row)
 329 |     session.flush()
 330 |     return Claim(
 331 |         user_message_id=row.id,
 332 |         conversation_id=conversation_id,
 333 |         content=content,
 334 |         generation_token=token,
 335 |         generation_expires_at=expires_at,
 336 |         client_request_id=client_request_id,
 337 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L307 | Define `_insert_user_turn`; bind its arguments when called. The body executes only when invoked. |
| L308 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L309 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L310 | Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L311 | Declare parameter `content` with annotation `str`. Message text supplied for a persisted conversation turn. |
| L312 | Declare parameter `client_request_id` with annotation `UUID`. Client request UUID used to deduplicate message sends. |
| L313 | Finish/continue the signature; the declared return annotation is `Claim`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L314 | Evaluate the right-hand side, then bind/store it in `now`: `utcnow()` — Read the current timezone-aware UTC timestamp. |
| L315 | Evaluate the right-hand side, then bind/store it in `token`: `uuid.uuid4()` — Generate a new random UUID. |
| L316 | Evaluate the right-hand side, then bind/store it in `expires_at`: add/concatenate `now` and `timedelta(seconds=GENERATION_LEASE_SECONDS)`, following the parentheses/operator precedence shown in `now + timedelta(seconds=GENERATION_LEASE_SECONDS)`. |
| L317 | Evaluate the right-hand side, then bind/store it in `position`: `next_message_position(session, conversation_id=conversation_id)` — Call [next_message_position](../db/queries.md#walk-next-message-position) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L318 | Evaluate the right-hand side, then bind/store it in `row`: `Message` with the arguments detailed below — Construct `Message` with the shown fields; its class/model initialization rules apply. |
| L319 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L320 | Supply `role` = `'user'`.  Evaluate the value as: `'user'`. |
| L321 | Supply `content` = `content`. Message text supplied for a persisted conversation turn. Evaluate the value as: the current `content` value. |
| L322 | Supply `position` = `position`.  Evaluate the value as: the current `position` value. |
| L323 | Supply `client_request_id` = `client_request_id`. Client request UUID used to deduplicate message sends. Evaluate the value as: the current `client_request_id` value. |
| L324 | Supply `generation_status` = `'generating'`.  Evaluate the value as: `'generating'`. |
| L325 | Supply `generation_token` = `token`. Generation claim token used to fence a late answer. Evaluate the value as: the current `token` value. |
| L326 | Supply `generation_expires_at` = `expires_at`.  Evaluate the value as: the current `expires_at` value. |
| L327 | Close the expression/container begun at L318; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L328 | `session.add(row)` — Attach the ORM object to this session for insertion/update tracking; this does not commit it. The return value is not assigned here. |
| L329 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L330 | Compute the return value: `Claim` with the arguments detailed below — Construct `Claim` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L331 | Supply `user_message_id` = `row.id`.  Evaluate the value as: the `id` attribute of `row`. |
| L332 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L333 | Supply `content` = `content`. Message text supplied for a persisted conversation turn. Evaluate the value as: the current `content` value. |
| L334 | Supply `generation_token` = `token`. Generation claim token used to fence a late answer. Evaluate the value as: the current `token` value. |
| L335 | Supply `generation_expires_at` = `expires_at`.  Evaluate the value as: the current `expires_at` value. |
| L336 | Supply `client_request_id` = `client_request_id`. Client request UUID used to deduplicate message sends. Evaluate the value as: the current `client_request_id` value. |
| L337 | Close the expression/container begun at L330; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `_reactivate(session, *, message: Message, conversation_id: UUID) -> Claim`

**Arguments:** Session, eligible existing message, conversation UUID. **Returns:** New claim retaining original ID/content/request key. **Work:** Sets `generating`, replaces token/expiry, and flushes. It preserves position and existing metadata, including earlier diagnostics until later writes replace relevant entries.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--reactivate"></a>

#### Line-by-line execution

[Current source: lines 340–360](../../../../Backend/app/repositories/messages.py#L340-L360). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `message` | `Message`; required; keyword-only | Caller-supplied message; each read, transformation, and validation is traced below. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |

**Declared result:** `Claim`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 340 | def _reactivate(
 341 |     session: Session,
 342 |     *,
 343 |     message: Message,
 344 |     conversation_id: UUID,
 345 | ) -> Claim:
 346 |     now = utcnow()
 347 |     token = uuid.uuid4()
 348 |     expires_at = now + timedelta(seconds=GENERATION_LEASE_SECONDS)
 349 |     message.generation_status = "generating"
 350 |     message.generation_token = token
 351 |     message.generation_expires_at = expires_at
 352 |     session.flush()
 353 |     return Claim(
 354 |         user_message_id=message.id,
 355 |         conversation_id=conversation_id,
 356 |         content=message.content,
 357 |         generation_token=token,
 358 |         generation_expires_at=expires_at,
 359 |         client_request_id=message.client_request_id,
 360 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L340 | Define `_reactivate`; bind its arguments when called. The body executes only when invoked. |
| L341 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L342 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L343 | Declare parameter `message` with annotation `Message`. Caller-supplied message; its uses and transformations are traced below. |
| L344 | Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L345 | Finish/continue the signature; the declared return annotation is `Claim`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L346 | Evaluate the right-hand side, then bind/store it in `now`: `utcnow()` — Read the current timezone-aware UTC timestamp. |
| L347 | Evaluate the right-hand side, then bind/store it in `token`: `uuid.uuid4()` — Generate a new random UUID. |
| L348 | Evaluate the right-hand side, then bind/store it in `expires_at`: add/concatenate `now` and `timedelta(seconds=GENERATION_LEASE_SECONDS)`, following the parentheses/operator precedence shown in `now + timedelta(seconds=GENERATION_LEASE_SECONDS)`. |
| L349 | Evaluate the right-hand side, then bind/store it in `message.generation_status`: `'generating'`. |
| L350 | Evaluate the right-hand side, then bind/store it in `message.generation_token`: the current `token` value. |
| L351 | Evaluate the right-hand side, then bind/store it in `message.generation_expires_at`: the current `expires_at` value. |
| L352 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L353 | Compute the return value: `Claim` with the arguments detailed below — Construct `Claim` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L354 | Supply `user_message_id` = `message.id`.  Evaluate the value as: the `id` attribute of `message`. |
| L355 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L356 | Supply `content` = `message.content`. Message text supplied for a persisted conversation turn. Evaluate the value as: the `content` attribute of `message`. |
| L357 | Supply `generation_token` = `token`. Generation claim token used to fence a late answer. Evaluate the value as: the current `token` value. |
| L358 | Supply `generation_expires_at` = `expires_at`.  Evaluate the value as: the current `expires_at` value. |
| L359 | Supply `client_request_id` = `message.client_request_id`. Client request UUID used to deduplicate message sends. Evaluate the value as: the `client_request_id` attribute of `message`. |
| L360 | Close the expression/container begun at L353; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `_settle_expired_turns(session, *, conversation_id: UUID) -> None`

**Arguments:** Session and conversation. **Returns:** `None`. **Work:** Bulk-updates active user rows with expiry ≤ UTC now to `failed`, clearing token/expiry, and flushes. Null expiry does not satisfy the comparison; no extra error metadata is recorded.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--settle-expired-turns"></a>

#### Line-by-line execution

[Current source: lines 363–386](../../../../Backend/app/repositories/messages.py#L363-L386). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 363 | def _settle_expired_turns(session: Session, *, conversation_id: UUID) -> None:
 364 |     """Force expired active turns to ``failed`` (interrupted).
 365 | 
 366 |     Generation expiry is a *logical* fence (the token check at persist
 367 |     time); this sweep just keeps the rows honest so they become
 368 |     retriable and the one-active-turn partial index never wedges on a
 369 |     crashed server process.
 370 |     """
 371 |     now = utcnow()
 372 |     session.execute(
 373 |         update(Message)
 374 |         .where(
 375 |             Message.conversation_id == conversation_id,
 376 |             Message.role == "user",
 377 |             Message.generation_status.in_(ACTIVE_STATUSES),
 378 |             Message.generation_expires_at <= now,
 379 |         )
 380 |         .values(
 381 |             generation_status="failed",
 382 |             generation_token=None,
 383 |             generation_expires_at=None,
 384 |         )
 385 |     )
 386 |     session.flush()
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L363 | Define `_settle_expired_turns`; bind its arguments when called. The body executes only when invoked. |
| L364 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L366 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L367 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L368 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L369 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L370 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L371 | Evaluate the right-hand side, then bind/store it in `now`: `utcnow()` — Read the current timezone-aware UTC timestamp. |
| L372 | `session.execute` with the arguments detailed below — Execute the SQL statement in the current transaction and return its Result (including rowcount for guarded updates); inputs include `update(Message).where(Message.conversation_id == conversation_id, Message.role == 'user', Message.generation_status.in_(ACTIVE_STATUSES), Message.generation_expires_at <= now).values` with the arguments detailed below — Attach column assignments to the UPDATE/INSERT expression without executing it; first obtain the receiver: `update(Message).where` with the arguments detailed below — Add SQL filtering predicates; multiple supplied predicates are combined with AND. The return value is not assigned here. |
| L373 | `update(Message)` — Construct a SQL UPDATE expression; execution and commit are separate operations. |
| L374 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L375 | Continue the enclosing expression: build a SQL predicate requiring `Message.conversation_id` equals `conversation_id`. |
| L376 | Continue the enclosing expression: build a SQL predicate requiring `Message.role` equals `'user'`. |
| L377 | `Message.generation_status.in_(ACTIVE_STATUSES)` — Build a SQL membership predicate for the supplied allowed values. |
| L378 | Continue the enclosing expression: build a SQL predicate requiring `Message.generation_expires_at` is at most `now`. |
| L379 | Close the expression/container begun at L373; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L380 | Attach column assignments to the UPDATE/INSERT expression without executing it; apply this method to the result built by the preceding chain. |
| L381 | Supply `generation_status` = `'failed'`.  Evaluate the value as: `'failed'`. |
| L382 | Supply `generation_token` = `None`. Generation claim token used to fence a late answer. Evaluate the value as: None (no value). |
| L383 | Supply `generation_expires_at` = `None`.  Evaluate the value as: None (no value). |
| L384 | Close the expression/container begun at L373; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L385 | Close the expression/container begun at L372; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L386 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |

<!-- END LINE WALKTHROUGH -->

### `_active_turn(session, *, conversation_id: UUID) -> Message | None`

**Arguments:** Session and conversation. **Returns:** Pending/generating user row whose expiry is strictly after UTC now, or `None`. **Work:** Executes the filtered scalar query; it neither locks nor settles rows itself.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--active-turn"></a>

#### Line-by-line execution

[Current source: lines 389–399](../../../../Backend/app/repositories/messages.py#L389-L399). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |

**Declared result:** `Message | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 389 | def _active_turn(session: Session, *, conversation_id: UUID) -> Message | None:
 390 |     """Return the unexpired pending/generating user turn, if any."""
 391 |     now = utcnow()
 392 |     return session.scalar(
 393 |         select(Message).where(
 394 |             Message.conversation_id == conversation_id,
 395 |             Message.role == "user",
 396 |             Message.generation_status.in_(ACTIVE_STATUSES),
 397 |             Message.generation_expires_at > now,
 398 |         )
 399 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L389 | Define `_active_turn`; bind its arguments when called. The body executes only when invoked. |
| L390 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L391 | Evaluate the right-hand side, then bind/store it in `now`: `utcnow()` — Read the current timezone-aware UTC timestamp. |
| L392 | Compute the return value: `session.scalar` with the arguments detailed below — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(Message).where` with the arguments detailed below — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L393 | `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L394 | Continue the enclosing expression: build a SQL predicate requiring `Message.conversation_id` equals `conversation_id`. |
| L395 | Continue the enclosing expression: build a SQL predicate requiring `Message.role` equals `'user'`. |
| L396 | `Message.generation_status.in_(ACTIVE_STATUSES)` — Build a SQL membership predicate for the supplied allowed values. |
| L397 | Continue the enclosing expression: build a SQL predicate requiring `Message.generation_expires_at` is greater than `now`. |
| L398 | Close the expression/container begun at L393; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L399 | Close the expression/container begun at L392; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

## History and evidence snapshot

### `select_history_rows(rows_desc: Sequence[Message], *, max_messages=20, char_budget=12000) -> list[Message]`

**Arguments:** Newest-first rows and selection budgets. **Returns:** Selected rows reversed to chronological order. **Work:** Iterates until count cap or adding the next row exceeds the character budget; the first row is allowed even if individually over budget (provided count permits). Stops rather than skipping over oversized older rows. Does not enforce user/assistant pairing.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-select-history-rows"></a>

#### Line-by-line execution

[Current source: lines 407–430](../../../../Backend/app/repositories/messages.py#L407-L430). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `rows_desc` | `Sequence[Message]`; required; positional or keyword | Caller-supplied rows desc; each read, transformation, and validation is traced below. |
| `max_messages` | `int`; default `HISTORY_MAX_MESSAGES`; keyword-only | Caller-supplied max messages; each read, transformation, and validation is traced below. |
| `char_budget` | `int`; default `HISTORY_CHAR_BUDGET`; keyword-only | Caller-supplied char budget; each read, transformation, and validation is traced below. |

**Declared result:** `list[Message]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 407 | def select_history_rows(
 408 |     rows_desc: Sequence[Message],
 409 |     *,
 410 |     max_messages: int = HISTORY_MAX_MESSAGES,
 411 |     char_budget: int = HISTORY_CHAR_BUDGET,
 412 | ) -> list[Message]:
 413 |     """Select the newest rows within the prompt budget (pure helper).
 414 | 
 415 |     Rows are given newest-first (descending ``position``); the result is
 416 |     chronological (ascending).  The newest row is always included, even
 417 |     if it alone exceeds the character budget, so context is never empty
 418 |     when completed history exists.
 419 |     """
 420 |     selected: list[Message] = []
 421 |     used = 0
 422 |     for row in rows_desc:
 423 |         if len(selected) >= max_messages:
 424 |             break
 425 |         if selected and used + len(row.content) > char_budget:
 426 |             break
 427 |         selected.append(row)
 428 |         used += len(row.content)
 429 |     selected.reverse()
 430 |     return selected
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L407 | Define `select_history_rows`; bind its arguments when called. The body executes only when invoked. |
| L408 | Declare parameter `rows_desc` with annotation `Sequence[Message]`. Caller-supplied rows desc; its uses and transformations are traced below. |
| L409 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L410 | Declare parameter `max_messages` with annotation `int`. Caller-supplied max messages; its uses and transformations are traced below. |
| L411 | Declare parameter `char_budget` with annotation `int`. Caller-supplied char budget; its uses and transformations are traced below. |
| L412 | Finish/continue the signature; the declared return annotation is `list[Message]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L413 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L415 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L416 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L417 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L418 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L419 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L420 | Evaluate the right-hand side, then bind/store it in `selected`: build a list containing no items. |
| L421 | Evaluate the right-hand side, then bind/store it in `used`: `0`. |
| L422 | Iterate `rows_desc` (the current `rows_desc` value), assigning each item to `row`. Execute the indented body once per item; an empty iterable skips it. |
| L423 | Evaluate the branch condition: compare whether `len(selected)` is at least `max_messages`. If truthy, enter L424; otherwise skip this indented block and continue after it. |
| L424 | Exit the innermost loop immediately and continue after it; active cleanup still applies. |
| L425 | Evaluate the branch condition: evaluate `selected and used + len(row.content) > char_budget` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L426; otherwise skip this indented block and continue after it. |
| L426 | Exit the innermost loop immediately and continue after it; active cleanup still applies. |
| L427 | `selected.append(row)` — Append one object to the mutable list in place. The return value is not assigned here. |
| L428 | Update `used` in place using `len(row.content)` and the Add operation; the previous target value participates in the calculation. |
| L429 | `selected.reverse()` — Invoke `selected.reverse` with the shown inputs and use its result; see the function overview for its role in this flow. The return value is not assigned here. |
| L430 | Compute the return value: the current `selected` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `load_history_turns(session, *, conversation_id, max_messages=20, char_budget=12000) -> list[HistoryTurn]`

**Arguments:** Session, already-authorized conversation ID, budgets. **Returns:** Bounded role/content/position DTOs. **Work:** Loads all assistant rows plus completed user rows newest-first, then uses `select_history_rows`. Current generating question, failed/cancelled user turns, and system rows are excluded. The SQL query itself is not limited and does not rejoin each assistant to a completed parent.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-load-history-turns"></a>

#### Line-by-line execution

[Current source: lines 433–467](../../../../Backend/app/repositories/messages.py#L433-L467). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |
| `max_messages` | `int`; default `HISTORY_MAX_MESSAGES`; keyword-only | Caller-supplied max messages; each read, transformation, and validation is traced below. |
| `char_budget` | `int`; default `HISTORY_CHAR_BUDGET`; keyword-only | Caller-supplied char budget; each read, transformation, and validation is traced below. |

**Declared result:** `list[HistoryTurn]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 433 | def load_history_turns(
 434 |     session: Session,
 435 |     *,
 436 |     conversation_id: UUID,
 437 |     max_messages: int = HISTORY_MAX_MESSAGES,
 438 |     char_budget: int = HISTORY_CHAR_BUDGET,
 439 | ) -> list[HistoryTurn]:
 440 |     """Load recent completed turns as generation context.
 441 | 
 442 |     Only completed user turns and their assistant replies qualify;
 443 |     failed/cancelled/pending/generating turns are excluded.  The current
 444 |     (claimed, still ``generating``) question is not part of the result —
 445 |     the caller adds it exactly once to the assembled prompt.
 446 |     """
 447 |     rows = list(
 448 |         session.scalars(
 449 |             select(Message)
 450 |             .where(
 451 |                 Message.conversation_id == conversation_id,
 452 |                 (Message.role == "assistant")
 453 |                 | (
 454 |                     (Message.role == "user")
 455 |                     & (Message.generation_status == "completed")
 456 |                 ),
 457 |             )
 458 |             .order_by(Message.position.desc())
 459 |         )
 460 |     )
 461 |     history_rows = select_history_rows(
 462 |         rows, max_messages=max_messages, char_budget=char_budget
 463 |     )
 464 |     return [
 465 |         HistoryTurn(role=row.role, content=row.content, position=row.position)
 466 |         for row in history_rows
 467 |     ]
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L433 | Define `load_history_turns`; bind its arguments when called. The body executes only when invoked. |
| L434 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L435 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L436 | Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L437 | Declare parameter `max_messages` with annotation `int`. Caller-supplied max messages; its uses and transformations are traced below. |
| L438 | Declare parameter `char_budget` with annotation `int`. Caller-supplied char budget; its uses and transformations are traced below. |
| L439 | Finish/continue the signature; the declared return annotation is `list[HistoryTurn]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L440 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L442 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L443 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L444 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L445 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L446 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L447 | Evaluate the right-hand side, then bind/store it in `rows`: `list` with the arguments detailed below — Materialize the iterable in order into a list (or create an empty list); inputs include `session.scalars` with the arguments detailed below — Execute the SQL expression and expose first-column values through a ScalarResult. |
| L448 | `session.scalars` with the arguments detailed below — Execute the SQL expression and expose first-column values through a ScalarResult; inputs include `select(Message).where(Message.conversation_id == conversation_id, (Message.role == 'assistant') \| (Message.role == 'user') & (Message.generation_status == 'completed')).order_by` with the arguments detailed below — Set SQL result ordering in the listed priority order; first obtain the receiver: `select(Message).where` with the arguments detailed below — Add SQL filtering predicates; multiple supplied predicates are combined with AND. |
| L449 | `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L450 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L451 | Continue the enclosing expression: build a SQL predicate requiring `Message.conversation_id` equals `conversation_id`. |
| L452 | Continue the enclosing expression: combine with \| `Message.role == 'assistant'` and `(Message.role == 'user') & (Message.generation_status == 'completed')`, following the parentheses/operator precedence shown in `(Message.role == 'assistant') \| (Message.role == 'user') & (Message.generation_status == 'completed')`. |
| L453 | Supply positional argument 2 to `select(Message).where`: combine with \| `Message.role == 'assistant'` and `(Message.role == 'user') & (Message.generation_status == 'completed')`, following the parentheses/operator precedence shown in `(Message.role == 'assistant') \| (Message.role == 'user') & (Message.generation_status == 'completed')`. |
| L454 | Continue the enclosing expression: combine with & `Message.role == 'user'` and `Message.generation_status == 'completed'`, following the parentheses/operator precedence shown in `(Message.role == 'user') & (Message.generation_status == 'completed')`. |
| L455 | Continue the enclosing expression: build a SQL predicate requiring `Message.generation_status` equals `'completed'`. |
| L456 | Close the expression/container begun at L449; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L457 | Close the expression/container begun at L449; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L458 | Set SQL result ordering in the listed priority order; apply this method to the result built by the preceding chain. |
| L459 | Close the expression/container begun at L448; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L460 | Close the expression/container begun at L447; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L461 | Evaluate the right-hand side, then bind/store it in `history_rows`: `select_history_rows(rows, max_messages=max_messages, char_budget=char_budget)` — Call [select_history_rows](#walk-select-history-rows) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L462 | Supply `max_messages` = `max_messages`.  Evaluate the value as: the current `max_messages` value. Supply `char_budget` = `char_budget`.  Evaluate the value as: the current `char_budget` value. |
| L463 | Close the expression/container begun at L461; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L464 | Compute the return value: iterate `history_rows`, binding each item to `row`; produce `HistoryTurn(role=row.role, content=row.content, position=row.position)` into a new list. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L465 | `HistoryTurn(role=row.role, content=row.content, position=row.position)` — Construct `HistoryTurn` with the shown fields; its class/model initialization rules apply. |
| L466 | Contribute the current `row` value to the expression being assembled. |
| L467 | Close the expression/container begun at L464; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `resolve_authorized_sources(session, *, user_id, project_id) -> list[AuthorizedSource]`

**Arguments:** Session and authenticated owner/project UUIDs. **Returns:** Sorted exact `(document_id, active_index_version)` DTOs with display names. **Work:** Requires owned live project, selects its live `Completed` documents with non-null active versions, constructs/sorts pairs by string IDs, and raises `NoReadySourcesError` if empty. No provider search happens here.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-resolve-authorized-sources"></a>

#### Line-by-line execution

[Current source: lines 470–509](../../../../Backend/app/repositories/messages.py#L470-L509). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |

**Declared result:** `list[AuthorizedSource]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 470 | def resolve_authorized_sources(
 471 |     session: Session, *, user_id: UUID, project_id: UUID
 472 | ) -> list[AuthorizedSource]:
 473 |     """Resolve the project's retrievable (document, active version) pairs.
 474 | 
 475 |     Only non-deleted ``Completed`` documents with a published
 476 |     ``active_index_version`` qualify.  Each result is an exact pair —
 477 |     retrieval must never mix a document from one version with the
 478 |     version of another document.  Empty results raise
 479 |     :class:`NoReadySourcesError` (never an unscoped search).
 480 |     """
 481 |     from app.db.queries import get_owned_project
 482 | 
 483 |     if get_owned_project(session, user_id=user_id, project_id=project_id) is None:
 484 |         raise NotFoundError(f"project not found: {project_id}")
 485 |     rows = list(
 486 |         session.scalars(
 487 |             select(Document).where(
 488 |                 Document.project_id == project_id,
 489 |                 Document.status == "Completed",
 490 |                 Document.deleted_at.is_(None),
 491 |                 Document.active_index_version.is_not(None),
 492 |             )
 493 |         )
 494 |     )
 495 |     sources = [
 496 |         AuthorizedSource(
 497 |             document_id=row.id,
 498 |             index_version=row.active_index_version,
 499 |             file_name=row.file_name,
 500 |         )
 501 |         for row in rows
 502 |         if row.active_index_version is not None
 503 |     ]
 504 |     sources.sort(key=lambda s: (str(s.document_id), str(s.index_version)))
 505 |     if not sources:
 506 |         raise NoReadySourcesError(
 507 |             "No completed documents are available to answer this question."
 508 |         )
 509 |     return sources
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L470 | Define `resolve_authorized_sources`; bind its arguments when called. The body executes only when invoked. |
| L471 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L472 | Finish/continue the signature; the declared return annotation is `list[AuthorizedSource]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L473 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L475 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L476 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L477 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L478 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L479 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L480 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L481 | Import `get_owned_project` from `app.db.queries`; inside a function this import is deferred until this path is reached. |
| L483 | Evaluate the branch condition: compare whether `get_owned_project(session, user_id=user_id, project_id=project_id)` is the same object as `None`. If truthy, enter L484; otherwise skip this indented block and continue after it. |
| L484 | Raise `NotFoundError(f'project not found: {project_id}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L485 | Evaluate the right-hand side, then bind/store it in `rows`: `list` with the arguments detailed below — Materialize the iterable in order into a list (or create an empty list); inputs include `session.scalars` with the arguments detailed below — Execute the SQL expression and expose first-column values through a ScalarResult. |
| L486 | `session.scalars` with the arguments detailed below — Execute the SQL expression and expose first-column values through a ScalarResult; inputs include `select(Document).where` with the arguments detailed below — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(Document)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L487 | `select(Document)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L488 | Continue the enclosing expression: build a SQL predicate requiring `Document.project_id` equals `project_id`. |
| L489 | Continue the enclosing expression: build a SQL predicate requiring `Document.status` equals `'Completed'`. |
| L490 | `Document.deleted_at.is_(None)` — Build an SQL IS predicate, commonly IS NULL for a live-row filter. |
| L491 | `Document.active_index_version.is_not(None)` — Build an SQL IS NOT predicate, commonly IS NOT NULL. |
| L492 | Close the expression/container begun at L487; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L493 | Close the expression/container begun at L486; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L494 | Close the expression/container begun at L485; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L495 | Evaluate the right-hand side, then bind/store it in `sources`: iterate `rows`, binding each item to `row` and retain only items satisfying `row.active_index_version is not None`; produce `AuthorizedSource(document_id=row.id, index_version=row.active_index_version, file_name=row.file_name)` into a new list. |
| L496 | `AuthorizedSource(document_id=row.id, index_version=row.active_index_version, file_name=row.file_name)` — Construct `AuthorizedSource` with the shown fields; its class/model initialization rules apply. |
| L497 | Supply `document_id` = `row.id`. Document UUID; filenames do not establish document identity. Evaluate the value as: the `id` attribute of `row`. |
| L498 | Supply `index_version` = `row.active_index_version`. UUID of one document's vector-index namespace, separate from its active publication pointer. Evaluate the value as: the `active_index_version` attribute of `row`. |
| L499 | Supply `file_name` = `row.file_name`. Display PDF filename; immutable IDs establish ownership and evidence identity. Evaluate the value as: the `file_name` attribute of `row`. |
| L500 | Close the expression/container begun at L496; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L501 | Contribute the current `row` value to the expression being assembled. |
| L502 | Continue the enclosing expression: compare whether `row.active_index_version` is not the same object as `None`. |
| L503 | Close the expression/container begun at L495; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L504 | `sources.sort(key=lambda s: (str(s.document_id), str(s.index_version)))` — Invoke `sources.sort` with the shown inputs and use its result; see the function overview for its role in this flow. The return value is not assigned here. |
| L505 | Evaluate the branch condition: invert the truthiness of `sources`. If truthy, enter L506; otherwise skip this indented block and continue after it. |
| L506 | Raise `NoReadySourcesError('No completed documents are available to answer this question.')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L507 | Supply positional argument 1 to `NoReadySourcesError`: `'No completed documents are available to answer this question.'`. |
| L508 | Close the expression/container begun at L506; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L509 | Compute the return value: the current `sources` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `snapshot_document_ids(sources: Sequence[AuthorizedSource]) -> list[dict[str, str]]`

**Arguments:** Authorized source DTOs. **Returns:** JSON dictionaries with `documentId`, `indexVersion`, `fileName`. **Work:** Converts UUIDs to strings in input order.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-snapshot-document-ids"></a>

#### Line-by-line execution

[Current source: lines 512–521](../../../../Backend/app/repositories/messages.py#L512-L521). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `sources` | `Sequence[AuthorizedSource]`; required; positional or keyword | Caller-supplied sources; each read, transformation, and validation is traced below. |

**Declared result:** `list[dict[str, str]]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 512 | def snapshot_document_ids(sources: Sequence[AuthorizedSource]) -> list[dict[str, str]]:
 513 |     """Serialize an authorized-source snapshot for turn metadata."""
 514 |     return [
 515 |         {
 516 |             "documentId": str(source.document_id),
 517 |             "indexVersion": str(source.index_version),
 518 |             "fileName": source.file_name,
 519 |         }
 520 |         for source in sources
 521 |     ]
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L512 | Define `snapshot_document_ids`; bind its arguments when called. The body executes only when invoked. |
| L513 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L514 | Compute the return value: iterate `sources`, binding each item to `source`; produce `{'documentId': str(source.document_id), 'indexVersion': str(source.index_version), 'fileName': source.file_name}` into a new list. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L515 | Contribute build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping to the expression being assembled. |
| L516 | Add mapping entry `'documentId'`: `str(source.document_id)` — Convert the input to its string representation. |
| L517 | Add mapping entry `'indexVersion'`: `str(source.index_version)` — Convert the input to its string representation. |
| L518 | Add mapping entry `'fileName'`: the `file_name` attribute of `source`. |
| L519 | Close the expression/container begun at L515; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L520 | Contribute the current `source` value to the expression being assembled. |
| L521 | Close the expression/container begun at L514; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `record_snapshot(session, *, user_message_id: UUID, snapshot: Sequence[AuthorizedSource]) -> None`

**Arguments:** Session, turn ID, source list. **Returns:** `None`. **Work:** Loads the message (missing → no-op), copies its metadata, replaces `sourceSnapshot` using the serializer, assigns the new dict, and flushes. This helper does not independently check token/role/ownership; caller has already claimed the turn.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-record-snapshot"></a>

#### Line-by-line execution

[Current source: lines 524–537](../../../../Backend/app/repositories/messages.py#L524-L537). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_message_id` | `UUID`; required; keyword-only | Caller-supplied user message id; each read, transformation, and validation is traced below. |
| `snapshot` | `Sequence[AuthorizedSource]`; required; keyword-only | Caller-supplied snapshot; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 524 | def record_snapshot(
 525 |     session: Session,
 526 |     *,
 527 |     user_message_id: UUID,
 528 |     snapshot: Sequence[AuthorizedSource],
 529 | ) -> None:
 530 |     """Persist the source snapshot into the claimed turn's metadata."""
 531 |     row = session.get(Message, user_message_id)
 532 |     if row is None:
 533 |         return
 534 |     metadata = dict(row.message_metadata or {})
 535 |     metadata["sourceSnapshot"] = snapshot_document_ids(snapshot)
 536 |     row.message_metadata = metadata
 537 |     session.flush()
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L524 | Define `record_snapshot`; bind its arguments when called. The body executes only when invoked. |
| L525 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L526 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L527 | Declare parameter `user_message_id` with annotation `UUID`. Caller-supplied user message id; its uses and transformations are traced below. |
| L528 | Declare parameter `snapshot` with annotation `Sequence[AuthorizedSource]`. Caller-supplied snapshot; its uses and transformations are traced below. |
| L529 | Finish/continue the signature; the declared return annotation is `None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L530 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L531 | Evaluate the right-hand side, then bind/store it in `row`: `session.get(Message, user_message_id)` — Look up the mapped object by primary key, using the session identity map when possible, otherwise SQL. |
| L532 | Evaluate the branch condition: compare whether `row` is the same object as `None`. If truthy, enter L533; otherwise skip this indented block and continue after it. |
| L533 | Compute the return value: None. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L534 | Evaluate the right-hand side, then bind/store it in `metadata`: `dict(row.message_metadata or {})` — Build a mapping from the supplied items/keywords; copying a mapping is shallow. |
| L535 | Evaluate the right-hand side, then bind/store it in `metadata['sourceSnapshot']`: `snapshot_document_ids(snapshot)` — Call [snapshot_document_ids](#walk-snapshot-document-ids) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L536 | Evaluate the right-hand side, then bind/store it in `row.message_metadata`: the current `metadata` value. |
| L537 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |

<!-- END LINE WALKTHROUGH -->

### `snapshot_matches(snapshot, current) -> bool`

**Arguments:** Two sequences of authorized sources. **Returns:** Exact set equality of `(document_id, index_version)`. **Work:** Ignores order, duplicate pairs, and display-name differences; adding/removing/reversioning a source changes the set.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-snapshot-matches"></a>

#### Line-by-line execution

[Current source: lines 540–544](../../../../Backend/app/repositories/messages.py#L540-L544). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `snapshot` | `Sequence[AuthorizedSource]`; required; positional or keyword | Caller-supplied snapshot; each read, transformation, and validation is traced below. |
| `current` | `Sequence[AuthorizedSource]`; required; positional or keyword | Caller-supplied current; each read, transformation, and validation is traced below. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 540 | def snapshot_matches(snapshot: Sequence[AuthorizedSource], current: Sequence[AuthorizedSource]) -> bool:
 541 |     """True when the authorized pairs are identical (order-insensitive)."""
 542 |     return {(s.document_id, s.index_version) for s in snapshot} == {
 543 |         (s.document_id, s.index_version) for s in current
 544 |     }
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L540 | Define `snapshot_matches`; bind its arguments when called. The body executes only when invoked. |
| L541 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L542 | Compute the return value: compare whether `{(s.document_id, s.index_version) for s in snapshot}` equals `{(s.document_id, s.index_version) for s in current}`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L543 | Contribute build a tuple containing `s.document_id`, `s.index_version` to the expression being assembled. |
| L544 | Close the parenthesized expression; delimiters only group the preceding operation. |

<!-- END LINE WALKTHROUGH -->

## Persistence, failure, cancellation

### `persist_assistant_answer(session, *, user_id, project_id, conversation_id, user_message_id, generation_token, snapshot, answer: str, citations: Sequence[Citation], model: str, latency_ms: int) -> TurnResponse`

- **Arguments:** Session, authenticated scope/turn UUIDs, expected generation UUID, original authorized pairs, generated content/verified citations, model label and elapsed milliseconds.
- **Returns:** DTOs for the completed user turn and new assistant reply, after flushing; caller commits.
- **Work:** Rechecks live ownership and the user row. Rejects non-active status, mismatched token, or a non-null expired deadline. Resolves the current ready-source set; missing/empty becomes `snapshot_invalid`, changed pairs become `snapshot_changed`. Allocates next position (conversation lock), creates an assistant with camelCase citation JSON and model/latency/snapshot metadata, marks the user completed, clears claim fields, adds/flushed reply, and converts both rows.
- **Boundaries:** Raises `ClaimLostError` or `SnapshotMismatchError` before normal completion when checks fail. It consumes already-refined `Citation` objects; it does not rerun citation matching or call providers. The checks are ORM reads followed by mutation; no compare-and-set update of the user row is issued here.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-persist-assistant-answer"></a>

#### Line-by-line execution

[Current source: lines 552–641](../../../../Backend/app/repositories/messages.py#L552-L641). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |
| `user_message_id` | `UUID`; required; keyword-only | Caller-supplied user message id; each read, transformation, and validation is traced below. |
| `generation_token` | `UUID`; required; keyword-only | Generation claim token used to fence a late answer. |
| `snapshot` | `Sequence[AuthorizedSource]`; required; keyword-only | Caller-supplied snapshot; each read, transformation, and validation is traced below. |
| `answer` | `str`; required; keyword-only | Caller-supplied answer; each read, transformation, and validation is traced below. |
| `citations` | `Sequence[Citation]`; required; keyword-only | Caller-supplied citations; each read, transformation, and validation is traced below. |
| `model` | `str`; required; keyword-only | Caller-supplied model; each read, transformation, and validation is traced below. |
| `latency_ms` | `int`; required; keyword-only | Caller-supplied latency ms; each read, transformation, and validation is traced below. |

**Declared result:** `TurnResponse`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 552 | def persist_assistant_answer(
 553 |     session: Session,
 554 |     *,
 555 |     user_id: UUID,
 556 |     project_id: UUID,
 557 |     conversation_id: UUID,
 558 |     user_message_id: UUID,
 559 |     generation_token: UUID,
 560 |     snapshot: Sequence[AuthorizedSource],
 561 |     answer: str,
 562 |     citations: Sequence[Citation],
 563 |     model: str,
 564 |     latency_ms: int,
 565 | ) -> TurnResponse:
 566 |     """Persist the assistant row and finalize the user turn.
 567 | 
 568 |     Commits only when the generation claim is still current and
 569 |     unexpired, the source snapshot is still valid, and the
 570 |     project/conversation is still accessible.  Raises
 571 |     :class:`ClaimLostError` otherwise (the late answer is discarded and
 572 |     no assistant row is created).  A snapshot mismatch raises
 573 |     :class:`SnapshotMismatchError` so the caller marks the turn
 574 |     ``failed`` in a fresh transaction, letting the client retry with
 575 |     fresh sources.
 576 |     """
 577 |     conversation = get_owned_conversation(
 578 |         session,
 579 |         user_id=user_id,
 580 |         project_id=project_id,
 581 |         conversation_id=conversation_id,
 582 |     )
 583 |     if conversation is None:
 584 |         raise ClaimLostError("conversation no longer accessible")
 585 |     user_message = session.scalar(
 586 |         select(Message).where(
 587 |             Message.id == user_message_id,
 588 |             Message.conversation_id == conversation_id,
 589 |             Message.role == "user",
 590 |         )
 591 |     )
 592 |     if user_message is None:
 593 |         raise ClaimLostError("user turn no longer exists")
 594 |     now = utcnow()
 595 |     if (
 596 |         user_message.generation_status not in ACTIVE_STATUSES
 597 |         or user_message.generation_token != generation_token
 598 |         or (
 599 |             user_message.generation_expires_at is not None
 600 |             and user_message.generation_expires_at <= now
 601 |         )
 602 |     ):
 603 |         raise ClaimLostError("generation claim is stale (cancelled or expired)")
 604 |     try:
 605 |         current = resolve_authorized_sources(
 606 |             session, user_id=user_id, project_id=project_id
 607 |         )
 608 |     except (NoReadySourcesError, NotFoundError) as exc:
 609 |         raise SnapshotMismatchError(
 610 |             "snapshot_invalid", "source snapshot no longer valid"
 611 |         ) from exc
 612 |     if not snapshot_matches(snapshot, current):
 613 |         raise SnapshotMismatchError(
 614 |             "snapshot_changed", "source snapshot changed during generation"
 615 |         )
 616 | 
 617 |     position = next_message_position(session, conversation_id=conversation_id)
 618 |     assistant = Message(
 619 |         conversation_id=conversation_id,
 620 |         role="assistant",
 621 |         content=answer,
 622 |         position=position,
 623 |         citations=[
 624 |             citation.model_dump(mode="json", by_alias=True) for citation in citations
 625 |         ],
 626 |         message_metadata={
 627 |             "model": model,
 628 |             "latencyMs": latency_ms,
 629 |             "sourceSnapshot": snapshot_document_ids(snapshot),
 630 |         },
 631 |         reply_to_message_id=user_message.id,
 632 |     )
 633 |     user_message.generation_status = "completed"
 634 |     user_message.generation_token = None
 635 |     user_message.generation_expires_at = None
 636 |     session.add(assistant)
 637 |     session.flush()
 638 |     return TurnResponse(
 639 |         user_message=to_message_dto(user_message),
 640 |         assistant_message=to_message_dto(assistant),
 641 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L552 | Define `persist_assistant_answer`; bind its arguments when called. The body executes only when invoked. |
| L553 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L554 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L555 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L556 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L557 | Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L558 | Declare parameter `user_message_id` with annotation `UUID`. Caller-supplied user message id; its uses and transformations are traced below. |
| L559 | Declare parameter `generation_token` with annotation `UUID`. Generation claim token used to fence a late answer. |
| L560 | Declare parameter `snapshot` with annotation `Sequence[AuthorizedSource]`. Caller-supplied snapshot; its uses and transformations are traced below. |
| L561 | Declare parameter `answer` with annotation `str`. Caller-supplied answer; its uses and transformations are traced below. |
| L562 | Declare parameter `citations` with annotation `Sequence[Citation]`. Caller-supplied citations; its uses and transformations are traced below. |
| L563 | Declare parameter `model` with annotation `str`. Caller-supplied model; its uses and transformations are traced below. |
| L564 | Declare parameter `latency_ms` with annotation `int`. Caller-supplied latency ms; its uses and transformations are traced below. |
| L565 | Finish/continue the signature; the declared return annotation is `TurnResponse`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L566 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L568 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L569 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L570 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L571 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L572 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L573 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L574 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L575 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L576 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L577 | Evaluate the right-hand side, then bind/store it in `conversation`: `get_owned_conversation(session, user_id=user_id, project_id=project_id, conversation_id=conversation_id)` — Call [get_owned_conversation](../db/queries.md#walk-get-owned-conversation) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L578 | Supply positional argument 1 to `get_owned_conversation`: the current `session` value. |
| L579 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L580 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L581 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L582 | Close the expression/container begun at L577; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L583 | Evaluate the branch condition: compare whether `conversation` is the same object as `None`. If truthy, enter L584; otherwise skip this indented block and continue after it. |
| L584 | Raise `ClaimLostError('conversation no longer accessible')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L585 | Evaluate the right-hand side, then bind/store it in `user_message`: `session.scalar(select(Message).where(Message.id == user_message_id, Message.conversation_id == conversation_id, Message.role == 'user'))` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(Message).where(Message.id == user_message_id, Message.conversation_id == conversation_id, Message.role == 'user')` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L586 | `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L587 | Continue the enclosing expression: build a SQL predicate requiring `Message.id` equals `user_message_id`. |
| L588 | Continue the enclosing expression: build a SQL predicate requiring `Message.conversation_id` equals `conversation_id`. |
| L589 | Continue the enclosing expression: build a SQL predicate requiring `Message.role` equals `'user'`. |
| L590 | Close the expression/container begun at L586; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L591 | Close the expression/container begun at L585; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L592 | Evaluate the branch condition: compare whether `user_message` is the same object as `None`. If truthy, enter L593; otherwise skip this indented block and continue after it. |
| L593 | Raise `ClaimLostError('user turn no longer exists')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L594 | Evaluate the right-hand side, then bind/store it in `now`: `utcnow()` — Read the current timezone-aware UTC timestamp. |
| L595 | Evaluate the branch condition: evaluate `user_message.generation_status not in ACTIVE_STATUSES or user_message.generation_token != generation_token or (user_message.generation_expires_at is not None and user_message.generation_expires_at <= now)` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L603; otherwise skip this indented block and continue after it. |
| L596 | Continue the enclosing expression: evaluate `user_message.generation_status not in ACTIVE_STATUSES or user_message.generation_token != generation_token or (user_message.generation_expires_at is not None and user_message.generation_expires_at <= now)` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L597 | Continue the enclosing expression: compare whether `user_message.generation_token` differs from `generation_token`. |
| L598 | Continue the operation begun at L595: Evaluate the branch condition: evaluate `user_message.generation_status not in ACTIVE_STATUSES or user_message.generation_token != generation_token or (user_message.generation_expires_at is not None and user_message.generation_expires_at <= now)` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L603; otherwise skip this indented block and continue after it. |
| L599 | Continue the enclosing expression: evaluate `user_message.generation_expires_at is not None and user_message.generation_expires_at <= now` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. |
| L600 | Continue the enclosing expression: compare whether `user_message.generation_expires_at` is at most `now`. |
| L601 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L602 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L603 | Raise `ClaimLostError('generation claim is stale (cancelled or expired)')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L604 | Enter the protected block; failures are matched against `(NoReadySourcesError, NotFoundError)` in order. |
| L605 | Evaluate the right-hand side, then bind/store it in `current`: `resolve_authorized_sources(session, user_id=user_id, project_id=project_id)` — Call [resolve_authorized_sources](#walk-resolve-authorized-sources) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L606 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L607 | Close the expression/container begun at L605; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L608 | Handle `(NoReadySourcesError, NotFoundError)` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L609 | Raise `SnapshotMismatchError('snapshot_invalid', 'source snapshot no longer valid')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L610 | Supply positional argument 1 to `SnapshotMismatchError`: `'snapshot_invalid'`. |
| L611 | Contribute the current `exc` value to the expression being assembled. |
| L612 | Evaluate the branch condition: invert the truthiness of `snapshot_matches(snapshot, current)`. If truthy, enter L613; otherwise skip this indented block and continue after it. |
| L613 | Raise `SnapshotMismatchError('snapshot_changed', 'source snapshot changed during generation')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L614 | Supply positional argument 1 to `SnapshotMismatchError`: `'snapshot_changed'`. |
| L615 | Close the expression/container begun at L613; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L617 | Evaluate the right-hand side, then bind/store it in `position`: `next_message_position(session, conversation_id=conversation_id)` — Call [next_message_position](../db/queries.md#walk-next-message-position) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L618 | Evaluate the right-hand side, then bind/store it in `assistant`: `Message` with the arguments detailed below — Construct `Message` with the shown fields; its class/model initialization rules apply. |
| L619 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L620 | Supply `role` = `'assistant'`.  Evaluate the value as: `'assistant'`. |
| L621 | Supply `content` = `answer`. Message text supplied for a persisted conversation turn. Evaluate the value as: the current `answer` value. |
| L622 | Supply `position` = `position`.  Evaluate the value as: the current `position` value. |
| L623 | Supply `citations` = `[citation.model_dump(mode='json', by_alias=True) for citation in citations]`.  Evaluate the value as: iterate `citations`, binding each item to `citation`; produce `citation.model_dump(mode='json', by_alias=True)` into a new list. |
| L624 | `citation.model_dump(mode='json', by_alias=True)` — Serialize Pydantic fields into a dictionary; by_alias=True uses wire names and mode='json' converts JSON-compatible values. |
| L625 | Close the expression/container begun at L623; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L626 | Supply `message_metadata` = `{'model': model, 'latencyMs': latency_ms, 'sourceSnapshot': snapshot_document_ids(snapshot)}`.  Evaluate the value as: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. |
| L627 | Add mapping entry `'model'`: the current `model` value. |
| L628 | Add mapping entry `'latencyMs'`: the current `latency_ms` value. |
| L629 | Add mapping entry `'sourceSnapshot'`: `snapshot_document_ids(snapshot)` — Call [snapshot_document_ids](#walk-snapshot-document-ids) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L630 | Close the expression/container begun at L626; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L631 | Supply `reply_to_message_id` = `user_message.id`.  Evaluate the value as: the `id` attribute of `user_message`. |
| L632 | Close the expression/container begun at L618; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L633 | Evaluate the right-hand side, then bind/store it in `user_message.generation_status`: `'completed'`. |
| L634 | Evaluate the right-hand side, then bind/store it in `user_message.generation_token`: None (no value). |
| L635 | Evaluate the right-hand side, then bind/store it in `user_message.generation_expires_at`: None (no value). |
| L636 | `session.add(assistant)` — Attach the ORM object to this session for insertion/update tracking; this does not commit it. The return value is not assigned here. |
| L637 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L638 | Compute the return value: `TurnResponse(user_message=to_message_dto(user_message), assistant_message=to_message_dto(assistant))` — Construct `TurnResponse` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L639 | Supply `user_message` = `to_message_dto(user_message)`.  Evaluate the value as: `to_message_dto(user_message)` — Call [to_message_dto](conversations.md#walk-to-message-dto) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L640 | Supply `assistant_message` = `to_message_dto(assistant)`.  Evaluate the value as: `to_message_dto(assistant)` — Call [to_message_dto](conversations.md#walk-to-message-dto) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L641 | Close the expression/container begun at L638; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `mark_turn_failed(session, *, user_message_id, generation_token, error_code: str, error_message: str) -> bool`

**Arguments:** Session, user-turn UUID, expected token, diagnostic code/text. **Returns:** True when changed, false if absent/non-active/token-mismatched. **Work:** Adds error metadata with message truncated to 500 characters and current ISO time; sets `failed`, clears claim fields, and flushes. It does not require an unexpired deadline and does not sanitize the supplied text beyond truncation.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-mark-turn-failed"></a>

#### Line-by-line execution

[Current source: lines 644–682](../../../../Backend/app/repositories/messages.py#L644-L682). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_message_id` | `UUID`; required; keyword-only | Caller-supplied user message id; each read, transformation, and validation is traced below. |
| `generation_token` | `UUID`; required; keyword-only | Generation claim token used to fence a late answer. |
| `error_code` | `str`; required; keyword-only | Machine-readable failure category stored or exposed by the operation. |
| `error_message` | `str`; required; keyword-only | Human-readable failure detail; truncation alone does not redact sensitive content. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 644 | def mark_turn_failed(
 645 |     session: Session,
 646 |     *,
 647 |     user_message_id: UUID,
 648 |     generation_token: UUID,
 649 |     error_code: str,
 650 |     error_message: str,
 651 | ) -> bool:
 652 |     """Mark an active turn ``failed`` when the claim is still current.
 653 | 
 654 |     Returns True when the row was updated, False when the claim is stale
 655 |     (e.g. the user already cancelled) — a cancelled turn is never
 656 |     resurrected to ``failed``.
 657 |     """
 658 |     row = session.scalar(
 659 |         select(Message).where(
 660 |             Message.id == user_message_id,
 661 |             Message.role == "user",
 662 |         )
 663 |     )
 664 |     if row is None:
 665 |         return False
 666 |     if (
 667 |         row.generation_status not in ACTIVE_STATUSES
 668 |         or row.generation_token != generation_token
 669 |     ):
 670 |         return False
 671 |     metadata = dict(row.message_metadata or {})
 672 |     metadata["error"] = {
 673 |         "code": error_code,
 674 |         "message": error_message[:500],
 675 |         "at": utcnow().isoformat(),
 676 |     }
 677 |     row.message_metadata = metadata
 678 |     row.generation_status = "failed"
 679 |     row.generation_token = None
 680 |     row.generation_expires_at = None
 681 |     session.flush()
 682 |     return True
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L644 | Define `mark_turn_failed`; bind its arguments when called. The body executes only when invoked. |
| L645 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L646 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L647 | Declare parameter `user_message_id` with annotation `UUID`. Caller-supplied user message id; its uses and transformations are traced below. |
| L648 | Declare parameter `generation_token` with annotation `UUID`. Generation claim token used to fence a late answer. |
| L649 | Declare parameter `error_code` with annotation `str`. Machine-readable failure category stored or exposed by the operation. |
| L650 | Declare parameter `error_message` with annotation `str`. Human-readable failure detail; truncation alone does not redact sensitive content. |
| L651 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L652 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L654 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L655 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L656 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L657 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L658 | Evaluate the right-hand side, then bind/store it in `row`: `session.scalar(select(Message).where(Message.id == user_message_id, Message.role == 'user'))` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(Message).where(Message.id == user_message_id, Message.role == 'user')` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L659 | `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L660 | Continue the enclosing expression: build a SQL predicate requiring `Message.id` equals `user_message_id`. |
| L661 | Continue the enclosing expression: build a SQL predicate requiring `Message.role` equals `'user'`. |
| L662 | Close the expression/container begun at L659; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L663 | Close the expression/container begun at L658; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L664 | Evaluate the branch condition: compare whether `row` is the same object as `None`. If truthy, enter L665; otherwise skip this indented block and continue after it. |
| L665 | Compute the return value: `False`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L666 | Evaluate the branch condition: evaluate `row.generation_status not in ACTIVE_STATUSES or row.generation_token != generation_token` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L670; otherwise skip this indented block and continue after it. |
| L667 | Continue the enclosing expression: evaluate `row.generation_status not in ACTIVE_STATUSES or row.generation_token != generation_token` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L668 | Continue the enclosing expression: compare whether `row.generation_token` differs from `generation_token`. |
| L669 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L670 | Compute the return value: `False`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L671 | Evaluate the right-hand side, then bind/store it in `metadata`: `dict(row.message_metadata or {})` — Build a mapping from the supplied items/keywords; copying a mapping is shallow. |
| L672 | Evaluate the right-hand side, then bind/store it in `metadata['error']`: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. |
| L673 | Add mapping entry `'code'`: the current `error_code` value. |
| L674 | Add mapping entry `'message'`: slice `error_message` from the beginning up to `500` (exclusive stop). |
| L675 | Add mapping entry `'at'`: `utcnow().isoformat()` — Format the timestamp/date as an ISO-format string for the cursor/payload; first obtain the receiver: `utcnow()` — Read the current timezone-aware UTC timestamp. |
| L676 | Close the expression/container begun at L672; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L677 | Evaluate the right-hand side, then bind/store it in `row.message_metadata`: the current `metadata` value. |
| L678 | Evaluate the right-hand side, then bind/store it in `row.generation_status`: `'failed'`. |
| L679 | Evaluate the right-hand side, then bind/store it in `row.generation_token`: None (no value). |
| L680 | Evaluate the right-hand side, then bind/store it in `row.generation_expires_at`: None (no value). |
| L681 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L682 | Compute the return value: `True`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `cancel_turn(session, *, user_id, project_id, conversation_id, message_id) -> tuple[MessageDto, bool]`

**Arguments:** Session and exact authenticated turn scope. **Returns:** Authoritative cancelled DTO and `True`, including already-cancelled replay. **Work:** Requires owned conversation and user message. For active status, sets cancelled, clears token/expiry, and flushes. Missing is `NotFoundError`; completed/failed/other states raise `InvalidStateError`. Does not abort the external network call already in progress.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-cancel-turn"></a>

#### Line-by-line execution

[Current source: lines 685–723](../../../../Backend/app/repositories/messages.py#L685-L723). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |
| `message_id` | `UUID`; required; keyword-only | Persisted message UUID identifying the turn being read, retried, or cancelled. |

**Declared result:** `tuple[MessageDto, bool]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 685 | def cancel_turn(
 686 |     session: Session,
 687 |     *,
 688 |     user_id: UUID,
 689 |     project_id: UUID,
 690 |     conversation_id: UUID,
 691 |     message_id: UUID,
 692 | ) -> tuple[MessageDto, bool]:
 693 |     """Cancel the active turn; the token is invalidated so late answers die.
 694 | 
 695 |     The persisted user message stays visible with
 696 |     ``generationStatus: "cancelled"``.  Cancelling an already-cancelled
 697 |     turn is idempotent (returns the same message).  Completed/failed
 698 |     turns raise :class:`InvalidStateError`.
 699 |     """
 700 |     conversation = _owned_conversation(
 701 |         session,
 702 |         user_id=user_id,
 703 |         project_id=project_id,
 704 |         conversation_id=conversation_id,
 705 |     )
 706 |     row = session.scalar(
 707 |         select(Message).where(
 708 |             Message.id == message_id,
 709 |             Message.conversation_id == conversation.id,
 710 |             Message.role == "user",
 711 |         )
 712 |     )
 713 |     if row is None:
 714 |         raise NotFoundError(f"message not found: {message_id}")
 715 |     if row.generation_status in ACTIVE_STATUSES:
 716 |         row.generation_status = "cancelled"
 717 |         row.generation_token = None
 718 |         row.generation_expires_at = None
 719 |         session.flush()
 720 |         return to_message_dto(row), True
 721 |     if row.generation_status == "cancelled":
 722 |         return to_message_dto(row), True
 723 |     raise InvalidStateError("Only an active turn can be cancelled.")
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L685 | Define `cancel_turn`; bind its arguments when called. The body executes only when invoked. |
| L686 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L687 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L688 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L689 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L690 | Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L691 | Declare parameter `message_id` with annotation `UUID`. Persisted message UUID identifying the turn being read, retried, or cancelled. |
| L692 | Finish/continue the signature; the declared return annotation is `tuple[MessageDto, bool]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L693 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L695 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L696 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L697 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L698 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L699 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L700 | Evaluate the right-hand side, then bind/store it in `conversation`: `_owned_conversation(session, user_id=user_id, project_id=project_id, conversation_id=conversation_id)` — Call [_owned_conversation](#walk--owned-conversation) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L701 | Supply positional argument 1 to `_owned_conversation`: the current `session` value. |
| L702 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L703 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L704 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L705 | Close the expression/container begun at L700; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L706 | Evaluate the right-hand side, then bind/store it in `row`: `session.scalar(select(Message).where(Message.id == message_id, Message.conversation_id == conversation.id, Message.role == 'user'))` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(Message).where(Message.id == message_id, Message.conversation_id == conversation.id, Message.role == 'user')` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L707 | `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L708 | Continue the enclosing expression: build a SQL predicate requiring `Message.id` equals `message_id`. |
| L709 | Continue the enclosing expression: build a SQL predicate requiring `Message.conversation_id` equals `conversation.id`. |
| L710 | Continue the enclosing expression: build a SQL predicate requiring `Message.role` equals `'user'`. |
| L711 | Close the expression/container begun at L707; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L712 | Close the expression/container begun at L706; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L713 | Evaluate the branch condition: compare whether `row` is the same object as `None`. If truthy, enter L714; otherwise skip this indented block and continue after it. |
| L714 | Raise `NotFoundError(f'message not found: {message_id}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L715 | Evaluate the branch condition: compare whether `row.generation_status` is contained in `ACTIVE_STATUSES`. If truthy, enter L716; otherwise skip this indented block and continue after it. |
| L716 | Evaluate the right-hand side, then bind/store it in `row.generation_status`: `'cancelled'`. |
| L717 | Evaluate the right-hand side, then bind/store it in `row.generation_token`: None (no value). |
| L718 | Evaluate the right-hand side, then bind/store it in `row.generation_expires_at`: None (no value). |
| L719 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L720 | Compute the return value: build a tuple containing `to_message_dto(row)`, `True`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L721 | Evaluate the branch condition: compare whether `row.generation_status` equals `'cancelled'`. If truthy, enter L722; otherwise skip this indented block and continue after it. |
| L722 | Compute the return value: build a tuple containing `to_message_dto(row)`, `True`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L723 | Raise `InvalidStateError('Only an active turn can be cancelled.')`; stop the normal path and transfer control to the nearest matching exception handler. |

<!-- END LINE WALKTHROUGH -->

### `get_turn_status(session, *, user_id, project_id, conversation_id, message_id) -> MessageDto`

**Arguments:** Session and authenticated turn scope. **Returns:** Current user-message DTO. **Work:** Rechecks owned conversation, selects the user message in it, rejects missing rows, and converts. Used internally after claim loss rather than exposed as a standalone GET route.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-turn-status"></a>

#### Line-by-line execution

[Current source: lines 726–750](../../../../Backend/app/repositories/messages.py#L726-L750). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |
| `message_id` | `UUID`; required; keyword-only | Persisted message UUID identifying the turn being read, retried, or cancelled. |

**Declared result:** `MessageDto`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 726 | def get_turn_status(
 727 |     session: Session,
 728 |     *,
 729 |     user_id: UUID,
 730 |     project_id: UUID,
 731 |     conversation_id: UUID,
 732 |     message_id: UUID,
 733 | ) -> MessageDto:
 734 |     """Return the current user-turn DTO for reconciliation after disconnect."""
 735 |     _owned_conversation(
 736 |         session,
 737 |         user_id=user_id,
 738 |         project_id=project_id,
 739 |         conversation_id=conversation_id,
 740 |     )
 741 |     row = session.scalar(
 742 |         select(Message).where(
 743 |             Message.id == message_id,
 744 |             Message.conversation_id == conversation_id,
 745 |             Message.role == "user",
 746 |         )
 747 |     )
 748 |     if row is None:
 749 |         raise NotFoundError(f"message not found: {message_id}")
 750 |     return to_message_dto(row)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L726 | Define `get_turn_status`; bind its arguments when called. The body executes only when invoked. |
| L727 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L728 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L729 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L730 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L731 | Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L732 | Declare parameter `message_id` with annotation `UUID`. Persisted message UUID identifying the turn being read, retried, or cancelled. |
| L733 | Finish/continue the signature; the declared return annotation is `MessageDto`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L734 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L735 | `_owned_conversation(session, user_id=user_id, project_id=project_id, conversation_id=conversation_id)` — Call [_owned_conversation](#walk--owned-conversation) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L736 | Supply positional argument 1 to `_owned_conversation`: the current `session` value. |
| L737 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L738 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L739 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L740 | Close the expression/container begun at L735; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L741 | Evaluate the right-hand side, then bind/store it in `row`: `session.scalar(select(Message).where(Message.id == message_id, Message.conversation_id == conversation_id, Message.role == 'user'))` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(Message).where(Message.id == message_id, Message.conversation_id == conversation_id, Message.role == 'user')` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L742 | `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L743 | Continue the enclosing expression: build a SQL predicate requiring `Message.id` equals `message_id`. |
| L744 | Continue the enclosing expression: build a SQL predicate requiring `Message.conversation_id` equals `conversation_id`. |
| L745 | Continue the enclosing expression: build a SQL predicate requiring `Message.role` equals `'user'`. |
| L746 | Close the expression/container begun at L742; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L747 | Close the expression/container begun at L741; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L748 | Evaluate the branch condition: compare whether `row` is the same object as `None`. If truthy, enter L749; otherwise skip this indented block and continue after it. |
| L749 | Raise `NotFoundError(f'message not found: {message_id}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L750 | Compute the return value: `to_message_dto(row)` — Call [to_message_dto](conversations.md#walk-to-message-dto) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_owned_conversation(session, *, user_id, project_id, conversation_id) -> Conversation`

**Arguments:** Session and scope IDs. **Returns:** Live owned conversation. **Work:** Delegates to `get_owned_conversation`, raising `NotFoundError` when unavailable; no row lock is added here.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--owned-conversation"></a>

#### Line-by-line execution

[Current source: lines 758–767](../../../../Backend/app/repositories/messages.py#L758-L767). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | not annotated; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | not annotated; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | not annotated; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | not annotated; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |

**Declared result:** `Conversation`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 758 | def _owned_conversation(session, *, user_id, project_id, conversation_id) -> Conversation:
 759 |     conversation = get_owned_conversation(
 760 |         session,
 761 |         user_id=user_id,
 762 |         project_id=project_id,
 763 |         conversation_id=conversation_id,
 764 |     )
 765 |     if conversation is None:
 766 |         raise NotFoundError(f"conversation not found: {conversation_id}")
 767 |     return conversation
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L758 | Define `_owned_conversation`; bind its arguments when called. The body executes only when invoked. |
| L759 | Evaluate the right-hand side, then bind/store it in `conversation`: `get_owned_conversation(session, user_id=user_id, project_id=project_id, conversation_id=conversation_id)` — Call [get_owned_conversation](../db/queries.md#walk-get-owned-conversation) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L760 | Supply positional argument 1 to `get_owned_conversation`: the current `session` value. |
| L761 | Supply `user_id` = `user_id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the current `user_id` value. |
| L762 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L763 | Supply `conversation_id` = `conversation_id`. Conversation UUID identifying the owned chat and ordered message sequence. Evaluate the value as: the current `conversation_id` value. |
| L764 | Close the expression/container begun at L759; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L765 | Evaluate the branch condition: compare whether `conversation` is the same object as `None`. If truthy, enter L766; otherwise skip this indented block and continue after it. |
| L766 | Raise `NotFoundError(f'conversation not found: {conversation_id}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L767 | Compute the return value: the current `conversation` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_load_completed_turn(session, *, user_message, conversation_id) -> TurnResponse`

**Arguments:** Session, completed user ORM row, conversation ID. **Returns:** Original persisted user/assistant pair. **Work:** Selects an assistant whose reply target and conversation match, converts both; missing reply raises `ClaimLostError` as an integrity failure.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--load-completed-turn"></a>

#### Line-by-line execution

[Current source: lines 770–785](../../../../Backend/app/repositories/messages.py#L770-L785). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | not annotated; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_message` | not annotated; required; keyword-only | Caller-supplied user message; each read, transformation, and validation is traced below. |
| `conversation_id` | not annotated; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |

**Declared result:** `TurnResponse`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 770 | def _load_completed_turn(session, *, user_message, conversation_id) -> TurnResponse:
 771 |     assistant = session.scalar(
 772 |         select(Message).where(
 773 |             Message.conversation_id == conversation_id,
 774 |             Message.role == "assistant",
 775 |             Message.reply_to_message_id == user_message.id,
 776 |         )
 777 |     )
 778 |     if assistant is None:
 779 |         # A completed user turn without its reply is an integrity
 780 |         # violation; treat it as an error the client cannot resolve.
 781 |         raise ClaimLostError("completed turn has no assistant reply")
 782 |     return TurnResponse(
 783 |         user_message=to_message_dto(user_message),
 784 |         assistant_message=to_message_dto(assistant),
 785 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L770 | Define `_load_completed_turn`; bind its arguments when called. The body executes only when invoked. |
| L771 | Evaluate the right-hand side, then bind/store it in `assistant`: `session.scalar(select(Message).where(Message.conversation_id == conversation_id, Message.role == 'assistant', Message.reply_to_message_id == user_message.id))` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(Message).where(Message.conversation_id == conversation_id, Message.role == 'assistant', Message.reply_to_message_id == user_message.id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L772 | `select(Message)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L773 | Continue the enclosing expression: build a SQL predicate requiring `Message.conversation_id` equals `conversation_id`. |
| L774 | Continue the enclosing expression: build a SQL predicate requiring `Message.role` equals `'assistant'`. |
| L775 | Continue the enclosing expression: build a SQL predicate requiring `Message.reply_to_message_id` equals `user_message.id`. |
| L776 | Close the expression/container begun at L772; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L777 | Close the expression/container begun at L771; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L778 | Evaluate the branch condition: compare whether `assistant` is the same object as `None`. If truthy, enter L781; otherwise skip this indented block and continue after it. |
| L779 | Comment only: A completed user turn without its reply is an integrity. It does not execute; the neighboring code determines behavior. |
| L780 | Comment only: violation; treat it as an error the client cannot resolve.. It does not execute; the neighboring code determines behavior. |
| L781 | Raise `ClaimLostError('completed turn has no assistant reply')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L782 | Compute the return value: `TurnResponse(user_message=to_message_dto(user_message), assistant_message=to_message_dto(assistant))` — Construct `TurnResponse` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L783 | Supply `user_message` = `to_message_dto(user_message)`.  Evaluate the value as: `to_message_dto(user_message)` — Call [to_message_dto](conversations.md#walk-to-message-dto) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L784 | Supply `assistant_message` = `to_message_dto(assistant)`.  Evaluate the value as: `to_message_dto(assistant)` — Call [to_message_dto](conversations.md#walk-to-message-dto) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L785 | Close the expression/container begun at L782; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `_fail_turn_locked(user_message: Message, *, code: str) -> None`

**Arguments:** ORM user row and diagnostic code. **Returns:** `None`. **Work:** Mutates status/token/expiry and adds a fixed "Sources changed while answering." metadata error. It accepts no session, does not acquire a lock or flush, and currently has no caller in this module.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--fail-turn-locked"></a>

#### Line-by-line execution

[Current source: lines 788–794](../../../../Backend/app/repositories/messages.py#L788-L794). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `user_message` | `Message`; required; positional or keyword | Caller-supplied user message; each read, transformation, and validation is traced below. |
| `code` | `str`; required; keyword-only | Caller-supplied code; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 788 | def _fail_turn_locked(user_message: Message, *, code: str) -> None:
 789 |     user_message.generation_status = "failed"
 790 |     user_message.generation_token = None
 791 |     user_message.generation_expires_at = None
 792 |     metadata = dict(user_message.message_metadata or {})
 793 |     metadata["error"] = {"code": code, "message": "Sources changed while answering."}
 794 |     user_message.message_metadata = metadata
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L788 | Define `_fail_turn_locked`; bind its arguments when called. The body executes only when invoked. |
| L789 | Evaluate the right-hand side, then bind/store it in `user_message.generation_status`: `'failed'`. |
| L790 | Evaluate the right-hand side, then bind/store it in `user_message.generation_token`: None (no value). |
| L791 | Evaluate the right-hand side, then bind/store it in `user_message.generation_expires_at`: None (no value). |
| L792 | Evaluate the right-hand side, then bind/store it in `metadata`: `dict(user_message.message_metadata or {})` — Build a mapping from the supplied items/keywords; copying a mapping is shallow. |
| L793 | Evaluate the right-hand side, then bind/store it in `metadata['error']`: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. |
| L794 | Evaluate the right-hand side, then bind/store it in `user_message.message_metadata`: the current `metadata` value. |

<!-- END LINE WALKTHROUGH -->
