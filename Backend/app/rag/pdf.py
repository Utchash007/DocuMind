"""Complete PDF extraction and page-bound, roughly 800-character chunks.

Malformed, partial, oversized, and textless documents fail explicitly.
Indexable chunk IDs include document/version/page/chunk. Standalone upload
preflight uses local ``preflight:p{page}:c{sub}`` labels, never filename
identities. Preflight chunks are discarded before owned worker indexing.
"""

from __future__ import annotations

import re
from pathlib import Path
from uuid import UUID

import pypdf



from app.schemas.services import PdfChunk
from app.rag.text import split_into_sentences
from app.limits import MAX_PDF_PAGES, MAX_PDF_SIZE_BYTES

MAX_CHUNK_TARGET = 800

DEFAULT_MAX_PDF_BYTES = MAX_PDF_SIZE_BYTES
DEFAULT_MAX_PDF_PAGES = MAX_PDF_PAGES


class PdfError(Exception):
    """Base for extraction failures.  ``retryable`` is False for all of
    them: reprocessing the same bytes cannot fix content problems."""

    code = "pdf_malformed"
    retryable = False

    def __init__(self, message: str, *, pages_extracted: int = 0) -> None:
        super().__init__(message)
        self.message = message
        self.pages_extracted = pages_extracted


class PdfMalformedError(PdfError):
    """Bytes are not a parseable PDF, or parsing failed mid-document."""

    code = "pdf_malformed"


class PdfTextlessError(PdfError):
    """PDF parsed cleanly but contains no extractable text."""

    code = "pdf_textless"


class PdfPageLimitError(PdfError):
    """Page count exceeds the bounded processing limit."""

    code = "page_limit_exceeded"


class PdfFileTooLargeError(PdfError):
    """File size exceeds the bounded processing limit."""

    code = "file_too_large"


def chunk_id_for(
    document_id: UUID | str | None,
    index_version: UUID | str | None,
    page_number: int,
    sub_index: int,
) -> str:
    """Deterministic chunk ID: document/version/page/chunk.

    With a document and version: ``{doc}:{version}:p{page}:c{sub}``.  An
    expired worker can only ever write into its obsolete
    ``index_version`` namespace, and re-running the same attempt
    regenerates the same IDs (idempotent upserts).
    """
    if document_id is not None and index_version is not None:
        return f"{document_id}:{index_version}:p{page_number}:c{sub_index}"
    if document_id is not None or index_version is not None:
        raise ValueError("document_id and index_version must be supplied together")
    return f"preflight:p{page_number}:c{sub_index}"


def chunk_page_text(
    text: str,
    *,
    page_number: int,
    file_name: str,
    document_id: UUID | str | None,
    index_version: UUID | str | None,
    target_chars: int = MAX_CHUNK_TARGET,
) -> list[PdfChunk]:
    """Group one page's sentences into ~``target_chars`` chunks.

    Append sentences until the running length reaches the target, then
    flush; flush leftovers at the end of the page.  Chunks never span
    pages because this function only ever sees one page of text.
    """
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    chunks: list[PdfChunk] = []
    current: list[str] = []
    current_len = 0
    sub_index = 0
    for sentence in split_into_sentences(cleaned):
        current.append(sentence)
        current_len += len(sentence)
        if current_len >= target_chars:
            chunks.append(
                PdfChunk(
                    chunk_id=chunk_id_for(
                        document_id, index_version, page_number, sub_index
                    ),
                    text=" ".join(current),
                    page_number=page_number,
                    source=file_name,
                )
            )
            current = []
            current_len = 0
            sub_index += 1
    if current:
        chunks.append(
            PdfChunk(
                chunk_id=chunk_id_for(
                    document_id, index_version, page_number, sub_index
                ),
                text=" ".join(current),
                page_number=page_number,
                source=file_name,
            )
        )
    return chunks


def extract_pdf_chunks(
    pdf_path: Path,
    *,
    file_name: str,
    document_id: UUID | str | None = None,
    index_version: UUID | str | None = None,
    max_pages: int = DEFAULT_MAX_PDF_PAGES,
    max_file_bytes: int = DEFAULT_MAX_PDF_BYTES,
    target_chars: int = MAX_CHUNK_TARGET,
) -> list[PdfChunk]:
    """Extract page-bound chunks from ``pdf_path`` (blocking, sync).

    Raises :class:`PdfMalformedError` (unparseable or partially parsed),
    :class:`PdfTextlessError` (no text at all),
    :class:`PdfPageLimitError`, or :class:`PdfFileTooLargeError` -- all
    terminal job failures.  Never returns a partial extraction.
    """
    path = Path(pdf_path)
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise PdfMalformedError(f"PDF is not readable: {exc}") from exc
    if size > max_file_bytes:
        raise PdfFileTooLargeError(
            f"PDF is {size} bytes, exceeding the {max_file_bytes}-byte limit"
        )
    if size == 0:
        raise PdfMalformedError("PDF file is empty")
    try:
        reader = pypdf.PdfReader(str(path))
        pages = list(reader.pages)
    except Exception as exc:  # pypdf raises several exception types
        raise PdfMalformedError(f"PDF could not be parsed: {exc}") from exc
    if len(pages) > max_pages:
        raise PdfPageLimitError(
            f"PDF has {len(pages)} pages, exceeding the {max_pages}-page limit"
        )
    chunks: list[PdfChunk] = []
    pages_extracted = 0
    for page_index, page in enumerate(pages):
        page_number = page_index + 1
        try:
            text = page.extract_text() or ""
        except Exception as exc:
            raise PdfMalformedError(
                f"PDF parsing failed on page {page_number} after "
                f"{pages_extracted} page(s): {exc}",
                pages_extracted=pages_extracted,
            ) from exc
        pages_extracted += 1
        chunks.extend(
            chunk_page_text(
                text,
                page_number=page_number,
                file_name=file_name,
                document_id=document_id,
                index_version=index_version,
                target_chars=target_chars,
            )
        )
    if not chunks:
        raise PdfTextlessError(
            f"PDF contains no extractable text ({len(pages)} page(s) parsed)"
        )
    return chunks


class PdfExtractionService:
    """Protocol-shaped facade (``PdfPipeline.extract_pdf_chunks``).

    Extra keyword-only arguments carry the document/version identity
    needed for deterministic indexable chunk IDs. Preflight callers without
    identity get local labels that are not published to the index.
    """

    def __init__(self, *, max_pages: int = DEFAULT_MAX_PDF_PAGES, max_file_bytes: int = DEFAULT_MAX_PDF_BYTES) -> None:
        self.max_pages = max_pages
        self.max_file_bytes = max_file_bytes

    def extract_pdf_chunks(
        self,
        pdf_path: Path,
        *,
        file_name: str,
        document_id: UUID | str | None = None,
        index_version: UUID | str | None = None,
    ) -> list[PdfChunk]:
        return extract_pdf_chunks(
            pdf_path,
            file_name=file_name,
            document_id=document_id,
            index_version=index_version,
            max_pages=self.max_pages,
            max_file_bytes=self.max_file_bytes,
        )


__all__ = [
    "DEFAULT_MAX_PDF_BYTES",
    "DEFAULT_MAX_PDF_PAGES",
    "MAX_CHUNK_TARGET",
    "PdfError",
    "PdfExtractionService",
    "PdfFileTooLargeError",
    "PdfMalformedError",
    "PdfPageLimitError",
    "PdfTextlessError",
    "chunk_id_for",
    "chunk_page_text",
    "extract_pdf_chunks",
    "split_into_sentences",
]
