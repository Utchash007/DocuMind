# `migrations/env.py`

[Source](../../../Backend/migrations/env.py) · [Backend index](../README.md)

Alembic runtime environment. Adds `Backend/` to `sys.path` if needed, imports model declarations into `Base.metadata`, configures logging from Alembic's config file, and selects offline/online execution at module load. Online URLs are normalized onto the installed psycopg 3 dialect with `normalize_postgres_url`, because managed providers such as Render hand out driverless `postgresql://` connection strings. This module is intended to run inside Alembic's context, not as a general application import. It does not load the application `.env`.

## Functions

### `_environment_name() -> str`

- **Arguments:** None; reads `config.cmd_opts.x` supplied by Alembic.
- **Returns:** The first `environment=<value>` value, stripped/lowercased, or `"default"` when missing/blank.
- **Work:** Safely handles absent command options, partitions each `-x` entry at `=`, and checks the stripped key exactly. Other entries are ignored.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--environment-name"></a>

#### Line-by-line execution

[Current source: lines 42–53](../../../Backend/migrations/env.py#L42-L53). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  42 | def _environment_name() -> str:
  43 |     """Parse ``-x environment=<name>`` from the Alembic command line.
  44 | 
  45 |     Alembic delivers ``-x`` values as ``config.cmd_opts.x`` (a list of
  46 |     ``key=value`` strings); there is no ``Config.get_option`` API.
  47 |     """
  48 |     raw = getattr(getattr(config, "cmd_opts", None), "x", None) or []
  49 |     for item in raw:
  50 |         key, sep, value = str(item).partition("=")
  51 |         if sep and key.strip() == "environment":
  52 |             return value.strip().lower() or "default"
  53 |     return "default"
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L42 | Define `_environment_name`; bind its arguments when called. The body executes only when invoked. |
| L43 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L45 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L46 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L47 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L48 | Evaluate the right-hand side, then bind/store it in `raw`: evaluate `getattr(getattr(config, 'cmd_opts', None), 'x', None) or []` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L49 | Iterate `raw` (the current `raw` value), assigning each item to `item`. Execute the indented body once per item; an empty iterable skips it. |
| L50 | Evaluate the right-hand side, then bind/store it in `(key, sep, value)`: `str(item).partition('=')` — Split once at the separator and return the before/separator/after triple; first obtain the receiver: `str(item)` — Convert the input to its string representation. |
| L51 | Evaluate the branch condition: evaluate `sep and key.strip() == 'environment'` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L52; otherwise skip this indented block and continue after it. |
| L52 | Compute the return value: evaluate `value.strip().lower() or 'default'` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L53 | Compute the return value: `'default'`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_database_url() -> str`

- **Arguments:** None.
- **Returns:** The selected shell URL (stripped), with a driverless `postgresql://`/`postgres://` scheme normalized onto `postgresql+psycopg://`.
- **Work:** Reads only the selected variable and raises `RuntimeError` if missing/empty. It does not call `validate_test_database_url` or compare targets in the current implementation; it only enforces presence and selection, then delegates scheme normalization to `normalize_postgres_url`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--database-url"></a>

#### Line-by-line execution

[Current source: lines 56–66](../../../Backend/migrations/env.py#L56-L66). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  56 | def _database_url() -> str:
  57 |     """Resolve the online URL, failing closed; driverless PostgreSQL URLs are normalized onto psycopg 3."""
  58 |     env_name = _environment_name()
  59 |     variable = "TEST_DATABASE_URL" if env_name == "test" else "DATABASE_URL"
  60 |     url = os.environ.get(variable, "").strip()
  61 |     if not url:
  62 |         raise RuntimeError(
  63 |             f"{variable} is required for Alembic environment {env_name!r} "
  64 |             "but is not set. Refusing to fall back to another database URL."
  65 |         )
  66 |     return normalize_postgres_url(url)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L56 | Define `_database_url`; bind its arguments when called. The body executes only when invoked. |
| L57 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L58 | Evaluate the right-hand side, then bind/store it in `env_name`: `_environment_name()` — Call [_environment_name](#walk--environment-name) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L59 | Evaluate the right-hand side, then bind/store it in `variable`: check `env_name == 'test'`; when true use `'TEST_DATABASE_URL'`, otherwise `'DATABASE_URL'` (only the selected branch is evaluated). |
| L60 | Evaluate the right-hand side, then bind/store it in `url`: `os.environ.get(variable, '').strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed; first obtain the receiver: `os.environ.get(variable, '')` — Read a process environment value without changing it, using the supplied fallback if absent. |
| L61 | Evaluate the branch condition: invert the truthiness of `url`. If truthy, enter L62; otherwise skip this indented block and continue after it. |
| L62 | Raise `RuntimeError(f'{variable} is required for Alembic environment {env_name!r} but is not set. Refusing to fall back to another database URL.')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L63 | Supply positional argument 1 to `RuntimeError`: format a string by inserting `variable`, `env_name` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L64 | Supply positional argument 1 to `RuntimeError`: format a string by inserting `variable`, `env_name` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L65 | Close the expression/container begun at L62; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L66 | Compute the return value: `normalize_postgres_url(url)` — Call [normalize_postgres_url](../app/db/session.md#walk-normalize-postgres-url) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `run_migrations_offline() -> None`

- **Arguments:** None; operates on Alembic's global context.
- **Returns:** `None`; SQL is emitted through Alembic's output mechanism.
- **Work:** Configures a placeholder PostgreSQL/psycopg URL, target metadata, literal binds, and named parameter style. Opens the Alembic transaction context and calls `context.run_migrations()`. No database URL or connection is needed for this SQL-rendering mode.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-run-migrations-offline"></a>

#### Line-by-line execution

[Current source: lines 69–78](../../../Backend/migrations/env.py#L69-L78). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  69 | def run_migrations_offline() -> None:
  70 |     """Render migrations to SQL without a live database."""
  71 |     context.configure(
  72 |         url="postgresql+psycopg://placeholder:placeholder@localhost/placeholder",
  73 |         target_metadata=target_metadata,
  74 |         literal_binds=True,
  75 |         dialect_opts={"paramstyle": "named"},
  76 |     )
  77 |     with context.begin_transaction():
  78 |         context.run_migrations()
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L69 | Define `run_migrations_offline`; bind its arguments when called. The body executes only when invoked. |
| L70 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L71 | `context.configure` with the arguments detailed below — Configure Alembic's migration context with connection/URL, metadata, and comparison options. The return value is not assigned here. |
| L72 | Supply `url` = `'postgresql+psycopg://placeholder:placeholder@localhost/placeholder'`.  Evaluate the value as: `'postgresql+psycopg://placeholder:placeholder@localhost/placeholder'`. |
| L73 | Supply `target_metadata` = `target_metadata`.  Evaluate the value as: the current `target_metadata` value. |
| L74 | Supply `literal_binds` = `True`.  Evaluate the value as: `True`. |
| L75 | Supply `dialect_opts` = `{'paramstyle': 'named'}`.  Evaluate the value as: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. |
| L76 | Close the expression/container begun at L71; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L77 | Enter `context.begin_transaction()` — Enter Alembic's migration transaction context (or offline transaction output context). Context exits run in reverse order, including on return/exception. |
| L78 | `context.run_migrations()` — Run the revision operations through Alembic's configured migration context. The return value is not assigned here. |

<!-- END LINE WALKTHROUGH -->

### `run_migrations_online() -> None`

- **Arguments:** None; consumes Alembic configuration and the selected shell URL.
- **Returns:** `None` after migration execution.
- **Work:** Copies the configured SQLAlchemy section, injects `_database_url()`, builds an engine with `pool.NullPool`, connects, configures metadata/type comparison, and runs migrations inside a transaction context. Connection and transaction contexts close on exit; errors propagate. This is the path that executes DDL against the selected database.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-run-migrations-online"></a>

#### Line-by-line execution

[Current source: lines 81–97](../../../Backend/migrations/env.py#L81-L97). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  81 | def run_migrations_online() -> None:
  82 |     """Run migrations against the environment-selected database."""
  83 |     configuration = config.get_section(config.config_ini_section, {})
  84 |     configuration["sqlalchemy.url"] = _database_url()
  85 |     connectable = engine_from_config(
  86 |         configuration,
  87 |         prefix="sqlalchemy.",
  88 |         poolclass=pool.NullPool,
  89 |     )
  90 |     with connectable.connect() as connection:
  91 |         context.configure(
  92 |             connection=connection,
  93 |             target_metadata=target_metadata,
  94 |             compare_type=True,
  95 |         )
  96 |         with context.begin_transaction():
  97 |             context.run_migrations()
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L81 | Define `run_migrations_online`; bind its arguments when called. The body executes only when invoked. |
| L82 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L83 | Evaluate the right-hand side, then bind/store it in `configuration`: `config.get_section(config.config_ini_section, {})` — Invoke `config.get_section` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L84 | Evaluate the right-hand side, then bind/store it in `configuration['sqlalchemy.url']`: `_database_url()` — Call [_database_url](#walk--database-url) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L85 | Evaluate the right-hand side, then bind/store it in `connectable`: `engine_from_config(configuration, prefix='sqlalchemy.', poolclass=pool.NullPool)` — Invoke `engine_from_config` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L86 | Supply positional argument 1 to `engine_from_config`: the current `configuration` value. |
| L87 | Supply `prefix` = `'sqlalchemy.'`.  Evaluate the value as: `'sqlalchemy.'`. |
| L88 | Supply `poolclass` = `pool.NullPool`.  Evaluate the value as: the `NullPool` attribute of `pool`. |
| L89 | Close the expression/container begun at L85; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L90 | Enter `connectable.connect()` — Invoke `connectable.connect` with the shown inputs and use its result; see the function overview for its role in this flow and bind its entered value to `connection`. Context exits run in reverse order, including on return/exception. |
| L91 | `context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)` — Configure Alembic's migration context with connection/URL, metadata, and comparison options. The return value is not assigned here. |
| L92 | Supply `connection` = `connection`.  Evaluate the value as: the current `connection` value. |
| L93 | Supply `target_metadata` = `target_metadata`.  Evaluate the value as: the current `target_metadata` value. |
| L94 | Supply `compare_type` = `True`.  Evaluate the value as: `True`. |
| L95 | Close the expression/container begun at L91; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L96 | Enter `context.begin_transaction()` — Enter Alembic's migration transaction context (or offline transaction output context). Context exits run in reverse order, including on return/exception. |
| L97 | `context.run_migrations()` — Run the revision operations through Alembic's configured migration context. The return value is not assigned here. |

<!-- END LINE WALKTHROUGH -->
