# `app/schemas/jobs.py`

[Source](../../../../Backend/app/schemas/jobs.py) · [Backend index](../../README.md)

`ProcessingJob` is the public job-status DTO. Required fields: `id`, `project_id`, `target_document_id`, `kind`, `status`, `attempt_count`, `max_attempts`, `available_at`, `created_at`, `updated_at`. Nullable fields: live `document_id`, `stage`, `index_version`, progress current/total, last error code/message, and `finished_at`.

It omits the immutable owner UUID, lease owner/token/expiry, target epoch, and resource snapshot. Those remain internal queue state. `TERMINAL_JOB_STATUSES` contains `succeeded`, `failed`, and `cancelled` enum values.

## Functions

### `ProcessingJob.is_terminal(self) -> bool`

- **Arguments:** A `ProcessingJob` DTO instance.
- **Returns:** Whether its current status belongs to `TERMINAL_JOB_STATUSES`.
- **Work:** Performs a set membership check. It does not query PostgreSQL, advance a job, or infer completion from document state.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-processingjob-is-terminal"></a>

#### Line-by-line execution

[Current source: lines 40–41](../../../../Backend/app/schemas/jobs.py#L40-L41). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  40 |     def is_terminal(self) -> bool:
  41 |         return self.status in TERMINAL_JOB_STATUSES
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L40 | Define `ProcessingJob.is_terminal`; bind its arguments when called. The body executes only when invoked. |
| L41 | Compute the return value: compare whether `self.status` is contained in `TERMINAL_JOB_STATUSES`. Return that value and end this call; enclosing finally/context-manager cleanup still runs before control reaches the caller. |

<!-- END LINE WALKTHROUGH -->
