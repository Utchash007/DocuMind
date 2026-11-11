"""Job error categories and bounded exponential backoff.

Every failure a job can record is classified into a stable
``last_error_code`` string plus a ``retryable`` flag.  Codes are part of
the operational contract: the API surfaces ``last_error_code`` /
``last_error_message`` through ``GET /jobs/{jobId}`` and the browser
polling UI, so they must stay stable and must never contain provider
payloads, credentials, or raw exception text beyond a safe summary.

Retryability rule (plan.md section 5.2): provider/transient failures
are retryable (bounded exponential backoff, then terminal ``failed``
when ``attempt_count`` reaches ``max_attempts``); input/content
failures are terminal -- reprocessing the same bytes cannot fix them.
"""

from __future__ import annotations

import hashlib

# Terminal error categories (retryable=False): the bytes/content are the
# problem; a retry would fail identically.
ERROR_FILE_TOO_LARGE = "file_too_large"
ERROR_PAGE_LIMIT_EXCEEDED = "page_limit_exceeded"
ERROR_PDF_MALFORMED = "pdf_malformed"
ERROR_PDF_TEXTLESS = "pdf_textless"
ERROR_FINGERPRINT_MISMATCH = "fingerprint_mismatch"
ERROR_STORAGE_MISSING = "storage_missing"
ERROR_UPLOAD_INCOMPLETE = "upload_incomplete"
ERROR_DOCUMENT_DELETED = "document_deleted"

# Retryable error categories: the environment is the problem; a later
# attempt may succeed.
ERROR_STORAGE_UNAVAILABLE = "storage_unavailable"
ERROR_EMBEDDING_PROVIDER = "embedding_provider_unavailable"
ERROR_INDEX_WRITE = "index_write_failed"
ERROR_LEASE_EXPIRED = "lease_expired"
ERROR_JOB_TIMEOUT = "job_timeout"
ERROR_UNEXPECTED = "unexpected"

ALL_ERROR_CODES = frozenset(
    {
        ERROR_FILE_TOO_LARGE,
        ERROR_PAGE_LIMIT_EXCEEDED,
        ERROR_PDF_MALFORMED,
        ERROR_PDF_TEXTLESS,
        ERROR_FINGERPRINT_MISMATCH,
        ERROR_STORAGE_MISSING,
        ERROR_UPLOAD_INCOMPLETE,
        ERROR_DOCUMENT_DELETED,
        ERROR_STORAGE_UNAVAILABLE,
        ERROR_EMBEDDING_PROVIDER,
        ERROR_INDEX_WRITE,
        ERROR_LEASE_EXPIRED,
        ERROR_JOB_TIMEOUT,
        ERROR_UNEXPECTED,
    }
)

TERMINAL_ERROR_CODES = frozenset(
    {
        ERROR_FILE_TOO_LARGE,
        ERROR_PAGE_LIMIT_EXCEEDED,
        ERROR_PDF_MALFORMED,
        ERROR_PDF_TEXTLESS,
        ERROR_FINGERPRINT_MISMATCH,
        ERROR_STORAGE_MISSING,
        ERROR_UPLOAD_INCOMPLETE,
        ERROR_DOCUMENT_DELETED,
    }
)

RETRYABLE_ERROR_CODES = ALL_ERROR_CODES - TERMINAL_ERROR_CODES


class JobError(Exception):
    """A classified job failure.

    ``code`` must be one of the stable categories above; ``message`` is
    a safe, bounded diagnostic summary (already truncated by the
    classification helpers).  ``retryable`` derives from the code so a
    caller cannot accidentally retry a content failure.  ``detail`` may
    carry implementation-controlled context (attempts, sizes) for logs.
    """

    def __init__(
        self,
        code: str,
        message: str,
        *,
        detail: str | None = None,
    ) -> None:
        if code not in ALL_ERROR_CODES:
            raise ValueError(f"unknown job error code: {code!r}")
        super().__init__(message)
        self.code = code
        self.message = message
        self.detail = detail

    @property
    def retryable(self) -> bool:
        return self.code in RETRYABLE_ERROR_CODES

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"JobError(code={self.code!r}, message={self.message!r})"


def safe_message(exc: BaseException, *, limit: int = 500) -> str:
    """Bounded, single-line summary of an unexpected exception for logs/DB.

    Never includes tokens/credentials: callers pass provider exceptions
    whose ``str()`` may be long; this truncates and flattens whitespace.
    """
    text = " ".join(str(exc).split())
    if len(text) > limit:
        text = text[: limit - 3] + "..."
    return text or type(exc).__name__


def compute_backoff_seconds(
    attempt: int,
    *,
    base_seconds: int = 5,
    cap_seconds: int = 3600,
    jitter_seed: str = "",
) -> int:
    """Bounded exponential backoff before the next attempt.

    ``attempt`` is the just-finished attempt count (1 after the first
    try): 1 -> base, 2 -> 2*base, 3 -> 4*base, ... capped at ``cap``.
    A deterministic jitter in ``[0, base)`` derived from ``jitter_seed``
    (job id) spreads retries from many jobs without ``random`` state,
    so backoff is reproducible in tests and across processes.
    """
    exponent = max(0, attempt - 1)
    delay = base_seconds * (2**exponent)
    if jitter_seed:
        digest = hashlib.sha256(jitter_seed.encode("utf-8")).hexdigest()
        jitter = int(digest[:8], 16) % max(1, base_seconds)
        delay += jitter
    return min(delay, cap_seconds)


__all__ = [
    "ALL_ERROR_CODES",
    "ERROR_DOCUMENT_DELETED",
    "ERROR_EMBEDDING_PROVIDER",
    "ERROR_FILE_TOO_LARGE",
    "ERROR_FINGERPRINT_MISMATCH",
    "ERROR_INDEX_WRITE",
    "ERROR_LEASE_EXPIRED",
    "ERROR_PAGE_LIMIT_EXCEEDED",
    "ERROR_PDF_MALFORMED",
    "ERROR_PDF_TEXTLESS",
    "ERROR_STORAGE_MISSING",
    "ERROR_STORAGE_UNAVAILABLE",
    "ERROR_UNEXPECTED",
    "ERROR_UPLOAD_INCOMPLETE",
    "RETRYABLE_ERROR_CODES",
    "TERMINAL_ERROR_CODES",
    "JobError",
    "compute_backoff_seconds",
    "safe_message",
]
