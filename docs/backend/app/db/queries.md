# `app/db/queries.py`

[Source](../../../../Backend/app/db/queries.py) · [Backend index](../../README.md)

Low-level owner-scoped SQL lookups. The caller supplies an open `Session` and the verified internal user UUID, and owns the transaction. Missing and inaccessible resources both return `None`.

## Functions

### `get_owned_project(session, *, user_id, project_id, include_deleted=False) -> Project | None`

- **Arguments:** SQLAlchemy session, internal owner UUID, project UUID, and an internal cleanup flag.
- **Returns:** The matching project or `None`.
- **Work:** Selects by project ID and `Project.user_id`. Unless `include_deleted`, also requires `deleted_at IS NULL`, then executes `session.scalar`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-owned-project"></a>

#### Line-by-line execution

[Current source: lines 22–36](../../../../Backend/app/db/queries.py#L22-L36). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `include_deleted` | `bool`; default `False`; keyword-only | Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |

**Declared result:** `Project | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  22 | def get_owned_project(
  23 |     session: Session,
  24 |     *,
  25 |     user_id: UUID,
  26 |     project_id: UUID,
  27 |     include_deleted: bool = False,
  28 | ) -> Project | None:
  29 |     """Return the project iff it exists and belongs to ``user_id``."""
  30 |     statement = select(Project).where(
  31 |         Project.id == project_id,
  32 |         Project.user_id == user_id,
  33 |     )
  34 |     if not include_deleted:
  35 |         statement = statement.where(Project.deleted_at.is_(None))
  36 |     return session.scalar(statement)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L22 | Define `get_owned_project`; bind its arguments when called. The body executes only when invoked. |
| L23 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L24 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L25 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L26 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L27 | Declare parameter `include_deleted` with annotation `bool`. Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |
| L28 | Finish/continue the signature; the declared return annotation is `Project \| None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L29 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L30 | Evaluate the right-hand side, then bind/store it in `statement`: `select(Project).where(Project.id == project_id, Project.user_id == user_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(Project)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L31 | Continue the enclosing expression: build a SQL predicate requiring `Project.id` equals `project_id`. |
| L32 | Continue the enclosing expression: build a SQL predicate requiring `Project.user_id` equals `user_id`. |
| L33 | Close the expression/container begun at L30; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L34 | Evaluate the branch condition: invert the truthiness of `include_deleted`. If truthy, enter L35; otherwise skip this indented block and continue after it. |
| L35 | Evaluate the right-hand side, then bind/store it in `statement`: `statement.where(Project.deleted_at.is_(None))` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; inputs include `Project.deleted_at.is_(None)` — Build an SQL IS predicate, commonly IS NULL for a live-row filter. |
| L36 | Compute the return value: `session.scalar(statement)` — Execute the SQL expression and return the first column of the first row, or None if no row exists. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `get_owned_document(session, *, user_id, project_id, document_id, include_deleted=False) -> Document | None`

- **Arguments:** Session; owner, project, and document UUIDs; optional tombstone visibility.
- **Returns:** The matching owned document or `None`.
- **Work:** Joins `Document` to `Project`, checks the document's exact project and the project's owner, and normally excludes both document and project tombstones. Supplying a valid document ID from another project cannot bypass the join.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-owned-document"></a>

#### Line-by-line execution

[Current source: lines 39–62](../../../../Backend/app/db/queries.py#L39-L62). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID`; required; keyword-only | Document UUID; filenames do not establish document identity. |
| `include_deleted` | `bool`; default `False`; keyword-only | Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |

**Declared result:** `Document | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  39 | def get_owned_document(
  40 |     session: Session,
  41 |     *,
  42 |     user_id: UUID,
  43 |     project_id: UUID,
  44 |     document_id: UUID,
  45 |     include_deleted: bool = False,
  46 | ) -> Document | None:
  47 |     """Return the document iff its project belongs to ``user_id``."""
  48 |     statement = (
  49 |         select(Document)
  50 |         .join(Project, Project.id == Document.project_id)
  51 |         .where(
  52 |             Document.id == document_id,
  53 |             Document.project_id == project_id,
  54 |             Project.user_id == user_id,
  55 |         )
  56 |     )
  57 |     if not include_deleted:
  58 |         statement = statement.where(
  59 |             Document.deleted_at.is_(None),
  60 |             Project.deleted_at.is_(None),
  61 |         )
  62 |     return session.scalar(statement)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L39 | Define `get_owned_document`; bind its arguments when called. The body executes only when invoked. |
| L40 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L41 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L42 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L43 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L44 | Declare parameter `document_id` with annotation `UUID`. Document UUID; filenames do not establish document identity. |
| L45 | Declare parameter `include_deleted` with annotation `bool`. Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |
| L46 | Finish/continue the signature; the declared return annotation is `Document \| None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L47 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L48 | Evaluate the right-hand side, then bind/store it in `statement`: `select(Document).join(Project, Project.id == Document.project_id).where` with the arguments detailed below — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(Document).join(Project, Project.id == Document.project_id)` — Add an inner SQL join using the supplied relationship/ON condition; first obtain the receiver: `select(Document)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L49 | `select(Document)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L50 | Add an inner SQL join using the supplied relationship/ON condition; apply this method to the result built by the preceding chain. |
| L51 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L52 | Continue the enclosing expression: build a SQL predicate requiring `Document.id` equals `document_id`. |
| L53 | Continue the enclosing expression: build a SQL predicate requiring `Document.project_id` equals `project_id`. |
| L54 | Continue the enclosing expression: build a SQL predicate requiring `Project.user_id` equals `user_id`. |
| L55 | Close the expression/container begun at L49; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L56 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L57 | Evaluate the branch condition: invert the truthiness of `include_deleted`. If truthy, enter L58; otherwise skip this indented block and continue after it. |
| L58 | Evaluate the right-hand side, then bind/store it in `statement`: `statement.where(Document.deleted_at.is_(None), Project.deleted_at.is_(None))` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; inputs include `Document.deleted_at.is_(None)` — Build an SQL IS predicate, commonly IS NULL for a live-row filter; `Project.deleted_at.is_(None)` — Build an SQL IS predicate, commonly IS NULL for a live-row filter. |
| L59 | `Document.deleted_at.is_(None)` — Build an SQL IS predicate, commonly IS NULL for a live-row filter. |
| L60 | `Project.deleted_at.is_(None)` — Build an SQL IS predicate, commonly IS NULL for a live-row filter. |
| L61 | Close the expression/container begun at L58; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L62 | Compute the return value: `session.scalar(statement)` — Execute the SQL expression and return the first column of the first row, or None if no row exists. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `get_owned_conversation(session, *, user_id, project_id, conversation_id, include_deleted=False) -> Conversation | None`

- **Arguments:** Session; owner, project, and conversation UUIDs; optional project-tombstone visibility.
- **Returns:** The matching conversation or `None`.
- **Work:** Joins through the project and checks all IDs plus the project owner. Normally hides a deleted project. Conversations themselves have no tombstone column.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-owned-conversation"></a>

#### Line-by-line execution

[Current source: lines 65–85](../../../../Backend/app/db/queries.py#L65-L85). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |
| `include_deleted` | `bool`; default `False`; keyword-only | Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |

**Declared result:** `Conversation | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  65 | def get_owned_conversation(
  66 |     session: Session,
  67 |     *,
  68 |     user_id: UUID,
  69 |     project_id: UUID,
  70 |     conversation_id: UUID,
  71 |     include_deleted: bool = False,
  72 | ) -> Conversation | None:
  73 |     """Return the conversation iff its project belongs to ``user_id``."""
  74 |     statement = (
  75 |         select(Conversation)
  76 |         .join(Project, Project.id == Conversation.project_id)
  77 |         .where(
  78 |             Conversation.id == conversation_id,
  79 |             Conversation.project_id == project_id,
  80 |             Project.user_id == user_id,
  81 |         )
  82 |     )
  83 |     if not include_deleted:
  84 |         statement = statement.where(Project.deleted_at.is_(None))
  85 |     return session.scalar(statement)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L65 | Define `get_owned_conversation`; bind its arguments when called. The body executes only when invoked. |
| L66 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L67 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L68 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L69 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L70 | Declare parameter `conversation_id` with annotation `UUID`. Conversation UUID identifying the owned chat and ordered message sequence. |
| L71 | Declare parameter `include_deleted` with annotation `bool`. Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. |
| L72 | Finish/continue the signature; the declared return annotation is `Conversation \| None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L73 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L74 | Evaluate the right-hand side, then bind/store it in `statement`: `select(Conversation).join(Project, Project.id == Conversation.project_id).where` with the arguments detailed below — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(Conversation).join(Project, Project.id == Conversation.project_id)` — Add an inner SQL join using the supplied relationship/ON condition; first obtain the receiver: `select(Conversation)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L75 | `select(Conversation)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L76 | Add an inner SQL join using the supplied relationship/ON condition; apply this method to the result built by the preceding chain. |
| L77 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L78 | Continue the enclosing expression: build a SQL predicate requiring `Conversation.id` equals `conversation_id`. |
| L79 | Continue the enclosing expression: build a SQL predicate requiring `Conversation.project_id` equals `project_id`. |
| L80 | Continue the enclosing expression: build a SQL predicate requiring `Project.user_id` equals `user_id`. |
| L81 | Close the expression/container begun at L75; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L82 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L83 | Evaluate the branch condition: invert the truthiness of `include_deleted`. If truthy, enter L84; otherwise skip this indented block and continue after it. |
| L84 | Evaluate the right-hand side, then bind/store it in `statement`: `statement.where(Project.deleted_at.is_(None))` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; inputs include `Project.deleted_at.is_(None)` — Build an SQL IS predicate, commonly IS NULL for a live-row filter. |
| L85 | Compute the return value: `session.scalar(statement)` — Execute the SQL expression and return the first column of the first row, or None if no row exists. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `get_owned_job(session, *, user_id, job_id) -> ProcessingJob | None`

- **Arguments:** Session, internal owner UUID, job UUID.
- **Returns:** The job whose immutable `owner_user_id` snapshot matches, or `None`.
- **Work:** Selects directly from `ProcessingJob`; it does not join live documents/projects. Cleanup status remains accessible to its owner after those resources are removed.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-owned-job"></a>

#### Line-by-line execution

[Current source: lines 88–104](../../../../Backend/app/db/queries.py#L88-L104). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `user_id` | `UUID`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |

**Declared result:** `ProcessingJob | None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  88 | def get_owned_job(
  89 |     session: Session,
  90 |     *,
  91 |     user_id: UUID,
  92 |     job_id: UUID,
  93 | ) -> ProcessingJob | None:
  94 |     """Return the job iff its immutable ``owner_user_id`` snapshot matches.
  95 | 
  96 |     Jobs are addressed by snapshot, not by a live join, so a job stays
  97 |     owner-scoped after its document/project rows are deleted.
  98 |     """
  99 |     return session.scalar(
 100 |         select(ProcessingJob).where(
 101 |             ProcessingJob.id == job_id,
 102 |             ProcessingJob.owner_user_id == user_id,
 103 |         )
 104 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L88 | Define `get_owned_job`; bind its arguments when called. The body executes only when invoked. |
| L89 | Declare parameter `session` with annotation `Session`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L90 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L91 | Declare parameter `user_id` with annotation `UUID`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L92 | Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. |
| L93 | Finish/continue the signature; the declared return annotation is `ProcessingJob \| None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L94 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L96 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L97 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L98 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L99 | Compute the return value: `session.scalar(select(ProcessingJob).where(ProcessingJob.id == job_id, ProcessingJob.owner_user_id == user_id))` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(ProcessingJob).where(ProcessingJob.id == job_id, ProcessingJob.owner_user_id == user_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L100 | `select(ProcessingJob)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L101 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.id` equals `job_id`. |
| L102 | Continue the enclosing expression: build a SQL predicate requiring `ProcessingJob.owner_user_id` equals `user_id`. |
| L103 | Close the expression/container begun at L100; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L104 | Close the expression/container begun at L99; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `next_message_position(session, *, conversation_id) -> int`

- **Arguments:** Session in an open transaction and conversation UUID.
- **Returns:** The current maximum message position plus one, starting at `1`.
- **Work:** Locks the conversation ID with `FOR UPDATE`, rejects a missing conversation with `LookupError`, and queries `coalesce(max(Message.position), 0)`. The lock serializes cooperating writers until transaction completion; the helper computes a number, it does not insert/reserve a message by itself. Callers perform ownership validation separately.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-next-message-position"></a>

#### Line-by-line execution

[Current source: lines 107–128](../../../../Backend/app/db/queries.py#L107-L128). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session` | `Session`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `conversation_id` | `UUID`; required; keyword-only | Conversation UUID identifying the owned chat and ordered message sequence. |

**Declared result:** `int`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 107 | def next_message_position(session: Session, *, conversation_id: UUID) -> int:
 108 |     """Allocate the next monotonic ``position`` inside a conversation.
 109 | 
 110 |     Must be called inside an open transaction.  The conversation row is
 111 |     locked with ``FOR UPDATE`` so concurrent writers serialize on it;
 112 |     combined with the unique ``(conversation_id, position)`` index this
 113 |     gives gap-checked, strictly increasing positions starting at 1.
 114 |     Raises :class:`LookupError` if the conversation does not exist.
 115 |     """
 116 |     locked = session.scalar(
 117 |         select(Conversation.id)
 118 |         .where(Conversation.id == conversation_id)
 119 |         .with_for_update()
 120 |     )
 121 |     if locked is None:
 122 |         raise LookupError(f"conversation not found: {conversation_id}")
 123 |     current_max = session.scalar(
 124 |         select(func.coalesce(func.max(Message.position), 0)).where(
 125 |             Message.conversation_id == conversation_id
 126 |         )
 127 |     )
 128 |     return int(current_max or 0) + 1
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L107 | Define `next_message_position`; bind its arguments when called. The body executes only when invoked. |
| L108 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L110 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L111 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L112 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L113 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L114 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L115 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L116 | Evaluate the right-hand side, then bind/store it in `locked`: `session.scalar(select(Conversation.id).where(Conversation.id == conversation_id).with_for_update())` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(Conversation.id).where(Conversation.id == conversation_id).with_for_update()` — Request row locks until transaction end; skip_locked=True avoids waiting on rows claimed elsewhere; first obtain the receiver: `select(Conversation.id).where(Conversation.id == conversation_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND. |
| L117 | `select(Conversation.id)` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L118 | Add SQL filtering predicates; multiple supplied predicates are combined with AND; apply this method to the result built by the preceding chain. |
| L119 | Request row locks until transaction end; skip_locked=True avoids waiting on rows claimed elsewhere; apply this method to the result built by the preceding chain. |
| L120 | Close the expression/container begun at L116; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L121 | Evaluate the branch condition: compare whether `locked` is the same object as `None`. If truthy, enter L122; otherwise skip this indented block and continue after it. |
| L122 | Raise `LookupError(f'conversation not found: {conversation_id}')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L123 | Evaluate the right-hand side, then bind/store it in `current_max`: `session.scalar(select(func.coalesce(func.max(Message.position), 0)).where(Message.conversation_id == conversation_id))` — Execute the SQL expression and return the first column of the first row, or None if no row exists; inputs include `select(func.coalesce(func.max(Message.position), 0)).where(Message.conversation_id == conversation_id)` — Add SQL filtering predicates; multiple supplied predicates are combined with AND; first obtain the receiver: `select(func.coalesce(func.max(Message.position), 0))` — Construct a SQL SELECT expression; building it does not execute SQL. |
| L124 | `select(func.coalesce(func.max(Message.position), 0))` — Construct a SQL SELECT expression; building it does not execute SQL; inputs include `func.coalesce(func.max(Message.position), 0)` — Build SQL COALESCE, selecting the first non-null expression at query execution. |
| L125 | Continue the enclosing expression: build a SQL predicate requiring `Message.conversation_id` equals `conversation_id`. |
| L126 | Close the expression/container begun at L124; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L127 | Close the expression/container begun at L123; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L128 | Compute the return value: add/concatenate `int(current_max or 0)` and `1`, following the parentheses/operator precedence shown in `int(current_max or 0) + 1`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
