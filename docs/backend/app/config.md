# `app/config.py`

[Source](../../../Backend/app/config.py) · [Backend index](../README.md)

Loads shared application settings for the API and standalone worker. `ROOT_ENV_PATH` resolves to the repository-root `.env`, two parents above this source file's containing directory.

## Functions

### `load_application_env(path: Path = ROOT_ENV_PATH) -> None`

- **Arguments:** `path`, the dotenv file to read; defaults to the repository-root application configuration.
- **Returns:** `None`.
- **Work:** Calls `dotenv_values(path)`, iterates its parsed key/value pairs, skips `TEST_DATABASE_URL` and entries without a value, and applies the rest with `os.environ.setdefault`. Existing shell values therefore take precedence. Empty strings are values and may be inserted; missing files follow python-dotenv's empty-result behavior.
- **Side effects:** Adds application variables to the current process environment. The reserved database-target variable is excluded even though the project test suites have been removed; URL selection and migration guards still use it explicitly.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-load-application-env"></a>

#### Line-by-line execution

[Current source: lines 11–16](../../../Backend/app/config.py#L11-L16). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `path` | `Path`; default `ROOT_ENV_PATH`; positional or keyword | Local PDF/file path used by the filesystem or extraction operation. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  11 | def load_application_env(path: Path = ROOT_ENV_PATH) -> None:
  12 |     for name, value in dotenv_values(path).items():
  13 |         # Live test authorization must be explicit in the invoking shell,
  14 |         # never inherited from a production application configuration file.
  15 |         if name != "TEST_DATABASE_URL" and value is not None:
  16 |             os.environ.setdefault(name, value)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L11 | Define `load_application_env`; bind its arguments when called. The body executes only when invoked. |
| L12 | Iterate `dotenv_values(path).items()` (`dotenv_values(path).items()` — Iterate the mapping's key/value pairs; first obtain the receiver: `dotenv_values(path)` — Parse dotenv entries into a mapping without applying them to process environment), assigning each item to `(name, value)`. Execute the indented body once per item; an empty iterable skips it. |
| L13 | Comment only: Live test authorization must be explicit in the invoking shell,. It does not execute; the neighboring code determines behavior. |
| L14 | Comment only: never inherited from a production application configuration file.. It does not execute; the neighboring code determines behavior. |
| L15 | Evaluate the branch condition: evaluate `name != 'TEST_DATABASE_URL' and value is not None` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L16; otherwise skip this indented block and continue after it. |
| L16 | `os.environ.setdefault(name, value)` — Set the environment entry only when it does not already exist, preserving shell precedence. The return value is not assigned here. |

<!-- END LINE WALKTHROUGH -->
