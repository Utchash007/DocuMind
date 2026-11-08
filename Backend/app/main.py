import os
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import chromadb
import instructor
from groq import Groq

# Import RAG utilities
from app.utils import (
    process_pdf, 
    get_embeddings_batch, 
    BM25Retriever, 
    match_citation_to_chunk
)

# Load env variables from the root directory (.env is in d:\AI_Projects\Documind)
root_dir = Path(__file__).resolve().parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(dotenv_path=env_path)

# Setup folders
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="DocuMind Backend", version="1.0.0")

# CORS middleware to allow Frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to Frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to Chroma hosted instance using verified settings
def get_chroma_collection():
    api_key = os.getenv("CHROMA_API_KEY")
    tenant = os.getenv("CHROMA_TENANT")
    database = os.getenv("CHROMA_DATABASE")
    
    client = chromadb.CloudClient(
        api_key=api_key,
        tenant=tenant,
        database=database
    )
    return client.get_or_create_collection(name="documind_chunks")

# Define Response Schema for Instructor / Pydantic
class Citation(BaseModel):
    sentence: str = Field(description="The exact sentence or short phrase from the context that supports the answer")
    page: int = Field(ge=1, description="The page number where this sentence was found in the document")
    filename: str | None = Field(default=None, description="The exact source filename for this citation")

class AnswerResponse(BaseModel):
    answer: str = Field(description="The comprehensive answer generated using only the provided context. Must be grounded in the context.")
    citations: List[Citation] = Field(description="List of exact sentence citations with page numbers supporting the answer")

class UploadResponse(BaseModel):
    message: str
    chunks_count: int = Field(ge=1)

@app.get("/")
def read_root():
    return {"message": "Welcome to DocuMind API"}

@app.get("/health")
def health_check():
    groq_key = os.getenv("GROQ_API_KEY")
    chroma_host = os.getenv("CHROMA_HOST")
    return {
        "status": "healthy",
        "config": {
            "groq_api_key_loaded": bool(groq_key),
            "chroma_host_loaded": bool(chroma_host)
        }
    }

@app.get("/files")
def list_files():
    """
    Returns list of processed files stored in the upload directory.
    """
    try:
        files = sorted(f.name for f in UPLOAD_DIR.iterdir() if f.is_file() and f.suffix.lower() == ".pdf")
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

def pdf_path(filename: str) -> Path:
    if not filename or any(character in filename for character in ("/", "\\", ":", "\x00")) or Path(filename).name != filename:
        raise HTTPException(status_code=400, detail="Invalid PDF filename.")
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    path = (UPLOAD_DIR / filename).resolve()
    if path.parent != UPLOAD_DIR.resolve():
        raise HTTPException(status_code=400, detail="Invalid PDF filename.")
    return path


@app.get("/files/{filename}")
def read_file(filename: str) -> FileResponse:
    path = pdf_path(filename)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="This PDF is no longer available.")
    return FileResponse(path, media_type="application/pdf", filename=filename, content_disposition_type="inline")


