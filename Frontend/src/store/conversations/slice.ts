import type { Conversation, Message } from "@/lib/api-types";
import { conversationScope, projectScope } from "@/lib/projects";
import { isV2ApiError, v2ErrorMessage } from "@/services/v2http";
import {
  cancelMessage, createConversation, deleteConversation, getConversation,
  listConversations, listMessages, retryMessage, sendMessage, updateConversation,
} from "@/services/projects/conversations";
import {
  conversationsReducer, emptyConversationsPage, emptyMessagesPage,
  messagesReducer, type ConversationsPage, type MessagesPage,
} from "@/store/conversations/reducer";
import type { StoreSetter } from "@/store/types";
import type { WorkspaceStore } from "@/store/workspace-store";

export interface TurnError {
  message: string;
  query?: string;
  messageId?: string | null;
  code: string | null;
}

export interface ConversationsState {
  conversationsByScope: Record<string, ConversationsPage>;
  conversationDetailByScope: Record<string, Conversation>;
  messagesByScope: Record<string, MessagesPage>;
  pendingByScope: Record<string, boolean>;
  errorsByScope: Record<string, TurnError>;
}

export const initialConversationsState: ConversationsState = {
  conversationsByScope: {},
  conversationDetailByScope: {},
  messagesByScope: {},
  pendingByScope: {},
  errorsByScope: {},
};

export class ConversationsActions {
  readonly #set: StoreSetter<WorkspaceStore>;
  readonly #get: () => WorkspaceStore;
  readonly #requests = new Map<string, AbortController>();
  readonly #turnControllers = new Map<string, AbortController>();

  constructor(set: StoreSetter<WorkspaceStore>, get: () => WorkspaceStore) {
    this.#set = set;
    this.#get = get;
  }

