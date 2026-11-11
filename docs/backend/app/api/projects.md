# `app/api/projects.py`

[Source](../../../../Backend/app/api/projects.py) · [Backend index](../../README.md)

Synchronous `/projects` router and shared dependencies used by document routes. `SessionDep` wraps `get_db`, `CurrentPrincipalDep` wraps `get_current_principal`, and `OnboardedPrincipalDep` adds the workspace profile gate. Explicit successful mutations commit here; repositories perform SQL/flushes.

## Functions

### `get_current_principal(authorization: str | None = None) -> AuthenticatedUser`

**Arguments:** FastAPI Authorization header. **Returns:** Verified internal principal. **Work:** Lazily imports `get_principal_resolver` and calls `resolve_principal(authorization or "")`. The real Appwrite/bootstrap resolver is wired; this is not a placeholder.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-get-current-principal"></a>

#### Line-by-line execution

[Current source: lines 74–85](../../../../Backend/app/api/projects.py#L74-L85). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `authorization` | `Annotated[str \| None, Header(alias='Authorization')]`; default `None`; positional or keyword | Incoming Authorization header, containing the Appwrite Bearer JWT. |

**Declared result:** `AuthenticatedUser`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  74 | def get_current_principal(
  75 |     authorization: Annotated[str | None, Header(alias="Authorization")] = None,
  76 | ) -> AuthenticatedUser:
  77 |     """Resolve the principal through Appwrite and the internal-user repository.
  78 | 
  79 |     Appwrite JWT verification + internal-user resolution via
  80 |     ``PrincipalResolver``. Identity comes from validated credentials
  81 |     only (plan §4.1.7); tests override this dependency.
  82 |     """
  83 |     from app.auth.principal import get_principal_resolver
  84 | 
  85 |     return get_principal_resolver().resolve_principal(authorization or "")
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L74 | Define `get_current_principal`; bind its arguments when called. The body executes only when invoked. |
| L75 | Declare parameter `authorization` with annotation `Annotated[str \| None, Header(alias='Authorization')]`. Incoming Authorization header, containing the Appwrite Bearer JWT. |
| L76 | Finish/continue the signature; the declared return annotation is `AuthenticatedUser`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L77 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L79 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L80 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L81 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L82 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L83 | Import `get_principal_resolver` from `app.auth.principal`; inside a function this import is deferred until this path is reached. |
| L85 | Compute the return value: `get_principal_resolver().resolve_principal(authorization or '')` — Invoke `get_principal_resolver().resolve_principal` with the shown inputs and use its result; see the function overview for its role in this flow; first obtain the receiver: `get_principal_resolver()` — Call [get_principal_resolver](../auth/principal.md#walk-get-principal-resolver) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `require_onboarded(principal: AuthenticatedUser) -> AuthenticatedUser`

**Arguments:** Verified principal. **Returns:** Same principal. **Work:** Checks `onboarding_completed`, raising structured HTTP 403 with a workspace-specific message if false.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-require-onboarded"></a>

#### Line-by-line execution

[Current source: lines 88–96](../../../../Backend/app/api/projects.py#L88-L96). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `principal` | `AuthenticatedUser`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |

**Declared result:** `AuthenticatedUser`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  88 | def require_onboarded(principal: AuthenticatedUser) -> AuthenticatedUser:
  89 |     """Enforce completed onboarding for every workspace route."""
  90 |     if not principal.onboarding_completed:
  91 |         raise_api_error(
  92 |             403,
  93 |             ErrorCode.ONBOARDING_REQUIRED,
  94 |             "Complete your profile before using the workspace.",
  95 |         )
  96 |     return principal
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L88 | Define `require_onboarded`; bind its arguments when called. The body executes only when invoked. |
| L89 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L90 | Evaluate the branch condition: invert the truthiness of `principal.onboarding_completed`. If truthy, enter L91; otherwise skip this indented block and continue after it. |
| L91 | `raise_api_error(403, ErrorCode.ONBOARDING_REQUIRED, 'Complete your profile before using the workspace.')` — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L92 | Supply positional argument 1 to `raise_api_error`: `403`. |
| L93 | Supply positional argument 2 to `raise_api_error`: the `ONBOARDING_REQUIRED` attribute of `ErrorCode`. |
| L94 | Supply positional argument 3 to `raise_api_error`: `'Complete your profile before using the workspace.'`. |
| L95 | Close the expression/container begun at L91; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L96 | Compute the return value: the current `principal` value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_get_onboarded_principal(principal) -> AuthenticatedUser`

**Arguments:** FastAPI-injected result of `get_current_principal`. **Returns:** `require_onboarded(principal)`. **Work:** Adapts the explicit gate into a reusable dependency chain.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--get-onboarded-principal"></a>

#### Line-by-line execution

[Current source: lines 99–102](../../../../Backend/app/api/projects.py#L99-L102). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `principal` | `Annotated[AuthenticatedUser, Depends(get_current_principal)]`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |

**Declared result:** `AuthenticatedUser`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  99 | def _get_onboarded_principal(
 100 |     principal: Annotated[AuthenticatedUser, Depends(get_current_principal)],
 101 | ) -> AuthenticatedUser:
 102 |     return require_onboarded(principal)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L99 | Define `_get_onboarded_principal`; bind its arguments when called. The body executes only when invoked. |
| L100 | Declare parameter `principal` with annotation `Annotated[AuthenticatedUser, Depends(get_current_principal)]`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L101 | Finish/continue the signature; the declared return annotation is `AuthenticatedUser`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L102 | Compute the return value: `require_onboarded(principal)` — Call [require_onboarded](#walk-require-onboarded) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `_paginated_dto(rows, next_cursor: str | None) -> PaginatedResponse[ProjectDto]`

**Arguments:** ORM project rows and continuation cursor. **Returns:** Typed list envelope. **Work:** Converts every row with `project_to_dto` and copies the cursor.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk--paginated-dto"></a>

#### Line-by-line execution

[Current source: lines 112–116](../../../../Backend/app/api/projects.py#L112-L116). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `rows` | not annotated; required; positional or keyword | Loaded ORM result rows to convert into a response page. |
| `next_cursor` | `str \| None`; required; positional or keyword | Continuation token to include in the returned page envelope, or null at the end. |

**Declared result:** `PaginatedResponse[ProjectDto]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 112 | def _paginated_dto(rows, next_cursor: str | None) -> PaginatedResponse[ProjectDto]:
 113 |     return PaginatedResponse[ProjectDto](
 114 |         items=[project_to_dto(row) for row in rows],
 115 |         next_cursor=next_cursor,
 116 |     )
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L112 | Define `_paginated_dto`; bind its arguments when called. The body executes only when invoked. |
| L113 | Compute the return value: `PaginatedResponse[ProjectDto](items=[project_to_dto(row) for row in rows], next_cursor=next_cursor)` — Construct `PaginatedResponse[ProjectDto]` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |
| L114 | Supply `items` = `[project_to_dto(row) for row in rows]`.  Evaluate the value as: iterate `rows`, binding each item to `row`; produce `project_to_dto(row)` into a new list. |
| L115 | Supply `next_cursor` = `next_cursor`. Continuation token to include in the returned page envelope, or null at the end. Evaluate the value as: the current `next_cursor` value. |
| L116 | Close the expression/container begun at L113; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |

<!-- END LINE WALKTHROUGH -->

### `list_projects(principal, session, cursor=None, limit=50) -> PaginatedResponse[ProjectDto]`

**Route:** `GET /projects` (200). **Arguments:** Onboarded principal, injected session, optional query cursor, bounded 1–200 query limit. **Returns:** Owner-scoped live project page. **Work:** Calls `list_owned_projects` with `principal.id`, then `_paginated_dto`. Invalid cursor/limit returns 422.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-list-projects"></a>

#### Line-by-line execution

[Current source: lines 119–130](../../../../Backend/app/api/projects.py#L119-L130). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `principal` | `OnboardedPrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `session` | `SessionDep`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `cursor` | `Annotated[str \| None, Query()]`; default `None`; positional or keyword | Opaque page continuation token; null starts the first page. |
| `limit` | `Annotated[int, Query(ge=1, le=200)]`; default `50`; positional or keyword | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |

**Declared result:** `PaginatedResponse[ProjectDto]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 119 | @router.get("", response_model=PaginatedResponse[ProjectDto])
 120 | def list_projects(
 121 |     principal: OnboardedPrincipalDep,
 122 |     session: SessionDep,
 123 |     cursor: Annotated[str | None, Query()] = None,
 124 |     limit: Annotated[int, Query(ge=1, le=200)] = 50,
 125 | ) -> PaginatedResponse[ProjectDto]:
 126 |     """GET /projects -> paginated owner-scoped listing."""
 127 |     rows, next_cursor = list_owned_projects(
 128 |         session, user_id=principal.id, cursor=cursor, limit=limit
 129 |     )
 130 |     return _paginated_dto(rows, next_cursor)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L119 | Register the handler with FastAPI using `router.get('', response_model=PaginatedResponse[ProjectDto])`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L120 | Define `list_projects`; bind its arguments when called. The body executes only when invoked. |
| L121 | Declare parameter `principal` with annotation `OnboardedPrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L122 | Declare parameter `session` with annotation `SessionDep`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L123 | Declare parameter `cursor` with annotation `Annotated[str \| None, Query()]`. Opaque page continuation token; null starts the first page. |
| L124 | Declare parameter `limit` with annotation `Annotated[int, Query(ge=1, le=200)]`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. |
| L125 | Finish/continue the signature; the declared return annotation is `PaginatedResponse[ProjectDto]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L126 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L127 | Evaluate the right-hand side, then bind/store it in `(rows, next_cursor)`: `list_owned_projects(session, user_id=principal.id, cursor=cursor, limit=limit)` — Call [list_owned_projects](../repositories/projects.md#walk-list-owned-projects) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L128 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. Supply `cursor` = `cursor`. Opaque page continuation token; null starts the first page. Evaluate the value as: the current `cursor` value. Supply `limit` = `limit`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. Evaluate the value as: the current `limit` value. |
| L129 | Close the expression/container begun at L127; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L130 | Compute the return value: `_paginated_dto(rows, next_cursor)` — Call [_paginated_dto](#walk--paginated-dto) with the shown inputs; its own walkthrough describes the delegated branches, side effects, and result. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `create_project(payload, principal, session) -> ProjectDto`

**Route:** `POST /projects` (201). **Arguments:** `ProjectCreateRequest`, onboarded principal, session. **Returns:** Persisted project DTO. **Work:** Creates with the principal's owner ID, rolls back repository exceptions, commits, and converts the row. Client input cannot supply an owner.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-create-project"></a>

#### Line-by-line execution

[Current source: lines 133–151](../../../../Backend/app/api/projects.py#L133-L151). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `payload` | `ProjectCreateRequest`; required; positional or keyword | Input mapping, DTO, or provider response; the annotated type and body identify its expected shape. |
| `principal` | `OnboardedPrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `session` | `SessionDep`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |

**Declared result:** `ProjectDto`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 133 | @router.post("", response_model=ProjectDto, status_code=201)
 134 | def create_project(
 135 |     payload: ProjectCreateRequest,
 136 |     principal: OnboardedPrincipalDep,
 137 |     session: SessionDep,
 138 | ) -> ProjectDto:
 139 |     """POST /projects -> create (system stamps the internal owner)."""
 140 |     try:
 141 |         project = create_owned_project(
 142 |             session,
 143 |             user_id=principal.id,
 144 |             name=payload.name,
 145 |             description=payload.description,
 146 |         )
 147 |     except Exception:
 148 |         session.rollback()
 149 |         raise
 150 |     session.commit()
 151 |     return project_to_dto(project)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L133 | Register the handler with FastAPI using `router.post('', response_model=ProjectDto, status_code=201)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L134 | Define `create_project`; bind its arguments when called. The body executes only when invoked. |
| L135 | Declare parameter `payload` with annotation `ProjectCreateRequest`. Input mapping, DTO, or provider response; the annotated type and body identify its expected shape. |
| L136 | Declare parameter `principal` with annotation `OnboardedPrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L137 | Declare parameter `session` with annotation `SessionDep`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L138 | Finish/continue the signature; the declared return annotation is `ProjectDto`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L139 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L140 | Enter the protected block; failures are matched against `Exception` in order. |
| L141 | Evaluate the right-hand side, then bind/store it in `project`: `create_owned_project(session, user_id=principal.id, name=payload.name, description=payload.description)` — Call [create_owned_project](../repositories/projects.md#walk-create-owned-project) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L142 | Supply positional argument 1 to `create_owned_project`: the current `session` value. |
| L143 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. |
| L144 | Supply `name` = `payload.name`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: the `name` attribute of `payload`. |
| L145 | Supply `description` = `payload.description`. Optional project description; update logic distinguishes clearing it from leaving it unchanged. Evaluate the value as: the `description` attribute of `payload`. |
| L146 | Close the expression/container begun at L141; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L147 | Handle `Exception`; only a matching error from the associated try enters this body. |
| L148 | `session.rollback()` — Roll back the active transaction and discard its uncommitted database changes. The return value is not assigned here. |
| L149 | Re-raise the currently handled exception with its traceback; no replacement result is returned. |
| L150 | `session.commit()` — Flush pending changes and commit this transaction; subsequent failures cannot undo that completed transaction. The return value is not assigned here. |
| L151 | Compute the return value: `project_to_dto(project)` — Call [project_to_dto](../repositories/projects.md#walk-project-to-dto) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `read_project(project_id: UUID, principal, session) -> ProjectDto`

**Route:** `GET /projects/{project_id}` (200). **Arguments:** Path UUID, onboarded principal, session. **Returns:** Project DTO. **Work:** Performs `get_owned_project_or_404`, then conversion; foreign/missing/tombstoned IDs return 404.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-read-project"></a>

#### Line-by-line execution

[Current source: lines 154–164](../../../../Backend/app/api/projects.py#L154-L164). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project_id` | `UUID`; required; positional or keyword | Project UUID used to constrain resource lookup or provider metadata. |
| `principal` | `OnboardedPrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `session` | `SessionDep`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |

**Declared result:** `ProjectDto`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 154 | @router.get("/{project_id}", response_model=ProjectDto)
 155 | def read_project(
 156 |     project_id: UUID,
 157 |     principal: OnboardedPrincipalDep,
 158 |     session: SessionDep,
 159 | ) -> ProjectDto:
 160 |     """GET /projects/{id} -> owner-scoped read (404 if forged/foreign)."""
 161 |     project = get_owned_project_or_404(
 162 |         session, user_id=principal.id, project_id=project_id
 163 |     )
 164 |     return project_to_dto(project)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L154 | Register the handler with FastAPI using `router.get('/{project_id}', response_model=ProjectDto)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L155 | Define `read_project`; bind its arguments when called. The body executes only when invoked. |
| L156 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L157 | Declare parameter `principal` with annotation `OnboardedPrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L158 | Declare parameter `session` with annotation `SessionDep`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L159 | Finish/continue the signature; the declared return annotation is `ProjectDto`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L160 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L161 | Evaluate the right-hand side, then bind/store it in `project`: `get_owned_project_or_404(session, user_id=principal.id, project_id=project_id)` — Call [get_owned_project_or_404](../repositories/projects.md#walk-get-owned-project-or-404) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L162 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L163 | Close the expression/container begun at L161; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L164 | Compute the return value: `project_to_dto(project)` — Call [project_to_dto](../repositories/projects.md#walk-project-to-dto) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `update_project(project_id: UUID, payload, principal, session) -> ProjectDto`

**Route:** `PATCH /projects/{project_id}` (200). **Arguments:** Path ID, `ProjectUpdateRequest`, principal, session. **Returns:** Committed updated DTO. **Work:** Loads owned project; uses `model_fields_set` to reject empty patches while supporting description clearing; calls `update_owned_project`, rolls back mutation errors, commits, and converts. Explicit null names are rejected by the repository.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-update-project"></a>

#### Line-by-line execution

[Current source: lines 167–199](../../../../Backend/app/api/projects.py#L167-L199). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project_id` | `UUID`; required; positional or keyword | Project UUID used to constrain resource lookup or provider metadata. |
| `payload` | `ProjectUpdateRequest`; required; positional or keyword | Input mapping, DTO, or provider response; the annotated type and body identify its expected shape. |
| `principal` | `OnboardedPrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `session` | `SessionDep`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |

**Declared result:** `ProjectDto`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 167 | @router.patch("/{project_id}", response_model=ProjectDto)
 168 | def update_project(
 169 |     project_id: UUID,
 170 |     payload: ProjectUpdateRequest,
 171 |     principal: OnboardedPrincipalDep,
 172 |     session: SessionDep,
 173 | ) -> ProjectDto:
 174 |     """PATCH /projects/{id} -> rename / change description."""
 175 |     project = get_owned_project_or_404(
 176 |         session, user_id=principal.id, project_id=project_id
 177 |     )
 178 |     fields_set = set(payload.model_fields_set)
 179 |     if not fields_set:
 180 |         session.rollback()
 181 |         raise_api_error(
 182 |             422,
 183 |             ErrorCode.VALIDATION_ERROR,
 184 |             "Provide at least one field to update.",
 185 |             project_id=project_id,
 186 |         )
 187 |     try:
 188 |         project = update_owned_project(
 189 |             session,
 190 |             project,
 191 |             name=payload.name,
 192 |             description=payload.description,
 193 |             fields_set=fields_set,
 194 |         )
 195 |     except Exception:
 196 |         session.rollback()
 197 |         raise
 198 |     session.commit()
 199 |     return project_to_dto(project)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L167 | Register the handler with FastAPI using `router.patch('/{project_id}', response_model=ProjectDto)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L168 | Define `update_project`; bind its arguments when called. The body executes only when invoked. |
| L169 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L170 | Declare parameter `payload` with annotation `ProjectUpdateRequest`. Input mapping, DTO, or provider response; the annotated type and body identify its expected shape. |
| L171 | Declare parameter `principal` with annotation `OnboardedPrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L172 | Declare parameter `session` with annotation `SessionDep`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L173 | Finish/continue the signature; the declared return annotation is `ProjectDto`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L174 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L175 | Evaluate the right-hand side, then bind/store it in `project`: `get_owned_project_or_404(session, user_id=principal.id, project_id=project_id)` — Call [get_owned_project_or_404](../repositories/projects.md#walk-get-owned-project-or-404) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L176 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L177 | Close the expression/container begun at L175; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L178 | Evaluate the right-hand side, then bind/store it in `fields_set`: `set(payload.model_fields_set)` — Collect unique hashable items into a set. |
| L179 | Evaluate the branch condition: invert the truthiness of `fields_set`. If truthy, enter L180; otherwise skip this indented block and continue after it. |
| L180 | `session.rollback()` — Roll back the active transaction and discard its uncommitted database changes. The return value is not assigned here. |
| L181 | `raise_api_error(422, ErrorCode.VALIDATION_ERROR, 'Provide at least one field to update.', project_id=project_id)` — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L182 | Supply positional argument 1 to `raise_api_error`: `422`. |
| L183 | Supply positional argument 2 to `raise_api_error`: the `VALIDATION_ERROR` attribute of `ErrorCode`. |
| L184 | Supply positional argument 3 to `raise_api_error`: `'Provide at least one field to update.'`. |
| L185 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L186 | Close the expression/container begun at L181; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L187 | Enter the protected block; failures are matched against `Exception` in order. |
| L188 | Evaluate the right-hand side, then bind/store it in `project`: `update_owned_project(session, project, name=payload.name, description=payload.description, fields_set=fields_set)` — Call [update_owned_project](../repositories/projects.md#walk-update-owned-project) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L189 | Supply positional argument 1 to `update_owned_project`: the current `session` value. |
| L190 | Supply positional argument 2 to `update_owned_project`: the current `project` value. |
| L191 | Supply `name` = `payload.name`. Name/key supplied by the caller; the overview specifies whether this is a project, field, or environment-variable name. Evaluate the value as: the `name` attribute of `payload`. |
| L192 | Supply `description` = `payload.description`. Optional project description; update logic distinguishes clearing it from leaving it unchanged. Evaluate the value as: the `description` attribute of `payload`. |
| L193 | Supply `fields_set` = `fields_set`.  Evaluate the value as: the current `fields_set` value. |
| L194 | Close the expression/container begun at L188; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L195 | Handle `Exception`; only a matching error from the associated try enters this body. |
| L196 | `session.rollback()` — Roll back the active transaction and discard its uncommitted database changes. The return value is not assigned here. |
| L197 | Re-raise the currently handled exception with its traceback; no replacement result is returned. |
| L198 | `session.commit()` — Flush pending changes and commit this transaction; subsequent failures cannot undo that completed transaction. The return value is not assigned here. |
| L199 | Compute the return value: `project_to_dto(project)` — Call [project_to_dto](../repositories/projects.md#walk-project-to-dto) with the shown arguments; the linked walkthrough explains its validation, work, and return value. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->

### `delete_project(project_id: UUID, principal, session, job_queue) -> ProjectDeleteAccepted`

- **Route/arguments:** `DELETE /projects/{project_id}` (202); path UUID, onboarded principal, session, injected `DirectJobQueue`.
- **Returns:** `{projectId, accepted: true}` after committing coordinated tombstones/jobs.
- **Work:** Looks up ownership including deleted projects; absence is 404, already tombstoned is 409. Enumerates live documents. Resolves the storage bucket only when documents exist (missing configuration → 503 with rollback). For each document, sets its tombstone and enqueues cleanup, cancelling active processing; then tombstones the project. Rolls back mutation exceptions and commits the batch.
- **Boundary:** Provider deletion occurs later in the worker. This handler queues work and hides resources; it does not itself perform a final hard delete.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-delete-project"></a>

#### Line-by-line execution

[Current source: lines 202–276](../../../../Backend/app/api/projects.py#L202-L276). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `project_id` | `UUID`; required; positional or keyword | Project UUID used to constrain resource lookup or provider metadata. |
| `principal` | `OnboardedPrincipalDep`; required; positional or keyword | Verified internal-user identity; ownership checks derive their user UUID from this object. |
| `session` | `SessionDep`; required; positional or keyword | Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| `job_queue` | `Annotated[DirectJobQueue, Depends(get_job_queue)]`; required; positional or keyword | Caller-supplied job queue; each read, transformation, and validation is traced below. |

**Declared result:** `ProjectDeleteAccepted`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 202 | @router.delete("/{project_id}", response_model=ProjectDeleteAccepted, status_code=202)
 203 | def delete_project(
 204 |     project_id: UUID,
 205 |     principal: OnboardedPrincipalDep,
 206 |     session: SessionDep,
 207 |     job_queue: Annotated[DirectJobQueue, Depends(get_job_queue)],
 208 | ) -> ProjectDeleteAccepted:
 209 |     """DELETE /projects/{id} -> 202 while cleanup is pending.
 210 | 
 211 |     Tombstones the project (hidden from reads immediately), tombstones
 212 |     every live document, cancels their processing claims, and enqueues
 213 |     one ``delete_document`` cleanup job per document in the same
 214 |     transaction.  The hard delete (SQL cascades) happens only after
 215 |     every cleanup job succeeds (A4 worker).
 216 | 
 217 |     A second delete of an already-tombstoned project returns
 218 |     ``409 conflict`` (distinct from ``404`` for never-owned IDs).
 219 |     """
 220 |     from app.db.queries import get_owned_project as _query_project
 221 | 
 222 |     project_or_none = _query_project(
 223 |         session,
 224 |         user_id=principal.id,
 225 |         project_id=project_id,
 226 |         include_deleted=True,
 227 |     )
 228 |     if project_or_none is None:
 229 |         raise_api_error(
 230 |             404,
 231 |             ErrorCode.NOT_FOUND,
 232 |             "Project not found.",
 233 |             project_id=project_id,
 234 |         )
 235 |     if project_or_none.deleted_at is not None:
 236 |         session.rollback()
 237 |         raise_api_error(
 238 |             409,
 239 |             ErrorCode.CONFLICT,
 240 |             "Project is already being deleted.",
 241 |             project_id=project_id,
 242 |         )
 243 |     project = project_or_none
 244 | 
 245 |     documents = list_live_documents_for_project(session, project_id=project.id)
 246 |     bucket_id: str | None = None
 247 |     if documents:
 248 |         from app.services.storage import default_bucket_id
 249 | 
 250 |         try:
 251 |             bucket_id = default_bucket_id()
 252 |         except RuntimeError:
 253 |             session.rollback()
 254 |             raise_api_error(
 255 |                 503,
 256 |                 ErrorCode.SERVICE_UNAVAILABLE,
 257 |                 "Storage is not configured.",
 258 |                 project_id=project_id,
 259 |             )
 260 | 
 261 |     try:
 262 |         for document in documents:
 263 |             tombstone_document(session, document)
 264 |             # bucket_id is set whenever documents is non-empty.
 265 |             enqueue_document_delete(
 266 |                 session,
 267 |                 document=document,
 268 |                 bucket_id=bucket_id or "",
 269 |                 job_queue=job_queue,
 270 |             )
 271 |         tombstone_project(session, project)
 272 |     except Exception:
 273 |         session.rollback()
 274 |         raise
 275 |     session.commit()
 276 |     return ProjectDeleteAccepted(project_id=project.id, accepted=True)
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L202 | Register the handler with FastAPI using `router.delete('/{project_id}', response_model=ProjectDeleteAccepted, status_code=202)`; method/path, response validation, aliases, and status options are declaration-time metadata. |
| L203 | Define `delete_project`; bind its arguments when called. The body executes only when invoked. |
| L204 | Declare parameter `project_id` with annotation `UUID`. Project UUID used to constrain resource lookup or provider metadata. |
| L205 | Declare parameter `principal` with annotation `OnboardedPrincipalDep`. Verified internal-user identity; ownership checks derive their user UUID from this object. |
| L206 | Declare parameter `session` with annotation `SessionDep`. Open SQLAlchemy session for the caller's transaction; the function's flush/commit lines determine persistence. |
| L207 | Declare parameter `job_queue` with annotation `Annotated[DirectJobQueue, Depends(get_job_queue)]`. Caller-supplied job queue; its uses and transformations are traced below. |
| L208 | Finish/continue the signature; the declared return annotation is `ProjectDeleteAccepted`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L209 | Function docstring: descriptive metadata, not an executed processing step. The walkthrough follows the executable body when older wording differs. |
| L211 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L212 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L213 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L214 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L215 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L217 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L218 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L219 | Continuation of the function's docstring; no branch, assignment, or provider/database operation executes on this line. |
| L220 | Import `get_owned_project` as `_query_project` from `app.db.queries`; inside a function this import is deferred until this path is reached. |
| L222 | Evaluate the right-hand side, then bind/store it in `project_or_none`: `_query_project(session, user_id=principal.id, project_id=project_id, include_deleted=True)` — Call [_query_project](../db/queries.md#walk-get-owned-project) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L223 | Supply positional argument 1 to `_query_project`: the current `session` value. |
| L224 | Supply `user_id` = `principal.id`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. Evaluate the value as: the `id` attribute of `principal`. |
| L225 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L226 | Supply `include_deleted` = `True`. Internal switch allowing tombstoned rows in lookups; ordinary owned reads hide them. Evaluate the value as: `True`. |
| L227 | Close the expression/container begun at L222; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L228 | Evaluate the branch condition: compare whether `project_or_none` is the same object as `None`. If truthy, enter L229; otherwise skip this indented block and continue after it. |
| L229 | `raise_api_error(404, ErrorCode.NOT_FOUND, 'Project not found.', project_id=project_id)` — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L230 | Supply positional argument 1 to `raise_api_error`: `404`. |
| L231 | Supply positional argument 2 to `raise_api_error`: the `NOT_FOUND` attribute of `ErrorCode`. |
| L232 | Supply positional argument 3 to `raise_api_error`: `'Project not found.'`. |
| L233 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L234 | Close the expression/container begun at L229; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L235 | Evaluate the branch condition: compare whether `project_or_none.deleted_at` is not the same object as `None`. If truthy, enter L236; otherwise skip this indented block and continue after it. |
| L236 | `session.rollback()` — Roll back the active transaction and discard its uncommitted database changes. The return value is not assigned here. |
| L237 | `raise_api_error(409, ErrorCode.CONFLICT, 'Project is already being deleted.', project_id=project_id)` — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L238 | Supply positional argument 1 to `raise_api_error`: `409`. |
| L239 | Supply positional argument 2 to `raise_api_error`: the `CONFLICT` attribute of `ErrorCode`. |
| L240 | Supply positional argument 3 to `raise_api_error`: `'Project is already being deleted.'`. |
| L241 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L242 | Close the expression/container begun at L237; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L243 | Evaluate the right-hand side, then bind/store it in `project`: the current `project_or_none` value. |
| L245 | Evaluate the right-hand side, then bind/store it in `documents`: `list_live_documents_for_project(session, project_id=project.id)` — Call [list_live_documents_for_project](../repositories/documents.md#walk-list-live-documents-for-project) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L246 | Evaluate the right-hand side, then bind/store it in `bucket_id`: None (no value). |
| L247 | Evaluate the branch condition: the current `documents` value. If truthy, enter L248; otherwise skip this indented block and continue after it. |
| L248 | Import `default_bucket_id` from `app.services.storage`; inside a function this import is deferred until this path is reached. |
| L250 | Enter the protected block; failures are matched against `RuntimeError` in order. |
| L251 | Evaluate the right-hand side, then bind/store it in `bucket_id`: `default_bucket_id()` — Call [default_bucket_id](../services/storage.md#walk-default-bucket-id) with the shown arguments; the linked walkthrough explains its validation, work, and return value. |
| L252 | Handle `RuntimeError`; only a matching error from the associated try enters this body. |
| L253 | `session.rollback()` — Roll back the active transaction and discard its uncommitted database changes. The return value is not assigned here. |
| L254 | `raise_api_error(503, ErrorCode.SERVICE_UNAVAILABLE, 'Storage is not configured.', project_id=project_id)` — Call [raise_api_error](../repositories/projects.md#walk-raise-api-error) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L255 | Supply positional argument 1 to `raise_api_error`: `503`. |
| L256 | Supply positional argument 2 to `raise_api_error`: the `SERVICE_UNAVAILABLE` attribute of `ErrorCode`. |
| L257 | Supply positional argument 3 to `raise_api_error`: `'Storage is not configured.'`. |
| L258 | Supply `project_id` = `project_id`. Project UUID used to constrain resource lookup or provider metadata. Evaluate the value as: the current `project_id` value. |
| L259 | Close the expression/container begun at L254; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L261 | Enter the protected block; failures are matched against `Exception` in order. |
| L262 | Iterate `documents` (the current `documents` value), assigning each item to `document`. Execute the indented body once per item; an empty iterable skips it. |
| L263 | `tombstone_document(session, document)` — Call [tombstone_document](../repositories/documents.md#walk-tombstone-document) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L264 | Comment only: bucket_id is set whenever documents is non-empty.. It does not execute; the neighboring code determines behavior. |
| L265 | `enqueue_document_delete(session, document=document, bucket_id=bucket_id or '', job_queue=job_queue)` — Call [enqueue_document_delete](../repositories/documents.md#walk-enqueue-document-delete) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L266 | Supply positional argument 1 to `enqueue_document_delete`: the current `session` value. |
| L267 | Supply `document` = `document`.  Evaluate the value as: the current `document` value. |
| L268 | Supply `bucket_id` = `bucket_id or ''`. Appwrite bucket identifier. Evaluate the value as: evaluate `bucket_id or ''` left-to-right with short-circuit OR: use the first truthy operand, otherwise the last; the result is an operand value, not necessarily a bool. |
| L269 | Supply `job_queue` = `job_queue`.  Evaluate the value as: the current `job_queue` value. |
| L270 | Close the expression/container begun at L265; this delimiter adds no separate operation. The enclosing call/assignment uses the completed value. |
| L271 | `tombstone_project(session, project)` — Call [tombstone_project](../repositories/projects.md#walk-tombstone-project) with the shown arguments; the linked walkthrough explains its validation, work, and return value. The return value is not assigned here. |
| L272 | Handle `Exception`; only a matching error from the associated try enters this body. |
| L273 | `session.rollback()` — Roll back the active transaction and discard its uncommitted database changes. The return value is not assigned here. |
| L274 | Re-raise the currently handled exception with its traceback; no replacement result is returned. |
| L275 | `session.commit()` — Flush pending changes and commit this transaction; subsequent failures cannot undo that completed transaction. The return value is not assigned here. |
| L276 | Compute the return value: `ProjectDeleteAccepted(project_id=project.id, accepted=True)` — Construct `ProjectDeleteAccepted` with the shown fields; its class/model initialization rules apply. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
