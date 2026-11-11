"""Refine model citation hints against retrieved evidence.

The LLM returns citation hints (``sentence``/``page``/
``filename``) together with its answer.  Those values are hints only:
every citation is refined against the retrieved chunks, and the
persisted v2 :class:`app.schemas.common.Citation` takes its sentence,
page, filename, document ID, chunk ID, and index version from the
*matched chunk* — never from the model.

Matching delegates to :func:`app.rag.text.match_citation_to_chunk` (exact token-sequence match,
query-word overlap, candidate precision, then model filename/page as
tie-breaks).  Unmatched model citations are dropped — a source is
never invented.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from app.schemas.common import Citation
from app.rag.text import match_citation_to_chunk
from pydantic import BaseModel, Field

if TYPE_CHECKING:  # pragma: no cover - typing only
    from app.rag.retrieval import RetrievedChunk


class ModelCitationLike(BaseModel):
    """Untrusted model hints, not the public verified citation DTO."""

    sentence: str = Field(
        description="One exact sentence copied verbatim from a single source-evidence chunk."
    )
    page: int = Field(description="One-based page number of the cited source-evidence chunk.")
    filename: str | None = Field(
        default=None,
        description="The chunk's Source filename, exactly as written in the evidence block.",
    )


def refine_citations(
    *,
    retrieved_chunks: Sequence[RetrievedChunk],
    model_citations: Sequence[ModelCitationLike],
) -> list[Citation]:
    """Refine model citations against retrieved chunks.

    Returns v2 citations whose identity, page, and exact supporting
    text all come from the matched chunk.  Model citations with no
    overlapping sentence in any retrieved chunk are dropped.
    """
    matching_chunks = [
        {
            "id": chunk.chunk_id,
            "text": chunk.text,
            "metadata": {
                "source": chunk.source,
                "page": chunk.page_number,
                "chunk_id": chunk.chunk_id,
            },
        }
        for chunk in retrieved_chunks
    ]
    refined: list[Citation] = []
    for model_citation in model_citations:
        match = match_citation_to_chunk(
            matching_chunks,
            model_citation.sentence,
            model_citation.filename,
            model_citation.page,
        )
        if match is None:
            continue
        chunk, exact_sentence = match
        retrieved = next(c for c in retrieved_chunks if c.chunk_id == chunk["id"])
        refined.append(
            Citation(
                document_id=retrieved.document_id,
                file_name=retrieved.source,
                page_number=retrieved.page_number,
                chunk_id=retrieved.chunk_id,
                text=exact_sentence,
                index_version=retrieved.index_version,
            )
        )
    return refined


__all__ = ["ModelCitationLike", "refine_citations"]