  #identityNow(): { userId: string; generation: number } | null {
    const { identity, identityGeneration } = this.#get();
    return identity ? { userId: identity, generation: identityGeneration } : null;
  }

  #current(generation: number): boolean {
    return this.#get().identityGeneration === generation;
  }

  #key(projectId: string, conversationId: string): string | null {
    const identity = this.#identityNow();
    return identity ? conversationScope(identity.userId, projectId, conversationId) : null;
  }

  #projectKey(projectId: string): string | null {
    const identity = this.#identityNow();
    return identity ? projectScope(identity.userId, projectId) : null;
  }

  #track(key: string, controller: AbortController) {
    this.#requests.set(key, controller);
    return () => { if (this.#requests.get(key) === controller) this.#requests.delete(key); };
  }

  loadConversations = async (projectId: string, options: { cursor?: string; reset?: boolean } = {}) => {
    const identity = this.#identityNow();
    if (!identity) return;
    const scope = projectScope(identity.userId, projectId);
    const previous = this.#get().conversationsByScope[scope];
    if (previous?.status === "loading" && !options.reset) return;
    const controller = new AbortController();
    const done = this.#track(scope, controller);
    this.#set((state) => ({ conversationsByScope: conversationsReducer(state.conversationsByScope, { type: "set-loading", scope }) }));
    try {
      const page = await listConversations(projectId, { cursor: options.cursor, limit: 50, signal: controller.signal });
      if (!this.#current(identity.generation) || controller.signal.aborted) return;
      const items = options.reset || !options.cursor ? page.items : [...(previous?.items ?? []), ...page.items.filter((item) => !(previous?.items ?? []).some((existing) => existing.id === item.id))];
      this.#set((state) => ({
        conversationsByScope: conversationsReducer(state.conversationsByScope, { type: "set-page", scope, page: { items, nextCursor: page.nextCursor, status: "ready", error: null } }),
      }));
    } catch (error) {
      if (!this.#current(identity.generation) || controller.signal.aborted) return;
      this.#set((state) => ({ conversationsByScope: conversationsReducer(state.conversationsByScope, { type: "set-error", scope, error: v2ErrorMessage(error) }) }));
    } finally { done(); }
  };

  createConversationForProject = async (projectId: string, title?: string): Promise<Conversation | null> => {
    const identity = this.#identityNow();
    if (!identity) return null;
    const trimmed = title?.trim().slice(0, 255) || null;
    const conversation = await createConversation(projectId, { title: trimmed });
    if (!this.#current(identity.generation)) return null;
    const scope = projectScope(identity.userId, projectId);
    this.#set((state) => ({
      conversationsByScope: conversationsReducer(state.conversationsByScope, { type: "upsert", scope, conversation }),
      conversationDetailByScope: { ...state.conversationDetailByScope, [conversationScope(identity.userId, projectId, conversation.id)]: conversation },
    }));
    return conversation;
  };

  renameConversation = async (projectId: string, conversationId: string, title: string): Promise<Conversation | null> => {
    const identity = this.#identityNow();
    if (!identity) return null;
    const trimmed = title.trim().slice(0, 255);
    if (!trimmed) return null;
    const conversation = await updateConversation(projectId, conversationId, { title: trimmed });
    if (!this.#current(identity.generation)) return null;
    const scope = projectScope(identity.userId, projectId);
    this.#set((state) => ({
      conversationsByScope: conversationsReducer(state.conversationsByScope, { type: "upsert", scope, conversation }),
      conversationDetailByScope: { ...state.conversationDetailByScope, [conversationScope(identity.userId, projectId, conversation.id)]: conversation },
    }));
    return conversation;
  };

  deleteConversationForProject = async (projectId: string, conversationId: string): Promise<boolean> => {
    const identity = this.#identityNow();
    if (!identity) return false;
    const key = conversationScope(identity.userId, projectId, conversationId);
    this.#turnControllers.get(key)?.abort();
    this.#turnControllers.delete(key);
    for (const suffix of ["", "#list", "#older", "#cancel"]) {
      this.#requests.get(`${key}${suffix}`)?.abort();
      this.#requests.delete(`${key}${suffix}`);
    }
    await deleteConversation(projectId, conversationId);
    if (!this.#current(identity.generation)) return false;
    const scope = projectScope(identity.userId, projectId);
    this.#set((state) => {
      const messagesByScope = Object.fromEntries(Object.entries(state.messagesByScope).filter(([k]) => k !== key));
      const conversationDetailByScope = Object.fromEntries(Object.entries(state.conversationDetailByScope).filter(([k]) => k !== key));
      const pendingByScope = Object.fromEntries(Object.entries(state.pendingByScope).filter(([k]) => k !== key));
      const errorsByScope = Object.fromEntries(Object.entries(state.errorsByScope).filter(([k]) => k !== key));
      return {
        conversationsByScope: conversationsReducer(state.conversationsByScope, { type: "remove", scope, conversationId }),
        messagesByScope, conversationDetailByScope, pendingByScope, errorsByScope,
      };
    });
    return true;
  };

  loadConversationDetail = async (projectId: string, conversationId: string) => {
    const identity = this.#identityNow();
    if (!identity) return null;
    const key = conversationScope(identity.userId, projectId, conversationId);
    const controller = new AbortController();
    const done = this.#track(key, controller);
    try {
      const conversation = await getConversation(projectId, conversationId, controller.signal);
      if (!this.#current(identity.generation) || controller.signal.aborted) return null;
      const scope = projectScope(identity.userId, projectId);
      this.#set((state) => ({
        conversationDetailByScope: { ...state.conversationDetailByScope, [key]: conversation },
        conversationsByScope: conversationsReducer(state.conversationsByScope, { type: "upsert", scope, conversation }),
      }));
      return conversation;
    } catch (error) {
      if (!this.#current(identity.generation) || controller.signal.aborted) return null;
      throw new Error(v2ErrorMessage(error));
    } finally { done(); }
  };

  loadMessages = async (projectId: string, conversationId: string) => {
    const identity = this.#identityNow();
    const key = this.#key(projectId, conversationId);
    if (!identity || !key) return;
    const previous = this.#get().messagesByScope[key];
    if (previous?.status === "loading") return;
    const controller = new AbortController();
    const done = this.#track(`${key}#list`, controller);
    this.#set((state) => ({ messagesByScope: messagesReducer(state.messagesByScope, { type: "set-loading", scope: key }) }));
    try {
      const page = await listMessages(projectId, conversationId, { limit: 50, signal: controller.signal });
      if (!this.#current(identity.generation) || controller.signal.aborted) return;
      // Preserve an in-flight optimistic turn that landed after load started.
      const current = this.#get().messagesByScope[key];
      const persistedKeys = new Set(page.items.filter((item) => item.role === "user").map((item) => item.clientRequestId));
      const optimistic = (current?.items ?? []).filter((item) => item.id.startsWith("optimistic:") && !persistedKeys.has(item.clientRequestId));
      const items = optimistic.length ? [...page.items, ...optimistic] : page.items;
      this.#set((state) => ({
        messagesByScope: messagesReducer(state.messagesByScope, { type: "set-page", scope: key, page: { items, nextCursor: page.nextCursor, status: "ready", error: null } }),
      }));
    } catch (error) {
      if (!this.#current(identity.generation) || controller.signal.aborted) return;
      this.#set((state) => ({ messagesByScope: messagesReducer(state.messagesByScope, { type: "set-error", scope: key, error: v2ErrorMessage(error) }) }));
    } finally { done(); }
  };

  loadOlderMessages = async (projectId: string, conversationId: string) => {
    const identity = this.#identityNow();
    const key = this.#key(projectId, conversationId);
    if (!identity || !key) return;
    const cursor = this.#get().messagesByScope[key]?.nextCursor;
    if (!cursor) return;
    const controller = new AbortController();
    const done = this.#track(`${key}#older`, controller);
    try {
      const page = await listMessages(projectId, conversationId, { cursor, limit: 50, signal: controller.signal });
      if (!this.#current(identity.generation) || controller.signal.aborted) return;
      this.#set((state) => ({ messagesByScope: messagesReducer(state.messagesByScope, { type: "prepend", scope: key, messages: page.items, nextCursor: page.nextCursor }) }));
    } catch (error) {
      if (!this.#current(identity.generation) || controller.signal.aborted) return;
      throw new Error(v2ErrorMessage(error));
    } finally { done(); }
  };

  sendMessage = async (projectId: string, conversationId: string, content: string): Promise<boolean> => {
    const identity = this.#identityNow();
    const key = this.#key(projectId, conversationId);
    if (!identity || !key) return false;
    const text = content.trim();
    if (!text || text.length > 8000) return false;
    if (this.#get().pendingByScope[key]) return false;
    return this.internal_sendTurn(projectId, conversationId, text, crypto.randomUUID(), null);
  };

  retryMessage = async (projectId: string, conversationId: string): Promise<boolean> => {
    const identity = this.#identityNow();
    const key = this.#key(projectId, conversationId);
    if (!identity || !key || this.#get().pendingByScope[key]) return false;
    const error = this.#get().errorsByScope[key];
    const page = this.#get().messagesByScope[key];
    const failed = [...(page?.items ?? [])].reverse().find((item) => item.role === "user");
    if (error?.code === "cancelled" || failed?.generationStatus === "cancelled") return false;
    if (failed && !failed.id.startsWith("optimistic:") && failed.generationStatus !== "failed" &&
      !((failed.generationStatus === "pending" || failed.generationStatus === "generating") && failed.generationExpiresAt && Date.parse(failed.generationExpiresAt) <= Date.now())) return false;
    const query = failed?.content ?? error?.query;
    if (!query) return false;
    if (failed && !failed.id.startsWith("optimistic:") && failed.id) {
      return this.internal_retryTurn(projectId, conversationId, failed.id, query);
    }
    if (failed?.clientRequestId) {
      return this.internal_sendTurn(projectId, conversationId, query, failed.clientRequestId, null, true);
    }
    return this.internal_sendTurn(projectId, conversationId, query, crypto.randomUUID(), null, true);
  };

  stopMessage = (projectId: string, conversationId: string) => {
    const key = this.#key(projectId, conversationId);
    if (!key) return;
    this.#turnControllers.get(key)?.abort();
  };

  cancelTurn = async (projectId: string, conversationId: string): Promise<void> => {
    const identity = this.#identityNow();
    const key = this.#key(projectId, conversationId);
    if (!identity || !key) return;
    const page = this.#get().messagesByScope[key];
    let active = [...(page?.items ?? [])].reverse().find((item) => item.role === "user");
    if (!active || (!this.#turnControllers.has(key) && active.generationStatus !== "pending" && active.generationStatus !== "generating")) return;
    this.#turnControllers.get(key)?.abort();
    this.#turnControllers.delete(key);
    this.#requests.get(`${key}#cancel`)?.abort();
    const controller = new AbortController();
    const done = this.#track(`${key}#cancel`, controller);
    const current = () => this.#current(identity.generation) && !controller.signal.aborted;
    this.#set((state) => ({ pendingByScope: { ...state.pendingByScope, [key]: true } }));
    try {
      // The send response is not delivered until generation finishes. Resolve
      // the persisted ID before cancelling an optimistic browser-only row.
      if (active.id.startsWith("optimistic:")) {
        const persisted = await listMessages(projectId, conversationId, { limit: 50, signal: controller.signal });
        if (!current()) return;
        active = persisted.items.find((item) => item.clientRequestId === active?.clientRequestId && item.role === "user") ?? active;
      }
      if (active.id.startsWith("optimistic:")) throw new Error("Question has not reached the server yet. Retry to recover its status.");
      const response = await cancelMessage(projectId, conversationId, active.id, controller.signal);
      if (!current()) return;
      this.#set((state) => ({
        messagesByScope: messagesReducer(state.messagesByScope, { type: "replace-optimistic", scope: key, clientRequestId: active!.clientRequestId ?? "", messages: [response.userMessage] }),
        errorsByScope: { ...state.errorsByScope, [key]: { message: response.cancelled ? "Response cancelled. Submit a new question to continue." : "The turn already finished. Reload the conversation to see its status.", query: response.userMessage.content, messageId: response.userMessage.id, code: response.cancelled ? "cancelled" : "turn_finished" } },
      }));
      if (!response.cancelled) void this.loadMessages(projectId, conversationId);
    } catch (error) {
      if (!current()) return;
      const stopped = active;
      this.#set((state) => ({ errorsByScope: { ...state.errorsByScope, [key]: { message: v2ErrorMessage(error), query: stopped.content, messageId: stopped.id, code: null } } }));
    } finally {
      if (this.#requests.get(`${key}#cancel`) === controller && current()) {
        this.#set((state) => ({ pendingByScope: { ...state.pendingByScope, [key]: false } }));
      }
      done();
    }
  };

  internal_cancelChatRequests = () => {
    for (const controller of this.#requests.values()) controller.abort();
    this.#requests.clear();
    for (const controller of this.#turnControllers.values()) controller.abort();
    this.#turnControllers.clear();
    this.#set({ pendingByScope: {} });
  };

  internal_cancelConversations = () => {
    this.internal_cancelChatRequests();
    this.#set({ ...initialConversationsState });
  };

  internal_sendTurn = async (projectId: string, conversationId: string, text: string, clientRequestId: string, _placeholder: null, isRetry = false): Promise<boolean> => {
    const identity = this.#identityNow();
    const key = this.#key(projectId, conversationId);
    if (!identity || !key) return false;
    const existing = this.#get().messagesByScope[key]?.items ?? [];
    const optimisticId = `optimistic:${clientRequestId}`;
    const maxPosition = existing.reduce((max, item) => Math.max(max, item.position), 0);
    const optimistic: Message = {
      id: optimisticId, conversationId, role: "user", content: text, position: maxPosition + 1,
      citations: null, metadata: null, clientRequestId, replyToMessageId: null,
      generationStatus: "pending", generationExpiresAt: null, createdAt: new Date().toISOString(),
    };
    if (!isRetry || !existing.some((item) => item.clientRequestId === clientRequestId)) {
      this.#set((state) => ({
        messagesByScope: messagesReducer(state.messagesByScope, { type: "append", scope: key, messages: [optimistic] }),
      }));
    }
    const controller = new AbortController();
    this.#turnControllers.set(key, controller);
    this.#set((state) => ({
      pendingByScope: { ...state.pendingByScope, [key]: true },
      errorsByScope: Object.fromEntries(Object.entries(state.errorsByScope).filter(([k]) => k !== key)),
    }));
    const generation = identity.generation;
    try {
      const turn = await sendMessage(projectId, conversationId, { content: text, clientRequestId }, controller.signal);
      if (!this.#current(generation) || this.#turnControllers.get(key) !== controller) return true;
      this.#set((state) => ({
        messagesByScope: messagesReducer(state.messagesByScope, { type: "replace-optimistic", scope: key, clientRequestId, messages: [turn.userMessage, turn.assistantMessage] }),
      }));
      void this.#get().loadConversations(projectId).catch(() => undefined);
      return true;
    } catch (error) {
      if (!this.#current(generation) || this.#turnControllers.get(key) !== controller) return false;
      const aborted = controller.signal.aborted;
      const message = aborted
        ? "Response stopped. You can retry this question whenever you’re ready."
        : v2ErrorMessage(error);
      const code = isV2ApiError(error) ? error.code : null;
      const serverMessageId = isV2ApiError(error) ? error.messageId : null;
      // If the server persisted the user message but generation failed, reconcile ids.
      if (isV2ApiError(error) && error.status >= 400 && error.status < 500 && code !== "active_turn_in_progress") {
        void this.loadMessages(projectId, conversationId).catch(() => undefined);
      }
      this.#set((state) => ({
        errorsByScope: { ...state.errorsByScope, [key]: { message, query: text, messageId: serverMessageId ?? optimisticId, code } },
      }));
      return false;
    } finally {
      if (this.#turnControllers.get(key) === controller) {
        this.#turnControllers.delete(key);
        if (this.#current(generation)) {
          this.#set((state) => ({ pendingByScope: { ...state.pendingByScope, [key]: false } }));
        }
      }
    }
  };

  internal_retryTurn = async (projectId: string, conversationId: string, messageId: string, query: string): Promise<boolean> => {
    const identity = this.#identityNow();
    const key = this.#key(projectId, conversationId);
    if (!identity || !key) return false;
    const controller = new AbortController();
    this.#turnControllers.set(key, controller);
    this.#set((state) => ({
      pendingByScope: { ...state.pendingByScope, [key]: true },
      errorsByScope: Object.fromEntries(Object.entries(state.errorsByScope).filter(([k]) => k !== key)),
    }));
    const generation = identity.generation;
    try {
      const turn = await retryMessage(projectId, conversationId, messageId, {}, controller.signal);
      if (!this.#current(generation) || this.#turnControllers.get(key) !== controller) return true;
      this.#set((state) => ({
        messagesByScope: messagesReducer(state.messagesByScope, { type: "append", scope: key, messages: [turn.assistantMessage] }),
      }));
      // Ensure the user turn shows completed + assistant order after reload-friendly state.
      this.#set((state) => ({
        messagesByScope: messagesReducer(state.messagesByScope, { type: "update", scope: key, message: turn.userMessage }),
      }));
      void query;
      return true;
    } catch (error) {
      if (!this.#current(generation) || this.#turnControllers.get(key) !== controller) return false;
      const aborted = controller.signal.aborted;
      const message = aborted ? "Response stopped. You can retry this question whenever you’re ready." : v2ErrorMessage(error);
      this.#set((state) => ({
        errorsByScope: { ...state.errorsByScope, [key]: { message, query, messageId, code: isV2ApiError(error) ? error.code : null } },
      }));
      return false;
    } finally {
      if (this.#turnControllers.get(key) === controller) {
        this.#turnControllers.delete(key);
        if (this.#current(generation)) {
          this.#set((state) => ({ pendingByScope: { ...state.pendingByScope, [key]: false } }));
        }
      }
    }
  };

  internal_dispatchConversations = (action: Parameters<typeof conversationsReducer>[1]) =>
    this.#set((state) => ({ conversationsByScope: conversationsReducer(state.conversationsByScope, action) }));

  internal_dispatchMessages = (action: Parameters<typeof messagesReducer>[1]) =>
    this.#set((state) => ({ messagesByScope: messagesReducer(state.messagesByScope, action) }));
}

export type ConversationsAction = Pick<ConversationsActions, keyof ConversationsActions>;
export { emptyConversationsPage, emptyMessagesPage };
