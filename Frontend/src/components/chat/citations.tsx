"use client";

import { useState } from "react";
import { ArrowUpRight, FileText, Quote } from "lucide-react";
import type { Citation } from "@/lib/types";
import { documentUrl } from "@/services/documents/documents";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

export function Citations({ citations, fallbackFilename }: { citations: Citation[]; fallbackFilename?: string }) {
  const [active, setActive] = useState<Citation | null>(null);
  const filename = active?.filename ?? fallbackFilename;
  return (
    <>
      <div className="flex flex-wrap items-center gap-2" aria-label="Supporting citations">
        {citations.map((citation, index) => <Tooltip key={`${citation.filename}-${citation.page}-${index}`}><TooltipTrigger asChild><Button variant="outline" size="sm" aria-label={`View citation${citation.filename ? ` from ${citation.filename}` : ""}, page ${citation.page}`} onClick={() => setActive(citation)} className="h-7 gap-1.5 rounded-lg bg-card/80 px-2.5 text-[10px] font-normal text-muted-foreground"><FileText className="size-3" />Page {citation.page}</Button></TooltipTrigger><TooltipContent>{citation.filename ?? fallbackFilename ?? "View supporting passage"}</TooltipContent></Tooltip>)}
      </div>
      <Dialog open={active !== null} onOpenChange={(open) => { if (!open) setActive(null); }}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader><DialogTitle className="flex items-center gap-2"><Quote className="size-4 text-muted-foreground" />Source passage</DialogTitle><DialogDescription className="break-all">{filename ?? "Supporting source"} · Page {active?.page}</DialogDescription></DialogHeader>
          <blockquote className="max-h-[50dvh] overflow-y-auto rounded-xl border bg-background/65 p-5 text-sm leading-7">{active?.sentence}</blockquote>
          <DialogFooter>{filename && active ? <Button asChild><a href={documentUrl(filename, active.page)} target="_blank" rel="noopener noreferrer">Open PDF at page {active.page}<ArrowUpRight /></a></Button> : <Button variant="outline" onClick={() => setActive(null)}>Close passage</Button>}</DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
