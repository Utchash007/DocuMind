"use client";

import Link from "next/link";
import { ArrowUpRight, BookOpenText, MoreHorizontal, PencilLine, Trash2 } from "lucide-react";
import type { Project } from "@/lib/api-types";
import { editedLabel, projectHref } from "@/lib/projects";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";

export function ProjectCard({ project, onRename, onDelete }: { project: Project; onRename: () => void; onDelete: () => void }) {
  return (
    <Card className="group relative min-h-60 gap-0 rounded-2xl p-6 shadow-xs transition-[box-shadow,transform] duration-200 hover:-translate-y-0.5 hover:shadow-md">
      <div className="mb-6 flex items-start justify-between">
        <span className="flex size-11 items-center justify-center rounded-xl border border-border/60 bg-secondary/70 text-foreground/75"><BookOpenText className="size-5" strokeWidth={1.6} /></span>
        <DropdownMenu>
          <DropdownMenuTrigger asChild><Button variant="ghost" size="icon" aria-label={`Project options for ${project.name}`} className="relative z-10 -mt-1 -mr-2 text-muted-foreground"><MoreHorizontal /></Button></DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-44">
            <DropdownMenuItem onSelect={onRename} className="py-2"><PencilLine />Rename</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem variant="destructive" onSelect={onDelete} className="py-2"><Trash2 />Delete project</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      <h2 className="line-clamp-2 text-[18px] leading-6 font-semibold tracking-tight">
        <Link href={projectHref(project.id)} aria-label={`Open project ${project.name}`} className="outline-none after:absolute after:inset-0 after:rounded-2xl focus-visible:after:ring-2 focus-visible:after:ring-ring focus-visible:after:ring-offset-4">{project.name}</Link>
      </h2>
      <p className="mt-2.5 line-clamp-2 text-xs leading-5 text-muted-foreground">{project.description || "Open to add sources and start a conversation."}</p>
      <div className="mt-auto flex items-center justify-between gap-3 pt-7">
        <p className="text-[10px] font-medium tracking-[0.08em] text-muted-foreground uppercase">{editedLabel(project.updatedAt)}</p>
        <ArrowUpRight className="size-4 text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
      </div>
    </Card>
  );
}
