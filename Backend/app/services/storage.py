"""Private Appwrite Storage adapter.

This module implements the frozen ``StorageAdapter`` Protocol from
``app/schemas/services.py`` against Appwrite Storage and provides the
reusable in-memory adapter for local callers.

Protocol surface (all synchronous, blocking-safe)::

    create_storage_file(bucket_id, file_id, data, mime_type) -> StorageFileInfo
    inspect_storage_file(bucket_id, file_id) -> StorageFileInfo
    open_storage_range(bucket_id, file_id, range_header) -> (bytes, headers)
    delete_storage_file(bucket_id, file_id) -> None   # idempotent

Network calls run outside any open PostgreSQL transaction.  Handlers
must commit the reservation transaction before calling ``create`` and
commit the finalize transaction after ``inspect`` (see plan.md §5.1).

File-level security and owner-only access
------------------------------------------
Files are created with a **reserved** ``file_id`` (allocated before the
PostgreSQL reservation transaction) and owner-only permissions derived
from the caller's external ``appwrite_user_id``::

    read("user:<appwrite_user_id>"), update("user:<appwrite_user_id>"),
    delete("user:<appwrite_user_id>")

The database always uses the internal ``users.id`` UUID; Appwrite file
permissions always use the external ``appwrite_user_id`` (plan §3.3).
The reserved ID lets the worker reconcile an interrupted upload or a
lost commit acknowledgment: the file is addressable before the first
database write.  ``InMemoryStorageAdapter`` records the same behavior
for tests.

Completion inspection
---------------------
``inspect_storage_file`` maps Appwrite file metadata (size + chunk
counters) to ``StorageFileInfo.completed``, defined as
``size > 0 and chunks_uploaded >= chunks_total`` (with
``chunks_total > 0``; Appwrite reports a single chunk for small
files).  For chunked uploads callers require
``chunks_uploaded == chunks_total`` (plan §5.1 step 5).  Incomplete
files stay ``awaiting_upload``; worker reconciliation later
queues complete files or fails abandoned ones.

Range downloads
---------------
``open_storage_range`` returns the full bytes sliced by the HTTP
``Range`` header plus RFC-compliant headers (``Accept-Ranges``,
``Content-Length``, ``Content-Type``, and ``Content-Range`` for
``206``).  Invalid range syntax falls back to a full ``200`` download
(Starlette ``FileResponse`` parity); a syntactically valid but
unsatisfiable range raises :class:`RangeNotSatisfiableError` so the
handler can answer ``416`` at the owned document file endpoint.

Deployment configuration
------------------------------------------------------------
Backend env (server-only)::

    APPWRITE_ENDPOINT            e.g. https://sgp.cloud.appwrite.io/v1
    APPWRITE_PROJECT_ID          Appwrite project ID
    APPWRITE_API_KEY             server API key (never exposed to browser)
    APPWRITE_STORAGE_BUCKET_ID   private PDF bucket ID

Legacy dev names ``appwrite_site_endpoint``, ``appwrite_project_id``,
``appwrite``, and ``appwrite_file_key`` are accepted as fallbacks so
the checked-in root ``.env`` keeps working during integration; new
deployments should use the standardized names above.

Bucket settings (create once, via console or server SDK)::

    fileSecurity = True
    permissions = []                      # no bucket-level access
    allowedFileExtensions = ["pdf"]
    maximumFileSize = 26214400            # 25 MiB, must match MAX_PDF_SIZE_BYTES
    encryption = True
    antivirus = False                     # worker + API validate; keep off for speed
    compression = "none"                  # PDFs are already compressed
    transformations = False

Appwrite 2.7.1 no longer accepts ``allowedFileMimeTypes`` (the field is
omitted from responses and sent payloads may reset it), so PDF MIME
enforcement relies on the extension allowlist above plus application
validation (``validate_pdf_bytes`` checks the ``%PDF-`` magic, and the
document API stores every accepted upload as ``application/pdf``).
Always send the full settings payload when updating the bucket: partial
updates reset omitted fields to their defaults.

Required server API-key scopes for the key above::

    storage.buckets.read, storage.buckets.write,
    storage.files.create, storage.files.read,
    storage.files.update, storage.files.delete

Limits (must stay consistent across proxy / API / bucket / worker / UI)::

    MAX_PDF_SIZE_BYTES = 25 MiB   API + bucket maximumFileSize
    MAX_PDF_PAGES      = 200      worker extraction budget (not enforced here)
    PDF magic          "%PDF-"    API sync validation (see document API)

To match the frozen Protocol, implementations accept exactly the
documented keyword arguments; :class:`AppwriteStorageAdapter` adds one
optional ``owner_appwrite_user_id`` on ``create_storage_file`` (extra
optional kwargs are Protocol-compatible) so the handler can enforce
owner-only file permissions without changing the shared signature.
"""

