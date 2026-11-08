"use client";

import dynamic from "next/dynamic";
import { useId, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { ArrowUpRight, BookOpenText, Check, Copy, Download, FileText, GraduationCap, HelpCircle, Share2, Sparkles, Trash2 } from "lucide-react";
import { toast } from "sonner";
import type { SavedNote } from "@/lib/types";
import { notebookMarkdown } from "@/lib/notebooks";
import { documentUrl } from "@/services/documents/documents";
import { Citations } from "@/components/chat/citations";
import { SourceUploadDialog } from "@/components/documents/source-upload-dialog";
import { DeleteNotebookDialog, RenameNotebookDialog } from "@/components/notebooks/notebook-dialogs";
import { useNotebook } from "@/components/notebooks/notebook-provider";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

const Markdown = dynamic(() => import("@/components/chat/markdown"));

export function NotebookDialogs() {
  const { state: { notebook, panel }, actions } = useNotebook();
  const note = useWorkspace((state) => panel?.kind === "note" && panel.id ? state.notesMap[panel.id] : undefined);
  const router = useRouter();
  if (!panel) return null;
  if (panel.kind === "upload") return <SourceUploadDialog notebookId={notebook.id} onClose={actions.closePanel} />;
  if (panel.kind === "rename") return <RenameNotebookDialog notebook={notebook} onClose={actions.closePanel} />;
  if (panel.kind === "delete") return <DeleteNotebookDialog notebook={notebook} onClose={actions.closePanel} onDeleted={() => router.replace("/")} />;
  if (panel.kind === "source") return <SourceDialog filename={panel.filename} />;
  if (panel.kind === "note") return <NoteDialog key={note?.id ?? "new-note"} note={note} />;
  if (panel.kind === "guide") return <GuideDialog />;
  if (panel.kind === "share") return <ShareDialog />;
  if (panel.kind === "clear-chat") return <ClearChatDialog />;
  return null;
}

function SourceDialog({ filename }: { filename: string }) {
  const { state: { notebook }, actions, meta } = useNotebook();
  const removeSource = useWorkspace((state) => state.removeNotebookSource);
  const pending = useWorkspace((state) => state.pendingMap[meta.scope]);
  return (
    <Dialog open onOpenChange={(open) => { if (!open) actions.closePanel(); }}>
      <DialogContent className="max-h-[92dvh] overflow-y-auto sm:max-w-3xl">
        <DialogHeader><DialogTitle className="flex items-center gap-2 pr-6"><FileText className="size-4 shrink-0" /><span className="truncate">{filename}</span></DialogTitle><DialogDescription>Original PDF source for {notebook.title}.</DialogDescription></DialogHeader>
        <iframe src={documentUrl(filename)} title={`PDF preview of ${filename}`} className="h-[55dvh] w-full rounded-lg border bg-muted" />
        <DialogFooter className="sm:justify-between"><Button variant="ghost" disabled={pending} onClick={() => { if (removeSource(notebook.id, filename)) { actions.closePanel(); toast.success("Source removed from this notebook."); } }} className="text-xs text-muted-foreground"><Trash2 className="size-3.5" />Remove from notebook</Button><Button asChild><a href={documentUrl(filename)} target="_blank" rel="noopener noreferrer">Open PDF<ArrowUpRight /></a></Button></DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function NoteDialog({ note }: { note?: SavedNote }) {
  const { state: { notebook }, actions } = useNotebook();
  const saveNote = useWorkspace((state) => state.saveNote);
  const removeNote = useWorkspace((state) => state.removeNote);
  const [title, setTitle] = useState(note?.title ?? "");
  const [text, setText] = useState(note?.text ?? "");
  const id = useId();
  function submit(event: FormEvent) {
    event.preventDefault();
    if (saveNote(notebook.id, title, text, note?.id)) { actions.closePanel(); toast.success("Note saved."); }
  }
  return (
    <Dialog open onOpenChange={(open) => { if (!open) actions.closePanel(); }}>
      <DialogContent className="max-h-[90dvh] overflow-y-auto sm:max-w-2xl">
        <DialogHeader><DialogTitle className="text-lg font-semibold">{note ? "Your saved note" : "Keep a thought"}</DialogTitle><DialogDescription>{note ? "Make this insight your own. Markdown is supported." : "Capture an idea, a connection, or something to come back to."}</DialogDescription></DialogHeader>
        <form onSubmit={submit} className="space-y-4">
          <div className="space-y-2"><label htmlFor={`${id}-title`} className="text-xs font-medium">Title</label><Input id={`${id}-title`} value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Give your note a title" maxLength={120} required className="h-10" /></div>
          <Tabs defaultValue="write" className="gap-3"><TabsList><TabsTrigger value="write">Write</TabsTrigger><TabsTrigger value="preview">Preview</TabsTrigger></TabsList><TabsContent value="write"><label htmlFor={`${id}-text`} className="sr-only">Note content</label><Textarea id={`${id}-text`} value={text} onChange={(event) => setText(event.target.value)} placeholder="What’s worth remembering?" maxLength={30000} required className="max-h-80 min-h-56 leading-7" /></TabsContent><TabsContent value="preview" className="max-h-80 min-h-56 overflow-y-auto rounded-lg border p-4">{text.trim() ? <Markdown text={text} /> : <p className="text-sm text-muted-foreground">Your formatted note will appear here.</p>}</TabsContent></Tabs>
          {note?.citations.length ? <Citations citations={note.citations} /> : null}
          <DialogFooter className="sm:justify-between"><div>{note ? <Button type="button" variant="ghost" className="text-destructive" onClick={() => { removeNote(note.id); actions.closePanel(); toast.success("Note deleted."); }}><Trash2 />Delete note</Button> : null}</div><div className="flex justify-end gap-2"><Button type="button" variant="outline" onClick={actions.closePanel}>Cancel</Button><Button type="submit" disabled={!title.trim() || !text.trim()}><Check />Save note</Button></div></DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

const guideOptions = [
  { id: "summary", icon: BookOpenText, title: "Source overview", text: "The main ideas, in a clear and concise summary.", prompt: "Create a clear overview of this notebook's sources, organized into key ideas and important findings. Include supporting page citations." },
  { id: "faq", icon: HelpCircle, title: "Frequently asked questions", text: "Questions and answers that get to the heart of it.", prompt: "Create a frequently asked questions guide from the sources in this notebook. Give useful questions and clear answers, with supporting citations." },
  { id: "study", icon: GraduationCap, title: "Study guide", text: "Core concepts, definitions, and questions to explore.", prompt: "Create a study guide from this notebook's sources. Include core concepts, important definitions, connections, and practice questions. Cite the source pages for factual explanations." },
];

function GuideDialog() {
  const { state: { notebook }, actions, meta } = useNotebook();
  const [selected, setSelected] = useState("summary");
  const pending = useWorkspace((state) => state.pendingMap[meta.scope]);
  const sendMessage = useWorkspace((state) => state.sendMessage);
  return (
    <Dialog open onOpenChange={(open) => { if (!open) actions.closePanel(); }}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader><span className="mb-2 flex size-10 items-center justify-center rounded-xl bg-secondary"><Sparkles className="size-5" /></span><DialogTitle className="text-xl font-semibold tracking-tight">A fresh perspective on your sources</DialogTitle><DialogDescription>Choose a guide to generate in your conversation. You can save the result as a note.</DialogDescription></DialogHeader>
        <fieldset className="space-y-2"><legend className="sr-only">Guide format</legend>{guideOptions.map(({ id, icon: Icon, title, text }) => <label key={id} className={cn("flex cursor-pointer items-start gap-3 rounded-xl border p-4 transition-colors hover:bg-muted/50", selected === id && "border-primary/35 bg-secondary/50")}><input type="radio" name="guide-format" value={id} checked={selected === id} onChange={() => setSelected(id)} className="mt-1 accent-primary" /><Icon className="mt-0.5 size-4 shrink-0 text-muted-foreground" /><span><span className="block text-sm font-medium">{title}</span><span className="mt-1 block text-xs leading-5 text-muted-foreground">{text}</span></span></label>)}</fieldset>
        <DialogFooter><Button disabled={pending || !notebook.sourceFilenames.length} onClick={() => { const guide = guideOptions.find((option) => option.id === selected); if (guide) { void sendMessage(guide.prompt, notebook.id); actions.closePanel(); } }}><Sparkles />Generate guide</Button></DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function ShareDialog() {
  const { state: { notebook }, actions, meta } = useNotebook();
  const thread = useWorkspace((state) => state.threadsMap[meta.scope]);
  const notesMap = useWorkspace((state) => state.notesMap);
  const notes = Object.values(notesMap).filter((note) => note.notebookId === notebook.id);
  const markdown = notebookMarkdown(notebook, thread?.messages ?? [], notes);
  function download() {
    const url = URL.createObjectURL(new Blob([markdown], { type: "text/markdown;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `${notebook.title.replace(/[^\p{L}\p{N} _-]/gu, "").trim() || "notebook"}.md`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    requestAnimationFrame(() => URL.revokeObjectURL(url));
    toast.success("Notebook exported.");
  }
  async function copy() {
    try { await navigator.clipboard.writeText(markdown); toast.success("Notebook copied as Markdown."); }
    catch { toast.error("Copy is unavailable. Use Download Markdown instead."); }
  }
  return (
    <Dialog open onOpenChange={(open) => { if (!open) actions.closePanel(); }}>
      <DialogContent className="sm:max-w-lg"><DialogHeader><span className="mb-2 flex size-10 items-center justify-center rounded-xl bg-secondary"><Share2 className="size-4" /></span><DialogTitle className="text-xl font-semibold tracking-tight">Share what you’ve learned</DialogTitle><DialogDescription>Export a readable copy of this notebook, including your conversation, notes, and citations.</DialogDescription></DialogHeader><div className="rounded-xl border bg-background/50 p-5"><p className="font-medium">{notebook.title}</p><p className="mt-2 text-xs text-muted-foreground">{notebook.sourceFilenames.length} sources · {notes.length} notes · {thread?.messages.length ?? 0} messages</p><p className="mt-4 text-xs leading-6 text-muted-foreground">Your notebooks live in this browser. Share a Markdown copy with anyone; the original PDF files are not included.</p></div><DialogFooter><Button variant="outline" onClick={() => void copy()}><Copy />Copy Markdown</Button><Button onClick={download}><Download />Download Markdown</Button></DialogFooter></DialogContent>
    </Dialog>
  );
}

function ClearChatDialog() {
  const { state: { notebook }, actions } = useNotebook();
  const clearThread = useWorkspace((state) => state.clearThread);
  return <Dialog open onOpenChange={(open) => { if (!open) actions.closePanel(); }}><DialogContent><DialogHeader><DialogTitle>Start a fresh conversation?</DialogTitle><DialogDescription>This clears the conversation in this notebook. Your sources and saved notes are kept.</DialogDescription></DialogHeader><DialogFooter><Button variant="outline" onClick={actions.closePanel}>Cancel</Button><Button variant="destructive" onClick={() => { clearThread(notebook.id); actions.closePanel(); }}>Clear conversation</Button></DialogFooter></DialogContent></Dialog>;
}
