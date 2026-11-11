"""Per-job processing orchestration.

:func:`DocumentProcessor.process` executes one claimed job end to end:

* ``process_document``: download the private PDF from storage (bounded
  streaming, size + SHA-256 verified) -> extract/page-bound chunk ->
  embed in batches of 16 -> write the fresh ``index_version``
  namespace -> fenced PostgreSQL publication.  Stage/progress writes
  are guarded by the live lease; a heartbeat thread renews the lease
  in the background and stops the work the moment it is lost.
* ``delete_document``: idempotently delete every known index version
  plus the private PDF, then complete (tombstone/hard-delete ordering
  is separate from provider cleanup).

No database transaction is ever held across a provider call: the
claim transaction is already committed when this runs, each progress
write is its own short transaction, and completion is one final
fenced transaction.  Lease loss, cancellation, or epoch invalidation
at any point yields ``stale``/``lease_lost`` outcomes without any
further writes -- the new owner (or the sweeper) takes it from there.
"""

from __future__ import annotations

import hashlib
import logging
import tempfile
import threading
import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID



from app.jobs.errors import (  # noqa: E402
    ERROR_EMBEDDING_PROVIDER,
    ERROR_FILE_TOO_LARGE,
    ERROR_FINGERPRINT_MISMATCH,
    ERROR_INDEX_WRITE,
    ERROR_JOB_TIMEOUT,
    ERROR_STORAGE_UNAVAILABLE,
    ERROR_UNEXPECTED,
    JobError,
    safe_message,
)
from app.jobs.ports import EmbedderPort, IndexPort, QueuePort, StoragePort  # noqa: E402
from app.jobs.queue import KIND_DELETE, KIND_PROCESS  # noqa: E402
from app.rag.embeddings import EmbeddingProviderError  # noqa: E402
from app.rag.indexing import IndexWriteError  # noqa: E402
from app.rag.pdf import (  # noqa: E402
    DEFAULT_MAX_PDF_BYTES,
    DEFAULT_MAX_PDF_PAGES,
    PdfError,
    PdfExtractionService,
)
from app.schemas.services import JobClaim  # noqa: E402

log = logging.getLogger("documind.worker.processor")

OUTCOME_SUCCEEDED = "succeeded"
OUTCOME_RETRY_WAIT = "retry_wait"
OUTCOME_FAILED = "failed"
OUTCOME_STALE = "stale"
OUTCOME_LEASE_LOST = "lease_lost"
OUTCOME_CANCELLED = "cancelled"

DOWNLOAD_CHUNK_BYTES = 1024 * 1024
EMBED_BATCH_SIZE = 16


def _kind_str(kind: Any) -> str:
    return str(getattr(kind, "value", kind))


