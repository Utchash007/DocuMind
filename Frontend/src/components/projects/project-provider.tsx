"use client";

import { createContext, use, useState, type ReactNode } from "react";
import type { Project } from "@/lib/api-types";
import { projectScope } from "@/lib/projects";

export type ProjectPanel =
  | { kind: "upload" | "guide" | "export" | "rename" | "delete" }
  | { kind: "document"; documentId: string }
  | { kind: "note"; id?: string }
  | { kind: "conversation-create" }
  | { kind: "conversation-rename"; conversationId: string }
  | { kind: "conversation-delete"; conversationId: string };

interface ProjectContextValue {
  state: { project: Project; projectId: string; conversationId: string | null; sidebarCollapsed: boolean; mobileNavigationOpen: boolean; panel: ProjectPanel | null };
  actions: {
    setSidebarCollapsed: (collapsed: boolean) => void;
    setMobileNavigationOpen: (open: boolean) => void;
    openPanel: (panel: ProjectPanel) => void;
    closePanel: () => void;
  };
  meta: { scope: string };
}

const ProjectContext = createContext<ProjectContextValue | null>(null);

export function ProjectProvider({ project, conversationId, children }: { project: Project; conversationId: string | null; children: ReactNode }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileNavigationOpen, setMobileNavigationOpen] = useState(false);
  const [panel, setPanel] = useState<ProjectPanel | null>(null);
  const value: ProjectContextValue = {
    state: { project, projectId: project.id, conversationId, sidebarCollapsed, mobileNavigationOpen, panel },
    actions: {
      setSidebarCollapsed, setMobileNavigationOpen,
      openPanel: (next) => { setMobileNavigationOpen(false); setPanel(next); },
      closePanel: () => setPanel(null),
    },
    meta: { scope: projectScope("workspace", project.id) },
  };
  return <ProjectContext value={value}>{children}</ProjectContext>;
}

export function useProject() {
  const context = use(ProjectContext);
  if (!context) throw new Error("Project components must be inside ProjectProvider.");
  return context;
}
