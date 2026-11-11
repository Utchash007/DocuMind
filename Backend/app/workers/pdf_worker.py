"""PDF worker entry point -- run with ``python -m app.workers.pdf_worker``.

## Run / deploy

From ``Backend/`` (the worker is a separate process from the API;
run it under the same supervisor as the API, e.g. systemd / Docker /
PM2 -- the supervisor restarts it, and persisted jobs survive both
API and worker restarts because PostgreSQL is the queue):

```powershell
cd Backend
python -m app.workers.pdf_worker
```

Useful flags: ``--worker-id``, ``--poll-interval``, ``--concurrency``,
``--lease-seconds``, ``--once`` (one reconcile + one claim batch, then
exit -- handy for manual runs and smoke tests).

```powershell
python -m app.workers.pdf_worker --once --concurrency 1
```

## Environment

| Variable | Required | Purpose |
| --- | --- | --- |
| ``DATABASE_URL`` | yes | PostgreSQL for the job queue (same DB as the API) |
| ``CHROMA_API_KEY`` / ``CHROMA_TENANT`` / ``CHROMA_DATABASE`` | yes (process) | Chroma Cloud for ``documind_chunks_v2`` |
| ``DOCUMIND_EMBEDDING_PROVIDER`` | no | ``hf`` (default, 384-d) or ``jina`` (1024-d) |
| ``HF_API_KEY`` (or ``HF_TOKEN``) | when provider ``hf`` | Hugging Face embeddings |
| ``JINA_API_KEY`` | when provider ``jina`` | Jina AI embeddings (``JINA_EMBEDDING_MODEL`` optional) |
| ``DOCUMIND_ALLOW_MOCK_EMBEDDINGS`` | no | ``1`` enables deterministic mock vectors -- **test/dev only**; production must leave it unset (JOB-12 -- a mock-indexed document is never marked ``Completed`` silently; see below) |
| ``DOCUMIND_WORKER_*`` | no | Limits below (``_ID``, ``_POLL_INTERVAL_SECONDS``, ``_CONCURRENCY``, ``_LEASE_SECONDS``, ``_MAX_FILE_BYTES``, ``_MAX_PAGES``, ``_JOB_TIMEOUT_SECONDS``, ``_BACKOFF_BASE_SECONDS``, ``_BACKOFF_CAP_SECONDS``, ``_AWAITING_UPLOAD_TTL_SECONDS``, ``_SWEEP_GRACE_SECONDS``) |

The storage adapter (``app.services.storage``) resolves server configuration
when the worker starts; missing required settings fail startup.

## Concurrency and timeout limits

* ``concurrency`` (default 2) is both the claim batch size and the
  thread-pool size: at most that many jobs are claimed/in-flight per
  worker process.  Scale horizontally by running more worker
  processes -- ``SKIP LOCKED`` claims keep them exclusive.
* ``lease_seconds`` (default 120) is the claim lease; the heartbeat
  renews it every ``lease/3`` (capped at 30s).  A dead worker's jobs
  are requeued/failed by the reconciler after expiry -- never stolen
  early.
* ``job_timeout_seconds`` (default 3600) bounds one attempt
  (checked at stage boundaries; retryable ``job_timeout``).
* Provider timeouts: Hugging Face 30s, bounded streaming downloads,
  and the file/page limits (``max_file_bytes`` default 25 MiB,
  ``max_pages`` default 200) -- shared with the API,
  bucket, and UI limits.

## Status and error semantics (what to watch)

Jobs move ``awaiting_upload -> queued -> running -> retry_wait |
succeeded | failed | cancelled`` with stages
``uploading/extracting/chunking/embedding/indexing/publishing/deleting``.
Public status is visible via ``GET /jobs/{jobId}`` and the
document row (``Pending/Processing/Completed/Failed``):

* only a fenced publication (running job + unexpired lease/token +
  expected epoch + live document/project) may set ``Completed``;
  stale workers write only into their obsolete ``index_version``
  namespace, never into the active pointer;
* retryable failures (``embedding_provider_unavailable``,
  ``index_write_failed``, ``storage_unavailable``, ``lease_expired``,
  ``job_timeout``, ``unexpected``) go to ``retry_wait`` with bounded
  exponential backoff (base 5s, doubling per attempt, cap 3600s) and
  become terminal ``failed`` at ``max_attempts`` (default 3);
* terminal failures (``file_too_large``, ``page_limit_exceeded``,
  ``pdf_malformed``, ``pdf_textless``, ``fingerprint_mismatch``,
  ``storage_missing``, ``upload_incomplete``, ``document_deleted``)
  fail immediately -- retrying the same bytes cannot fix them;
* every failure records a bounded ``last_error_code`` +
  ``last_error_message``; provider payloads/credentials never appear.

Operational signals: queue depth/age (``queued``/``retry_wait`` older
than the backoff window), ``failed`` jobs, lease expiries, and
embedding/index provider errors -- log lines are prefixed
``documind.worker.*`` and carry resource IDs (never secrets).
"""

