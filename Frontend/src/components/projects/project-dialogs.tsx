"use client";

import { useId, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { NotebookPen, Trash2 } from "lucide-react";
import { toast } from "sonner";
import type { Project } from "@/lib/api-types";
import { projectHref } from "@/lib/projects";
import { v2ErrorMessage } from "@/services/v2http";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

function ProjectNameDialog({ title, description, initialName, initialDescription, submitLabel, onSubmit, onClose, busy }: {
  title: string; description: string; initialName: string; initialDescription?: string; submitLabel: string;
  onSubmit: (name: string, description: string | null) => void; onClose: () => void; busy?: boolean;
}) {
  const id = useId();
  const [name, setName] = useState(initialName);
  const [desc, setDesc] = useState(initialDescription ?? "");
  function submit(event: FormEvent) {
    event.preventDefault();
    if (name.trim()) onSubmit(name.trim(), desc.trim() ? desc.trim() : null);
  }
  return (
    <Dialog open onOpenChange={(open) => { if (!open) onClose(); }}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader><span className="mb-2 flex size-11 items-center justify-center rounded-xl bg-secondary"><NotebookPen className="size-5" /></span><DialogTitle className="text-xl font-semibold tracking-tight">{title}</DialogTitle><DialogDescription>{description}</DialogDescription></DialogHeader>
        <form onSubmit={submit} className="space-y-4">
          <div className="space-y-2"><label htmlFor={id} className="text-xs font-medium">Project name</label><Input id={id} value={name} onChange={(event) => setName(event.target.value)} placeholder="e.g. Quantum Computing Basics" maxLength={120} required className="h-11" /></div>
          <div className="space-y-2"><label htmlFor={`${id}-desc`} className="text-xs font-medium">Description <span className="font-normal text-muted-foreground">(optional)</span></label><Textarea id={`${id}-desc`} value={desc} onChange={(event) => setDesc(event.target.value)} placeholder="What is this project about?" maxLength={1000} rows={2} /></div>
          <DialogFooter><Button type="button" variant="outline" onClick={onClose}>Cancel</Button><Button type="submit" disabled={!name.trim() || busy}>{busy ? "Saving…" : submitLabel}</Button></DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function CreateProjectDialog({ onClose }: { onClose: () => void }) {
  const createProject = useWorkspace((state) => state.createProject);
  const [busy, setBusy] = useState(false);
  const router = useRouter();
  async function create(name: string, description: string | null) {
    setBusy(true);
    try {
      const project = await createProject({ name, description });
      if (!project) return;
      onClose();
      router.push(projectHref(project.id));
    } catch (error) {
      toast.error(v2ErrorMessage(error));
    } finally { setBusy(false); }
  }
  return <ProjectNameDialog title="A new space for your ideas" description="Give your project a name. You can add PDF sources next." initialName="" submitLabel="Create project" onSubmit={create} onClose={onClose} busy={busy} />;
}

export function RenameProjectDialog({ project, onClose }: { project: Project; onClose: () => void }) {
  const renameProject = useWorkspace((state) => state.renameProject);
  const [busy, setBusy] = useState(false);
  async function rename(name: string) {
    setBusy(true);
    try { await renameProject(project.id, name); onClose(); toast.success("Project renamed."); }
    catch (error) { toast.error(v2ErrorMessage(error)); }
    finally { setBusy(false); }
  }
  return <ProjectNameDialog title="Rename project" description="A good name makes your research easier to find." initialName={project.name} initialDescription={project.description ?? ""} submitLabel="Save name" onSubmit={rename} onClose={onClose} busy={busy} />;
}

export function DeleteProjectDialog({ project, onClose, onDeleted }: { project: Project; onClose: () => void; onDeleted?: () => void }) {
  const deleteProject = useWorkspace((state) => state.deleteProject);
  const [busy, setBusy] = useState(false);
  async function remove() {
    setBusy(true);
    try {
      const ok = await deleteProject(project.id);
      if (!ok) return;
      onClose();
      onDeleted?.();
      toast.success("Project deletion started. Cleanup continues in the background.");
    } catch (error) {
      toast.error(v2ErrorMessage(error));
    } finally { setBusy(false); }
  }
  return (
    <Dialog open onOpenChange={(open) => { if (!open) onClose(); }}>
      <DialogContent>
        <DialogHeader><DialogTitle>Delete this project?</DialogTitle><DialogDescription>This removes “{project.name}”, its conversations and documents from your workspace. Cleanup of stored PDFs runs in the background and cannot be undone.</DialogDescription></DialogHeader>
        <DialogFooter><Button variant="outline" onClick={onClose}>Keep project</Button><Button variant="destructive" disabled={busy} onClick={() => void remove()}><Trash2 />{busy ? "Deleting…" : "Delete project"}</Button></DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export function CreateConversationDialog({ projectId, onClose, onCreated }: { projectId: string; onClose: () => void; onCreated: (conversationId: string) => void }) {
  const createConversationForProject = useWorkspace((state) => state.createConversationForProject);
  const [title, setTitle] = useState("");
  const [busy, setBusy] = useState(false);
  const id = useId();
  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    try {
      const conversation = await createConversationForProject(projectId, title.trim() || undefined);
      if (!conversation) return;
      onClose();
      onCreated(conversation.id);
    } catch (error) {
      toast.error(v2ErrorMessage(error));
    } finally { setBusy(false); }
  }
  return (
    <Dialog open onOpenChange={(open) => { if (!open) onClose(); }}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader><DialogTitle className="text-xl font-semibold tracking-tight">New conversation</DialogTitle><DialogDescription>Conversations in a project share its sources but keep separate histories.</DialogDescription></DialogHeader>
        <form onSubmit={submit} className="space-y-4">
          <div className="space-y-2"><label htmlFor={id} className="text-xs font-medium">Title <span className="font-normal text-muted-foreground">(optional)</span></label><Input id={id} value={title} onChange={(event) => setTitle(event.target.value)} placeholder="e.g. Explain transformers" maxLength={120} className="h-11" /></div>
          <DialogFooter><Button type="button" variant="outline" onClick={onClose}>Cancel</Button><Button type="submit" disabled={busy}>{busy ? "Creating…" : "Create conversation"}</Button></DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function RenameConversationDialog({ projectId, conversationId, initialTitle, onClose }: { projectId: string; conversationId: string; initialTitle: string; onClose: () => void }) {
  const renameConversation = useWorkspace((state) => state.renameConversation);
  const [title, setTitle] = useState(initialTitle);
  const [busy, setBusy] = useState(false);
  const id = useId();
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!title.trim()) return;
    setBusy(true);
    try { await renameConversation(projectId, conversationId, title.trim()); onClose(); toast.success("Conversation renamed."); }
    catch (error) { toast.error(v2ErrorMessage(error)); }
    finally { setBusy(false); }
  }
  return (
    <Dialog open onOpenChange={(open) => { if (!open) onClose(); }}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader><DialogTitle>Rename conversation</DialogTitle><DialogDescription>A good title makes it easy to return to this thread.</DialogDescription></DialogHeader>
        <form onSubmit={submit} className="space-y-4">
          <div className="space-y-2"><label htmlFor={id} className="text-xs font-medium">Title</label><Input id={id} value={title} onChange={(event) => setTitle(event.target.value)} maxLength={120} required className="h-11" /></div>
          <DialogFooter><Button type="button" variant="outline" onClick={onClose}>Cancel</Button><Button type="submit" disabled={!title.trim() || busy}>{busy ? "Saving…" : "Save"}</Button></DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function DeleteConversationDialog({ projectId, conversationId, title, onClose }: { projectId: string; conversationId: string; title: string | null; onClose: () => void }) {
  const deleteConversationForProject = useWorkspace((state) => state.deleteConversationForProject);
  const [busy, setBusy] = useState(false);
  async function remove() {
    setBusy(true);
    try { await deleteConversationForProject(projectId, conversationId); onClose(); toast.success("Conversation deleted."); }
    catch (error) { toast.error(v2ErrorMessage(error)); }
    finally { setBusy(false); }
  }
  return (
    <Dialog open onOpenChange={(open) => { if (!open) onClose(); }}>
      <DialogContent>
        <DialogHeader><DialogTitle>Delete this conversation?</DialogTitle><DialogDescription>This permanently removes “{title ?? "Untitled conversation"}” and its messages. Sources and saved notes are kept.</DialogDescription></DialogHeader>
        <DialogFooter><Button variant="outline" onClick={onClose}>Keep conversation</Button><Button variant="destructive" disabled={busy} onClick={() => void remove()}><Trash2 />{busy ? "Deleting…" : "Delete"}</Button></DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
