# 🧠 DocuMind: AI-Powered Document Question Answering (Hybrid RAG)

![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwindcss&logoColor=white)
![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)

DocuMind is an AI-powered document query system that provides page-level citations and exact sentence references from uploaded PDF files, similar to NotebookLM. It uses a hybrid retrieval pipeline combining semantic vector search and keyword matching.

The **NoteMind** frontend organizes research into browser-saved notebooks, with required Appwrite email-code sign-in. Each notebook has its own PDF sources, conversation, editable notes, and Markdown export. It implements the [NoteMind UX wireframe](notemind-ux-wireframe.md) using shadcn/ui and the [Chalk theme](https://tweakcn.com/r/themes/cmmjgn9pc000404lg7c2q0fl6). See [Frontend/README.md](Frontend/README.md) for routes, architecture, and verification.

---

## 📁 Repository Structure

```text
DocuMind/
├── Frontend/           # NoteMind: Next.js, shadcn/ui, Zustand, and Playwright checks
├── Backend/            # FastAPI, PDF/retrieval utilities, and focused API checks
├── .env                # Backend provider configuration
├── .gitignore          # Git exclusion rules
└── README.md           # Project documentation
```

---

## ⚙️ Setup & Installation

### 1. Environment Configuration

Create a `.env` file in the root of the project (if not already present) with the following parameters:

```env
# Large Language Model Providers
GROQ_API_KEY="your_groq_api_key"

# Hosted Vector Database Setup (Chroma Cloud)
CHROMA_HOST="api.trychroma.com"
CHROMA_API_KEY="your_chroma_api_key"
CHROMA_TENANT="your_chroma_tenant_id"
CHROMA_DATABASE="Documind"

# Hugging Face API (For Embeddings)
HF_API_KEY="your_hugging_face_token"
```

---

### 2. Backend Setup (FastAPI)

1. Navigate to the `Backend` directory:
   ```bash
   cd Backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux**:
     ```bash
     source .venv/bin/activate
     ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Start the FastAPI development server:
   ```bash
   python -m uvicorn app.main:app --port 8000 --reload
   ```

The backend API will be available at [http://localhost:8000](http://localhost:8000). You can verify its status by visiting [http://localhost:8000/health](http://localhost:8000/health).

`/health` reports configuration presence, not provider connectivity. Chroma connections use the cloud API key, tenant, and database; `CHROMA_HOST` is a legacy health flag. Embeddings fall back to deterministic mock vectors when Hugging Face is unavailable, so that fallback does not establish semantic retrieval quality.

---

### 3. Frontend Setup (Next.js)

1. Navigate to the `Frontend` directory:
   ```bash
   cd Frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Copy `Frontend/.env.example` to `Frontend/.env.local`, or merge these settings into an existing file:
   ```env
   BACKEND_URL=http://127.0.0.1:8000
   NEXT_PUBLIC_API_BASE_URL=/api/backend
   NEXT_PUBLIC_APPWRITE_ENDPOINT=https://<REGION>.cloud.appwrite.io/v1
   NEXT_PUBLIC_APPWRITE_PROJECT_ID=your-project-id
   ```

4. Start the Next.js development server:
   ```bash
   npm run dev
   ```

The notebook library is available at [http://localhost:3000](http://localhost:3000) after email-code sign-in at [http://localhost:3000/sign-in](http://localhost:3000/sign-in). Library and notebook links redirect to sign-in when there is no authenticated account. Enable **Email OTP** and register the website hostname as a Web platform in Appwrite. Use the project’s actual endpoint and ID; both settings are required, are public, and require a rebuild when changed. No Appwrite API key is needed. See the [Appwrite setup guide](Frontend/README.md#appwrite-email-code-authentication). Application npm scripts run from `Frontend/`; the root npm manifest is for tooling.

Notebook organization, conversations, and notes live in browser local storage and are accessible in the workspace after signing in. Signing out closes access and cancels pending browser requests; saved data is preserved across account changes and sign-out. Notebooks do not sync across devices or become account-scoped. Appwrite manages account sessions; the FastAPI/proxy API and its PDFs remain deployment-wide without Appwrite authorization. PDFs and indexed chunks live on the backend, and **Share** exports Markdown rather than creating a collaborative link.

---

## API contract

FastAPI's interactive documentation is available at [localhost:8000/docs](http://localhost:8000/docs).

| Endpoint | Request | Response |
| --- | --- | --- |
| `GET /health` | None | Status and configuration-presence flags |
| `GET /files` | None | `{ "files": ["research.pdf"] }` |
| `GET /files/{filename}` | URL-encoded PDF filename; optional `Range` header | Original PDF served inline, with byte-range support |
| `POST /upload` | Multipart `file` containing a text-bearing PDF | `{ "message": "...", "chunks_count": 2 }` |
| `POST /query` | Form field `query`, and either `filename` or repeated `filenames` fields | Answer with sentence, page, and filename citations |

Example multi-source request from PowerShell:

```powershell
curl.exe http://localhost:8000/query -F "query=What are the key findings?" -F "filenames=research.pdf" -F "filenames=notes.pdf"
```

```json
{
  "answer": "The key findings are...",
  "citations": [
    { "sentence": "A supporting sentence from the source.", "page": 2, "filename": "research.pdf" }
  ]
}
```

Both retrieval paths use the selected source filter. The backend keeps legacy all-document queries when both filename fields are omitted; the notebook UI always sends its sources and prevents queries on empty notebooks. Page numbers are one-based, and citation metadata comes from the matched source chunk.

Filenames are source identities shared across this API deployment. Re-uploading a filename replaces its contents and removes stale chunks after indexing. Files are staged during processing, so rejected PDFs and embedding/indexing failures do not delete the existing PDF. Removing a notebook or its source association in the frontend does not delete backend files.

## Checks

From `Frontend/`, run `npm run lint`, `npx tsc --noEmit --incremental false`, and `npm run build`. After installing Chromium with `npx playwright install chromium`, run `npm run test:e2e` for authentication and notebook workflows. The runner builds with a local mocked Appwrite endpoint and uses an isolated PDF API fixture; see the [frontend verification guide](Frontend/README.md#verification). Rebuild with your own environment before serving a normal production build.

From `Backend/`, run `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` for source filtering, upload replacement/error behavior, PDF serving, and citation/page checks. The automated checks substitute external providers and do not validate live Groq, Chroma Cloud, or Hugging Face connectivity.

---

## 🛠️ Technology Stack

| Component | Technology | Badge |
| --- | --- | --- |
| **Frontend** | Next.js 16, React 19, Tailwind CSS 4, shadcn/ui, Zustand, TypeScript | ![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=nextdotjs&logoColor=white) ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat-square&logo=tailwindcss&logoColor=white) ![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat-square&logo=typescript&logoColor=white) |
| **Backend** | FastAPI, Python 3, Uvicorn | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) |
| **LLMs / Orchestration** | Groq API, `instructor`, Pydantic | ![Groq](https://img.shields.io/badge/Groq-F55036?style=flat-square&logo=groq&logoColor=white) ![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white) |
| **Embeddings** | Hugging Face Inference API | ![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-FFD21E?style=flat-square) |
| **Vector DB** | Chroma DB (Hosted Database) | ![ChromaDB](https://img.shields.io/badge/ChromaDB-0078D4?style=flat-square) |
