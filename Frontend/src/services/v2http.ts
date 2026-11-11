import { API_BASE } from "@/services/api/api";
import type { ApiError, ErrorCode } from "@/lib/api-types";

export { API_BASE };

export class V2ApiError extends Error {
  readonly status: number;
  readonly code: ErrorCode | null;
  readonly jobId: string | null;
  readonly messageId: string | null;
  readonly documentId: string | null;
  readonly projectId: string | null;
  readonly conversationId: string | null;
  /** Raw parsed detail object when present (A0 owns api.ts; this is the v2 superset). */
  readonly detail: ApiError | string | unknown[] | null;

  constructor(message: string, status: number, detail: ApiError | string | unknown[] | null, code: ErrorCode | null) {
    super(message);
    this.name = "V2ApiError";
    this.status = status;
    this.detail = detail;
    this.code = code;
    this.jobId = detail && typeof detail === "object" && !Array.isArray(detail) ? ((detail as ApiError).jobId ?? null) : null;
    this.messageId = detail && typeof detail === "object" && !Array.isArray(detail) ? ((detail as ApiError).messageId ?? null) : null;
    this.documentId = detail && typeof detail === "object" && !Array.isArray(detail) ? ((detail as ApiError).documentId ?? null) : null;
    this.projectId = detail && typeof detail === "object" && !Array.isArray(detail) ? ((detail as ApiError).projectId ?? null) : null;
    this.conversationId = detail && typeof detail === "object" && !Array.isArray(detail) ? ((detail as ApiError).conversationId ?? null) : null;
  }
}

export function isV2ApiError(error: unknown): error is V2ApiError {
  return error instanceof V2ApiError;
}

export function errorCodeOf(error: unknown): ErrorCode | null {
  return isV2ApiError(error) ? error.code : null;
}

export function isAbortError(error: unknown, signal?: AbortSignal): boolean {
  if (signal?.aborted) return true;
  return error instanceof DOMException && error.name === "AbortError";
}

function parseDetail(payload: unknown): ApiError | string | unknown[] | null {
  if (!payload || typeof payload !== "object") return null;
  if (!("detail" in payload)) {
    return "code" in payload && "message" in payload ? payload as ApiError : null;
  }
  const detail = (payload as { detail: unknown }).detail;
  if (typeof detail === "string" || Array.isArray(detail)) return detail as string | unknown[];
  if (detail && typeof detail === "object") return detail as ApiError;
  return null;
}

function detailToMessage(detail: ApiError | string | unknown[] | null, status: number): string {
  if (typeof detail === "string" && detail.trim()) return detail;
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => (item && typeof item === "object" && "msg" in item ? String((item as { msg?: unknown }).msg ?? "") : ""))
      .filter(Boolean);
    if (messages.length) return messages.join(". ");
  }
  if (detail && typeof detail === "object" && "message" in detail && typeof (detail as ApiError).message === "string" && (detail as ApiError).message.trim()) {
    return (detail as ApiError).message;
  }
  if (status === 401) return "Your session has expired. Please sign in again.";
  if (status === 403) return "You do not have access to this workspace.";
  if (status === 404) return "The requested item was not found. It may have been deleted or you may not have access to it.";
  if (status === 409) return "This action conflicts with the current state. Please refresh and try again.";
  if (status === 422) return "Some of the information you sent was invalid. Please check it and try again.";
  if (status === 503) return "A service is temporarily unavailable. Please try again in a moment.";
  return "The server could not complete this request. Please try again.";
}

function detailToCode(detail: ApiError | string | unknown[] | null): ErrorCode | null {
  if (detail && typeof detail === "object" && !Array.isArray(detail) && "code" in detail) {
    const code = (detail as ApiError).code;
    const known: ErrorCode[] = [
      "unauthenticated", "onboarding_required", "forbidden", "not_found", "validation_error",
      "conflict", "duplicate_request_conflict", "active_turn_in_progress", "invalid_state",
      "no_ready_sources", "processing_in_progress", "service_unavailable", "internal_error",
    ];
    if (typeof code === "string" && (known as string[]).includes(code)) return code as ErrorCode;
  }
  return null;
}

export function v2ErrorMessage(error: unknown): string {
  if (isV2ApiError(error)) return error.message;
  return error instanceof Error ? error.message : "Something went wrong. Please try again.";
}

export function v2ResponseError(payload: unknown, status: number): V2ApiError {
  const detail = parseDetail(payload);
  return new V2ApiError(detailToMessage(detail, status), status, detail, detailToCode(detail));
}

export function queryString(params: Record<string, string | number | null | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === null || value === undefined || value === "") continue;
    search.set(key, String(value));
  }
  const text = search.toString();
  return text ? `?${text}` : "";
}

export interface V2FetchOptions {
  signal?: AbortSignal;
  timeoutMs?: number;
  headers?: Record<string, string>;
}

/**
 * Typed v2 fetch over the same-origin proxy (API_BASE).
 * - Handles 204 / empty bodies without JSON parsing.
 * - Normalizes the FastAPI `detail` envelope (string | validation array | ApiError object).
 * - Preserves abort-by-caller and timeout semantics; throws V2ApiError otherwise.
 */
export async function v2Fetch<T>(path: string, init: RequestInit & V2FetchOptions = {}, timeoutMs = 30_000): Promise<T> {
  const timeout = AbortSignal.timeout(timeoutMs);
  const signal = init.signal ? AbortSignal.any([init.signal, timeout]) : timeout;
  const headers: Record<string, string> = { ...(init.headers as Record<string, string> | undefined) };
  const hasBody = init.body !== undefined && init.body !== null;
  const isForm = typeof FormData !== "undefined" && init.body instanceof FormData;
  if (!headers["Content-Type"] && !headers["content-type"] && hasBody && !isForm) headers["Content-Type"] = "application/json";

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...init, headers, signal, cache: "no-store" });
  } catch (error) {
    if (init.signal?.aborted || (error instanceof DOMException && error.name === "AbortError" && init.signal?.aborted)) throw error;
    if (timeout.aborted) throw new V2ApiError("This is taking longer than expected. Please try again.", 408, null, null);
    throw new V2ApiError("Could not connect to the backend. Check that the API server is running and try again.", 0, null, null);
  }

  if (response.status === 204) return undefined as T;
  const payload: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    throw v2ResponseError(payload, response.status);
  }
  if (payload === null) {
    // Empty successful body (treat as undefined for void/204-like responses).
    return undefined as T;
  }
  return payload as T;
}

/** For endpoints that may return 202 with a body or 204 with no body. */
export async function v2FetchMaybeEmpty<T>(path: string, init: RequestInit & V2FetchOptions = {}, timeoutMs = 30_000): Promise<T | undefined> {
  return v2Fetch<T | undefined>(path, init, timeoutMs);
}

export function newIdempotencyKey(): string {
  return crypto.randomUUID();
}