@app.post("/upload")
def upload_file(file: Annotated[UploadFile, File()]) -> UploadResponse:
    """
    Accepts PDF upload, parses text page-by-page, generates embeddings,
    and indexes chunks in Chroma hosted DB.
    """
    filename = file.filename or ""
    file_path = pdf_path(filename)
    staged_path = None
    try:
        with NamedTemporaryFile(dir=UPLOAD_DIR, suffix=".upload", delete=False) as buffer:
            staged_path = Path(buffer.name)
            shutil.copyfileobj(file.file, buffer)
            
        # Parse PDF page-by-page
        chunks = process_pdf(str(staged_path), filename)
        if not chunks:
            raise HTTPException(status_code=400, detail="No extractable text found in PDF.")
        
        # Prepare data for vector database
        ids = [c["id"] for c in chunks]
        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        
        # Generate embeddings in batches of 16 to respect Hugging Face limits
        embeddings = []
        batch_size = 16
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_embs = get_embeddings_batch(batch_texts)
            embeddings.extend(batch_embs)
            
        collection = get_chroma_collection()
        previous_ids = set(collection.get(where={"source": filename}, include=[])["ids"])
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        stale_ids = previous_ids.difference(ids)
        if stale_ids:
            collection.delete(ids=sorted(stale_ids))
        staged_path.replace(file_path)

        return UploadResponse(
            message=f"Successfully processed '{filename}'",
            chunks_count=len(chunks),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {str(e)}")
    finally:
        if staged_path is not None:
            staged_path.unlink(missing_ok=True)

@app.post("/query", response_model=AnswerResponse)
def query_document(
    query: Annotated[str, Form(min_length=1, max_length=8000)],
    filename: Annotated[str | None, Form()] = None,
    filenames: Annotated[list[str] | None, Form()] = None,
) -> AnswerResponse:
    """
    Retrieves context using Hybrid RAG (Dense Chroma + Sparse BM25),
    then queries Groq using instructor for structured answers with citations.
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Enter a question about your sources.")
    if filename is not None and filenames is not None:
        raise HTTPException(status_code=400, detail="Use either filename or filenames, not both.")
    sources = list(dict.fromkeys(filenames if filenames is not None else ([filename] if filename is not None else [])))
    if filenames is not None and not sources:
        raise HTTPException(status_code=400, detail="Select at least one source.")
    for source in sources:
        pdf_path(source)

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable is missing.")
        
    try:
        collection = get_chroma_collection()
        
        # Fetch all document chunks matching source filter to build BM25 index
        # If no filename is specified, we query across all uploaded documents
        filter_dict = {"source": sources[0]} if len(sources) == 1 else ({"source": {"$in": sources}} if sources else None)
        filter_args = {"where": filter_dict} if filter_dict else {}
        all_data = collection.get(**filter_args)
        
        if not all_data or not all_data["ids"]:
            raise HTTPException(status_code=400, detail="No documents indexed yet. Please upload a PDF first.")
            
        corpus = []
        for i in range(len(all_data["ids"])):
            corpus.append({
                "id": all_data["ids"][i],
                "text": all_data["documents"][i],
                "metadata": all_data["metadatas"][i]
            })
            
        # 1. Sparse Retrieval (BM25)
        bm25 = BM25Retriever(corpus)
        bm25_scores = bm25.get_scores(query)
        
        # 2. Dense Retrieval (Chroma Vector Search)
        query_vector = get_embeddings_batch([query])[0]
        
        # Search top-10 candidates
        vector_results = collection.query(
            query_embeddings=[query_vector],
            n_results=min(10, len(corpus)),
            **filter_args
        )
        
        # Map dense similarity scores
        dense_scores = {}
        if vector_results and vector_results["ids"]:
            ids = vector_results["ids"][0]
            distances = vector_results["distances"][0]
            for idx, dist in zip(ids, distances):
                # Convert distance (L2 or cosine) to positive similarity
                sim = 1.0 / (1.0 + dist)
                dense_scores[idx] = sim
                
        # 3. Hybrid Merger (Combine scores)
        max_bm25 = max(bm25_scores.values()) if bm25_scores else 1.0
        
        hybrid_scores = []
        for chunk in corpus:
            c_id = chunk["id"]
            dense_sim = dense_scores.get(c_id, 0.0)
            sparse_sim = bm25_scores.get(c_id, 0.0) / max_bm25 if max_bm25 > 0 else 0.0
            
            # Equal weight combination
            combined_score = 0.5 * dense_sim + 0.5 * sparse_sim
            hybrid_scores.append((chunk, combined_score))
            
        # Sort by combined score descending
        hybrid_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select top-4 chunks for context
        top_candidates = hybrid_scores[:4]
        
        # Build prompt context and reference mapper
        context_parts = []
        for rank, (chunk, score) in enumerate(top_candidates):
            page_num = chunk["metadata"]["page"]
            source = chunk["metadata"]["source"]
            text_content = chunk["text"]
            context_parts.append(f"[Document Chunk {rank+1} | Source: {source} | Page {page_num}]: {text_content}")
            
        context_text = "\n\n".join(context_parts)
        
        # Initialize Groq client with instructor wrapper
        groq_client = Groq(api_key=groq_api_key)
        instructor_client = instructor.from_groq(groq_client)
        
        # Create LLM structured completion
        # Use llama-3.1-8b-instant as it is fast, active, and supported on Groq
        structured_response = instructor_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            response_model=AnswerResponse,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a meticulous, document-answering assistant. "
                        "Answer the user's question using ONLY the provided document chunks as context. "
                        "For every statement or fact you write, extract the exact supporting sentence "
                        "from the context and specify its page number and exact source filename. "
                        "Do not make up facts or use external knowledge."
                    )
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context_text}\n\nQuestion: {query}"
                }
            ],
            temperature=0.0
        )
        
        # Double check and match exact supporting sentences inside references
        refined_citations = []
        candidate_chunks = [chunk for chunk, _score in top_candidates]
        for cit in structured_response.citations:
            # Find the best sentence match in the top chunks to make sure it's accurate
            match = match_citation_to_chunk(
                candidate_chunks, cit.sentence, cit.filename, cit.page
            )
            if match is not None:
                chunk, exact_match = match
                refined_citations.append(Citation(
                    sentence=exact_match,
                    page=chunk["metadata"]["page"],
                    filename=chunk["metadata"]["source"],
                ))
            
        return AnswerResponse(
            answer=structured_response.answer,
            citations=refined_citations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query answering failed: {str(e)}")
