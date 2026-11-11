# Step 5 — Chat View

Goal: implement the ChatGPT-style chat described below — fullscreen, no sidebar — with a compound `Composer`, explicit message variants, citation chips, and a working query round-trip.

## 5.1 Chat service — `src/services/chat.ts` (full file)

The backend's `POST /query` accepts **FormData** (`query`, optional `filename`) — not JSON:

```ts
import { apiFetch } from "./api";
import type { AnswerResponse } from "@/lib/types";

export async function sendQuery(params: {
  question: string;
  filename?: string;
}): Promise<AnswerResponse> {
  const form = new FormData();
  form.append("query", params.question);
  if (params.filename) {
    form.append("filename", params.filename);
  }
  return apiFetch<AnswerResponse>("/query", { method: "POST", body: form });
}
```

## 5.2 Chat context — `src/components/chat/chat-context.ts` (full file)

The generic `{ state, actions, meta }` interface from the composition skill. UI components consume this — they never touch Zustand or fetch:

```ts
"use client";

import { createContext, use } from "react";
import type { ChatMessage } from "@/lib/types";

interface ChatState {
  messages: ChatMessage[];
  input: string;
  isSending: boolean;
}

interface ChatActions {
  update: (text: string) => void;
  submit: () => void;
}

interface ChatMeta {
  inputId: string;
}

export interface ChatContextValue {
  state: ChatState;
  actions: ChatActions;
  meta: ChatMeta;
}

export const ChatContext = createContext<ChatContextValue | null>(null);

export function useChat(): ChatContextValue {
  const value = use(ChatContext);
  if (!value) {
    throw new Error("Chat components must be rendered inside <ChatProvider>");
  }
  return value;
}
```

## 5.3 Provider — `src/components/chat/ChatProvider.tsx` (full file)

Step 5 version uses local state so the UI is testable immediately. In Step 6 you swap this single file to a Zustand-backed implementation with the **same context interface** — no other component changes.

```tsx
"use client";

import { type ReactNode, useCallback, useState } from "react";
import { sendQuery } from "@/services/chat";
import type { ChatMessage } from "@/lib/types";
import { ChatContext, type ChatContextValue } from "./chat-context";

let nextId = 0;

export function ChatProvider({ filename, children }: { filename?: string; children: ReactNode }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);

  const submit = useCallback(async () => {
    const question = input.trim();
    if (!question || isSending) return;

    setMessages((curr) => [...curr, { id: `u${++nextId}`, role: "user", text: question }]);
    setInput("");
    setIsSending(true);
    try {
      const data = await sendQuery({ question, filename });
      setMessages((curr) => [
        ...curr,
        {
          id: `a${++nextId}`,
          role: "assistant",
          text: data.answer,
          citations: data.citations,
        },
      ]);
    } catch {
      setMessages((curr) => [
        ...curr,
        {
          id: `e${++nextId}`,
          role: "assistant",
          text: "Something went wrong while answering. Please try again.",
        },
      ]);
    } finally {
      setIsSending(false);
    }
  }, [input, isSending, filename]);

  const value: ChatContextValue = {
    state: { messages, input, isSending },
    actions: { update: setInput, submit },
    meta: { inputId: "chat-input" },
  };

  return <ChatContext value={value}>{children}</ChatContext>;
}
```

## 5.4 `Composer` — `src/components/chat/Composer.tsx` (full file)

Compound component: `Composer.Frame` (a real `<form>`), `Composer.Attach`, `Composer.Input`, `Composer.Submit`. State flows only through `useChat()`.

