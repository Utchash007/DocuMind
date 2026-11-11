/**
 * NoteMind v2 API DTOs (TypeScript mirror).
 *
 * Source of truth: `Backend/app/schemas/` (Pydantic, snake_case Python /
 * camelCase JSON). Keep this file in lockstep with those DTOs and
 * `docs/v2-contracts.md`.
 *
 * Conventions:
 * - All wire fields are camelCase; timestamps are ISO-8601 strings;
 *   UUIDs are strings.
 * - Lists are `{ items, nextCursor }`; `nextCursor` is opaque.
 * - Errors are `{ detail: ApiError }` (FastAPI `detail` envelope).
 * - `generationToken`, job lease fields, `resourceSnapshot`,
 *   `appwriteFileId`, and `appwriteUserId` are never part of a DTO.
 */

// ---------------------------------------------------------------------------
// Enums (string unions; values match Backend/app/schemas/common.py)
// ---------------------------------------------------------------------------

export type DocumentStatus = "Pending" | "Processing" | "Completed" | "Failed";

export type MessageRole = "user" | "assistant" | "system";

export type GenerationStatus =
  | "pending"
  | "generating"
  | "completed"
  | "failed"
  | "cancelled";

export type JobKind = "process_document" | "delete_document";

export type JobStatus =
  | "awaiting_upload"
  | "queued"
  | "running"
  | "retry_wait"
  | "succeeded"
  | "failed"
  | "cancelled";

export type JobStage =
  | "uploading"
  | "extracting"
  | "chunking"
  | "embedding"
  | "indexing"
  | "publishing"
  | "deleting";

export type ErrorCode =
  | "unauthenticated"
  | "onboarding_required"
  | "forbidden"
  | "not_found"
  | "validation_error"
  | "conflict"
  | "duplicate_request_conflict"
  | "active_turn_in_progress"
  | "invalid_state"
  | "no_ready_sources"
  | "processing_in_progress"
  | "service_unavailable"
  | "internal_error";

// ---------------------------------------------------------------------------
// Errors (FastAPI `detail` envelope)
// ---------------------------------------------------------------------------

export interface ApiError {
  code: ErrorCode;
  message: string;
  jobId?: string | null;
  messageId?: string | null;
  documentId?: string | null;
  projectId?: string | null;
  conversationId?: string | null;
}

export interface ErrorEnvelope {
  detail: ApiError;
}

// ---------------------------------------------------------------------------
// Pagination
// ---------------------------------------------------------------------------

export interface CursorPageParams {
  cursor?: string | null;
  limit?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  nextCursor: string | null;
}

// ---------------------------------------------------------------------------
// Citations
// ---------------------------------------------------------------------------

/** Verified citation: identity, page, and exact text from a chunk. */
export interface Citation {
  documentId: string;
  fileName: string;
  pageNumber: number;
  chunkId: string;
  text: string;
  indexVersion: string;
}

// ---------------------------------------------------------------------------
// Users
// ---------------------------------------------------------------------------

export interface ApplicationUser {
  id: string;
  email: string;
  name: string | null;
  dateOfBirth: string | null; // ISO date (YYYY-MM-DD)
  onboardingCompleted: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ProfileUpdateRequest {
  name: string;
  dateOfBirth: string; // ISO date (YYYY-MM-DD)
}

// ---------------------------------------------------------------------------
// Projects
// ---------------------------------------------------------------------------

export interface Project {
  id: string;
  name: string;
  description: string | null;
  deletedAt: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface ProjectCreateRequest {
  name: string;
  description?: string | null;
}

export interface ProjectUpdateRequest {
  name?: string;
  description?: string | null;
}

export interface ProjectDeleteAccepted {
  projectId: string;
  accepted: boolean;
}

// ---------------------------------------------------------------------------
// Jobs (public view; lease/snapshot fields are server-only)
// ---------------------------------------------------------------------------

export interface ProcessingJob {
  id: string;
  documentId: string | null;
  projectId: string;
  targetDocumentId: string;
  kind: JobKind;
  status: JobStatus;
  stage: JobStage | null;
  attemptCount: number;
  maxAttempts: number;
  availableAt: string;
  indexVersion: string | null;
  progressCurrent: number | null;
  progressTotal: number | null;
  lastErrorCode: string | null;
  lastErrorMessage: string | null;
  createdAt: string;
  updatedAt: string;
  finishedAt: string | null;
}

// ---------------------------------------------------------------------------
// Documents
// ---------------------------------------------------------------------------

export interface Document {
  id: string;
  projectId: string;
  fileName: string;
  fileSize: number | null;
  mimeType: string | null;
  status: DocumentStatus;
  uploadCompletedAt: string | null;
  processingEpoch: number;
  activeIndexVersion: string | null;
  chunkCount: number | null;
  processedAt: string | null;
  processingError: string | null;
  deletedAt: string | null;
  createdAt: string;
  updatedAt: string;
}

/** 202 response for a coordinated document deletion (cleanup pending). */
export interface DocumentDeleteAccepted {
  projectId: string;
  documentId: string;
  jobId: string;
  accepted: boolean;
}

/**
 * 202 response for document upload and document retry.
 * Receiving it means the PDF is stored and queued — chunks are not
 * indexed yet; poll `document.status` / `job.status` for terminal state.
 */
export interface UploadAcceptance {
  document: Document;
  job: ProcessingJob;
}

// ---------------------------------------------------------------------------
// Conversations
// ---------------------------------------------------------------------------

export interface Conversation {
  id: string;
  projectId: string;
  title: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface ConversationCreateRequest {
  title?: string | null;
}

export interface ConversationUpdateRequest {
  title: string;
}

export interface ConversationDeleteAccepted {
  conversationId: string;
  accepted: boolean;
}

// ---------------------------------------------------------------------------
// Messages
// ---------------------------------------------------------------------------

export interface Message {
  id: string;
  conversationId: string;
  role: MessageRole;
  content: string;
  position: number;
  citations: Citation[] | null;
  metadata: Record<string, unknown> | null;
  clientRequestId: string | null;
  replyToMessageId: string | null;
  generationStatus: GenerationStatus | null;
  generationExpiresAt: string | null;
  createdAt: string;
}

/** `clientRequestId` is required: it is the send idempotency key. */
export interface MessageCreateRequest {
  content: string; // 1..8000 chars
  clientRequestId: string;
}

/** Both turns persisted before success is returned. */
export interface TurnResponse {
  userMessage: Message;
  assistantMessage: Message;
}

export interface MessageRetryRequest {
  clientRequestId?: string | null;
}

export interface MessageCancelResponse {
  userMessage: Message;
  cancelled: boolean;
}
