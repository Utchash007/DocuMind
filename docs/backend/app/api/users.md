# `app/api/users.py`

[Source](../../../../Backend/app/api/users.py) · [Backend index](../../README.md)

Router prefix `/me`, tag `users`. Both synchronous routes use `PrincipalDep`, allowing authenticated accounts to finish onboarding. Responses serialize `ApplicationUser` using aliases.

## Functions

### `read_me(principal: PrincipalDep) -> ApplicationUser` — `GET /me`

- **Arguments:** Verified principal; its dependency has already bootstrapped the account.
- **Returns:** The current profile DTO (HTTP 200).
- **Work:** Opens `request_transaction`, reads `principal.id` with `get_user`, raises 401 if the user has disappeared, and converts ORM attributes with `ApplicationUser.model_validate`. Context exit closes the short transaction before delivery.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-read-me"></a>

#### Line-by-line execution

[Current source: lines 34–41](../../../../Backend/app/api/users.py#L34-L41). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `principal` | `PrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |

**Declared result:** `ApplicationUser`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  34 | @router.get("", response_model=ApplicationUser, response_model_by_alias=True)
  35 | def read_me(principal: PrincipalDep) -> ApplicationUser:
  36 |     """Return (and idempotently bootstrap) the signed-in application user."""
  37 |     with request_transaction() as session:
  38 |         user = get_user(session, principal.id)
  39 |         if user is None:
  40 |             raise unauthenticated()
  41 |         return ApplicationUser.model_validate(user)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L34 | Register the handler with FastAPI using `router.get('', response_model=ApplicationUser, response_model_by_alias=True)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L35 | Define `read_me`; bind its arguments when called. The body executes only when invoked. |
| L36 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L37 | Enter `request_transaction()` — Open a short session/transaction context that commits on success, rolls back on exception, and closes the session and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L38 | Evaluate the right-hand side, then bind/store it in `user`: `get_user(session, principal.id)` — Call [get_user](../repositories/users.md#walk-get-user) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L39 | Evaluate the branch condition: compare whether `user` is the same object as `None`. If truthy, enter L40; otherwise skip this indented block and continue after it. |
| L40 | Raise `unauthenticated()`; stop the normal path and transfer control to the nearest matching exception handler. |
| L41 | Compute the return value: `ApplicationUser.model_validate(user)` — Validate/coerce the input into this Pydantic model, including configured field validators. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `update_me(payload: ProfileUpdateRequest, principal: PrincipalDep) -> ApplicationUser` — `PATCH /me`

- **Arguments:** Validated name/DOB request and verified principal.
- **Returns:** Updated profile DTO (HTTP 200).
- **Work:** Within `request_transaction`, calls `update_profile` for the principal's internal ID, raises 401 for a missing user, and constructs the response. The context commits profile/onboarding changes on success and rolls back exceptions. Unknown body fields and invalid profile values are rejected by Pydantic before this function runs.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-update-me"></a>

#### Line-by-line execution

[Current source: lines 44–56](../../../../Backend/app/api/users.py#L44-L56). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `payload` | `ProfileUpdateRequest`; required; positional or keyword | Input mapping, DTO, or provider response; the annotated type and body identify its expected shape. |
| `principal` | `PrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |

**Declared result:** `ApplicationUser`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  44 | @router.patch("", response_model=ApplicationUser, response_model_by_alias=True)
  45 | def update_me(payload: ProfileUpdateRequest, principal: PrincipalDep) -> ApplicationUser:
  46 |     """Complete or update the caller's profile; onboarding is derived."""
  47 |     with request_transaction() as session:
  48 |         user = update_profile(
  49 |             session,
  50 |             user_id=principal.id,
  51 |             name=payload.name,
  52 |             date_of_birth=payload.date_of_birth,
  53 |         )
  54 |         if user is None:
  55 |             raise unauthenticated()
  56 |         return ApplicationUser.model_validate(user)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L44 | Register the handler with FastAPI using `router.patch('', response_model=ApplicationUser, response_model_by_alias=True)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L45 | Define `update_me`; bind its arguments when called. The body executes only when invoked. |
| L46 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L47 | Enter `request_transaction()` — Open a short session/transaction context that commits on success, rolls back on exception, and closes the session and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L48 | Evaluate the right-hand side, then bind/store it in `user`: `update_profile(session, user_id=principal.id, name=payload.name, date_of_birth=payload.date_of_birth)` — Call [update_profile](../repositories/users.md#walk-update-profile) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L49 | Supply positional argument 1 to `update_profile`: the current `session` value. |
| L50 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. |
| L51 | Supply `name` = `payload.name`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: the `name` attribute of `payload`. |
| L52 | Supply `date_of_birth` = `payload.date_of_birth`. Profile birth date validated against the current date before onboarding completion. Evaluate the value as: the `date_of_birth` attribute of `payload`. |
| L53 | Close the expression/container begun at L48; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L54 | Evaluate the branch condition: compare whether `user` is the same object as `None`. If truthy, enter L55; otherwise skip this indented block and continue after it. |
| L55 | Raise `unauthenticated()`; stop the normal path and transfer control to the nearest matching exception handler. |
| L56 | Compute the return value: `ApplicationUser.model_validate(user)` — Validate/coerce the input into this Pydantic model, including configured field validators. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