from __future__ import annotations

import hashlib
import os
import re
import uuid
from typing import Any

from app.limits import MAX_PDF_PAGES, MAX_PDF_SIZE_BYTES
from app.schemas.services import StorageFileInfo

# ---------------------------------------------------------------------------
# Deployment constants (keep in lockstep with Appwrite bucket + proxy + UI)
# ---------------------------------------------------------------------------

# Shared budgets live in app.limits. The proxy reserves extra multipart
# overhead; page count is enforced during worker extraction.

#: Chroma collection for owned document/version retrieval.
V2_CHROMA_COLLECTION = "documind_chunks_v2"

PDF_MIME_TYPE = "application/pdf"
PDF_EXTENSION = ".pdf"
PDF_MAGIC = b"%PDF-"

#: Environment variable names (standardized; legacy fallbacks in code).
APPWRITE_ENDPOINT_ENV = "APPWRITE_ENDPOINT"
APPWRITE_PROJECT_ID_ENV = "APPWRITE_PROJECT_ID"
APPWRITE_API_KEY_ENV = "APPWRITE_API_KEY"
APPWRITE_BUCKET_ENV = "APPWRITE_STORAGE_BUCKET_ID"

#: Required Appwrite server scopes for the bucket + file operations here.
APPWRITE_REQUIRED_SCOPES: tuple[str, ...] = (
    "storage.buckets.read",
    "storage.buckets.write",
    "storage.files.create",
    "storage.files.read",
    "storage.files.update",
    "storage.files.delete",
)

#: Exact bucket creation settings for A0 / Appwrite console.
#: ``allowedFileMimeTypes`` is intentionally absent: Appwrite 2.7.1 does
#: not expose it, and PDF MIME is enforced by extension + magic checks.
STORAGE_BUCKET_SETTINGS: dict[str, Any] = {
    "fileSecurity": True,
    "permissions": [],
    "allowedFileExtensions": ["pdf"],
    "maximumFileSize": MAX_PDF_SIZE_BYTES,
    "encryption": True,
    "antivirus": False,
    "compression": "none",
    "transformations": False,
}


# ---------------------------------------------------------------------------
# Errors (mapped to HTTP by handlers; never leak provider payloads)
# ---------------------------------------------------------------------------


class StorageError(Exception):
    """Base for adapter failures."""


class StorageNotFoundError(StorageError):
    """The bucket/file does not exist (idempotent delete treats this as success)."""

    def __init__(self, bucket_id: str, file_id: str) -> None:
        super().__init__(f"storage file not found: bucket={bucket_id!r} file={file_id!r}")
        self.bucket_id = bucket_id
        self.file_id = file_id


class StorageUnavailableError(StorageError):
    """Storage backend unreachable or faulted; retryable (HTTP 503)."""


class StorageConflictError(StorageError):
    """Reserved file ID already exists with different content (HTTP 409)."""


class RangeNotSatisfiableError(StorageError):
    """Valid Range syntax but no bytes overlap the file (HTTP 416)."""

    def __init__(self, size: int) -> None:
        super().__init__(f"range not satisfiable for size {size}")
        self.size = size


# ---------------------------------------------------------------------------
# Pure helpers (no network, no DB) -- unit-tested directly
# ---------------------------------------------------------------------------

_RANGE_RE = re.compile(r"^\s*bytes\s*=\s*(?P<rest>.+?)\s*$", re.IGNORECASE)
_RANGE_SINGLE_RE = re.compile(r"^(?P<start>\d*)-(?P<end>\d*)$")


def generate_appwrite_file_id() -> str:
    """Allocate a reserved Appwrite file ID (32 lowercase hex chars).

    Appwrite custom IDs allow ``a-z0-9-. _`` up to 36 chars and must not
    start with a special character; a UUID hex string always satisfies
    this.  The ID is allocated *before* the PostgreSQL reservation so
    the file is addressable during reconciliation (plan §5.1).
    """
    return uuid.uuid4().hex


