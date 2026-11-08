import { API_BASE, apiFetch } from "@/services/api/api";
import type { DocumentInfo } from "@/lib/types";
import { uploadFilename } from "@/lib/documents";

interface FilesResponse {
  files: string[];
}

export async function fetchDocuments(signal?: AbortSignal): Promise<DocumentInfo[]> {
  const data = await apiFetch<FilesResponse>("/files", { signal });
  if (!Array.isArray(data.files) || data.files.some((filename) => typeof filename !== "string")) {
    throw new Error("The document list could not be read. Please refresh and try again.");
  }
  return [...new Set(data.files)].map((filename) => ({ filename }));
}

interface UploadResponse {
  message: string;
  chunks_count: number;
}

export async function uploadDocument(file: File, signal?: AbortSignal): Promise<DocumentInfo> {
  const filename = uploadFilename(file.name);
  const form = new FormData();
  form.append("file", file, filename);
  const data = await apiFetch<UploadResponse>("/upload", { method: "POST", body: form, signal }, 180_000);
  if (!Number.isInteger(data.chunks_count) || data.chunks_count < 1) {
    throw new Error("The server did not confirm that this PDF was indexed. Please try again.");
  }
  return { filename, chunksCount: data.chunks_count };
}

export function documentUrl(filename: string, page?: number) {
  return `${API_BASE}/files/${encodeURIComponent(filename)}${page ? `#page=${page}` : ""}`;
}
