# `app/auth/config.py`

[Source](../../../../Backend/app/auth/config.py) · [Backend index](../../README.md)

Lazy environment lookup for JWT identity verification. Authentication uses a session-bound JWT and needs no server API key here. `DEFAULT_ENDPOINT` is `https://cloud.appwrite.io/v1`.

## Functions

### `appwrite_endpoint() -> str`

**Arguments:** None. **Returns:** Endpoint without trailing slashes. **Work:** Tries stripped `APPWRITE_ENDPOINT`, then stripped `NEXT_PUBLIC_APPWRITE_ENDPOINT`, then `DEFAULT_ENDPOINT`, and applies `rstrip("/")`. Does not validate network reachability.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-appwrite-endpoint"></a>

#### Line-by-line execution

[Current source: lines 21–26](../../../../Backend/app/auth/config.py#L21-L26). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  21 | def appwrite_endpoint() -> str:
  22 |     endpoint = (
  23 |         os.environ.get("APPWRITE_ENDPOINT", "").strip()
  24 |         or os.environ.get("NEXT_PUBLIC_APPWRITE_ENDPOINT", "").strip()
  25 |     )
  26 |     return (endpoint or DEFAULT_ENDPOINT).rstrip("/")
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L21 | Define `appwrite_endpoint`; bind its arguments when called. The body executes only when invoked. |
| L22 | Evaluate the right-hand side, then bind/store it in `endpoint`: evaluate `os.environ.get('APPWRITE_ENDPOINT', '').strip() or os.environ.get('NEXT_PUBLIC_APPWRITE_ENDPOINT', '').strip()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L23 | `os.environ.get('APPWRITE_ENDPOINT', '').strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed; first obtain the receiver: `os.environ.get('APPWRITE_ENDPOINT', '')` — Read a process environment value without changing it, using the supplied fallback if absent. |
| L24 | Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed. |
| L25 | Close the parenthesized expression; delimiters only group the preceding operation. |
| L26 | Compute the return value: `(endpoint or DEFAULT_ENDPOINT).rstrip('/')` — Remove matching trailing characters (not a whole substring). Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `appwrite_project_id() -> str`

**Arguments:** None. **Returns:** Stripped server project ID, the public fallback, or an empty string. **Work:** Reads `APPWRITE_PROJECT_ID` before `NEXT_PUBLIC_APPWRITE_PROJECT_ID` at call time.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-appwrite-project-id"></a>

#### Line-by-line execution

[Current source: lines 29–33](../../../../Backend/app/auth/config.py#L29-L33). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  29 | def appwrite_project_id() -> str:
  30 |     return (
  31 |         os.environ.get("APPWRITE_PROJECT_ID", "").strip()
  32 |         or os.environ.get("NEXT_PUBLIC_APPWRITE_PROJECT_ID", "").strip()
  33 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L29 | Define `appwrite_project_id`; bind its arguments when called. The body executes only when invoked. |
| L30 | Compute the return value: evaluate `os.environ.get('APPWRITE_PROJECT_ID', '').strip() or os.environ.get('NEXT_PUBLIC_APPWRITE_PROJECT_ID', '').strip()` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L31 | `os.environ.get('APPWRITE_PROJECT_ID', '').strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed; first obtain the receiver: `os.environ.get('APPWRITE_PROJECT_ID', '')` — Read a process environment value without changing it, using the supplied fallback if absent. |
| L32 | Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed. |
| L33 | Close the parenthesized expression; delimiters only group the preceding operation. |

<!-- END LINE WALKTHROUGH -->

### `appwrite_configured() -> bool`

**Arguments:** None. **Returns:** Whether `appwrite_project_id()` is nonempty. **Work:** Performs only that presence check; endpoint syntax, permissions, credentials, and connectivity are not checked.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-appwrite-configured"></a>

#### Line-by-line execution

[Current source: lines 36–37](../../../../Backend/app/auth/config.py#L36-L37). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  36 | def appwrite_configured() -> bool:
  37 |     return bool(appwrite_project_id())
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L36 | Define `appwrite_configured`; bind its arguments when called. The body executes only when invoked. |
| L37 | Compute the return value: `bool(appwrite_project_id())` — Convert the value's truthiness to True or False; inputs include `appwrite_project_id()` — Call [appwrite_project_id](#walk-appwrite-project-id) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
