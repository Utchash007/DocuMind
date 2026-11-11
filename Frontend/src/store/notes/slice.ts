import { noteTitle, type LocalNote } from "@/lib/projects";
import type { Citation, Message } from "@/lib/api-types";
import { notesReducer } from "@/store/notes/reducer";
import { readLocalDrafts, readLocalNotes, writeLocalDrafts, writeLocalNotes } from "@/store/persistence";
import type { StoreSetter } from "@/store/types";
import type { WorkspaceStore } from "@/store/workspace-store";

export interface NotesState {
  notes: LocalNote[];
  notesOwner: string | null;
  drafts: Record<string, string>;
  storageError: string | null;
}

export const initialNotesState: NotesState = {
  notes: [],
  notesOwner: null,
  drafts: {},
  storageError: null,
};

export class NotesActions {
  readonly #set: StoreSetter<WorkspaceStore>;
  readonly #get: () => WorkspaceStore;

  constructor(set: StoreSetter<WorkspaceStore>, get: () => WorkspaceStore) {
    this.#set = set;
    this.#get = get;
  }

  loadNotesForUser = (userId: string | null) => {
    if (!userId) {
      this.#set({ notes: [], notesOwner: null, drafts: {} });
      return;
    }
    this.#set({ notes: readLocalNotes(userId), notesOwner: userId, drafts: readLocalDrafts(userId) });
  };

  saveNote = (projectId: string, title: string, text: string, citations: Citation[] = [], id?: string): string | null => {
    const owner = this.#get().notesOwner;
    if (!owner || !projectId || !title.trim() || !text.trim()) return null;
    const existing = id ? this.#get().notes.find((note) => note.id === id) : undefined;
    const now = new Date().toISOString();
    const note: LocalNote = {
      id: existing?.id ?? crypto.randomUUID(), projectId,
      title: title.trim().slice(0, 120), text: text.trim(), citations: existing?.citations ?? citations,
      createdAt: existing?.createdAt ?? now, updatedAt: now,
    };
    this.internal_dispatchNotes({ type: "save", note });
    this.#persistNotes();
    return note.id;
  };

  removeNote = (id: string) => {
    this.internal_dispatchNotes({ type: "remove", id });
    this.#persistNotes();
  };

  removeNotesForProject = (projectId: string) => {
    this.internal_dispatchNotes({ type: "remove-project", projectId });
    this.#persistNotes();
  };

  toggleNoteFromMessage = (message: Message, projectId: string): boolean => {
    const existing = this.#get().notes.find((note) => note.id === `${projectId}:${message.id}`);
    if (existing) {
      this.removeNote(existing.id);
      return false;
    }
    const now = new Date().toISOString();
    const note: LocalNote = {
      id: `${projectId}:${message.id}`, projectId, title: noteTitle(message.content),
      text: message.content, citations: message.citations ?? [], createdAt: now, updatedAt: now,
    };
    this.internal_dispatchNotes({ type: "save", note });
    this.#persistNotes();
    return true;
  };

  setDraft = (key: string, text: string) => {
    this.#set((state) => ({ drafts: { ...state.drafts, [key]: text } }));
    const owner = this.#get().notesOwner;
    if (owner) {
      const next = { ...this.#get().drafts, [key]: text };
      if (!writeLocalDrafts(owner, next)) this.reportStorageError();
    }
  };

  clearDraft = (key: string) => {
    this.#set((state) => {
      const drafts = { ...state.drafts };
      delete drafts[key];
      return { drafts };
    });
    const owner = this.#get().notesOwner;
    if (owner && !writeLocalDrafts(owner, this.#get().drafts)) this.reportStorageError();
  };

  reportStorageError = () => {
    this.#set({ storageError: "Notes could not be saved on this device. Export important notes before leaving." });
  };

  internal_dispatchNotes = (action: Parameters<typeof notesReducer>[1]) =>
    this.#set((state) => ({ notes: notesReducer(state.notes, action) }));

  #persistNotes = () => {
    const { notes, notesOwner } = this.#get();
    if (!notesOwner) return;
    if (!writeLocalNotes(notesOwner, notes)) this.reportStorageError();
  };
}

export type NotesAction = Pick<NotesActions, keyof NotesActions>;
