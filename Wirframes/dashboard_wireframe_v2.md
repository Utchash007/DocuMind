# Dashboard Wireframe — Version 2

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ ┌──────────────┐ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │              │ │                         TOP HEADER                                       │ │
│ │              │ └─────────────────────────────────────────────────────────────────────────┘ │
│ │              │                                                                            │
│ │   SIDEBAR    │   ┌──────────────────────────────┐      ┌──────────────────────────────┐   │
│ │              │   │                              │      │                              │   │
│ ├──────────────┤   │                              │      │                              │   │
│ │              │   │          TOP CARD             │      │          TOP CARD             │   │
│ │  ─────────   │   │                              │      │                              │   │
│ │              │   │  ┌──────┐ ┌──────┐ ┌─────┐ │      │  ┌──────┐ ┌──────┐ ┌──────┐ │   │
│ │  ─────────   │   │  │      │ │      │ │     │ │      │  │      │ │      │ │      │ │   │
│ │              │   │  └──────┘ └──────┘ └─────┘ │      │  └──────┘ └──────┘ └──────┘ │   │
│ │  ─────────   │   └──────────────────────────────┘      └──────────────────────────────┘   │
│ │              │                                                                            │
│ ├──────────────┤                                                                            │
│ │              │      ┌──────────────────────────┐          ┌──────────────────────────┐    │
│ │  ─────────   │      │                          │          │                          │    │
│ │              │      │                          │          │                          │    │
│ │  ─────────   │      │       BOTTOM CARD        │          │       BOTTOM CARD        │    │
│ │              │      │                          │          │                          │    │
│ │  ─────────   │      │  ┌────┐ ┌────┐ ┌────┐  │          │  ┌────┐ ┌────┐ ┌────┐  │    │
│ │              │      │  │    │ │    │ │    │  │          │  │    │ │    │ │    │  │    │
│ │              │      │  └────┘ └────┘ └────┘  │          │  └────┘ └────┘ └────┘  │    │
│ │              │      └──────────────────────────┘          └──────────────────────────┘    │
│ ├──────────────┤                                                                            │
│ │      ○       │                                                    │                        │
│ │   ─────────  │                                                    │                        │
│ └──────────────┘                                                    │                        │
└─────────────────────────────────────────────────────────────────────┴────────────────────────┘
```

## Layout Structure

- **Outer container:** Full-page bordered application/dashboard.
- **Top header:** A horizontal header spanning the main content area above the cards.
- **Left sidebar:** Fixed vertical navigation panel.
  - Upper navigation section with three menu items.
  - Lower navigation section with three menu items.
  - Bottom profile/action area with a circular icon and horizontal control.
- **Main content area:** Four cards arranged in a 2×2 grid.
  - **Top-left card:** Large display/content region with three small controls at the bottom.
  - **Top-right card:** Large display/content region with three small controls at the bottom.
  - **Bottom-left card:** Medium content region with three small controls at the bottom.
  - **Bottom-right card:** Medium content region with three small controls at the bottom.
- **Right side:** A tall vertical scrollbar/control near the right edge of the main content area.

## Suggested Component Structure

```text
App
├── Sidebar
│   ├── SidebarHeader
│   ├── NavigationGroup
│   │   ├── NavItem
│   │   ├── NavItem
│   │   └── NavItem
│   ├── NavigationGroup
│   │   ├── NavItem
│   │   ├── NavItem
│   │   └── NavItem
│   └── ProfileControl
│
└── MainContent
    ├── Header
    ├── DashboardGrid
    │   ├── DashboardCard
    │   │   └── CardActions × 3
    │   ├── DashboardCard
    │   │   └── CardActions × 3
    │   ├── DashboardCard
    │   │   └── CardActions × 3
    │   └── DashboardCard
    │       └── CardActions × 3
    └── ScrollControl
```

## Wireframe Notes

- The sidebar is visually separated from the main application area.
- The header sits above the main card grid.
- The four cards use a two-column layout.
- Each card has a large empty area intended for the eventual content, chart, image, or data visualization.
- Small rectangular elements at the bottom of each card represent buttons, metrics, tabs, or other card-level controls.
- The wireframe intentionally keeps all content as placeholders so the structure can be implemented independently of the final UI design.
