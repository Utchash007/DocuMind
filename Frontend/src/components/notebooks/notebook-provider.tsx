"use client";

import { createContext, use, useState, type ReactNode } from "react";
import type { Notebook } from "@/lib/types";
import { notebookScope } from "@/lib/notebooks";

export type NotebookPanel =
  | { kind: "upload" | "guide" | "share" | "rename" | "delete" | "clear-chat" }
  | { kind: "source"; filename: string }
  | { kind: "note"; id?: string };

interface NotebookContextValue {
  state: { notebook: Notebook; sidebarCollapsed: boolean; mobileNavigationOpen: boolean; panel: NotebookPanel | null };
  actions: {
    setSidebarCollapsed: (collapsed: boolean) => void;
    setMobileNavigationOpen: (open: boolean) => void;
    openPanel: (panel: NotebookPanel) => void;
    closePanel: () => void;
  };
  meta: { scope: string };
}

const NotebookContext = createContext<NotebookContextValue | null>(null);

export function NotebookProvider({ notebook, children }: { notebook: Notebook; children: ReactNode }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileNavigationOpen, setMobileNavigationOpen] = useState(false);
  const [panel, setPanel] = useState<NotebookPanel | null>(null);
  const value: NotebookContextValue = {
    state: { notebook, sidebarCollapsed, mobileNavigationOpen, panel },
    actions: {
      setSidebarCollapsed, setMobileNavigationOpen,
      openPanel: (next) => { setMobileNavigationOpen(false); setPanel(next); },
      closePanel: () => setPanel(null),
    },
    meta: { scope: notebookScope(notebook.id) },
  };
  return <NotebookContext value={value}>{children}</NotebookContext>;
}

export function useNotebook() {
  const context = use(NotebookContext);
  if (!context) throw new Error("Notebook components must be inside NotebookProvider.");
  return context;
}
