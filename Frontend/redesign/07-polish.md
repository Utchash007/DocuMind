# Step 7 — Polish, Performance & Cleanup

Goal: route-level loading states, transitions, accessibility, and the final performance pass that turns the working app into the finished redesign.

## 7.1 Route loading state — `src/app/(main)/documents/loading.tsx` (full file)

Streams instantly while the documents page loads:

```tsx
export default function DocumentsLoading() {
  return (
    <div className="flex max-w-2xl flex-col gap-6" aria-hidden="true">
      <div className="h-7 w-40 animate-pulse rounded bg-hover" />
      <div className="h-48 animate-pulse rounded-card border border-line bg-white/60" />
      <div className="flex flex-col gap-3">
        <div className="h-[60px] animate-pulse rounded-control bg-white/60" />
        <div className="h-[60px] animate-pulse rounded-control bg-white/60" />
      </div>
    </div>
  );
}
```

## 7.2 View Transitions (optional, from `vercel-react-view-transitions`)

React 19.2+ / Next.js support the experimental View Transition API for route cross-fades. In `src/app/layout.tsx`:

```tsx
import { unstable_ViewTransition as ViewTransition } from "react";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <ViewTransition>{children}</ViewTransition>
      </body>
    </html>
  );
}
```

If the export is unavailable in your Next.js version, skip this — the CSS hover lifts and cursor blink already carry the motion design. The `prefers-reduced-motion` block from Step 1 covers accessibility either way.

## 7.3 Accessibility checklist

- [ ] Sidebar: `<nav aria-label>`, real `<Link>`s, `aria-current="page"` on the active item (done in Step 3)
- [ ] Icon-only buttons have `aria-label`: `Composer.Submit`, `Composer.Attach`, profile gear
- [ ] Composer input has a `sr-only` label tied via `htmlFor`/`id` (done in Step 5)
- [ ] `focus-visible:ring-2 focus-visible:ring-slate focus-visible:outline-none` on every interactive element
- [ ] Upload dropzone is keyboard operable (`role="button"`, `tabIndex={0}`, Enter/Space) — done in Step 4
- [ ] Pending assistant block announces via `aria-label="Assistant is responding"`
- [ ] Body text uses `text-muted` (#5f6b85) or darker — never `bluegray` (#9ba4b5) for body copy (AA contrast)

## 7.4 Performance checklist (from `vercel-react-best-practices`)

- [ ] No component defined inside another component (grep for `= () =>` returning JSX inside a component body)
- [ ] All state updates that depend on previous state use the functional form `set(curr => ...)`
- [ ] Derived values computed during render, never written in `useEffect`
- [ ] Store selectors are narrow (one field each); `EMPTY_MESSAGES`-style defaults are module-level constants
- [ ] `MessageList` items use `content-visibility: auto` (`.message-item`, Step 1)
- [ ] No barrel files; every import points at a concrete module path
- [ ] No `forwardRef` anywhere; context consumed via `use()` not `useContext()`
- [ ] No `useEffect` doing what an event handler should (upload refresh, submit)
- [ ] `npm run build` passes with zero type errors
- [ ] `npm run lint` is clean
- [ ] No comments in any source file

## 7.5 Final cleanup

- [ ] `grep -rn "localhost:8000" src/` → empty (only `.env.local` holds the URL)
- [ ] `grep -rn "MOCK_" src/` → empty
- [ ] `src/app/page.tsx` does not exist (dashboard is `(main)/page.tsx`)
- [ ] No unused exports left in `icons.tsx` (remove any icon no component imports)
- [ ] Update root `README.md`: frontend env var `NEXT_PUBLIC_API_BASE_URL`, route map (`/`, `/documents`, `/chats`, `/chats/<filename>`)

## 7.6 Manual QA script

Run the backend (`uvicorn app.main:app --port 8000`) and frontend (`npm run dev`), then:

1. `/documents` — upload a PDF → success banner → file appears in list
2. Upload a non-PDF → error banner
3. `/` — skeleton appears, then one card per uploaded document
4. Click a document row → `/chats/<filename>` → ask a question → user bubble → blinking cursor → answer with `p. N` citation chips
5. Navigate to `/chats` → separate (empty) history → ask → answer cites across all documents
6. Navigate away and back → chat history persisted (session store)
7. Keyboard only: tab through sidebar → upload → composer → send; all focus rings visible
8. Stop the backend → send a message → inline error message appears, UI recovers when backend restarts

## Definition of done

A user can upload a PDF, see it as a dashboard card, chat about it with exact page-level citations, and navigate everything from the sidebar — with zero hardcoded URLs, zero mock data, all checklists above ticked, and every component following the layout descriptions in these guides.
