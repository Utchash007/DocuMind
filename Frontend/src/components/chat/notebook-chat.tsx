"use client";

import { useEffect, useRef } from "react";
import { ArrowUpRight, FileText, FileUp, Layers3, Loader2, RotateCcw, Sparkles } from "lucide-react";
import type { ChatMessage as Message } from "@/lib/types";
import { BrandMark } from "@/components/brand";
import { ChatComposer } from "@/components/chat/chat-composer";
import { ChatMessage } from "@/components/chat/chat-message";
import { useNotebook } from "@/components/notebooks/notebook-provider";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { WorkspaceNotices } from "@/components/workspace-notices";
import { Button } from "@/components/ui/button";

const emptyMessages: Message[] = [];

export function NotebookChat() {
  const { state: { notebook }, meta } = useNotebook();
  const messages = useWorkspace((state) => state.threadsMap[meta.scope]?.messages ?? emptyMessages);
  const pending = useWorkspace((state) => state.pendingMap[meta.scope] ?? false);
  const error = useWorkspace((state) => state.errorsMap[meta.scope]);
  const retryMessage = useWorkspace((state) => state.retryMessage);
  const scrollRef = useRef<HTMLDivElement>(null);
  const following = useRef(true);

  useEffect(() => {
    const container = scrollRef.current;
    if (container && (following.current || messages.at(-1)?.role === "user")) {
      container.scrollTo({ top: container.scrollHeight, behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth" });
    }
  }, [messages, pending]);

  return (
    <>
      <div ref={scrollRef} onScroll={(event) => { const element = event.currentTarget; following.current = element.scrollHeight - element.scrollTop - element.clientHeight < 100; }} className="flex min-h-0 flex-1 flex-col overflow-y-auto overscroll-contain px-4 py-6 sm:px-8 sm:py-8">
        <div className="mx-auto w-full max-w-[760px]"><WorkspaceNotices /></div>
        {!messages.length ? <EmptyChat /> : <div role="log" aria-label="Conversation" aria-live="polite" aria-relevant="additions" className="mx-auto flex w-full max-w-[760px] flex-col gap-8 pt-3 pb-4">{messages.map((message) => <ChatMessage key={message.id} message={message} notebookId={notebook.id} />)}</div>}
        {pending ? <div role="status" className="mx-auto mt-5 mb-4 flex w-full max-w-[760px] items-center gap-3 text-xs text-muted-foreground"><span className="flex size-7 shrink-0 items-center justify-center rounded-lg border bg-card"><Sparkles className="size-3.5" /></span><Loader2 className="size-3.5 animate-spin" />Reading your sources...</div> : null}
        {error && !pending ? <div role="alert" className="mx-auto mt-5 w-full max-w-[760px] rounded-xl border border-destructive/20 bg-card p-4"><p className="text-sm font-medium">We couldn’t finish that answer.</p><p className="mt-1.5 text-xs leading-6 text-muted-foreground">{error.message}</p><Button variant="outline" size="sm" className="mt-3" disabled={!notebook.sourceFilenames.length} onClick={() => void retryMessage(notebook.id)}><RotateCcw className="size-3.5" />Retry question</Button></div> : null}
      </div>
      <ChatComposer />
    </>
  );
}

function EmptyChat() {
  const { state: { notebook }, actions } = useNotebook();
  const sendMessage = useWorkspace((state) => state.sendMessage);
  const hasSources = notebook.sourceFilenames.length > 0;
  return (
    <section aria-label="Start a conversation" className="mx-auto flex w-full max-w-[680px] flex-1 flex-col justify-center py-8 sm:py-12">
      <div className="text-center"><BrandMark className="mb-6 size-12 rounded-2xl" /><h2 className="text-[27px] leading-tight font-semibold tracking-[-0.045em] sm:text-[34px]">What would you like to know?</h2><p className="mt-3 text-sm leading-6 text-muted-foreground">Ask a question about your uploaded sources.</p>{!hasSources ? <Button onClick={() => actions.openPanel({ kind: "upload" })} className="mt-6 h-10 gap-2 rounded-xl px-4"><FileUp className="size-4" />Add your first PDF</Button> : <p className="mt-4 text-[10px] text-muted-foreground">A conversation grounded in {notebook.sourceFilenames.length} {notebook.sourceFilenames.length === 1 ? "source" : "sources"}.</p>}</div>
      <div className="mt-9 grid gap-3 sm:grid-cols-2 sm:gap-4">
        <button disabled={!hasSources} onClick={() => void sendMessage("Summarize the main ideas and key findings across the sources in this notebook. Include supporting citations.", notebook.id)} className="group rounded-xl border bg-card/65 p-5 text-left transition-colors hover:bg-card disabled:cursor-default disabled:opacity-55"><span className="mb-5 flex items-center justify-between"><FileText className="size-4 text-muted-foreground" /><ArrowUpRight className="size-3.5 text-muted-foreground/60 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" /></span><span className="block text-sm font-medium">Summarize all sources</span><span className="mt-2 block text-xs leading-5 text-muted-foreground">Get a high-level overview of everything you’ve uploaded.</span></button>
        <button disabled={!hasSources} onClick={() => void sendMessage("Identify the key themes and recurring ideas across the sources in this notebook. Explain connections and include supporting citations.", notebook.id)} className="group rounded-xl border bg-card/65 p-5 text-left transition-colors hover:bg-card disabled:cursor-default disabled:opacity-55"><span className="mb-5 flex items-center justify-between"><Layers3 className="size-4 text-muted-foreground" /><ArrowUpRight className="size-3.5 text-muted-foreground/60 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" /></span><span className="block text-sm font-medium">Extract key themes</span><span className="mt-2 block text-xs leading-5 text-muted-foreground">Identify recurring patterns and topics across documents.</span></button>
      </div>
    </section>
  );
}
