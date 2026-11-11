# `app/db/__init__.py`

[Source](../../../../Backend/app/db/__init__.py) · [Backend index](../../README.md)

Package import surface for `Base`, `utcnow`, `User`, `Project`, `Document`, `Conversation`, `Message`, and `ProcessingJob`. The additional `_models` import ensures table declarations register on `Base.metadata` for Alembic.

There are no locally defined functions or classes. Model imports construct metadata only; session factories and owned lookup helpers are imported explicitly from [session.md](session.md) and [queries.md](queries.md).
