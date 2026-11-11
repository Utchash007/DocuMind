# `app/jobs/__init__.py`

[Source](../../../../Backend/app/jobs/__init__.py) · [Backend index](../../README.md)

Re-exports durable queue operations and support types:

- [errors.md](errors.md): `JobError`, backoff calculation, bounded message formatting.
- [queue.md](queue.md): contexts/candidates, `JobQueueStore`, enqueue/find/claim/lease/progress/complete/fail/cancel, publication evaluation, upload reconciliation, and lease expiry.
- [reconcile.md](reconcile.md): reconciler/report and pure upload/lease/sweep decisions.

No functions or classes are defined locally. Imports construct declarations and metadata, not database sessions or provider requests. Worker ports are imported from [ports.md](ports.md) explicitly.
