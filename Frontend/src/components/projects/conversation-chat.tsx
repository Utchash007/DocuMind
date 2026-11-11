"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowUpRight, FileText, FileUp, Layers3, Loader2, RotateCcw, Sparkles, Square } from "lucide-react";
import type { Message } from "@/lib/api-types";
import { BrandMark } from "@/components/brand";
import { ChatComposer } from "@/components/chat/chat-composer";
import { ChatMessage } from "@/components/chat/chat-message";
import { useProject } from "@/components/projects/project-provider";
import { conversationScope, projectScope } from "@/lib/projects";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { WorkspaceNotices } from "@/components/workspace-notices";
import { Button } from "@/components/ui/button";

const emptyMessages: Message[] = [];

export function ConversationChat({ readyDocumentCount }: { readyDocumentCount: number }) {
  const { state: { project, conversationId }, actions } = useProject();
  const identity = useWorkspace((state) => state.identity);
  const activeId = conversationId ?? "";
  const messages = useWorkspace((state) => (identity && activeId ? state.messagesByScope[conversationScope(identity, project.id, activeId)]?.items ?? emptyMessages : emptyMessages));
  const nextCursor = useWorkspace((state) => (identity && activeId ? state.messagesByScope[conversationScope(identity, project.id, activeId)]?.nextCursor ?? null : null));
  const messagesStatus = useWorkspace((state) => (identity && activeId ? state.messagesByScope[conversationScope(identity, project.id, activeId)]?.status ?? "idle" : "idle"));
  const pending = useWorkspace((state) => (identity && activeId ? state.pendingByScope[conversationScope(identity, project.id, activeId)] ?? false : false));
  const error = useWorkspace((state) => (identity && activeId ? state.errorsByScope[conversationScope(identity, project.id, activeId)] : undefined));
  const latestTurn = messages.findLast((message) => message.role === "user");
  const deadline = latestTurn?.generationStatus === "pending" || latestTurn?.generationStatus === "generating" ? latestTurn.generationExpiresAt : null;
  const [expiredDeadline, setExpiredDeadline] = useState<string | null>(null);
  useEffect(() => {
    if (!deadline) return;
    const expiresAt = Date.parse(deadline);
    if (!Number.isFinite(expiresAt)) return;
    function checkExpiry() {
      const remaining = expiresAt - Date.now();
      if (remaining > 0) timer = setTimeout(checkExpiry, Math.min(remaining, 2_147_483_647));
      else setExpiredDeadline(deadline);
    }
    let timer = setTimeout(checkExpiry, 0);
    return () => clearTimeout(timer);
  }, [deadline]);
  const retryable = latestTurn?.generationStatus !== "cancelled" && error?.code !== "cancelled" && error?.code !== "turn_finished" && (
    latestTurn?.generationStatus === "failed" || latestTurn?.id.startsWith("optimistic:") ||
    !!(deadline && deadline === expiredDeadline)
  );
  const retryMessage = useWorkspace((state) => state.retryMessage);
  const cancelTurn = useWorkspace((state) => state.cancelTurn);
  const loadMessages = useWorkspace((state) => state.loadMessages);
  const loadOlderMessages = useWorkspace((state) => state.loadOlderMessages);
  const scrollRef = useRef<HTMLDivElement>(null);
  const following = useRef(true);
  const anchorRef = useRef<number | null>(null);

  useEffect(() => {
    if (identity && activeId) void loadMessages(project.id, activeId);
  }, [identity, activeId, project.id, loadMessages]);

  useEffect(() => {
    const container = scrollRef.current;
    if (!container) return;
    // Preserve scroll when prepending history: restore distance from top.
    if (anchorRef.current !== null) {
      container.scrollTop = container.scrollHeight - anchorRef.current;
      anchorRef.current = null;
      return;
    }
    if (following.current || messages.at(-1)?.role === "user") {
      container.scrollTo({ top: container.scrollHeight, behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth" });
    }
  }, [messages, pending]);

  async function loadOlder() {
    const container = scrollRef.current;
    if (container) anchorRef.current = container.scrollHeight - container.scrollTop;
    try { await loadOlderMessages(project.id, activeId); }
    catch { anchorRef.current = null; }
  }

  if (!activeId) return <ProjectHome readyDocumentCount={readyDocumentCount} />;

  return (
    <>
      <div
        ref={scrollRef}
        onScroll={(event) => { const element = event.currentTarget; following.current = element.scrollHeight - element.scrollTop - element.clientHeight < 100; }}
        className="flex min-h-0 flex-1 flex-col overflow-y-auto overscroll-contain px-4 py-6 sm:px-8 sm:py-8"
      >
        <div className="mx-auto w-full max-w-[760px]"><WorkspaceNotices /></div>
        {nextCursor ? (
          <div className="mx-auto mb-4 w-full max-w-[760px] text-center">
            <Button variant="outline" size="sm" onClick={() => void loadOlder()}>Load earlier messages</Button>
          </div>
        ) : null}
        {messagesStatus === "loading" && !messages.length ? (
          <div role="status" className="mx-auto flex w-full max-w-[760px] items-center gap-3 text-sm text-muted-foreground"><Loader2 className="size-4 animate-spin" />Loading conversation…</div>
        ) : !messages.length ? (
          <EmptyChat readyDocumentCount={readyDocumentCount} onAddSources={() => actions.openPanel({ kind: "upload" })} />
        ) : (
          <div role="log" aria-label="Conversation" aria-live="polite" aria-relevant="additions" className="mx-auto flex w-full max-w-[760px] flex-col gap-8 pt-3 pb-4">
            {messages.map((message) => <ChatMessage key={message.id} message={message} projectId={project.id} />)}
          </div>
        )}
        {pending ? (
          <div role="status" className="mx-auto mt-5 mb-4 flex w-full max-w-[760px] items-center gap-3 text-xs text-muted-foreground">
            <span className="flex size-7 shrink-0 items-center justify-center rounded-lg border bg-card"><Sparkles className="size-3.5" /></span>
            <Loader2 className="size-3.5 animate-spin" />Reading your sources…
            <Button variant="outline" size="sm" className="ml-auto" onClick={() => void cancelTurn(project.id, activeId)}><Square className="size-3" />Cancel</Button>
          </div>
        ) : null}
        {(error || retryable) && !pending ? (
          <div role="alert" className="mx-auto mt-5 w-full max-w-[760px] rounded-xl border border-destructive/20 bg-card p-4">
            <p className="text-sm font-medium">We couldn’t finish that answer.</p>
            <p className="mt-1.5 text-xs leading-6 text-muted-foreground">{error?.message ?? "The latest question was interrupted. You can retry it without creating another turn."}</p>
            <div className="mt-3 flex gap-2">
              {retryable ? <Button variant="outline" size="sm" disabled={!readyDocumentCount} onClick={() => void retryMessage(project.id, activeId)}><RotateCcw className="size-3.5" />Retry question</Button> : null}
              {error?.code === "no_ready_sources" ? <Button variant="ghost" size="sm" onClick={() => actions.openPanel({ kind: "upload" })}><FileUp className="size-3.5" />Add a ready PDF</Button> : null}
            </div>
          </div>
        ) : null}
      </div>
      <ChatComposer projectId={project.id} conversationId={activeId} readyDocumentCount={readyDocumentCount} onAddSources={() => actions.openPanel({ kind: "upload" })} />
    </>
  );
}

function EmptyChat({ readyDocumentCount, onAddSources }: { readyDocumentCount: number; onAddSources: () => void }) {
  const { state: { project, conversationId } } = useProject();
  const sendMessage = useWorkspace((state) => state.sendMessage);
  const hasSources = readyDocumentCount > 0;
  function start(prompt: string) {
    if (!conversationId) return;
    void sendMessage(project.id, conversationId, prompt);
  }
  return (
    <section aria-label="Start a conversation" className="mx-auto flex w-full max-w-[680px] flex-1 flex-col justify-center py-8 sm:py-12">
      <div className="text-center">
        <BrandMark className="mb-6 size-12 rounded-2xl" />
        <h2 className="text-[27px] leading-tight font-semibold tracking-[-0.045em] sm:text-[34px]">What would you like to know?</h2>
        <p className="mt-3 text-sm leading-6 text-muted-foreground">Ask a question about your uploaded sources.</p>
        {!hasSources ? <Button onClick={onAddSources} className="mt-6 h-10 gap-2 rounded-xl px-4"><FileUp className="size-4" />Add your first PDF</Button> : <p className="mt-4 text-[10px] text-muted-foreground">A conversation grounded in {readyDocumentCount} {readyDocumentCount === 1 ? "ready source" : "ready sources"}.</p>}
      </div>
      <div className="mt-9 grid gap-3 sm:grid-cols-2 sm:gap-4">
        <button disabled={!hasSources || !conversationId} onClick={() => void start("Summarize the main ideas and key findings across the sources in this project. Include supporting citations.")} className="group rounded-xl border bg-card/65 p-5 text-left transition-colors hover:bg-card disabled:cursor-default disabled:opacity-55"><span className="mb-5 flex items-center justify-between"><FileText className="size-4 text-muted-foreground" /><ArrowUpRight className="size-3.5 text-muted-foreground/60 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" /></span><span className="block text-sm font-medium">Summarize all sources</span><span className="mt-2 block text-xs leading-5 text-muted-foreground">Get a high-level overview of everything you’ve uploaded.</span></button>
        <button disabled={!hasSources || !conversationId} onClick={() => void start("Identify the key themes and recurring ideas across the sources in this project. Explain connections and include supporting citations.")} className="group rounded-xl border bg-card/65 p-5 text-left transition-colors hover:bg-card disabled:cursor-default disabled:opacity-55"><span className="mb-5 flex items-center justify-between"><Layers3 className="size-4 text-muted-foreground" /><ArrowUpRight className="size-3.5 text-muted-foreground/60 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" /></span><span className="block text-sm font-medium">Extract key themes</span><span className="mt-2 block text-xs leading-5 text-muted-foreground">Identify recurring patterns and topics across documents.</span></button>
      </div>
      {!conversationId ? <p className="mt-4 text-center text-xs text-muted-foreground">Create a conversation from the sidebar to start asking questions.</p> : null}
    </section>
  );
}

export function ProjectHome({ readyDocumentCount }: { readyDocumentCount: number }) {
  const { state: { project }, actions } = useProject();
  const identity = useWorkspace((state) => state.identity);
  const conversationsPage = useWorkspace((state) => (identity ? state.conversationsByScope[projectScope(identity, project.id)] : undefined));
  const conversations = conversationsPage?.items ?? [];
  const documentsCount = useWorkspace((state) => (identity ? state.documentsByScope[projectScope(identity, project.id)]?.items.length ?? 0 : 0));
  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-y-auto px-4 py-8 sm:px-8">
      <div className="mx-auto w-full max-w-[860px]">
        <WorkspaceNotices />
        <section aria-label="Project overview" className="mt-2 text-center">
          <h2 className="text-2xl font-semibold tracking-tight">{project.name}</h2>
          <p className="mt-2 text-sm text-muted-foreground">{documentsCount} sources · {readyDocumentCount} ready · {conversations.length} conversations</p>
          <div className="mt-5 flex flex-wrap justify-center gap-2">
            <Button onClick={() => actions.openPanel({ kind: "conversation-create" })}><FileUp className="size-4" />New conversation</Button>
            <Button variant="outline" onClick={() => actions.openPanel({ kind: "upload" })}><PlusIcon />Add PDF</Button>
          </div>
        </section>
        {conversations.length ? (
          <ul className="mt-8 grid gap-3 sm:grid-cols-2">
            {conversations.map((conversation) => (
              <li key={conversation.id}>
                <a href={`/projects/${encodeURIComponent(project.id)}/conversations/${encodeURIComponent(conversation.id)}`} className="block rounded-xl border bg-card/65 p-5 transition-colors hover:bg-card">
                  <span className="block text-sm font-medium">{conversation.title ?? "Untitled conversation"}</span>
                  <span className="mt-2 block text-xs text-muted-foreground">Open conversation</span>
                </a>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-8 text-center text-sm text-muted-foreground">Create a conversation to start asking questions about your ready sources.</p>
        )}
      </div>
    </div>
  );
}

function PlusIcon() {
  return <span aria-hidden="true">+</span>;
}
