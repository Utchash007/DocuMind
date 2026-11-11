# `app/repositories/users.py`

[Source](../../../../Backend/app/repositories/users.py) · [Backend index](../../README.md)

Account bootstrap/profile SQL operations. Callers own short transactions; this module flushes but never commits or contacts Appwrite. Identity is keyed by verified `appwrite_user_id`, never by matching email alone.

## Functions

### `normalize_email(email: str) -> str`

**Arguments:** Verified email string. **Returns:** Stripped lowercase email. **Work:** Applies `strip().lower()`; does not perform syntax or delivery verification.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-normalize-email"></a>

#### Line-by-line execution

[Current source: lines 31–32](../../../../Backend/app/repositories/users.py#L31-L32). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `email` | `str`; required; positional or keyword | Verified identity email, normalized by the user repository before persistence. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  31 | def normalize_email(email: str) -> str:
  32 |     return email.strip().lower()
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L31 | Define `normalize_email`; bind its arguments when called. The body executes only when invoked. |
| L32 | Compute the return value: `email.strip().lower()` — Return a lowercased string copy; first obtain the receiver: `email.strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `get_user(session: Session, user_id: UUID) -> User | None`

**Arguments:** Session and internal UUID. **Returns:** ORM user or `None`. **Work:** Uses `session.get`, benefiting from the identity map when already loaded.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-user"></a>

#### Line-by-line execution

[Current source: lines 35–36](../../../../Backend/app/repositories/users.py#L35-L36). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; positional or keyword | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |

**Declared result:** `User | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  35 | def get_user(session: Session, user_id: UUID) -> User | None:
  36 |     return session.get(User, user_id)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L35 | Define `get_user`; bind its arguments when called. The body executes only when invoked. |
| L36 | Compute the return value: `session.get(User, user_id)` — Look up the mapped object by primary key, using the session identity map when possible, otherwise SQL. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_find_by_appwrite_id(session: Session, appwrite_user_id: str) -> User | None`

**Arguments:** Session and external identity string. **Returns:** Matching user or `None`. **Work:** Executes a scalar `User.appwrite_user_id` equality query.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--find-by-appwrite-id"></a>

#### Line-by-line execution

[Current source: lines 39–42](../../../../Backend/app/repositories/users.py#L39-L42). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `appwrite_user_id` | `str`; required; positional or keyword | Verified external Appwrite identity, distinct from the internal PostgreSQL UUID. |

**Declared result:** `User | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  39 | def _find_by_appwrite_id(session: Session, appwrite_user_id: str) -> User | None:
  40 |     return session.scalar(
  41 |         select(User).where(User.appwrite_user_id == appwrite_user_id)
  42 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L39 | Define `_find_by_appwrite_id`; bind its arguments when called. The body executes only when invoked. |
| L40 | Compute the return value: `session.scalar(select(User).where(User.appwrite_user_id == appwrite_user_id))` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(User).where(User.appwrite_user_id == appwrite_user_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(User)` — Construct a SQL SELECT expression; building it does not execute SQL. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L41 | `select(User).where(User.appwrite_user_id == appwrite_user_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(User)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L42 | Close the expression/container begun at L40; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `_find_by_email(session: Session, email: str) -> User | None`

**Arguments:** Session and already-normalized email. **Returns:** Matching user or `None`. **Work:** Executes exact email equality; normalization is the caller's responsibility.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--find-by-email"></a>

#### Line-by-line execution

[Current source: lines 45–46](../../../../Backend/app/repositories/users.py#L45-L46). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `email` | `str`; required; positional or keyword | Verified identity email, normalized by the user repository before persistence. |

**Declared result:** `User | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  45 | def _find_by_email(session: Session, email: str) -> User | None:
  46 |     return session.scalar(select(User).where(User.email == email))
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L45 | Define `_find_by_email`; bind its arguments when called. The body executes only when invoked. |
| L46 | Compute the return value: `session.scalar(select(User).where(User.email == email))` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(User).where(User.email == email)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(User)` — Construct a SQL SELECT expression; building it does not execute SQL. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_sync_email(session: Session, user: User, email: str) -> None`

**Arguments:** Session, existing user, newly verified normalized email. **Returns:** `None`. **Work:** Returns immediately if unchanged; looks up the new address and leaves the old email intact if another user owns it; otherwise assigns it on the ORM object. Does not flush independently.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--sync-email"></a>

#### Line-by-line execution

[Current source: lines 49–57](../../../../Backend/app/repositories/users.py#L49-L57). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user` | `User`; required; positional or keyword | Caller-supplied user; each read, transformation, and validation is traced below. |
| `email` | `str`; required; positional or keyword | Verified identity email, normalized by the user repository before persistence. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  49 | def _sync_email(session: Session, user: User, email: str) -> None:
  50 |     """Adopt the verified email unless another identity already owns it."""
  51 |     if user.email == email:
  52 |         return
  53 |     owner = _find_by_email(session, email)
  54 |     if owner is not None and owner.id != user.id:
  55 |         # Never merge identities: keep the existing email.
  56 |         return
  57 |     user.email = email
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L49 | Define `_sync_email`; bind its arguments when called. The body executes only when invoked. |
| L50 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L51 | Evaluate the branch condition: compare whether `user.email` equals `email`. If truthy, enter L52; otherwise skip this indented block and continue after it. |
| L52 | Compute the return value: None. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L53 | Evaluate the right-hand side, then bind/store it in `owner`: `_find_by_email(session, email)` — Call [_find_by_email](#walk--find-by-email) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L54 | Evaluate the branch condition: evaluate `owner is not None and owner.id != user.id` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L56; otherwise skip this indented block and continue after it. |
| L55 | Comment only: Never merge identities: keep the existing email.. It does not execute; the neighboring code determines behavior. |
| L56 | Compute the return value: None. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L57 | Evaluate the right-hand side, then bind/store it in `user.email`: the current `email` value. |

<!-- END LINE WALKTHROUGH -->

### `bootstrap_user(session, *, appwrite_user_id: str, email: str) -> User`

- **Arguments:** Caller session, verified external identity, verified email.
- **Returns:** Existing or newly inserted internal user.
- **Work:** Normalizes email, looks up identity, synchronizes/flushes an existing row. Otherwise creates an un-onboarded row within `begin_nested()` and flushes. On `IntegrityError`, the savepoint rolls back; it re-reads a concurrent identity winner, syncs/flushes, and returns it. If no identity winner exists, raises HTTP 409 because the email belongs to another account. Outer transaction ownership remains with the caller.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-bootstrap-user"></a>

#### Line-by-line execution

[Current source: lines 60–99](../../../../Backend/app/repositories/users.py#L60-L99). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `appwrite_user_id` | `str`; required; keyword-only | Verified external Appwrite identity, distinct from the internal PostgreSQL UUID. |
| `email` | `str`; required; keyword-only | Verified identity email, normalized by the user repository before persistence. |

**Declared result:** `User`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  60 | def bootstrap_user(
  61 |     session: Session,
  62 |     *,
  63 |     appwrite_user_id: str,
  64 |     email: str,
  65 | ) -> User:
  66 |     """Return the row for ``appwrite_user_id``, creating it on first login.
  67 | 
  68 |     Creation stores only the verified identity and email; profile fields
  69 |     stay NULL and ``onboarding_completed`` starts ``False``.
  70 |     """
  71 |     normalized = normalize_email(email)
  72 |     existing = _find_by_appwrite_id(session, appwrite_user_id)
  73 |     if existing is not None:
  74 |         _sync_email(session, existing, normalized)
  75 |         session.flush()
  76 |         return existing
  77 | 
  78 |     try:
  79 |         with session.begin_nested():
  80 |             user = User(
  81 |                 appwrite_user_id=appwrite_user_id,
  82 |                 email=normalized,
  83 |                 onboarding_completed=False,
  84 |             )
  85 |             session.add(user)
  86 |             session.flush()
  87 |             return user
  88 |     except IntegrityError:
  89 |         # Either a concurrent first login won the appwrite_user_id race
  90 |         # (re-read the winner below) or a different identity owns this
  91 |         # email (never merge -> conflict).
  92 |         existing = _find_by_appwrite_id(session, appwrite_user_id)
  93 |         if existing is not None:
  94 |             _sync_email(session, existing, normalized)
  95 |             session.flush()
  96 |             return existing
  97 |         raise conflict(
  98 |             "That email address is already associated with another account."
  99 |         ) from None
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L60 | Define `bootstrap_user`; bind its arguments when called. The body executes only when invoked. |
| L61 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L62 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L63 | Declare parameter `appwrite_user_id` with annotation `str`. Verified external Appwrite identity, distinct from the internal PostgreSQL UUID. |
| L64 | Declare parameter `email` with annotation `str`. Verified identity email, normalized by the user repository before persistence. |
| L65 | Finish/continue the signature; the declared return annotation is `User`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L66 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L68 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L69 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L70 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L71 | Evaluate the right-hand side, then bind/store it in `normalized`: `normalize_email(email)` — Call [normalize_email](#walk-normalize-email) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L72 | Evaluate the right-hand side, then bind/store it in `existing`: `_find_by_appwrite_id(session, appwrite_user_id)` — Call [_find_by_appwrite_id](#walk--find-by-appwrite-id) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L73 | Evaluate the branch condition: compare whether `existing` is not the same object as `None`. If truthy, enter L74; otherwise skip this indented block and continue after it. |
| L74 | `_sync_email(session, existing, normalized)` — Call [_sync_email](#walk--sync-email) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L75 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L76 | Compute the return value: the current `existing` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L78 | Enter the protected block; failures are matched against `IntegrityError` in order. |
| L79 | Enter `session.begin_nested()` — Open a SAVEPOINT after SQLAlchemy's pre-flush; a duplicate-insert failure can roll back this savepoint while preserving the outer transaction. Context exits run in reverse order, including on return/exception. |
| L80 | Evaluate the right-hand side, then bind/store it in `user`: `User(appwrite_user_id=appwrite_user_id, email=normalized, onboarding_completed=False)` — Construct `User` with the shown fields; its class/model initialization rules apply. |
| L81 | Supply `appwrite_user_id` = `appwrite_user_id`. Verified external Appwrite identity, distinct from the internal PostgreSQL UUID. Evaluate the value as: the current `appwrite_user_id` value. |
| L82 | Supply `email` = `normalized`. Verified identity email, normalized by the user repository before persistence. Evaluate the value as: the current `normalized` value. |
| L83 | Supply `onboarding_completed` = `False`.  Evaluate the value as: `False`. |
| L84 | Close the expression/container begun at L80; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L85 | `session.add(user)` — Attach the ORM object to this session for insertion/update tracking; this does not commit it. The return value is not assigned here. |
| L86 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L87 | Compute the return value: the current `user` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L88 | Handle `IntegrityError`; only a matching error from the associated try enters this body. |
| L89 | Comment only: Either a concurrent first login won the appwrite_user_id race. It does not execute; the neighboring code determines behavior. |
| L90 | Comment only: (re-read the winner below) or a different identity owns this. It does not execute; the neighboring code determines behavior. |
| L91 | Comment only: email (never merge -> conflict).. It does not execute; the neighboring code determines behavior. |
| L92 | Evaluate the right-hand side, then bind/store it in `existing`: `_find_by_appwrite_id(session, appwrite_user_id)` — Call [_find_by_appwrite_id](#walk--find-by-appwrite-id) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L93 | Evaluate the branch condition: compare whether `existing` is not the same object as `None`. If truthy, enter L94; otherwise skip this indented block and continue after it. |
| L94 | `_sync_email(session, existing, normalized)` — Call [_sync_email](#walk--sync-email) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. The return value is not assigned here. |
| L95 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L96 | Compute the return value: the current `existing` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L97 | Raise `conflict('That email address is already associated with another account.')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `None` as its cause. |
| L98 | Supply positional argument 1 to `conflict`: `'That email address is already associated with another account.'`. |
| L99 | Continue the string/literal value in the surrounding expression. Adjacent string literals are concatenated into one value; no extra function call occurs. |

<!-- END LINE WALKTHROUGH -->

### `update_profile(session, *, user_id: UUID, name: str, date_of_birth: date) -> User | None`

**Arguments:** Session, internal UUID, already-validated name/DOB. **Returns:** Updated user or `None` if absent. **Work:** Loads by primary key, assigns only profile fields, derives onboarding completion with `derive_onboarding_completed`, and flushes. It does not independently repeat all request-model validation or permit identity/email changes.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-update-profile"></a>

#### Line-by-line execution

[Current source: lines 102–123](../../../../Backend/app/repositories/users.py#L102-L123). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `name` | `str`; required; keyword-only | Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. |
| `date_of_birth` | `date`; required; keyword-only | Profile birth date validated against the current date before onboarding completion. |

**Declared result:** `User | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 102 | def update_profile(
 103 |     session: Session,
 104 |     *,
 105 |     user_id: UUID,
 106 |     name: str,
 107 |     date_of_birth: date,
 108 | ) -> User | None:
 109 |     """Store the validated profile; onboarding completion is server-derived.
 110 | 
 111 |     ``name``/``date_of_birth`` arrive already validated by ``ProfileUpdateRequest``
 112 |     (non-blank name <= 150 chars, DOB not in the future); both are required,
 113 |     so a successful update always completes onboarding.  Nothing else on the
 114 |     row ( ``id``, ``appwrite_user_id``, ``email``) is client-settable.
 115 |     """
 116 |     user = session.get(User, user_id)
 117 |     if user is None:
 118 |         return None
 119 |     user.name = name
 120 |     user.date_of_birth = date_of_birth
 121 |     user.onboarding_completed = derive_onboarding_completed(name, date_of_birth)
 122 |     session.flush()
 123 |     return user
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L102 | Define `update_profile`; bind its arguments when called. The body executes only when invoked. |
| L103 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L104 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L105 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L106 | Declare parameter `name` with annotation `str`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. |
| L107 | Declare parameter `date_of_birth` with annotation `date`. Profile birth date validated against the current date before onboarding completion. |
| L108 | Finish/continue the signature; the declared return annotation is `User \| None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L109 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L111 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L112 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L113 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L114 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L115 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L116 | Evaluate the right-hand side, then bind/store it in `user`: `session.get(User, user_id)` — Look up the mapped object by primary key, using the session identity map when possible, otherwise SQL. |
| L117 | Evaluate the branch condition: compare whether `user` is the same object as `None`. If truthy, enter L118; otherwise skip this indented block and continue after it. |
| L118 | Compute the return value: None (no value). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L119 | Evaluate the right-hand side, then bind/store it in `user.name`: the current `name` value. |
| L120 | Evaluate the right-hand side, then bind/store it in `user.date_of_birth`: the current `date_of_birth` value. |
| L121 | Evaluate the right-hand side, then bind/store it in `user.onboarding_completed`: `derive_onboarding_completed(name, date_of_birth)` — Call [derive_onboarding_completed](../schemas/users.md#walk-derive-onboarding-completed) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L122 | `session.flush()` — Send pending ORM changes to SQL and check database constraints within the current transaction; no commit occurs. The return value is not assigned here. |
| L123 | Compute the return value: the current `user` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
