# Appwrite Authentication, File Upload, and PDF Processing Plan

## Recommended architecture

Use **Appwrite Auth + private Appwrite Storage + a Python Appwrite Function for background PDF processing**. Appwrite TablesDB will track ownership and processing jobs; FastAPI will handle authorized document queries using Chroma and Groq.

```text
Appwrite login → Server-validated session
                         ↓
                Authorized PDF upload
                         ↓
                  Appwrite Storage
                         ↓
                 Background Python job
                         ↓
          Extract text → Chunk → Embed → Chroma
                         ↓
              Mark document ready → Update UI
```

The implementation and **AI-RAG-DOC** project were reviewed on November 8, 2026. Email-code login and the **Notemind** storage bucket already exist. Server-side API authorization, ownership records, and background processing still need to be added.

## 1. Authenticate every protected entry point

Move the email-code session exchange into Next.js server endpoints using Appwrite's server SDK.

- Store the Appwrite session secret in a **Secure, HttpOnly cookie**.
- Verify the session with Appwrite before serving protected pages or data.
- Use Next.js `proxy.ts` for early redirects, with authoritative checks in page/data handlers, API routes, and server actions.
- Protect FastAPI independently: Next.js forwards a session-derived Appwrite JWT, which FastAPI validates through Appwrite.
- Derive the user ID from the verified identity.
- Apply origin/CSRF protection to cookie-authenticated mutations and rate limits to OTP endpoints.

Every route gets an explicit access policy. Sign-in, OTP endpoints, public help/legal content, and static assets form the public allowlist.

**Both authentication and ownership matter:** being logged in must only grant access to that user's resources.

## 2. Establish server-owned resource records

Create these Appwrite TablesDB tables:

| Table | Purpose |
| --- | --- |
| `notebooks` | Notebook identity, title, and owner |
| `documents` | Owner, Appwrite file ID, filename, processing status, active index version |
| `notebook_sources` | Associations between notebooks and documents |
| `processing_jobs` | Processing stage, attempts, progress, errors, and worker lease |

The server controls ownership, file mappings, permissions, and processing status. Users receive access only to their own records.

Use **document IDs and file IDs** as identities. Filenames become display labels, allowing different users to upload `research.pdf` safely.

Also scope browser-persisted notes and conversations by Appwrite user ID, resetting active state when accounts change.

## 3. Upload PDFs into private Appwrite Storage

For the initial implementation, route uploads through the authenticated API so the server controls permissions.

1. Validate the session and notebook ownership.
2. Validate the upload's type and size.
3. Reserve a document ID, file ID, and pending job **before uploading**.
4. Upload to Appwrite Storage with owner-only read access.
5. Return `202 Accepted` with `documentId` and `jobId` once storage succeeds.

Configure the existing bucket with file-level security, PDF restrictions, and appropriate size limits. File creation, permission changes, and deletion go through authorized server operations.

PDF previews and downloads use an authenticated endpoint, preserving citation page links and PDF range handling.

## 4. Process the PDF asynchronously

Configure a Python Appwrite Function for:

```text
buckets.<bucketId>.files.*.create
```

**Important:** Appwrite fires this event for individual upload parts. Processing starts only when `chunksUploaded === chunksTotal`. [Appwrite event documentation](https://appwrite.io/docs/apis/events)

The function will:

1. Resolve the trusted document/job record.
2. Claim the job exclusively.
3. Download the PDF from Appwrite.
4. Validate and extract its text page by page.
5. Create chunks with one-based page numbers.
6. Generate embeddings and write chunks to Chroma.
7. Publish the completed index version and mark the document ready.

Extract the reusable pipeline from `Backend/app/main.py` and `Backend/app/utils.py`.

Each indexed chunk carries:

```text
ownerId, documentId, indexVersion, filename, page, chunkId
```

### Job reliability

- Deterministic chunk IDs make duplicate executions safe.
- Persist attempts, progress, and expiring worker leases.
- Retry temporary provider failures with bounded backoff.
- Use a scheduled recovery function for missed events and stalled jobs.
- Publish an index version only after processing completes successfully.
- Bound processing batches to Appwrite's execution limits.
- Coordinate deletion and worker completion so late jobs cannot restore deleted documents.

Once the upload completes, processing continues independently of the browser session.

## 5. Show processing status and enforce query access

The source list will show:

```text
Uploading → Queued → Extracting → Chunking → Embedding → Ready
                                                    ↘ Failed / Retry
```

Use authenticated status polling while jobs are active, and reload their persisted status after refresh.

For questions, FastAPI will:

- Verify the user and notebook ownership.
- Resolve the notebook's authorized, ready document IDs.
- Apply the same owner/document/index-version restrictions to **both BM25 and dense retrieval**.
- Return citations containing the document ID, filename, and page.

Only ready documents become queryable. PDF access, retries, source attachment, and deletion receive the same ownership checks.

## 6. Implementation order and verification

| Phase | Deliverable |
| --- | --- |
| 1 | Server-side sessions and protected frontend/backend routes |
| 2 | TablesDB ownership model and account-scoped workspace state |
| 3 | Private Appwrite uploads and authenticated PDF access |
| 4 | Background processing, retries, and recovery |
| 5 | Processing UI and document-ID-based retrieval/citations |
| 6 | Migration, automated checks, and live integration verification |

Existing PDFs and browser-local records need explicit ownership mapping or re-upload during migration.

The key acceptance tests are:

- Two users cannot access each other's notebooks, PDFs, jobs, or answers.
- Expired sessions and direct unauthorized API calls are rejected.
- Multipart uploads start processing only after completion.
- Duplicate events, failures, and interrupted workers recover correctly.
- Refreshing restores job progress; citations open the correct PDF page.

**Start with authentication and ownership, then build storage and jobs on that foundation.**
