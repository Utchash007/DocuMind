import type { ChatMessage, Notebook, SavedNote } from "@/lib/types";

export function notebookScope(id: string) {
  return `notebook:${id}`;
}

export function notebookHref(id: string) {
  return `/notebooks/${encodeURIComponent(id)}`;
}

export function noteTitle(text: string) {
  return text.replace(/[#*_>`]/g, "").trim().split(/\r?\n/)[0].slice(0, 72) || "Saved answer";
}

export function editedLabel(timestamp: string) {
  const minutes = Math.max(0, Math.floor((Date.now() - Date.parse(timestamp)) / 60_000));
  if (minutes < 1) return "Edited just now";
  if (minutes < 60) return `Edited ${minutes}m ago`;
  if (minutes < 1440) return `Edited ${Math.floor(minutes / 60)}h ago`;
  if (minutes < 2880) return "Edited yesterday";
  return `Edited ${new Intl.DateTimeFormat("en", { month: "short", day: "numeric" }).format(new Date(timestamp))}`;
}

export function notebookMarkdown(notebook: Notebook, messages: ChatMessage[], notes: SavedNote[]) {
  const citations = (items: ChatMessage["citations"]) => (items ?? []).map((citation) =>
    `> ${citation.sentence}\n> — ${citation.filename ?? "Source"}, page ${citation.page}`,
  ).join("\n\n");

  return [
    `# ${notebook.title}`,
    "Exported from NoteMind",
    `## Sources\n\n${notebook.sourceFilenames.map((filename) => `- ${filename}`).join("\n") || "No sources added."}`,
    `## Saved notes\n\n${notes.map((note) => `### ${note.title}\n\n${note.text}\n\n${citations(note.citations)}`).join("\n\n") || "No saved notes."}`,
    `## Conversation\n\n${messages.map((message) => `### ${message.role === "user" ? "You" : "NoteMind"}\n\n${message.text}\n\n${citations(message.citations)}`).join("\n\n") || "No conversation yet."}`,
  ].join("\n\n");
}
