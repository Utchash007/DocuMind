# Step 3 — App Shell: Route Groups + Sidebar

Goal: replace the single-page layout with real routes wrapped in a persistent shell containing the redesigned sidebar (per `Wirframes/sidebar.md` / `sidebar.html`).

## 3.1 Root layout — `src/app/layout.tsx` (full file)

```tsx
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DocuMind",
  description: "AI-powered document question answering with page-level citations",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
```

## 3.2 Main group layout — `src/app/(main)/layout.tsx` (full file)

```tsx
import { Sidebar } from "@/components/layout/Sidebar";

export default function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen">
      <Sidebar />
      <main className="my-6 ml-[312px] mr-6">{children}</main>
    </div>
  );
}
```

(`312px` = 24px sidebar left offset + 264px sidebar width + 24px gutter.)

## 3.3 Sidebar — `src/components/layout/Sidebar.tsx` (full file)

```tsx
"use client";

import { usePathname } from "next/navigation";
import { ChatIcon, FileIcon, GearIcon, GridIcon, HelpIcon, NoteIcon, SparkleIcon } from "@/components/icons";
import { NavSection, type NavItemDef } from "./NavSection";
import { ProfileControl } from "./ProfileControl";

const NAV_SECTIONS: NavItemDef[][] = [
  [
    { label: "Dashboard", href: "/", icon: GridIcon },
    { label: "Documents", href: "/documents", icon: FileIcon },
    { label: "Chats", href: "/chats", icon: ChatIcon },
  ],
  [
    { label: "Notes", href: "/notes", icon: NoteIcon },
    { label: "Settings", href: "/settings", icon: GearIcon },
    { label: "Help", href: "/help", icon: HelpIcon },
  ],
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed top-6 bottom-6 left-6 z-10 flex w-[264px] flex-col rounded-card border border-line bg-white p-[14px] pt-5 shadow-panel">
      <div className="flex items-center gap-3 px-2 pb-1">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-chip bg-gradient-to-br from-slate to-navy shadow-[0_4px_10px_-3px_rgb(33_42_62/0.5)]">
          <SparkleIcon className="h-5 w-5 text-white" />
        </div>
        <span className="text-[1.15rem] font-bold tracking-tight text-navy">DocuMind</span>
      </div>

      <div className="mx-2.5 my-3.5 h-px bg-line" />

      <nav aria-label="Main navigation" className="flex flex-col gap-4">
        {NAV_SECTIONS.map((items) => (
          <NavSection key={items[0].href} items={items} pathname={pathname} />
        ))}
      </nav>

      <ProfileControl />
    </aside>
  );
}
```

## 3.4 NavSection — `src/components/layout/NavSection.tsx` (full file)

```tsx
import Link from "next/link";
import type { ComponentType } from "react";

export interface NavItemDef {
  label: string;
  href: string;
  icon: ComponentType<{ className?: string }>;
}

export function NavSection({ items, pathname }: { items: NavItemDef[]; pathname: string }) {
  return (
    <div className="flex flex-col gap-1">
      {items.map((item) => (
        <NavItem key={item.href} item={item} isActive={pathname === item.href} />
      ))}
    </div>
  );
}

function NavItem({ item, isActive }: { item: NavItemDef; isActive: boolean }) {
  const Icon = item.icon;
  return (
    <Link
      href={item.href}
      aria-current={isActive ? "page" : undefined}
      className={`relative flex items-center gap-3 rounded-control px-3.5 py-2.5 text-[0.925rem] transition-colors duration-200 focus-visible:ring-2 focus-visible:ring-slate focus-visible:outline-none ${
        isActive
          ? "bg-active font-semibold text-navy"
          : "font-medium text-muted hover:bg-hover hover:text-navy"
      }`}
    >
      {isActive && (
        <span className="absolute top-1/2 left-0 h-[22px] w-[3px] -translate-y-1/2 rounded-full bg-slate" />
      )}
      <Icon className="h-[18px] w-[18px] shrink-0" />
      {item.label}
    </Link>
  );
}
```

## 3.5 ProfileControl — `src/components/layout/ProfileControl.tsx` (full file)

```tsx
import { GearIcon } from "@/components/icons";

export function ProfileControl() {
  return (
    <div className="mt-auto px-1.5">
      <div className="mb-3.5 h-px bg-line" />
      <div className="flex h-10 w-10 items-center justify-center rounded-full border border-line bg-active text-[0.85rem] font-bold tracking-wide text-slate">
        UH
      </div>
      <div className="mt-2.5 flex items-center justify-between gap-2.5 pb-0.5">
        <span className="text-[0.9rem] font-semibold text-navy">Utchash</span>
        <button
          type="button"
          aria-label="User settings"
          className="flex h-[30px] w-[30px] items-center justify-center rounded-chip text-muted transition-colors duration-200 hover:bg-hover hover:text-navy"
        >
          <GearIcon className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
```

## 3.6 Placeholder pages (full files)

`src/app/(main)/page.tsx` — temporary dashboard stub (rebuilt in Step 4):

```tsx
export default function DashboardPage() {
  return <h1 className="text-xl font-bold text-navy">Dashboard</h1>;
}
```

`src/app/(main)/documents/page.tsx`:

```tsx
export default function DocumentsPage() {
  return <h1 className="text-xl font-bold text-navy">Documents</h1>;
}
```

`src/app/(main)/notes/page.tsx`:

```tsx
export default function NotesPage() {
  return <h1 className="text-xl font-bold text-navy">Notes</h1>;
}
```

`src/app/(main)/settings/page.tsx`:

```tsx
export default function SettingsPage() {
  return <h1 className="text-xl font-bold text-navy">Settings</h1>;
}
```

`src/app/(main)/help/page.tsx`:

```tsx
export default function HelpPage() {
  return <h1 className="text-xl font-bold text-navy">Help</h1>;
}
```

`src/app/chats/page.tsx` — chat lives **outside** `(main)` (fullscreen, no sidebar; built in Step 5):

```tsx
export default function ChatsPage() {
  return <h1 className="text-xl font-bold text-navy">Chats</h1>;
}
```

## 3.7 Delete the old monolith

- Delete `src/app/page.tsx` — the `(main)` route group now serves `/`.
- Keep the old file's logic in mind: upload, file list, and query flows are rebuilt across Steps 4–6.

## Acceptance criteria

- [ ] `/` renders sidebar + stub dashboard; `/documents`, `/notes`, `/settings`, `/help` navigate with the accent bar following the active route
- [ ] Sidebar visually matches `Wirframes/sidebar.html` (brand tile, dividers, bottom-pinned profile)
- [ ] `Sidebar` is the only `"use client"` component added in this step
- [ ] Old `src/app/page.tsx` is deleted
