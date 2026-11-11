"use client";

import { useRef, useState, type DragEvent } from "react";
import { Check, CircleAlert, FileText, Loader2, RotateCcw, Upload } from "lucide-react";
import { jobStageLabel } from "@/services/projects/jobs";
import { documentStatusLabel, projectScope } from "@/lib/projects";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
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

export function DocumentUploadDialog({ projectId, onClose }: { projectId: string; onClose: () => void }) {
  const identity = useWorkspace((state) => state.identity);
  const uploading = useWorkspace((state) => state.isUploading);
  const uploadingProjectId = useWorkspace((state) => state.uploadingProjectId);
  const uploadQueue = useWorkspace((state) => state.uploadQueue);
  const uploadDocuments = useWorkspace((state) => state.uploadDocuments);
  const clearUploadQueue = useWorkspace((state) => state.clearUploadQueue);
  const jobsById = useWorkspace((state) => state.jobsById);
  const documentsPage = useWorkspace((state) => (identity ? state.documentsByScope[projectScope(identity, projectId)] : undefined));
  const queue = uploadingProjectId === projectId ? uploadQueue : [];
  const documents = documentsPage?.items ?? [];

  function close() {
    if (!uploading && uploadingProjectId === projectId) clearUploadQueue();
    onClose();
  }

  return (
    <Dialog open onOpenChange={(open) => { if (!open) close(); }}>
      <DialogContent className="max-h-[90dvh] overflow-y-auto sm:max-w-lg">
        <DialogHeader><DialogTitle className="text-xl font-semibold tracking-tight">Bring your sources together</DialogTitle><DialogDescription>Add PDFs to this project. Answers will use only the ready sources in this project — the same filename may be uploaded again as a distinct document.</DialogDescription></DialogHeader>
        <div className="mt-2 space-y-4">
          <PdfDropzone disabled={uploading} onFiles={(files) => void uploadDocuments(files, projectId)} />
          <p className="text-center text-[11px] leading-5 text-muted-foreground">PDFs with selectable text. Uploads are stored first, then processed in the background — you can navigate away and return; status is polled with backoff until it completes.</p>
          {uploading && uploadingProjectId !== projectId ? <p role="status" className="text-sm text-muted-foreground">Another project is uploading. You can add more files when it finishes.</p> : null}
          {queue.length ? (
            <ul aria-live="polite" aria-label="Upload progress" className="max-h-52 space-y-2 overflow-y-auto">
              {queue.map((task) => {
                const job = task.jobId ? jobsById[task.jobId] : undefined;
                const document = task.documentId ? documents.find((item) => item.id === task.documentId) : undefined;
                return (
                  <li key={task.id} className="rounded-lg border p-3">
                    <div className="flex items-start gap-3">
                      {task.status === "error" ? <CircleAlert className="mt-0.5 size-4 shrink-0 text-destructive" /> : task.status === "done" ? <Check className="mt-0.5 size-4 shrink-0" /> : task.status === "uploading" || task.status === "processing" ? <Loader2 className="mt-0.5 size-4 shrink-0 animate-spin text-muted-foreground" /> : <FileText className="mt-0.5 size-4 shrink-0 text-muted-foreground" />}
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-xs font-medium">{task.fileName}</p>
                        <p className={cn("mt-1 text-[11px] leading-5 text-muted-foreground", task.status === "error" && "text-destructive")}>
                          {task.message ?? (task.status === "uploading" ? `Uploading${task.progress != null ? ` ${task.progress}%` : "…"}` : document ? `${documentStatusLabel(document.status)}${job?.stage ? ` · ${jobStageLabel(job.stage)}` : ""}` : "Waiting…")}
                        </p>
                        {task.progress != null && task.status === "uploading" ? (
                          <div className="mt-2 h-1.5 overflow-hidden rounded bg-muted" role="progressbar" aria-valuenow={task.progress} aria-valuemin={0} aria-valuemax={100} aria-label={`Upload progress for ${task.fileName}`}>
                            <div className="h-full bg-primary transition-[width]" style={{ width: `${task.progress}%` }} />
                          </div>
                        ) : null}
                        {document?.processingError ? <p className="mt-1 text-[11px] text-destructive">{document.processingError}</p> : null}
                      </div>
                    </div>
                  </li>
                );
              })}
            </ul>
          ) : null}
          <div className="flex items-center justify-between gap-3">
            <p className="text-xs text-muted-foreground">PDFs already in this project</p>
            <Button variant="ghost" size="icon-sm" disabled aria-label="Project documents refresh automatically"><RotateCcw /></Button>
          </div>
          {documents.length ? (
            <ul className="max-h-48 space-y-1 overflow-y-auto rounded-xl border p-2">
              {documents.map((document) => (
                <li key={document.id} className="flex items-center gap-3 rounded-lg p-3">
                  <FileText className="size-4 shrink-0 text-muted-foreground" />
                  <span className="min-w-0 flex-1 truncate text-xs" title={document.fileName}>{document.fileName}</span>
                  <span className="shrink-0 text-[10px] text-muted-foreground">{documentStatusLabel(document.status)}</span>
                </li>
              ))}
            </ul>
          ) : <p className="text-xs text-muted-foreground">No project documents yet.</p>}
        </div>
        <DialogFooter className="mt-2"><Button variant="outline" onClick={close}>{uploading ? "Continue in background" : "Done"}</Button></DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
