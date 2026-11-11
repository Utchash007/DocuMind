import type { Conversation, Message } from "@/lib/api-types";

export type ConversationsPage = {
  items: Conversation[];
  nextCursor: string | null;
  status: "idle" | "loading" | "ready" | "error";
  error: string | null;
};

export type MessagesPage = {
  items: Message[];
  nextCursor: string | null;
  status: "idle" | "loading" | "ready" | "error";
  error: string | null;
};

export const emptyConversationsPage: ConversationsPage = { items: [], nextCursor: null, status: "idle", error: null };
export const emptyMessagesPage: MessagesPage = { items: [], nextCursor: null, status: "idle", error: null };

export type ConversationAction =
  | { type: "set-loading"; scope: string }
  | { type: "set-page"; scope: string; page: ConversationsPage }
  | { type: "set-error"; scope: string; error: string }
  | { type: "upsert"; scope: string; conversation: Conversation }
  | { type: "remove"; scope: string; conversationId: string }
  | { type: "reset" };

export function conversationsReducer(state: Record<string, ConversationsPage>, action: ConversationAction): Record<string, ConversationsPage> {
  switch (action.type) {
    case "reset": return {};
    case "set-loading": return { ...state, [action.scope]: { ...(state[action.scope] ?? emptyConversationsPage), status: "loading" } };
    case "set-page": return { ...state, [action.scope]: action.page };
    case "set-error": return { ...state, [action.scope]: { ...(state[action.scope] ?? emptyConversationsPage), status: "error", error: action.error } };
    case "upsert": {
      const page = state[action.scope] ?? emptyConversationsPage;
      const items = page.items.some((item) => item.id === action.conversation.id)
        ? page.items.map((item) => (item.id === action.conversation.id ? action.conversation : item))
        : [action.conversation, ...page.items];
      return { ...state, [action.scope]: { ...page, items, status: page.status === "idle" ? "ready" : page.status } };
    }
    case "remove": {
      const page = state[action.scope];
      if (!page) return state;
      return { ...state, [action.scope]: { ...page, items: page.items.filter((item) => item.id !== action.conversationId) } };
    }
  }
}

export type MessagesAction =
  | { type: "set-loading"; scope: string }
  | { type: "set-page"; scope: string; page: MessagesPage }
  | { type: "prepend"; scope: string; messages: Message[]; nextCursor: string | null }
  | { type: "append"; scope: string; messages: Message[] }
  | { type: "replace-optimistic"; scope: string; clientRequestId: string; messages: Message[] }
  | { type: "update"; scope: string; message: Message }
  | { type: "set-error"; scope: string; error: string }
  | { type: "reset" };

function dedupeSort(messages: Message[]): Message[] {
  const byId = new Map<string, Message>();
  for (const message of messages) byId.set(message.id, message);
  return [...byId.values()].toSorted((a, b) => a.position - b.position);
}

export function messagesReducer(state: Record<string, MessagesPage>, action: MessagesAction): Record<string, MessagesPage> {
  switch (action.type) {
    case "reset": return {};
    case "set-loading": return { ...state, [action.scope]: { ...(state[action.scope] ?? emptyMessagesPage), status: "loading" } };
    case "set-page": return { ...state, [action.scope]: action.page };
    case "set-error": return { ...state, [action.scope]: { ...(state[action.scope] ?? emptyMessagesPage), status: "error", error: action.error } };
    case "prepend": {
      const page = state[action.scope] ?? emptyMessagesPage;
      return { ...state, [action.scope]: { ...page, items: dedupeSort([...action.messages, ...page.items]), nextCursor: action.nextCursor, status: "ready", error: null } };
    }
    case "append": {
      const page = state[action.scope] ?? emptyMessagesPage;
      return { ...state, [action.scope]: { ...page, items: dedupeSort([...page.items, ...action.messages]), status: "ready", error: null } };
    }
    case "replace-optimistic": {
      const page = state[action.scope] ?? emptyMessagesPage;
      const withoutOptimistic = page.items.filter((item) => item.clientRequestId !== action.clientRequestId && item.id !== `optimistic:${action.clientRequestId}`);
      return { ...state, [action.scope]: { ...page, items: dedupeSort([...withoutOptimistic, ...action.messages]), status: "ready", error: null } };
    }
    case "update": {
      const page = state[action.scope] ?? emptyMessagesPage;
      return { ...state, [action.scope]: { ...page, items: page.items.map((item) => (item.id === action.message.id ? action.message : item)) } };
    }
  }
}
