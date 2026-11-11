"""Versioned Chroma indexing: ``documind_chunks_v2`` publications.

This is the index contract used for retrieval. Facts a retriever
must rely on:

* Collection name is ``COLLECTION_NAME`` (``documind_chunks_v2``) --
  never the legacy filename-keyed ``documind_chunks`` collection.
* Every write targets one fresh ``index_version`` namespace per job
  attempt.  Only the PostgreSQL publication fence
  (:func:`app.jobs.queue.complete_job`) may move a document's
  ``active_index_version`` pointer; a stale worker's vectors can only
  ever land in its obsolete namespace (JOB-08).
* Canonical metadata on every record is exactly
  ``CHROMA_METADATA_KEYS``: ``user_id``, ``project_id``,
  ``document_id``, ``index_version`` (all string UUIDs), ``source``
  (display file name), ``page`` (1-based int), ``chunk_id``.
* Chunk IDs are deterministic (``{document_id}:{index_version}:p{page}:c{n}``)
  so re-running an attempt upserts the same IDs (idempotent), and
  citations can carry ``chunkId`` + ``indexVersion``.
* Retrieval must filter by the *exact* permitted (document, version)
  pairs with ``$and`` clauses -- independent document/version lists
  must never be combined as independent filters (plan.md 5.3.5).

Writes are batched (``INDEX_BATCH_SIZE``, default 100) and validated
before the first upsert (chunk/vector count agreement, non-empty).
Deletes are idempotent: removing an already-missing version counts as
deleted, which is what makes cleanup retries (DEL-02/DEL-03) safe.
Provider errors raise :class:`IndexWriteError` (retryable job error);
nothing is published to PostgreSQL from this module.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Sequence
from typing import Any, Protocol
from uuid import UUID



from app.schemas.services import PdfChunk  # noqa: E402

COLLECTION_NAME = "documind_chunks_v2"
INDEX_BATCH_SIZE = 100

CHROMA_METADATA_KEYS = (
    "user_id",
    "project_id",
    "document_id",
    "index_version",
    "source",
    "page",
    "chunk_id",
)


class IndexWriteError(Exception):
    """Chroma write/delete failed (retryable job error)."""

    code = "index_write_failed"
    retryable = True

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def chunk_id_for(
    document_id: UUID | str | None,
    index_version: UUID | str | None,
    page_number: int,
    sub_index: int,
) -> str:
    """Re-export of the canonical chunk-ID builder (see ``app.rag.pdf``)."""
    from app.rag.pdf import chunk_id_for as _build

    return _build(document_id, index_version, page_number, sub_index)


def build_metadata(
    *,
    user_id: UUID | str,
    project_id: UUID | str,
    document_id: UUID | str,
    index_version: UUID | str,
    chunk: PdfChunk,
) -> dict[str, Any]:
    """Canonical v2 metadata for one chunk (exactly the 7 frozen keys)."""
    return {
        "user_id": str(user_id),
        "project_id": str(project_id),
        "document_id": str(document_id),
        "index_version": str(index_version),
        "source": chunk.source,
        "page": int(chunk.page_number),
        "chunk_id": chunk.chunk_id,
    }


def version_where(
    *,
    user_id: UUID | str | None = None,
    project_id: UUID | str | None = None,
    document_id: UUID | str | None = None,
    index_version: UUID | str | None = None,
) -> dict[str, Any]:
    """Chroma ``where`` filter for an exact (document, version) scope."""
    clauses: list[dict[str, str]] = []
    if user_id is not None:
        clauses.append({"user_id": str(user_id)})
    if project_id is not None:
        clauses.append({"project_id": str(project_id)})
    if document_id is not None:
        clauses.append({"document_id": str(document_id)})
    if index_version is not None:
        clauses.append({"index_version": str(index_version)})
    if not clauses:
        raise ValueError("version_where requires at least one scope clause")
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


class ChromaCollection(Protocol):
    """The subset of the Chroma collection API this module uses."""

    def upsert(
        self,
        *,
        ids: Sequence[str],
        embeddings: Sequence[Sequence[float]],
        documents: Sequence[str],
        metadatas: Sequence[dict[str, Any]],
    ) -> None:
        ...

    def delete(self, *, where: dict[str, Any] | None = None, ids: Sequence[str] | None = None) -> None:
        ...


def default_chroma_collection():
    """Build the production ``documind_chunks_v2`` collection.

    Uses ``CHROMA_API_KEY`` / ``CHROMA_TENANT`` / ``CHROMA_DATABASE``.
    Constructed lazily so importing this
    module never touches the network or requires credentials.
    """
    import chromadb

    client = chromadb.CloudClient(
        api_key=os.environ.get("CHROMA_API_KEY"),
        tenant=os.environ.get("CHROMA_TENANT"),
        database=os.environ.get("CHROMA_DATABASE"),
    )
    return client.get_or_create_collection(name=COLLECTION_NAME)


class IndexService:
    """Protocol-shaped index publication (``PdfPipeline.publish_*``).

    The ``collection_factory`` is injectable: production uses
    :func:`default_chroma_collection`; tests pass an in-memory double
    implementing the :class:`ChromaCollection` protocol.  The optional
    ``embedder`` honours the frozen protocol shape
    (``publish_index_version(..., chunks)`` with no embeddings
    argument): when ``embeddings`` is omitted, chunks are embedded
    through it.  Without either, publishing raises -- production
    callers can never silently index without vectors.
    """

    def __init__(
        self,
        collection_factory: Callable[[], ChromaCollection] | None = None,
        *,
        batch_size: int = INDEX_BATCH_SIZE,
        embedder: Any | None = None,
    ) -> None:
        self._factory = collection_factory or default_chroma_collection
        self.batch_size = max(1, batch_size)
        self._embedder = embedder

    def publish_index_version(
        self,
        *,
        user_id: UUID | str,
        project_id: UUID | str,
        document_id: UUID | str,
        index_version: UUID | str,
        chunks: Sequence[PdfChunk],
        embeddings: Sequence[Sequence[float]] | None = None,
    ) -> int:
        """Write ``chunks`` into the ``index_version`` namespace.

        ``embeddings`` must be the output of
        ``EmbeddingService.embed_texts`` for the chunk texts, in order.
        When omitted, the service's injected ``embedder`` computes
        them (the frozen protocol shape); with neither, this raises --
        production must never index without vectors.  Returns the
        number of records written.
        """
        items = list(chunks)
        if not items:
            raise IndexWriteError("refusing to publish an empty index version")
        if embeddings is None:
            if self._embedder is None:
                raise IndexWriteError(
                    "embeddings are required: pass embeddings or an embedder"
                )
            try:
                embeddings = self._embedder.embed_texts([chunk.text for chunk in items])
            except Exception as exc:
                raise IndexWriteError(f"index-time embedding failed: {exc}") from exc
        vectors = list(embeddings)
        if len(vectors) != len(items):
            raise IndexWriteError(
                f"chunk/vector count mismatch: {len(items)} chunks, {len(vectors)} vectors"
            )
        collection = self._collection()
        written = 0
        for start in range(0, len(items), self.batch_size):
            batch = items[start : start + self.batch_size]
            batch_vectors = vectors[start : start + self.batch_size]
            ids = [chunk.chunk_id for chunk in batch]
            documents = [chunk.text for chunk in batch]
            metadatas = [
                build_metadata(
                    user_id=user_id,
                    project_id=project_id,
                    document_id=document_id,
                    index_version=index_version,
                    chunk=chunk,
                )
                for chunk in batch
            ]
            try:
                collection.upsert(
                    ids=ids,
                    embeddings=batch_vectors,
                    documents=documents,
                    metadatas=metadatas,
                )
            except IndexWriteError:
                raise
            except Exception as exc:
                raise IndexWriteError(f"chroma upsert failed: {exc}") from exc
            written += len(batch)
        return written

    def delete_index_version(
        self,
        *,
        user_id: UUID | str | None = None,
        project_id: UUID | str | None = None,
        document_id: UUID | str,
        index_version: UUID | str,
    ) -> None:
        """Idempotently delete one (document, version) namespace."""
        collection = self._collection()
        try:
            collection.delete(
                where=version_where(
                    user_id=user_id,
                    project_id=project_id,
                    document_id=document_id,
                    index_version=index_version,
                )
            )
        except IndexWriteError:
            raise
        except Exception as exc:
            raise IndexWriteError(f"chroma namespace delete failed: {exc}") from exc

    def delete_all_versions(
        self,
        *,
        user_id: UUID | str | None = None,
        project_id: UUID | str | None = None,
        document_id: UUID | str,
        index_versions: Sequence[UUID | str],
    ) -> int:
        """Delete every known version of a document; returns attempts."""
        attempts = 0
        for version in index_versions:
            self.delete_index_version(
                user_id=user_id,
                project_id=project_id,
                document_id=document_id,
                index_version=version,
            )
            attempts += 1
        return attempts

    def _collection(self) -> ChromaCollection:
        try:
            return self._factory()
        except IndexWriteError:
            raise
        except Exception as exc:
            raise IndexWriteError(f"chroma collection unavailable: {exc}") from exc


__all__ = [
    "CHROMA_METADATA_KEYS",
    "COLLECTION_NAME",
    "INDEX_BATCH_SIZE",
    "ChromaCollection",
    "IndexService",
    "IndexWriteError",
    "build_metadata",
    "chunk_id_for",
    "default_chroma_collection",
    "version_where",
]
