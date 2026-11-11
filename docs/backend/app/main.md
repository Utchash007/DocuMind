# `app/main.py`

[Source](../../../Backend/app/main.py) · [Backend index](../README.md)

Creates the synchronous FastAPI application exported as `app` (title `DocuMind Backend`, version `2.0.0`). Importing the module first loads the repository-root application environment, then registers the user, project, document/job, conversation, and message routers. Provider clients and database connections are resolved later by dependencies.

## Configuration and middleware

`CORS_ORIGINS` is split on commas, stripped, and empty entries are discarded. Its default allows `http://localhost:3000` and `http://127.0.0.1:3000`. CORS allows all methods and headers but sets `allow_credentials=False`. FastAPI supplies its usual OpenAPI, Swagger, and ReDoc endpoints.

## Functions

### `read_root() -> dict[str, str]`

- **Arguments:** None; registered as public `GET /`.
- **Returns:** `{"message": "Welcome to DocuMind API"}`.
- **Work:** Constructs the response dictionary directly. It performs no authentication, database query, or provider request.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-read-root"></a>

#### Line-by-line execution

[Current source: lines 40–42](../../../Backend/app/main.py#L40-L42). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `dict[str, str]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  40 | @app.get("/")
  41 | def read_root() -> dict[str, str]:
  42 |     return {"message": "Welcome to DocuMind API"}
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L40 | Register the handler with FastAPI using `app.get('/')`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L41 | Define `read_root`; bind its arguments when called. The body executes only when invoked. |
| L42 | Compute the return value: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `health_check() -> dict[str, object]`

- **Arguments:** None; registered as public `GET /health`.
- **Returns:** `status: "healthy"` and a `config` object containing `groq_api_key_loaded` and `chroma_host_loaded` booleans.
- **Work:** Reads `GROQ_API_KEY` and `CHROMA_HOST` from the process environment and converts their presence/nonempty value to `bool`. These are configuration-presence indicators; the function does not contact Groq, Chroma, PostgreSQL, or Appwrite.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-health-check"></a>

#### Line-by-line execution

[Current source: lines 45–53](../../../Backend/app/main.py#L45-L53). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `dict[str, object]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  45 | @app.get("/health")
  46 | def health_check() -> dict[str, object]:
  47 |     return {
  48 |         "status": "healthy",
  49 |         "config": {
  50 |             "groq_api_key_loaded": bool(os.getenv("GROQ_API_KEY")),
  51 |             "chroma_host_loaded": bool(os.getenv("CHROMA_HOST")),
  52 |         },
  53 |     }
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L45 | Register the handler with FastAPI using `app.get('/health')`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L46 | Define `health_check`; bind its arguments when called. The body executes only when invoked. |
| L47 | Compute the return value: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L48 | Add mapping entry `'status'`: `'healthy'`. |
| L49 | Add mapping entry `'config'`: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. |
| L50 | Add mapping entry `'groq_api_key_loaded'`: `bool(os.getenv('GROQ_API_KEY'))` — Convert the value's truthiness to True or False; inputs include `os.getenv('GROQ_API_KEY')` — Read a process environment value, using the supplied fallback if absent. |
| L51 | Add mapping entry `'chroma_host_loaded'`: `bool(os.getenv('CHROMA_HOST'))` — Convert the value's truthiness to True or False; inputs include `os.getenv('CHROMA_HOST')` — Read a process environment value, using the supplied fallback if absent. |
| L52 | Close the expression/container begun at L49; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L53 | Close the expression/container begun at L47; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->
