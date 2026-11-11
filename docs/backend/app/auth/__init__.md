# `app/auth/__init__.py`

[Source](../../../../Backend/app/auth/__init__.py) · [Backend index](../../README.md)

Lazily exports `PrincipalDep`, `OnboardedPrincipalDep`, `PrincipalResolver`, `get_principal`, `get_principal_resolver`, `require_onboarded`, and `verify_appwrite_identity`. `_EXPORTS` maps these public names to attributes in [principal.md](principal.md).

## Functions

### `__getattr__(name: str)`

- **Arguments:** An attribute name requested from the package.
- **Returns:** The corresponding object from `app.auth.principal` for an allowed export.
- **Work:** Checks `_EXPORTS`, imports the principal submodule on demand, and calls `getattr` on it. Unknown names raise `AttributeError`. Delayed import prevents the cycle `repositories.users → auth.errors → auth.principal → repositories.users`.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk---getattr--"></a>

#### Line-by-line execution

[Current source: lines 42–50](../../../../Backend/app/auth/__init__.py#L42-L50). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `name` | `str`; required; positional or keyword | Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. |

**Declared result:** No return annotation; follow the return/yield lines below. Python supplies None when a non-generator reaches the end without return.

**Numbered source**

```text
  42 | def __getattr__(name: str):
  43 |     # Lazy imports: app.repositories.users imports app.auth.errors, while
  44 |     # app.auth.principal imports app.repositories.users. Eager imports here
  45 |     # would create a cycle; defer principal until first use (PEP 562).
  46 |     if name in _EXPORTS:
  47 |         from app.auth import principal
  48 | 
  49 |         return getattr(principal, _EXPORTS[name])
  50 |     raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L42 | Define `__getattr__`; bind its arguments when called. The body executes only when invoked. |
| L43 | Comment only: Lazy imports: app.repositories.users imports app.auth.errors, while. It does not execute; the neighboring code determines behavior. |
| L44 | Comment only: app.auth.principal imports app.repositories.users. Eager imports here. It does not execute; the neighboring code determines behavior. |
| L45 | Comment only: would create a cycle; defer principal until first use (PEP 562).. It does not execute; the neighboring code determines behavior. |
| L46 | Evaluate the branch condition: compare whether `name` is contained in `_EXPORTS`. If truthy, enter L47; otherwise skip this indented block and continue after it. |
| L47 | Import `principal` from `app.auth`; inside a function this import is deferred until this path is reached. |
| L49 | Compute the return value: `getattr(principal, _EXPORTS[name])` — Read the named attribute, using the supplied default only if the attribute is absent. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L50 | Raise `AttributeError(f'module {__name__!r} has no attribute {name!r}')`; stop the normal path and transfer control to the nearest matching exception handler. |

<!-- END LINE WALKTHROUGH -->

### `__dir__() -> list[str]`

- **Arguments:** None.
- **Returns:** A sorted copy of `__all__`.
- **Work:** Makes introspection expose the lazy public API without importing/resolving its members.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk---dir--"></a>

#### Line-by-line execution

[Current source: lines 53–54](../../../../Backend/app/auth/__init__.py#L53-L54). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `list[str]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  53 | def __dir__() -> list[str]:
  54 |     return sorted(__all__)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L53 | Define `__dir__`; bind its arguments when called. The body executes only when invoked. |
| L54 | Compute the return value: `sorted(__all__)` — Create a sorted list using the supplied key/reverse options; equal keys retain input order. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
