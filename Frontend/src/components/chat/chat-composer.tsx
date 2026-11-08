"use client";

import { useId, useState, type FormEvent } from "react";
import { ArrowUp, Plus, Square } from "lucide-react";
import { useNotebook } from "@/components/notebooks/notebook-provider";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

export function ChatComposer() {
  const { state: { notebook }, actions, meta } = useNotebook();
  const [input, setInput] = useState("");
  const inputId = useId();
  const pending = useWorkspace((state) => state.pendingMap[meta.scope] ?? false);
  const sendMessage = useWorkspace((state) => state.sendMessage);
  const stopMessage = useWorkspace((state) => state.stopMessage);
  const hasSources = notebook.sourceFilenames.length > 0;
  function submit(event: FormEvent) {
    event.preventDefault();
    if (!input.trim() || pending || !hasSources) return;
    const query = input.trim();
    setInput("");
    void sendMessage(query, notebook.id);
  }
  return (
    <div className="shrink-0 px-4 pt-3 pb-[max(16px,env(safe-area-inset-bottom))] sm:px-8 sm:pb-5">
      <form onSubmit={submit} aria-label="Ask about notebook sources" className="mx-auto max-w-[760px] rounded-2xl border bg-card shadow-sm transition-shadow focus-within:border-ring/70 focus-within:ring-2 focus-within:ring-ring/15">
        <label htmlFor={inputId} className="sr-only">Ask a question</label>
        <Textarea id={inputId} value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} disabled={!hasSources} maxLength={8000} rows={1} placeholder={hasSources ? "Ask a question about your sources..." : "Add a PDF source to start a conversation..."} className="max-h-40 min-h-14 resize-none rounded-2xl border-0 bg-transparent! px-4 pt-4 pb-2 text-sm shadow-none focus-visible:ring-0 disabled:opacity-70 sm:px-5" />
        <div className="flex items-center justify-between gap-3 px-3 pt-1 pb-3 sm:px-4">
          <div className="flex items-center gap-2"><Tooltip><TooltipTrigger asChild><Button type="button" variant="ghost" size="icon-sm" aria-label="Add sources to notebook" onClick={() => actions.openPanel({ kind: "upload" })} className="text-muted-foreground"><Plus /></Button></TooltipTrigger><TooltipContent>Add PDF sources</TooltipContent></Tooltip><span className="text-[10px] text-muted-foreground">{notebook.sourceFilenames.length} {notebook.sourceFilenames.length === 1 ? "source" : "sources"}</span></div>
          <div className="flex items-center gap-3"><span className="hidden text-[10px] text-muted-foreground/75 sm:inline">Shift + Enter for a new line</span>{pending ? <Button type="button" variant="secondary" size="icon" aria-label="Stop response" onClick={() => stopMessage(notebook.id)} className="size-9 rounded-xl"><Square className="size-3.5 fill-current" /></Button> : <Button type="submit" size="icon" disabled={!input.trim() || !hasSources} aria-label="Send question" className="size-9 rounded-xl"><ArrowUp className="size-4" /></Button>}</div>
        </div>
      </form>
      <p className="mt-3 text-center text-[10px] text-muted-foreground">NoteMind can make mistakes. Verify important info.</p>
    </div>
  );
}
