"use client";

import dynamic from "next/dynamic";
import { Bookmark, BookmarkCheck, Copy, Sparkles } from "lucide-react";
import { toast } from "sonner";
import type { ChatMessage as Message } from "@/lib/types";
import { notebookScope } from "@/lib/notebooks";
import { Citations } from "@/components/chat/citations";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

const Markdown = dynamic(() => import("@/components/chat/markdown"), { loading: () => <Skeleton className="h-20 w-full" /> });

export function ChatMessage({ message, notebookId }: { message: Message; notebookId: string }) {
  if (message.role === "user") return <article aria-label="Your question" className="message-item flex justify-end"><div className="max-w-[88%] rounded-2xl rounded-tr-md border border-border/40 bg-secondary/75 px-5 py-3.5 text-sm leading-7 break-words whitespace-pre-wrap sm:max-w-[78%]">{message.text}</div></article>;
  return <AssistantMessage message={message} notebookId={notebookId} />;
}

function AssistantMessage({ message, notebookId }: { message: Message; notebookId: string }) {
  const saved = useWorkspace((state) => !!state.notesMap[`${notebookScope(notebookId)}:${message.id}`]);
  const toggleSavedNote = useWorkspace((state) => state.toggleSavedNote);
  async function copy() {
    try { await navigator.clipboard.writeText(message.text); toast.success("Answer copied."); }
    catch { toast.error("Copy is unavailable. Select the answer text to copy it."); }
  }
  return (
    <article aria-label="NoteMind response" className="message-item flex gap-3 sm:gap-4">
      <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-lg border bg-card"><Sparkles className="size-3.5" strokeWidth={1.6} /></span>
      <div className="min-w-0 flex-1">
        <p className="mb-3 flex items-center gap-2 text-xs font-semibold">NoteMind<span className="text-[10px] font-normal text-muted-foreground">Grounded in your sources</span></p>
        <Markdown text={message.text} />
        {message.citations?.length ? <div className="mt-4"><Citations citations={message.citations} fallbackFilename={message.sourceFilenames?.length === 1 ? message.sourceFilenames[0] : undefined} /></div> : null}
        <div className="mt-3 flex items-center gap-1">
          <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="icon-sm" onClick={() => void copy()} aria-label="Copy answer" className="text-muted-foreground"><Copy className="size-3.5" /></Button></TooltipTrigger><TooltipContent>Copy answer</TooltipContent></Tooltip>
          <Button variant="ghost" size="sm" onClick={() => toast.success(toggleSavedNote(message, notebookId) ? "Answer saved to notes." : "Answer removed from notes.")} className="gap-1.5 text-[10px] font-normal text-muted-foreground">{saved ? <BookmarkCheck className="size-3.5" /> : <Bookmark className="size-3.5" />}{saved ? "Saved to notes" : "Save to notes"}</Button>
        </div>
      </div>
    </article>
  );
}
