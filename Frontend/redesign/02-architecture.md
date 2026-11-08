# Step 2 — Architecture & Conventions

Goal: agree on the folder structure, the server/client split, and the component + state patterns before writing any feature code. Everything in later steps follows this document.

## 2.1 Target folder structure

```text
src/
├── app/
│   ├── layout.tsx              # root layout: fonts, metadata only
│   ├── globals.css             # tokens (Step 1)
│   ├── (main)/                 # route group: pages with the sidebar shell
│   │   ├── layout.tsx          # Sidebar + <main> wrapper
│   │   ├── page.tsx            # Dashboard
│   │   ├── documents/page.tsx  # Upload + document list
│   │   └── settings/page.tsx   # placeholder
│   └── chats/
│       ├── page.tsx            # all-documents chat
│       └── [filename]/page.tsx # chat scoped to one document
├── components/
│   ├── layout/                 # Sidebar, NavSection, NavItem, ProfileControl
│   ├── cards/                  # PrimaryCard, ContentCard, StatChip
│   ├── chat/                   # Composer, MessageList, UserMessage, AssistantMessage, CitationChip
│   ├── documents/              # UploadDropzone, DocumentRow
│   └── ui/                     # small primitives: Spinner, AlertBanner
├── store/
│   ├── chat/slice.ts           # messages, sending state, actions
│   └── documents/slice.ts      # file list, active document
├── services/
│   ├── api.ts                  # base client (reads env var)
│   ├── chat.ts                 # POST /query
│   └── documents.ts            # GET /files, POST /upload
└── lib/
    └── types.ts                # shared types: Citation, AnswerResponse, DocumentInfo
```

## 2.2 Server vs client components

Default to **server components**. Add `"use client"` only where interactivity demands it:

| Server (default) | Client (`"use client"`) |
|---|---|
| Dashboard page shell | `Sidebar` (needs `usePathname`) |
| Card layouts with static content | `Composer` (input state) |
| Document list rendering | `UploadDropzone` (drag events, `FormData`) |
| — | `MessageList` (auto-scroll, store subscription) |

Never mark a whole page client just because one leaf is interactive — push `"use client"` to the leaves.

## 2.3 Component composition rules (from `vercel-composition-patterns`)

1. **No boolean-prop variants.** Not `<Card isPrimary isCompact>` — separate explicit components: `PrimaryCard`, `ContentCard`.
2. **Compound components for complex UI.** `Composer` and `PrimaryCard` expose sub-parts (`Composer.Input`, `Composer.Submit`, `Card.Header`, `Card.Stats`) sharing state through a provider, not through prop drilling.
3. **Provider owns state; UI consumes an interface.** Context value shape is always `{ state, actions, meta }`. The provider is the only place that knows state comes from Zustand.
4. **Children over render props** for static structure.
5. **React 19:** `ref` is a plain prop — no `forwardRef`. Use `use(Context)` instead of `useContext(Context)`.

## 2.4 State strategy (from `zustand` skill)

- One store per domain: `chatStore`, `documentsStore`. Each store = `initialState` + slices.
- Action naming: public `sendMessage`, `uploadDocument`; internal `internal_sendMessage`, `internal_dispatchMessages`; dispatch handlers `internal_dispatch*`.
- Reducer pattern for message lists/maps; plain `set` for booleans/simple values.
- Optimistic updates: allowed for **sending a message** (append user bubble immediately, replace pending state on response). Not for deletions.
- Components subscribe with narrow selectors (`useChatStore(s => s.messages)`) — never destructure the whole store.

## 2.5 Data layer rules (from `vercel-react-best-practices`)

- `API_BASE` comes from `process.env.NEXT_PUBLIC_API_BASE_URL` (add `.env.local`). No hardcoded localhost.
- One typed fetcher per endpoint in `services/`; components never call `fetch` directly.
- Independent requests run in `Promise.all`. Server pages stream slow sections inside `<Suspense>` with skeleton fallbacks.
- No barrel files (`index.ts` re-exports) — import from concrete paths.
- Long lists (`MessageList`) use `content-visibility: auto` on items.
- Never define components inside components; never mutate state (use `toSorted`, spread).

## Acceptance criteria

- [ ] Folder skeleton created (empty files are fine at this point)
- [ ] `.env.local` has `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`
- [ ] You can point at any planned file and say whether it will be a server or client component
