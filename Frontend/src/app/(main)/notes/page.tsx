"use client";

import Link from "next/link";
import { Bookmark, Plus } from "lucide-react";
import { Brand } from "@/components/brand";
import { AccountMenu } from "@/components/account-menu";
import { projectHref } from "@/lib/projects";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { ThemeMenu } from "@/components/theme-menu";
import { WorkspaceNotices } from "@/components/workspace-notices";

export default function NotesPage() {
  const notes = useWorkspace((state) => state.notes);
  return (
    <div className="flex min-h-dvh flex-col">
      <header className="border-b bg-card/65">
        <div className="mx-auto flex w-full max-w-[1440px] items-center justify-between gap-4 px-6 py-4 sm:px-8 lg:px-10">
          <Brand />
          <div className="flex items-center gap-1.5">
            <ThemeMenu />
            <AccountMenu />
          </div>
        </div>
      </header>
      <main id="main-content" className="mx-auto w-full max-w-4xl flex-1 px-6 pt-10 pb-16 sm:pt-14">
        <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="mb-3 text-[10px] font-semibold tracking-[0.18em] text-muted-foreground uppercase">On this device · your account only</p>
            <h1 className="text-3xl font-semibold tracking-[-0.045em]">Saved notes</h1>
            <p className="mt-3 text-sm leading-6 text-muted-foreground">Editable notes are local to this browser and account — never part of server history. They export with your projects.</p>
          </div>
        </div>
        <WorkspaceNotices />
        {notes.length ? (
          <ul className="mt-7 space-y-3">
            {notes.toSorted((a, b) => Date.parse(b.updatedAt) - Date.parse(a.updatedAt)).map((note) => (
              <li key={note.id}>
                <Link href={projectHref(note.projectId)} className="flex items-start gap-3 rounded-2xl border bg-card/65 p-5 transition-colors hover:bg-card">
                  <Bookmark className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
                  <span className="min-w-0">
                    <span className="block text-sm font-medium">{note.title}</span>
                    <span className="mt-1 line-clamp-2 block text-xs leading-5 text-muted-foreground">{note.text}</span>
                    <span className="mt-2 block text-[10px] text-muted-foreground">Open project to edit this note</span>
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <div className="mt-7 rounded-2xl border border-dashed px-5 py-16 text-center">
            <Plus className="mx-auto mb-4 size-7 text-muted-foreground" />
            <p className="font-medium">No notes yet</p>
            <p className="mt-2 text-sm text-muted-foreground">Open a project and save an answer, or add a note from the sidebar.</p>
          </div>
        )}
      </main>
    </div>
  );
}
