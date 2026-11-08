"use client";

import Link from "next/link";
import { useEffect } from "react";
import { ArrowLeft, BookOpenText } from "lucide-react";
import { NotebookChat } from "@/components/chat/notebook-chat";
import { NotebookHeader } from "@/components/notebooks/notebook-header";
import { NotebookProvider, useNotebook } from "@/components/notebooks/notebook-provider";
import { NotebookSidebar } from "@/components/notebooks/notebook-sidebar";
import { NotebookDialogs } from "@/components/notebooks/workspace-dialogs";
import { WorkspaceSkeleton } from "@/components/notebooks/workspace-skeleton";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetDescription, SheetTitle } from "@/components/ui/sheet";

export function NotebookWorkspace({ notebookId }: { notebookId: string }) {
  const notebook = useWorkspace((state) => state.notebooksMap[notebookId]);
  const hydrated = useWorkspace((state) => state.hydrated);
  useEffect(() => {
    if (notebook?.title) document.title = `${notebook.title} | NoteMind`;
  }, [notebook?.title]);
  if (!hydrated) return <WorkspaceSkeleton />;
  if (!notebook) return <main id="main-content" className="flex min-h-dvh flex-col items-center justify-center px-6 text-center"><BookOpenText className="mb-5 size-9 text-muted-foreground" /><h1 className="text-2xl font-semibold tracking-tight">This notebook isn’t in this browser.</h1><p className="mt-3 max-w-sm text-sm leading-6 text-muted-foreground">Notebooks are stored in the browser where they were created. It may also have been deleted.</p><Button asChild className="mt-6"><Link href="/"><ArrowLeft />Back to notebooks</Link></Button></main>;
  return <NotebookProvider key={notebook.id} notebook={notebook}><NotebookShell /></NotebookProvider>;
}

function NotebookShell() {
  const { state, actions } = useNotebook();
  return (
    <Sheet open={state.mobileNavigationOpen} onOpenChange={actions.setMobileNavigationOpen}>
      <div className="flex h-dvh min-h-0 overflow-hidden bg-background">
        {!state.sidebarCollapsed ? <aside aria-label="Notebook sources and notes" className="hidden w-[272px] shrink-0 border-r lg:block xl:w-[288px]"><NotebookSidebar /></aside> : null}
        <SheetContent side="left" className="gap-0 p-0 data-[side=left]:w-[min(320px,90vw)]" onCloseAutoFocus={(event) => { if (state.panel) event.preventDefault(); }}><SheetTitle className="sr-only">Notebook navigation</SheetTitle><SheetDescription className="sr-only">Sources, saved notes, and notebook guide.</SheetDescription><NotebookSidebar /></SheetContent>
        <main id="main-content" className="flex min-w-0 flex-1 flex-col"><NotebookHeader /><NotebookChat /></main>
        <NotebookDialogs />
      </div>
    </Sheet>
  );
}