```tsx
"use client";

import type { ReactNode } from "react";
import { PlusIcon, SendIcon } from "@/components/icons";
import { useChat } from "./chat-context";

function Frame({ children }: { children: ReactNode }) {
  const { actions } = useChat();
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void actions.submit();
      }}
      className="flex items-center gap-2 rounded-full border border-line bg-white py-2 pr-2 pl-5 shadow-panel focus-within:border-slate"
    >
      {children}
    </form>
  );
}

function Attach() {
  return (
    <button
      type="button"
      aria-label="Attach file"
      className="shrink-0 text-bluegray transition-colors duration-200 hover:text-slate"
    >
      <PlusIcon className="h-5 w-5" />
    </button>
  );
}

function Input() {
  const { state, actions, meta } = useChat();
  return (
    <>
      <label htmlFor={meta.inputId} className="sr-only">
        Ask anything
      </label>
      <input
        id={meta.inputId}
        value={state.input}
        onChange={(e) => actions.update(e.target.value)}
        placeholder="Ask anything…"
        autoComplete="off"
        className="h-10 min-w-0 flex-1 bg-transparent text-[0.95rem] text-navy placeholder:text-bluegray focus:outline-none"
      />
    </>
  );
}

function Submit() {
  const { state } = useChat();
  const disabled = state.isSending || state.input.trim().length === 0;
  return (
    <button
      type="submit"
      disabled={disabled}
      aria-label="Send message"
      className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-navy text-white transition-colors duration-200 hover:bg-slate disabled:cursor-not-allowed disabled:opacity-40"
    >
      <SendIcon className="h-4 w-4" />
    </button>
  );
}

export const Composer = { Frame, Attach, Input, Submit };
```

## 5.5 Messages — explicit variants (full files)

`src/components/chat/CitationChip.tsx`:

```tsx
export function CitationChip({ page }: { page: number }) {
  return (
    <span className="inline-flex items-center rounded bg-active px-1.5 py-0.5 align-baseline text-xs font-medium text-slate">
      p.&nbsp;{page}
    </span>
  );
}
```

`src/components/chat/UserMessage.tsx`:

```tsx
export function UserMessage({ text }: { text: string }) {
  return (
    <div className="message-item flex justify-end">
      <div className="max-w-[70%] rounded-2xl rounded-br-md bg-slate px-4 py-2.5 text-[0.95rem] leading-relaxed text-white">
        {text}
      </div>
    </div>
  );
}
```

`src/components/chat/AssistantMessage.tsx`:

```tsx
import type { ChatMessage } from "@/lib/types";
import { FileIcon } from "@/components/icons";
import { CitationChip } from "./CitationChip";

interface AssistantMessageProps {
  message?: ChatMessage;
  pending?: boolean;
}

export function AssistantMessage({ message, pending = false }: AssistantMessageProps) {
  return (
    <div className="message-item flex gap-3">
      <div className="flex h-[30px] w-[30px] shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-slate to-navy">
        <FileIcon className="h-3.5 w-3.5 text-white" />
      </div>
      <div className="min-w-0 flex-1 rounded-2xl bg-[#f5f7fa] px-4 py-3 text-[0.95rem] leading-relaxed text-navy">
        {pending ? (
          <span className="blinking-cursor" aria-label="Assistant is responding">
            ▍
          </span>
        ) : (
          <>
            <span>{message?.text}</span>
            {message?.citations && message.citations.length > 0 && (
              <span className="ml-2 inline-flex gap-1">
                {message.citations.slice(0, 4).map((c, i) => (
                  <CitationChip key={`${message.id}-cite-${i}`} page={c.page} />
                ))}
              </span>
            )}
          </>
        )}
      </div>
    </div>
  );
}
```

## 5.6 `MessageList` — `src/components/chat/MessageList.tsx` (full file)

```tsx
"use client";

import { useEffect, useRef } from "react";
import { useChat } from "./chat-context";
import { AssistantMessage } from "./AssistantMessage";
import { UserMessage } from "./UserMessage";

export function MessageList() {
  const { state } = useChat();
  const containerRef = useRef<HTMLDivElement>(null);
  const isAtBottom = useRef(true);

  useEffect(() => {
    const el = containerRef.current;
    if (el && isAtBottom.current) {
      el.scrollTop = el.scrollHeight;
    }
  }, [state.messages.length, state.isSending]);

  return (
    <div
      ref={containerRef}
      onScroll={(e) => {
        const el = e.currentTarget;
        isAtBottom.current = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
      }}
      className="mx-auto w-full max-w-[760px] flex-1 space-y-5 overflow-y-auto px-6 py-6"
    >
      {messagesEmpty(state) ? (
        <div className="flex h-full items-center justify-center text-sm text-bluegray">
          Ask anything about your documents
        </div>
      ) : (
        <>
          {state.messages.map((message) =>
            message.role === "user" ? (
              <UserMessage key={message.id} text={message.text} />
            ) : (
              <AssistantMessage key={message.id} message={message} />
            ),
          )}
          {state.isSending && <AssistantMessage pending />}
        </>
      )}
    </div>
  );
}

function messagesEmpty(state: { messages: unknown[] }) {
  return state.messages.length === 0;
}
```

