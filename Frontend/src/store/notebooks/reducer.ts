import type { Notebook } from "@/lib/types";

type NotebookUpdate =
  | { type: "add"; notebook: Notebook }
  | { type: "remove"; id: string }
  | { type: "update"; id: string; changes: Partial<Pick<Notebook, "title" | "updatedAt">> }
  | { type: "add-sources"; id: string; filenames: string[]; updatedAt: string }
  | { type: "remove-source"; id: string; filename: string; updatedAt: string };

export function notebooksReducer(notebooks: Record<string, Notebook>, action: NotebookUpdate): Record<string, Notebook> {
  if (action.type === "add") return { ...notebooks, [action.notebook.id]: action.notebook };
  if (action.type === "remove") return Object.fromEntries(Object.entries(notebooks).filter(([id]) => id !== action.id));
  const notebook = notebooks[action.id];
  if (!notebook) return notebooks;
  if (action.type === "update") return { ...notebooks, [action.id]: { ...notebook, ...action.changes } };
  const sourceFilenames = action.type === "add-sources"
    ? [...new Set([...notebook.sourceFilenames, ...action.filenames])]
    : notebook.sourceFilenames.filter((filename) => filename !== action.filename);
  return { ...notebooks, [action.id]: { ...notebook, sourceFilenames, updatedAt: action.updatedAt } };
}
