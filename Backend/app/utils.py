import os
import re
import math
import hashlib
import random
from collections import Counter
import pypdf
import httpx

# Helper: Split text into sentences
def split_into_sentences(text: str) -> list[str]:
    # Simple regex split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

# PDF Processing: Extract text page-by-page
def process_pdf(pdf_path: str, filename: str) -> list[dict]:
    """
    Extracts text page-by-page from a PDF.
    Returns a list of chunks, where each chunk is strictly bound to its page.
    """
    chunks = []
    try:
        reader = pypdf.PdfReader(pdf_path)
        for page_idx, page in enumerate(reader.pages):
            page_num = page_idx + 1
            text = page.extract_text()
            if not text or not text.strip():
                continue
            
            # Clean text whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Chunking strategy: We can split a single page's text into small paragraphs or sentence blocks
            # if it's too long, but we keep them tied to the same page.
            # Let's group sentences into blocks of roughly 800 characters
            sentences = split_into_sentences(text)
            current_chunk = []
            current_len = 0
            chunk_sub_idx = 0
            
            for sentence in sentences:
                current_chunk.append(sentence)
                current_len += len(sentence)
                
                if current_len >= 800:
                    chunk_text = " ".join(current_chunk)
                    chunks.append({
                        "id": f"{filename}_p{page_num}_c{chunk_sub_idx}",
                        "text": chunk_text,
                        "metadata": {
                            "source": filename,
                            "page": page_num,
                            "chunk_id": f"{filename}_p{page_num}_c{chunk_sub_idx}"
                        }
                    })
                    current_chunk = []
                    current_len = 0
                    chunk_sub_idx += 1
            
            # Add any remaining sentences as a final chunk for the page
            if current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append({
                    "id": f"{filename}_p{page_num}_c{chunk_sub_idx}",
                    "text": chunk_text,
                    "metadata": {
                        "source": filename,
                        "page": page_num,
                        "chunk_id": f"{filename}_p{page_num}_c{chunk_sub_idx}"
                    }
                })
                
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
        
    return chunks

# Robust Fallback Embeddings
def get_fallback_embedding(text: str) -> list[float]:
    """
    Generates a deterministic pseudo-random embedding vector of dimension 384
    based on the hash of the input text. Used as a fallback if Hugging Face API is offline.
    """
    h = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
    rng = random.Random(h)
    # Generate 384 dimensional vector
    vector = [rng.uniform(-1.0, 1.0) for _ in range(384)]
    # Normalize vector to unit length
    magnitude = math.sqrt(sum(x*x for x in vector))
    if magnitude > 0:
        vector = [x / magnitude for x in vector]
    return vector

# Hugging Face Embeddings
def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings using Hugging Face Inference API.
    Falls back to deterministic mock embeddings if the network or API is down.
    """
    hf_token = os.getenv("HF_API_KEY") or os.getenv("HF_TOKEN")
    model_id = "sentence-transformers/all-MiniLM-L6-v2"
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
    
    headers = {}
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"
        
    try:
        response = httpx.post(
            api_url,
            headers=headers,
            json={"inputs": texts, "options": {"wait_for_model": True}},
            timeout=15.0
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"HF API returned status {response.status_code}: {response.text}. Using fallback.")
    except Exception as e:
        print(f"HF API network connection failed: {e}. Using fallback.")
        
    # Return fallbacks for each text
    return [get_fallback_embedding(text) for text in texts]

# BM25 Sparse Retriever
class BM25Retriever:
    def __init__(self, corpus: list[dict]):
        """
        corpus is a list of chunks: [{"id": ..., "text": ..., "metadata": ...}]
        """
        self.corpus = corpus
        self.corpus_size = len(corpus)
        self.avg_doc_len = sum(len(c["text"].split()) for c in corpus) / self.corpus_size if self.corpus_size > 0 else 1
        self.doc_freqs = []
        self.idf = {}
        self.doc_lens = []
        
        words_in_docs = []
        for chunk in corpus:
            words = chunk["text"].lower().split()
            self.doc_lens.append(len(words))
            self.doc_freqs.append(Counter(words))
            words_in_docs.append(set(words))
            
        all_words = set(w for doc in words_in_docs for w in doc)
        for word in all_words:
            doc_count = sum(1 for doc_words in words_in_docs if word in doc_words)
            # Standard BM25 IDF calculation
            self.idf[word] = math.log((self.corpus_size - doc_count + 0.5) / (doc_count + 0.5) + 1.0)
            
    def get_scores(self, query: str, k1=1.5, b=0.75) -> dict:
        """
        Returns a dictionary of {chunk_id: bm25_score}
        """
        query_words = query.lower().split()
        scores = {}
        for i, chunk in enumerate(self.corpus):
            score = 0.0
            doc_len = self.doc_lens[i]
            doc_freq = self.doc_freqs[i]
            for word in query_words:
                if word in doc_freq:
                    tf = doc_freq[word]
                    idf = self.idf.get(word, 0.0)
                    denom = tf + k1 * (1 - b + b * doc_len / self.avg_doc_len)
                    score += idf * tf * (k1 + 1) / denom
            scores[chunk["id"]] = score
        return scores

# Extract most relevant exact sentence from a text block
def extract_relevant_sentence(text_block: str, query: str) -> str:
    sentences = split_into_sentences(text_block)
    if not sentences:
        return text_block
        
    query_words = set(query.lower().split())
    best_sentence = sentences[0]
    best_score = -1.0
    
    for sentence in sentences:
        # Simple Jaccard similarity / overlap score
        words = set(sentence.lower().split())
        overlap = len(query_words.intersection(words))
        score = overlap / len(query_words) if query_words else 0
        if score > best_score:
            best_score = score
            best_sentence = sentence
            
    return best_sentence
