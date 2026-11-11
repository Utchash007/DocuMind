"""RAG services: PDF extraction, embeddings, versioned indexing.

Retrieval contract: :mod:`app.rag.indexing` writes collection
``documind_chunks_v2`` with Chroma metadata keys ``user_id``,
``project_id``, ``document_id``, ``index_version``, ``source``,
``page``, ``chunk_id`` and deterministic chunk IDs of the form
``{document_id}:{index_version}:p{page}:c{index}``.  Embeddings are
provider-selectable: Hugging Face ``all-MiniLM-L6-v2`` (384-d) or
Jina AI (1024-d), computed in batches of 16 by
:class:`app.rag.embeddings.EmbeddingService`.

Everything here is synchronous and holds no database transaction:
providers (Hugging Face, Jina AI, Chroma) are called outside any open
transaction; callers persist results separately, fenced by the job
lease (see :mod:`app.jobs.queue`).
"""

from __future__ import annotations

from app.rag.embeddings import (
    EMBEDDING_DIM,
    EmbeddingProviderError,
    EmbeddingService,
    deterministic_fallback_embedding,
)
from app.rag.indexing import (
    CHROMA_METADATA_KEYS,
    COLLECTION_NAME,
    IndexService,
    IndexWriteError,
    build_metadata,
    chunk_id_for,
)
from app.rag.pdf import (
    MAX_CHUNK_TARGET,
    PdfError,
    PdfExtractionService,
    PdfFileTooLargeError,
    PdfMalformedError,
    PdfPageLimitError,
    PdfTextlessError,
    extract_pdf_chunks,
    split_into_sentences,
)

__all__ = [
    "CHROMA_METADATA_KEYS",
    "COLLECTION_NAME",
    "EMBEDDING_DIM",
    "EmbeddingProviderError",
    "EmbeddingService",
    "IndexService",
    "IndexWriteError",
    "MAX_CHUNK_TARGET",
    "PdfError",
    "PdfExtractionService",
    "PdfFileTooLargeError",
    "PdfMalformedError",
    "PdfPageLimitError",
    "PdfTextlessError",
    "build_metadata",
    "chunk_id_for",
    "deterministic_fallback_embedding",
    "extract_pdf_chunks",
    "split_into_sentences",
]
