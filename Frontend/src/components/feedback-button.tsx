"use client";

import { useState } from "react";
import { Copy, MessageSquare } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";

export function FeedbackButton() {
  const [feedback, setFeedback] = useState("");
  async function copyFeedback() {
    try {
      await navigator.clipboard.writeText(`DocuMind feedback\n\n${feedback.trim()}`);
      toast.success("Feedback copied. Share it with the project maintainer.");
    } catch {
      toast.error("Copy is unavailable. You can select and copy the feedback text instead.");
    }
  }
  return (
    <Dialog>
      <DialogTrigger asChild><button className="rounded-sm text-xs transition-colors hover:text-foreground">Send feedback</button></DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader><DialogTitle className="flex items-center gap-2"><MessageSquare className="size-4" />A little feedback goes a long way</DialogTitle><DialogDescription>Write your feedback and copy it to share with the project maintainer.</DialogDescription></DialogHeader>
        <label htmlFor="feedback" className="sr-only">Your feedback</label>
        <Textarea id="feedback" value={feedback} onChange={(event) => setFeedback(event.target.value)} placeholder="What worked well? What could be better?" className="min-h-36" maxLength={4000} />
        <DialogFooter><Button onClick={() => void copyFeedback()} disabled={!feedback.trim()}><Copy />Copy feedback</Button></DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
