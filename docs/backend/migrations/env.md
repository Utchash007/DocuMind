# `migrations/env.py`

[Source](../../../Backend/migrations/env.py) · [Backend index](../README.md)

Alembic runtime environment. Adds `Backend/` to `sys.path` if needed, imports model declarations into `Base.metadata`, configures logging from Alembic's config file, and selects offline/online execution at module load. This module is intended to run inside Alembic's context, not as a general application import. It does not load the application `.env`.

## Functions

### `_environment_name() -> str`

- **Arguments:** None; reads `config.cmd_opts.x` supplied by Alembic.
- **Returns:** The first `environment=<value>` value, stripped/lowercased, or `"default"` when missing/blank.
- **Work:** Safely handles absent command options, partitions each `-x` entry at `=`, and checks the stripped key exactly. Other entries are ignored.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--environment-name"></a>

#### Line-by-line execution

[Current source: lines 41–52](../../../Backend/migrations/env.py#L41-L52). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  41 | def _environment_name() -> str:
  42 |     """Parse ``-x environment=<name>`` from the Alembic command line.
  43 | 
  44 |     Alembic delivers ``-x`` values as ``config.cmd_opts.x`` (a list of
  45 |     ``key=value`` strings); there is no ``Config.get_option`` API.
  46 |     """
  47 |     raw = getattr(getattr(config, "cmd_opts", None), "x", None) or []
  48 |     for item in raw:
  49 |         key, sep, value = str(item).partition("=")
  50 |         if sep and key.strip() == "environment":
  51 |             return value.strip().lower() or "default"
  52 |     return "default"
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L41 | Define `_environment_name`; bind its arguments when called. The body executes only when invoked. |
| L42 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L44 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L45 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L46 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L47 | Evaluate the right-hand side, then bind/store it in `raw`: evaluate `getattr(getattr(config, 'cmd_opts', None), 'x', None) or []` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L48 | Iterate `raw` (the current `raw` value), assigning each item to `item`. Execute the indented body once per item; an empty iterable skips it. |
| L49 | Evaluate the right-hand side, then bind/store it in `(key, sep, value)`: `str(item).partition('=')` — Split once at the separator and return the before/separator/after triple; first obtain the receiver: `str(item)` — Convert the input to its string representation. |
| L50 | Evaluate the branch condition: evaluate `sep and key.strip() == 'environment'` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L51; otherwise skip this indented block and continue after it. |
| L51 | Compute the return value: evaluate `value.strip().lower() or 'default'` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L52 | Compute the return value: `'default'`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_database_url() -> str`

- **Arguments:** None.
- **Returns:** Stripped shell `TEST_DATABASE_URL` if the environment name is `test`, otherwise `DATABASE_URL`.
- **Work:** Reads only the selected variable and raises `RuntimeError` if missing/empty. It does not call `validate_test_database_url` or compare targets in the current implementation; it only enforces presence and selection.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--database-url"></a>

#### Line-by-line execution

[Current source: lines 55–65](../../../Backend/migrations/env.py#L55-L65). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  55 | def _database_url() -> str:
  56 |     """Resolve the online URL, failing closed when it is not configured."""
  57 |     env_name = _environment_name()
  58 |     variable = "TEST_DATABASE_URL" if env_name == "test" else "DATABASE_URL"
  59 |     url = os.environ.get(variable, "").strip()
  60 |     if not url:
  61 |         raise RuntimeError(
  62 |             f"{variable} is required for Alembic environment {env_name!r} "
  63 |             "but is not set. Refusing to fall back to another database URL."
  64 |         )
  65 |     return url
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L55 | Define `_database_url`; bind its arguments when called. The body executes only when invoked. |
| L56 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L57 | Evaluate the right-hand side, then bind/store it in `env_name`: `_environment_name()` — Call [_environment_name](#walk--environment-name) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L58 | Evaluate the right-hand side, then bind/store it in `variable`: check `env_name == 'test'`; when true use `'TEST_DATABASE_URL'`, otherwise `'DATABASE_URL'` (only the selected branch is evaluated). |
| L59 | Evaluate the right-hand side, then bind/store it in `url`: `os.environ.get(variable, '').strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed; first obtain the receiver: `os.environ.get(variable, '')` — Read a process environment value without changing it, using the supplied fallback if absent. |
| L60 | Evaluate the branch condition: invert the truthiness of `url`. If truthy, enter L61; otherwise skip this indented block and continue after it. |
| L61 | Raise `RuntimeError(f'{variable} is required for Alembic environment {env_name!r} but is not set. Refusing to fall back to another database URL.')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L62 | Supply positional argument 1 to `RuntimeError`: format a string by inserting `variable`, `env_name` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L63 | Supply positional argument 1 to `RuntimeError`: format a string by inserting `variable`, `env_name` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L64 | Close the expression/container begun at L61; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L65 | Compute the return value: the current `url` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `run_migrations_offline() -> None`

- **Arguments:** None; operates on Alembic's global context.
- **Returns:** `None`; SQL is emitted through Alembic's output mechanism.
- **Work:** Configures a placeholder PostgreSQL/psycopg URL, target metadata, literal binds, and named parameter style. Opens the Alembic transaction context and calls `context.run_migrations()`. No database URL or connection is needed for this SQL-rendering mode.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-run-migrations-offline"></a>

#### Line-by-line execution

[Current source: lines 68–77](../../../Backend/migrations/env.py#L68-L77). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  68 | def run_migrations_offline() -> None:
  69 |     """Render migrations to SQL without a live database."""
  70 |     context.configure(
  71 |         url="postgresql+psycopg://placeholder:placeholder@localhost/placeholder",
  72 |         target_metadata=target_metadata,
  73 |         literal_binds=True,
  74 |         dialect_opts={"paramstyle": "named"},
  75 |     )
  76 |     with context.begin_transaction():
  77 |         context.run_migrations()
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L68 | Define `run_migrations_offline`; bind its arguments when called. The body executes only when invoked. |
| L69 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L70 | `context.configure` with the arguments detailed below — Configure Alembic's migration context with connection/URL, metadata, and comparison options. The return value is not assigned here. |
| L71 | Supply `url` = `'postgresql+psycopg://placeholder:placeholder@localhost/placeholder'`.  Evaluate the value as: `'postgresql+psycopg://placeholder:placeholder@localhost/placeholder'`. |
| L72 | Supply `target_metadata` = `target_metadata`.  Evaluate the value as: the current `target_metadata` value. |
| L73 | Supply `literal_binds` = `True`.  Evaluate the value as: `True`. |
| L74 | Supply `dialect_opts` = `{'paramstyle': 'named'}`.  Evaluate the value as: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. |
| L75 | Close the expression/container begun at L70; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L76 | Enter `context.begin_transaction()` — Enter Alembic's migration transaction context (or offline transaction output context). Context exits run in reverse order, including on return/exception. |
| L77 | `context.run_migrations()` — Run the revision operations through Alembic's configured migration context. The return value is not assigned here. |

<!-- END LINE WALKTHROUGH -->

### `run_migrations_online() -> None`

- **Arguments:** None; consumes Alembic configuration and the selected shell URL.
- **Returns:** `None` after migration execution.
- **Work:** Copies the configured SQLAlchemy section, injects `_database_url()`, builds an engine with `pool.NullPool`, connects, configures metadata/type comparison, and runs migrations inside a transaction context. Connection and transaction contexts close on exit; errors propagate. This is the path that executes DDL against the selected database.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-run-migrations-online"></a>

#### Line-by-line execution

[Current source: lines 80–96](../../../Backend/migrations/env.py#L80-L96). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  80 | def run_migrations_online() -> None:
  81 |     """Run migrations against the environment-selected database."""
  82 |     configuration = config.get_section(config.config_ini_section, {})
  83 |     configuration["sqlalchemy.url"] = _database_url()
  84 |     connectable = engine_from_config(
  85 |         configuration,
  86 |         prefix="sqlalchemy.",
  87 |         poolclass=pool.NullPool,
  88 |     )
  89 |     with connectable.connect() as connection:
  90 |         context.configure(
  91 |             connection=connection,
  92 |             target_metadata=target_metadata,
  93 |             compare_type=True,
  94 |         )
  95 |         with context.begin_transaction():
  96 |             context.run_migrations()
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L80 | Define `run_migrations_online`; bind its arguments when called. The body executes only when invoked. |
| L81 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L82 | Evaluate the right-hand side, then bind/store it in `configuration`: `config.get_section(config.config_ini_section, {})` — Invoke `config.get_section` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L83 | Evaluate the right-hand side, then bind/store it in `configuration['sqlalchemy.url']`: `_database_url()` — Call [_database_url](#walk--database-url) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L84 | Evaluate the right-hand side, then bind/store it in `connectable`: `engine_from_config(configuration, prefix='sqlalchemy.', poolclass=pool.NullPool)` — Invoke `engine_from_config` with the shown inputs and use its result; see the function overview for its role in this flow. |
| L85 | Supply positional argument 1 to `engine_from_config`: the current `configuration` value. |
| L86 | Supply `prefix` = `'sqlalchemy.'`.  Evaluate the value as: `'sqlalchemy.'`. |
| L87 | Supply `poolclass` = `pool.NullPool`.  Evaluate the value as: the `NullPool` attribute of `pool`. |
| L88 | Close the expression/container begun at L84; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L89 | Enter `connectable.connect()` — Invoke `connectable.connect` with the shown inputs and use its result; see the function overview for its role in this flow and bind its entered value to `connection`. Context exits run in reverse order, including on return/exception. |
| L90 | `context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)` — Configure Alembic's migration context with connection/URL, metadata, and comparison options. The return value is not assigned here. |
| L91 | Supply `connection` = `connection`.  Evaluate the value as: the current `connection` value. |
| L92 | Supply `target_metadata` = `target_metadata`.  Evaluate the value as: the current `target_metadata` value. |
| L93 | Supply `compare_type` = `True`.  Evaluate the value as: `True`. |
| L94 | Close the expression/container begun at L90; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L95 | Enter `context.begin_transaction()` — Enter Alembic's migration transaction context (or offline transaction output context). Context exits run in reverse order, including on return/exception. |
| L96 | `context.run_migrations()` — Run the revision operations through Alembic's configured migration context. The return value is not assigned here. |

<!-- END LINE WALKTHROUGH -->
