import type { ChatMessage, ChatThread, SavedNote } from "@/lib/types";

type ThreadAction =
  | { type: "append"; scope: string; notebookId: string; message: ChatMessage }
  | { type: "clear"; scope: string }
  | { type: "clear-all" };

export function threadsReducer(threads: Record<string, ChatThread>, action: ThreadAction): Record<string, ChatThread> {
  if (action.type === "clear-all") return {};
  if (action.type === "clear") return Object.fromEntries(Object.entries(threads).filter(([scope]) => scope !== action.scope));
  const previous = threads[action.scope];
  return {
    ...threads,
    [action.scope]: {
      notebookId: action.notebookId,
      messages: [...(previous?.messages ?? []), action.message],
      updatedAt: new Date().toISOString(),
    },
  };
}

type NoteAction = { type: "save"; note: SavedNote } | { type: "remove"; id: string } | { type: "remove-notebook"; notebookId: string };

export function notesReducer(notes: Record<string, SavedNote>, action: NoteAction) {
  if (action.type === "save") return { ...notes, [action.note.id]: action.note };
  if (action.type === "remove-notebook") return Object.fromEntries(Object.entries(notes).filter(([, note]) => note.notebookId !== action.notebookId));
  return Object.fromEntries(Object.entries(notes).filter(([id]) => id !== action.id));
}
