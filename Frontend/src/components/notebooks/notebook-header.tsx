"use client";

import { Check, HardDrive, Menu, MoreHorizontal, PanelLeftOpen, PencilLine, Share2, Trash2 } from "lucide-react";
import { useNotebook } from "@/components/notebooks/notebook-provider";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { ThemeMenu } from "@/components/theme-menu";
import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { SheetTrigger } from "@/components/ui/sheet";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

export function NotebookHeader() {
  const { state: { notebook, sidebarCollapsed }, actions } = useNotebook();
  const storageError = useWorkspace((state) => state.storageError);
  return (
    <header className="flex h-[76px] shrink-0 items-center justify-between gap-2 border-b bg-card/45 px-4 sm:gap-4 sm:px-7">
      <div className="flex min-w-0 items-center gap-2.5">
        <SheetTrigger asChild><Button variant="ghost" size="icon" className="shrink-0 lg:hidden" data-dialog-return-focus aria-label="Open notebook sidebar"><Menu /></Button></SheetTrigger>
        {sidebarCollapsed ? <Button variant="ghost" size="icon" className="hidden shrink-0 lg:inline-flex" aria-label="Expand sidebar" onClick={() => actions.setSidebarCollapsed(false)}><PanelLeftOpen /></Button> : null}
        <h1 className="truncate text-sm font-medium" title={notebook.title}><span className="mr-1.5 hidden font-normal text-muted-foreground md:inline">Project:</span>{notebook.title}</h1>
      </div>
      <div className="flex shrink-0 items-center gap-1.5 sm:gap-3">
        <Tooltip><TooltipTrigger asChild><span tabIndex={0} className="hidden items-center gap-1.5 rounded-sm text-[10px] text-muted-foreground md:flex">{storageError ? <HardDrive className="size-3" /> : <Check className="size-3" />}{storageError ? "Not saved" : "Auto-saved"}</span></TooltipTrigger><TooltipContent>{storageError ? "Browser storage is unavailable." : "Notebook, notes, and conversation saved in this browser."}</TooltipContent></Tooltip>
        <div className="hidden sm:block"><ThemeMenu /></div>
        <Button variant="outline" size="sm" onClick={() => actions.openPanel({ kind: "share" })} className="h-9 gap-2 bg-card px-3 text-xs"><Share2 className="size-3.5" /><span className="hidden sm:inline">Share</span><span className="sr-only sm:hidden">Share notebook</span></Button>
        <DropdownMenu><DropdownMenuTrigger asChild><Button variant="ghost" size="icon-sm" aria-label="Notebook actions" className="text-muted-foreground"><MoreHorizontal /></Button></DropdownMenuTrigger><DropdownMenuContent align="end" className="w-48"><DropdownMenuItem onSelect={() => actions.openPanel({ kind: "rename" })} className="py-2"><PencilLine />Rename notebook</DropdownMenuItem><DropdownMenuItem onSelect={() => actions.openPanel({ kind: "clear-chat" })} className="py-2"><Trash2 />Clear conversation</DropdownMenuItem><DropdownMenuSeparator /><DropdownMenuItem variant="destructive" onSelect={() => actions.openPanel({ kind: "delete" })} className="py-2"><Trash2 />Delete notebook</DropdownMenuItem></DropdownMenuContent></DropdownMenu>
      </div>
    </header>
  );
}
