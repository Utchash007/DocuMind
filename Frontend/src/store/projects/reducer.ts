import type { Project } from "@/lib/api-types";

export type ProjectsPage = {
  items: Project[];
  nextCursor: string | null;
  status: "idle" | "loading" | "ready" | "error";
  error: string | null;
};

export const emptyProjectsPage: ProjectsPage = { items: [], nextCursor: null, status: "idle", error: null };

export type ProjectsAction =
  | { type: "set-loading"; scope: string }
  | { type: "set-page"; scope: string; page: ProjectsPage }
  | { type: "set-error"; scope: string; error: string }
  | { type: "upsert"; scope: string; project: Project }
  | { type: "remove"; scope: string; projectId: string }
  | { type: "reset" };

export function projectsReducer(state: Record<string, ProjectsPage>, action: ProjectsAction): Record<string, ProjectsPage> {
  switch (action.type) {
    case "reset": return {};
    case "set-loading": return { ...state, [action.scope]: { ...(state[action.scope] ?? emptyProjectsPage), status: "loading" } };
    case "set-page": return { ...state, [action.scope]: action.page };
    case "set-error": return { ...state, [action.scope]: { ...(state[action.scope] ?? emptyProjectsPage), status: "error", error: action.error } };
    case "upsert": {
      const page = state[action.scope] ?? emptyProjectsPage;
      const items = page.items.some((item) => item.id === action.project.id)
        ? page.items.map((item) => (item.id === action.project.id ? action.project : item))
        : [action.project, ...page.items];
      return { ...state, [action.scope]: { ...page, items, status: page.status === "idle" ? "ready" : page.status } };
    }
    case "remove": {
      const page = state[action.scope];
      if (!page) return state;
      return { ...state, [action.scope]: { ...page, items: page.items.filter((item) => item.id !== action.projectId) } };
    }
  }
}

export function upsertProjectMap(state: Record<string, Project>, project: Project): Record<string, Project> {
  return { ...state, [project.id]: project };
}

export function removeProjectMaps(detail: Record<string, Project>, projectId: string): Record<string, Project> {
  return Object.fromEntries(Object.entries(detail).filter(([key]) => !key.endsWith(`:${projectId}`)));
}
