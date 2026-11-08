# Step 6 — State & Data Layer (Zustand)

Goal: move chat and documents state into Zustand stores following the LobeHub slice conventions (public actions → `internal_*` actions → `internal_dispatch*` reducers), and swap the Step 5 provider to the store-backed one **without touching any UI component**. Mock data is replaced with live data.

Prerequisite: `npm install zustand`

## 6.1 Documents store — `src/store/documents/slice.ts` (full file)

```ts
import { create } from "zustand";
import { fetchDocuments } from "@/services/documents";
import type { DocumentInfo } from "@/lib/types";

interface DocumentsState {
  documents: DocumentInfo[];
  isLoading: boolean;
  error: string | null;
}

interface DocumentsActions {
  fetchAll: () => Promise<void>;
  internal_dispatchDocuments: (documents: DocumentInfo[]) => void;
  internal_setLoading: (value: boolean) => void;
  internal_setError: (error: string | null) => void;
}

export const useDocumentsStore = create<DocumentsState & DocumentsActions>()((set, get) => ({
  documents: [],
  isLoading: false,
  error: null,

  fetchAll: async () => {
    get().internal_setLoading(true);
    try {
      const documents = await fetchDocuments();
      get().internal_dispatchDocuments(documents);
      get().internal_setError(null);
    } catch {
      get().internal_setError("Could not reach the backend. Is it running on port 8000?");
    } finally {
      get().internal_setLoading(false);
    }
  },

  internal_dispatchDocuments: (documents) => set({ documents }),
  internal_setLoading: (value) => set({ isLoading: value }),
  internal_setError: (error) => set({ error }),
}));
```

Notes:

- `fetchAll` is the **public action**: validation + orchestration only.
- All state writes go through `internal_*` actions — UI never calls `set`.
- Upload stays in `UploadDropzone`'s event handler (interaction logic belongs in handlers, not effects); it calls `onUploaded()` → the page refetches via `fetchAll`. No optimistic update for uploads (the server does heavy PDF processing — reflect real state).

## 6.2 Chat store — `src/store/chat/slice.ts` (full file)

```ts
import { create } from "zustand";
import { sendQuery } from "@/services/chat";
import type { ChatMessage } from "@/lib/types";

interface ChatState {
  messagesMap: Record<string, ChatMessage[]>;
  input: string;
  isSending: boolean;
}

interface SendMessageParams {
  question: string;
  filename?: string;
  scopeId: string;
}

interface ChatActions {
  updateInput: (text: string) => void;
  sendMessage: (params: SendMessageParams) => Promise<void>;
  internal_sendMessage: (params: SendMessageParams) => Promise<void>;
  internal_dispatchMessages: (scopeId: string, updater: (curr: ChatMessage[]) => ChatMessage[]) => void;
  internal_setSending: (value: boolean) => void;
}

export const useChatStore = create<ChatState & ChatActions>()((set, get) => ({
  messagesMap: {},
  input: "",
  isSending: false,

  updateInput: (text) => set({ input: text }),

  sendMessage: async ({ question, filename, scopeId }) => {
    const { internal_dispatchMessages, internal_sendMessage } = get();
    const userMessage: ChatMessage = {
      id: `u${Date.now()}`,
      role: "user",
      text: question,
    };
    internal_dispatchMessages(scopeId, (curr) => [...curr, userMessage]);
    await internal_sendMessage({ question, filename, scopeId });
  },

  internal_sendMessage: async ({ question, filename, scopeId }) => {
    const { internal_dispatchMessages, internal_setSending } = get();
    internal_setSending(true);
    try {
      const data = await sendQuery({ question, filename });
      internal_dispatchMessages(scopeId, (curr) => [
        ...curr,
        {
          id: `a${Date.now()}`,
          role: "assistant",
          text: data.answer,
          citations: data.citations,
        },
      ]);
    } catch {
      internal_dispatchMessages(scopeId, (curr) => [
        ...curr,
        {
          id: `e${Date.now()}`,
          role: "assistant",
          text: "Something went wrong while answering. Please try again.",
        },
      ]);
    } finally {
      internal_setSending(false);
    }
  },

  internal_dispatchMessages: (scopeId, updater) =>
    set((state) => ({
      messagesMap: {
        ...state.messagesMap,
        [scopeId]: updater(state.messagesMap[scopeId] ?? []),
      },
    })),

  internal_setSending: (value) => set({ isSending: value }),
}));
```

