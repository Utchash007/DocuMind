# Step 4 — Dashboard Page: Cards + Documents + Upload

Goal: build the dashboard grid described below with explicit card components, plus the documents page with a working PDF upload.

## 4.1 Types — `src/lib/types.ts` (full file)

```ts
export interface DocumentInfo {
  filename: string;
}

export interface Citation {
  sentence: string;
  page: number;
}

export interface AnswerResponse {
  answer: string;
  citations: Citation[];
}

export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  text: string;
  citations?: Citation[];
}
```

## 4.2 API base — `src/services/api.ts` (full file)

```ts
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL;

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${path}`);
  }
  return res.json() as Promise<T>;
}
```

Add to `Frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## 4.3 Documents service — `src/services/documents.ts` (full file)

```ts
import { apiFetch } from "./api";
import type { DocumentInfo } from "@/lib/types";

interface FilesResponse {
  files: string[];
}

export async function fetchDocuments(): Promise<DocumentInfo[]> {
  const data = await apiFetch<FilesResponse>("/files");
  return data.files.map((filename) => ({ filename }));
}

interface UploadResponse {
  message: string;
  chunks_count: number;
}

export async function uploadDocument(form: FormData): Promise<UploadResponse> {
  return apiFetch<UploadResponse>("/upload", { method: "POST", body: form });
}
```

(`GET /files` returns `{ files: string[] }`; `POST /upload` is multipart with field `file` — never set `Content-Type` manually, the browser adds the boundary.)

## 4.4 `PrimaryCard` — `src/components/cards/PrimaryCard.tsx` (full file)

Compound component — no boolean variants. Consumers compose `Header`, `Summary`, `Stats`.

```tsx
import type { ComponentType, ReactNode } from "react";

export function PrimaryCard({ children }: { children: ReactNode }) {
  return (
    <article className="flex flex-col gap-3.5 rounded-card border border-line bg-white p-6 shadow-panel transition-all duration-200 hover:-translate-y-0.5 hover:shadow-panel-hover">
      {children}
    </article>
  );
}

function Header({ icon: Icon, title }: { icon: ComponentType<{ className?: string }>; title: string }) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-[42px] w-[42px] shrink-0 items-center justify-center rounded-chip bg-gradient-to-br from-slate to-navy shadow-[0_4px_10px_-3px_rgb(33_42_62/0.5)]">
        <Icon className="h-5 w-5 text-white" />
      </div>
      <h2 className="truncate text-[1.1rem] leading-tight font-bold tracking-tight text-navy">{title}</h2>
    </div>
  );
}

function Summary({ text }: { text: string }) {
  return <p className="line-clamp-3 text-[0.9rem] leading-relaxed text-muted">{text}</p>;
}

function Stats({ children }: { children: ReactNode }) {
  return <div className="flex gap-3">{children}</div>;
}

PrimaryCard.Header = Header;
PrimaryCard.Summary = Summary;
PrimaryCard.Stats = Stats;
```

## 4.5 `StatChip` — `src/components/cards/StatChip.tsx` (full file)

```tsx
import type { ComponentType } from "react";

const TONES = {
  slate: { tile: "bg-tint-slate", icon: "text-slate" },
  bluegray: { tile: "bg-tint-bluegray", icon: "text-bluegray" },
  navy: { tile: "bg-tint-navy", icon: "text-navy" },
} as const;

interface StatChipProps {
  icon: ComponentType<{ className?: string }>;
  value: number | string;
  label: string;
  tone: keyof typeof TONES;
}

export function StatChip({ icon: Icon, value, label, tone }: StatChipProps) {
  const t = TONES[tone];
  return (
    <div className="flex flex-1 items-center gap-2.5 rounded-control border border-line bg-light px-3 py-2.5 transition-colors duration-200 hover:border-slate hover:bg-white">
      <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-chip ${t.tile}`}>
        <Icon className={`h-4 w-4 ${t.icon}`} />
      </div>
      <div>
        <div className="text-[1.05rem] leading-tight font-bold text-navy">{value}</div>
        <div className="text-[0.7rem] tracking-[0.06em] text-muted uppercase">{label}</div>
      </div>
    </div>
  );
}
```

## 4.6 `ContentCard` — `src/components/cards/ContentCard.tsx` (full file)

Per `bottom_card.md`: title + text only, 3-line clamp, no actions.

```tsx
export function ContentCard({ title, text }: { title: string; text: string }) {
  return (
    <article className="flex flex-col gap-3 rounded-card border border-line bg-white p-6 shadow-panel transition-all duration-200 hover:-translate-y-0.5 hover:shadow-panel-hover">
      <h3 className="text-[1.05rem] leading-tight font-bold text-navy">{title}</h3>
      <p className="line-clamp-3 text-[0.9rem] leading-relaxed text-muted">{text}</p>
    </article>
  );
}
```

## 4.7 UI primitives — `src/components/ui/CardSkeleton.tsx` (full file)

```tsx
export function CardSkeleton() {
  return (
    <div className="flex flex-col gap-3.5 rounded-card border border-line bg-white p-6 shadow-panel" aria-hidden="true">
      <div className="flex items-center gap-3">
        <div className="h-[42px] w-[42px] animate-pulse rounded-chip bg-hover" />
        <div className="h-4 w-40 animate-pulse rounded bg-hover" />
      </div>
      <div className="space-y-2">
        <div className="h-3 w-full animate-pulse rounded bg-hover" />
        <div className="h-3 w-11/12 animate-pulse rounded bg-hover" />
        <div className="h-3 w-3/5 animate-pulse rounded bg-hover" />
      </div>
      <div className="flex gap-3">
        <div className="h-14 flex-1 animate-pulse rounded-control bg-hover" />
        <div className="h-14 flex-1 animate-pulse rounded-control bg-hover" />
        <div className="h-14 flex-1 animate-pulse rounded-control bg-hover" />
      </div>
    </div>
  );
}
```

`src/components/ui/AlertBanner.tsx` (full file):

```tsx
const STYLES = {
  error: "border-red-200 bg-red-50 text-red-700",
  success: "border-emerald-200 bg-emerald-50 text-emerald-700",
} as const;

