# 🧠 DocuMind: AI-Powered Document Question Answering (Hybrid RAG)

![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwindcss&logoColor=white)
![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)

DocuMind is an AI-powered document query system that provides page-level citations and exact sentence references from uploaded PDF files, similar to NotebookLM. It uses a hybrid retrieval pipeline combining semantic vector search and keyword matching.


---

## 📁 Repository Structure

```text
DocuMind/
├── Frontend/           # Next.js (App Router, TypeScript, Tailwind CSS)
├── Backend/            # FastAPI (Python, Uvicorn)
├── .env                # Root environment variables (shared)
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

3. Start the Next.js development server:
   ```bash
   npm run dev
   ```

The frontend web app will be available at [http://localhost:3000](http://localhost:3000).

---

## 🛠️ Technology Stack

| Component | Technology | Badge |
| --- | --- | --- |
| **Frontend** | Next.js 15, Tailwind CSS, TypeScript | ![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=nextdotjs&logoColor=white) ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat-square&logo=tailwindcss&logoColor=white) ![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat-square&logo=typescript&logoColor=white) |
| **Backend** | FastAPI, Python 3, Uvicorn | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) |
| **LLMs / Orchestration** | Groq API, `instructor`, Pydantic | ![Groq](https://img.shields.io/badge/Groq-F55036?style=flat-square&logo=groq&logoColor=white) ![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white) |
| **Embeddings** | Hugging Face Inference API | ![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-FFD21E?style=flat-square) |
| **Vector DB** | Chroma DB (Hosted Database) | ![ChromaDB](https://img.shields.io/badge/ChromaDB-0078D4?style=flat-square) |