from __future__ import annotations

import argparse
import logging
import os
import signal
import socket
import sys
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any



from app.jobs.ports import EmbedderPort, IndexPort, QueuePort, StoragePort  # noqa: E402
from app.jobs.queue import JobQueueStore  # noqa: E402
from app.jobs.reconcile import (  # noqa: E402
    DEFAULT_AWAITING_UPLOAD_TTL_SECONDS,
    DEFAULT_SWEEP_GRACE_SECONDS,
    ReconcileReport,
    Reconciler,
)
from app.rag.embeddings import (  # noqa: E402
    PROVIDER_JINA,
    EmbeddingConfig,
    EmbeddingService,
)
from app.rag.indexing import IndexService  # noqa: E402
from app.rag.pdf import DEFAULT_MAX_PDF_BYTES, DEFAULT_MAX_PDF_PAGES  # noqa: E402
from app.workers.processor import DocumentProcessor, ProcessOutcome, ProcessorConfig  # noqa: E402

log = logging.getLogger("documind.worker")


def _env_int(env: dict[str, str], name: str, default: int) -> int:
    raw = env.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        log.warning("invalid integer for %s=%r; using default %s", name, raw, default)
        return default


def _default_worker_id() -> str:
    return f"worker-{socket.gethostname()}-{os.getpid()}-{uuid.uuid4().hex[:6]}"


@dataclass
class WorkerConfig:
    """All worker limits; build with :meth:`from_env` or flags."""

    worker_id: str = field(default_factory=_default_worker_id)
    poll_interval_seconds: int = 2
    concurrency: int = 2
    lease_seconds: int = 120
    max_file_bytes: int = DEFAULT_MAX_PDF_BYTES
    max_pages: int = DEFAULT_MAX_PDF_PAGES
    job_timeout_seconds: int = 3600
    backoff_base_seconds: int = 5
    backoff_cap_seconds: int = 3600
    awaiting_upload_ttl_seconds: int = DEFAULT_AWAITING_UPLOAD_TTL_SECONDS
    sweep_grace_seconds: int = DEFAULT_SWEEP_GRACE_SECONDS
    batch_size: int = 50

    def __post_init__(self) -> None:
        if self.max_file_bytes < DEFAULT_MAX_PDF_BYTES or self.max_pages < DEFAULT_MAX_PDF_PAGES:
            raise ValueError("Worker PDF limits must cover the API's 25 MiB / 200-page budget.")
        self.concurrency = max(1, self.concurrency)
        self.poll_interval_seconds = max(0, self.poll_interval_seconds)
        self.lease_seconds = max(5, self.lease_seconds)

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None, **overrides: Any) -> "WorkerConfig":
        source = env if env is not None else os.environ
        values: dict[str, Any] = dict(
            worker_id=source.get("DOCUMIND_WORKER_ID", "").strip() or _default_worker_id(),
            poll_interval_seconds=_env_int(source, "DOCUMIND_WORKER_POLL_INTERVAL_SECONDS", 2),
            concurrency=_env_int(source, "DOCUMIND_WORKER_CONCURRENCY", 2),
            lease_seconds=_env_int(source, "DOCUMIND_WORKER_LEASE_SECONDS", 120),
            max_file_bytes=_env_int(source, "DOCUMIND_WORKER_MAX_FILE_BYTES", DEFAULT_MAX_PDF_BYTES),
            max_pages=_env_int(source, "DOCUMIND_WORKER_MAX_PAGES", DEFAULT_MAX_PDF_PAGES),
            job_timeout_seconds=_env_int(source, "DOCUMIND_WORKER_JOB_TIMEOUT_SECONDS", 3600),
            backoff_base_seconds=_env_int(source, "DOCUMIND_WORKER_BACKOFF_BASE_SECONDS", 5),
            backoff_cap_seconds=_env_int(source, "DOCUMIND_WORKER_BACKOFF_CAP_SECONDS", 3600),
            awaiting_upload_ttl_seconds=_env_int(
                source, "DOCUMIND_WORKER_AWAITING_UPLOAD_TTL_SECONDS", DEFAULT_AWAITING_UPLOAD_TTL_SECONDS
            ),
            sweep_grace_seconds=_env_int(
                source, "DOCUMIND_WORKER_SWEEP_GRACE_SECONDS", DEFAULT_SWEEP_GRACE_SECONDS
            ),
        )
        values.update({k: v for k, v in overrides.items() if v is not None})
        return cls(**values)

    def processor_config(self) -> ProcessorConfig:
        return ProcessorConfig(
            worker_id=self.worker_id,
            lease_seconds=self.lease_seconds,
            max_file_bytes=self.max_file_bytes,
            max_pages=self.max_pages,
            job_timeout_seconds=self.job_timeout_seconds,
            backoff_base_seconds=self.backoff_base_seconds,
            backoff_cap_seconds=self.backoff_cap_seconds,
        )


