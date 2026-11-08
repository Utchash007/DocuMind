# Bottom Card Component — Wireframe

> Extracted from [dashboard_wireframe_v2.md](./dashboard_wireframe_v2.md). All layout and placeholder principles are inherited from that document; nothing there is modified.

## Component Anatomy

```text
┌────────────────────────────────────┐
│          BOTTOM CARD               │
│                                    │
│  Content line one…                 │
│  Content line two…                 │
│  Content line three…               │
│  …                                 │
│                                    │
└────────────────────────────────────┘
```

## Structure

- **Card container:** Outlined rectangle, spans one column of the 2×2 dashboard grid (bottom row).
- **Title:** The card name/heading, displayed in full at the top.
- **Content (display region):** A plain text block directly below the title — the **only** other element on the card:
  - Shows a maximum of **3 lines**.
  - Any overflow is collapsed into **three dots (…)** — no expand button, no stats, no action row.

## Principles (inherited)

1. **Placeholder-first:** Structure is independent of the final visual design.
2. **Title + preview only:** The card holds exactly two elements — title and clamped content. Nothing else.
3. **Hard 3-line cap:** Content never exceeds 3 lines; overflow is always signaled by "…", never truncated mid-line without it.
4. **Grid-driven sizing:** Width and height are determined by the parent grid column, never hardcoded in the component.
5. **Smaller footprint:** Bottom cards are more compact than top cards (which carry summaries + stat rows); this card is a glanceable preview.

## Placement in Dashboard

- Occupies the **bottom row** of the main content 2×2 grid (left and right instances).
- Sits below the two Top Cards.
- Both bottom card instances share identical structure.

## Component Mapping

```text
BottomCard
├── CardTitle
└── CardContent        # clamped: max 3 lines, "…" on overflow
```
