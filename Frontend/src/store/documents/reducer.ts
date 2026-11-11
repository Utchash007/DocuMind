import type { Document } from "@/lib/api-types";

export type DocumentsPage = {
  items: Document[];
  nextCursor: string | null;
  status: "idle" | "loading" | "ready" | "error";
  error: string | null;
};

export const emptyDocumentsPage: DocumentsPage = { items: [], nextCursor: null, status: "idle", error: null };

export type DocumentsAction =
  | { type: "set-loading"; scope: string }
  | { type: "set-page"; scope: string; page: DocumentsPage }
  | { type: "set-error"; scope: string; error: string }
  | { type: "upsert-document"; scope: string; document: Document }
  | { type: "remove-document"; scope: string; documentId: string }
  | { type: "reset" };

export function documentsReducer(state: Record<string, DocumentsPage>, action: DocumentsAction): Record<string, DocumentsPage> {
  switch (action.type) {
    case "reset": return {};
    case "set-loading": return { ...state, [action.scope]: { ...(state[action.scope] ?? emptyDocumentsPage), status: "loading" } };
    case "set-page": return { ...state, [action.scope]: action.page };
    case "set-error": return { ...state, [action.scope]: { ...(state[action.scope] ?? emptyDocumentsPage), status: "error", error: action.error } };
    case "upsert-document": {
      const page = state[action.scope] ?? emptyDocumentsPage;
      const items = page.items.some((item) => item.id === action.document.id)
        ? page.items.map((item) => (item.id === action.document.id ? action.document : item))
        : [action.document, ...page.items];
      return { ...state, [action.scope]: { ...page, items, status: page.status === "idle" ? "ready" : page.status } };
    }
    case "remove-document": {
      const page = state[action.scope];
      if (!page) return state;
      return { ...state, [action.scope]: { ...page, items: page.items.filter((item) => item.id !== action.documentId) } };
    }
  }
}
