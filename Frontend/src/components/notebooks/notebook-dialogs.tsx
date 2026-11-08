"use client";

import { useId, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { NotebookPen, Trash2 } from "lucide-react";
import { toast } from "sonner";
import type { Notebook } from "@/lib/types";
import { notebookHref } from "@/lib/notebooks";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";

function NotebookNameDialog({ title, description, initialName, submitLabel, onSubmit, onClose }: {
  title: string; description: string; initialName: string; submitLabel: string;
  onSubmit: (name: string) => void; onClose: () => void;
}) {
  const id = useId();
  const [name, setName] = useState(initialName);
  function submit(event: FormEvent) {
    event.preventDefault();
    if (name.trim()) onSubmit(name.trim());
  }
  return (
    <Dialog open onOpenChange={(open) => { if (!open) onClose(); }}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader><span className="mb-2 flex size-11 items-center justify-center rounded-xl bg-secondary"><NotebookPen className="size-5" /></span><DialogTitle className="text-xl font-semibold tracking-tight">{title}</DialogTitle><DialogDescription>{description}</DialogDescription></DialogHeader>
        <form onSubmit={submit} className="space-y-6">
          <div className="space-y-2"><label htmlFor={id} className="text-xs font-medium">Notebook name</label><Input id={id} value={name} onChange={(event) => setName(event.target.value)} placeholder="e.g. Quantum Computing Basics" maxLength={120} required className="h-11" /></div>
          <DialogFooter><Button type="button" variant="outline" onClick={onClose}>Cancel</Button><Button type="submit" disabled={!name.trim()}>{submitLabel}</Button></DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function CreateNotebookDialog({ onClose }: { onClose: () => void }) {
  const createNotebook = useWorkspace((state) => state.createNotebook);
  const router = useRouter();
  function create(name: string) {
    const id = createNotebook(name);
    if (!id) return;
    onClose();
    router.push(notebookHref(id));
  }
  return <NotebookNameDialog title="A new space for your ideas" description="Give your notebook a name. You can add PDF sources next." initialName="" submitLabel="Create notebook" onSubmit={create} onClose={onClose} />;
}

export function RenameNotebookDialog({ notebook, onClose }: { notebook: Notebook; onClose: () => void }) {
  const renameNotebook = useWorkspace((state) => state.renameNotebook);
  return <NotebookNameDialog title="Rename notebook" description="A good name makes your research easier to find." initialName={notebook.title} submitLabel="Save name" onSubmit={(name) => { renameNotebook(notebook.id, name); onClose(); }} onClose={onClose} />;
}

export function DeleteNotebookDialog({ notebook, onClose, onDeleted }: { notebook: Notebook; onClose: () => void; onDeleted?: () => void }) {
  const removeNotebook = useWorkspace((state) => state.removeNotebook);
  const uploading = useWorkspace((state) => state.isUploading && state.uploadNotebookId === notebook.id);
  function remove() {
    if (!removeNotebook(notebook.id)) return;
    onClose();
    onDeleted?.();
    toast.success("Notebook deleted.");
  }
  return (
    <Dialog open onOpenChange={(open) => { if (!open) onClose(); }}>
      <DialogContent>
        <DialogHeader><DialogTitle>Delete this notebook?</DialogTitle><DialogDescription>This removes “{notebook.title}”, its conversation, and its notes from this browser. Uploaded PDFs remain available to add to another notebook.</DialogDescription></DialogHeader>
        {uploading ? <p className="text-sm text-muted-foreground">Wait for this notebook’s upload to finish.</p> : null}
        <DialogFooter><Button variant="outline" onClick={onClose}>Keep notebook</Button><Button variant="destructive" disabled={uploading} onClick={remove}><Trash2 />Delete notebook</Button></DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
