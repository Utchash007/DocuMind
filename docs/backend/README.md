# Backend Python reference

**53 Python files · 387 explicitly defined functions and methods.** This reference mirrors `Backend/` and describes the current implementation, including private helpers, nested functions, properties, protocol declarations, package initializers, and both migration files.

For example, `Backend/app/rag/generation.py` is documented in [app/rag/generation.md](app/rag/generation.md).

## How to read a page

Each page explains the module's role, its classes/data, and each function's arguments, result, operations, and error behavior. Each function also has:

1. A parameter table with the actual annotation, default, and positional/keyword binding.
2. A numbered copy of its source, linked to the corresponding Python file.
3. A **line-by-line execution table** covering every nonblank source line: expressions, arguments, conditions, loops, SQL/provider calls, returns, exceptions, and cleanup. Blank lines are visual separators; docstrings/comments are identified as descriptive rather than executable.

Line numbers refer to the source as reviewed on **2026-11-11**. Update the matching page when a Python implementation changes. Function overviews explain application intent; walkthroughs explain how the actual statements implement it. A class with only declared fields uses inherited or generated initialization, rather than an undocumented local constructor. `Protocol` methods ending in `...` specify adapter contracts and do not implement their operations. Anonymous lambdas/comprehensions are explained at their containing statement; named nested functions also have their own entries.

## Architecture and suggested reading order

| Layer | Start here | Responsibility |
| --- | --- | --- |
| Startup/configuration | [main](app/main.md), [config](app/config.md), [limits](app/limits.md) | Register routers, load shell-first settings, declare liveness and public PDF budgets |
| Authentication | [principal](app/auth/principal.md), [user repository](app/repositories/users.md) | Verify Appwrite JWTs and resolve internal account identity/onboarding |
| Data/contracts | [models](app/db/models.md), [session](app/db/session.md), [common DTOs](app/schemas/common.md), [service protocols](app/schemas/services.md) | PostgreSQL tables, short transactions, camelCase responses, provider boundaries |
| HTTP/resources | [projects](app/api/projects.md), [documents](app/api/documents.md), [conversations](app/api/conversations.md), [messages](app/api/messages.md) | Owned input validation, response conversion, and transaction orchestration |
| Private PDFs | [storage](app/services/storage.md), [PDF extraction](app/rag/pdf.md) | Private file permissions/ranges, complete bounded parsing and page-local chunks |
| Durable processing | [queue](app/jobs/queue.md), [processor](app/workers/processor.md), [reconciler](app/jobs/reconcile.md), [worker CLI](app/workers/pdf_worker.md) | Claims, leases, attempts, progress, publication, recovery, and cleanup |
| Answers/evidence | [retrieval](app/rag/retrieval.md), [text scoring](app/rag/text.md), [generation](app/rag/generation.md), [citations](app/rag/citations.md) | Exact authorized-pair hybrid retrieval, structured Groq answers, matched evidence |
| Schema deployment | [Alembic environment](migrations/env.md), [initial revision](migrations/versions/a1v2init0001_v2_initial_schema.md) | Migration configuration and six-table upgrade/downgrade |

### Sign-in and request ownership

Next.js owns email-code/session handling. It sends a session-minted Appwrite JWT to FastAPI. The principal resolver verifies that JWT, bootstraps/synchronizes the internal user in a short transaction, and returns an `AuthenticatedUser`. Workspace routes require onboarding. Resource queries constrain the internal user UUID through the project relationship; job reads use the job's immutable owner snapshot. Missing and inaccessible resources both produce 404 responses.

### PDF upload and worker processing

1. The document route checks ownership and validates/stages the PDF: extension/path, magic, nonempty bytes, **25 MiB**, **200 pages**, and complete extractable text.
2. A short transaction reserves an idempotent document and `awaiting_upload` job. Repeated keys return the same pair for matching content and conflict for different content.
3. Private Appwrite upload/inspection runs outside that transaction; finalization conditionally queues the job. `202` means accepted, not indexed.
4. The standalone worker reconciles old work, claims due jobs using row locks/`SKIP LOCKED`, advances the lease token/attempt, and allocates an index version.
5. A heartbeat renews the lease while the processor downloads, parses, embeds, and writes Chroma chunks into that version's namespace.
6. Queue completion checks publication conditions before updating document status and the active index pointer. Failed attempts retry with bounded backoff or become terminal. The detailed pages describe each guard and its limits.

