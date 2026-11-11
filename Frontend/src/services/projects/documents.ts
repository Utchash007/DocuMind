import { API_BASE, V2ApiError, queryString, v2Fetch, v2ResponseError } from "@/services/v2http";
import type {
  CursorPageParams, Document, DocumentDeleteAccepted, PaginatedResponse, UploadAcceptance,
} from "@/lib/api-types";

const seg = (id: string) => encodeURIComponent(id);
export const MAX_PDF_SIZE_BYTES = 25 * 1024 * 1024;

export function listDocuments(projectId: string, params: CursorPageParams & { signal?: AbortSignal } = {}): Promise<PaginatedResponse<Document>> {
  return v2Fetch<PaginatedResponse<Document>>(
    `/projects/${seg(projectId)}/documents${queryString({ cursor: params.cursor, limit: params.limit ?? 50 })}`,
    { signal: params.signal },
  );
}

export function getDocument(projectId: string, documentId: string, signal?: AbortSignal): Promise<Document> {
  return v2Fetch<Document>(`/projects/${seg(projectId)}/documents/${seg(documentId)}`, { signal });
}

export async function deleteDocument(projectId: string, documentId: string, signal?: AbortSignal): Promise<DocumentDeleteAccepted> {
  const result = await v2Fetch<DocumentDeleteAccepted | undefined>(
    `/projects/${seg(projectId)}/documents/${seg(documentId)}`, { method: "DELETE", signal }, 30_000,
  );
  return result ?? { projectId, documentId, jobId: "", accepted: true };
}

export function retryDocument(projectId: string, documentId: string, signal?: AbortSignal): Promise<UploadAcceptance> {
  return v2Fetch<UploadAcceptance>(`/projects/${seg(projectId)}/documents/${seg(documentId)}/retry`, { method: "POST", signal }, 30_000);
}

/** Authorized inline PDF URL (byte ranges supported server-side). */
export function documentFileUrl(projectId: string, documentId: string, page?: number): string {
  const base = `${API_BASE}/projects/${seg(projectId)}/documents/${seg(documentId)}/file`;
  return page ? `${base}#page=${page}` : base;
}

export function validatePdfFile(file: File): string | null {
  if (!/\.pdf$/i.test(file.name)) return "Only PDF documents are supported.";
  if (file.size === 0) return "This file is empty. Choose a PDF with text.";
  if (file.size > MAX_PDF_SIZE_BYTES) return "PDFs must be 25 MiB or smaller (up to 200 pages).";
  return null;
}

export interface UploadOptions {
  idempotencyKey?: string;
  signal?: AbortSignal;
  onProgress?: (loadedBytes: number, totalBytes: number) => void;
  timeoutMs?: number;
}

/**
 * Multipart upload returning 202 {document, job}.
 * Uses XHR for upload progress and the shared v2 error parser.
 * The browser sets multipart Content-Type/boundary.
 */
export function uploadDocument(projectId: string, file: File, options: UploadOptions = {}): Promise<UploadAcceptance> {
  const url = `${API_BASE}/projects/${seg(projectId)}/documents`;
  const timeoutMs = options.timeoutMs ?? 180_000;
  if (options.signal?.aborted) return Promise.reject(new DOMException("Aborted", "AbortError"));
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    let settled = false;
    const cleanup = () => options.signal?.removeEventListener("abort", abort);
    const fail = (error: Error) => { if (!settled) { settled = true; cleanup(); reject(error); } };
    const succeed = (value: UploadAcceptance) => { if (!settled) { settled = true; cleanup(); resolve(value); } };
    const abort = () => {
      fail(new DOMException("Aborted", "AbortError"));
      xhr.abort();
    };

    xhr.open("POST", url);
    xhr.withCredentials = true;
    xhr.timeout = timeoutMs;
    if (options.idempotencyKey) xhr.setRequestHeader("Idempotency-Key", options.idempotencyKey);
    xhr.upload.addEventListener("progress", (event) => {
      if (event.lengthComputable) options.onProgress?.(event.loaded, event.total);
    });
    xhr.addEventListener("load", () => {
      if (options.signal?.aborted) { fail(new DOMException("Aborted", "AbortError")); return; }
      let payload: unknown = null;
      try { payload = xhr.responseText ? JSON.parse(xhr.responseText) : null; } catch { payload = null; }
      if (xhr.status >= 200 && xhr.status < 300) {
        if (payload && typeof payload === "object" && "document" in payload && "job" in payload) succeed(payload as UploadAcceptance);
        else fail(new V2ApiError("The server returned an unreadable response. Please try again.", 502, null, null));
        return;
      }
      fail(v2ResponseError(payload, xhr.status));
    });
    xhr.addEventListener("error", () => fail(new V2ApiError("Could not connect to the backend. Check that the API server is running and try again.", 0, null, null)));
    xhr.addEventListener("abort", () => fail(new DOMException("Aborted", "AbortError")));
    xhr.addEventListener("timeout", () => fail(new V2ApiError("This is taking longer than expected. Please try again.", 408, null, null)));

    const form = new FormData();
    form.append("file", file, file.name);
    options.signal?.addEventListener("abort", abort, { once: true });
    if (options.signal?.aborted) { abort(); return; }
    try { xhr.send(form); } catch (error) { fail(error instanceof Error ? error : new Error("Upload could not start.")); }
  });
}