def build_storage_adapter() -> StoragePort:
    """Lazily load the configured Appwrite storage adapter."""
    try:
        from app.services.storage import get_storage_adapter  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "A3 storage adapter (app.services.storage) "
            "is not available; the worker cannot process uploads until "
            "it lands (see docs/v2-contracts.md section 6)."
        ) from exc
    # Resolves endpoint/project/api_key/bucket from the environment
    # (raises RuntimeError if unconfigured — fail fast, as before).
    return get_storage_adapter()  # type: ignore[return-value]


def build_default_dependencies(
    config: WorkerConfig,
) -> tuple[JobQueueStore, StoragePort, EmbedderPort, IndexPort]:
    """Production wiring: PG queue, private storage, embeddings, Chroma."""
    embedding_config = EmbeddingConfig.from_env()
    if embedding_config.provider == PROVIDER_JINA and not (
        os.environ.get("JINA_API_KEY") or ""
    ).strip():
        raise RuntimeError(
            "JINA_API_KEY is required when DOCUMIND_EMBEDDING_PROVIDER=jina"
        )
    from app.db.session import make_worker_session_factory

    store = JobQueueStore(make_worker_session_factory())
    storage = build_storage_adapter()
    if embedding_config.allow_mock:
        log.warning(
            "DOCUMIND_ALLOW_MOCK_EMBEDDINGS is enabled: documents will be indexed "
            "with deterministic mock vectors (test/development only).",
        )
    embedder = EmbeddingService(embedding_config)
    index_service = IndexService()
    return store, storage, embedder, index_service


def run_worker_once(
    config: WorkerConfig,
    *,
    queue: QueuePort,
    storage: StoragePort,
    embedder: EmbedderPort | None = None,
    index_service: IndexPort | None = None,
    reconciler: Reconciler | None = None,
    processor: DocumentProcessor | None = None,
) -> tuple[ReconcileReport, list[ProcessOutcome]]:
    """One loop iteration: reconcile, claim one batch, process it.

    Returned for tests, manual runs, and the ``--once`` flag.  Each
    reconciliation pass and each job is isolated: failures are logged
    and retried on a later iteration, never fatal to the loop.
    """
    if reconciler is None:
        reconciler = Reconciler(
            queue,  # type: ignore[arg-type]
            storage=storage,
            index_service=index_service,
            awaiting_upload_ttl_seconds=config.awaiting_upload_ttl_seconds,
            sweep_grace_seconds=config.sweep_grace_seconds,
            batch_size=config.batch_size,
            backoff_base_seconds=config.backoff_base_seconds,
            backoff_cap_seconds=config.backoff_cap_seconds,
        )
    report = reconciler.run_once()
    claims = queue.claim_next_jobs(
        worker_id=config.worker_id, limit=config.concurrency, lease_seconds=config.lease_seconds
    )
    if not claims:
        return report, []
    if processor is None:
        processor = DocumentProcessor(
            queue=queue,
            storage=storage,
            embedder=embedder,
            index_service=index_service,
            config=config.processor_config(),
        )
    outcomes: list[ProcessOutcome] = []
    if config.concurrency <= 1 or len(claims) <= 1:
        for claim in claims:
            outcomes.append(processor.process(claim))
        return report, outcomes
    with ThreadPoolExecutor(max_workers=config.concurrency, thread_name_prefix="pdf-job") as pool:
        futures = {pool.submit(processor.process, claim): claim for claim in claims}
        for future in as_completed(futures):
            claim = futures[future]
            try:
                outcomes.append(future.result())
            except Exception:
                log.exception("worker crashed processing job %s", claim.job_id)
    return report, outcomes


