# <img src="Frontend/src/app/icon.svg" alt="NoteMind logo" width="36" height="36"> DocuMind

A PDF research app that answers questions with supporting passages and links to the source pages.

![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwindcss&logoColor=white)
![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)

The web interface is called **NoteMind**. Sign in with an email code, organize PDFs into projects, ask questions across each project's sources, and keep your findings as notes or Markdown exports. **DocuMind** is the repository and backend API name.

> [!NOTE]
> **Development status:** the v2 workspace is implemented; live end-to-end and production deployment verification remain outstanding. Running it requires PostgreSQL and configured cloud services. A project license file is not currently included.

## Why DocuMind?

For developers who want to run and inspect a document-research application, DocuMind exposes the retrieval, citation, storage, and authentication code behind the workspace.

- **Trace answers to the PDF.** Citation passages and page numbers come from matched source text; click a citation to inspect the passage or open its PDF page.
- **Search by meaning and keywords.** Hybrid retrieval combines semantic search with BM25 keyword scoring, using only ready documents in the current account-owned project.
- **Keep research together.** Projects hold sources and multiple conversations. Save answers as editable notes, generate study guides, and export your work as Markdown.
- **Process PDFs in the background.** A separate worker handles indexing and retryable jobs; processing state is stored in PostgreSQL.

The trade-off is operating a frontend, API, worker, and external services. Uploads support PDFs with extractable text, up to **25 MiB and 200 pages**. OCR, other upload formats, and collaborative sharing are not implemented. Notes are saved on the current device; answers arrive as complete responses rather than a token stream.

## Get started

You'll need:

- **Node.js 24+ (64-bit)** with npm; **Python 3.11+** with venv and pip.
- **PostgreSQL** for application data and processing jobs.
- **Appwrite** for email-code authentication and private PDF storage.
- **Chroma Cloud**, **Groq**, and **Hugging Face or Jina AI** for retrieval and answers.

From the repository root in **PowerShell**, create the local configuration files if they don't exist:

```powershell
if (-not (Test-Path .env)) { Copy-Item Backend/.env.example .env }
if (-not (Test-Path Frontend/.env.local)) { Copy-Item Frontend/.env.example Frontend/.env.local }
```

**Continue with the [local setup guide](docs/getting-started.md)** to fill in credentials, install dependencies, migrate your chosen database, and start all three processes. It includes PowerShell and macOS/Linux commands. Application npm commands run from `Frontend/`.

Once running, open [localhost:3000](http://localhost:3000). Interactive API documentation is at [localhost:8000/docs](http://localhost:8000/docs).

## Your first research session

1. **Sign in** with the code sent to your email and complete your profile.
2. **Create a project** and upload a text-bearing PDF. Wait for its status to become **Ready**.
3. **Ask a question**, such as “What are the main findings, and which pages support them?”
4. **Inspect the citations** to read the supporting passages and open the original pages.
5. **Save a useful answer as a note**, or choose **Export** to copy or download Markdown.

Projects and conversations persist on the server. Editable notes and drafts use account-scoped browser storage and do not sync across devices; clearing browser data removes them.

## How it works

```text
NoteMind browser UI
    │
    ▼
Next.js ── Appwrite email sign-in and session cookie
    │ session-bound JWT through /api/backend
    ▼
FastAPI ── PostgreSQL: projects, documents, conversations, jobs
    │
    ├── Private PDFs ── Appwrite Storage
    ├── PDF worker ── page-bound text ── embeddings ── Chroma Cloud
    └── Questions ── hybrid retrieval ── Groq ── answer + citations
```

The API verifies identity and resource ownership. Uploads return a document and job; the worker publishes a versioned index before the document becomes ready. Both retrieval paths use the same authorized document/version pairs, combine their scores equally, and send the top four chunks to Groq. Conversation history supplies context; PDF text supplies citation evidence.

The default embedding model is Hugging Face's `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions); Jina AI is an alternative (1024 dimensions). Answer generation uses Groq's `openai/gpt-oss-120b` through Instructor. Provider failures surface as errors or retryable jobs; mock embeddings require explicit development opt-in.

Original PDFs live in Appwrite Storage, extracted text and vectors in Chroma, and retrieved passages are sent to the answer provider. See the [backend walkthrough](docs/backend/README.md#architecture-and-suggested-reading-order) for the implementation.

## Technology stack

| Layer | Technology | Logos |
| --- | --- | --- |
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS 4, shadcn/ui, Zustand | ![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=nextdotjs&logoColor=white) ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat-square&logo=tailwindcss&logoColor=white) ![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat-square&logo=typescript&logoColor=white) |
| **API** | FastAPI, Python, Uvicorn, Pydantic | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) |
| **Application data** | PostgreSQL, SQLAlchemy 2, Alembic, psycopg | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white) |
| **Authentication and files** | Appwrite Auth, private Appwrite Storage, server-side Node SDK | ![Appwrite](https://img.shields.io/badge/Appwrite-FD366E?style=flat-square&logo=appwrite&logoColor=white) |
| **Answers** | Groq API, Instructor, Pydantic | ![Groq](https://img.shields.io/badge/Groq-F55036?style=flat-square&logo=groq&logoColor=white) ![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white) |
| **Embeddings** | Hugging Face Inference API or Jina AI | ![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-FFD21E?style=flat-square) |
| **Vector search** | Chroma Cloud, combined with BM25 keyword retrieval | ![ChromaDB](https://img.shields.io/badge/ChromaDB-0078D4?style=flat-square) |

## Development and verification

From `Frontend/`:

```powershell
npm run lint
npm run build
npx tsc --noEmit --incremental false
```

Project tests, fixtures, and test runners were retired on **2026-11-11**. Current checks are frontend lint/type/build checks and backend syntax/reference validation. A fresh service-backed installation, PostgreSQL migration/concurrency/durability, live authentication/storage/model integrations, and worker supervision remain unverified.

The application is **v2-only**. Filename-based APIs, browser imports, and `/notebooks/[id]` compatibility routes have been removed. Old browser data is not read or automatically deleted, and unresolved legacy citations have no automatic repair path.

## Documentation and code map

The repository keeps `Backend/`, `Frontend/`, `docs/`, `README.md`, and `.gitignore` at the root. Other root files and folders are local-only and ignored by Git.

| Start here | What you'll find |
| --- | --- |
| [Local setup](docs/getting-started.md) | Service configuration, installation, startup, troubleshooting, and an API request example |
| [Frontend guide](Frontend/README.md) | Authentication, routes, interactions, state, and frontend verification |
| [Backend reference](docs/backend/README.md) | Per-file and per-function explanations with numbered Python source |
| [HTTP handlers](docs/backend/README.md#architecture-and-suggested-reading-order) and [TypeScript API types](Frontend/src/lib/api-types.ts) | Resource endpoints, response shapes, and ownership boundaries |
| [Frontend source](Frontend/src) and [backend source](Backend/app) | The Next.js interface and FastAPI/worker implementation |
| [UI styles](Frontend/src/app/globals.css) | NoteMind's theme tokens and shared styles |
