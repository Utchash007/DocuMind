"""Document and job API routes.

Routes (FastAPI paths; browser calls go via ``/api/backend``)::

    GET    /projects/{project_id}/documents
    POST   /projects/{project_id}/documents            -> 202 {document, job}
    GET    /projects/{project_id}/documents/{document_id}
    DELETE /projects/{project_id}/documents/{document_id}  -> 202
    GET    /projects/{project_id}/documents/{document_id}/file
    POST   /projects/{project_id}/documents/{document_id}/retry  -> 202
    GET    /jobs/{job_id}

Upload flow (plan.md §5.1)
--------------------------
1. Resolve principal, require onboarding, verify project ownership.
2. Validate/stage a bounded PDF and fingerprint it (SHA-256).
   Allocate the document UUID + reserved Appwrite file ID *before*
    any database write. Page limits and complete text extraction use the
    same parser as the worker and are checked synchronously so rejected
   inputs leave no row, job, or storage object (UPL-04).
3. In one PostgreSQL transaction create ``Pending`` + ``awaiting_upload``
   with ``upload_request_id`` (unique ``(project_id, upload_request_id)``).
   Same key + same content returns the original pair; same key +
   different content is ``409 duplicate_request_conflict``.  Duplicates
   never reset a running/completed job.
4. Create the file in Storage with the reserved ID and owner-only
   permissions (outside any open transaction).
5. Inspect storage completion (``size`` match + ``chunks_uploaded ==
   chunks_total`` for chunked uploads).  Conditionally set
   ``upload_completed_at`` + move the job to ``queued`` only while it
   is still ``awaiting_upload``.  Incomplete files stay
   ``awaiting_upload`` for worker reconciliation and the call
   still answers ``202`` with the current states.
6. Return ``202 {document, job}``.  Receiving it means the PDF is
   stored and queued — not that chunks are indexed.

Partial Storage failures keep the reserved row/job (``awaiting_upload``)
and answer ``503 service_unavailable`` with the document/job IDs so
the client and reconciliation can poll/recover; the row is never
silently dropped.  The reserved file ID makes that recovery
addressable (UPL-06).

Dependencies
-----------------------------------
``get_current_principal`` (see :mod:`app.api.projects`),
``get_db``, ``get_storage_adapter`` (:mod:`app.services.storage`),
``get_job_queue`` (:mod:`app.repositories.documents`, where
``DirectJobQueue`` is the default).  All handlers are synchronous.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Header, Query, Request, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.projects import OnboardedPrincipalDep, SessionDep
from app.repositories.documents import (
    DirectJobQueue,
    DocumentConflictError,
    confirm_upload_completion,
    document_to_dto,
    enqueue_document_delete,
    get_job_queue,
    job_to_dto,
    list_owned_documents,
    nonterminal_process_job,
    prepare_document_retry,
    reserve_upload,
    tombstone_document,
)
from app.repositories.projects import (
    get_owned_document_or_404,
    get_owned_job_or_404,
    get_owned_project_or_404,
    raise_api_error,
)
from app.schemas.common import ErrorCode, PaginatedResponse
from app.schemas.documents import (
    Document as DocumentDto,
)
from app.schemas.documents import (
    DocumentDeleteAccepted,
    UploadAcceptance,
)
from app.schemas.jobs import ProcessingJob as ProcessingJobDto
from app.services.storage import (
    MAX_PDF_SIZE_BYTES,
    PDF_MIME_TYPE,
    RangeNotSatisfiableError,
    StorageNotFoundError,
    StorageUnavailableError,
    default_bucket_id,
    generate_appwrite_file_id,
    get_storage_adapter,
    is_pdf_filename,
    validate_pdf_bytes,
)

__all__ = ["get_job_queue", "get_storage_adapter", "router"]

router = APIRouter(tags=["documents", "jobs"])


def _validation_error(
    message: str,
    *,
    project_id: UUID | None = None,
    document_id: UUID | None = None,
) -> None:
    raise_api_error(
        422,
        ErrorCode.VALIDATION_ERROR,
        message,
        project_id=project_id,
        document_id=document_id,
    )


def _resolve_upload_request_id(raw: str | None, *, project_id: UUID) -> UUID:
    if raw is None or not raw.strip():
        return uuid.uuid4()
    try:
        return UUID(raw.strip())
    except (ValueError, AttributeError, TypeError):
        _validation_error(
            "Idempotency-Key must be a UUID.",
            project_id=project_id,
        )
        raise AssertionError("unreachable")  # pragma: no cover


def _read_bounded_upload(file: UploadFile, *, project_id: UUID) -> tuple[bytes, str]:
    filename = file.filename or ""
    if not is_pdf_filename(filename):
        _validation_error("Only PDF files are supported.", project_id=project_id)
        raise AssertionError("unreachable")  # pragma: no cover
    # Read with a hard bound so an oversized multipart body is
    # rejected without buffering unbounded bytes.
    try:
        file.file.seek(0)
    except Exception:
        pass
    data = file.file.read(MAX_PDF_SIZE_BYTES + 1)
    if not data:
        _validation_error("PDF file is empty.", project_id=project_id)
        raise AssertionError("unreachable")  # pragma: no cover
    if len(data) > MAX_PDF_SIZE_BYTES:
        _validation_error(
            f"PDF file exceeds the {MAX_PDF_SIZE_BYTES}-byte limit.",
            project_id=project_id,
        )
        raise AssertionError("unreachable")  # pragma: no cover
    return data, filename


def _check_extractable(data: bytes, filename: str, *, project_id: UUID) -> None:
    """Reject invalid, textless or over-budget PDFs before reservation."""
    from app.rag.pdf import PdfError, extract_pdf_chunks

    staged: Path | None = None
    try:
        with NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            staged = Path(tmp.name)
            tmp.write(data)
        extract_pdf_chunks(staged, file_name=filename)
    except PdfError as exc:
        _validation_error(str(exc), project_id=project_id)
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Listing
# ---------------------------------------------------------------------------


@router.get(
    "/projects/{project_id}/documents", response_model=PaginatedResponse[DocumentDto]
)
def list_documents(
    project_id: UUID,
    principal: OnboardedPrincipalDep,
    session: SessionDep,
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> PaginatedResponse[DocumentDto]:
    """GET .../documents -> paginated owner-scoped listing (forged project -> 404)."""
    # list_owned_documents re-verifies ownership (project -> user).
    rows, next_cursor = list_owned_documents(
        session, user_id=principal.id, project_id=project_id, cursor=cursor, limit=limit
    )
    return PaginatedResponse[DocumentDto](
        items=[document_to_dto(row) for row in rows],
        next_cursor=next_cursor,
    )


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------


@router.post(
    "/projects/{project_id}/documents",
    response_model=UploadAcceptance,
    status_code=202,
)
def upload_document(
    project_id: UUID,
    file: Annotated[UploadFile, File()],
    principal: OnboardedPrincipalDep,
    session: SessionDep,
    storage: Annotated[object, Depends(get_storage_adapter)],
    job_queue: Annotated[DirectJobQueue, Depends(get_job_queue)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> UploadAcceptance:
    """POST .../documents -> 202 {document, job} (see module docstring)."""
    # 1. Ownership (404 for foreign/forged projects).
    get_owned_project_or_404(session, user_id=principal.id, project_id=project_id)

    # 2. Validate/stage + fingerprint (no row/job/storage writes yet).
    data, file_name = _read_bounded_upload(file, project_id=project_id)
    try:
        content_sha256 = validate_pdf_bytes(data, file_name)
    except ValueError as exc:
        _validation_error(str(exc), project_id=project_id)
        raise AssertionError("unreachable")  # pragma: no cover
    _check_extractable(data, file_name, project_id=project_id)

    upload_request_id = _resolve_upload_request_id(idempotency_key, project_id=project_id)
    document_id = uuid.uuid4()
    appwrite_file_id = generate_appwrite_file_id()

    try:
        bucket_id = default_bucket_id()
    except RuntimeError:
        raise_api_error(
            503,
            ErrorCode.SERVICE_UNAVAILABLE,
            "Storage is not configured.",
            project_id=project_id,
        )
        raise AssertionError("unreachable")  # pragma: no cover

    # 3. Reservation transaction (Pending + awaiting_upload).
    try:
        document, job, is_duplicate = reserve_upload(
            session,
            owner_user_id=principal.id,
            project_id=project_id,
            document_id=document_id,
            appwrite_file_id=appwrite_file_id,
            file_name=file_name,
            file_size=len(data),
            mime_type=PDF_MIME_TYPE,
            upload_request_id=upload_request_id,
            content_sha256=content_sha256,
            bucket_id=bucket_id,
            job_queue=job_queue,
        )
    except DocumentConflictError as exc:
        session.rollback()
        raise_api_error(
            409,
            ErrorCode.DUPLICATE_REQUEST_CONFLICT,
            "This request key was already used with different content.",
            project_id=project_id,
            document_id=exc.document.id,
        )
        raise AssertionError("unreachable")  # pragma: no cover

    session.commit()
    # Re-fetch identities for the response (detached after commit is
    # safe with expire_on_commit=False, but re-read keeps it explicit).
    if is_duplicate:
        # Same key + same content: return the original pair, never
        # reset a running/completed job, never touch storage again.
        return UploadAcceptance(
            document=document_to_dto(document), job=job_to_dto(job)
        )

    # 4. Storage create with the reserved ID (outside any transaction).
    try:
        info = storage.create_storage_file(  # type: ignore[attr-defined]
            bucket_id=bucket_id,
            file_id=appwrite_file_id,
            data=data,
            mime_type=PDF_MIME_TYPE,
            owner_appwrite_user_id=principal.appwrite_user_id,
            file_name=file_name,
        )
    except StorageUnavailableError:
        raise_api_error(
            503,
            ErrorCode.SERVICE_UNAVAILABLE,
            "Storage upload failed; the document is pending reconciliation.",
            project_id=project_id,
            document_id=document.id,
            job_id=job.id,
        )
        raise AssertionError("unreachable")  # pragma: no cover
    except Exception:
        raise_api_error(
            503,
            ErrorCode.SERVICE_UNAVAILABLE,
            "Storage upload failed; the document is pending reconciliation.",
            project_id=project_id,
            document_id=document.id,
            job_id=job.id,
        )
        raise AssertionError("unreachable")  # pragma: no cover

    # 5. Completion inspection -> conditional queue (second transaction).
    try:
        inspected = storage.inspect_storage_file(  # type: ignore[attr-defined]
            bucket_id=bucket_id, file_id=appwrite_file_id
        )
    except StorageNotFoundError:
        raise_api_error(
            503,
            ErrorCode.SERVICE_UNAVAILABLE,
            "Storage upload was not found after create; the document is pending reconciliation.",
            project_id=project_id,
            document_id=document.id,
            job_id=job.id,
        )
        raise AssertionError("unreachable")  # pragma: no cover
    except StorageUnavailableError:
        raise_api_error(
            503,
            ErrorCode.SERVICE_UNAVAILABLE,
            "Storage inspection failed; the document is pending reconciliation.",
            project_id=project_id,
            document_id=document.id,
            job_id=job.id,
        )
        raise AssertionError("unreachable")  # pragma: no cover

    complete = (
        getattr(info, "completed", False)
        and int(getattr(info, "size", 0)) == len(data)
        and not (
            int(getattr(info, "chunks_total", 0)) > 0
            and int(getattr(info, "chunks_uploaded", 0))
            != int(getattr(info, "chunks_total", 0))
        )
    )
    if complete:
        try:
            confirm_upload_completion(session, document=document, job=job)
        except Exception:
            session.rollback()
            raise
        session.commit()

    # 6. 202 with current states (queued when complete, else awaiting_upload).
    return UploadAcceptance(
        document=document_to_dto(document), job=job_to_dto(job)
    )


# ---------------------------------------------------------------------------
# Read / delete / file / retry
# ---------------------------------------------------------------------------


@router.get(
    "/projects/{project_id}/documents/{document_id}", response_model=DocumentDto
)
def read_document(
    project_id: UUID,
    document_id: UUID,
    principal: OnboardedPrincipalDep,
    session: SessionDep,
) -> DocumentDto:
    """GET .../documents/{id} -> owner-scoped read."""
    document = get_owned_document_or_404(
        session,
        user_id=principal.id,
        project_id=project_id,
        document_id=document_id,
    )
    return document_to_dto(document)


@router.delete(
    "/projects/{project_id}/documents/{document_id}",
    response_model=DocumentDeleteAccepted,
    status_code=202,
)
def delete_document(
    project_id: UUID,
    document_id: UUID,
    principal: OnboardedPrincipalDep,
    session: SessionDep,
    job_queue: Annotated[DirectJobQueue, Depends(get_job_queue)],
) -> DocumentDeleteAccepted:
    """DELETE .../documents/{id} -> 202 {projectId, documentId, jobId}."""
    from app.db.queries import get_owned_document as _query_doc

    # Distinguish "already deleting" (409) from "never owned" (404).
    existing = _query_doc(
        session,
        user_id=principal.id,
        project_id=project_id,
        document_id=document_id,
        include_deleted=True,
    )
    if existing is None:
        raise_api_error(
            404,
            ErrorCode.NOT_FOUND,
            "Document not found.",
            project_id=project_id,
            document_id=document_id,
        )
    if existing.deleted_at is not None:
        session.rollback()
        raise_api_error(
            409,
            ErrorCode.CONFLICT,
            "Document is already being deleted.",
            project_id=project_id,
            document_id=document_id,
        )
    document = existing

    try:
        bucket_id = default_bucket_id()
    except RuntimeError:
        session.rollback()
        raise_api_error(
            503,
            ErrorCode.SERVICE_UNAVAILABLE,
            "Storage is not configured.",
            project_id=project_id,
            document_id=document_id,
        )
        raise AssertionError("unreachable")  # pragma: no cover

    try:
        tombstone_document(session, document)
        delete_job = enqueue_document_delete(
            session,
            document=document,
            bucket_id=bucket_id,
            job_queue=job_queue,
        )
    except Exception:
        session.rollback()
        raise
    session.commit()
    return DocumentDeleteAccepted(
        project_id=project_id, document_id=document.id, job_id=delete_job.id
    )


@router.get("/projects/{project_id}/documents/{document_id}/file")
def download_document_file(
    project_id: UUID,
    document_id: UUID,
    request: Request,
    principal: OnboardedPrincipalDep,
    session: SessionDep,
    storage: Annotated[object, Depends(get_storage_adapter)],
) -> Response:
    """GET .../documents/{id}/file -> authorized inline PDF (Range support).

    Returns ``200`` full / ``206`` byte range,
    ``application/pdf``, inline disposition, ``Accept-Ranges``.
    Owner-only: the bucket is private and reads go through the
    server API key after the ``document -> project -> user`` check.
    """
    document = get_owned_document_or_404(
        session,
        user_id=principal.id,
        project_id=project_id,
        document_id=document_id,
    )
    try:
        bucket_id = default_bucket_id()
    except RuntimeError:
        raise_api_error(
            503,
            ErrorCode.SERVICE_UNAVAILABLE,
            "Storage is not configured.",
            project_id=project_id,
            document_id=document_id,
        )
        raise AssertionError("unreachable")  # pragma: no cover

    range_header = request.headers.get("Range")
    try:
        chunk, headers = storage.open_storage_range(  # type: ignore[attr-defined]
            bucket_id=bucket_id,
            file_id=document.appwrite_file_id,
            range_header=range_header,
        )
    except RangeNotSatisfiableError as exc:
        return Response(
            status_code=416,
            headers={
                "Accept-Ranges": "bytes",
                "Content-Range": f"bytes */{exc.size}",
                "Content-Type": "application/pdf",
            },
        )
    except StorageNotFoundError:
        raise_api_error(
            503,
            ErrorCode.SERVICE_UNAVAILABLE,
            "Stored PDF is unavailable.",
            project_id=project_id,
            document_id=document_id,
        )
        raise AssertionError("unreachable")  # pragma: no cover
    except StorageUnavailableError:
        raise_api_error(
            503,
            ErrorCode.SERVICE_UNAVAILABLE,
            "Stored PDF is unavailable.",
            project_id=project_id,
            document_id=document_id,
        )
        raise AssertionError("unreachable")  # pragma: no cover

    disposition = _inline_disposition(document.file_name)
    # Adapter headers are lowercase-insensitive; normalize for clients.
    normalized = {str(k).lower(): str(v) for k, v in dict(headers).items()}
    content_type = normalized.get("content-type", "application/pdf")
    content_length = normalized.get("content-length", str(len(chunk)))
    content_range = normalized.get("content-range")
    response_headers: dict[str, str] = {
        "Content-Type": content_type,
        "Content-Disposition": disposition,
        "Accept-Ranges": "bytes",
        "Content-Length": content_length,
    }
    if content_range is not None:
        response_headers["Content-Range"] = content_range
        status_code = 206
    else:
        status_code = 200
    return Response(
        content=chunk, status_code=status_code, headers=response_headers
    )


@router.post(
    "/projects/{project_id}/documents/{document_id}/retry",
    response_model=UploadAcceptance,
    status_code=202,
)
def retry_document(
    project_id: UUID,
    document_id: UUID,
    principal: OnboardedPrincipalDep,
    session: SessionDep,
    job_queue: Annotated[DirectJobQueue, Depends(get_job_queue)],
) -> UploadAcceptance:
    """POST .../documents/{id}/retry -> 202 with a new queued job.

    Eligible only when the document is ``Failed`` and no nonterminal
    job exists; otherwise ``409 invalid_state`` /
    ``409 processing_in_progress``.  The failed job stays terminal;
    ``processing_epoch`` advances (see :func:`prepare_document_retry`).
    """
    document = get_owned_document_or_404(
        session,
        user_id=principal.id,
        project_id=project_id,
        document_id=document_id,
    )
    active = nonterminal_process_job(session, target_document_id=document.id)
    if active is not None:
        session.rollback()
        raise_api_error(
            409,
            ErrorCode.PROCESSING_IN_PROGRESS,
            "Document processing is still in progress.",
            project_id=project_id,
            document_id=document_id,
            job_id=active.id,
        )
        raise AssertionError("unreachable")  # pragma: no cover
    if document.status != "Failed":
        session.rollback()
        raise_api_error(
            409,
            ErrorCode.INVALID_STATE,
            "Only failed documents can be retried.",
            project_id=project_id,
            document_id=document_id,
        )
        raise AssertionError("unreachable")  # pragma: no cover

    try:
        bucket_id = default_bucket_id()
    except RuntimeError:
        session.rollback()
        raise_api_error(
            503,
            ErrorCode.SERVICE_UNAVAILABLE,
            "Storage is not configured.",
            project_id=project_id,
            document_id=document_id,
        )
        raise AssertionError("unreachable")  # pragma: no cover

    try:
        document, job = prepare_document_retry(
            session,
            document=document,
            bucket_id=bucket_id,
            job_queue=job_queue,
        )
    except Exception:
        session.rollback()
        raise
    session.commit()
    return UploadAcceptance(
        document=document_to_dto(document), job=job_to_dto(job)
    )


# ---------------------------------------------------------------------------
# Job status
# ---------------------------------------------------------------------------


@router.get("/jobs/{job_id}", response_model=ProcessingJobDto)
def read_job(
    job_id: UUID,
    principal: OnboardedPrincipalDep,
    session: SessionDep,
) -> ProcessingJobDto:
    """GET /jobs/{jobId} -> owner-scoped status incl. tombstones."""
    job = get_owned_job_or_404(session, user_id=principal.id, job_id=job_id)
    return job_to_dto(job)


def _inline_disposition(filename: str) -> str:
    """``inline; filename="..."`` with RFC 5987 fallback for unicode."""
    ascii_name = filename.encode("ascii", "ignore").decode("ascii").strip() or "document.pdf"
    escaped = ascii_name.replace("\\", "\\\\").replace('"', '\\"')
    if ascii_name != filename:
        encoded = _rfc5987_encode(filename)
        return f"inline; filename=\"{escaped}\"; filename*=UTF-8''{encoded}"
    return f'inline; filename="{escaped}"'


def _rfc5987_encode(value: str) -> str:
    from urllib.parse import quote

    return quote(value, safe="")