def run_worker(
    config: WorkerConfig,
    *,
    queue: QueuePort,
    storage: StoragePort,
    embedder: EmbedderPort | None = None,
    index_service: IndexPort | None = None,
    stop_event: threading.Event | None = None,
) -> None:
    """Poll loop.  ``SIGTERM``/``SIGINT`` stop after in-flight jobs."""
    stop = stop_event or threading.Event()
    reconciler = Reconciler(
        queue,  # type: ignore[arg-type]
        storage=storage,
        index_service=index_service,
        awaiting_upload_ttl_seconds=config.awaiting_upload_ttl_seconds,
        sweep_grace_seconds=config.sweep_grace_seconds,
        batch_size=config.batch_size,
        backoff_base_seconds=config.backoff_base_seconds,
        backoff_cap_seconds=config.backoff_cap_seconds,
    )
    processor = DocumentProcessor(
        queue=queue,
        storage=storage,
        embedder=embedder,
        index_service=index_service,
        config=config.processor_config(),
    )
    log.info(
        "worker %s starting (poll=%ss concurrency=%s lease=%ss)",
        config.worker_id,
        config.poll_interval_seconds,
        config.concurrency,
        config.lease_seconds,
    )
    while not stop.is_set():
        try:
            report, outcomes = run_worker_once(
                config,
                queue=queue,
                storage=storage,
                embedder=embedder,
                index_service=index_service,
                reconciler=reconciler,
                processor=processor,
            )
        except Exception:
            log.exception("worker iteration failed; will retry next poll")
            report, outcomes = ReconcileReport(), []
        for outcome in outcomes:
            log.info(
                "job %s -> %s (%s)",
                outcome.job_id,
                outcome.status,
                outcome.detail or outcome.kind,
            )
        if report.actions:
            for action in report.actions[:20]:
                log.info("reconcile: %s", action)
        if not outcomes and not stop.is_set():
            stop.wait(config.poll_interval_seconds)
    log.info("worker %s stopped", config.worker_id)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pdf_worker", description="DocuMind PDF job worker")
    parser.add_argument("--worker-id", default=None)
    parser.add_argument("--poll-interval", type=int, default=None)
    parser.add_argument("--concurrency", type=int, default=None)
    parser.add_argument("--lease-seconds", type=int, default=None)
    parser.add_argument("--once", action="store_true", help="one reconcile + one claim batch, then exit")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")

    # Local-dev parity with app/main.py: load the repository-root .env
    # without overriding variables already set in the process environment.
    from app.config import load_application_env

    load_application_env()

    config = WorkerConfig.from_env(
        worker_id=args.worker_id,
        poll_interval_seconds=args.poll_interval,
        concurrency=args.concurrency,
        lease_seconds=args.lease_seconds,
    )
    store, storage, embedder, index_service = build_default_dependencies(config)

    if args.once:
        report, outcomes = run_worker_once(
            config, queue=store, storage=storage, embedder=embedder, index_service=index_service
        )
        for outcome in outcomes:
            print(f"job {outcome.job_id} -> {outcome.status} ({outcome.detail})")
        print(f"reconciled: {len(report.actions)} action(s)")
        return 0

    stop = threading.Event()

    def _request_stop(signum: int, _frame: Any) -> None:
        log.info("received signal %s; stopping after in-flight jobs", signum)
        stop.set()

    try:
        signal.signal(signal.SIGTERM, _request_stop)
        signal.signal(signal.SIGINT, _request_stop)
    except (ValueError, OSError):  # not the main thread (tests, embedded)
        pass
    run_worker(config, queue=store, storage=storage, embedder=embedder, index_service=index_service, stop_event=stop)
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "WorkerConfig",
    "build_default_dependencies",
    "build_storage_adapter",
    "main",
    "run_worker",
    "run_worker_once",
]
