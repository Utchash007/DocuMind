import { isUuid, type LocalNote } from "@/lib/projects";

function isRecord(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === "object" && !Array.isArray(value);
}

function isDate(value: unknown): value is string {
  return typeof value === "string" && Number.isFinite(Date.parse(value));
}

function isCitation(value: unknown): boolean {
  return isRecord(value) && typeof value.text === "string" && value.text.trim().length > 0 &&
    typeof value.fileName === "string" && value.fileName.trim().length > 0 &&
    typeof value.documentId === "string" && isUuid(value.documentId) &&
    typeof value.indexVersion === "string" && isUuid(value.indexVersion) &&
    typeof value.chunkId === "string" && value.chunkId.trim().length > 0 &&
    typeof value.pageNumber === "number" && Number.isInteger(value.pageNumber) && value.pageNumber >= 1;
}

export function isLocalNote(value: unknown): value is LocalNote {
  return isRecord(value) && typeof value.id === "string" && typeof value.projectId === "string" &&
    typeof value.title === "string" && typeof value.text === "string" &&
    Array.isArray(value.citations) && value.citations.every(isCitation) &&
    isDate(value.createdAt) && isDate(value.updatedAt);
}

export function notesStorageKey(userId: string): string {
  return `notemind-notes:${encodeURIComponent(userId)}`;
}

export function draftsStorageKey(userId: string): string {
  return `notemind-drafts:${encodeURIComponent(userId)}`;
}

export function readLocalNotes(userId: string): LocalNote[] {
  if (typeof window === "undefined" || !userId) return [];
  try {
    const raw = localStorage.getItem(notesStorageKey(userId));
    if (!raw) return [];
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(isLocalNote);
  } catch {
    return [];
  }
}

export function writeLocalNotes(userId: string, notes: LocalNote[]): boolean {
  if (typeof window === "undefined" || !userId) return false;
  try {
    localStorage.setItem(notesStorageKey(userId), JSON.stringify(notes));
    return true;
  } catch {
    return false;
  }
}

export function readLocalDrafts(userId: string): Record<string, string> {
  if (typeof window === "undefined" || !userId) return {};
  try {
    const raw = localStorage.getItem(draftsStorageKey(userId));
    if (!raw) return {};
    const parsed: unknown = JSON.parse(raw);
    if (!isRecord(parsed)) return {};
    return Object.fromEntries(Object.entries(parsed).filter(([, v]) => typeof v === "string")) as Record<string, string>;
  } catch {
    return {};
  }
}

export function writeLocalDrafts(userId: string, drafts: Record<string, string>): boolean {
  if (typeof window === "undefined" || !userId) return false;
  try {
    localStorage.setItem(draftsStorageKey(userId), JSON.stringify(drafts));
    return true;
  } catch {
    return false;
  }
}
