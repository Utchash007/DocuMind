"use client";

import { useId, useRef, useState, type DragEvent } from "react";
import { Check, CircleAlert, FileText, FileUp, Loader2, Plus, RotateCcw, Upload } from "lucide-react";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";

function PdfDropzone({ disabled, onFiles }: { disabled: boolean; onFiles: (files: File[]) => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  function drop(event: DragEvent<HTMLButtonElement>) {
    event.preventDefault();
    setDragging(false);
    if (!disabled) onFiles(Array.from(event.dataTransfer.files));
  }
  return (
    <>
      <input ref={inputRef} type="file" accept=".pdf,application/pdf" multiple hidden disabled={disabled} onChange={(event) => { onFiles(Array.from(event.target.files ?? [])); event.target.value = ""; }} aria-label="PDF files" />
      <Button variant="outline" disabled={disabled} onClick={() => inputRef.current?.click()} onDragOver={(event) => { event.preventDefault(); if (!disabled) setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={drop} className={cn("h-48 w-full flex-col gap-3 rounded-xl border-dashed bg-background/50 p-6 whitespace-normal shadow-none", dragging && "border-primary bg-secondary")}>
        <span className="flex size-12 items-center justify-center rounded-xl border bg-card"><Upload className="size-5 text-muted-foreground" /></span>
        <span className="text-sm font-medium">Drop your PDFs here</span>
        <span className="text-xs font-normal text-muted-foreground">or click to choose files</span>
      </Button>
    </>
  );
}

export function SourceUploadDialog({ notebookId, onClose }: { notebookId: string; onClose: () => void }) {
  const notebook = useWorkspace((state) => state.notebooksMap[notebookId]);
  const documents = useWorkspace((state) => state.documents);
  const status = useWorkspace((state) => state.documentsStatus);
  const error = useWorkspace((state) => state.documentsError);
  const uploading = useWorkspace((state) => state.isUploading);
  const uploadNotebookId = useWorkspace((state) => state.uploadNotebookId);
  const uploadQueue = useWorkspace((state) => state.uploadQueue);
  const uploadDocuments = useWorkspace((state) => state.uploadDocuments);
  const clearUploadQueue = useWorkspace((state) => state.clearUploadQueue);
  const refreshDocuments = useWorkspace((state) => state.refreshDocuments);
  const addNotebookSources = useWorkspace((state) => state.addNotebookSources);
  const [selected, setSelected] = useState<string[]>([]);
  const [tab, setTab] = useState("upload");
  const id = useId();
  const available = documents.filter((document) => !notebook?.sourceFilenames.includes(document.filename));
  const queue = uploadNotebookId === notebookId ? uploadQueue : [];

  function close() {
    if (!uploading && uploadNotebookId === notebookId) clearUploadQueue();
    onClose();
  }

  return (
    <Dialog open onOpenChange={(open) => { if (!open) close(); }}>
      <DialogContent className="max-h-[90dvh] overflow-y-auto sm:max-w-lg">
        <DialogHeader><DialogTitle className="text-xl font-semibold tracking-tight">Bring your sources together</DialogTitle><DialogDescription>Add PDFs to this notebook. Answers will use only the sources you add here.</DialogDescription></DialogHeader>
        <Tabs value={tab} onValueChange={setTab} className="mt-2 gap-4">
          <TabsList className="w-full"><TabsTrigger value="upload"><FileUp />Upload PDFs</TabsTrigger><TabsTrigger value="existing"><FileText />Existing sources</TabsTrigger></TabsList>
          <TabsContent value="upload" className="space-y-4">
            <PdfDropzone disabled={uploading} onFiles={(files) => void uploadDocuments(files, notebookId)} />
            <p className="text-center text-[11px] leading-5 text-muted-foreground">PDFs with selectable text. Matching filenames replace existing sources on this API.</p>
            {uploading && uploadNotebookId !== notebookId ? <p role="status" className="text-sm text-muted-foreground">Another notebook is uploading. You can add more files when it finishes.</p> : null}
            {queue.length ? <ul aria-live="polite" aria-label="Upload progress" className="max-h-52 space-y-2 overflow-y-auto">{queue.map((task) => <li key={task.id} className="flex items-start gap-3 rounded-lg border p-3">{task.status === "processing" ? <Loader2 className="mt-0.5 size-4 shrink-0 animate-spin text-muted-foreground" /> : task.status === "done" ? <Check className="mt-0.5 size-4 shrink-0" /> : task.status === "error" ? <CircleAlert className="mt-0.5 size-4 shrink-0 text-destructive" /> : <FileText className="mt-0.5 size-4 shrink-0 text-muted-foreground" />}<div className="min-w-0"><p className="truncate text-xs font-medium">{task.filename}</p><p className={cn("mt-1 text-[11px] leading-5 text-muted-foreground", task.status === "error" && "text-destructive")}>{task.message ?? (task.status === "processing" ? "Reading and indexing your PDF..." : "Waiting to upload...")}</p></div></li>)}</ul> : null}
          </TabsContent>
          <TabsContent value="existing" className="space-y-3">
            <div className="flex items-center justify-between gap-3"><p className="text-xs text-muted-foreground">PDFs available on the connected API</p><Button variant="ghost" size="icon-sm" onClick={() => void refreshDocuments()} disabled={status === "loading" || uploading} aria-label="Refresh available sources"><RotateCcw className={status === "loading" ? "animate-spin" : ""} /></Button></div>
            {error ? <p role="alert" className="rounded-lg border border-destructive/20 p-3 text-xs leading-5 text-destructive">{error}</p> : null}
            {status === "loading" ? <div className="flex items-center justify-center gap-2 py-10 text-sm text-muted-foreground"><Loader2 className="size-4 animate-spin" />Loading available PDFs...</div> : available.length ? <div className="max-h-64 space-y-1 overflow-y-auto rounded-xl border p-2">{available.map((document, index) => <label key={document.filename} htmlFor={`${id}-${index}`} className="flex cursor-pointer items-center gap-3 rounded-lg p-3 hover:bg-muted"><input id={`${id}-${index}`} type="checkbox" checked={selected.includes(document.filename)} onChange={(event) => setSelected((previous) => event.target.checked ? [...previous, document.filename] : previous.filter((filename) => filename !== document.filename))} className="size-4 shrink-0 accent-primary" /><FileText className="size-4 shrink-0 text-muted-foreground" /><span className="min-w-0 break-all text-xs">{document.filename}</span></label>)}</div> : <div className="rounded-xl border border-dashed px-5 py-10 text-center"><FileText className="mx-auto mb-3 size-6 text-muted-foreground" /><p className="text-sm">No additional PDFs available</p><p className="mt-2 text-xs leading-5 text-muted-foreground">Upload a new PDF to add your first source.</p></div>}
          </TabsContent>
        </Tabs>
        <DialogFooter className="mt-2"><Button variant="outline" onClick={close}>{uploading ? "Continue in background" : "Done"}</Button>{tab === "existing" ? <Button disabled={!selected.length} onClick={() => { addNotebookSources(notebookId, selected); close(); }}><Plus />Add {selected.length || "selected"} {selected.length === 1 ? "source" : "sources"}</Button> : null}</DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
