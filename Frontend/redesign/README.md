# DocuMind Frontend Redesign — Step-by-Step Guide

> These guides describe the earlier redesign plan. The implemented NoteMind workspace requires email-code sign-in and follows [`notemind-ux-wireframe.md`](../../notemind-ux-wireframe.md) and the Chalk shadcn/ui theme. See the [current frontend README](../README.md) for implemented routes, data flow, and checks.

This folder is a numbered, hands-on guide for redesigning the DocuMind frontend from the current single-file monolith into a properly structured Next.js App Router application that implements the approved wireframes and navy palette.

## Read in this order

| # | File | What you build |
|---|------|----------------|
| 1 | [01-foundations.md](./01-foundations.md) | Design tokens (palette, radii, shadows) in Tailwind v4 `@theme` |
| 2 | [02-architecture.md](./02-architecture.md) | Target folder structure, composition rules, state strategy |
| 3 | [03-app-shell.md](./03-app-shell.md) | Route groups, `Sidebar`, navigation, placeholder pages |
| 4 | [04-dashboard.md](./04-dashboard.md) | Dashboard page: `PrimaryCard`, `ContentCard`, upload flow |
| 5 | [05-chat-view.md](./05-chat-view.md) | Chat page: `Composer`, `MessageList`, citations, streaming |
| 6 | [06-state-data.md](./06-state-data.md) | Zustand stores (LobeHub slice conventions), typed API services |
| 7 | [07-polish.md](./07-polish.md) | Transitions, loading/empty/error states, a11y, perf checklist |

## Current state (what we are fixing)

- Entire UI lives in one client component: `src/app/page.tsx` (~300 lines of inline JSX).
- Hardcoded `API_BASE = http://localhost:8000`.
- No component directory, no state library, no design tokens — inline Tailwind classes everywhere.
- No routing: upload, document selection, and chat are all one page.

## Target design sources

- Wireframes: `../Wirframes/dashboard_wireframe.md`, `sidebar.md`, `top_card.md`, `bottom_card.md`, `chat_wireframe.md`
- Approved HTML mockups: `../Wirframes/sidebar.html`, `dashboard.html`, `chat.html`, `top_card.html`
- Palette: `#F1F6F9` (light) `#394867` (slate) `#212A3E` (navy) `#9BA4B5` (bluegray)

## Rules that apply to every step

1. Follow `.agents/skills/vercel-composition-patterns` — compound components, no boolean-prop variants, providers own state.
2. Follow `.agents/skills/vercel-react-best-practices` — no waterfalls, Suspense boundaries, no components defined inside components.
3. Follow `.agents/skills/zustand` — public actions, `internal_*` actions, dispatch pattern, optimistic updates only where safe.
4. React 19: never use `forwardRef` (`ref` is a normal prop); use `use()` instead of `useContext()`.
5. No comments in code. No new heavy dependencies (no component kits, no icon libraries — inline SVGs like the mockups).

## Backend contract (unchanged)

- `POST /upload` — multipart PDF upload
- `GET /files` — list of processed documents
- `POST /query` — `{ question, filename? }` → `{ answer, citations: [{ sentence, page }] }`
- `GET /health`
