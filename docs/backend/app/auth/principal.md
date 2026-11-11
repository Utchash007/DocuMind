# `app/auth/principal.py`

[Source](../../../../Backend/app/auth/principal.py) · [Backend index](../../README.md)

Verifies Next.js-minted Appwrite JWTs, then resolves the account's internal PostgreSQL identity. `IdentityVerifier` is `Callable[[str], dict[str, str]]`; `SessionScope` creates a context manager yielding a SQLAlchemy session. `PrincipalDep` wraps `get_principal`; `OnboardedPrincipalDep` wraps `require_onboarded`.

## Functions

### `extract_bearer_token(authorization_header: str) -> str`

- **Arguments:** Full Authorization header.
- **Returns:** The trimmed token.
- **Work:** Partitions once at a literal space, requires a case-insensitive `Bearer` scheme, strips outer token whitespace, and rejects missing or internally whitespace-containing tokens. Invalid input raises HTTP 401.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-extract-bearer-token"></a>

#### Line-by-line execution

[Current source: lines 63–71](../../../../Backend/app/auth/principal.py#L63-L71). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `authorization_header` | `str`; required; positional or keyword | Authorization header to parse and verify through Appwrite. |

**Declared result:** `str`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  63 | def extract_bearer_token(authorization_header: str) -> str:
  64 |     """Return the token from ``Authorization: Bearer <token>`` or 401."""
  65 |     (scheme, separator, token) = authorization_header.partition(" ")
  66 |     if not separator or scheme.lower() != "bearer":
  67 |         raise unauthenticated()
  68 |     token = token.strip()
  69 |     if not token or any(character.isspace() for character in token):
  70 |         raise unauthenticated()
  71 |     return token
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L63 | Define `extract_bearer_token`; bind its arguments when called. The body executes only when invoked. |
| L64 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L65 | Evaluate the right-hand side, then bind/store it in `(scheme, separator, token)`: `authorization_header.partition(' ')` — Split once at the separator and return the before/separator/after triple. |
| L66 | Evaluate the branch condition: evaluate `not separator or scheme.lower() != 'bearer'` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L67; otherwise skip this indented block and continue after it. |
| L67 | Raise `unauthenticated()`; stop the normal path and transfer control to the nearest matching exception handler. |
| L68 | Evaluate the right-hand side, then bind/store it in `token`: `token.strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed. |
| L69 | Evaluate the branch condition: evaluate `not token or any((character.isspace() for character in token))` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L70; otherwise skip this indented block and continue after it. |
| L70 | Raise `unauthenticated()`; stop the normal path and transfer control to the nearest matching exception handler. |
| L71 | Compute the return value: the current `token` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `verify_appwrite_identity(token: str) -> dict[str, str]`

- **Arguments:** Raw Bearer token, without the scheme.
- **Returns:** `{"appwrite_user_id": ..., "email": ...}` from the Appwrite account; email is trimmed/lowercased.
- **Work:** Resolves endpoint/project, lazily imports the Appwrite SDK, constructs `Client().set_endpoint(...).set_project(...).set_jwt(token)`, and calls `Account.get()`. Appwrite performs credential verification. Extracts `$id`/email and requires both nonempty; it does not separately inspect `emailVerification`.
- **Errors:** Missing project, SDK import failures, transport/provider errors → 503; Appwrite 401/403 → 401; missing account ID/email → 401. No database transaction surrounds this network call.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-verify-appwrite-identity"></a>

#### Line-by-line execution

[Current source: lines 74–111](../../../../Backend/app/auth/principal.py#L74-L111). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `token` | `str`; required; positional or keyword | Expected claim/generation token compared with persisted state. |

**Declared result:** `dict[str, str]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  74 | def verify_appwrite_identity(token: str) -> dict[str, str]:
  75 |     """Verify ``token`` through Appwrite; return the verified identity.
  76 | 
  77 |     The Appwrite server performs the signature/expiry checks: we send
  78 |     the JWT in ``x-appwrite-jwt`` and read back the account.  Client
  79 |     auth rejections map to 401; transport/5xx/configuration problems
  80 |     map to a retryable 503 (fail closed).
  81 |     """
  82 |     project_id = config.appwrite_project_id()
  83 |     endpoint = config.appwrite_endpoint()
  84 |     if not project_id:
  85 |         raise service_unavailable(
  86 |             "Identity verification is not configured. Please try again."
  87 |         )
  88 | 
  89 |     try:
  90 |         from appwrite.client import Client
  91 |         from appwrite.exception import AppwriteException
  92 |         from appwrite.services.account import Account
  93 |     except Exception:
  94 |         raise service_unavailable() from None
  95 | 
  96 |     client = Client().set_endpoint(endpoint).set_project(project_id).set_jwt(token)
  97 |     try:
  98 |         user: Any = Account(client).get()
  99 |     except AppwriteException as error:
 100 |         code = getattr(error, "code", None)
 101 |         if isinstance(code, int) and code in (401, 403):
 102 |             raise unauthenticated() from None
 103 |         raise service_unavailable() from None
 104 |     except Exception:
 105 |         raise service_unavailable() from None
 106 | 
 107 |     appwrite_user_id = str(user.get("$id") or "").strip()
 108 |     email = str(user.get("email") or "").strip().lower()
 109 |     if not appwrite_user_id or not email:
 110 |         raise unauthenticated("An email account is required to access NoteMind.")
 111 |     return {"appwrite_user_id": appwrite_user_id, "email": email}
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L74 | Define `verify_appwrite_identity`; bind its arguments when called. The body executes only when invoked. |
| L75 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L77 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L78 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L79 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L80 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L81 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L82 | Evaluate the right-hand side, then bind/store it in `project_id`: `config.appwrite_project_id()` — Call [config.appwrite_project_id](config.md#walk-appwrite-project-id) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L83 | Evaluate the right-hand side, then bind/store it in `endpoint`: `config.appwrite_endpoint()` — Call [config.appwrite_endpoint](config.md#walk-appwrite-endpoint) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L84 | Evaluate the branch condition: invert the truthiness of `project_id`. If truthy, enter L85; otherwise skip this indented block and continue after it. |
| L85 | Raise `service_unavailable('Identity verification is not configured. Please try again.')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L86 | Supply positional argument 1 to `service_unavailable`: `'Identity verification is not configured. Please try again.'`. |
| L87 | Close the expression/container begun at L85; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L89 | Enter the protected block; failures are matched against `Exception` in order. |
| L90 | Import `Client` from `appwrite.client`; inside a function this import is deferred until this path is reached. |
| L91 | Import `AppwriteException` from `appwrite.exception`; inside a function this import is deferred until this path is reached. |
| L92 | Import `Account` from `appwrite.services.account`; inside a function this import is deferred until this path is reached. |
| L93 | Handle `Exception`; only a matching error from the associated try enters this body. |
| L94 | Raise `service_unavailable()`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `None` as its cause. |
| L96 | Evaluate the right-hand side, then bind/store it in `client`: `Client().set_endpoint(endpoint).set_project(project_id).set_jwt(token)` — Set the user-bound JWT on this fresh Appwrite client for identity verification; first obtain the receiver: `Client().set_endpoint(endpoint).set_project(project_id)` — Set the Appwrite project identifier on the client and return the client for chaining; first obtain the receiver: `Client().set_endpoint(endpoint)` — Set the Appwrite service endpoint on the client and return the client for chaining. |
| L97 | Enter the protected block; failures are matched against `AppwriteException`, `Exception` in order. |
| L98 | Evaluate the right-hand side, then bind/store it in `user`: `Account(client).get()` — Read the authenticated Appwrite account through this client; failure rejects the credential or signals a provider outage; first obtain the receiver: `Account(client)` — Construct `Account` with the shown fields; its class/model initialization rules apply. |
| L99 | Handle `AppwriteException` and bind it to `error`; only a matching error from the associated try enters this body. |
| L100 | Evaluate the right-hand side, then bind/store it in `code`: `getattr(error, 'code', None)` — Read the named attribute, using the supplied default only if the attribute is absent. |
| L101 | Evaluate the branch condition: evaluate `isinstance(code, int) and code in (401, 403)` left-to-right with short-circuit AND: stop at the first falsy operand, otherwise use the last; the result is an operand value, not necessarily a bool. If truthy, enter L102; otherwise skip this indented block and continue after it. |
| L102 | Raise `unauthenticated()`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `None` as its cause. |
| L103 | Raise `service_unavailable()`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `None` as its cause. |
| L104 | Handle `Exception`; only a matching error from the associated try enters this body. |
| L105 | Raise `service_unavailable()`; stop the normal path and transfer control to the nearest matching exception handler. Explicitly chain `None` as its cause. |
| L107 | Evaluate the right-hand side, then bind/store it in `appwrite_user_id`: `str(user.get('$id') or '').strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed; first obtain the receiver: `str(user.get('$id') or '')` — Convert the input to its string representation. |
| L108 | Evaluate the right-hand side, then bind/store it in `email`: `str(user.get('email') or '').strip().lower()` — Return a lowercased string copy; first obtain the receiver: `str(user.get('email') or '').strip()` — Return a copy with leading/trailing whitespace removed, or the specified boundary characters removed; first obtain the receiver: `str(user.get('email') or '')` — Convert the input to its string representation. |
| L109 | Evaluate the branch condition: evaluate `not appwrite_user_id or not email` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. If truthy, enter L110; otherwise skip this indented block and continue after it. |
| L110 | Raise `unauthenticated('An email account is required to access NoteMind.')`; stop the normal path and transfer control to the nearest matching exception handler. |
| L111 | Compute the return value: build a dictionary from the shown key/value entries, evaluating values now; ** entries expand another mapping. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `PrincipalResolver.__init__(self, verify_identity=None, session_scope=None) -> None`

- **Arguments:** Optional verifier callable and short-transaction context factory.
- **Returns:** `None`.
- **Work:** Stores supplied collaborators or defaults to `verify_appwrite_identity` and a zero-argument lambda returning `request_transaction()`. The lambda does not start its transaction until resolution uses the context manager. Construction performs no network/SQL work.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-principalresolver---init--"></a>

#### Line-by-line execution

[Current source: lines 121–127](../../../../Backend/app/auth/principal.py#L121-L127). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `verify_identity` | `IdentityVerifier \| None`; default `None`; positional or keyword | Caller-supplied verify identity; each read, transformation, and validation is traced below. |
| `session_scope` | `SessionScope \| None`; default `None`; positional or keyword | Caller-supplied session scope; each read, transformation, and validation is traced below. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 121 |     def __init__(
 122 |         self,
 123 |         verify_identity: IdentityVerifier | None = None,
 124 |         session_scope: SessionScope | None = None,
 125 |     ) -> None:
 126 |         self._verify_identity = verify_identity or verify_appwrite_identity
 127 |         self._session_scope = session_scope or (lambda: request_transaction())
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L121 | Define `PrincipalResolver.__init__`; bind its arguments when called. The body executes only when invoked. |
| L122 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L123 | Declare parameter `verify_identity` with annotation `IdentityVerifier \| None`. Caller-supplied verify identity; its uses and transformations are traced below. |
| L124 | Declare parameter `session_scope` with annotation `SessionScope \| None`. Caller-supplied session scope; its uses and transformations are traced below. |
| L125 | Finish/continue the signature; the declared return annotation is `None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L126 | Evaluate the right-hand side, then bind/store it in `self._verify_identity`: evaluate `verify_identity or verify_appwrite_identity` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L127 | Evaluate the right-hand side, then bind/store it in `self._session_scope`: evaluate `session_scope or (lambda: request_transaction())` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |

<!-- END LINE WALKTHROUGH -->

### `PrincipalResolver.resolve_principal(self, authorization_header: str) -> AuthenticatedUser`

- **Arguments:** Full Authorization header and the configured resolver instance.
- **Returns:** An internal authenticated-user DTO with database UUID, external Appwrite ID, email, and onboarding state.
- **Work:** Extracts/verifies the token first; then enters a short SQL scope, calls `bootstrap_user` using verified identity values, and validates/copies the public principal fields. Context exit commits before the result reaches the caller. Authentication, bootstrap conflict, and database errors propagate.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-principalresolver-resolve-principal"></a>

#### Line-by-line execution

[Current source: lines 129–143](../../../../Backend/app/auth/principal.py#L129-L143). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `authorization_header` | `str`; required; positional or keyword | Authorization header to parse and verify through Appwrite. |

**Declared result:** `AuthenticatedUser`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 129 |     def resolve_principal(self, authorization_header: str) -> AuthenticatedUser:
 130 |         token = extract_bearer_token(authorization_header)
 131 |         identity = self._verify_identity(token)
 132 |         with self._session_scope() as session:
 133 |             user = bootstrap_user(
 134 |                 session,
 135 |                 appwrite_user_id=identity["appwrite_user_id"],
 136 |                 email=identity["email"],
 137 |             )
 138 |             return AuthenticatedUser(
 139 |                 id=user.id,
 140 |                 appwrite_user_id=user.appwrite_user_id,
 141 |                 email=user.email,
 142 |                 onboarding_completed=user.onboarding_completed,
 143 |             )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L129 | Define `PrincipalResolver.resolve_principal`; bind its arguments when called. The body executes only when invoked. |
| L130 | Evaluate the right-hand side, then bind/store it in `token`: `extract_bearer_token(authorization_header)` — Call [extract_bearer_token](#walk-extract-bearer-token) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. |
| L131 | Evaluate the right-hand side, then bind/store it in `identity`: `self._verify_identity(token)` — Call the identity-verifier collaborator with the parsed JWT; default wiring verifies it through Appwrite. |
| L132 | Enter `self._session_scope()` — Create the injected/default short transaction context used for internal-user bootstrap and bind its entered value to `session`. Context exits run in reverse order, including on return/exception. |
| L133 | Evaluate the right-hand side, then bind/store it in `user`: `bootstrap_user(session, appwrite_user_id=identity['appwrite_user_id'], email=identity['email'])` — Call [bootstrap_user](../repositories/users.md#walk-bootstrap-user) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L134 | Supply positional argument 1 to `bootstrap_user`: the current `session` value. |
| L135 | Supply `appwrite_user_id` = `identity['appwrite_user_id']`. Verified external Appwrite identity, distinct from the internal PostgreSQL UUID. Evaluate the value as: look up index/key `'appwrite_user_id'` in `identity`; a missing key or out-of-range index raises. |
| L136 | Supply `email` = `identity['email']`. Verified identity email, normalized by the user repository before persistence. Evaluate the value as: look up index/key `'email'` in `identity`; a missing key or out-of-range index raises. |
| L137 | Close the expression/container begun at L133; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L138 | Compute the return value: `AuthenticatedUser(id=user.id, appwrite_user_id=user.appwrite_user_id, email=user.email, onboarding_completed=user.onboarding_completed)` — Construct `AuthenticatedUser` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L139 | Supply `id` = `user.id`.  Evaluate the value as: the `id` attribute of `user`. |
| L140 | Supply `appwrite_user_id` = `user.appwrite_user_id`. Verified external Appwrite identity, distinct from the internal PostgreSQL UUID. Evaluate the value as: the `appwrite_user_id` attribute of `user`. |
| L141 | Supply `email` = `user.email`. Verified identity email, normalized by the user repository before persistence. Evaluate the value as: the `email` attribute of `user`. |
| L142 | Supply `onboarding_completed` = `user.onboarding_completed`.  Evaluate the value as: the `onboarding_completed` attribute of `user`. |
| L143 | Close the expression/container begun at L138; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `get_principal_resolver() -> PrincipalResolver`

**Arguments:** None. **Returns:** Process-local `_default_resolver`. **Work:** Constructs it on first use and reuses it afterward; adapters still read configuration when invoked.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-principal-resolver"></a>

#### Line-by-line execution

[Current source: lines 149–154](../../../../Backend/app/auth/principal.py#L149-L154). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

No parameters.

**Declared result:** `PrincipalResolver`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 149 | def get_principal_resolver() -> PrincipalResolver:
 150 |     """Default resolver factory (tests override this via FastAPI)."""
 151 |     global _default_resolver
 152 |     if _default_resolver is None:
 153 |         _default_resolver = PrincipalResolver()
 154 |     return _default_resolver
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L149 | Define `get_principal_resolver`; bind its arguments when called. The body executes only when invoked. |
| L150 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L151 | Bind assignments to module-level `_default_resolver` rather than creating local variables. |
| L152 | Evaluate the branch condition: compare whether `_default_resolver` is the same object as `None`. If truthy, enter L153; otherwise skip this indented block and continue after it. |
| L153 | Evaluate the right-hand side, then bind/store it in `_default_resolver`: `PrincipalResolver()` — Construct `PrincipalResolver` with the shown fields; its class/model initialization rules apply. |
| L154 | Compute the return value: the current `_default_resolver` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `get_principal(resolver, authorization: str | None = None) -> AuthenticatedUser`

**Arguments:** FastAPI-injected resolver and optional Authorization header. **Returns:** `resolver.resolve_principal(authorization or "")`. **Work:** Converts a missing header to the empty string, letting the same Bearer validation raise 401.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-principal"></a>

#### Line-by-line execution

[Current source: lines 157–162](../../../../Backend/app/auth/principal.py#L157-L162). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `resolver` | `Annotated[PrincipalResolver, Depends(get_principal_resolver)]`; required; positional or keyword | Caller-supplied resolver; each read, transformation, and validation is traced below. |
| `authorization` | `Annotated[str \| None, Header()]`; default `None`; positional or keyword | Incoming Authorization header, containing the Appwrite Bearer JWT. |

**Declared result:** `AuthenticatedUser`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 157 | def get_principal(
 158 |     resolver: Annotated[PrincipalResolver, Depends(get_principal_resolver)],
 159 |     authorization: Annotated[str | None, Header()] = None,
 160 | ) -> AuthenticatedUser:
 161 |     """FastAPI dependency: the verified principal for this request."""
 162 |     return resolver.resolve_principal(authorization or "")
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L157 | Define `get_principal`; bind its arguments when called. The body executes only when invoked. |
| L158 | Declare parameter `resolver` with annotation `Annotated[PrincipalResolver, Depends(get_principal_resolver)]`. Caller-supplied resolver; its uses and transformations are traced below. |
| L159 | Declare parameter `authorization` with annotation `Annotated[str \| None, Header()]`. Incoming Authorization header, containing the Appwrite Bearer JWT. |
| L160 | Finish/continue the signature; the declared return annotation is `AuthenticatedUser`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L161 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L162 | Compute the return value: `resolver.resolve_principal(authorization or '')` — Invoke `resolver.resolve_principal` with the shown inputs and use its result; see the function overview for its role in this flow. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `require_onboarded(principal: AuthenticatedUser) -> AuthenticatedUser`

**Arguments:** FastAPI-injected verified principal. **Returns:** That same principal when onboarded. **Work:** Checks `onboarding_completed`; false raises HTTP 403 / `onboarding_required`. No provider/database calls are added.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-require-onboarded"></a>

#### Line-by-line execution

[Current source: lines 165–171](../../../../Backend/app/auth/principal.py#L165-L171). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `principal` | `Annotated[AuthenticatedUser, Depends(get_principal)]`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |

**Declared result:** `AuthenticatedUser`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 165 | def require_onboarded(
 166 |     principal: Annotated[AuthenticatedUser, Depends(get_principal)],
 167 | ) -> AuthenticatedUser:
 168 |     """FastAPI dependency: the principal, with profile completion enforced."""
 169 |     if not principal.onboarding_completed:
 170 |         raise onboarding_required()
 171 |     return principal
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L165 | Define `require_onboarded`; bind its arguments when called. The body executes only when invoked. |
| L166 | Declare parameter `principal` with annotation `Annotated[AuthenticatedUser, Depends(get_principal)]`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L167 | Finish/continue the signature; the declared return annotation is `AuthenticatedUser`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L168 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L169 | Evaluate the branch condition: invert the truthiness of `principal.onboarding_completed`. If truthy, enter L170; otherwise skip this indented block and continue after it. |
| L170 | Raise `onboarding_required()`; stop the normal path and transfer control to the nearest matching exception handler. |
| L171 | Compute the return value: the current `principal` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
