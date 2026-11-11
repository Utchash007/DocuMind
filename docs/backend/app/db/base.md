# `app/db/base.py`

[Source](../../../../Backend/app/db/base.py) · [Backend index](../../README.md)

Defines SQLAlchemy's shared declarative `Base` and column factories. `Base.metadata` uses `NAMING_CONVENTION` for primary keys, foreign keys, checks, unique constraints, and indexes. Concrete tables are declared in [models.md](models.md); importing these declarations does not open a database connection.

## Functions

### `utcnow() -> datetime`

- **Arguments:** None.
- **Returns:** The current timezone-aware UTC `datetime`.
- **Work:** Calls `datetime.now(timezone.utc)`. Used as a callable Python default so each inserted/updated row gets a fresh timestamp.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-utcnow"></a>

#### Line-by-line execution

[Current source: lines 18–24](../../../../Backend/app/db/base.py#L18-L24). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `datetime`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  18 | def utcnow() -> datetime:
  19 |     """Timezone-aware "now" used as the Python-side timestamp default.
  20 | 
  21 |     The database also applies ``now()`` as a server default, so rows
  22 |     inserted through raw SQL still receive timezone-aware timestamps.
  23 |     """
  24 |     return datetime.now(timezone.utc)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L18 | Define `utcnow`; bind its arguments when called. The body executes only when invoked. |
| L19 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L21 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L22 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L23 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L24 | Compute the return value: `datetime.now(timezone.utc)` — Read the current wall-clock date/time in the supplied timezone. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `uuid_pk() -> Mapped[UUID]`

- **Arguments:** None.
- **Returns:** A SQLAlchemy mapped-column declaration (annotated `Mapped[UUID]`).
- **Work:** Configures a native UUID primary key, Python `uuid4` default, and PostgreSQL `gen_random_uuid()` server default. This declares how a future insert obtains its ID; calling the factory does not insert a row or immediately allocate a UUID.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-uuid-pk"></a>

#### Line-by-line execution

[Current source: lines 46–53](../../../../Backend/app/db/base.py#L46-L53). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `Mapped[UUID]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  46 | def uuid_pk() -> Mapped[UUID]:
  47 |     """Application UUID primary key (Python default + PG server default)."""
  48 |     return mapped_column(
  49 |         Uuid,  # native UUID on PostgreSQL
  50 |         primary_key=True,
  51 |         default=uuid4,
  52 |         server_default=func.gen_random_uuid(),
  53 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L46 | Define `uuid_pk`; bind its arguments when called. The body executes only when invoked. |
| L47 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L48 | Compute the return value: `mapped_column(Uuid, primary_key=True, default=uuid4, server_default=func.gen_random_uuid())` — Declare a mapped SQLAlchemy column with the supplied type, default, nullability, and constraints. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L49 | Supply positional argument 1 to `mapped_column`: the current `Uuid` value. |
| L50 | Supply `primary_key` = `True`.  Evaluate the value as: `True`. |
| L51 | Supply `default` = `uuid4`. Fallback returned when the selected input is absent or cannot be parsed where explicitly handled. Evaluate the value as: the current `uuid4` value. |
| L52 | Supply `server_default` = `func.gen_random_uuid()`.  Evaluate the value as: `func.gen_random_uuid()` — Build the PostgreSQL UUID-generation expression used as a server default. |
| L53 | Close the expression/container begun at L48; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `created_at_col() -> Mapped[datetime]`

- **Arguments:** None.
- **Returns:** A nonnullable timezone-aware timestamp column declaration.
- **Work:** Supplies `utcnow` as the Python insert default and `now()` as the SQL server default, covering both ORM and raw-SQL inserts.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-created-at-col"></a>

#### Line-by-line execution

[Current source: lines 56–63](../../../../Backend/app/db/base.py#L56-L63). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `Mapped[datetime]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  56 | def created_at_col() -> Mapped[datetime]:
  57 |     """Timezone-aware creation timestamp with a ``now()`` server default."""
  58 |     return mapped_column(
  59 |         DateTime(timezone=True),
  60 |         nullable=False,
  61 |         default=utcnow,
  62 |         server_default=func.now(),
  63 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L56 | Define `created_at_col`; bind its arguments when called. The body executes only when invoked. |
| L57 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L58 | Compute the return value: `mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=func.now())` — Declare a mapped SQLAlchemy column with the supplied type, default, nullability, and constraints; inputs include `DateTime(timezone=True)` — Construct `DateTime` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L59 | `DateTime(timezone=True)` — Construct `DateTime` with the shown fields; its class/model initialization rules apply. |
| L60 | Supply `nullable` = `False`.  Evaluate the value as: `False`. |
| L61 | Supply `default` = `utcnow`. Fallback returned when the selected input is absent or cannot be parsed where explicitly handled. Evaluate the value as: the current `utcnow` value. |
| L62 | Supply `server_default` = `func.now()`.  Evaluate the value as: `func.now()` — Build a database-side current-timestamp expression. |
| L63 | Close the expression/container begun at L58; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `updated_at_col() -> Mapped[datetime]`

- **Arguments:** None.
- **Returns:** A nonnullable timezone-aware timestamp column declaration.
- **Work:** Uses the same insert defaults as `created_at_col` and adds ORM `onupdate=utcnow`. This is an ORM update hook, not a PostgreSQL trigger for arbitrary external updates.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-updated-at-col"></a>

#### Line-by-line execution

[Current source: lines 66–74](../../../../Backend/app/db/base.py#L66-L74). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `Mapped[datetime]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  66 | def updated_at_col() -> Mapped[datetime]:
  67 |     """Timezone-aware update timestamp, refreshed on every ORM update."""
  68 |     return mapped_column(
  69 |         DateTime(timezone=True),
  70 |         nullable=False,
  71 |         default=utcnow,
  72 |         server_default=func.now(),
  73 |         onupdate=utcnow,
  74 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L66 | Define `updated_at_col`; bind its arguments when called. The body executes only when invoked. |
| L67 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L68 | Compute the return value: `mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default=func.now(), onupdate=utcnow)` — Declare a mapped SQLAlchemy column with the supplied type, default, nullability, and constraints; inputs include `DateTime(timezone=True)` — Construct `DateTime` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L69 | `DateTime(timezone=True)` — Construct `DateTime` with the shown fields; its class/model initialization rules apply. |
| L70 | Supply `nullable` = `False`.  Evaluate the value as: `False`. |
| L71 | Supply `default` = `utcnow`. Fallback returned when the selected input is absent or cannot be parsed where explicitly handled. Evaluate the value as: the current `utcnow` value. |
| L72 | Supply `server_default` = `func.now()`.  Evaluate the value as: `func.now()` — Build a database-side current-timestamp expression. |
| L73 | Supply `onupdate` = `utcnow`.  Evaluate the value as: the current `utcnow` value. |
| L74 | Close the expression/container begun at L68; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->