(The `onScroll` listener is React's synthetic handler — passive by default for scroll in React 19. Auto-scroll only fires when the user hasn't scrolled up.)

## 5.7 `ChatHeader` — `src/components/chat/ChatHeader.tsx` (full file)

```tsx
import { FileIcon } from "@/components/icons";

export function ChatHeader({ title }: { title: string }) {
  return (
    <header className="flex items-center gap-3 border-b border-line bg-white px-6 py-4">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-chip bg-gradient-to-br from-slate to-navy">
        <FileIcon className="h-4 w-4 text-white" />
      </div>
      <div className="min-w-0">
        <h1 className="truncate text-[1.05rem] font-bold text-navy">{title}</h1>
        <p className="text-xs text-muted">DocuMind</p>
      </div>
      <span className="ml-auto shrink-0 rounded-full bg-active px-3 py-1 text-xs font-semibold text-slate">
        DocuMind
      </span>
    </header>
  );
}
```

## 5.8 `ChatView` — `src/components/chat/ChatView.tsx` (full file)

```tsx
"use client";

import type { ReactNode } from "react";
import { ChatHeader } from "./ChatHeader";
import { ChatProvider } from "./ChatProvider";
import { Composer } from "./Composer";
import { MessageList } from "./MessageList";

interface ChatViewProps {
  title: string;
  filename?: string;
  headerExtra?: ReactNode;
}

export function ChatView({ title, filename, headerExtra }: ChatViewProps) {
  return (
    <ChatProvider filename={filename}>
      <div className="flex h-screen flex-col">
        <ChatHeader title={title}>
          {headerExtra}
        </ChatHeader>
        <MessageList />
        <div className="border-t border-line bg-white px-6 py-4">
          <div className="mx-auto max-w-[760px]">
            <Composer.Frame>
              <Composer.Attach />
              <Composer.Input />
              <Composer.Submit />
            </Composer.Frame>
            <p className="mt-2 text-center text-xs text-bluegray">
              DocuMind answers cite page numbers from {title}.
            </p>
          </div>
        </div>
      </div>
    </ChatProvider>
  );
}
```

`ChatHeader` takes children for the right-side pill — adjust it by replacing the static `<span>` with `{children}`:

```tsx
import type { ReactNode } from "react";
import { FileIcon } from "@/components/icons";

export function ChatHeader({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <header className="flex items-center gap-3 border-b border-line bg-white px-6 py-4">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-chip bg-gradient-to-br from-slate to-navy">
        <FileIcon className="h-4 w-4 text-white" />
      </div>
      <div className="min-w-0">
        <h1 className="truncate text-[1.05rem] font-bold text-navy">{title}</h1>
        <p className="text-xs text-muted">DocuMind</p>
      </div>
      {children && <div className="ml-auto shrink-0">{children}</div>}
    </header>
  );
}
```

## 5.9 Pages (full files)

`src/app/chats/page.tsx` — replace the stub:

```tsx
import { ChatView } from "@/components/chat/ChatView";

export const metadata = { title: "Chats — DocuMind" };

export default function ChatsPage() {
  return <ChatView title="All Documents" />;
}
```

`src/app/chats/[filename]/page.tsx`:

```tsx
import { ChatView } from "@/components/chat/ChatView";

export default async function ScopedChatPage({
  params,
}: {
  params: Promise<{ filename: string }>;
}) {
  const { filename } = await params;
  const decoded = decodeURIComponent(filename);
  return <ChatView title={decoded} filename={decoded} />;
}
```

## Acceptance criteria

- [ ] `/chats` and `/chats/Quarterly%20Report%20Q3.pdf` both render fullscreen (no sidebar)
- [ ] Asking a question shows: optimistic user bubble → pending block with blinking `▍` → answer with `p. N` chips (verify against the real backend)
- [ ] Send button disabled while empty or sending; error produces an inline assistant error message
- [ ] List auto-scrolls on new messages, but not after you scroll up
- [ ] `Composer.Input` holds no local state; everything flows through `useChat()`
- [ ] Follows the fullscreen chat layout described here
