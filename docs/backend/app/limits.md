# `app/limits.py`

[Source](../../../Backend/app/limits.py) · [Backend index](../README.md)

Defines the shared PDF budgets used by validation, storage, parsing, and the worker:

| Constant | Value | Meaning |
| --- | --- | --- |
| `MAX_PDF_SIZE_BYTES` | `25 * 1024 * 1024` = 26,214,400 | Maximum accepted PDF byte length (25 MiB) |
| `MAX_PDF_PAGES` | `200` | Maximum pages inspected/extracted from an accepted PDF |

There are no classes or functions. Importing the module only assigns these integers. Worker configuration cannot lower the public budgets; increasing a worker setting does not change API or bucket limits.
