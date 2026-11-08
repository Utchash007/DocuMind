# Top Card Component — Wireframe

> Extracted from [dashboard_wireframe_v2.md](./dashboard_wireframe_v2.md). All layout and placeholder principles are inherited from that document; nothing there is modified.

## Component Anatomy

```text
┌────────────────────────────────────┐
│            TOP CARD                │
│  ┌──────────────────────────────┐  │
│  │  Summary text clamped to a   │  │
│  │  maximum of 2–3 lines…       │  │
│  └──────────────────────────────┘  │
│  ┌──────┐  ┌──────┐  ┌──────┐     │
│  │ X    │  │ Y    │  │ Z    │     │
│  │files │  │chats │  │notes │     │
│  └──────┘  └──────┘  └──────┘     │
└────────────────────────────────────┘
```

## Structure

- **Card container:** Outlined rectangle, spans one column of the 2×2 dashboard grid.
- **Title:** First element of the card — the name/heading, displayed in full at the top.
- **Summary (display region):** A text block directly below the title. The full summary is **never** shown; it is clamped to a maximum of **2–3 lines** with truncation/ellipsis for overflow.
- **Stat row:** Three small boxes centered at the bottom:
  - **Files** — "X files" (number of uploaded/linked files)
  - **Chats** — "Y chats" (number of conversations)
  - **Notes** — "Z notes" (number of saved notes)

## Principles (inherited)

1. **Placeholder-first:** Structure is independent of the final visual design.
2. **Truncated summary:** The display region shows a preview only — hard cap of 2–3 lines; the full text lives behind the card (detail view/chat).
3. **Fixed stat row:** Exactly three stats — files, chats, notes — always bottom-centered, in that order.
4. **Grid-driven sizing:** Width and height are determined by the parent grid column, never hardcoded in the component.
5. **Consistent insets:** Equal padding between the card border, summary region, and stat row.

## Placement in Dashboard

- Occupies the **top row** of the main content 2×2 grid (left and right instances).
- Sits below the TOP HEADER and above the bottom card row.
- Both top card instances share identical structure; each represents one document/workspace with its own title, summary, and stats.

## Component Mapping

```text
TopCard
├── CardTitle
├── CardSummary        # clamped: max 2–3 lines, ellipsis on overflow
└── CardStats
    ├── StatFiles      # "X files"
    ├── StatChats      # "Y chats"
    └── StatNotes      # "Z notes"
```