@dataclass(frozen=True)
class ProcessorConfig:
    """Bounded worker limits (set consistently with API/bucket/UI)."""

    worker_id: str
    lease_seconds: int = 120
    max_file_bytes: int = DEFAULT_MAX_PDF_BYTES
    max_pages: int = DEFAULT_MAX_PDF_PAGES
    embed_batch_size: int = EMBED_BATCH_SIZE
    job_timeout_seconds: int = 3600
    backoff_base_seconds: int = 5
    backoff_cap_seconds: int = 3600

    @property
    def heartbeat_interval_seconds(self) -> int:
        return max(1, min(30, self.lease_seconds // 3))


@dataclass(frozen=True)
class ProcessOutcome:
    job_id: UUID
    kind: str
    status: str
    detail: str = ""


class _Heartbeat:
    """Background lease renewal; ``lost`` is set when it is revoked."""

    def __init__(
        self,
        queue: QueuePort,
        *,
        job_id: UUID,
        lease_token: int,
        worker_id: str,
        lease_seconds: int,
        interval_seconds: int,
    ) -> None:
        self._queue = queue
        self._job_id = job_id
        self._token = lease_token
        self._worker_id = worker_id
        self._lease_seconds = lease_seconds
        self._interval = interval_seconds
        self.lost = threading.Event()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, name="lease-heartbeat", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)

    def _run(self) -> None:
        while not self._stop.wait(self._interval):
            try:
                renewed = self._queue.renew_job_lease(
                    job_id=self._job_id,
                    lease_token=self._token,
                    worker_id=self._worker_id,
                    lease_seconds=self._lease_seconds,
                )
            except Exception as exc:  # transient DB errors do not kill the job
                log.warning("heartbeat for job %s failed: %s", self._job_id, safe_message(exc))
                continue
            if not renewed:
                self.lost.set()
                return


class DocumentProcessor:
    """Executes claimed jobs; all dependencies are injectable."""

    def __init__(
        self,
        *,
        queue: QueuePort,
        storage: StoragePort,
        embedder: EmbedderPort | None = None,
        index_service: IndexPort | None = None,
        extractor: PdfExtractionService | None = None,
        config: ProcessorConfig,
    ) -> None:
        self.queue = queue
        self.storage = storage
        self.embedder = embedder
        self.index_service = index_service
        self.extractor = extractor or PdfExtractionService(
            max_pages=config.max_pages, max_file_bytes=config.max_file_bytes
        )
        self.config = config

    # -- dispatch --------------------------------------------------------
    def process(self, claim: JobClaim) -> ProcessOutcome:
        kind = _kind_str(claim.kind)
        context = None
        try:
            context = self.queue.load_job_context(claim.job_id)
            if (
                context is None
                or context.status != "running"
                or context.lease_token != claim.lease_token
            ):
                return ProcessOutcome(claim.job_id, kind, OUTCOME_STALE, "claim no longer current")
            if kind == KIND_DELETE:
                return self._process_delete(claim, context)
            return self._process_document(claim, context)
        except JobError as exc:
            return self._fail(claim, exc.code, exc.message, exc.retryable, context=None)
        except EmbeddingProviderError as exc:
            return self._fail(claim, ERROR_EMBEDDING_PROVIDER, exc.message, True, context=None)
        except IndexWriteError as exc:
            return self._fail(claim, ERROR_INDEX_WRITE, exc.message, True, context=None)
        except PdfError as exc:
            return self._fail(claim, exc.code, exc.message, False, context=None)
        except Exception as exc:  # never let one job kill the worker loop
            log.exception("unexpected processor error for job %s", claim.job_id)
            return self._fail(claim, ERROR_UNEXPECTED, safe_message(exc), True, context=None)

    # -- process_document ------------------------------------------------
    def _process_document(self, claim: JobClaim, context: Any) -> ProcessOutcome:
        started = time.monotonic()
        heartbeat = self._start_heartbeat(claim)
        try:
            if self._timed_out(started, claim):
                return self._fail(claim, ERROR_JOB_TIMEOUT, "job exceeded its time budget", True, context)
            if self._still_live(context.target_document_id) is False:
                return self._cancel(claim, "document was deleted during processing")
            pdf_path = self._download_pdf(context)
            try:
                if self._timed_out(started, claim):
                    return self._fail(claim, ERROR_JOB_TIMEOUT, "job exceeded its time budget", True, context)
                if heartbeat.lost.is_set():
                    return self._lease_lost(claim, heartbeat)
                chunks = self.extractor.extract_pdf_chunks(
                    pdf_path,
                    file_name=context.storage_file_name or context.file_id or "document.pdf",
                    document_id=context.target_document_id,
                    index_version=context.index_version,
                )
            finally:
                pdf_path.unlink(missing_ok=True)
            if heartbeat.lost.is_set():
                return self._lease_lost(claim, heartbeat)
            if not self._progress(claim, stage="chunking", current=0, total=len(chunks)):
                return self._lease_lost(claim, heartbeat)
            if self._timed_out(started, claim):
                return self._fail(claim, ERROR_JOB_TIMEOUT, "job exceeded its time budget", True, context)
            embeddings = self._embed(claim, heartbeat, chunks)
            if isinstance(embeddings, ProcessOutcome):
                return embeddings
            if not self._progress(claim, stage="embedding", current=len(chunks), total=len(chunks)):
                return self._lease_lost(claim, heartbeat)
            if self._timed_out(started, claim):
                return self._fail(claim, ERROR_JOB_TIMEOUT, "job exceeded its time budget", True, context)
            if self.index_service is None:
                raise JobError(ERROR_UNEXPECTED, "index service is not configured")
            if not self._progress(claim, stage="indexing", current=0, total=len(chunks)):
                return self._lease_lost(claim, heartbeat)
            written = self.index_service.publish_index_version(
                user_id=context.owner_user_id,
                project_id=context.project_id,
                document_id=context.target_document_id,
                index_version=context.index_version,
                chunks=chunks,
                embeddings=embeddings,
            )
            if written != len(chunks):
                raise JobError(
                    ERROR_INDEX_WRITE,
                    f"index wrote {written} of {len(chunks)} chunks",
                )
            if not self._progress(claim, stage="indexing", current=written, total=len(chunks)):
                return self._lease_lost(claim, heartbeat)
            if heartbeat.lost.is_set():
                return self._lease_lost(claim, heartbeat)
            if not self._progress(claim, stage="publishing", current=written, total=len(chunks)):
                return self._lease_lost(claim, heartbeat)
            if self._still_live(context.target_document_id) is False:
                return self._cancel(claim, "document was deleted during processing")
            published = self.queue.complete_job(
                job_id=claim.job_id,
                lease_token=int(claim.lease_token),
                worker_id=self.config.worker_id,
                chunk_count=len(chunks),
            )
            if not published:
                return ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_STALE, "publication fenced out")
            return ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_SUCCEEDED)
        finally:
            heartbeat.stop()

    def _download_pdf(self, context: Any) -> Path:
        bucket_id = context.storage_bucket_id
        file_id = context.storage_file_id
        if bucket_id is None or file_id is None:
            raise JobError(ERROR_STORAGE_UNAVAILABLE, "job has no storage bucket/file reference")
        try:
            info = self.storage.inspect_storage_file(bucket_id=bucket_id, file_id=file_id)
        except Exception as exc:
            raise JobError(
                ERROR_STORAGE_UNAVAILABLE, f"storage inspection failed: {safe_message(exc)}"
            ) from exc
        size = int(info.size) if info.size is not None else context.expected_size_bytes
        if size is not None and size > self.config.max_file_bytes:
            raise JobError(
                ERROR_FILE_TOO_LARGE,
                f"stored PDF is {size} bytes, exceeding the {self.config.max_file_bytes}-byte limit",
            )
        handle = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        path = Path(handle.name)
        digest = hashlib.sha256()
        downloaded = 0
        expected = size
        try:
            while expected is None or downloaded < expected:
                start = downloaded
                end = expected - 1 if expected is not None else start + DOWNLOAD_CHUNK_BYTES - 1
                try:
                    chunk_bytes, _headers = self.storage.open_storage_range(
                        bucket_id=bucket_id,
                        file_id=file_id,
                        range_header=f"bytes={start}-{end}",
                    )
                except Exception as exc:
                    raise JobError(
                        ERROR_STORAGE_UNAVAILABLE,
                        f"storage read failed: {safe_message(exc)}",
                    ) from exc
                if not chunk_bytes:
                    if expected is not None and downloaded < expected:
                        raise JobError(
                            ERROR_STORAGE_UNAVAILABLE,
                            f"storage returned a short read ({downloaded} of {expected} bytes)",
                        )
                    break
                piece = chunk_bytes[: (expected - downloaded)] if expected is not None else chunk_bytes
                downloaded += len(piece)
                if downloaded > self.config.max_file_bytes:
                    raise JobError(
                        ERROR_FILE_TOO_LARGE,
                        f"downloaded PDF exceeds the {self.config.max_file_bytes}-byte limit",
                    )
                digest.update(piece)
                handle.write(piece)
            handle.flush()
        except BaseException:
            handle.close()
            path.unlink(missing_ok=True)
            raise
        handle.close()
        expected_sha = context.expected_sha256
        if expected_sha and digest.hexdigest() != str(expected_sha).lower():
            path.unlink(missing_ok=True)
            raise JobError(ERROR_FINGERPRINT_MISMATCH, "downloaded PDF does not match the expected fingerprint")
        return path

    def _embed(
        self, claim: JobClaim, heartbeat: _Heartbeat, chunks: Sequence[Any]
    ) -> list[list[float]] | ProcessOutcome:
        if self.embedder is None:
            raise JobError(ERROR_UNEXPECTED, "embedding service is not configured")
        texts = [chunk.text for chunk in chunks]
        embeddings: list[list[float]] = []
        batch_size = max(1, self.config.embed_batch_size)
        for start in range(0, len(texts), batch_size):
            if heartbeat.lost.is_set():
                return self._lease_lost(claim, heartbeat)
            batch = texts[start : start + batch_size]
            batch_embeddings = self.embedder.embed_texts(batch)
            if len(batch_embeddings) != len(batch):
                raise JobError(ERROR_UNEXPECTED, "embedding provider returned a mismatched count")
            embeddings.extend(batch_embeddings)
            if not self._progress(claim, stage="embedding", current=len(embeddings), total=len(texts)):
                return self._lease_lost(claim, heartbeat)
        return embeddings

    # -- delete_document ---------------------------------------------------
    def _process_delete(self, claim: JobClaim, context: Any) -> ProcessOutcome:
        heartbeat = self._start_heartbeat(claim)
        try:
            snapshot = context.resource_snapshot or {}
            seen: list[str] = []
            for version in snapshot.get("index_versions") or []:
                if str(version) not in seen:
                    seen.append(str(version))
            if snapshot.get("active_index_version"):
                version = str(snapshot["active_index_version"])
                if version not in seen:
                    seen.append(version)
            if context.doc_active_index_version is not None:
                version = str(context.doc_active_index_version)
                if version not in seen:
                    seen.append(version)
            if context.index_version is not None:
                version = str(context.index_version)
                if version not in seen:
                    seen.append(version)
            total = max(1, len(seen) + 1)
            if self.index_service is not None:
                for position, version in enumerate(seen, start=1):
                    if heartbeat.lost.is_set():
                        return self._lease_lost(claim, heartbeat)
                    self.index_service.delete_index_version(
                        user_id=context.owner_user_id,
                        project_id=context.project_id,
                        document_id=context.target_document_id,
                        index_version=version,
                    )
                    if not self._progress(claim, stage="deleting", current=position, total=total):
                        return self._lease_lost(claim, heartbeat)
            bucket_id = context.storage_bucket_id
            file_id = context.storage_file_id
            if bucket_id is not None and file_id is not None:
                try:
                    self.storage.delete_storage_file(bucket_id=bucket_id, file_id=file_id)
                except Exception as exc:
                    raise JobError(
                        ERROR_STORAGE_UNAVAILABLE,
                        f"storage delete failed: {safe_message(exc)}",
                    ) from exc
            if not self._progress(claim, stage="deleting", current=total, total=total):
                return self._lease_lost(claim, heartbeat)
            published = self.queue.complete_job(
                job_id=claim.job_id,
                lease_token=int(claim.lease_token),
                worker_id=self.config.worker_id,
            )
            if not published:
                return ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_STALE, "completion fenced out")
            return ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_SUCCEEDED)
        finally:
            heartbeat.stop()

    # -- helpers -----------------------------------------------------------
    def _start_heartbeat(self, claim: JobClaim) -> _Heartbeat:
        heartbeat = _Heartbeat(
            self.queue,
            job_id=claim.job_id,
            lease_token=int(claim.lease_token),
            worker_id=self.config.worker_id,
            lease_seconds=self.config.lease_seconds,
            interval_seconds=self.config.heartbeat_interval_seconds,
        )
        heartbeat.start()
        return heartbeat

    def _progress(
        self, claim: JobClaim, *, stage: str, current: int | None, total: int | None
    ) -> bool:
        try:
            return bool(
                self.queue.update_progress(
                    job_id=claim.job_id,
                    lease_token=int(claim.lease_token),
                    worker_id=self.config.worker_id,
                    stage=stage,
                    progress_current=current,
                    progress_total=total,
                )
            )
        except Exception as exc:
            log.warning("progress write for job %s failed: %s", claim.job_id, safe_message(exc))
            return False

    def _lease_lost(self, claim: JobClaim, heartbeat: _Heartbeat) -> ProcessOutcome:
        if not heartbeat.lost.is_set():
            log.info("stopping job %s (lease/progress guard failed)", claim.job_id)
        return ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_LEASE_LOST, "lease no longer current")

    def _still_live(self, target_document_id: UUID) -> bool | None:
        """Re-check liveness cheaply; None = unknown (assume live)."""
        checker = getattr(self.queue, "get_active_version", None)
        if checker is None:
            return None
        try:
            live, _active = checker(target_document_id)
        except Exception:
            return None
        return bool(live)

    def _timed_out(self, started: float, claim: JobClaim) -> bool:
        if time.monotonic() - started <= self.config.job_timeout_seconds:
            return False
        log.warning("job %s exceeded %ss budget", claim.job_id, self.config.job_timeout_seconds)
        return True

    def _cancel(self, claim: JobClaim, reason: str) -> ProcessOutcome:
        cancel = getattr(self.queue, "cancel_job", None)
        if cancel is not None:
            try:
                cancel(job_id=claim.job_id, reason=reason)
            except Exception:
                pass
        return ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_CANCELLED, reason)

    def _fail(
        self,
        claim: JobClaim,
        error_code: str,
        error_message: str,
        retryable: bool,
        context: Any | None,
    ) -> ProcessOutcome:
        try:
            applied = self.queue.fail_job(
                job_id=claim.job_id,
                lease_token=int(claim.lease_token),
                worker_id=self.config.worker_id,
                error_code=error_code,
                error_message=error_message[:500],
                retryable=retryable,
                backoff_base_seconds=self.config.backoff_base_seconds,
                backoff_cap_seconds=self.config.backoff_cap_seconds,
            )
        except Exception as exc:
            log.warning("fail write for job %s failed: %s", claim.job_id, safe_message(exc))
            return ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_STALE, "fail write failed")
        if not applied:
            return ProcessOutcome(claim.job_id, _kind_str(claim.kind), OUTCOME_STALE, "fail fenced out")
        will_retry = retryable
        if context is not None:
            will_retry = retryable and context.attempt_count < context.max_attempts
        status = OUTCOME_RETRY_WAIT if will_retry else OUTCOME_FAILED
        return ProcessOutcome(
            claim.job_id, _kind_str(claim.kind), status, f"{error_code}: {error_message}"
        )


__all__ = [
    "OUTCOME_CANCELLED",
    "OUTCOME_FAILED",
    "OUTCOME_LEASE_LOST",
    "OUTCOME_RETRY_WAIT",
    "OUTCOME_STALE",
    "OUTCOME_SUCCEEDED",
    "DocumentProcessor",
    "ProcessOutcome",
    "ProcessorConfig",
]
