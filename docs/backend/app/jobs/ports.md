# `app/jobs/ports.py`

[Source](../../../../Backend/app/jobs/ports.py) · [Backend index](../../README.md)

Structural `Protocol` interfaces for worker dependency injection. All methods below are declarations (`...`): their bodies perform no work and fall through to `None`; return annotations describe what concrete adapters must produce. These ports neither import HTTP routers nor commit transactions. The concrete queue wrapper supplies one short transaction per call.

## Storage port

### `StoragePort.inspect_storage_file(self, *, bucket_id: str, file_id: str) -> StorageFileInfo`

**Arguments:** Bucket and reserved file IDs. **Returns:** Contractually size/MIME/chunk completion metadata. **Operation:** Inspect the private object outside SQL; missing/provider errors are handled by worker/reconciler. Implementation: [storage.md](../services/storage.md).

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-storageport-inspect-storage-file"></a>

#### Line-by-line execution

[Current source: lines 34–35](../../../../Backend/app/jobs/ports.py#L34-L35). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |

**Declared result:** `StorageFileInfo`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  34 |     def inspect_storage_file(self, *, bucket_id: str, file_id: str) -> StorageFileInfo:
  35 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L34 | Define `StoragePort.inspect_storage_file`; bind its arguments when called. The body executes only when invoked. |
| L35 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `StoragePort.open_storage_range(self, *, bucket_id: str, file_id: str, range_header: str | None) -> tuple[bytes, dict[str, str]]`

**Arguments:** Storage IDs and optional Range header. **Returns:** Bytes and response headers. **Operation:** Download the requested representation; workers pass `None` for the full PDF and validate its bytes afterward.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-storageport-open-storage-range"></a>

#### Line-by-line execution

[Current source: lines 37–40](../../../../Backend/app/jobs/ports.py#L37-L40). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |
| `range_header` | `str \| None`; required; keyword-only | Optional HTTP byte-range selector; parsing determines full, partial, or unsatisfiable behavior. |

**Declared result:** `tuple[bytes, dict[str, str]]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  37 |     def open_storage_range(
  38 |         self, *, bucket_id: str, file_id: str, range_header: str | None
  39 |     ) -> tuple[bytes, dict[str, str]]:
  40 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L37 | Define `StoragePort.open_storage_range`; bind its arguments when called. The body executes only when invoked. |
| L38 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `bucket_id` with annotation `str`. Appwrite bucket identifier. Declare parameter `file_id` with annotation `str`. Reserved Appwrite storage-object identifier. Declare parameter `range_header` with annotation `str \| None`. Optional HTTP byte-range selector; parsing determines full, partial, or unsatisfiable behavior. |
| L39 | Finish/continue the signature; the declared return annotation is `tuple[bytes, dict[str, str]]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L40 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `StoragePort.delete_storage_file(self, *, bucket_id: str, file_id: str) -> None`

**Arguments:** Storage IDs. **Returns:** No result. **Operation:** Idempotent private-file deletion; missing objects count as success.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-storageport-delete-storage-file"></a>

#### Line-by-line execution

[Current source: lines 42–43](../../../../Backend/app/jobs/ports.py#L42-L43). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `bucket_id` | `str`; required; keyword-only | Appwrite bucket identifier. |
| `file_id` | `str`; required; keyword-only | Reserved Appwrite storage-object identifier. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  42 |     def delete_storage_file(self, *, bucket_id: str, file_id: str) -> None:
  43 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L42 | Define `StoragePort.delete_storage_file`; bind its arguments when called. The body executes only when invoked. |
| L43 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

## Embedding/index ports

### `EmbedderPort.embed_texts(self, texts: Sequence[str]) -> list[list[float]]`

**Arguments:** Ordered chunk texts. **Returns:** Corresponding vector list. **Operation:** Batch provider embedding/validation, implemented by [EmbeddingService](../rag/embeddings.md).

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-embedderport-embed-texts"></a>

#### Line-by-line execution

[Current source: lines 49–50](../../../../Backend/app/jobs/ports.py#L49-L50). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `texts` | `Sequence[str]`; required; positional or keyword | Input text sequence; embedding output preserves its order. |

**Declared result:** `list[list[float]]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  49 |     def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
  50 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L49 | Define `EmbedderPort.embed_texts`; bind its arguments when called. The body executes only when invoked. |
| L50 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `IndexPort.publish_index_version(self, *, user_id, project_id, document_id, index_version, chunks, embeddings=None) -> int`

**Arguments:** Four UUID/string scope IDs, `PdfChunk` sequence, optional matching vectors. **Returns:** Written record count. **Operation:** Upsert a version namespace outside SQL; it does not move the database's active pointer. Implementation: [IndexService](../rag/indexing.md).

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-indexport-publish-index-version"></a>

#### Line-by-line execution

[Current source: lines 56–66](../../../../Backend/app/jobs/ports.py#L56-L66). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `user_id` | `UUID \| str`; required; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID \| str`; required; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID \| str`; required; keyword-only | Document UUID; filenames do not establish document identity. |
| `index_version` | `UUID \| str`; required; keyword-only | UUID of one document's vector-index namespace, separate from its active publication pointer. |
| `chunks` | `Sequence[PdfChunk]`; required; keyword-only | PDF text chunks with the metadata required by this operation. |
| `embeddings` | `Sequence[Sequence[float]] \| None`; default `None`; keyword-only | Per-chunk numeric vectors supplied for indexing. |

**Declared result:** `int`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  56 |     def publish_index_version(
  57 |         self,
  58 |         *,
  59 |         user_id: UUID | str,
  60 |         project_id: UUID | str,
  61 |         document_id: UUID | str,
  62 |         index_version: UUID | str,
  63 |         chunks: Sequence[PdfChunk],
  64 |         embeddings: Sequence[Sequence[float]] | None = None,
  65 |     ) -> int:
  66 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L56 | Define `IndexPort.publish_index_version`; bind its arguments when called. The body executes only when invoked. |
| L57 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L58 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L59 | Declare parameter `user_id` with annotation `UUID \| str`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L60 | Declare parameter `project_id` with annotation `UUID \| str`. Project UUID used to constrain resource lookup or provider metadata. |
| L61 | Declare parameter `document_id` with annotation `UUID \| str`. Document UUID; filenames do not establish document identity. |
| L62 | Declare parameter `index_version` with annotation `UUID \| str`. UUID of one document's vector-index namespace, separate from its active publication pointer. |
| L63 | Declare parameter `chunks` with annotation `Sequence[PdfChunk]`. PDF text chunks with the metadata required by this operation. |
| L64 | Declare parameter `embeddings` with annotation `Sequence[Sequence[float]] \| None`. Per-chunk numeric vectors supplied for indexing. |
| L65 | Finish/continue the signature; the declared return annotation is `int`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L66 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `IndexPort.delete_index_version(self, *, user_id=None, project_id=None, document_id, index_version) -> None`

**Arguments:** Document/version identities and optional owner/project identities. **Returns:** No result. **Operation:** Idempotent scoped deletion of one version's records.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-indexport-delete-index-version"></a>

#### Line-by-line execution

[Current source: lines 68–76](../../../../Backend/app/jobs/ports.py#L68-L76). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `user_id` | `UUID \| str \| None`; default `None`; keyword-only | Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| `project_id` | `UUID \| str \| None`; default `None`; keyword-only | Project UUID used to constrain resource lookup or provider metadata. |
| `document_id` | `UUID \| str`; required; keyword-only | Document UUID; filenames do not establish document identity. |
| `index_version` | `UUID \| str`; required; keyword-only | UUID of one document's vector-index namespace, separate from its active publication pointer. |

**Declared result:** `None`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  68 |     def delete_index_version(
  69 |         self,
  70 |         *,
  71 |         user_id: UUID | str | None = None,
  72 |         project_id: UUID | str | None = None,
  73 |         document_id: UUID | str,
  74 |         index_version: UUID | str,
  75 |     ) -> None:
  76 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L68 | Define `IndexPort.delete_index_version`; bind its arguments when called. The body executes only when invoked. |
| L69 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L70 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L71 | Declare parameter `user_id` with annotation `UUID \| str \| None`. Internal PostgreSQL user UUID used for owner scoping, not the Appwrite account ID. |
| L72 | Declare parameter `project_id` with annotation `UUID \| str \| None`. Project UUID used to constrain resource lookup or provider metadata. |
| L73 | Declare parameter `document_id` with annotation `UUID \| str`. Document UUID; filenames do not establish document identity. |
| L74 | Declare parameter `index_version` with annotation `UUID \| str`. UUID of one document's vector-index namespace, separate from its active publication pointer. |
| L75 | Finish/continue the signature; the declared return annotation is `None`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L76 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

## Queue port

### `QueuePort.claim_next_jobs(self, *, worker_id: str, limit: int, lease_seconds: int) -> list[JobClaim]`

**Arguments:** Worker identity, batch cap, lease duration. **Returns:** Durable fenced claims. **Operation:** Select/lock due work, assign leases/tokens, commit before processing.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-queueport-claim-next-jobs"></a>

#### Line-by-line execution

[Current source: lines 82–85](../../../../Backend/app/jobs/ports.py#L82-L85). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `limit` | `int`; required; keyword-only | Maximum requested result/batch size; validation and clamping appear in the body or annotation. |
| `lease_seconds` | `int`; required; keyword-only | Lease duration in seconds; positive-duration validation is not implicit in this parameter. |

**Declared result:** `list[JobClaim]`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  82 |     def claim_next_jobs(
  83 |         self, *, worker_id: str, limit: int, lease_seconds: int
  84 |     ) -> list[JobClaim]:
  85 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L82 | Define `QueuePort.claim_next_jobs`; bind its arguments when called. The body executes only when invoked. |
| L83 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. Declare parameter `limit` with annotation `int`. Maximum requested result/batch size; validation and clamping appear in the body or annotation. Declare parameter `lease_seconds` with annotation `int`. Lease duration in seconds; positive-duration validation is not implicit in this parameter. |
| L84 | Finish/continue the signature; the declared return annotation is `list[JobClaim]`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L85 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `QueuePort.renew_job_lease(self, *, job_id: UUID, lease_token: int, worker_id: str, lease_seconds: int) -> bool`

**Arguments:** Exact claim identity and extension interval. **Returns:** Whether renewal succeeded. **Operation:** Extend an unexpired matching running lease.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-queueport-renew-job-lease"></a>

#### Line-by-line execution

[Current source: lines 87–90](../../../../Backend/app/jobs/ports.py#L87-L90). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `lease_token` | `int`; required; keyword-only | Monotonic claim token used to reject stale worker writes. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `lease_seconds` | `int`; required; keyword-only | Lease duration in seconds; positive-duration validation is not implicit in this parameter. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  87 |     def renew_job_lease(
  88 |         self, *, job_id: UUID, lease_token: int, worker_id: str, lease_seconds: int
  89 |     ) -> bool:
  90 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L87 | Define `QueuePort.renew_job_lease`; bind its arguments when called. The body executes only when invoked. |
| L88 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. Declare parameter `lease_token` with annotation `int`. Monotonic claim token used to reject stale worker writes. Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. Declare parameter `lease_seconds` with annotation `int`. Lease duration in seconds; positive-duration validation is not implicit in this parameter. |
| L89 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L90 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `QueuePort.update_progress(self, *, job_id: UUID, lease_token: int, worker_id: str, stage=None, progress_current=None, progress_total=None) -> bool`

**Arguments:** Claim identity and optional stage/counters. **Returns:** Whether the current claim accepted the update. **Operation:** Persist progress under lease fencing; concrete queue behavior is in [queue.md](queue.md).

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-queueport-update-progress"></a>

#### Line-by-line execution

[Current source: lines 92–102](../../../../Backend/app/jobs/ports.py#L92-L102). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `lease_token` | `int`; required; keyword-only | Monotonic claim token used to reject stale worker writes. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `stage` | `str \| None`; default `None`; keyword-only | Public job stage to record, such as extracting, embedding, indexing, or publishing. |
| `progress_current` | `int \| None`; default `None`; keyword-only | Current completed-work counter; null means do not update it. |
| `progress_total` | `int \| None`; default `None`; keyword-only | Total-work counter; null means do not update it. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
  92 |     def update_progress(
  93 |         self,
  94 |         *,
  95 |         job_id: UUID,
  96 |         lease_token: int,
  97 |         worker_id: str,
  98 |         stage: str | None = None,
  99 |         progress_current: int | None = None,
 100 |         progress_total: int | None = None,
 101 |     ) -> bool:
 102 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L92 | Define `QueuePort.update_progress`; bind its arguments when called. The body executes only when invoked. |
| L93 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L94 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L95 | Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. |
| L96 | Declare parameter `lease_token` with annotation `int`. Monotonic claim token used to reject stale worker writes. |
| L97 | Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. |
| L98 | Declare parameter `stage` with annotation `str \| None`. Public job stage to record, such as extracting, embedding, indexing, or publishing. |
| L99 | Declare parameter `progress_current` with annotation `int \| None`. Current completed-work counter; null means do not update it. |
| L100 | Declare parameter `progress_total` with annotation `int \| None`. Total-work counter; null means do not update it. |
| L101 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L102 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `QueuePort.complete_job(self, *, job_id: UUID, lease_token: int, worker_id: str, chunk_count: int | None = None) -> bool`

**Arguments:** Claim identity and optional published chunk count. **Returns:** Whether completion/publication succeeded. **Operation:** Recheck current lease/resource/epoch and finalize atomically in SQL.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-queueport-complete-job"></a>

#### Line-by-line execution

[Current source: lines 104–107](../../../../Backend/app/jobs/ports.py#L104-L107). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `lease_token` | `int`; required; keyword-only | Monotonic claim token used to reject stale worker writes. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `chunk_count` | `int \| None`; default `None`; keyword-only | Number of chunks to record when publishing a processed document. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 104 |     def complete_job(
 105 |         self, *, job_id: UUID, lease_token: int, worker_id: str, chunk_count: int | None = None
 106 |     ) -> bool:
 107 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L104 | Define `QueuePort.complete_job`; bind its arguments when called. The body executes only when invoked. |
| L105 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. Declare parameter `lease_token` with annotation `int`. Monotonic claim token used to reject stale worker writes. Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. Declare parameter `chunk_count` with annotation `int \| None`. Number of chunks to record when publishing a processed document. |
| L106 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L107 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `QueuePort.fail_job(self, *, job_id: UUID, lease_token: int, worker_id: str, error_code: str, error_message: str, retryable: bool, **backoff: Any) -> bool`

**Arguments:** Claim identity, safe classified failure, retry decision, optional backoff parameters. **Returns:** Whether the current claim transitioned. **Operation:** Persist delayed retry or terminal failure; a stale claim cannot replace current state.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-queueport-fail-job"></a>

#### Line-by-line execution

[Current source: lines 109–120](../../../../Backend/app/jobs/ports.py#L109-L120). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `job_id` | `UUID`; required; keyword-only | Durable processing-job UUID. |
| `lease_token` | `int`; required; keyword-only | Monotonic claim token used to reject stale worker writes. |
| `worker_id` | `str`; required; keyword-only | Worker identity that must match the stored lease owner for guarded writes. |
| `error_code` | `str`; required; keyword-only | Machine-readable failure category stored or exposed by the operation. |
| `error_message` | `str`; required; keyword-only | Human-readable failure detail; truncation alone does not redact sensitive content. |
| `retryable` | `bool`; required; keyword-only | Whether the failure may be retried while the attempt budget remains. |
| `backoff` | `Any`; implicitly supplied/collected; ** keyword extras | Caller-supplied backoff; each read, transformation, and validation is traced below. |

**Declared result:** `bool`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 109 |     def fail_job(
 110 |         self,
 111 |         *,
 112 |         job_id: UUID,
 113 |         lease_token: int,
 114 |         worker_id: str,
 115 |         error_code: str,
 116 |         error_message: str,
 117 |         retryable: bool,
 118 |         **backoff: Any,
 119 |     ) -> bool:
 120 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L109 | Define `QueuePort.fail_job`; bind its arguments when called. The body executes only when invoked. |
| L110 | Declare parameter `self` without a type annotation. The current instance; instance methods receive it automatically. |
| L111 | Make every following named parameter keyword-only; callers cannot supply those values positionally. |
| L112 | Declare parameter `job_id` with annotation `UUID`. Durable processing-job UUID. |
| L113 | Declare parameter `lease_token` with annotation `int`. Monotonic claim token used to reject stale worker writes. |
| L114 | Declare parameter `worker_id` with annotation `str`. Worker identity that must match the stored lease owner for guarded writes. |
| L115 | Declare parameter `error_code` with annotation `str`. Machine-readable failure category stored or exposed by the operation. |
| L116 | Declare parameter `error_message` with annotation `str`. Human-readable failure detail; truncation alone does not redact sensitive content. |
| L117 | Declare parameter `retryable` with annotation `bool`. Whether the failure may be retried while the attempt budget remains. |
| L118 | Declare parameter `backoff` with annotation `Any`. Caller-supplied backoff; its uses and transformations are traced below. |
| L119 | Finish/continue the signature; the declared return annotation is `bool`. An annotation documents the contract but does not enforce ordinary Python return values. |
| L120 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->

### `QueuePort.load_job_context(self, job_id: UUID) -> Any`

**Arguments:** Durable job UUID. **Returns:** Normally a detached `JobContext`, or `None` if missing. **Operation:** Read the provider-input/resource snapshot under a short SQL scope; subsequent provider work uses copied values.

<!-- BEGIN LINE WALKTHROUGH -->
<a id="walk-queueport-load-job-context"></a>

#### Line-by-line execution

[Current source: lines 122–123](../../../../Backend/app/jobs/ports.py#L122-L123). Line numbers below are file line numbers, not a separate example.

**Parameters and binding**

| Parameter | Type / default | Meaning |
| --- | --- | --- |
| `self` | not annotated; implicitly supplied/collected; positional or keyword | The current instance; instance methods receive it automatically. |
| `job_id` | `UUID`; required; positional or keyword | Durable processing-job UUID. |

**Declared result:** `Any`. The overview above explains the returned value and failure cases.

**Numbered source**

```text
 122 |     def load_job_context(self, job_id: UUID) -> Any:
 123 |         ...
```

**What each line does** (blank lines are visual separators)

| Line | Detailed operation |
| --- | --- |
| L122 | Define `QueuePort.load_job_context`; bind its arguments when called. The body executes only when invoked. |
| L123 | Protocol declaration only: the ellipsis body performs no work. Concrete adapters implement this signature; calling this placeholder itself falls through to None. |

<!-- END LINE WALKTHROUGH -->
