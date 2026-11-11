"""Background PDF workers.

Run from ``Backend/``::

    python -m app.workers.pdf_worker

See :mod:`app.workers.pdf_worker` for deployment instructions,
concurrency and timeout limits, and status/error semantics.  This
package deliberately does not import the entry point: importing it as
a side effect breaks ``python -m`` execution.
"""

from __future__ import annotations

__all__ = []