def sha256_hex(data: bytes) -> str:
    """Content fingerprint stored as ``document.content_sha256``."""
    return hashlib.sha256(data).hexdigest()


def is_pdf_filename(filename: str) -> bool:
    """True when ``filename`` is a bare ``.pdf`` basename."""
    if not filename or filename.strip() != filename:
        return False
    if any(c in filename for c in ("/", "\\", ":", "\x00")):
        return False
    if filename != filename.strip():
        return False
    # Path(filename).name must equal filename (reject dir components).
    # Compare without importing pathlib for purity: any separator was
    # already rejected above, so only the extension check remains.
    return filename.lower().endswith(PDF_EXTENSION) and len(filename) > len(PDF_EXTENSION)


def validate_pdf_bytes(data: bytes, filename: str, *, max_size: int = MAX_PDF_SIZE_BYTES) -> str:
    """Validate staged PDF bytes; return the SHA-256 hex fingerprint.

    Raises ``ValueError`` with a human-safe message for each rejection
    (empty, oversized, bad extension, bad magic).  Extractability (at
    least one text-bearing page via ``process_pdf``) is checked by the
    document API before reservation so rejected uploads leave no row,
    job, or storage object (UPL-04).  This helper covers the
    size/magic/filename half so storage-level callers (A4 worker) can
    reuse it without the API concern.
    """
    if not is_pdf_filename(filename):
        raise ValueError("Only PDF files are supported.")
    if not data:
        raise ValueError("PDF file is empty.")
    if len(data) > max_size:
        raise ValueError(
            f"PDF file exceeds the {max_size}-byte limit."
        )
    if not data.startswith(PDF_MAGIC):
        raise ValueError("Only PDF files are supported.")
    return sha256_hex(data)


def owner_file_permissions(appwrite_user_id: str) -> list[str]:
    """Owner-only Appwrite permission strings for one file.

    ``appwrite_user_id`` is the *external* Appwrite account ID (never
    the internal ``users.id`` UUID).  Bucket-level permissions stay
    empty and file-level security is enabled, so direct Appwrite
    access is restricted to the owner while the server API key
    mediates all application reads/writes/deletes.
    """
    if not appwrite_user_id or not appwrite_user_id.strip():
        raise ValueError("appwrite_user_id is required for owner permissions")
    target = f"user:{appwrite_user_id}"
    return [
        f'read("{target}")',
        f'update("{target}")',
        f'delete("{target}")',
    ]


def make_resource_snapshot(
    *,
    bucket_id: str,
    file_id: str,
    file_name: str,
    file_size: int,
    content_sha256: str,
    chroma_collection: str = V2_CHROMA_COLLECTION,
    active_index_version: str | None = None,
) -> dict[str, Any]:
    """Immutable ``processing_jobs.resource_snapshot`` for one document.

    Carries trusted bucket/file/Chroma references so job history and
    cleanup survive deletion of the document/project rows (plan §3.2).
    The snapshot is a JSON *object* (DB check ``resource_snapshot_is_object``).
    """
    snapshot: dict[str, Any] = {
        "bucket_id": bucket_id,
        "file_id": file_id,
        "file_name": file_name,
        "file_size": file_size,
        "content_sha256": content_sha256,
        "chroma_collection": chroma_collection,
    }
    if active_index_version is not None:
        snapshot["active_index_version"] = active_index_version
    return snapshot


def apply_range(
    data: bytes, range_header: str | None, *, mime_type: str = PDF_MIME_TYPE
) -> tuple[bytes, dict[str, str]]:
    """Slice ``data`` per an HTTP ``Range`` header; return ``(bytes, headers)``.

    * No header / invalid syntax -> full body headers (``200``).
    * Valid satisfiable range -> sliced body + ``Content-Range`` (``206``).
    * Valid unsatisfiable range -> raise :class:`RangeNotSatisfiableError` (``416``).

    Multi-range requests (``bytes=0-4,10-19``) are treated as invalid syntax
    and fall back to a full download.
    """
    size = len(data)
    headers: dict[str, str] = {
        "Accept-Ranges": "bytes",
        "Content-Type": mime_type,
        "Content-Length": str(size),
    }
    if not range_header or not range_header.strip():
        return data, headers
    match = _RANGE_RE.match(range_header)
    if match is None:
        return data, headers
    rest = match.group("rest")
    if "," in rest:  # multipart ranges unsupported -> full download
        return data, headers
    single = _RANGE_SINGLE_RE.match(rest.strip())
    if single is None:
        return data, headers
    start_raw = single.group("start")
    end_raw = single.group("end")
    if start_raw == "" and end_raw == "":
        return data, headers
    if size == 0:
        raise RangeNotSatisfiableError(size)

    if start_raw == "":
        # Suffix range: last N bytes.
        suffix = int(end_raw)
        if suffix == 0:
            raise RangeNotSatisfiableError(size)
        start = max(size - suffix, 0)
        end = size - 1
    else:
        start = int(start_raw)
        end = int(end_raw) if end_raw != "" else size - 1
        if start > end or start >= size:
            raise RangeNotSatisfiableError(size)
        if end >= size:
            end = size - 1

    sliced = data[start : end + 1]
    headers["Content-Length"] = str(len(sliced))
    headers["Content-Range"] = f"bytes {start}-{end}/{size}"
    return sliced, headers


