import type {
  Citation, Conversation, Document, Message, Project,
} from "@/lib/api-types";

export const UUID_PATTERN = /^[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12}$/i;

export function isUuid(value: string): boolean {
  return UUID_PATTERN.test(value);
}

// ---- Scopes & routes (cache keys are always scoped by internal user) ----

export function projectScope(userId: string, projectId: string): string {
  return `${userId}:${projectId}`;
}

export function conversationScope(userId: string, projectId: string, conversationId: string): string {
  return `${userId}:${projectId}:${conversationId}`;
}

export function projectHref(projectId: string): string {
  return `/projects/${encodeURIComponent(projectId)}`;
}

export function conversationHref(projectId: string, conversationId: string): string {
  return `${projectHref(projectId)}/conversations/${encodeURIComponent(conversationId)}`;
}

// ---- Display helpers (NoteMind wireframe: monochrome, Chalk tokens) ----

export function noteTitle(text: string): string {
  return text.replace(/[#*_>`]/g, "").trim().split(/\r?\n/)[0].slice(0, 72) || "Saved answer";
}

export function editedLabel(timestamp: string): string {
  const minutes = Math.max(0, Math.floor((Date.now() - Date.parse(timestamp)) / 60_000));
  if (minutes < 1) return "Edited just now";
  if (minutes < 60) return `Edited ${minutes}m ago`;
  if (minutes < 1440) return `Edited ${Math.floor(minutes / 60)}h ago`;
  if (minutes < 2880) return "Edited yesterday";
  return `Edited ${new Intl.DateTimeFormat("en", { month: "short", day: "numeric" }).format(new Date(timestamp))}`;
}

export function formatFileSize(bytes: number | null | undefined): string {
  if (bytes == null) return "—";
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function documentStatusLabel(status: Document["status"]): string {
  switch (status) {
    case "Completed": return "Ready";
    case "Processing": return "Processing";
    case "Failed": return "Failed";
    default: return "Pending";
  }
}

export function citationLocation(citation: Citation): string {
  return citation.fileName ? `${citation.fileName}, page ${citation.pageNumber ?? "?"}` : `page ${citation.pageNumber ?? "?"}`;
}

// ---- Markdown export (FE-05: all server pages + local notes) ----

export interface LocalNote {
  id: string;
  projectId: string;
  title: string;
  text: string;
  citations: Citation[];
  createdAt: string;
  updatedAt: string;
}

function citationMarkdown(citations: Citation[] | null | undefined): string {
  const items = citations ?? [];
  if (!items.length) return "";
  return items.map((citation) => `> ${citation.text}\n> — ${citationLocation(citation)}`).join("\n\n");
}

export function conversationMarkdown(project: Project, conversation: Conversation, messages: Message[], notes: LocalNote[]): string {
  const sorted = [...messages].toSorted((a, b) => a.position - b.position);
  return [
    `# ${project.name}`,
    conversation.title ? `## ${conversation.title}\n\nExported from NoteMind` : "Exported from NoteMind",
    `## Conversation\n\n${sorted.map((message) => `### ${message.role === "user" ? "You" : "NoteMind"}\n\n${message.content}\n\n${citationMarkdown(message.citations)}`).join("\n\n") || "No conversation yet."}`,
    `## Saved notes (on this device)\n\n${notes.map((note) => `### ${note.title}\n\n${note.text}\n\n${citationMarkdown(note.citations)}`).join("\n\n") || "No saved notes."}`,
  ].join("\n\n");
}

export function projectMarkdown(project: Project, documents: Document[], conversations: Conversation[], messagesByConversation: Record<string, Message[]>, notes: LocalNote[]): string {
  const sections = conversations.map((conversation) =>
    conversationMarkdown(project, conversation, messagesByConversation[conversation.id] ?? [], notes),
  );
  return [
    `# ${project.name}`,
    "Exported from NoteMind",
    project.description ? `${project.description}\n` : "",
    `## Sources\n\n${documents.map((document) => `- ${document.fileName} (${documentStatusLabel(document.status)})`).join("\n") || "No sources added."}`,
    sections.join("\n\n---\n\n") || "## Conversation\n\nNo conversations yet.",
  ].join("\n\n");
}

export function markdownFilename(title: string, fallback = "project"): string {
  const clean = title.replace(/[^\p{L}\p{N} _-]/gu, "").trim().replace(/\s+/g, "-").slice(0, 80);
  return `${clean || fallback}.md`;
}
