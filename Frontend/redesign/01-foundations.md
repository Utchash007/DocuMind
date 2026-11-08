# Step 1 — Design Foundations

Goal: encode the approved navy palette and visual language as Tailwind v4 theme tokens so every later step uses semantic utilities (`bg-navy`, `text-muted`, `rounded-card`) instead of raw hex values.

## 1.1 `src/app/globals.css` — full file

Replace the entire file with:

```css
@import "tailwindcss";

@theme {
  --color-light: #f1f6f9;
  --color-surface: #e4ebf3;
  --color-slate: #394867;
  --color-navy: #212a3e;
  --color-bluegray: #9ba4b5;
  --color-muted: #5f6b85;
  --color-line: #e1e6ee;
  --color-active: #e3e9f2;
  --color-hover: #eceff5;
  --color-tint-slate: #e3e9f2;
  --color-tint-bluegray: #eceef2;
  --color-tint-navy: #e8ebf1;

  --radius-card: 20px;
  --radius-control: 14px;
  --radius-chip: 10px;

  --shadow-panel:
    0 1px 2px rgb(33 42 62 / 0.06),
    0 12px 32px -12px rgb(57 72 103 / 0.25);
  --shadow-panel-hover:
    0 2px 4px rgb(33 42 62 / 0.07),
    0 20px 44px -14px rgb(57 72 103 / 0.35);

  --font-sans: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
}

body {
  background: linear-gradient(135deg, var(--color-light) 0%, var(--color-surface) 100%);
  color: var(--color-navy);
  min-height: 100vh;
}

@keyframes blink {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}

.blinking-cursor {
  animation: blink 1s step-end infinite;
}

.message-item {
  content-visibility: auto;
  contain-intrinsic-size: 0 80px;
}

@media (prefers-reduced-motion: reduce) {
  .blinking-cursor {
    animation: none;
  }
  *,
  *::before,
  *::after {
    transition-duration: 0.01ms !important;
  }
}
```

What each block is for:

- `@theme` → Tailwind v4 generates utilities: `bg-navy`, `text-muted`, `border-line`, `rounded-card`, `shadow-panel`, `font-sans`, plus tint colors for stat chips.
- `body` → the cream-to-blue page gradient from the mockups.
- `blink` / `.blinking-cursor` → the streaming cursor in the chat (Step 5).
- `.message-item` → `content-visibility` so long chats skip off-screen rendering (perf rule 6.2).
- `prefers-reduced-motion` → accessibility fallback.

## 1.2 `src/components/icons.tsx` — full file

All icons share one wrapper so stroke style stays consistent (Feather style, `strokeWidth 2`, round caps — same as the HTML mockups):

```tsx
import type { ReactNode } from "react";

interface IconProps {
  className?: string;
}

function Svg({ className = "h-5 w-5", children }: IconProps & { children: ReactNode }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

export function GridIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="14" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" />
    </Svg>
  );
}

export function FileIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <path d="M14 2v6h6" />
    </Svg>
  );
}

export function FolderIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
    </Svg>
  );
}

export function ChatIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </Svg>
  );
}

export function NoteIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z" />
    </Svg>
  );
}

export function GearIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </Svg>
  );
}

export function HelpIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <circle cx="12" cy="12" r="10" />
      <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </Svg>
  );
}

export function SendIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <path d="M12 19V5" />
      <path d="M5 12l7-7 7 7" />
    </Svg>
  );
}

export function PlusIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <path d="M12 5v14" />
      <path d="M5 12h14" />
    </Svg>
  );
}

export function SpinnerIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <path d="M21 12a9 9 0 1 1-6.219-8.56" />
    </Svg>
  );
}

export function SparkleIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <path d="M14 2v6h6" />
      <path d="M12 10.8c.42 1.66 1.44 2.68 3.1 3.1-1.66.42-2.68 1.44-3.1 3.1-.42-1.66-1.44-2.68-3.1-3.1 1.66-.42 2.68-1.44 3.1-3.1z" />
    </Svg>
  );
}
```

## 1.3 Verify

Run `npm run dev` and confirm in DevTools that `bg-navy`, `text-muted`, `rounded-card`, and `shadow-panel` all resolve to the token values.

## Acceptance criteria

- [ ] `globals.css` matches the file above exactly
- [ ] `icons.tsx` exports: `GridIcon`, `FileIcon`, `FolderIcon`, `ChatIcon`, `NoteIcon`, `GearIcon`, `HelpIcon`, `SendIcon`, `PlusIcon`, `SpinnerIcon`, `SparkleIcon`
- [ ] No hex values appear outside `globals.css` from this point on
