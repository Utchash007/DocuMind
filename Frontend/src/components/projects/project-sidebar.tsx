"use client";

import Link from "next/link";
import { useId, useState } from "react";
import {
  ArrowLeft, ArrowRight, Bookmark, Check, CircleAlert, FileUp, Loader2,
  MessageSquarePlus, MoreHorizontal, PanelLeftClose, PencilLine, Plus, RotateCcw, Sparkles, Trash2,
} from "lucide-react";
import type { Document } from "@/lib/api-types";
import { Brand } from "@/components/brand";
import { AccountMenu } from "@/components/account-menu";
import { useProject } from "@/components/projects/project-provider";
import { conversationHref, documentStatusLabel, projectScope } from "@/lib/projects";
import { jobStageLabel } from "@/services/projects/jobs";
import { v2ErrorMessage } from "@/services/v2http";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { toast } from "sonner";

export function ProjectSidebar() {
  const sectionId = useId();
  const { state: { project }, actions } = useProject();
  const identity = useWorkspace((state) => state.identity);
  const notes = useWorkspace((state) => state.notes);
  const documentsPage = useWorkspace((state) => (identity ? state.documentsByScope[projectScope(identity, project.id)] : undefined));
  const conversationsPage = useWorkspace((state) => (identity ? state.conversationsByScope[projectScope(identity, project.id)] : undefined));
  const uploadingProjectId = useWorkspace((state) => state.uploadingProjectId);
  const uploadQueue = useWorkspace((state) => state.uploadQueue);
  const jobsById = useWorkspace((state) => state.jobsById);
  const documents = documentsPage?.items ?? [];
  const conversations = conversationsPage?.items ?? [];
  const projectNotes = notes.filter((note) => note.projectId === project.id).toSorted((a, b) => Date.parse(b.updatedAt) - Date.parse(a.updatedAt));
  const queue = uploadingProjectId === project.id ? uploadQueue : [];
  const readyCount = documents.filter((document) => document.status === "Completed").length;

  return (
    <div className="flex h-full min-h-0 flex-col bg-sidebar text-sidebar-foreground">
      <div className="flex h-[76px] shrink-0 items-center justify-between gap-2 border-b border-sidebar-border px-5">
        <Brand />
        <Button variant="ghost" size="icon-sm" className="hidden text-muted-foreground lg:inline-flex" aria-label="Collapse sidebar" onClick={() => actions.setSidebarCollapsed(true)}><PanelLeftClose /></Button>
      </div>
      <div className="flex-1 overflow-y-auto px-4 pt-4 pb-6">
        <Button asChild variant="ghost" size="sm" className="mb-5 w-full justify-start text-xs font-normal text-muted-foreground"><Link href="/"><ArrowLeft className="size-3.5" />All projects</Link></Button>

        <section aria-labelledby={`${sectionId}-conversations`}>
          <div className="mb-3 flex items-center justify-between px-2">
            <h2 id={`${sectionId}-conversations`} className="text-[10px] font-semibold tracking-[0.13em] text-muted-foreground">CONVERSATIONS <span className="ml-1.5 font-normal tracking-normal">{conversations.length}</span></h2>
            <Button variant="ghost" size="icon-xs" aria-label="New conversation" onClick={() => actions.openPanel({ kind: "conversation-create" })}><MessageSquarePlus /></Button>
          </div>
          {conversationsPage?.status === "error" ? <p role="alert" className="px-2 text-[11px] text-destructive">{conversationsPage.error}</p> : null}
          {conversations.length ? (
            <ul className="space-y-1">
              {conversations.map((conversation) => (
                <li key={conversation.id}>
                  <div className="group flex items-center gap-1">
                    <Link href={conversationHref(project.id, conversation.id)} className="flex min-w-0 flex-1 items-start gap-2.5 rounded-lg px-2.5 py-2.5 transition-colors hover:bg-sidebar-accent" aria-label={`Open conversation ${conversation.title ?? "Untitled"}`}>
                      <span className="line-clamp-2 text-xs leading-5 font-medium">{conversation.title ?? "Untitled conversation"}</span>
                    </Link>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild><Button variant="ghost" size="icon-xs" aria-label={`Conversation options for ${conversation.title ?? "Untitled"}`} className="shrink-0 opacity-0 group-hover:opacity-100 focus:opacity-100"><MoreHorizontal /></Button></DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-44">
                        <DropdownMenuItem onSelect={() => actions.openPanel({ kind: "conversation-rename", conversationId: conversation.id })} className="py-2"><PencilLine />Rename</DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem variant="destructive" onSelect={() => actions.openPanel({ kind: "conversation-delete", conversationId: conversation.id })} className="py-2"><Trash2 />Delete</DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="mx-1 rounded-xl border border-dashed border-sidebar-border px-3 py-5 text-center">
              <p className="text-xs text-muted-foreground">No conversations yet.</p>
              <Button variant="outline" size="sm" onClick={() => actions.openPanel({ kind: "conversation-create" })} className="mt-3 bg-card text-xs"><Plus />New conversation</Button>
            </div>
          )}
        </section>

        <section aria-labelledby={`${sectionId}-sources`} className="mt-8">
          <div className="mb-3 flex items-center justify-between px-2">
            <h2 id={`${sectionId}-sources`} className="text-[10px] font-semibold tracking-[0.13em] text-muted-foreground">SOURCES <span className="ml-1.5 font-normal tracking-normal">{documents.length}</span></h2>
            <Button variant="ghost" size="icon-xs" data-dialog-return-focus aria-label="Add sources" onClick={() => actions.openPanel({ kind: "upload" })}><Plus /></Button>
          </div>
          {documents.length ? (
            <ul className="space-y-1">
              {documents.map((document) => <DocumentRow key={document.id} document={document} jobStage={jobsById[documentJobId(document, jobsById)]?.stage} />)}
            </ul>
          ) : (
            <div className="mx-1 rounded-xl border border-dashed border-sidebar-border px-3 py-5 text-center">
              <FileUp className="mx-auto mb-2.5 size-5 text-muted-foreground" />
              <p className="text-xs text-muted-foreground">Your research starts here.</p>
              <Button variant="outline" size="sm" onClick={() => actions.openPanel({ kind: "upload" })} className="mt-3 bg-card text-xs"><Plus />Add your first source</Button>
            </div>
          )}
          {queue.length ? (
            <button onClick={() => actions.openPanel({ kind: "upload" })} className="mt-3 flex w-full items-center gap-2 rounded-lg border bg-card/60 px-3 py-2.5 text-left text-[11px]">
              {queue.some((task) => task.status === "error") ? <CircleAlert className="size-3.5 shrink-0 text-destructive" /> : <Loader2 className="size-3.5 shrink-0 animate-spin" />}
              <span>{queue.some((task) => task.status === "error") ? "Some files need attention" : "Uploading your sources..."}</span>
            </button>
          ) : null}
          {readyCount > 0 ? <p className="mt-2 px-2 text-[10px] text-muted-foreground">{readyCount} {readyCount === 1 ? "source ready" : "sources ready"} for questions.</p> : null}
        </section>

        <section aria-labelledby={`${sectionId}-notes`} className="mt-8">
          <div className="mb-3 flex items-center justify-between px-2">
            <h2 id={`${sectionId}-notes`} className="text-[10px] font-semibold tracking-[0.13em] text-muted-foreground">SAVED NOTES <span className="ml-1.5 font-normal tracking-normal">{projectNotes.length}</span></h2>
            <Button variant="ghost" size="icon-xs" aria-label="Add note" onClick={() => actions.openPanel({ kind: "note" })}><Plus /></Button>
          </div>
          {projectNotes.length ? (
            <ul className="space-y-1">{projectNotes.map((note) => <li key={note.id}><button onClick={() => actions.openPanel({ kind: "note", id: note.id })} className="flex w-full items-start gap-2.5 rounded-lg px-2.5 py-2.5 text-left transition-colors hover:bg-sidebar-accent"><Bookmark className="mt-0.5 size-4 shrink-0 text-muted-foreground" /><span className="line-clamp-2 text-xs leading-5">{note.title}</span></button></li>)}</ul>
          ) : <p className="px-2.5 text-[11px] leading-5 text-muted-foreground">Save a useful answer or add a thought of your own. Notes stay on this device.</p>}
        </section>

        <section aria-labelledby={`${sectionId}-guide`} className="mt-8 rounded-xl border border-sidebar-border bg-card/65 p-4">
          <h2 id={`${sectionId}-guide`} className="mb-3 flex items-center gap-2 text-[10px] font-semibold tracking-[0.1em]"><Sparkles className="size-3.5 text-muted-foreground" />PROJECT GUIDE</h2>
          <p className="text-xs leading-5 text-muted-foreground">Generate summaries, FAQs, or study guides from your sources.</p>
          <Button variant="outline" size="sm" className="mt-4 w-full justify-between bg-card text-xs" disabled={!readyCount} onClick={() => actions.openPanel({ kind: "guide" })}>Generate Guide<ArrowRight className="size-3.5" /></Button>
        </section>
      </div>
      <div className="shrink-0 border-t border-sidebar-border p-3">
        <AccountMenu variant="sidebar" />
      </div>
    </div>
  );
}

function documentJobId(document: Document, jobsById: Record<string, unknown>): string {
  for (const [id, job] of Object.entries(jobsById)) {
    if (job && typeof job === "object" && (job as { targetDocumentId?: string }).targetDocumentId === document.id) return id;
  }
  return "";
}

function DocumentRow({ document, jobStage }: { document: Document; jobStage?: string | null }) {
  const { state: { project }, actions } = useProject();
  const retryDocumentTask = useWorkspace((state) => state.retryDocumentTask);
  const deleteDocumentTask = useWorkspace((state) => state.deleteDocumentTask);
  const [busy, setBusy] = useState(false);
  const isProcessing = document.status === "Pending" || document.status === "Processing";
  const Icon = document.status === "Completed" ? Check : document.status === "Failed" ? CircleAlert : Loader2;
  async function retry() {
    setBusy(true);
    try { await retryDocumentTask(project.id, document.id); toast.success("Processing restarted."); }
    catch (error) { toast.error(v2ErrorMessage(error)); }
    finally { setBusy(false); }
  }
  async function remove() {
    setBusy(true);
    try { await deleteDocumentTask(project.id, document.id); toast.success("Document deletion started."); }
    catch (error) { toast.error(v2ErrorMessage(error)); }
    finally { setBusy(false); }
  }
  return (
    <li className="group">
      <div className="flex items-center gap-1">
        <button onClick={() => actions.openPanel({ kind: "document", documentId: document.id })} className="flex min-w-0 flex-1 items-start gap-2.5 rounded-lg px-2.5 py-2.5 text-left transition-colors hover:bg-sidebar-accent" aria-label={`Open source ${document.fileName}`}>
          <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-md border border-sidebar-border bg-card/60">
            <Icon className={`size-3.5 text-muted-foreground ${isProcessing ? "animate-spin" : ""}`} />
          </span>
          <span className="min-w-0">
            <span className="block truncate text-xs leading-5 font-medium" title={document.fileName}>{document.fileName}</span>
            <span className="block text-[10px] text-muted-foreground">
              {document.status === "Completed" ? `${document.chunkCount ?? "?"} chunks · Ready` : `${documentStatusLabel(document.status)}${jobStage ? ` · ${jobStageLabel(jobStage as never)}` : ""}`}
              {document.processingError ? ` — ${document.processingError}` : ""}
            </span>
          </span>
        </button>
        <DropdownMenu>
          <DropdownMenuTrigger asChild><Button variant="ghost" size="icon-xs" aria-label={`Options for ${document.fileName}`} className="shrink-0 opacity-0 group-hover:opacity-100 focus:opacity-100"><MoreHorizontal /></Button></DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-44">
            {document.status === "Failed" ? <DropdownMenuItem onSelect={() => void retry()} className="py-2" disabled={busy}><RotateCcw />Retry processing</DropdownMenuItem> : null}
            <DropdownMenuItem variant="destructive" onSelect={() => void remove()} className="py-2" disabled={busy}><Trash2 />Delete document</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </li>
  );
}

