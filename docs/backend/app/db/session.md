# `app/db/session.py`

[Source](../../../../Backend/app/db/session.py) · [Backend index](../../README.md)

Builds synchronous SQLAlchemy engines/sessions lazily and provides short transaction boundaries. `_FACTORY_CACHE` is keyed **only by URL**. `ENV_DEFAULT` is `"default"`; `ENV_TEST` is `"test"`. `DbSessionDep` is `Annotated[Session, Depends(get_db)]`.

## Functions

### `validate_test_database_url(url: str, application_url: str | None = None) -> str`

- **Arguments:** `url`, an explicitly supplied database target; optional `application_url`, the application target to exclude.
- **Returns:** The original `url` unchanged after validation.
- **Work:** Parses with `make_url`; requires the `postgresql` backend and a database name containing a delimited `test` or `tests` segment (case-insensitive). Rejects query keys `host`, `hostaddr`, `port`, `dbname`, and `service`, then compares normalized host/port/database with the application target when supplied.
- **Errors:** Wraps URL parsing/type/validation errors in `RuntimeError`. It never creates an engine, connects, or establishes that a database is actually disposable.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-validate-test-database-url"></a>

#### Line-by-line execution

[Current source: lines 43–63](../../../../Backend/app/db/session.py#L43-L63). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `url` | `str`; required; positional or keyword | Caller-supplied url; each read, transformation, and validation is traced below. |
| `application_url` | `str \| None`; default `None`; positional or keyword | Application connection target used only for comparison by the pure target guard. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  43 | def validate_test_database_url(url: str, application_url: str | None = None) -> str:
  44 |     """Validate an explicitly supplied, disposable PostgreSQL test target.
  45 | 
  46 |     Pure configuration check: never creates an engine or opens a connection.
  47 |     """
  48 |     try:
  49 |         target = make_url(url)
  50 |         if target.get_backend_name() != "postgresql" or not re.search(r"(^|[_-])tests?([_-]|$)", target.database or "", re.IGNORECASE):
  51 |             raise ValueError("not a clearly named PostgreSQL test database")
  52 |         # Connection target overrides can defeat host/database comparison.
  53 |         if any(key in target.query for key in ("host", "hostaddr", "port", "dbname", "service")):
  54 |             raise ValueError("connection target overrides are not allowed")
  55 |         if application_url:
  56 |             application = make_url(application_url)
  57 |             def identity(value):
  58 |                 return ((value.host or "").lower(), value.port or 5432, value.database)
  59 |             if identity(target) == identity(application):
  60 |                 raise ValueError("same database as the application")
  61 |     except (ArgumentError, ValueError, TypeError) as exc:
  62 |         raise RuntimeError("TEST_DATABASE_URL must target a separate, clearly test-named PostgreSQL database.") from exc
  63 |     return url
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L43 | Define `validate_test_database_url`; bind its arguments when called. The body executes only when invoked. |
| L44 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L46 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L47 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L48 | Enter the protected block; failures are matched against `(ArgumentError, ValueError, TypeError)` in order. |
| L49 | Evaluate the right-hand side, then bind/store it in `target`: `make_url(url)` — Parse the URL into SQLAlchemy connection components without connecting. |
| L50 | Evaluate the branch condition: evaluate `target.get_backend_name() != 'postgresql' or not re.search('(^\|[_-])tests?([_-]\|$)', target.database or '', re.IGNORECASE)` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L51; otherwise skip this indented block and continue after it. |
| L51 | Raise `ValueError('not a clearly named PostgreSQL test database')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L52 | Comment only: Connection target overrides can defeat host/database comparison.. It does not execute; the neighboring code determines behavior. |
| L53 | Evaluate the branch condition: `any((key in target.query for key in ('host', 'hostaddr', 'port', 'dbname', 'service')))` — Evaluate the iterable lazily, stopping at the first truthy item (True); empty input gives False; inputs include iterate `('host', 'hostaddr', 'port', 'dbname', 'service')`, binding each item to `key`; produce `key in target.query` into a lazy generator (items computed when consumed). If truthy, enter L54; otherwise skip this indented block and continue after it. |
| L54 | Raise `ValueError('connection target overrides are not allowed')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L55 | Evaluate the branch condition: the current `application_url` value. If truthy, enter L56; otherwise skip this indented block and continue after it. |
| L56 | Evaluate the right-hand side, then bind/store it in `application`: `make_url(application_url)` — Parse the URL into SQLAlchemy connection components without connecting. |
| L57 | Define the local closure [validate_test_database_url.identity](#walk-validate-test-database-url-identity); it can capture enclosing locals. Definition does not execute its body. |
| L58 | Compute the return value: build a tuple containing `(value.host or '').lower()`, `value.port or 5432`, `value.database`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L59 | Evaluate the branch condition: compare whether `identity(target)` equals `identity(application)`. If truthy, enter L60; otherwise skip this indented block and continue after it. |
| L60 | Raise `ValueError('same database as the application')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L61 | Handle `(ArgumentError, ValueError, TypeError)` and bind it to `exc`; only a matching error from the associated try enters this body. |
| L62 | Raise `RuntimeError('TEST_DATABASE_URL must target a separate, clearly test-named PostgreSQL database.')`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `exc` as its cause. |
| L63 | Compute the return value: the current `url` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `validate_test_database_url.identity(value)` (nested helper)

- **Arguments:** `value`, a parsed SQLAlchemy URL.
- **Returns:** `(lowercase_host_or_empty, port_or_5432, database)`.
- **Work:** Normalizes just the connection identity used by the enclosing function. Credentials and driver spelling are deliberately excluded; there is no DNS resolution.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-validate-test-database-url-identity"></a>

#### Line-by-line execution

[Current source: lines 57–58](../../../../Backend/app/db/session.py#L57-L58). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `value` | not annotated; required; positional or keyword | Input value being normalized, validated, or compared by this helper. |

**Declared result:** No return annotation; follow the return/yield lines below. Python supplies None when a non-generator reaches the end without return.

**Numbered source**

```text
  57 |             def identity(value):
  58 |                 return ((value.host or "").lower(), value.port or 5432, value.database)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L57 | Define `validate_test_database_url.identity`; bind its arguments when called. The body executes only when invoked. |
| L58 | Compute the return value: build a tuple containing `(value.host or '').lower()`, `value.port or 5432`, `value.database`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `get_database_url(environment: str | None = None) -> str`

- **Arguments:** Optional environment label, normalized with `strip().lower()`; a falsey label selects `default`.
- **Returns:** The stripped `TEST_DATABASE_URL` for `test`, otherwise the stripped `DATABASE_URL`.
- **Work:** Resolves the one selected variable, rejects missing/empty values, and calls `validate_test_database_url` for the test label, supplying the application URL if available.
- **Errors:** `RuntimeError` for absent settings or rejected test targets. There is no fallback between database variables.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-database-url"></a>

#### Line-by-line execution

[Current source: lines 66–83](../../../../Backend/app/db/session.py#L66-L83). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `environment` | `str \| None`; default `None`; positional or keyword | Configuration selector; only normalized test mode selects TEST_DATABASE_URL. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  66 | def get_database_url(environment: str | None = None) -> str:
  67 |     """Return the database URL for ``environment`` from the environment.
  68 | 
  69 |     ``environment="test"`` requires ``TEST_DATABASE_URL``; every other
  70 |     value (including ``None``) requires ``DATABASE_URL``.  Missing or
  71 |     empty variables raise :class:`RuntimeError` instead of falling back.
  72 |     """
  73 |     env = (environment or ENV_DEFAULT).strip().lower()
  74 |     variable = "TEST_DATABASE_URL" if env == ENV_TEST else "DATABASE_URL"
  75 |     url = os.environ.get(variable, "").strip()
  76 |     if not url:
  77 |         raise RuntimeError(
  78 |             f"{variable} is required (environment={env!r}) but is not set. "
  79 |             "Refusing to fall back to another database URL."
  80 |         )
  81 |     if env == ENV_TEST:
  82 |         return validate_test_database_url(url, os.environ.get("DATABASE_URL", "").strip() or None)
  83 |     return url
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L66 | Define `get_database_url`; bind its arguments when called. The body executes only when invoked. |
| L67 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L69 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L70 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L71 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L72 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L73 | Evaluate the right-hand side, then bind/store it in `env`: `(environment or ENV_DEFAULT).strip().lower()` — Return a lowercased string copy; first obtain the receiver: `(environment or ENV_DEFAULT).strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed. |
| L74 | Evaluate the right-hand side, then bind/store it in `variable`: check `env == ENV_TEST`; when true use `'TEST_DATABASE_URL'`, otherwise `'DATABASE_URL'` (only the selected branch is evaluated). |
| L75 | Evaluate the right-hand side, then bind/store it in `url`: `os.environ.get(variable, '').strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed; first obtain the receiver: `os.environ.get(variable, '')` — Read a process environment value without changing it, using the supplied fallback if absent. |
| L76 | Evaluate the branch condition: invert the truthiness of `url`. If truthy, enter L77; otherwise skip this indented block and continue after it. |
| L77 | Raise `RuntimeError(f'{variable} is required (environment={env!r}) but is not set. Refusing to fall back to another database URL.')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L78 | Supply positional argument 1 to `RuntimeError`: format a string by inserting `variable`, `env` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L79 | Supply positional argument 1 to `RuntimeError`: format a string by inserting `variable`, `env` into the literal text; !r uses repr, and this formatting does not escape or redact values. |
| L80 | Close the expression/container begun at L77; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L81 | Evaluate the branch condition: compare whether `env` equals `ENV_TEST`. If truthy, enter L82; otherwise skip this indented block and continue after it. |
| L82 | Compute the return value: `validate_test_database_url(url, os.environ.get('DATABASE_URL', '').strip() or None)` — Call [validate_test_database_url](#walk-validate-test-database-url) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L83 | Compute the return value: the current `url` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `make_engine(database_url: str | None = None, *, environment: str | None = None) -> Engine`

- **Arguments:** Optional explicit URL; otherwise `environment` chooses the environment variable.
- **Returns:** A new synchronous SQLAlchemy engine.
- **Work:** Calls `create_engine` with `pool_pre_ping=True` and `future=True`. Pool connections are acquired when used. An explicitly supplied URL bypasses environment lookup and its target validation.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-make-engine"></a>

#### Line-by-line execution

[Current source: lines 86–93](../../../../Backend/app/db/session.py#L86-L93). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `database_url` | `str \| None`; default `None`; positional or keyword | Explicit SQLAlchemy connection URL, or null for environment resolution. |
| `environment` | `str \| None`; default `None`; keyword-only | Configuration selector; only normalized test mode selects TEST_DATABASE_URL. |

**Declared result:** `Engine`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  86 | def make_engine(database_url: str | None = None, *, environment: str | None = None) -> Engine:
  87 |     """Create a synchronous SQLAlchemy engine for PostgreSQL (psycopg)."""
  88 |     url = database_url or get_database_url(environment)
  89 |     return create_engine(
  90 |         url,
  91 |         pool_pre_ping=True,  # tolerate idle/balancer-dropped connections
  92 |         future=True,
  93 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L86 | Define `make_engine`; bind its arguments when called. The body executes only when invoked. |
| L87 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L88 | Evaluate the right-hand side, then bind/store it in `url`: evaluate `database_url or get_database_url(environment)` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L89 | Compute the return value: `create_engine(url, pool_pre_ping=True, future=True)` — Construct a synchronous SQLAlchemy engine/pool; ordinary connection checkout happens later. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L90 | Supply positional argument 1 to `create_engine`: the current `url` value. |
| L91 | Supply `pool_pre_ping` = `True`.  Evaluate the value as: `True`. |
| L92 | Supply `future` = `True`.  Evaluate the value as: `True`. |
| L93 | Close the expression/container begun at L89; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `make_session_factory(database_url: str | None = None, *, environment: str | None = None, expire_on_commit: bool = False) -> sessionmaker[Session]`

- **Arguments:** URL/environment selection as above; `expire_on_commit` controls ORM attribute expiration for a newly created factory.
- **Returns:** The cached factory for the resolved URL, or a newly cached one.
- **Work:** Checks `_FACTORY_CACHE`; on a miss creates an engine and a `sessionmaker` with `autoflush=False`, `autocommit=False`, `future=True`, and the requested expiration policy. Because the cache key is URL-only, the first caller's expiration policy wins for that URL.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-make-session-factory"></a>

#### Line-by-line execution

[Current source: lines 96–123](../../../../Backend/app/db/session.py#L96-L123). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `database_url` | `str \| None`; default `None`; positional or keyword | Explicit SQLAlchemy connection URL, or null for environment resolution. |
| `environment` | `str \| None`; default `None`; keyword-only | Configuration selector; only normalized test mode selects TEST_DATABASE_URL. |
| `expire_on_commit` | `bool`; default `False`; keyword-only | Caller-supplied expire on commit; each read, transformation, and validation is traced below. |

**Declared result:** `sessionmaker[Session]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  96 | def make_session_factory(
  97 |     database_url: str | None = None,
  98 |     *,
  99 |     environment: str | None = None,
 100 |     expire_on_commit: bool = False,
 101 | ) -> sessionmaker[Session]:
 102 |     """Return a cached ``sessionmaker`` for the resolved database URL.
 103 | 
 104 |     ``expire_on_commit=False`` (default) keeps attribute access safe after
 105 |     the transaction commits, which is how the request handlers in this
 106 |     codebase serialize DTOs.  Note the cache key includes the URL only:
 107 |     the first caller's ``expire_on_commit`` wins for a given URL, so use
 108 |     :func:`make_worker_session_factory` explicitly for worker code that
 109 |     needs detached instances.
 110 |     """
 111 |     url = database_url or get_database_url(environment)
 112 |     cached = _FACTORY_CACHE.get(url)
 113 |     if cached is not None:
 114 |         return cached
 115 |     factory: sessionmaker[Session] = sessionmaker(
 116 |         bind=make_engine(url),
 117 |         autoflush=False,
 118 |         autocommit=False,
 119 |         expire_on_commit=expire_on_commit,
 120 |         future=True,
 121 |     )
 122 |     _FACTORY_CACHE[url] = factory
 123 |     return factory
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L96 | Define `make_session_factory`; bind its arguments when called. The body executes only when invoked. |
| L97 | Declare parameter `database_url` with annotation `str \| None`. Explicit SQLAlchemy connection URL, or null for environment resolution. |
| L98 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L99 | Declare parameter `environment` with annotation `str \| None`. Configuration selector; only normalized test mode selects TEST_DATABASE_URL. |
| L100 | Declare parameter `expire_on_commit` with annotation `bool`. Caller-supplied expire on commit; its uses and transformations are traced below. |
| L101 | Finish/continue the signature; the declared return annotation is `sessionmaker[Session]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L102 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L104 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L105 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L106 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L107 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L108 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L109 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L110 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L111 | Evaluate the right-hand side, then bind/store it in `url`: evaluate `database_url or get_database_url(environment)` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L112 | Evaluate the right-hand side, then bind/store it in `cached`: `_FACTORY_CACHE.get(url)` — Look up `url` in `_FACTORY_CACHE`, using None when the key is absent (an existing null value is not replaced). |
| L113 | Evaluate the branch condition: compare whether `cached` is not the same object as `None`. If truthy, enter L114; otherwise skip this indented block and continue after it. |
| L114 | Compute the return value: the current `cached` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L115 | Evaluate the right-hand side, then bind/store it in `factory`: `sessionmaker(bind=make_engine(url), autoflush=False, autocommit=False, expire_on_commit=expire_on_commit, future=True)` — Build a callable session factory with the supplied engine and session settings. |
| L116 | Supply `bind` = `make_engine(url)`.  Evaluate the value as: `make_engine(url)` — Call [make_engine](#walk-make-engine) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L117 | Supply `autoflush` = `False`.  Evaluate the value as: `False`. |
| L118 | Supply `autocommit` = `False`.  Evaluate the value as: `False`. |
| L119 | Supply `expire_on_commit` = `expire_on_commit`.  Evaluate the value as: the current `expire_on_commit` value. |
| L120 | Supply `future` = `True`.  Evaluate the value as: `True`. |
| L121 | Close the expression/container begun at L115; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L122 | Evaluate the right-hand side, then bind/store it in `_FACTORY_CACHE[url]`: the current `factory` value. |
| L123 | Compute the return value: the current `factory` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `get_session_factory(environment: str | None = None) -> sessionmaker[Session]`

- **Arguments:** Optional environment label.
- **Returns:** `make_session_factory(environment=environment)`.
- **Work:** Provides the lazy request-side dependency entry point; it does not itself create a session or execute SQL.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-session-factory"></a>

#### Line-by-line execution

[Current source: lines 126–128](../../../../Backend/app/db/session.py#L126-L128). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `environment` | `str \| None`; default `None`; positional or keyword | Configuration selector; only normalized test mode selects TEST_DATABASE_URL. |

**Declared result:** `sessionmaker[Session]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 126 | def get_session_factory(environment: str | None = None) -> sessionmaker[Session]:
 127 |     """Lazily resolve the request-scoped session factory from the env."""
 128 |     return make_session_factory(environment=environment)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L126 | Define `get_session_factory`; bind its arguments when called. The body executes only when invoked. |
| L127 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L128 | Compute the return value: `make_session_factory(environment=environment)` — Call [make_session_factory](#walk-make-session-factory) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `make_worker_session_factory(database_url: str | None = None, *, environment: str | None = None) -> sessionmaker[Session]`

- **Arguments:** Optional explicit URL and environment selector.
- **Returns:** A new, uncached session factory with its own engine.
- **Work:** Resolves the URL and disables autoflush, autocommit, and expiration on commit. Keeping a separate engine lets a worker manage its own pool lifecycle independently of request factories.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-make-worker-session-factory"></a>

#### Line-by-line execution

[Current source: lines 131–150](../../../../Backend/app/db/session.py#L131-L150). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `database_url` | `str \| None`; default `None`; positional or keyword | Explicit SQLAlchemy connection URL, or null for environment resolution. |
| `environment` | `str \| None`; default `None`; keyword-only | Configuration selector; only normalized test mode selects TEST_DATABASE_URL. |

**Declared result:** `sessionmaker[Session]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 131 | def make_worker_session_factory(
 132 |     database_url: str | None = None,
 133 |     *,
 134 |     environment: str | None = None,
 135 | ) -> sessionmaker[Session]:
 136 |     """Session factory for the PDF worker (separate, uncached-by-default).
 137 | 
 138 |     Workers must not share the request factory's engine lifecycle: the
 139 |     worker process outlives requests and claims jobs in many short
 140 |     transactions.  Each call builds a fresh factory bound to its own
 141 |     engine; the worker entry point owns and disposes it.
 142 |     """
 143 |     url = database_url or get_database_url(environment)
 144 |     return sessionmaker(
 145 |         bind=make_engine(url),
 146 |         autoflush=False,
 147 |         autocommit=False,
 148 |         expire_on_commit=False,
 149 |         future=True,
 150 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L131 | Define `make_worker_session_factory`; bind its arguments when called. The body executes only when invoked. |
| L132 | Declare parameter `database_url` with annotation `str \| None`. Explicit SQLAlchemy connection URL, or null for environment resolution. |
| L133 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L134 | Declare parameter `environment` with annotation `str \| None`. Configuration selector; only normalized test mode selects TEST_DATABASE_URL. |
| L135 | Finish/continue the signature; the declared return annotation is `sessionmaker[Session]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L136 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L138 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L139 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L140 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L141 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L142 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L143 | Evaluate the right-hand side, then bind/store it in `url`: evaluate `database_url or get_database_url(environment)` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L144 | Compute the return value: `sessionmaker(bind=make_engine(url), autoflush=False, autocommit=False, expire_on_commit=False, future=True)` — Build a callable session factory with the supplied engine and session settings. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L145 | Supply `bind` = `make_engine(url)`.  Evaluate the value as: `make_engine(url)` — Call [make_engine](#walk-make-engine) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L146 | Supply `autoflush` = `False`.  Evaluate the value as: `False`. |
| L147 | Supply `autocommit` = `False`.  Evaluate the value as: `False`. |
| L148 | Supply `expire_on_commit` = `False`.  Evaluate the value as: `False`. |
| L149 | Supply `future` = `True`.  Evaluate the value as: `True`. |
| L150 | Close the expression/container begun at L144; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `request_transaction(session_factory: sessionmaker[Session] | None = None) -> Iterator[Session]`

- **Arguments:** Optional factory; defaults to `get_session_factory()`.
- **Returns/yields:** As a `@contextmanager`, returns a context manager that yields one session to its `with` block.
- **Work:** Opens a session and `session.begin()`, yields control, commits on successful block exit, and rolls back on an exception via SQLAlchemy's context manager. Exceptions propagate and the outer context closes the session. Provider calls belong outside the block.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-request-transaction"></a>

#### Line-by-line execution

[Current source: lines 153–173](../../../../Backend/app/db/session.py#L153-L173). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session_factory` | `sessionmaker[Session] \| None`; default `None`; positional or keyword | Callable that creates database sessions; a null value selects the function's configured default. |

**Declared result:** `Iterator[Session]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 153 | @contextmanager
 154 | def request_transaction(
 155 |     session_factory: sessionmaker[Session] | None = None,
 156 | ) -> Iterator[Session]:
 157 |     """Run a short unit of work: commit on success, rollback on error.
 158 | 
 159 |     Usage pattern for every repository/service write path::
 160 | 
 161 |         with request_transaction() as session:
 162 |             ... pure DB reads/writes only, no provider calls ...
 163 | 
 164 |     The session is closed on exit.  Keep the ``with`` body free of
 165 |     network calls; see the module docstring.
 166 |     """
 167 |     factory = session_factory or get_session_factory()
 168 |     with factory() as session:
 169 |         try:
 170 |             with session.begin():
 171 |                 yield session
 172 |         except Exception:
 173 |             raise
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L153 | Wrap the generator as a context manager: code before yield runs on entry and code after yield/finally runs on exit. |
| L154 | Define `request_transaction`; bind its arguments when called. The body is a generator because it contains yield; work proceeds when advanced. |
| L155 | Declare parameter `session_factory` with annotation `sessionmaker[Session] \| None`. Callable that creates database sessions; a null value selects the function's configured default. |
| L156 | Finish/continue the signature; the declared return annotation is `Iterator[Session]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L157 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L159 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L161 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L162 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L164 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L165 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L166 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L167 | Evaluate the right-hand side, then bind/store it in `factory`: evaluate `session_factory or get_session_factory()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L168 | Enter `factory()` — Create a new SQLAlchemy session from the selected factory and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L169 | Enter the protected block; failures are matched against `Exception` in order. |
| L170 | Enter `session.begin()` — Create a transaction context: successful exit commits, exceptional exit rolls back. Context exits run in reverse order, including on return/exception. |
| L171 | yield `session` to the caller and suspend until the generator is resumed or closed. |
| L172 | Handle `Exception`; only a matching error from the associated try enters this body. |
| L173 | Re-raise the currently handled exception with its traceback; no replacement result is returned. |

<!-- END LINE WALKTHROUGH -->

### `worker_transaction(session_factory: sessionmaker[Session] | None = None) -> Iterator[Session]`

- **Arguments:** Optional worker factory; if omitted, creates a fresh `make_worker_session_factory()`.
- **Returns/yields:** A context manager yielding one session.
- **Work:** Uses the same begin/yield/commit-or-rollback/close sequence as `request_transaction`. Reusing a supplied factory avoids creating a new engine for each operation; the helper does not explicitly dispose engines.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-worker-transaction"></a>

#### Line-by-line execution

[Current source: lines 176–188](../../../../Backend/app/db/session.py#L176-L188). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `session_factory` | `sessionmaker[Session] \| None`; default `None`; positional or keyword | Callable that creates database sessions; a null value selects the function's configured default. |

**Declared result:** `Iterator[Session]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 176 | @contextmanager
 177 | def worker_transaction(
 178 |     session_factory: sessionmaker[Session] | None = None,
 179 | ) -> Iterator[Session]:
 180 |     """Worker counterpart of :func:`request_transaction` (same semantics)."""
 181 |     if session_factory is None:
 182 |         session_factory = make_worker_session_factory()
 183 |     with session_factory() as session:
 184 |         try:
 185 |             with session.begin():
 186 |                 yield session
 187 |         except Exception:
 188 |             raise
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L176 | Wrap the generator as a context manager: code before yield runs on entry and code after yield/finally runs on exit. |
| L177 | Define `worker_transaction`; bind its arguments when called. The body is a generator because it contains yield; work proceeds when advanced. |
| L178 | Declare parameter `session_factory` with annotation `sessionmaker[Session] \| None`. Callable that creates database sessions; a null value selects the function's configured default. |
| L179 | Finish/continue the signature; the declared return annotation is `Iterator[Session]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L180 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L181 | Evaluate the branch condition: compare whether `session_factory` is the same object as `None`. If truthy, enter L182; otherwise skip this indented block and continue after it. |
| L182 | Evaluate the right-hand side, then bind/store it in `session_factory`: `make_worker_session_factory()` — Call [make_worker_session_factory](#walk-make-worker-session-factory) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L183 | Enter `session_factory()` — Create a new SQLAlchemy session from the supplied factory and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L184 | Enter the protected block; failures are matched against `Exception` in order. |
| L185 | Enter `session.begin()` — Create a transaction context: successful exit commits, exceptional exit rolls back. Context exits run in reverse order, including on return/exception. |
| L186 | yield `session` to the caller and suspend until the generator is resumed or closed. |
| L187 | Handle `Exception`; only a matching error from the associated try enters this body. |
| L188 | Re-raise the currently handled exception with its traceback; no replacement result is returned. |

<!-- END LINE WALKTHROUGH -->

### `get_db() -> Iterator[Session]`

- **Arguments:** None; used as a FastAPI yield dependency.
- **Returns/yields:** One request-scoped session from the cached request factory.
- **Work:** Opens, yields, and closes the session. It never commits implicitly; handlers using this dependency explicitly commit successful mutations and roll back failures. Closing discards any still-uncommitted transaction.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-db"></a>

#### Line-by-line execution

[Current source: lines 191–202](../../../../Backend/app/db/session.py#L191-L202). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `Iterator[Session]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 191 | def get_db() -> Iterator[Session]:
 192 |     """FastAPI dependency yielding a request-scoped session.
 193 | 
 194 |     Handlers that only read (or that manage their own short transactions
 195 |     via :func:`request_transaction`) use this dependency.  It never
 196 |     commits implicitly; write handlers must use ``request_transaction``
 197 |     or an explicit ``session.begin()`` block so commit boundaries stay
 198 |     visible in code review.
 199 |     """
 200 |     factory = get_session_factory()
 201 |     with factory() as session:
 202 |         yield session
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L191 | Define `get_db`; bind its arguments when called. The body is a generator because it contains yield; work proceeds when advanced. |
| L192 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L194 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L195 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L196 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L197 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L198 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L199 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L200 | Evaluate the right-hand side, then bind/store it in `factory`: `get_session_factory()` — Call [get_session_factory](#walk-get-session-factory) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L201 | Enter `factory()` — Create a new SQLAlchemy session from the selected factory and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L202 | yield `session` to the caller and suspend until the generator is resumed or closed. |

<!-- END LINE WALKTHROUGH -->
