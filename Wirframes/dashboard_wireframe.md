# Dashboard Wireframe

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ ┌──────────────┐                                                                            │
│ │              │                                                                            │
│ │   SIDEBAR    │                                                                            │
│ │              │                                                                            │
│ ├──────────────┤   ┌──────────────────────────────┐      ┌──────────────────────────────┐   │
│ │              │   │                              │      │                              │   │
│ │  ─────────   │   │                              │      │                              │   │
│ │  ─────────   │   │         MAIN CARD            │      │         MAIN CARD            │   │
│ │  ─────────   │   │                              │      │                              │   │
│ │              │   │  ┌────────┐ ┌────────┐ ┌────────┐ │ │  ┌────────┐ ┌────────┐ ┌────────┐ │
│ │  ─────────   │   │  │  BOX   │ │  BOX   │ │  BOX   │ │ │  │  BOX   │ │  BOX   │ │  BOX   │ │
│ │  ─────────   │   │  └────────┘ └────────┘ └────────┘ │ │  └────────┘ └────────┘ └────────┘ │
│ │  ─────────   │   └──────────────────────────────┘      └──────────────────────────────┘   │
│ │              │                                                                            │
│ ├──────────────┤       ┌──────────────────────────┐          ┌──────────────────────────┐   │
│ │              │       │                          │          │                          │   │
│ │  ─────────   │       │                          │          │                          │   │
│ │  ─────────   │       │        CONTENT           │          │        CONTENT           │   │
│ │  ─────────   │       │          CARD            │          │          CARD            │   │
│ │              │       │                          │          │                          │   │
│ │              │       └──────────────────────────┘          └──────────────────────────┘   │
│ │              │                                                                            │
│ ├──────────────┤                                                                            │
│ │              │                                                                            │
│ │      ○       │                                                                            │
│ │   ─────────  │                                                                            │
│ └──────────────┘                                                                            │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Layout Structure

- **Outer container:** Full-page bordered dashboard.
- **Left sidebar:** Fixed vertical navigation area.
  - Top empty/header section.
  - First navigation group with three menu items.
  - Second navigation group with three menu items.
  - Bottom profile/action area with circular icon and horizontal control.
- **Main content area:**
  - **Top row:** Two large cards.
    - Each card contains a large content/display area.
    - Each card has three small boxes/actions along the bottom.
  - **Bottom row:** Two medium-sized content cards.
- **Overall layout:** Sidebar + 2-column main dashboard grid.

## Suggested Component Names

| Area | Component |
|---|---|
| Page | `Dashboard` |
| Left navigation | `Sidebar` |
| Navigation groups | `NavSection` |
| Top-left card | `PrimaryCard` |
| Top-right card | `PrimaryCard` |
| Small boxes | `CardAction` |
| Bottom-left card | `ContentCard` |
| Bottom-right card | `ContentCard` |
| Bottom sidebar control | `ProfileControl` |
