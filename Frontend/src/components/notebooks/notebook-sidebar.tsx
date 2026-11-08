"use client";

import Link from "next/link";
import { useId } from "react";
import { ArrowLeft, ArrowRight, Bookmark, Check, CircleAlert, FileText, FileUp, Loader2, PanelLeftClose, Plus, Sparkles } from "lucide-react";
import { Brand } from "@/components/brand";
import { AccountMenu } from "@/components/account-menu";
import { useNotebook } from "@/components/notebooks/notebook-provider";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { Button } from "@/components/ui/button";

export function NotebookSidebar() {
  const sectionId = useId();
  const { state: { notebook }, actions, meta } = useNotebook();
  const notesMap = useWorkspace((state) => state.notesMap);
  const pending = useWorkspace((state) => state.pendingMap[meta.scope]);
  const uploadNotebookId = useWorkspace((state) => state.uploadNotebookId);
  const uploadQueue = useWorkspace((state) => state.uploadQueue);
  const uploading = useWorkspace((state) => state.isUploading);
  const notes = Object.values(notesMap).filter((note) => note.notebookId === notebook.id).toSorted((a, b) => Date.parse(b.updatedAt) - Date.parse(a.updatedAt));
  const queue = uploadNotebookId === notebook.id ? uploadQueue : [];

  return (
    <div className="flex h-full min-h-0 flex-col bg-sidebar text-sidebar-foreground">
      <div className="flex h-[76px] shrink-0 items-center justify-between gap-2 border-b border-sidebar-border px-5"><Brand /><Button variant="ghost" size="icon-sm" className="hidden text-muted-foreground lg:inline-flex" aria-label="Collapse sidebar" onClick={() => actions.setSidebarCollapsed(true)}><PanelLeftClose /></Button></div>
      <div className="flex-1 overflow-y-auto px-4 pt-4 pb-6">
        <Button asChild variant="ghost" size="sm" className="mb-7 w-full justify-start text-xs font-normal text-muted-foreground"><Link href="/"><ArrowLeft className="size-3.5" />All notebooks</Link></Button>
        <section aria-labelledby={`${sectionId}-sources`}>
          <div className="mb-3 flex items-center justify-between px-2"><h2 id={`${sectionId}-sources`} className="text-[10px] font-semibold tracking-[0.13em] text-muted-foreground">SOURCES <span className="ml-1.5 font-normal tracking-normal">{notebook.sourceFilenames.length}</span></h2><Button variant="ghost" size="icon-xs" data-dialog-return-focus aria-label="Add sources" onClick={() => actions.openPanel({ kind: "upload" })}><Plus /></Button></div>
          {notebook.sourceFilenames.length ? <ul className="space-y-1">{notebook.sourceFilenames.map((filename) => <li key={filename}><button onClick={() => actions.openPanel({ kind: "source", filename })} className="group flex w-full items-start gap-2.5 rounded-lg px-2.5 py-2.5 text-left transition-colors hover:bg-sidebar-accent"><span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-md border border-sidebar-border bg-card/60"><FileText className="size-3.5 text-muted-foreground" /></span><span className="min-w-0"><span className="block truncate text-xs leading-5 font-medium" title={filename}>{filename}</span><span className="text-[10px] text-muted-foreground">PDF source</span></span></button></li>)}</ul> : <div className="mx-1 rounded-xl border border-dashed border-sidebar-border px-3 py-5 text-center"><FileUp className="mx-auto mb-2.5 size-5 text-muted-foreground" /><p className="text-xs text-muted-foreground">Your research starts here.</p><Button variant="outline" size="sm" onClick={() => actions.openPanel({ kind: "upload" })} className="mt-3 bg-card text-xs"><Plus />Add your first source</Button></div>}
          {queue.length ? <button onClick={() => actions.openPanel({ kind: "upload" })} className="mt-3 flex w-full items-center gap-2 rounded-lg border bg-card/60 px-3 py-2.5 text-left text-[11px]">{uploading ? <Loader2 className="size-3.5 shrink-0 animate-spin" /> : queue.some((task) => task.status === "error") ? <CircleAlert className="size-3.5 shrink-0 text-destructive" /> : <Check className="size-3.5 shrink-0" />}<span>{uploading ? "Processing your sources..." : queue.some((task) => task.status === "error") ? "Some files need attention" : "Sources added"}</span></button> : null}
        </section>
        <section aria-labelledby={`${sectionId}-notes`} className="mt-8">
          <div className="mb-3 flex items-center justify-between px-2"><h2 id={`${sectionId}-notes`} className="text-[10px] font-semibold tracking-[0.13em] text-muted-foreground">SAVED NOTES <span className="ml-1.5 font-normal tracking-normal">{notes.length}</span></h2><Button variant="ghost" size="icon-xs" aria-label="Add note" onClick={() => actions.openPanel({ kind: "note" })}><Plus /></Button></div>
          {notes.length ? <ul className="space-y-1">{notes.map((note) => <li key={note.id}><button onClick={() => actions.openPanel({ kind: "note", id: note.id })} className="flex w-full items-start gap-2.5 rounded-lg px-2.5 py-2.5 text-left transition-colors hover:bg-sidebar-accent"><Bookmark className="mt-0.5 size-4 shrink-0 text-muted-foreground" /><span className="line-clamp-2 text-xs leading-5">{note.title}</span></button></li>)}</ul> : <p className="px-2.5 text-[11px] leading-5 text-muted-foreground">Save a useful answer or add a thought of your own.</p>}
        </section>
        <section aria-labelledby={`${sectionId}-guide`} className="mt-8 rounded-xl border border-sidebar-border bg-card/65 p-4">
          <h2 id={`${sectionId}-guide`} className="mb-3 flex items-center gap-2 text-[10px] font-semibold tracking-[0.1em]"><Sparkles className="size-3.5 text-muted-foreground" />NOTEBOOK GUIDE</h2>
          <p className="text-xs leading-5 text-muted-foreground">Generate summaries, FAQs, or study guides from your sources.</p>
          <Button variant="outline" size="sm" className="mt-4 w-full justify-between bg-card text-xs" disabled={!notebook.sourceFilenames.length || pending} onClick={() => actions.openPanel({ kind: "guide" })}>Generate Guide<ArrowRight className="size-3.5" /></Button>
        </section>
      </div>
      <div className="shrink-0 border-t border-sidebar-border p-3">
        <AccountMenu variant="sidebar" />
      </div>
    </div>
  );
}
