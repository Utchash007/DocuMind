"use client";

import { useState } from "react";
import { ArrowUpRight, FileText, Quote } from "lucide-react";
import type { Citation } from "@/lib/api-types";
import { documentFileUrl } from "@/services/projects/documents";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

export function Citations({ citations, projectId }: { citations: Citation[]; projectId?: string }) {
  const [active, setActive] = useState<Citation | null>(null);
  return (
    <>
      <div className="flex flex-wrap items-center gap-2" aria-label="Supporting citations">
        {citations.map((citation, index) => (
          <Tooltip key={`${citation.fileName}-${citation.pageNumber}-${index}`}>
            <TooltipTrigger asChild>
              <Button
                variant="outline" size="sm"
                aria-label={`View citation from ${citation.fileName}, page ${citation.pageNumber}`}
                onClick={() => setActive(citation)}
                className="h-7 gap-1.5 rounded-lg bg-card/80 px-2.5 text-[10px] font-normal text-muted-foreground"
              >
                <FileText className="size-3" />
                Page {citation.pageNumber}
              </Button>
            </TooltipTrigger>
            <TooltipContent>{citation.fileName}</TooltipContent>
          </Tooltip>
        ))}
      </div>
      <Dialog open={active !== null} onOpenChange={(open) => { if (!open) setActive(null); }}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2"><Quote className="size-4 text-muted-foreground" />Source passage</DialogTitle>
            <DialogDescription className="break-all">
              {active?.fileName ?? "Supporting source"} · Page {active?.pageNumber ?? "?"}
            </DialogDescription>
          </DialogHeader>
          <blockquote className="max-h-[50dvh] overflow-y-auto rounded-xl border bg-background/65 p-5 text-sm leading-7">{active?.text}</blockquote>
          <DialogFooter>
            {active && projectId ? (
              <Button asChild><a href={documentFileUrl(projectId, active.documentId, active.pageNumber)} target="_blank" rel="noopener noreferrer">Open PDF at page {active.pageNumber}<ArrowUpRight /></a></Button>
            ) : (
              <Button variant="outline" onClick={() => setActive(null)}>Close passage</Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