interface AlertBannerProps {
  kind: keyof typeof STYLES;
  message: string;
  onDismiss?: () => void;
}

export function AlertBanner({ kind, message, onDismiss }: AlertBannerProps) {
  return (
    <div role="status" className={`flex items-center justify-between gap-3 rounded-control border px-4 py-3 text-sm ${STYLES[kind]}`}>
      <span>{message}</span>
      {onDismiss && (
        <button type="button" onClick={onDismiss} aria-label="Dismiss" className="text-lg leading-none opacity-60 hover:opacity-100">
          ×
        </button>
      )}
    </div>
  );
}
```

## 4.8 `UploadDropzone` — `src/components/documents/UploadDropzone.tsx` (full file)

```tsx
"use client";

import { useRef, useState } from "react";
import { uploadDocument } from "@/services/documents";
import { AlertBanner } from "@/components/ui/AlertBanner";
import { FileIcon, SpinnerIcon } from "@/components/icons";

interface UploadDropzoneProps {
  onUploaded: () => void;
}

export function UploadDropzone({ onUploaded }: UploadDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [feedback, setFeedback] = useState<{ kind: "error" | "success"; message: string } | null>(null);

  async function handleFiles(files: FileList | null) {
    const file = files?.[0];
    if (!file || isUploading) return;
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setFeedback({ kind: "error", message: "Only PDF files are supported." });
      return;
    }
    setIsUploading(true);
    setFeedback(null);
    try {
      const form = new FormData();
      form.append("file", file);
      await uploadDocument(form);
      setFeedback({ kind: "success", message: `${file.name} processed successfully.` });
      onUploaded();
    } catch {
      setFeedback({ kind: "error", message: "Upload failed. Is the backend running?" });
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <div
        role="button"
        tabIndex={0}
        aria-label="Upload a PDF"
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          void handleFiles(e.dataTransfer.files);
        }}
        className={`flex cursor-pointer flex-col items-center justify-center gap-3 rounded-card border-2 border-dashed p-10 text-center transition-colors duration-200 focus-visible:ring-2 focus-visible:ring-slate focus-visible:outline-none ${
          isDragging ? "border-slate bg-active" : "border-line bg-white hover:border-slate"
        }`}
      >
        {isUploading ? (
          <SpinnerIcon className="h-8 w-8 animate-spin text-slate" />
        ) : (
          <FileIcon className="h-8 w-8 text-bluegray" />
        )}
        <div>
          <p className="font-semibold text-navy">{isUploading ? "Processing…" : "Drop a PDF here"}</p>
          <p className="text-sm text-muted">or click to browse</p>
        </div>
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={(e) => {
            void handleFiles(e.target.files);
            e.target.value = "";
          }}
        />
      </div>
      {feedback && <AlertBanner kind={feedback.kind} message={feedback.message} onDismiss={() => setFeedback(null)} />}
    </div>
  );
}
```

## 4.9 `DocumentRow` — `src/components/documents/DocumentRow.tsx` (full file)

```tsx
import Link from "next/link";
import { FileIcon } from "@/components/icons";