def _get_env(*names: str) -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


def default_bucket_id() -> str:
    """Resolve the private PDF bucket ID, or raise ``RuntimeError`` if unset."""
    bucket = _get_env(APPWRITE_BUCKET_ENV, "appwrite_file_key")
    if not bucket:
        raise RuntimeError(
            f"{APPWRITE_BUCKET_ENV} is required but is not set."
        )
    return bucket


def storage_config() -> dict[str, str]:
    """Resolve endpoint/project/key/bucket or raise ``RuntimeError``.

    Standardized names take precedence; legacy root-``.env`` names are
    fallbacks.  Called lazily by :func:`get_storage_adapter`, never at
    import time, so importing this module never requires credentials.
    """
    endpoint = _get_env(APPWRITE_ENDPOINT_ENV, "appwrite_site_endpoint", "APPWRITE_ENDPOINT")
    project_id = _get_env(APPWRITE_PROJECT_ID_ENV, "appwrite_project_id")
    api_key = _get_env(APPWRITE_API_KEY_ENV, "appwrite", "APPWRITE_API_KEY")
    bucket = _get_env(APPWRITE_BUCKET_ENV, "appwrite_file_key")
    missing = [
        label
        for label, value in (
            (APPWRITE_ENDPOINT_ENV, endpoint),
            (APPWRITE_PROJECT_ID_ENV, project_id),
            (APPWRITE_API_KEY_ENV, api_key),
            (APPWRITE_BUCKET_ENV, bucket),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(
            "Appwrite Storage configuration missing: " + ", ".join(missing)
        )
    return {
        "endpoint": endpoint,
        "project_id": project_id,
        "api_key": api_key,
        "bucket_id": bucket,
    }


# ---------------------------------------------------------------------------
# Real adapter (Appwrite server SDK)
# ---------------------------------------------------------------------------


class AppwriteStorageAdapter:
    """``StorageAdapter`` Protocol implementation against Appwrite Storage.

    Construct with explicit config (tests inject a fake client), or use
    :func:`get_storage_adapter` which resolves config from the
    environment.  The ``storage`` attribute is the underlying
    ``appwrite.services.storage.Storage`` service (patchable in tests).
    """

    def __init__(
        self,
        *,
        endpoint: str,
        project_id: str,
        api_key: str,
        bucket_id: str | None = None,
    ) -> None:
        from appwrite.client import Client
        from appwrite.services.storage import Storage

        self.endpoint = endpoint
        self.project_id = project_id
        self._api_key = api_key
        self.bucket_id = bucket_id or default_bucket_id()
        client = (
            Client()
            .set_endpoint(endpoint)
            .set_project(project_id)
            .set_key(api_key)
        )
        self.storage = Storage(client)

    # -- mapping ----------------------------------------------------------

    @staticmethod
    def _metadata_to_info(
        metadata: dict[str, Any], *, bucket_id: str, file_id: str
    ) -> StorageFileInfo:
        size = int(
            metadata.get("sizeOriginal", metadata.get("size_original", 0)) or 0
        )
        mime = str(metadata.get("mimeType", metadata.get("mime_type", PDF_MIME_TYPE)) or PDF_MIME_TYPE)
        chunks_total = int(metadata.get("chunksTotal", metadata.get("chunks_total", 0)) or 0)
        chunks_uploaded = int(
            metadata.get("chunksUploaded", metadata.get("chunks_uploaded", 0)) or 0
        )
        # A single-chunk file reports chunks_total == 1; treat a
        # zero-counter response with a non-zero size as completed
        # (defensive against SDK/version drift).
        if chunks_total == 0 and size > 0:
            chunks_total = chunks_uploaded = 1
        completed = size > 0 and chunks_total > 0 and chunks_uploaded >= chunks_total
        return StorageFileInfo(
            file_id=str(metadata.get("$id", metadata.get("id", file_id))),
            bucket_id=str(metadata.get("bucketId", metadata.get("bucket_id", bucket_id))),
            size=size,
            mime_type=mime,
            chunks_uploaded=chunks_uploaded,
            chunks_total=chunks_total,
            completed=completed,
        )

    def _wrap(self, bucket_id: str, file_id: str, action: Any) -> Any:
        from appwrite.exception import AppwriteException

        try:
            return action()
        except AppwriteException as exc:
            code = int(exc.code or 0)
            exc_type = str(exc.type or "").lower()
            if code == 404 or "not_found" in exc_type or "not found" in str(exc.message).lower():
                raise StorageNotFoundError(bucket_id, file_id) from exc
            if code == 409 or "conflict" in exc_type or "already exists" in str(exc.message).lower():
                raise StorageConflictError(
                    f"storage file already exists: bucket={bucket_id!r} file={file_id!r}"
                ) from exc
            raise StorageUnavailableError(
                f"storage operation failed ({code}): {exc.message}"
            ) from exc
        except StorageError:
            raise
        except Exception as exc:  # network, timeout, SDK drift
            raise StorageUnavailableError(f"storage operation failed: {exc}") from exc

    # -- Protocol ---------------------------------------------------------

    def create_storage_file(
        self,
        *,
        bucket_id: str,
        file_id: str,
        data: bytes,
        mime_type: str,
        owner_appwrite_user_id: str | None = None,
        file_name: str | None = None,
    ) -> StorageFileInfo:
        """Upload with a pre-reserved file ID and owner-only access.

        ``owner_appwrite_user_id`` (optional, Protocol-compatible) sets
        file-level ``read/update/delete("user:<external id>")``
        permissions.  Without it the file is server-only (API key
        mediates every access); prefer always passing it from the
        upload handler.  The SDK chunks large files internally; the
        returned metadata carries the chunk counters inspected by
        :meth:`inspect_storage_file`.
        """
        from appwrite.input_file import InputFile

        if not data:
            raise ValueError("data must not be empty")
        permissions = (
            owner_file_permissions(owner_appwrite_user_id)
            if owner_appwrite_user_id is not None
            else None
        )
        filename = file_name or f"{file_id}{PDF_EXTENSION}"
        input_file = InputFile.from_bytes(data, filename, mime_type)

        def _create() -> dict[str, Any]:
            return self.storage.create_file(
                bucket_id, file_id, input_file, permissions
            )

        metadata = self._wrap(bucket_id, file_id, _create)
        return self._metadata_to_info(metadata, bucket_id=bucket_id, file_id=file_id)

    def inspect_storage_file(self, *, bucket_id: str, file_id: str) -> StorageFileInfo:
        """Return size/fingerprint/chunk completion for reconciliation."""
        metadata = self._wrap(
            bucket_id, file_id, lambda: self.storage.get_file(bucket_id, file_id)
        )
        return self._metadata_to_info(metadata, bucket_id=bucket_id, file_id=file_id)

    def open_storage_range(
        self, *, bucket_id: str, file_id: str, range_header: str | None
    ) -> tuple[bytes, dict[str, str]]:
        """Return (chunk bytes, response headers) for inline PDF serving.

        Downloads through the server API key (bucket stays private)
        and slices locally with :func:`apply_range` for byte-range responses.
        """
        raw = self._wrap(
            bucket_id,
            file_id,
            lambda: self.storage.get_file_download(bucket_id, file_id),
        )
        if isinstance(raw, (bytearray, memoryview)):
            raw = bytes(raw)
        if not isinstance(raw, (bytes, str)):
            raise StorageUnavailableError(
                f"unexpected storage download type: {type(raw).__name__}"
            )
        data = raw.encode() if isinstance(raw, str) else raw
        return apply_range(data, range_header)

    def delete_storage_file(self, *, bucket_id: str, file_id: str) -> None:
        """Idempotent delete: already-missing files count as deleted."""
        try:
            self._wrap(bucket_id, file_id, lambda: self.storage.delete_file(bucket_id, file_id))
        except StorageNotFoundError:
            return None
        return None


# ---------------------------------------------------------------------------
# In-memory double (A3 tests + A4/A7 reuse)
# ---------------------------------------------------------------------------


class InMemoryStorageAdapter:
    """Faithful ``StorageAdapter`` test double with fault injection.

    Stores ``(bucket_id, file_id) -> entry`` where entry carries the
    bytes, mime type, permissions, and chunk counters.  Fault flags:

    * ``fail_next_create``: exception raised by the next ``create``.
    * ``fail_next_inspect`` / ``fail_next_download`` / ``fail_next_delete``.
    * ``incomplete_next_create``: next ``create`` lands incomplete
      (``chunks_uploaded=0``) to exercise UPL-05 reconciliation.
    * ``seed_incomplete`` / direct ``seed_file(..., complete=False)``.

    ``calls`` records every attempted operation for assertions
    (reserved-ID usage, idempotent delete, range slices).
    """

    def __init__(self, *, default_complete: bool = True) -> None:
        self._files: dict[tuple[str, str], dict[str, Any]] = {}
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.fail_next_create: Exception | None = None
        self.fail_next_inspect: Exception | None = None
        self.fail_next_download: Exception | None = None
        self.fail_next_delete: Exception | None = None
        self.incomplete_next_create = False
        self.default_complete = default_complete

    # -- test helpers -----------------------------------------------------

    def seed_file(
        self,
        *,
        bucket_id: str,
        file_id: str,
        data: bytes,
        mime_type: str = PDF_MIME_TYPE,
        permissions: list[str] | None = None,
        complete: bool = True,
    ) -> StorageFileInfo:
        chunks_total = 1
        chunks_uploaded = 1 if complete else 0
        self._files[(bucket_id, file_id)] = {
            "data": bytes(data),
            "mime_type": mime_type,
            "permissions": list(permissions) if permissions else [],
            "file_name": f"{file_id}{PDF_EXTENSION}",
            "chunks_total": chunks_total,
            "chunks_uploaded": chunks_uploaded,
        }
        return self._info(bucket_id, file_id)

    def mark_complete(self, *, bucket_id: str, file_id: str) -> StorageFileInfo:
        entry = self._files.get((bucket_id, file_id))
        if entry is None:
            raise StorageNotFoundError(bucket_id, file_id)
        entry["chunks_uploaded"] = entry["chunks_total"]
        return self._info(bucket_id, file_id)

    def permissions_for(self, *, bucket_id: str, file_id: str) -> list[str]:
        entry = self._files.get((bucket_id, file_id))
        if entry is None:
            raise StorageNotFoundError(bucket_id, file_id)
        return list(entry["permissions"])

    def stored_bytes(self, *, bucket_id: str, file_id: str) -> bytes:
        entry = self._files.get((bucket_id, file_id))
        if entry is None:
            raise StorageNotFoundError(bucket_id, file_id)
        return bytes(entry["data"])

    def has_file(self, *, bucket_id: str, file_id: str) -> bool:
        return (bucket_id, file_id) in self._files

    # -- internals --------------------------------------------------------

    def _info(self, bucket_id: str, file_id: str) -> StorageFileInfo:
        entry = self._files[(bucket_id, file_id)]
        size = len(entry["data"])
        total = int(entry["chunks_total"])
        uploaded = int(entry["chunks_uploaded"])
        return StorageFileInfo(
            file_id=file_id,
            bucket_id=bucket_id,
            size=size,
            mime_type=str(entry["mime_type"]),
            chunks_uploaded=uploaded,
            chunks_total=total,
            completed=size > 0 and total > 0 and uploaded >= total,
        )

    # -- Protocol ---------------------------------------------------------

    def create_storage_file(
        self,
        *,
        bucket_id: str,
        file_id: str,
        data: bytes,
        mime_type: str,
        owner_appwrite_user_id: str | None = None,
        file_name: str | None = None,
    ) -> StorageFileInfo:
        self.calls.append(
            (
                "create",
                {
                    "bucket_id": bucket_id,
                    "file_id": file_id,
                    "size": len(data),
                    "mime_type": mime_type,
                    "owner_appwrite_user_id": owner_appwrite_user_id,
                    "file_name": file_name,
                },
            )
        )
        if self.fail_next_create is not None:
            exc, self.fail_next_create = self.fail_next_create, None
            raise exc
        if (bucket_id, file_id) in self._files:
            raise StorageConflictError(
                f"storage file already exists: bucket={bucket_id!r} file={file_id!r}"
            )
        if not data:
            raise ValueError("data must not be empty")
        complete = self.default_complete and not self.incomplete_next_create
        self.incomplete_next_create = False
        permissions = (
            owner_file_permissions(owner_appwrite_user_id)
            if owner_appwrite_user_id is not None
            else []
        )
        self._files[(bucket_id, file_id)] = {
            "data": bytes(data),
            "mime_type": mime_type,
            "permissions": permissions,
            "file_name": file_name or f"{file_id}{PDF_EXTENSION}",
            "chunks_total": 1,
            "chunks_uploaded": 1 if complete else 0,
        }
        return self._info(bucket_id, file_id)

    def inspect_storage_file(self, *, bucket_id: str, file_id: str) -> StorageFileInfo:
        self.calls.append(("inspect", {"bucket_id": bucket_id, "file_id": file_id}))
        if self.fail_next_inspect is not None:
            exc, self.fail_next_inspect = self.fail_next_inspect, None
            raise exc
        if (bucket_id, file_id) not in self._files:
            raise StorageNotFoundError(bucket_id, file_id)
        return self._info(bucket_id, file_id)

    def open_storage_range(
        self, *, bucket_id: str, file_id: str, range_header: str | None
    ) -> tuple[bytes, dict[str, str]]:
        self.calls.append(
            (
                "download",
                {"bucket_id": bucket_id, "file_id": file_id, "range_header": range_header},
            )
        )
        if self.fail_next_download is not None:
            exc, self.fail_next_download = self.fail_next_download, None
            raise exc
        if (bucket_id, file_id) not in self._files:
            raise StorageNotFoundError(bucket_id, file_id)
        entry = self._files[(bucket_id, file_id)]
        return apply_range(bytes(entry["data"]), range_header, mime_type=str(entry["mime_type"]))

    def delete_storage_file(self, *, bucket_id: str, file_id: str) -> None:
        self.calls.append(("delete", {"bucket_id": bucket_id, "file_id": file_id}))
        if self.fail_next_delete is not None:
            exc, self.fail_next_delete = self.fail_next_delete, None
            raise exc
        self._files.pop((bucket_id, file_id), None)
        return None


# ---------------------------------------------------------------------------
# FastAPI factory (overridable in tests)
# ---------------------------------------------------------------------------


def get_storage_adapter() -> AppwriteStorageAdapter:
    """Resolve the real adapter from server env (never at import time).

    Tests override this FastAPI dependency with
    :class:`InMemoryStorageAdapter`; A0 wires the real factory only
    when ``APPWRITE_*`` env is present and fails closed (``RuntimeError``
    -> ``503`` at the handler) otherwise.
    """
    config = storage_config()
    return AppwriteStorageAdapter(
        endpoint=config["endpoint"],
        project_id=config["project_id"],
        api_key=config["api_key"],
        bucket_id=config["bucket_id"],
    )


# Alias for Annotated dependency declarations (FastAPI skill convention).
# Imported by API routers; tests override ``get_storage_adapter``.
try:  # pragma: no cover - import-time typing helper
    from typing import Annotated

    from fastapi import Depends

    StorageAdapterDep = Annotated[Any, Depends(get_storage_adapter)]
except Exception:  # pragma: no cover
    StorageAdapterDep = Any  # type: ignore

__all__ = [
    "APPWRITE_REQUIRED_SCOPES",
    "MAX_PDF_PAGES",
    "MAX_PDF_SIZE_BYTES",
    "PDF_EXTENSION",
    "PDF_MAGIC",
    "PDF_MIME_TYPE",
    "STORAGE_BUCKET_SETTINGS",
    "V2_CHROMA_COLLECTION",
    "AppwriteStorageAdapter",
    "InMemoryStorageAdapter",
    "RangeNotSatisfiableError",
    "StorageAdapterDep",
    "StorageConflictError",
    "StorageError",
    "StorageNotFoundError",
    "StorageUnavailableError",
    "apply_range",
    "default_bucket_id",
    "generate_appwrite_file_id",
    "get_storage_adapter",
    "is_pdf_filename",
    "make_resource_snapshot",
    "owner_file_permissions",
    "sha256_hex",
    "storage_config",
    "validate_pdf_bytes",
]
