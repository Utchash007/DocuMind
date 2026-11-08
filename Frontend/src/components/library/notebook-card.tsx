"use client";

import Link from "next/link";
import { ArrowUpRight, BookOpenText, FileText, MoreHorizontal, PencilLine, Trash2 } from "lucide-react";
import type { Notebook } from "@/lib/types";
import { editedLabel, notebookHref } from "@/lib/notebooks";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";

export function NotebookCard({ notebook, onRename, onDelete }: { notebook: Notebook; onRename: () => void; onDelete: () => void }) {
  const count = notebook.sourceFilenames.length;
  return (
    <Card className="group relative min-h-60 gap-0 rounded-2xl p-6 shadow-xs transition-[box-shadow,transform] duration-200 hover:-translate-y-0.5 hover:shadow-md">
      <div className="mb-6 flex items-start justify-between">
        <span className="flex size-11 items-center justify-center rounded-xl border border-border/60 bg-secondary/70 text-foreground/75"><BookOpenText className="size-5" strokeWidth={1.6} /></span>
        <DropdownMenu>
          <DropdownMenuTrigger asChild><Button variant="ghost" size="icon" aria-label={`Notebook options for ${notebook.title}`} className="relative z-10 -mt-1 -mr-2 text-muted-foreground"><MoreHorizontal /></Button></DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-44"><DropdownMenuItem onSelect={onRename} className="py-2"><PencilLine />Rename</DropdownMenuItem><DropdownMenuSeparator /><DropdownMenuItem variant="destructive" onSelect={onDelete} className="py-2"><Trash2 />Delete notebook</DropdownMenuItem></DropdownMenuContent>
        </DropdownMenu>
      </div>
      <h2 className="line-clamp-2 text-[18px] leading-6 font-semibold tracking-tight"><Link href={notebookHref(notebook.id)} aria-label={`Open notebook ${notebook.title}`} className="outline-none after:absolute after:inset-0 after:rounded-2xl focus-visible:after:ring-2 focus-visible:after:ring-ring focus-visible:after:ring-offset-4">{notebook.title}</Link></h2>
      <p className="mt-2.5 flex items-center gap-1.5 text-xs text-muted-foreground"><FileText className="size-3.5" />{count} {count === 1 ? "source" : "sources"}</p>
      <div className="mt-auto flex items-center justify-between gap-3 pt-7"><p className="text-[10px] font-medium tracking-[0.08em] text-muted-foreground uppercase">{editedLabel(notebook.updatedAt)}</p><ArrowUpRight className="size-4 text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" /></div>
    </Card>
  );
}
