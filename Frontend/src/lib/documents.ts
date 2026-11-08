export const ALL_DOCUMENTS_SCOPE = "all-documents";

export function chatScope(filename?: string) {
  return filename ? `document:${filename}` : ALL_DOCUMENTS_SCOPE;
}

export function chatHref(filename?: string) {
  return filename ? `/chats/${encodeURIComponent(filename)}` : "/chats";
}

export function documentTitle(filename: string) {
  return filename.replace(/\.pdf$/i, "").replace(/_/g, " ");
}

export function uploadFilename(filename: string) {
  return filename.replace(/\.pdf$/i, ".pdf");
}

export function formatFileSize(bytes: number) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
