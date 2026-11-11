# `app/schemas/documents.py`

[Source](../../../../Backend/app/schemas/documents.py) · [Backend index](../../README.md)

Contains three camelCase Pydantic DTOs and **no locally implemented functions**.

| Model | Fields and purpose |
| --- | --- |
| `Document` | UUID `id`, `project_id`; display `file_name`; optional `file_size`/`mime_type`; `DocumentStatus`; upload completion timestamp; `processing_epoch`; optional `active_index_version`, `chunk_count`, `processed_at`, `processing_error`, `deleted_at`; required creation/update timestamps |
| `DocumentDeleteAccepted` | `project_id`, `document_id`, cleanup `job_id`, and `accepted=True`; returned with HTTP 202 |
| `UploadAcceptance` | `document: Document` and `job: ProcessingJob`; upload/retry HTTP 202 envelope |

The document response omits `appwrite_file_id` and `content_sha256`. Its version/epoch fields describe processing state; a filename is only a label. Processing errors are expected to be safe summaries supplied by the caller.

`UploadAcceptance` describes the persisted states at response time. An interrupted/incomplete upload can still be `awaiting_upload`; a 202 response does not itself guarantee queue readiness or indexed chunks. Follow the job/document status. Validation and serialization are provided by Pydantic; the model does not perform upload, deletion, polling, or ownership checks.
