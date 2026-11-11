"use client";

import Link from "next/link";
import { useDeferredValue, useEffect, useRef, useState } from "react";
import { ArrowRight, BookOpenText, CircleHelp, FileUp, HardDrive, Plus, Search, Sparkles, X } from "lucide-react";
import { Brand } from "@/components/brand";
import { AccountMenu } from "@/components/account-menu";
import { ProjectCard } from "@/components/projects/project-card";
import { CreateProjectDialog, DeleteProjectDialog, RenameProjectDialog } from "@/components/projects/project-dialogs";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { ThemeMenu } from "@/components/theme-menu";
import { WorkspaceNotices } from "@/components/workspace-notices";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { projectScope } from "@/lib/projects";
import type { Project } from "@/lib/api-types";

type LibraryDialog = { kind: "create" } | { kind: "rename" | "delete"; project: Project } | null;

export function ProjectLibrary() {
  const identity = useWorkspace((state) => state.identity);
  const page = useWorkspace((state) => (identity ? state.projectsByUser[projectScope(identity, "list")] : undefined));
  const loadProjects = useWorkspace((state) => state.loadProjects);
  const refreshProjects = useWorkspace((state) => state.refreshProjects);
  const nextCursor = page?.nextCursor;
  const status = page?.status ?? "idle";
  const projects = page?.items ?? [];
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("recent");
  const [dialog, setDialog] = useState<LibraryDialog>(null);
  const deferredSearch = useDeferredValue(search).trim().toLowerCase();
  const searchRef = useRef<HTMLInputElement>(null);
  const filtered = projects.filter((project) => project.name.toLowerCase().includes(deferredSearch)).toSorted((a, b) =>
    sort === "name" ? a.name.localeCompare(b.name) : Date.parse(b[sort === "created" ? "createdAt" : "updatedAt"]) - Date.parse(a[sort === "created" ? "createdAt" : "updatedAt"]),
  );

  useEffect(() => { if (identity) void loadProjects({ reset: true }); }, [identity, loadProjects]);

  useEffect(() => {
    function focusSearch(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        searchRef.current?.focus();
      }
    }
    document.addEventListener("keydown", focusSearch);
    return () => document.removeEventListener("keydown", focusSearch);
  }, []);

  const loading = status === "loading" || status === "idle";

  return (
    <>
      <header className="border-b bg-card/65">
        <div className="mx-auto grid w-full max-w-[1440px] grid-cols-[1fr_auto] items-center gap-4 px-6 py-4 sm:grid-cols-[1fr_minmax(180px,380px)_1fr] sm:gap-8 sm:px-8 lg:px-10">
          <Brand />
          <div className="relative order-3 col-span-2 sm:order-2 sm:col-span-1">
            <label htmlFor="project-search" className="sr-only">Search projects</label>
            <Search className="pointer-events-none absolute top-1/2 left-3.5 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input ref={searchRef} id="project-search" type="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search projects..." className="h-10 border-border/70 bg-background/60 pr-12 pl-10 shadow-none [&::-webkit-search-cancel-button]:hidden" />
            {search ? <Button variant="ghost" size="icon-sm" onClick={() => { setSearch(""); searchRef.current?.focus(); }} aria-label="Clear search" className="absolute top-1/2 right-1.5 -translate-y-1/2"><X /></Button> : <kbd aria-hidden="true" className="pointer-events-none absolute top-1/2 right-3 hidden -translate-y-1/2 rounded border px-1.5 py-0.5 text-[10px] text-muted-foreground lg:block">⌘ K</kbd>}
          </div>
          <div className="order-2 flex items-center justify-end gap-1.5 sm:order-3">
            <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="icon" asChild className="size-9 text-muted-foreground"><Link href="/help" aria-label="Help and getting started"><CircleHelp /></Link></Button></TooltipTrigger><TooltipContent>Help & getting started</TooltipContent></Tooltip>
            <ThemeMenu />
            <span aria-hidden="true" className="mx-1 hidden h-5 w-px bg-border sm:block" />
            <AccountMenu />
          </div>
        </div>
      </header>
      <main id="main-content" className="mx-auto w-full max-w-6xl flex-1 px-6 pt-10 pb-16 sm:pt-16 lg:px-10">
        <div className="mb-9 flex flex-col justify-between gap-6 sm:flex-row sm:items-center">
          <div><p className="mb-3 text-[10px] font-semibold tracking-[0.18em] text-muted-foreground uppercase">Your personal research space</p><h1 className="text-3xl font-semibold tracking-[-0.045em] sm:text-[38px]">Your Projects</h1><p className="mt-3 text-sm leading-6 text-muted-foreground">Select a project to start chatting with your sources.</p></div>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => setDialog({ kind: "create" })} disabled={!identity} className="h-11 w-fit gap-2 rounded-xl px-5 shadow-xs"><Plus className="size-4" />New Project</Button>
          </div>
        </div>
        <WorkspaceNotices />
        <div className="mt-7 mb-5 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3 text-xs text-muted-foreground">
            <span>{loading ? "Loading projects..." : `${projects.length} ${projects.length === 1 ? "project" : "projects"}`}</span>
            <span aria-hidden="true" className="size-0.5 rounded-full bg-muted-foreground/60" />
            <Tooltip><TooltipTrigger asChild><span tabIndex={0} className="flex items-center gap-1.5 rounded-sm"><HardDrive className="size-3" />Your account</span></TooltipTrigger><TooltipContent>Projects and conversations are saved on the server. Notes and drafts stay on this device for your account.</TooltipContent></Tooltip>
          </div>
          <Select value={sort} onValueChange={setSort}><SelectTrigger aria-label="Sort projects" size="sm" className="border-transparent bg-transparent text-xs text-muted-foreground shadow-none"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="recent">Recently edited</SelectItem><SelectItem value="created">Recently created</SelectItem><SelectItem value="name">Name A–Z</SelectItem></SelectContent></Select>
        </div>
        {page?.status === "error" ? (
          <div role="alert" className="rounded-2xl border border-destructive/20 bg-card p-8 text-center">
            <p className="font-medium">Projects could not be loaded</p>
            <p className="mt-2 text-sm text-muted-foreground">{page.error}</p>
            <Button variant="outline" className="mt-5" onClick={() => void refreshProjects()}>Try again</Button>
          </div>
        ) : loading ? (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3" aria-label="Loading projects">{[0, 1, 2].map((id) => <Skeleton key={id} className="h-60 rounded-2xl" />)}</div>
        ) : (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {!deferredSearch ? <button onClick={() => setDialog({ kind: "create" })} className="group flex min-h-60 flex-col items-center justify-center rounded-2xl border border-dashed border-foreground/20 bg-card/25 p-6 text-center transition-colors hover:border-foreground/40 hover:bg-card/70"><span className="mb-5 flex size-12 items-center justify-center rounded-full border bg-card shadow-xs transition-transform group-hover:scale-105"><Plus className="size-5 text-foreground/70" strokeWidth={1.5} /></span><h2 className="font-medium">Create Project</h2><p className="mt-2 text-xs text-muted-foreground">Upload sources to begin</p></button> : null}
            {filtered.map((project) => <ProjectCard key={project.id} project={project} onRename={() => setDialog({ kind: "rename", project })} onDelete={() => setDialog({ kind: "delete", project })} />)}
            {!projects.length && !deferredSearch ? <GettingStartedCard /> : null}
          </div>
        )}
        {nextCursor && !loading ? <div className="mt-8 text-center"><Button variant="outline" onClick={() => void loadProjects({ cursor: nextCursor })}>Load more projects</Button></div> : null}
        {!loading && deferredSearch && !filtered.length ? <div className="rounded-2xl border border-dashed py-16 text-center"><Search className="mx-auto mb-4 size-7 text-muted-foreground" /><h2 className="font-medium">No projects found</h2><p className="mt-2 px-4 text-sm text-muted-foreground">Try another name, or create a project for your next idea.</p><Button variant="outline" onClick={() => setSearch("")} className="mt-5">Clear search</Button></div> : null}
      </main>
      {dialog?.kind === "create" ? <CreateProjectDialog onClose={() => setDialog(null)} /> : null}
      {dialog?.kind === "rename" ? <RenameProjectDialog project={dialog.project} onClose={() => setDialog(null)} /> : null}
      {dialog?.kind === "delete" ? <DeleteProjectDialog project={dialog.project} onClose={() => setDialog(null)} /> : null}
    </>
  );
}

function GettingStartedCard() {
  return (
    <Card className="justify-center rounded-2xl bg-card/40 p-7 shadow-none ring-border/70 lg:col-span-2">
      <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground"><Sparkles className="size-3.5" />A clearer way to think</div>
      <h2 className="mt-1 text-xl font-medium tracking-tight">Big ideas start with a few good sources.</h2>
      <p className="max-w-md text-sm leading-6 text-muted-foreground">Gather your PDFs in a project. Ask questions, connect the dots, and turn useful answers into lasting notes.</p>
      <div className="mt-2 flex flex-wrap items-center gap-3 text-[11px] text-muted-foreground"><span className="flex items-center gap-1.5"><FileUp className="size-3.5" />Add sources</span><ArrowRight className="size-3" /><span className="flex items-center gap-1.5"><Sparkles className="size-3.5" />Find insight</span><ArrowRight className="size-3" /><span className="flex items-center gap-1.5"><BookOpenText className="size-3.5" />Keep what matters</span></div>
    </Card>
  );
}
