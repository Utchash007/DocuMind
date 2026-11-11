import type { LocalNote } from "@/lib/projects";

export type NotesAction =
  | { type: "save"; note: LocalNote }
  | { type: "remove"; id: string }
  | { type: "remove-project"; projectId: string }
  | { type: "replace-all"; notes: LocalNote[] }
  | { type: "reset" };

export function notesReducer(notes: LocalNote[], action: NotesAction): LocalNote[] {
  switch (action.type) {
    case "reset": return [];
    case "replace-all": return action.notes;
    case "save": {
      const index = notes.findIndex((note) => note.id === action.note.id);
      if (index >= 0) return notes.map((note, i) => (i === index ? action.note : note));
      return [action.note, ...notes];
    }
    case "remove": return notes.filter((note) => note.id !== action.id);
    case "remove-project": return notes.filter((note) => note.projectId !== action.projectId);
  }
}
