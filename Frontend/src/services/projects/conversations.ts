import { queryString, v2Fetch } from "@/services/v2http";
import type {
  Conversation, ConversationCreateRequest, ConversationDeleteAccepted,
  ConversationUpdateRequest, CursorPageParams, Message, MessageCancelResponse,
  MessageCreateRequest, MessageRetryRequest, PaginatedResponse, TurnResponse,
} from "@/lib/api-types";

const seg = (id: string) => encodeURIComponent(id);
const base = (projectId: string) => `/projects/${seg(projectId)}/conversations`;
const convBase = (projectId: string, conversationId: string) => `${base(projectId)}/${seg(conversationId)}`;
const msgBase = (projectId: string, conversationId: string) => `${convBase(projectId, conversationId)}/messages`;

export function listConversations(projectId: string, params: CursorPageParams & { signal?: AbortSignal } = {}): Promise<PaginatedResponse<Conversation>> {
  return v2Fetch<PaginatedResponse<Conversation>>(`${base(projectId)}${queryString({ cursor: params.cursor, limit: params.limit ?? 50 })}`, { signal: params.signal });
}

export function createConversation(projectId: string, input: ConversationCreateRequest = {}, signal?: AbortSignal): Promise<Conversation> {
  return v2Fetch<Conversation>(base(projectId), { method: "POST", body: JSON.stringify(input), signal }, 30_000);
}

export function getConversation(projectId: string, conversationId: string, signal?: AbortSignal): Promise<Conversation> {
  return v2Fetch<Conversation>(convBase(projectId, conversationId), { signal });
}

export function updateConversation(projectId: string, conversationId: string, input: ConversationUpdateRequest, signal?: AbortSignal): Promise<Conversation> {
  return v2Fetch<Conversation>(convBase(projectId, conversationId), { method: "PATCH", body: JSON.stringify(input), signal }, 30_000);
}

export async function deleteConversation(projectId: string, conversationId: string, signal?: AbortSignal): Promise<ConversationDeleteAccepted> {
  const result = await v2Fetch<ConversationDeleteAccepted | undefined>(convBase(projectId, conversationId), { method: "DELETE", signal }, 30_000);
  return result ?? { conversationId, accepted: true };
}

export function listMessages(projectId: string, conversationId: string, params: CursorPageParams & { signal?: AbortSignal } = {}): Promise<PaginatedResponse<Message>> {
  return v2Fetch<PaginatedResponse<Message>>(
    `${msgBase(projectId, conversationId)}${queryString({ cursor: params.cursor, limit: params.limit ?? 50 })}`,
    { signal: params.signal },
  );
}

/** Paginate through all server pages in position order (deduplicated). Used by Markdown export (FE-05/MIG-05). */
export async function fetchAllMessages(projectId: string, conversationId: string, signal?: AbortSignal, pageSize = 50): Promise<Message[]> {
  const all: Message[] = [];
  const seen = new Set<string>();
  let cursor: string | null = null;
  for (let guard = 0; guard < 100; guard += 1) {
    const page = await listMessages(projectId, conversationId, { cursor: cursor ?? undefined, limit: pageSize, signal });
    for (const message of page.items) {
      if (!seen.has(message.id)) { seen.add(message.id); all.push(message); }
    }
    cursor = page.nextCursor;
    if (!cursor) break;
  }
  return all.toSorted((a, b) => a.position - b.position);
}

export function sendMessage(projectId: string, conversationId: string, input: MessageCreateRequest, signal?: AbortSignal): Promise<TurnResponse> {
  if (!input.content || input.content.length > 8000) throw new Error("Questions must be between 1 and 8000 characters.");
  if (!input.clientRequestId) throw new Error("A client request id is required to send a message.");
  return v2Fetch<TurnResponse>(msgBase(projectId, conversationId), { method: "POST", body: JSON.stringify(input), signal }, 120_000);
}

export function retryMessage(projectId: string, conversationId: string, messageId: string, input: MessageRetryRequest = {}, signal?: AbortSignal): Promise<TurnResponse> {
  return v2Fetch<TurnResponse>(`${msgBase(projectId, conversationId)}/${seg(messageId)}/retry`, { method: "POST", body: JSON.stringify(input), signal }, 120_000);
}

export function cancelMessage(projectId: string, conversationId: string, messageId: string, signal?: AbortSignal): Promise<MessageCancelResponse> {
  return v2Fetch<MessageCancelResponse>(`${msgBase(projectId, conversationId)}/${seg(messageId)}/cancel`, { method: "POST", signal }, 30_000);
}
