"use client";

import dynamic from "next/dynamic";
import { Bookmark, BookmarkCheck, Copy, Sparkles } from "lucide-react";
import { toast } from "sonner";
import type { Message } from "@/lib/api-types";
import { Citations } from "@/components/chat/citations";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

const Markdown = dynamic(() => import("@/components/chat/markdown"), { loading: () => <Skeleton className="h-20 w-full" /> });

export function ChatMessage({ message, projectId }: { message: Message; projectId: string }) {
  if (message.role === "user") {
    const failed = message.generationStatus === "failed" || message.generationStatus === "cancelled";
    return (
      <article aria-label="Your question" className="message-item flex justify-end">
        <div className="max-w-[88%] rounded-2xl rounded-tr-md border border-border/40 bg-secondary/75 px-5 py-3.5 text-sm leading-7 break-words whitespace-pre-wrap sm:max-w-[78%]">
          {message.content}
          {message.generationStatus === "pending" || message.generationStatus === "generating" ? (
            <p className="mt-2 text-[10px] text-muted-foreground">Sending…</p>
          ) : null}
          {failed ? (
            <p className="mt-2 text-[10px] font-medium text-destructive">{message.generationStatus === "cancelled" ? "Cancelled — submit a new question to continue." : "Not answered yet"}</p>
          ) : null}
        </div>
      </article>
    );
  }
  if (message.role === "system") {
    return <article aria-label="System note" className="message-item text-xs text-muted-foreground">{message.content}</article>;
  }
  return <AssistantMessage message={message} projectId={projectId} />;
}

function AssistantMessage({ message, projectId }: { message: Message; projectId: string }) {
  const saved = useWorkspace((state) => state.notes.some((note) => note.id === `${projectId}:${message.id}`));
  const toggleNoteFromMessage = useWorkspace((state) => state.toggleNoteFromMessage);
  async function copy() {
    try { await navigator.clipboard.writeText(message.content); toast.success("Answer copied."); }
    catch { toast.error("Copy is unavailable. Select the answer text to copy it."); }
  }
  return (
    <article aria-label="NoteMind response" className="message-item flex gap-3 sm:gap-4">
      <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-lg border bg-card"><Sparkles className="size-3.5" strokeWidth={1.6} /></span>
      <div className="min-w-0 flex-1">
        <p className="mb-3 flex items-center gap-2 text-xs font-semibold">NoteMind<span className="text-[10px] font-normal text-muted-foreground">Grounded in your sources</span></p>
        <Markdown text={message.content} />
        {message.citations?.length ? <div className="mt-4"><Citations citations={message.citations} projectId={projectId} /></div> : null}
        <div className="mt-3 flex items-center gap-1">
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="icon-sm" onClick={() => void copy()} aria-label="Copy answer" className="text-muted-foreground"><Copy className="size-3.5" /></Button></TooltipTrigger><TooltipContent>Copy answer</TooltipContent></Tooltip>
          <Button
            variant="ghost" size="sm"
            onClick={() => toast.success(toggleNoteFromMessage(message, projectId) ? "Answer saved to notes." : "Answer removed from notes.")}
            className="gap-1.5 text-[10px] font-normal text-muted-foreground"
          >
            {saved ? <BookmarkCheck className="size-3.5" /> : <Bookmark className="size-3.5" />}{saved ? "Saved to notes" : "Save to notes"}
          </Button>
        </div>
      </div>
    </article>
  );
}
