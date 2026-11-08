import type { ChatMessage, ChatThread, QueryError, SavedNote } from "@/lib/types";
import { notebookScope, noteTitle } from "@/lib/notebooks";
import { errorMessage } from "@/services/api/api";
import { sendQuery } from "@/services/chat/chat";
import { notesReducer, threadsReducer } from "@/store/chat/reducer";
import type { StoreSetter } from "@/store/types";
import type { WorkspaceStore } from "@/store/workspace-store";

export interface ChatState {
  threadsMap: Record<string, ChatThread>;
  pendingMap: Record<string, boolean>;
  errorsMap: Record<string, QueryError>;
  notesMap: Record<string, SavedNote>;
  hydrated: boolean;
}

export const initialChatState: ChatState = {
  threadsMap: {},
  pendingMap: {},
  errorsMap: {},
  notesMap: {},
  hydrated: false,
};

export class ChatActions {
  readonly #set: StoreSetter<WorkspaceStore>;
  readonly #get: () => WorkspaceStore;
  readonly #requests = new Map<string, AbortController>();

  constructor(set: StoreSetter<WorkspaceStore>, get: () => WorkspaceStore) {
    this.#set = set;
    this.#get = get;
  }

  finishHydration = () => {
    const errorsMap = { ...this.#get().errorsMap };
    for (const [scope, thread] of Object.entries(this.#get().threadsMap)) {
      const last = thread.messages.at(-1);
      if (last?.role === "user") errorsMap[scope] ??= { query: last.text, message: "The previous response was interrupted. You can try it again." };
    }
    this.#set({ hydrated: true, errorsMap });
  };

  sendMessage = async (query: string, notebookId: string) => {
    const text = query.trim();
    const scope = notebookScope(notebookId);
    const notebook = this.#get().notebooksMap[notebookId];
    if (!text || !notebook?.sourceFilenames.length || this.#get().pendingMap[scope]) return;
    const filenames = [...notebook.sourceFilenames];
    this.internal_dispatchThreads({ type: "append", scope, notebookId, message: { id: crypto.randomUUID(), role: "user", text, sourceFilenames: filenames } });
    this.#get().touchNotebook(notebookId);
    await this.internal_sendMessage(text, notebookId, filenames);
  };

  retryMessage = async (notebookId: string) => {
    const scope = notebookScope(notebookId);
    const error = this.#get().errorsMap[scope];
    const notebook = this.#get().notebooksMap[notebookId];
    if (!error || !notebook?.sourceFilenames.length || this.#get().pendingMap[scope]) return;
    await this.internal_sendMessage(error.query, notebookId, [...notebook.sourceFilenames]);
  };

  stopMessage = (notebookId: string) => this.#requests.get(notebookScope(notebookId))?.abort();

  internal_cancelChatRequests = () => {
    const requests = [...this.#requests.values()];
    this.#requests.clear();
    requests.forEach((request) => request.abort());
    this.#set({ pendingMap: {} });
  };

  clearThread = (notebookId: string) => {
    const scope = notebookScope(notebookId);
    const request = this.#requests.get(scope);
    this.#requests.delete(scope);
    request?.abort();
    this.internal_dispatchThreads({ type: "clear", scope });
    this.#set((state) => ({
      pendingMap: { ...state.pendingMap, [scope]: false },
      errorsMap: Object.fromEntries(Object.entries(state.errorsMap).filter(([key]) => key !== scope)),
    }));
  };

  clearHistory = () => {
    const requests = [...this.#requests.values()];
    this.#requests.clear();
    requests.forEach((request) => request.abort());
    this.internal_dispatchThreads({ type: "clear-all" });
    this.#set({ pendingMap: {}, errorsMap: {} });
  };

  toggleSavedNote = (message: ChatMessage, notebookId: string) => {
    const id = `${notebookScope(notebookId)}:${message.id}`;
    this.#get().touchNotebook(notebookId);
    if (this.#get().notesMap[id]) {
      this.internal_dispatchNotes({ type: "remove", id });
      return false;
    }
    const now = new Date().toISOString();
    this.internal_dispatchNotes({ type: "save", note: { id, notebookId, title: noteTitle(message.text), text: message.text, citations: message.citations ?? [], createdAt: now, updatedAt: now } });
    return true;
  };

  saveNote = (notebookId: string, title: string, text: string, id?: string) => {
    if (!title.trim() || !text.trim() || !this.#get().notebooksMap[notebookId]) return;
    const existing = id ? this.#get().notesMap[id] : undefined;
    const now = new Date().toISOString();
    const note: SavedNote = {
      id: existing?.id ?? crypto.randomUUID(), notebookId, title: title.trim().slice(0, 120),
      text: text.trim(), citations: existing?.citations ?? [], createdAt: existing?.createdAt ?? now, updatedAt: now,
    };
    this.internal_dispatchNotes({ type: "save", note });
    this.#get().touchNotebook(notebookId);
    return note.id;
  };

  removeNote = (id: string) => {
    const note = this.#get().notesMap[id];
    this.internal_dispatchNotes({ type: "remove", id });
    if (note) this.#get().touchNotebook(note.notebookId);
  };

  internal_sendMessage = async (query: string, notebookId: string, filenames: string[]) => {
    const scope = notebookScope(notebookId);
    const controller = new AbortController();
    this.#requests.set(scope, controller);
    this.#set((state) => ({
      pendingMap: { ...state.pendingMap, [scope]: true },
      errorsMap: Object.fromEntries(Object.entries(state.errorsMap).filter(([key]) => key !== scope)),
    }));

    try {
      const response = await sendQuery(query, filenames, controller.signal);
      if (this.#requests.get(scope) !== controller) return;
      this.internal_dispatchThreads({ type: "append", scope, notebookId, message: { id: crypto.randomUUID(), role: "assistant", text: response.answer, citations: response.citations, sourceFilenames: filenames } });
      this.#get().touchNotebook(notebookId);
    } catch (error) {
      if (this.#requests.get(scope) !== controller) return;
      const message = controller.signal.aborted ? "Response stopped. You can retry this question whenever you’re ready." : errorMessage(error);
      this.#set((state) => ({ errorsMap: { ...state.errorsMap, [scope]: { query, message } } }));
    } finally {
      if (this.#requests.get(scope) === controller) {
        this.#requests.delete(scope);
        this.#set((state) => ({ pendingMap: { ...state.pendingMap, [scope]: false } }));
      }
    }
  };

  internal_dispatchThreads = (action: Parameters<typeof threadsReducer>[1]) => this.#set((state) => ({ threadsMap: threadsReducer(state.threadsMap, action) }));

  internal_dispatchNotes = (action: Parameters<typeof notesReducer>[1]) => this.#set((state) => ({ notesMap: notesReducer(state.notesMap, action) }));
}

export type ChatAction = Pick<ChatActions, keyof ChatActions>;
