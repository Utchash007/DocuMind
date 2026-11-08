# Sidebar Component — Wireframe

> Extracted from [dashboard_wireframe_v2.md](./dashboard_wireframe_v2.md). All layout and placeholder principles are inherited from that document; nothing there is modified.

## Component Anatomy

```text
┌──────────────────┐
│     SIDEBAR      │
├──────────────────┤
│  ┌────────────┐  │
│  └────────────┘  │
│  ┌────────────┐  │
│  └────────────┘  │
│  ┌────────────┐  │
│  └────────────┘  │
│  ──────────────  │
│  ┌────────────┐  │
│  └────────────┘  │
│  ┌────────────┐  │
│  └────────────┘  │
│  ┌────────────┐  │
│  └────────────┘  │
│  ──────────────  │
│                  │
│       ○          │
│  ──────────────  │
└──────────────────┘
```

## Structure

- **Sidebar container:** Fixed vertical panel, visually separated from the main application area by its own border.
- **Header:** Label area at the top of the panel.
- **Navigation group (upper):** Three stacked menu items.
- **Navigation group (lower):** Three stacked menu items.
- **Profile/action area:** Circular icon with a horizontal control beneath it, anchored at the bottom.

## Principles (inherited)

1. **Placeholder-first:** All items are empty placeholders; structure is independent of the final visual design.
2. **Fixed width, full height:** The sidebar spans the full application height with a constant width; it never resizes with content.
3. **Grouped navigation:** Menu items always come in groups of three, separated by horizontal divider lines.
4. **Bottom-anchored profile:** The circular profile icon and its control are pinned to the bottom of the panel, regardless of navigation length.
5. **Visual separation:** Dividers — not color or spacing alone — delineate the header, nav groups, and profile area.

## Placement in Dashboard

- Occupies the **left edge** of the outer application container, full height.
- Sits to the left of the main content area (header + 2×2 card grid + scrollbar).
- The main content area starts immediately after the sidebar's right border.

## Component Mapping

```text
Sidebar
├── SidebarHeader
├── NavigationGroup
│   ├── NavItem
│   ├── NavItem
│   └── NavItem
├── NavigationGroup
│   ├── NavItem
│   ├── NavItem
│   └── NavItem
└── ProfileControl
```