export function DocumentRow({ filename }: { filename: string }) {
  return (
    <Link
      href={`/chats/${encodeURIComponent(filename)}`}
      className="flex items-center gap-3 rounded-control border border-line bg-white px-4 py-3 shadow-panel transition-all duration-200 hover:-translate-y-0.5 hover:shadow-panel-hover"
    >
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-chip bg-tint-slate">
        <FileIcon className="h-4 w-4 text-slate" />
      </div>
      <span className="truncate font-medium text-navy">{filename}</span>
    </Link>
  );
}
```

## 4.10 Dashboard page — `src/app/(main)/page.tsx` (full file, mock data)

Server component. Mock data unblocks layout work; Step 6 replaces `MOCK_*` with live data inside `<Suspense>`.

```tsx
import { ContentCard } from "@/components/cards/ContentCard";
import { PrimaryCard } from "@/components/cards/PrimaryCard";
import { StatChip } from "@/components/cards/StatChip";
import { ChatIcon, FileIcon, FolderIcon, NoteIcon } from "@/components/icons";

const MOCK_DOCUMENTS = [
  {
    filename: "Quarterly Report Q3",
    summary:
      "This document covers the quarterly performance review including revenue growth, customer retention metrics, and regional breakdowns. It also outlines the key strategic initiatives planned for the next quarter and highlights risks identified by the operations team.",
    stats: { files: 12, chats: 8, notes: 23 },
  },
  {
    filename: "Product Roadmap 2026",
    summary:
      "The roadmap outlines the planned feature releases for the next four quarters, covering the AI assistant upgrade, mobile application launch, and enterprise integrations. It includes dependency mapping, resource allocation, and milestone dates.",
    stats: { files: 7, chats: 15, notes: 9 },
  },
];

const MOCK_CONTENT = [
  {
    title: "Meeting Summary — Ops Review",
    text: "The operations review covered supply-chain delays affecting hardware bundles, elevated churn in the SMB tier at 3.2% monthly, and hiring bottlenecks in support engineering. Mitigation owners were assigned for each risk with checkpoints set for the first week of October.",
  },
  {
    title: "Research Notes — EMEA Expansion",
    text: "Initial research on the EMEA expansion highlights strong demand in DACH and Nordics, with localization and data-residency requirements as the primary blockers. A phased entry beginning with Ireland as the data hub is recommended.",
  },
];

export default function DashboardPage() {
  return (
    <div className="grid grid-cols-2 content-start gap-6">
      {MOCK_DOCUMENTS.map((doc) => (
        <PrimaryCard key={doc.filename}>
          <PrimaryCard.Header icon={FileIcon} title={doc.filename} />
          <PrimaryCard.Summary text={doc.summary} />
          <PrimaryCard.Stats>
            <StatChip icon={FolderIcon} value={doc.stats.files} label="Files" tone="slate" />
            <StatChip icon={ChatIcon} value={doc.stats.chats} label="Chats" tone="bluegray" />
            <StatChip icon={NoteIcon} value={doc.stats.notes} label="Notes" tone="navy" />
          </PrimaryCard.Stats>
        </PrimaryCard>
      ))}
      {MOCK_CONTENT.map((card) => (
        <ContentCard key={card.title} title={card.title} text={card.text} />
      ))}
    </div>
  );
}
```

## 4.11 Documents page — `src/app/(main)/documents/page.tsx` (full file, upload live / list mocked)

```tsx
"use client";

import { DocumentRow } from "@/components/documents/DocumentRow";
import { UploadDropzone } from "@/components/documents/UploadDropzone";

const MOCK_FILES = ["Quarterly Report Q3.pdf", "Product Roadmap 2026.pdf"];

export default function DocumentsPage() {
  return (
    <div className="flex max-w-2xl flex-col gap-6">
      <h1 className="text-xl font-bold text-navy">Documents</h1>
      <UploadDropzone onUploaded={() => {}} />
      <div className="flex flex-col gap-3">
        {MOCK_FILES.map((filename) => (
          <DocumentRow key={filename} filename={filename} />
        ))}
      </div>
    </div>
  );
}
```

## Acceptance criteria

- [ ] Dashboard follows the layout described here: 2 `PrimaryCard` + 2 `ContentCard`, 3-line clamps with ellipsis
- [ ] Uploading a real PDF against the running backend returns success and the file appears in `Backend/uploads/`
- [ ] Non-PDF files show the error banner; upload failure (backend off) shows the error banner
- [ ] `tone` is the only variant selector on `StatChip`; no boolean props anywhere
- [ ] `grep -r "localhost:8000" src/` finds nothing (env var only)
