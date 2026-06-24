# 📚 DocuMind: AI-Powered Document Question Answering System (Hybrid RAG)

## 🧠 Project Overview

DocuMind is an AI-powered application designed to answer user queries based on uploaded documents (e.g., PDFs). The system uses a **Hybrid Retrieval-Augmented Generation (RAG)** approach to generate accurate, context-aware answers with **exact sentence references and page numbers**, similar to modern tools like NotebookLM.

The architecture combines **Hugging Face embeddings (API-based)** with **OpenAI LLMs** for answer generation.

---
## Github link
-  empty repo: https://github.com/Utchash007/DocuMind

## 🎯 Key Features

* 📄 PDF upload and cloud storage
* 🔍 Hybrid retrieval (semantic + keyword search)
* 📌 Page-level citation tracking
* ✨ Exact sentence extraction
* 💬 Chat-based query system
* 🌐 Next.js frontend
* ⚡ Fast and modular backend

---

## 🏗️ System Architecture

### 🔄 Workflow

1. User uploads PDF via frontend
2. Backend stores file in cloud storage
3. PDF processed page-by-page
4. Text chunked with metadata (page number)
5. Embeddings generated via Hugging Face API
6. Stored in vector database
7. User submits query
8. Hybrid retrieval (dense + BM25)
9. OpenAI LLM generates answer with references
10. Frontend displays result

---

## 🧠 RAG Technique

### Hybrid RAG (Dense + Sparse Retrieval)

#### 🔹 Dense Retrieval

* Embeddings generated using Hugging Face API
* Semantic similarity search

#### 🔹 Sparse Retrieval

* BM25 keyword matching

#### 🔹 Combined Retrieval

* Merge both results for better accuracy

#### 🔹 Future Enhancement

* Re-ranking using cross-encoder

---

## 🧠 Embeddings

### Hugging Face Inference API

Model:

* `sentence-transformers/all-MiniLM-L6-v2`

### Purpose:

* Convert document chunks into vector embeddings
* Convert user queries into embeddings

---

## 🤖 LLM (Answer Generation)

Using OpenAI SDK:

* Model: `gpt-4o-mini`

### Role:

* Generate final answers from retrieved context
* Ensure grounded responses

---

## 🗄️ Database Design

### 📌 Vector Database

* Chroma DB

Stores:

* Embeddings
* Text chunks
* Metadata:

  * page number
  * chunk ID
  * file reference

---

### 📌 Metadata Database (Optional)

* PostgreSQL (via Supabase)

Stores:

* User data
* File info
* Query logs

---

## 📂 File Storage

### ☁️ Cloud Storage

* Supabase Storage (Free tier)

Stores:

* Uploaded PDF files
* File URLs

---

## 🔍 Retrieval Pipeline

1. Convert query → embedding (Hugging Face API)
2. Perform:

   * Vector search (Chroma)
   * BM25 keyword search
3. Merge results (Hybrid Retrieval)
4. Select top-k chunks
5. Extract most relevant sentence
6. Send context to OpenAI
7. Generate answer + references

---

## ✂️ Chunking Strategy

* Chunking is strictly **page-based**
* No chunk crosses page boundaries

### Each chunk contains:

* Text
* Page number
* Chunk ID
* File reference

---

## 🧾 Output Format

```text
Answer:
<Generated answer>

References:
1. "Exact sentence..." (Page X)
2. "Exact sentence..." (Page Y)
```

---

## ⚙️ Tech Stack

### 🧩 Backend

* Django
* Django REST Framework

### 🌐 Frontend

* Next.js
* Tailwind CSS
* Axios / Fetch API

---

### 🧠 AI / NLP

#### 🔹 Embeddings

* Hugging Face Inference API
* Model: `all-MiniLM-L6-v2`

#### 🔹 LLM

* OpenAI SDK
* Model: `gpt-4o-mini`

---

### 🔍 Retrieval

* Hybrid RAG (Dense + BM25)

---

### 🗄️ Vector Database

* Chroma DB

---

### 📂 File Storage

* Supabase Storage (Free tier)

---

### 🧠 Optional Framework

* LlamaIndex (optional for pipeline management)

---

## 🖥️ Frontend Features (Next.js)

* 📤 PDF upload UI
* 💬 Chat interface
* 📄 Answer display with citations
* 🔗 Clickable references (future)
* 📱 Responsive UI

---

## 🚀 Future Improvements

* 🔁 Re-ranking with cross-encoder
* 📊 Multi-document querying
* 🧠 Chat memory
* 📍 PDF highlighting system
* 🔐 Authentication system
* ☁️ Scalable deployment

---

## ⚠️ Limitations

* FastAPI Face API rate limits
* Free-tier storage limits (Supabase)
* Not optimized for large-scale usage yet

---

## 🏁 Conclusion

DocuMind demonstrates a practical Hybrid RAG system combining **Hugging Face embeddings + OpenAI LLMs** with a modern full-stack architecture (FastAPI + Next.js). It provides accurate, explainable answers with page-level citations, making it ideal for document-based AI systems.

---
