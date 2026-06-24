import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
    extract_relevant_sentence
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
    page: int = Field(description="The page number where this sentence was found in the document")

class AnswerResponse(BaseModel):
    answer: str = Field(description="The comprehensive answer generated using only the provided context. Must be grounded in the context.")
    citations: List[Citation] = Field(description="List of exact sentence citations with page numbers supporting the answer")

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
        files = [f.name for f in UPLOAD_DIR.glob("*.pdf")]
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Accepts PDF upload, parses text page-by-page, generates embeddings,
    and indexes chunks in Chroma hosted DB.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    file_path = UPLOAD_DIR / file.filename
    try:
        # Save file to local disk
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Parse PDF page-by-page
        chunks = process_pdf(str(file_path), file.filename)
        if not chunks:
            raise HTTPException(status_code=400, detail="No extractable text found in PDF.")
        
        # Get Chroma database collection
        collection = get_chroma_collection()
        
        # Clean any existing chunks for this specific document to prevent duplicates
        collection.delete(where={"source": file.filename})
        
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
            
        # Ingest into Chroma
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        return {
            "message": f"Successfully processed '{file.filename}'",
            "chunks_count": len(chunks)
        }
    except Exception as e:
        # Cleanup file if processing failed
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {str(e)}")

@app.post("/query", response_model=AnswerResponse)
async def query_document(query: str = Form(...), filename: Optional[str] = Form(None)):
    """
    Retrieves context using Hybrid RAG (Dense Chroma + Sparse BM25),
    then queries Groq using instructor for structured answers with citations.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable is missing.")
        
    try:
        collection = get_chroma_collection()
        
        # Fetch all document chunks matching source filter to build BM25 index
        # If no filename is specified, we query across all uploaded documents
        filter_dict = {"source": filename} if filename else {}
        all_data = collection.get(where=filter_dict)
        
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
            where=filter_dict
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
            text_content = chunk["text"]
            context_parts.append(f"[Document Chunk {rank+1} | Page {page_num}]: {text_content}")
            
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
                        "from the context and specify its page number. "
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
        for cit in structured_response.citations:
            # Find the best sentence match in the top chunks to make sure it's accurate
            exact_match = extract_relevant_sentence(context_text, cit.sentence)
            refined_citations.append(
                Citation(sentence=exact_match, page=cit.page)
            )
            
        return AnswerResponse(
            answer=structured_response.answer,
            citations=refined_citations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query answering failed: {str(e)}")