Why this shape (per the zustand skill):

- `messagesMap` (a map keyed by chat scope) uses the reducer pattern; `input` / `isSending` use plain `set`.
- Optimistic update is safe here: the user bubble is appended before the request, and the assistant reply/error always lands after. Deletions would NOT get optimistic updates.
- `internal_dispatchMessages` is the only place that mutates `messagesMap`.

## 6.3 Swap the provider — `src/components/chat/ChatProvider.tsx` (full replacement)

Same `ChatContextValue` interface, store-backed implementation. **No UI component changes.**

```tsx
"use client";

import { use, type ReactNode, useCallback } from "react";
import { useChatStore } from "@/store/chat/slice";
import type { ChatMessage } from "@/lib/types";
import { ChatContext, type ChatContextValue } from "./chat-context";

const EMPTY_MESSAGES: ChatMessage[] = [];

export function scopeId(filename?: string) {
  return filename ?? "all";
}

export function ChatProvider({ filename, children }: { filename?: string; children: ReactNode }) {
  const scope = scopeId(filename);

  const messages = useChatStore((s) => s.messagesMap[scope]) ?? EMPTY_MESSAGES;
  const input = useChatStore((s) => s.input);
  const isSending = useChatStore((s) => s.isSending);

  const update = useCallback((text: string) => {
    useChatStore.getState().updateInput(text);
  }, []);

  const submit = useCallback(async () => {
    const store = useChatStore.getState();
    const question = store.input.trim();
    if (!question || store.isSending) return;
    store.updateInput("");
    await store.sendMessage({ question, filename, scopeId: scope });
  }, [filename, scope]);

  const value: ChatContextValue = {
    state: { messages, input, isSending },
    actions: { update, submit },
    meta: { inputId: "chat-input" },
  };

  return <ChatContext value={value}>{children}</ChatContext>;
}
```

Details that matter:

- `EMPTY_MESSAGES` is a module-level constant — an inline `?? []` would create a new array every render and defeat selector equality (re-render optimization 5.5).
- Selectors are narrow: each subscription reads one field, so typing in the input doesn't re-render `MessageList`.
- Actions read the store imperatively via `useChatStore.getState()` inside stable `useCallback`s — no stale closures, no changing identities.

## 6.4 Documents page — live data (`src/app/(main)/documents/page.tsx`, full replacement)

```tsx
"use client";

import { useEffect } from "react";
import { DocumentRow } from "@/components/documents/DocumentRow";
import { UploadDropzone } from "@/components/documents/UploadDropzone";
import { AlertBanner } from "@/components/ui/AlertBanner";
import { useDocumentsStore } from "@/store/documents/slice";

export default function DocumentsPage() {
  const documents = useDocumentsStore((s) => s.documents);
  const isLoading = useDocumentsStore((s) => s.isLoading);
  const error = useDocumentsStore((s) => s.error);
  const fetchAll = useDocumentsStore((s) => s.fetchAll);

  useEffect(() => {
    void fetchAll();
  }, [fetchAll]);

  return (
    <div className="flex max-w-2xl flex-col gap-6">
      <h1 className="text-xl font-bold text-navy">Documents</h1>
      <UploadDropzone onUploaded={() => void fetchAll()} />
      {error && <AlertBanner kind="error" message={error} />}
      {isLoading ? (
        <p className="text-sm text-muted">Loading documents…</p>
      ) : documents.length === 0 ? (
        <p className="text-sm text-muted">No documents yet. Upload your first PDF above.</p>
      ) : (
        <div className="flex flex-col gap-3">
          {documents.map((doc) => (
            <DocumentRow key={doc.filename} filename={doc.filename} />
          ))}
        </div>
      )}
    </div>
  );
}
```

