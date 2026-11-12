"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowLeft, BookOpenText } from "lucide-react";
import { ConversationChat } from "@/components/projects/conversation-chat";
import { ProjectHeader } from "@/components/projects/project-header";
import { ProjectProvider, useProject } from "@/components/projects/project-provider";
import { ProjectSidebar } from "@/components/projects/project-sidebar";
import { ProjectDialogs } from "@/components/projects/workspace-dialogs";
import { WorkspaceSkeleton } from "@/components/projects/workspace-skeleton";
import { projectScope } from "@/lib/projects";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetDescription, SheetTitle } from "@/components/ui/sheet";

export function ProjectWorkspace({ projectId, conversationId }: { projectId: string; conversationId?: string | null }) {
  const identity = useWorkspace((state) => state.identity);
  const project = useWorkspace((state) => (identity ? state.projectDetailByUser[projectScope(identity, projectId)] : undefined));
  const loadProjectDetail = useWorkspace((state) => state.loadProjectDetail);
  const loadDocuments = useWorkspace((state) => state.loadDocuments);
  const loadConversations = useWorkspace((state) => state.loadConversations);
  const loadConversationDetail = useWorkspace((state) => state.loadConversationDetail);
  const documentsPage = useWorkspace((state) => (identity ? state.documentsByScope[projectScope(identity, projectId)] : undefined));
  const documents = documentsPage?.items ?? [];
  const [loadError, setLoadError] = useState<string | null>(null);
  const [prevProjectId, setPrevProjectId] = useState(projectId);
  if (prevProjectId !== projectId) {
    setPrevProjectId(projectId);
    setLoadError(null);
  }

  useEffect(() => {
    if (!identity) return;
    void loadProjectDetail(projectId).catch(() => setLoadError("This project could not be loaded. It may have been deleted or you may not have access to it."));
    void loadDocuments(projectId, { reset: true });
    void loadConversations(projectId, { reset: true });
    if (conversationId) void loadConversationDetail(projectId, conversationId).catch(() => undefined);
  }, [identity, projectId, conversationId, loadProjectDetail, loadDocuments, loadConversations, loadConversationDetail]);

  useEffect(() => {
    if (project?.name) document.title = `${project.name} | DocuMind`;
  }, [project?.name]);

  if (!identity) return <WorkspaceSkeleton />;
  if (!project && !loadError) return <WorkspaceSkeleton />;
  if (!project) {
    return (
      <main id="main-content" className="flex min-h-dvh flex-col items-center justify-center px-6 text-center">
        <BookOpenText className="mb-5 size-9 text-muted-foreground" />
        <h1 className="text-2xl font-semibold tracking-tight">Project not found</h1>
        <p className="mt-3 max-w-sm text-sm leading-6 text-muted-foreground">{loadError ?? "This project may have been deleted or you may not have access to it."}</p>
        <Button asChild className="mt-6"><Link href="/"><ArrowLeft />Back to projects</Link></Button>
      </main>
    );
  }

  const readyCount = documents.filter((document) => document.status === "Completed").length;
  return (
    <ProjectProvider key={project.id} project={project} conversationId={conversationId ?? null}>
      <ProjectShell readyDocumentCount={readyCount} />
    </ProjectProvider>
  );
}

function ProjectShell({ readyDocumentCount }: { readyDocumentCount: number }) {
  const { state, actions } = useProject();
  return (
    <Sheet open={state.mobileNavigationOpen} onOpenChange={actions.setMobileNavigationOpen}>
      <div className="flex h-dvh min-h-0 overflow-hidden bg-background">
        {!state.sidebarCollapsed ? <aside aria-label="Project sources, conversations and notes" className="hidden w-[272px] shrink-0 border-r lg:block xl:w-[288px]"><ProjectSidebar /></aside> : null}
        <SheetContent side="left" className="gap-0 p-0 data-[side=left]:w-[min(320px,90vw)]" onCloseAutoFocus={(event) => { if (state.panel) event.preventDefault(); }}>
          <SheetTitle className="sr-only">Project navigation</SheetTitle>
          <SheetDescription className="sr-only">Conversations, sources, saved notes, and project guide.</SheetDescription>
          <ProjectSidebar />
        </SheetContent>
        <main id="main-content" className="flex min-w-0 flex-1 flex-col"><ProjectHeader /><ConversationChat readyDocumentCount={readyDocumentCount} /></main>
        <ProjectDialogs />
      </div>
    </Sheet>
  );
}
