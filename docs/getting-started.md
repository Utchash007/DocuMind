# Run DocuMind locally

DocuMind runs as three processes: the NoteMind Next.js frontend, the FastAPI backend, and the PDF worker. All three need configuration before the upload-and-answer workflow can run.

Return to the [project overview](../README.md).

## Prerequisites

- Use **Node.js 24+ (64-bit)** with npm for this setup. Node.js 22.13+ on the 22.x line also meets the current frontend dependency and lint-tool engine requirements.
- Python **3.11+**, venv, and pip. The backend uses Python's `StrEnum`.
- A PostgreSQL database you intend to use for this application, with permission to apply its schema migrations.
- An Appwrite project, a private PDF bucket, and server API keys for authentication and storage operations.
- Chroma Cloud credentials, a Groq API key, and access to the selected embedding provider.

The examples below assume you have a local checkout. Start each independent command block from the directory stated above it.

## 1. Configure services

In Appwrite, enable **Email OTP** and register `localhost` as a **Web** platform. Register `127.0.0.1` separately if you use it. Configure the PDF bucket with file security enabled, no public read grants, `pdf` as its allowed extension, and a **25 MiB** maximum file size. The API and worker need access to that bucket. See [email-code authentication](../Frontend/README.md#appwrite-email-code-authentication) and the [storage adapter settings](backend/app/services/storage.md).

Create the local configuration files from the repository root.

**PowerShell:**

```powershell
if (-not (Test-Path .env)) { Copy-Item Backend/.env.example .env }
if (-not (Test-Path Frontend/.env.local)) { Copy-Item Frontend/.env.example Frontend/.env.local }
```

**macOS/Linux:**

```bash
test -f .env || cp Backend/.env.example .env
test -f Frontend/.env.local || cp Frontend/.env.example Frontend/.env.local
```

Fill in the files; if they already exist, merge the required settings.

| File | Settings |
| --- | --- |
| Repository-root `.env` | `DATABASE_URL`; `APPWRITE_ENDPOINT`, `APPWRITE_PROJECT_ID`, `APPWRITE_API_KEY`, `APPWRITE_STORAGE_BUCKET_ID`; `CHROMA_API_KEY`, `CHROMA_TENANT`, `CHROMA_DATABASE`; `GROQ_API_KEY` |
| Repository-root `.env` — embeddings | `DOCUMIND_EMBEDDING_PROVIDER=hf` (default), with `HF_API_KEY` or `HF_TOKEN` as the bearer token when needed; or `DOCUMIND_EMBEDDING_PROVIDER=jina` with `JINA_API_KEY` |
| `Frontend/.env.local` | `BACKEND_URL=http://127.0.0.1:8000`, `NEXT_PUBLIC_API_BASE_URL=/api/backend`, and server-only `APPWRITE_ENDPOINT`, `APPWRITE_PROJECT_ID`, `APPWRITE_API_KEY` |

Use the same Appwrite endpoint and project in both files. The endpoint includes `/v1`, for example `https://<REGION>.cloud.appwrite.io/v1`. Next.js needs its server auth key; the backend key needs its storage permissions. Keep credentials server-side: API keys must never use a `NEXT_PUBLIC_` prefix. Public endpoint/project fallback variables are optional when the server variables are set.

The API and worker load the repository-root `.env`; existing shell variables take precedence. Alembic reads `DATABASE_URL` from the shell instead. The backend examples also contain obsolete `ENABLE_LEGACY_API` and test-runner comments; v1 routes and project test runners are retired, and these settings do not restore them.

Embedding configuration is shared by the API and worker. Hugging Face uses `sentence-transformers/all-MiniLM-L6-v2` with 384-dimensional vectors. Jina uses `jina-embeddings-v5-text-small` with 1024-dimensional vectors; `JINA_EMBEDDING_MODEL` can override the Jina model. Keep the provider consistent with the existing index. Mock embeddings require `DOCUMIND_ALLOW_MOCK_EMBEDDINGS=true` and are for development only.

## 2. Install dependencies

From `Backend/`, create a virtual environment if needed and install the Python dependencies.

**PowerShell:**

```powershell
if (-not (Test-Path .venv)) { python -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS/Linux:**

```bash
test -d .venv || python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

From `Frontend/`, on either platform:

```bash
npm install
```

The application scripts and npm lockfile live in `Frontend/`. Run npm commands there; local-only root tooling is not required for the application.

## 3. Apply the database schema

From `Backend/`, set `DATABASE_URL` to the same application database configured in the root `.env`, replacing the example values below. Apply this only to the database you have chosen for this installation; Alembic changes its schema.

**PowerShell:**

```powershell
$env:DATABASE_URL="postgresql+psycopg://user:password@host:5432/documind"
.\.venv\Scripts\python.exe -m alembic upgrade head
```

**macOS/Linux:**

```bash
export DATABASE_URL='postgresql+psycopg://user:password@host:5432/documind'
.venv/bin/python -m alembic upgrade head
```

For migration details, see the [Alembic environment](backend/migrations/env.md) and [schema revision](backend/migrations/versions/a1v2init0001_v2_initial_schema.md).

## 4. Start the API, worker, and frontend

Keep each process running in its own terminal.

**Terminal 1 — API, from `Backend/`:**

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000 --reload
```

**Terminal 2 — PDF worker, from `Backend/`:**

```powershell
.\.venv\Scripts\python.exe -m app.workers.pdf_worker
```

On macOS/Linux, use `.venv/bin/python` in place of `.\.venv\Scripts\python.exe` in both commands. The API and worker must share the database and provider settings. Without a worker, accepted uploads remain pending.

**Terminal 3 — frontend, from `Frontend/`:**

```bash
npm run dev
```

Open [localhost:3000/sign-in](http://localhost:3000/sign-in), sign in with an email code, and complete your profile. Then follow the [first research session](../README.md#your-first-research-session).

The backend exposes [interactive docs](http://localhost:8000/docs), [ReDoc](http://localhost:8000/redoc), and [OpenAPI JSON](http://localhost:8000/openapi.json). These are direct-backend URLs; the Next.js `/api/backend` proxy does not expose the documentation routes.

## 4b. Run the same stack with containers

Instead of the three terminals, build the two images and start the stack from the repository root:

```powershell
docker compose build
docker compose run --rm backend alembic upgrade head
docker compose up -d
```

| Service | Address | Notes |
| --- | --- | --- |
| `frontend` | [localhost:3000](http://localhost:3000) | Only published port; the browser never talks to the API directly |
| `backend` | `http://backend:8000` | Reachable from the frontend over the internal network only |
| `worker` | none | Same image as the API, runs `python -m app.workers.pdf_worker` |
| `postgres` | `postgres:5432` | Optional, enabled with `--profile local-db` |

Configuration is read from the repository-root `.env`, so the same file drives the containers and the local processes. Server-only values are injected at runtime; `NEXT_PUBLIC_*` values are baked into the frontend image at build time, so rebuild the image after changing them.

To add New Relic, put the license key in the root `.env` and restart the stack:

```dotenv
NEW_RELIC_LICENSE_KEY=<your license key>
NEW_RELIC_ENVIRONMENT=development
```

The agents stay off while the key is empty. With a key set, the API, the worker, and the Next.js server report to New Relic, and the trace context is propagated across the internal proxy.

## Check startup and troubleshoot

Visit [localhost:8000/health](http://localhost:8000/health). It returns `status: "healthy"` plus configuration-presence flags. This is a liveness check, not a database or provider connectivity check; `CHROMA_HOST` affects only its Chroma flag. The actual Chroma Cloud connection uses the API key, tenant, and database.

| Symptom | Check |
| --- | --- |
| Sign-in is unavailable | Server Appwrite endpoint/project/key in `Frontend/.env.local`, Email OTP, and the registered browser hostname; restart Next.js after changing configuration |
| Workspace requests fail | FastAPI is running, `BACKEND_URL` points to it, both servers use the same Appwrite project, and the database schema is applied |
| A PDF stays pending | The worker is running with the same database, bucket, and provider settings as the API |
| A PDF is rejected | It contains extractable text and is within 25 MiB / 200 pages; scanned image-only PDFs need OCR outside this app |
| Indexing or answers fail | Worker/API logs and the configured embedding, Chroma, and Groq access; provider outages are surfaced rather than replaced with mock results |

The Next.js proxy buffers **26 MiB** for the 25 MiB multipart upload budget. A deployed ingress must allow that envelope. Worker limits cannot be configured below the API budgets; increasing them does not raise the API or bucket caps. Production also needs worker supervision and live verification of authentication, storage, database behavior, and providers.

For a production frontend build, run `npm run build` and then `npm run start` from `Frontend/`. This starts only Next.js; the API and worker are separate processes.

## Use the API directly

Workspace endpoints require a valid Appwrite session JWT, completed profile onboarding, and owned resource IDs. The browser normally uses the authenticated `/api/backend` proxy, which mints and forwards the JWT server-side. Direct clients send `Authorization: Bearer <JWT>` to FastAPI.

| Endpoint | Purpose |
| --- | --- |
| `GET/PATCH /me` | Read or complete the application profile |
| `GET/POST /projects` | List or create projects |
| `GET/PATCH/DELETE /projects/{projectId}` | Read, rename, or delete an owned project |
| `GET/POST /projects/{projectId}/documents` | List documents or upload a multipart `file`; upload returns `202 {document, job}` |
| `GET /projects/{projectId}/documents/{documentId}/file` | Read an owned PDF, including byte-range requests |
| `GET /jobs/{jobId}` | Read durable processing status |
| `GET/POST /projects/{projectId}/conversations` | List or create conversations |
| `GET/POST /projects/{projectId}/conversations/{conversationId}/messages` | List messages or submit a question |
| `POST /projects/{projectId}/conversations/{conversationId}/messages/{messageId}/retry` | Retry the latest failed or expired-active user turn; send `{}` or the matching `clientRequestId` |
| `POST /projects/{projectId}/conversations/{conversationId}/messages/{messageId}/cancel` | Cancel an active generation |

For this PowerShell example, supply a valid session JWT in `$env:APPWRITE_JWT` and existing owned IDs in `$env:PROJECT_ID` and `$env:CONVERSATION_ID`. These are example inputs, not application configuration settings. The project must have a ready document.

```powershell
$body = @{
    content = "What are the key findings?"
    clientRequestId = [guid]::NewGuid().ToString()
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
    -Uri "http://localhost:8000/projects/$env:PROJECT_ID/conversations/$env:CONVERSATION_ID/messages" `
    -Headers @{ Authorization = "Bearer $env:APPWRITE_JWT" } `
    -ContentType "application/json" -Body $body
```

On success, the response contains the persisted `userMessage` and `assistantMessage`. The answer depends on the PDFs; citations contain `documentId`, `fileName`, one-based `pageNumber`, `chunkId`, supporting `text`, and `indexVersion`. Questions accept 1–8000 characters. Reuse the same `clientRequestId` when resending the same request; completed duplicates replay their stored result. Cancelled turns require a new question.

Responses use camelCase; lists return `{items, nextCursor}`. Explicit backend errors use `detail` objects, validation errors use 422 detail arrays, and proxy/auth errors can use direct `{code, message}` objects. See the [message handlers](backend/app/api/messages.md), [document handlers](backend/app/api/documents.md), and [frontend API types](../Frontend/src/lib/api-types.ts) for the full surface and response shapes.

Filenames are labels, so same-name PDFs can coexist. Deletion hides resources immediately and queues file/index cleanup. Sign-out clears visible browser state without deleting saved data or cancelling every durable job. Removed `/files`, `/upload`, `/query`, and `/imports/legacy` APIs return 404. Old browser workspace data is not imported, and incomplete or unresolved citations are unsupported.