### Conversation answers

1. Message POST claims a user turn using its `clientRequestId`; completed duplicates replay their stored result.
2. The repository captures exact live, completed `(documentId, indexVersion)` sources and bounded prior history, then closes its transactions before model work.
3. BM25 and dense Chroma retrieval use the same authorized pairs plus owner/project scope and recheck returned metadata. Scores combine normalized sparse relevance and `1/(1+distance)` dense similarity equally; the best four chunks become evidence.
4. Groq `openai/gpt-oss-120b` runs at temperature 0 through Instructor JSON mode. History is prompt context, not citation evidence.
5. Citation hints are matched back to retrieved text; persisted identity/page/source/version comes from the matched chunk. A guarded transaction persists the assistant result. Cancellation or obsolete claims prevent late answers from publishing.

### Deletion and recovery

Resource deletion tombstones rows immediately and queues private-file/index cleanup. Queue snapshots preserve cleanup references; the worker removes known versions and storage objects. Recovery passes inspect abandoned uploads, expire leases, cancel processing for deleted documents, and sweep eligible stale index namespaces after rechecking the active pointer. Provider cleanup and SQL state changes occur in separate operations.

## Implementation details to notice

These are documented observations of the current code:

- [Upload completion](app/api/documents.md) stores the inspection result in `inspected` but evaluates the earlier `info` object.
- [Resource snapshots](app/repositories/documents.md) use `file_size`/`content_sha256`; [job-context loading](app/jobs/queue.md) reads `expected_size_bytes`/`expected_sha256`. The [processor](app/workers/processor.md) does not substitute the live document hash into that expected-hash field.
- [Upload reconciliation](app/jobs/reconcile.md) treats a raised storage-not-found error as an inspection failure to revisit; a returned `None` follows a different path. Partial-file deletion failure is logged without enqueuing a durable retry.
- [Error formatting](app/jobs/errors.md) flattens/truncates exception text; it does not redact secrets.
- [Worker outcomes](app/workers/processor.md) can estimate `retry_wait` after a retryable exception even when the queue has exhausted attempts and recorded `failed`; the database state is authoritative.
- [Answer generation](app/rag/generation.md) accepts optional owner/project arguments without explicit validation there. Retrieval validates returned rows against the supplied scope; normal route callers provide verified IDs.

## Configuration and running