## 6.5 Dashboard page — live data (`src/app/(main)/page.tsx`, full replacement)

Server component + `<Suspense>`: the page shell renders instantly, cards stream in.

```tsx
import { Suspense } from "react";
import Link from "next/link";
import { ContentCard } from "@/components/cards/ContentCard";
import { PrimaryCard } from "@/components/cards/PrimaryCard";
import { StatChip } from "@/components/cards/StatChip";
import { CardSkeleton } from "@/components/ui/CardSkeleton";
import { fetchDocuments } from "@/services/documents";
import { ChatIcon, FileIcon, FolderIcon, NoteIcon } from "@/components/icons";

export default function DashboardPage() {
  return (
    <div className="grid grid-cols-2 content-start gap-6">
      <Suspense
        fallback={
          <>
            <CardSkeleton />
            <CardSkeleton />
          </>
        }
      >
        <DocumentCards />
      </Suspense>
      <ContentCard
        title="Getting started"
        text="Upload a PDF from the Documents page, then open a chat to ask questions with page-level citations. Cards on this dashboard will summarize each document once summaries are generated."
      />
      <ContentCard
        title="Hybrid RAG"
        text="DocuMind combines dense vector search with BM25 keyword matching, then answers with exact sentence citations and page numbers powered by Groq."
      />
    </div>
  );
}

async function DocumentCards() {
  const documents = await fetchDocuments();

  if (documents.length === 0) {
    return (
      <div className="col-span-2 rounded-card border border-dashed border-line bg-white/60 p-10 text-center">
        <p className="font-semibold text-navy">No documents yet</p>
        <p className="mt-1 text-sm text-muted">
          Upload your first PDF on the{" "}
          <Link href="/documents" className="font-medium text-slate underline">
            Documents
          </Link>{" "}
          page.
        </p>
      </div>
    );
  }

  return (
    <>
      {documents.map((doc) => (
        <PrimaryCard key={doc.filename}>
          <PrimaryCard.Header icon={FileIcon} title={doc.filename} />
          <PrimaryCard.Summary text="Open a chat to ask questions about this document. Automatic summaries will appear here." />
          <PrimaryCard.Stats>
            <StatChip icon={FolderIcon} value="—" label="Files" tone="slate" />
            <StatChip icon={ChatIcon} value="—" label="Chats" tone="bluegray" />
            <StatChip icon={NoteIcon} value="—" label="Notes" tone="navy" />
          </PrimaryCard.Stats>
        </PrimaryCard>
      ))}
    </>
  );
}
```

(Stats show `—` until the backend exposes per-document counts — placeholder-first, no fake numbers.)

## 6.6 Delete the mocks

- Step 4's `MOCK_DOCUMENTS` / `MOCK_CONTENT` / `MOCK_FILES` arrays are now gone from all pages.
- `grep -rn "MOCK_" src/` must return nothing.

## Acceptance criteria

- [ ] `/documents` lists real uploads from `GET /files`; uploading refreshes the list automatically
- [ ] Dashboard shows one `PrimaryCard` per uploaded file with skeletons while loading
- [ ] Chat works identically after the provider swap — zero edits were needed in `Composer`, `MessageList`, or message components
- [ ] Chat history survives navigating dashboard → chat and back (store persists for the session)
- [ ] Scoped chats (`/chats/<filename>`) and all-documents chat (`/chats`) keep separate histories (`messagesMap` keys)
- [ ] Store naming follows `public / internal_ / internal_dispatch*` throughout
