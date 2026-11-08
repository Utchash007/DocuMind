import type { ChatMessage, ChatThread, Citation, Notebook, QueryError, SavedNote } from "@/lib/types";
import type { WorkspaceStore } from "@/store/workspace-store";

function isRecord(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === "object" && !Array.isArray(value);
}

function isDate(value: unknown): value is string {
  return typeof value === "string" && Number.isFinite(Date.parse(value));
}

function isCitation(value: unknown): value is Citation {
  return isRecord(value) && typeof value.sentence === "string" && Number.isInteger(value.page) && Number(value.page) > 0 &&
    (value.filename == null || typeof value.filename === "string");
}

function isMessage(value: unknown): value is ChatMessage {
  return isRecord(value) && typeof value.id === "string" && (value.role === "user" || value.role === "assistant") &&
    typeof value.text === "string" && (value.citations === undefined || (Array.isArray(value.citations) && value.citations.every(isCitation))) &&
    (value.sourceFilenames === undefined || (Array.isArray(value.sourceFilenames) && value.sourceFilenames.every((name) => typeof name === "string")));
}

function validEntries<T>(value: unknown, validate: (item: unknown) => item is T): Record<string, T> {
  if (!isRecord(value)) return {};
  return Object.fromEntries(Object.entries(value).filter((entry): entry is [string, T] => validate(entry[1])));
}

export function restoreWorkspace(persisted: unknown, current: WorkspaceStore): WorkspaceStore {
  if (!isRecord(persisted)) return current;
  const notebooksMap = validEntries(persisted.notebooksMap, (value): value is Notebook =>
    isRecord(value) && typeof value.id === "string" && typeof value.title === "string" &&
    Array.isArray(value.sourceFilenames) && value.sourceFilenames.every((name) => typeof name === "string") &&
    isDate(value.createdAt) && isDate(value.updatedAt),
  );
  const threadsMap = validEntries(persisted.threadsMap, (value): value is ChatThread =>
    isRecord(value) && typeof value.notebookId === "string" && !!notebooksMap[value.notebookId] &&
    Array.isArray(value.messages) && value.messages.every(isMessage) && isDate(value.updatedAt),
  );
  const notesMap = validEntries(persisted.notesMap, (value): value is SavedNote =>
    isRecord(value) && typeof value.id === "string" && typeof value.notebookId === "string" && !!notebooksMap[value.notebookId] &&
    typeof value.title === "string" && typeof value.text === "string" && Array.isArray(value.citations) && value.citations.every(isCitation) &&
    isDate(value.createdAt) && isDate(value.updatedAt),
  );
  const errorsMap = validEntries(persisted.errorsMap, (value): value is QueryError =>
    isRecord(value) && typeof value.message === "string" && typeof value.query === "string",
  );
  return { ...current, notebooksMap, threadsMap, notesMap, errorsMap };
}