Use the existing backend virtual environment. Run from `Backend/`, in separate terminals:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000 --reload
```

```powershell
.\.venv\Scripts\python.exe -m app.workers.pdf_worker
```

| Settings | Consumer |
| --- | --- |
| `DATABASE_URL` | API/worker PostgreSQL sessions; Alembic reads shell configuration |
| `APPWRITE_ENDPOINT`, `APPWRITE_PROJECT_ID`, `APPWRITE_API_KEY`, `APPWRITE_STORAGE_BUCKET_ID` | Auth/private storage; see the respective factories for accepted aliases |
| `CHROMA_API_KEY`, `CHROMA_TENANT`, `CHROMA_DATABASE` | Chroma Cloud indexing/retrieval |
| `DOCUMIND_EMBEDDING_PROVIDER`, optional `HF_API_KEY`/`HF_TOKEN`, or `JINA_API_KEY` | HF 384-dimensional or Jina 1024-dimensional embeddings |
| `GROQ_API_KEY` | Structured answer generation |
| `DOCUMIND_ALLOW_MOCK_EMBEDDINGS` | Explicit deterministic-vector development mode |
| `DOCUMIND_WORKER_*` | Worker identity, concurrency, polling, leases, limits, timeout, backoff, and recovery timing; see [the worker](app/workers/pdf_worker.md) |
| `CORS_ORIGINS` | Explicit allowed frontend origins |

API/worker [environment loading](app/config.md) preserves existing shell values and excludes `TEST_DATABASE_URL`. The retained database-target helper and Alembic test-mode branch are configuration utilities; the project test runners and fixtures were removed. See [setup](../../README.md), [API contracts](../v2-contracts.md), and [current verification/history](../acceptance-matrix.md#current-integration-status).

## Complete mirrored file index

Counts include explicitly defined methods, property getters, nested functions, and protocol declarations. Generated/inherited constructors are described with their classes.

| Python file → mirrored reference | Functions / methods |
| --- | ---: |
| [app/api/__init__.py](app/api/__init__.md) | 0 |
| [app/api/conversations.py](app/api/conversations.md) | 8 |
| [app/api/documents.py](app/api/documents.md) | 13 |
| [app/api/messages.py](app/api/messages.md) | 9 |
| [app/api/projects.py](app/api/projects.md) | 9 |
| [app/api/users.py](app/api/users.md) | 2 |
| [app/auth/__init__.py](app/auth/__init__.md) | 2 |
| [app/auth/config.py](app/auth/config.md) | 3 |
| [app/auth/errors.py](app/auth/errors.md) | 7 |
| [app/auth/principal.py](app/auth/principal.md) | 7 |
| [app/config.py](app/config.md) | 1 |
| [app/db/__init__.py](app/db/__init__.md) | 0 |
| [app/db/base.py](app/db/base.md) | 4 |
| [app/db/models.py](app/db/models.md) | 1 |
| [app/db/queries.py](app/db/queries.md) | 5 |
| [app/db/session.py](app/db/session.md) | 10 |
| [app/jobs/__init__.py](app/jobs/__init__.md) | 0 |
| [app/jobs/errors.py](app/jobs/errors.md) | 5 |
| [app/jobs/ports.py](app/jobs/ports.md) | 12 |
| [app/jobs/queue.py](app/jobs/queue.md) | 41 |
| [app/jobs/reconcile.py](app/jobs/reconcile.md) | 13 |
| [app/limits.py](app/limits.md) | 0 |
| [app/main.py](app/main.md) | 2 |
| [app/rag/__init__.py](app/rag/__init__.md) | 0 |
| [app/rag/citations.py](app/rag/citations.md) | 1 |
| [app/rag/embeddings.py](app/rag/embeddings.md) | 15 |
| [app/rag/generation.py](app/rag/generation.md) | 3 |
| [app/rag/indexing.py](app/rag/indexing.md) | 12 |
| [app/rag/pdf.py](app/rag/pdf.md) | 6 |
| [app/rag/retrieval.py](app/rag/retrieval.md) | 8 |
| [app/rag/text.py](app/rag/text.md) | 4 |
| [app/repositories/__init__.py](app/repositories/__init__.md) | 0 |
| [app/repositories/conversations.py](app/repositories/conversations.md) | 11 |
| [app/repositories/documents.py](app/repositories/documents.md) | 24 |
| [app/repositories/messages.py](app/repositories/messages.md) | 24 |
| [app/repositories/projects.py](app/repositories/projects.md) | 12 |
| [app/repositories/users.py](app/repositories/users.md) | 7 |
| [app/schemas/__init__.py](app/schemas/__init__.md) | 0 |
| [app/schemas/common.py](app/schemas/common.md) | 4 |
| [app/schemas/conversations.py](app/schemas/conversations.md) | 3 |
| [app/schemas/documents.py](app/schemas/documents.md) | 0 |
| [app/schemas/jobs.py](app/schemas/jobs.md) | 1 |
| [app/schemas/messages.py](app/schemas/messages.md) | 1 |
| [app/schemas/projects.py](app/schemas/projects.md) | 6 |
| [app/schemas/services.py](app/schemas/services.md) | 20 |
| [app/schemas/users.py](app/schemas/users.md) | 3 |
| [app/services/__init__.py](app/services/__init__.md) | 0 |
| [app/services/storage.py](app/services/storage.md) | 32 |
| [app/workers/__init__.py](app/workers/__init__.md) | 0 |
| [app/workers/pdf_worker.py](app/workers/pdf_worker.md) | 11 |
| [app/workers/processor.py](app/workers/processor.md) | 19 |
| [migrations/env.py](migrations/env.md) | 4 |
| [migrations/versions/a1v2init0001_v2_initial_schema.py](migrations/versions/a1v2init0001_v2_initial_schema.md) | 2 |
