"use client";

import dynamic from "next/dynamic";
import { useId, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { ArrowUpRight, BookOpenText, Check, Copy, Download, FileText, GraduationCap, HelpCircle, RotateCcw, Share2, Sparkles, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { documentStatusLabel, markdownFilename, projectMarkdown, conversationHref, conversationMarkdown } from "@/lib/projects";
import { documentFileUrl } from "@/services/projects/documents";
import { fetchAllMessages } from "@/services/projects/conversations";
import { v2ErrorMessage } from "@/services/v2http";
import { Citations } from "@/components/chat/citations";
import { DocumentUploadDialog } from "@/components/documents/source-upload-dialog";
import { CreateConversationDialog, DeleteConversationDialog, DeleteProjectDialog, RenameConversationDialog, RenameProjectDialog } from "@/components/projects/project-dialogs";
import { useProject } from "@/components/projects/project-provider";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { projectScope } from "@/lib/projects";

const Markdown = dynamic(() => import("@/components/chat/markdown"));

export function ProjectDialogs() {
  const { state: { project, panel }, actions } = useProject();
  const note = useWorkspace((state) => (panel?.kind === "note" && panel.id ? state.notes.find((item) => item.id === panel.id) : undefined));
  const router = useRouter();
  if (!panel) return null;
  if (panel.kind === "upload") return <DocumentUploadDialog projectId={project.id} onClose={actions.closePanel} />;
  if (panel.kind === "rename") return <RenameProjectDialog project={project} onClose={actions.closePanel} />;
  if (panel.kind === "delete") return <DeleteProjectDialog project={project} onClose={actions.closePanel} onDeleted={() => router.replace("/")} />;
  if (panel.kind === "conversation-create") return <CreateConversationDialog projectId={project.id} onClose={actions.closePanel} onCreated={(conversationId) => router.push(conversationHref(project.id, conversationId))} />;
  if (panel.kind === "conversation-rename") return <RenameConversationDialogWrapper conversationId={panel.conversationId} onClose={actions.closePanel} />;
  if (panel.kind === "conversation-delete") return <DeleteConversationDialogWrapper conversationId={panel.conversationId} onClose={actions.closePanel} />;
  if (panel.kind === "document") return <DocumentDialog documentId={panel.documentId} />;
  if (panel.kind === "note") return <NoteDialog note={note} />;
  if (panel.kind === "guide") return <GuideDialog />;
  if (panel.kind === "export") return <ExportDialog />;
  return null;
}

function RenameConversationDialogWrapper({ conversationId, onClose }: { conversationId: string; onClose: () => void }) {
  const identity = useWorkspace((state) => state.identity);
  const { state: { project } } = useProject();
  const conversation = useWorkspace((state) => (identity ? state.conversationDetailByScope[`${identity}:${project.id}:${conversationId}`] : undefined));
  const conversations = useWorkspace((state) => (identity ? state.conversationsByScope[projectScope(identity, project.id)]?.items.find((item) => item.id === conversationId) : undefined));
  return <RenameConversationDialog projectId={project.id} conversationId={conversationId} initialTitle={conversation?.title ?? conversations?.title ?? ""} onClose={onClose} />;
}

function DeleteConversationDialogWrapper({ conversationId, onClose }: { conversationId: string; onClose: () => void }) {
  const identity = useWorkspace((state) => state.identity);
  const { state: { project } } = useProject();
  const conversation = useWorkspace((state) => (identity ? state.conversationDetailByScope[`${identity}:${project.id}:${conversationId}`] : undefined));
  const conversations = useWorkspace((state) => (identity ? state.conversationsByScope[projectScope(identity, project.id)]?.items.find((item) => item.id === conversationId) : undefined));
  return <DeleteConversationDialog projectId={project.id} conversationId={conversationId} title={conversation?.title ?? conversations?.title ?? null} onClose={onClose} />;
}

function DocumentDialog({ documentId }: { documentId: string }) {
  const { state: { project }, actions } = useProject();
  const identity = useWorkspace((state) => state.identity);
  const document = useWorkspace((state) => (identity ? state.documentsByScope[projectScope(identity, project.id)]?.items.find((item) => item.id === documentId) : undefined));
  const retryDocumentTask = useWorkspace((state) => state.retryDocumentTask);
  const deleteDocumentTask = useWorkspace((state) => state.deleteDocumentTask);
  const loadDocuments = useWorkspace((state) => state.loadDocuments);
  const [busy, setBusy] = useState(false);
  if (!document) return null;
  const fileUrl = documentFileUrl(project.id, document.id);
  const docId = document.id;
  async function retry() {
    setBusy(true);
    try { await retryDocumentTask(project.id, docId); toast.success("Processing restarted."); void loadDocuments(project.id, { reset: true }); }
    catch (error) { toast.error(v2ErrorMessage(error)); }
    finally { setBusy(false); }
  }
  async function remove() {
    setBusy(true);
    try { await deleteDocumentTask(project.id, docId); actions.closePanel(); toast.success("Document deletion started."); }
    catch (error) { toast.error(v2ErrorMessage(error)); }
    finally { setBusy(false); }
  }
  return (
    <Dialog open onOpenChange={(open) => { if (!open) actions.closePanel(); }}>
      <DialogContent className="max-h-[92dvh] overflow-y-auto sm:max-w-3xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 pr-6"><FileText className="size-4 shrink-0" /><span className="truncate">{document.fileName}</span></DialogTitle>
          <DialogDescription>{documentStatusLabel(document.status)}{document.chunkCount ? ` · ${document.chunkCount} chunks` : ""}{document.processingError ? ` — ${document.processingError}` : ""}. Original PDF for {project.name}.</DialogDescription>
        </DialogHeader>
        {document.status === "Completed" ? (
          <iframe src={fileUrl} title={`PDF preview of ${document.fileName}`} className="h-[55dvh] w-full rounded-lg border bg-muted" />
        ) : (
          <div className="rounded-xl border border-dashed px-5 py-10 text-center text-sm text-muted-foreground">
            {document.status === "Failed" ? `Processing failed${document.processingError ? `: ${document.processingError}` : ""}.` : "The PDF is not ready to preview yet. Processing continues in the background."}
          </div>
        )}
        <DialogFooter className="sm:justify-between">
          <div className="flex gap-2">
            <Button variant="ghost" disabled={busy} onClick={() => void remove()} className="text-xs text-destructive"><Trash2 className="size-3.5" />Delete document</Button>
            {document.status === "Failed" ? <Button variant="outline" disabled={busy} onClick={() => void retry()}><RotateCcw />Retry processing</Button> : null}
          </div>
          {document.status === "Completed" ? <Button asChild><a href={fileUrl} target="_blank" rel="noopener noreferrer">Open PDF<ArrowUpRight /></a></Button> : <Button variant="outline" onClick={actions.closePanel}>Close</Button>}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function NoteDialog({ note }: { note?: { id: string } }) {
  const { state: { project }, actions } = useProject();
  const saveNote = useWorkspace((state) => state.saveNote);
  const removeNote = useWorkspace((state) => state.removeNote);
  const foundNote = useWorkspace((state) => (note?.id ? state.notes.find((item) => item.id === note.id) : undefined));
  const [title, setTitle] = useState(foundNote?.title ?? "");
  const [text, setText] = useState(foundNote?.text ?? "");
  const id = useId();
  function submit(event: FormEvent) {
    event.preventDefault();
    if (saveNote(project.id, title, text, foundNote?.citations ?? [], foundNote?.id)) { actions.closePanel(); toast.success("Note saved."); }
  }
  return (
    <Dialog open onOpenChange={(open) => { if (!open) actions.closePanel(); }}>
      <DialogContent className="max-h-[90dvh] overflow-y-auto sm:max-w-2xl">
        <DialogHeader><DialogTitle className="text-lg font-semibold">{foundNote ? "Your saved note" : "Keep a thought"}</DialogTitle><DialogDescription>{foundNote ? "Make this insight your own. Markdown is supported." : "Capture an idea, a connection, or something to come back to. Notes stay on this device for your account."}</DialogDescription></DialogHeader>
        <form onSubmit={submit} className="space-y-4">
          <div className="space-y-2"><label htmlFor={`${id}-title`} className="text-xs font-medium">Title</label><Input id={`${id}-title`} value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Give your note a title" maxLength={120} required className="h-10" /></div>
          <Tabs defaultValue="write" className="gap-3"><TabsList><TabsTrigger value="write">Write</TabsTrigger><TabsTrigger value="preview">Preview</TabsTrigger></TabsList><TabsContent value="write"><label htmlFor={`${id}-text`} className="sr-only">Note content</label><Textarea id={`${id}-text`} value={text} onChange={(event) => setText(event.target.value)} placeholder="What’s worth remembering?" maxLength={30000} required className="max-h-80 min-h-56 leading-7" /></TabsContent><TabsContent value="preview" className="max-h-80 min-h-56 overflow-y-auto rounded-lg border p-4">{text.trim() ? <Markdown text={text} /> : <p className="text-sm text-muted-foreground">Your formatted note will appear here.</p>}</TabsContent></Tabs>
          {foundNote?.citations.length ? <Citations citations={foundNote.citations} projectId={project.id} /> : null}
          <DialogFooter className="sm:justify-between"><div>{foundNote ? <Button type="button" variant="ghost" className="text-destructive" onClick={() => { removeNote(foundNote.id); actions.closePanel(); toast.success("Note deleted."); }}><Trash2 />Delete note</Button> : null}</div><div className="flex justify-end gap-2"><Button type="button" variant="outline" onClick={actions.closePanel}>Cancel</Button><Button type="submit" disabled={!title.trim() || !text.trim()}><Check />Save note</Button></div></DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

const guideOptions = [
  { id: "summary", icon: BookOpenText, title: "Source overview", text: "The main ideas, in a clear and concise summary.", prompt: "Create a clear overview of this project's sources, organized into key ideas and important findings. Include supporting page citations." },
  { id: "faq", icon: HelpCircle, title: "Frequently asked questions", text: "Questions and answers that get to the heart of it.", prompt: "Create a frequently asked questions guide from the sources in this project. Give useful questions and clear answers, with supporting citations." },
  { id: "study", icon: GraduationCap, title: "Study guide", text: "Core concepts, definitions, and questions to explore.", prompt: "Create a study guide from this project's sources. Include core concepts, important definitions, connections, and practice questions. Cite the source pages for factual explanations." },
];

function GuideDialog() {
  const { state: { project, conversationId }, actions } = useProject();
  const router = useRouter();
  const [selected, setSelected] = useState("summary");
  const sendMessage = useWorkspace((state) => state.sendMessage);
  const createConversationForProject = useWorkspace((state) => state.createConversationForProject);
  const [busy, setBusy] = useState(false);
  async function generate() {
    const guide = guideOptions.find((option) => option.id === selected);
    if (!guide) return;
    setBusy(true);
    try {
      let targetConversationId = conversationId;
      if (!targetConversationId) {
        const created = await createConversationForProject(project.id, guide.title);
        if (!created) return;
        targetConversationId = created.id;
      }
      actions.closePanel();
      router.push(conversationHref(project.id, targetConversationId));
      void sendMessage(project.id, targetConversationId, guide.prompt);
    } catch (error) {
      toast.error(v2ErrorMessage(error));
    } finally { setBusy(false); }
  }
  return (
    <Dialog open onOpenChange={(open) => { if (!open) actions.closePanel(); }}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader><span className="mb-2 flex size-10 items-center justify-center rounded-xl bg-secondary"><Sparkles className="size-5" /></span><DialogTitle className="text-xl font-semibold tracking-tight">A fresh perspective on your sources</DialogTitle><DialogDescription>Choose a guide to generate in your conversation. You can save the result as a note.</DialogDescription></DialogHeader>
        <fieldset className="space-y-2"><legend className="sr-only">Guide format</legend>{guideOptions.map(({ id, icon: Icon, title, text }) => <label key={id} className={`flex cursor-pointer items-start gap-3 rounded-xl border p-4 transition-colors hover:bg-muted/50 ${selected === id ? "border-primary/35 bg-secondary/50" : ""}`}><input type="radio" name="guide-format" value={id} checked={selected === id} onChange={() => setSelected(id)} className="mt-1 accent-primary" /><Icon className="mt-0.5 size-4 shrink-0 text-muted-foreground" /><span><span className="block text-sm font-medium">{title}</span><span className="mt-1 block text-xs leading-5 text-muted-foreground">{text}</span></span></label>)}</fieldset>
        <DialogFooter><Button disabled={busy} onClick={() => void generate()}><Sparkles />{busy ? "Creating…" : "Generate guide"}</Button></DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function ExportDialog() {
  const { state: { project, conversationId }, actions } = useProject();
  const identity = useWorkspace((state) => state.identity);
  const allNotes = useWorkspace((state) => state.notes);
  const notes = allNotes.filter((note) => note.projectId === project.id);
  const documentsPage = useWorkspace((state) => (identity ? state.documentsByScope[projectScope(identity, project.id)] : undefined));
  const documents = documentsPage?.items ?? [];
  const conversationsPage = useWorkspace((state) => (identity ? state.conversationsByScope[projectScope(identity, project.id)] : undefined));
  const conversations = conversationsPage?.items ?? [];
  const [markdown, setMarkdown] = useState("");
  const [busy, setBusy] = useState(false);

  async function build() {
    setBusy(true);
    try {
      const targets = conversationId ? conversations.filter((item) => item.id === conversationId) : conversations;
      const messagesByConversation: Record<string, import("@/lib/api-types").Message[]> = {};
      for (const conversation of targets) {
        messagesByConversation[conversation.id] = await fetchAllMessages(project.id, conversation.id);
      }
      if (conversationId) {
        const conversation = targets[0];
        const text = conversation ? conversationMarkdown(project, conversation, messagesByConversation[conversation.id] ?? [], notes) : projectMarkdown(project, documents, conversations, messagesByConversation, notes);
        setMarkdown(text);
      } else {
        setMarkdown(projectMarkdown(project, documents, conversations, messagesByConversation, notes));
      }
    } catch (error) {
      toast.error(v2ErrorMessage(error));
    } finally { setBusy(false); }
  }

  async function copy() {
    const text = markdown || (await buildAndGet());
    try { await navigator.clipboard.writeText(text); toast.success("Copied as Markdown."); }
    catch { toast.error("Copy is unavailable. Use Download Markdown instead."); }
  }
  async function buildAndGet(): Promise<string> {
    if (markdown) return markdown;
    setBusy(true);
    try {
      const targets = conversationId ? conversations.filter((item) => item.id === conversationId) : conversations;
      const messagesByConversation: Record<string, unknown> = {};
      for (const conversation of targets) {
        messagesByConversation[conversation.id] = await fetchAllMessages(project.id, conversation.id);
      }
      const text = projectMarkdown(project, documents, conversations, messagesByConversation as Record<string, import("@/lib/api-types").Message[]>, notes);
      setMarkdown(text);
      return text;
    } finally { setBusy(false); }
  }
  function download() {
    const text = markdown;
    if (!text) return;
    const url = URL.createObjectURL(new Blob([text], { type: "text/markdown;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = markdownFilename(project.name);
    document.body.appendChild(link);
    link.click();
    link.remove();
    requestAnimationFrame(() => URL.revokeObjectURL(url));
    toast.success("Project exported.");
  }

  return (
    <Dialog open onOpenChange={(open) => { if (!open) actions.closePanel(); }}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader><span className="mb-2 flex size-10 items-center justify-center rounded-xl bg-secondary"><Share2 className="size-4" /></span><DialogTitle className="text-xl font-semibold tracking-tight">Export what you’ve learned</DialogTitle><DialogDescription>Export all server pages for this {conversationId ? "conversation" : "project"} plus your on-device notes, with citations. Unresolved imported citations stay visibly unresolved.</DialogDescription></DialogHeader>
        <div className="rounded-xl border bg-background/50 p-5">
          <p className="font-medium">{project.name}</p>
          <p className="mt-2 text-xs text-muted-foreground">{documents.length} sources · {notes.length} notes · {conversations.length} conversations</p>
          {!markdown ? <Button variant="outline" size="sm" className="mt-4" disabled={busy} onClick={() => void build()}>{busy ? "Collecting pages…" : "Collect all pages"}</Button> : <p className="mt-4 text-xs text-muted-foreground">Markdown collected — copy or download it.</p>}
        </div>
        <DialogFooter>
          <Button variant="outline" disabled={busy || !markdown} onClick={() => void copy()}><Copy />Copy Markdown</Button>
          <Button disabled={busy || !markdown} onClick={download}><Download />Download Markdown</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
