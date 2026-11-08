import type { Notebook } from "@/lib/types";
import { notebookScope } from "@/lib/notebooks";
import { notebooksReducer } from "@/store/notebooks/reducer";
import type { StoreSetter } from "@/store/types";
import type { WorkspaceStore } from "@/store/workspace-store";

export interface NotebooksState {
  notebooksMap: Record<string, Notebook>;
  storageError: string | null;
}

export const initialNotebooksState: NotebooksState = { notebooksMap: {}, storageError: null };

export class NotebooksActions {
  readonly #set: StoreSetter<WorkspaceStore>;
  readonly #get: () => WorkspaceStore;

  constructor(set: StoreSetter<WorkspaceStore>, get: () => WorkspaceStore) {
    this.#set = set;
    this.#get = get;
  }

  createNotebook = (title: string) => {
    const name = title.trim().slice(0, 120);
    if (!name || !this.#get().hydrated) return;
    const id = crypto.randomUUID();
    const now = new Date().toISOString();
    this.internal_dispatchNotebooks({ type: "add", notebook: { id, title: name, sourceFilenames: [], createdAt: now, updatedAt: now } });
    return id;
  };

  renameNotebook = (id: string, title: string) => {
    const name = title.trim().slice(0, 120);
    if (name) this.internal_dispatchNotebooks({ type: "update", id, changes: { title: name, updatedAt: new Date().toISOString() } });
  };

  touchNotebook = (id: string) => {
    this.internal_dispatchNotebooks({ type: "update", id, changes: { updatedAt: new Date().toISOString() } });
  };

  addNotebookSources = (id: string, filenames: string[]) => {
    const known = new Set(this.#get().documents.map((document) => document.filename));
    const available = filenames.filter((filename) => known.has(filename));
    if (available.length) this.internal_dispatchNotebooks({ type: "add-sources", id, filenames: available, updatedAt: new Date().toISOString() });
  };

  removeNotebookSource = (id: string, filename: string) => {
    if (this.#get().pendingMap[notebookScope(id)]) return false;
    this.internal_dispatchNotebooks({ type: "remove-source", id, filename, updatedAt: new Date().toISOString() });
    return true;
  };

  removeNotebook = (id: string) => {
    const state = this.#get();
    if (state.isUploading && state.uploadNotebookId === id) return false;
    state.clearThread(id);
    state.internal_dispatchNotes({ type: "remove-notebook", notebookId: id });
    this.internal_dispatchNotebooks({ type: "remove", id });
    return true;
  };

  reportStorageError = () => {
    this.#set({ storageError: "Browser storage is unavailable or full. Your latest changes may not survive a reload. Export important notes before leaving." });
  };

  internal_dispatchNotebooks = (action: Parameters<typeof notebooksReducer>[1]) => {
    this.#set((state) => ({ notebooksMap: notebooksReducer(state.notebooksMap, action) }));
  };
}

export type NotebooksAction = Pick<NotebooksActions, keyof NotebooksActions>;
