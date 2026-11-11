"""Scoped hybrid retrieval from exact authorized document/version pairs.

Retrieval is the only evidence path for answers: conversation history
is context, retrieved PDF text is evidence (``plan.md`` section 5.3).
Both the BM25 corpus load and the dense Chroma query filter by
internal user, project, and the *exact* permitted
``(document_id, index_version)`` pairs — independent document/version
lists must never admit a wrong pairing.  Every returned chunk is
re-validated against the same pairs (defense in depth, so a matcher
that ignores filters cannot leak data).

Hybrid scoring:

* sparse score = BM25 score divided by the maximum BM25 score,
* dense similarity = ``1 / (1 + distance)``,
* combined score = ``0.5 * dense + 0.5 * sparse``,
* best 4 chunks become the generation context.

Collection: ``documind_chunks_v2``. Canonical chunk metadata (written by the
worker): ``user_id``, ``project_id``, ``document_id``,
``index_version``, ``source``, ``page``, ``chunk_id`` (the seven keys
in ``app.rag.indexing.CHROMA_METADATA_KEYS``), string UUIDs, 1-based
``page`` ints, deterministic IDs
``{document_id}:{index_version}:p{page}:c{n}``.

Exact-pair filters use ``app.rag.indexing.version_where`` and embeddings
use ``EmbeddingService.embed_texts``. Provider failures raise; mock vectors
require explicit development/test opt-in. Sparse scoring uses ``app.rag.text``.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.schemas.services import AuthorizedSource
from app.rag.indexing import version_where
from app.rag.text import BM25Retriever

TARGET_COLLECTION = "documind_chunks_v2"
BEST_N = 4
DENSE_CANDIDATES = 10
Embedder = Callable[[Sequence[str]], list[list[float]]]


class NoReadySourcesError(Exception):
    """No authorized sources were supplied (``409 no_ready_sources``)."""


class IndexUnavailableError(Exception):
    """Authorized sources exist but no chunks could be retrieved (``503``)."""


@dataclass(frozen=True)
class RetrievedChunk:
    """One retrievable chunk from the scoped corpus (immutable)."""

    chunk_id: str
    text: str
    page_number: int
    source: str
    document_id: UUID
    index_version: UUID
    user_id: UUID
    project_id: UUID


def get_chroma_collection():
    """Resolve the canonical v2 collection lazily; tests inject a double."""
    from app.rag.indexing import default_chroma_collection

    return default_chroma_collection()


def default_embedder(texts: Sequence[str]) -> list[list[float]]:
    """Embed queries with the configured provider, without silent fallback."""
    from app.rag.embeddings import (
        TASK_RETRIEVAL_QUERY,
        EmbeddingConfig,
        EmbeddingService,
    )

    return EmbeddingService(EmbeddingConfig.from_env()).embed_texts(
        list(texts), task=TASK_RETRIEVAL_QUERY
    )


def build_retrieval_where(
    *,
    user_id: UUID,
    project_id: UUID,
    authorized_sources: Sequence[AuthorizedSource],
) -> dict[str, Any]:
    """Build the Chroma ``where`` filter for an exact authorized pair set.

    Each permitted pair compiles to one ``$and`` clause (via
    :func:`version_where` — document and version correlated per
    clause, never emitted as independent lists); several pairs compile
    to an ``$or`` of those clauses.
    """
    pairs = sorted(
        {(str(source.document_id), str(source.index_version)) for source in authorized_sources}
    )
    if not pairs:
        raise NoReadySourcesError(
            "No completed documents are available to answer this question."
        )
    clauses = [
        version_where(
            user_id=user_id,
            project_id=project_id,
            document_id=document_id,
            index_version=index_version,
        )
        for document_id, index_version in pairs
    ]
    return clauses[0] if len(clauses) == 1 else {"$or": clauses}


def _chunk_from_row(
    *,
    chunk_id: str | None,
    text: str | None,
    metadata: dict[str, Any] | None,
    allowed_pairs: set[tuple[UUID, UUID]],
    user_id: UUID,
    project_id: UUID,
) -> RetrievedChunk | None:
    """Validate one corpus row against the authorized pairs.

    Returns ``None`` for rows with missing metadata or for rows outside
    the authorized (document, version) pairs — including cross-pairings
    (a document paired with another document's version) and foreign
    user/project rows that a broken filter might admit.
    """
    if not chunk_id or not text or not metadata:
        return None
    try:
        row_user = UUID(str(metadata["user_id"]))
        row_project = UUID(str(metadata["project_id"]))
        row_document = UUID(str(metadata["document_id"]))
        row_version = UUID(str(metadata["index_version"]))
        page_number = int(metadata["page"])
        source = str(metadata["source"])
        metadata_chunk_id = str(metadata["chunk_id"])
    except (KeyError, TypeError, ValueError):
        return None
    if row_user != user_id or row_project != project_id:
        return None
    if (row_document, row_version) not in allowed_pairs:
        return None
    if not source or not metadata_chunk_id or page_number < 1:
        return None
    return RetrievedChunk(
        chunk_id=metadata_chunk_id,
        text=text,
        page_number=page_number,
        source=source,
        document_id=row_document,
        index_version=row_version,
        user_id=row_user,
        project_id=row_project,
    )


def merge_hybrid_scores(
    *,
    chunks: Sequence[RetrievedChunk],
    bm25_scores: dict[str, float],
    dense_scores: dict[str, float],
) -> list[tuple[RetrievedChunk, float]]:
    """Rank chunks with the preserved 0.5/0.5 hybrid merger (best first).

    ``bm25_scores`` are normalized by their maximum (zero when the
    maximum is not positive); ``dense_scores`` carry the
    ``1 / (1 + distance)`` similarity (missing candidates score zero).
    """
    max_bm25 = max(bm25_scores.values()) if bm25_scores else 1.0
    scored: list[tuple[RetrievedChunk, float]] = []
    for chunk in chunks:
        dense_sim = dense_scores.get(chunk.chunk_id, 0.0)
        sparse_sim = (
            bm25_scores.get(chunk.chunk_id, 0.0) / max_bm25 if max_bm25 > 0 else 0.0
        )
        combined = 0.5 * dense_sim + 0.5 * sparse_sim
        scored.append((chunk, combined))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored


def _is_embedding_provider_error(exc: BaseException) -> bool:
    """True when ``exc`` is A4's embedding-provider failure type."""
    try:
        from app.rag.embeddings import EmbeddingProviderError
    except ImportError:
        return False
    return isinstance(exc, EmbeddingProviderError)


def _embed_query(embedder: Embedder, question: str) -> list[float]:
    """Embed the query, mapping provider outages to 503 (retryable)."""
    try:
        return embedder([question])[0]
    except Exception as exc:
        if _is_embedding_provider_error(exc):
            raise IndexUnavailableError(
                f"embedding provider unavailable: {exc}"
            ) from exc
        raise


def retrieve_context(
    *,
    question: str,
    user_id: UUID,
    project_id: UUID,
    authorized_sources: Sequence[AuthorizedSource],
    collection: Any | None = None,
    embedder: Embedder | None = None,
    best_n: int = BEST_N,
) -> list[RetrievedChunk]:
    """Retrieve the best ``best_n`` chunks from authorized sources.

    Both branches (BM25 corpus load and dense query) use the identical
    exact-pair filter from :func:`build_retrieval_where`, and every
    corpus row is re-validated against the authorized pairs before
    scoring.
    """
    if not authorized_sources:
        raise NoReadySourcesError(
            "No completed documents are available to answer this question."
        )
    where = build_retrieval_where(
        user_id=user_id,
        project_id=project_id,
        authorized_sources=authorized_sources,
    )
    allowed_pairs = {
        (source.document_id, source.index_version) for source in authorized_sources
    }
    collection = collection or get_chroma_collection()
    embedder = embedder or default_embedder

    data = collection.get(where=where)
    chunks: list[RetrievedChunk] = []
    for chunk_id, text, metadata in zip(
        data.get("ids") or [],
        data.get("documents") or [],
        data.get("metadatas") or [],
    ):
        chunk = _chunk_from_row(
            chunk_id=chunk_id,
            text=text,
            metadata=metadata,
            allowed_pairs=allowed_pairs,
            user_id=user_id,
            project_id=project_id,
        )
        if chunk is not None:
            chunks.append(chunk)
    if not chunks:
        raise IndexUnavailableError(
            "Retrieved no content from the authorized sources yet. "
            "Please retry shortly."
        )

    corpus = [
        {"id": chunk.chunk_id, "text": chunk.text, "metadata": {"source": chunk.source, "page": chunk.page_number, "chunk_id": chunk.chunk_id}}
        for chunk in chunks
    ]
    bm25 = BM25Retriever(corpus)
    bm25_scores = bm25.get_scores(question)

    query_vector = _embed_query(embedder, question)
    vector_results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(DENSE_CANDIDATES, len(chunks)),
        where=where,
    )
    dense_scores: dict[str, float] = {}
    if vector_results and vector_results.get("ids"):
        for identifier, distance in zip(
            vector_results["ids"][0], vector_results["distances"][0]
        ):
            dense_scores[identifier] = 1.0 / (1.0 + distance)

    scored = merge_hybrid_scores(
        chunks=chunks, bm25_scores=bm25_scores, dense_scores=dense_scores
    )
    return [chunk for chunk, _score in scored[:best_n]]


__all__ = [
    "BEST_N",
    "TARGET_COLLECTION",
    "IndexUnavailableError",
    "NoReadySourcesError",
    "RetrievedChunk",
    "build_retrieval_where",
    "default_embedder",
    "get_chroma_collection",
    "merge_hybrid_scores",
    "retrieve_context",
]
