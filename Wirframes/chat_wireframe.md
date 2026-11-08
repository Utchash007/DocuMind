# Chat View Wireframe — ChatGPT-style (chat area only)

> Standalone wireframe for the chat panel. No sidebar — this view assumes it occupies the main content area. Layout principles follow the placeholder-first approach of [dashboard_wireframe_v2.md](./dashboard_wireframe_v2.md).

## Wireframe

```text
┌──────────────────────────────────────────────────────────┐
│                      CHAT HEADER                         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│                                                          │
│   ┌────────────────────────────────────────────┐         │
│   │ ASSISTANT MESSAGE (full-width block)       │         │
│   │ ○  response text…                          │         │
│   └────────────────────────────────────────────┘         │
│                                                          │
│                        ┌──────────────────────────┐      │
│                        │ USER MESSAGE (bubble)    │      │
│                        └──────────────────────────┘      │
│                                                          │
│   ┌────────────────────────────────────────────┐         │
│   │ ASSISTANT MESSAGE                          │         │
│   │ ○  response text…                          │         │
│   │    ▍(streaming cursor while generating)    │         │
│   └────────────────────────────────────────────┘         │
│                                                          │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────┐ ┌───┐  │
│  │  Ask anything…                        (＋)   │ │ ↑ │  │
│  └──────────────────────────────────────────────┘ └───┘  │
└──────────────────────────────────────────────────────────┘
```

## Structure

- **Chat header:** Slim top bar with the chat/document title; spans the full chat width.
- **Message stream (center):** Scrollable region containing the conversation:
  - **User message:** Compact, right-aligned bubble, max-width ~70% of the stream.
  - **Assistant message:** Left-aligned, full-width block (no bubble) with a small avatar/marker; response text flows edge to edge.
  - **Streaming state:** While generating, the assistant block shows a blinking cursor (▍) or "Consulting context…" placeholder.
- **Composer (bottom):** Pinned input bar:
  - Rounded input field with placeholder text and an attach (+) affordance.
  - Send button (↑) to the right; disabled while empty.

## Principles

1. **Asymmetric alignment:** User messages right (bubble), assistant messages left (full-width block) — the assistant owns the canvas.
2. **Pinned composer:** The input bar is always visible at the bottom; only the message stream scrolls.
3. **Auto-scroll:** The stream follows the newest message unless the user has scrolled up.
4. **Streaming-first:** Assistant output renders progressively; the block reserves space as text arrives.
5. **Placeholder-first:** All content is placeholder; structure is independent of final styling.
6. **Single-column flow:** Messages stack vertically in one centered column with a max readable width.

## Placement in Dashboard

- Replaces/overlays the main content area (right of the sidebar) when a chat is open.
- Can be launched from a Top Card (chat with one document) or globally (all documents).

## Component Mapping

```text
ChatView
├── ChatHeader
├── MessageList
│   ├── UserMessage
│   └── AssistantMessage
│       └── StreamingCursor?
└── Composer
    ├── InputField
    ├── AttachButton
    └── SendButton
```
