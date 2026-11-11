# NoteMind frontend

An account-owned project research workspace for DocuMind v2, with Appwrite email-code sign-in and profile onboarding. Built with Next.js 16 App Router, React 19, TypeScript, Tailwind CSS 4, shadcn/ui, and Zustand. Only editable notes are browser-local; projects, PDF metadata, and conversations persist in PostgreSQL.

The interface uses the [Chalk theme from tweakcn](https://tweakcn.com/r/themes/cmmjgn9pc000404lg7c2q0fl6), with light, dark, and system appearance settings. Theme tokens and shared styles live in [`src/app/globals.css`](src/app/globals.css).

## Run locally

Start the [FastAPI backend and PDF worker](../docs/getting-started.md#4-start-the-api-worker-and-frontend) in separate terminals, with a migrated application database. Run these commands from `Frontend/`:

```powershell
npm install
if (-not (Test-Path .env.local)) { Copy-Item .env.example .env.local }
npm run dev
```

If `.env.local` already exists, merge the settings rather than replacing it. Configure Appwrite below, then open [localhost:3000/sign-in](http://localhost:3000/sign-in) to sign in with an email code. The library at [localhost:3000](http://localhost:3000) requires an authenticated account.

### Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `BACKEND_URL` | `http://127.0.0.1:8000` | Server-only FastAPI origin used by the Next.js proxy |
| `NEXT_PUBLIC_API_BASE_URL` | `/api/backend` | Browser API base URL; compiled into the frontend at build time |
| `APPWRITE_ENDPOINT` | Public fallback, then cloud endpoint | Server-side Appwrite API endpoint, including `/v1` |
| `APPWRITE_PROJECT_ID` | Public fallback | Server Appwrite project ID, matching FastAPI |
| `APPWRITE_API_KEY` | Unset, required | Server-only auth key for session secrets; never exposed to the browser |
| `NEXT_PUBLIC_APPWRITE_ENDPOINT` / `NEXT_PUBLIC_APPWRITE_PROJECT_ID` | Unset | Optional public fallback settings; server-only values take precedence |

The default setup sends browser requests through `/api/backend`, including multipart uploads and PDF previews. Keep Chroma, Groq, and embedding-provider credentials in the backend's repository-root `.env`.

For production:

```powershell
npm run build
npm run start
```

### Appwrite email-code authentication

1. Create or select an Appwrite project and enable **Email OTP** in its Auth settings.
2. Add a **Web** platform for `localhost`. Also register `127.0.0.1` if you use it, and your deployed website hostname.
3. Copy the API endpoint and project ID from the project settings into `Frontend/.env.local`:

   ```env
    APPWRITE_ENDPOINT=https://<REGION>.cloud.appwrite.io/v1
    APPWRITE_PROJECT_ID=your-project-id
    APPWRITE_API_KEY=your-server-auth-key
   ```

4. Restart the development server, or rebuild for production. Configure an auth API key for the Next.js server; keep it server-only. FastAPI/worker also need their backend Appwrite settings and a private PDF bucket. Public fallback changes require rebuilding.
5. At `/sign-in`, enter an email, click **Send sign-in code**, then enter the six-digit code from your inbox. Use the account menu in the dashboard or project sidebar to sign out.

The browser always restores `/api/auth/session` and sends email-code requests through the Next.js auth routes. Those routes validate the server configuration and return retryable errors when unavailable; public Appwrite variables are optional and do not gate the sign-in form.

The browser calls `/api/auth/otp/request` and `/api/auth/otp/verify`. Next.js uses server-side `node-appwrite` for email tokens and session creation, retaining the user ID returned by Appwrite and its expiry. The UI supports six-digit codes, a 60-second resend countdown, changing email, and rate-limit/delivery errors. New emails create Appwrite accounts. Authentication secrets never appear in safe browser DTOs.

Appwrite Cloud supplies email delivery out of the box. Self-hosted Appwrite needs working SMTP configuration; custom email content is managed in Appwrite’s email templates. See [Email OTP](https://appwrite.io/docs/products/auth/email-otp) and [message templates](https://appwrite.io/docs/products/auth/message-templates).

Next.js stores the session secret in a host-only HttpOnly, SameSite cookie (`Secure` on HTTPS); JavaScript cannot read it. `AuthProvider` checks `/api/auth/session` on startup and refocus. Session-bound server clients mint short-lived JWTs, which the backend proxy forwards to FastAPI for identity and ownership verification. Browser-supplied authorization/owner headers are not trusted. Missing configuration and verification outages fail closed; session lookup can be retried without consuming another code.

`src/proxy.ts` is an optimistic cookie-presence route gate, not authoritative authorization. `RequireAuth` and the session/backend checks enforce verified access and onboarding. `/onboarding` collects name and date of birth. Sign-out, session expiry, or account changes clear visible workspace data, abort requests/polls, and ignore late responses. Auth/proxy mutations enforce same-origin requests. In-process OTP throttling is not a distributed rate limiter; configure production ingress accordingly.

## Screens and interactions

| Route | Features |
| --- | --- |
| `/sign-in` | Email-code sign-in, resend/change-email, and session recovery |
| `/onboarding` | Required name/date-of-birth profile completion |
| `/` | Account project dashboard; creation, search (`Ctrl/Cmd + K`), sorting, renaming, and deletion |
| `/projects/[projectId]` | Project sources, processing status, conversations, notes, and export |
| `/projects/[projectId]/conversations/[conversationId]` | Persisted conversation, retry/cancel, and citations |
| `/notes` | Account-scoped on-device notes |
| `/help` | Getting started, storage/privacy information, and connection troubleshooting |

- Upload PDFs with extractable text, up to 25 MiB and 200 pages. There is no global shared-file picker.
- Uploads show per-file progress/errors and can continue while navigating between projects in the app.
- Questions use only ready documents owned by the current project. Enter sends; Shift + Enter inserts a newline.
- Answers arrive as complete JSON turns. Retry only the latest failed or expired-active user turn. Cancelled turns require a new question.
- Citation chips show the supporting passage and open the source PDF at its one-based page number.
- Save answers as notes, write your own notes, and edit Markdown with a preview.
- Generate an overview, FAQ, or study guide in the project conversation.
- **Share** copies or downloads a Markdown export containing sources, notes, conversations, and citations.
- Desktop sidebars collapse; narrow screens use a navigation drawer.

## Workspace storage and authentication scope

PostgreSQL owns project/document metadata, conversations/messages, and durable processing jobs. Private PDFs live in Appwrite Storage; published chunks live in `documind_chunks_v2`. Reloads re-fetch canonical data. An upload's `202 {document, job}` means accepted, not ready to answer; the worker must publish a completed index first.

Only notes/drafts use account-scoped localStorage; clearing browser data removes them, not server projects. Notes do not sync across devices. Sign-out preserves saved data but clears active state; another account cannot see the previous account's notes. Use **Share** for complete Markdown exports (all message pages plus local notes, without embedded PDFs). Same filenames can identify distinct v2 documents; deletion queues storage/index cleanup.

V1 APIs, browser-data import, unresolved citation DTOs, and `/notebooks/[id]` compatibility routes are removed. `notemind-workspace` is not read or automatically deleted. Existing server data and external storage are not migrated or cleaned up by this removal. Billing, collaboration, OCR, and non-PDF uploads are not implemented.

## Code map

| Path | Responsibility |
| --- | --- |
| `src/app/(main)/` | Project/conversation and account-note routes |
| `src/app/api/auth/`, `src/lib/server/auth.ts` | Server OTP/session flow and session-bound JWTs |
| `src/lib/server/auth-config.ts`, `backend-routes.ts`, `src/proxy.ts` | Shared cookie/origin settings, exact resource/method/query allowlist, and route gate |
| `src/app/api/backend/[...path]/route.ts` | Allowlisted FastAPI proxy, PDF range requests, timeouts, and HTTP error forwarding |
| `src/components/auth/email-sign-in-form.tsx` | Email/code forms, resend countdown, expiry, errors, and success navigation |
| `src/components/auth/require-auth.tsx` | Workspace route gate, session-loading state, and sign-in redirects |
| `src/components/providers/auth-provider.tsx` | Account session restoration, sign-in, sign-out, and shared account state |
| `src/components/account-menu.tsx` | Signed-in library/sidebar account identity and sign-out |
| `src/components/projects/` | Dashboard, project shell/provider, chat, dialogs, and loading skeleton |
| `src/components/chat/` | Composer, Markdown answers, actions, and citations |
| `src/components/documents/` | Project PDF upload and processing tasks |
| `src/components/ui/` | shadcn/ui primitives |
| `src/store/` | Projects, documents, conversations, account-local notes, identity reset, and request cancellation |
| `src/services/projects/`, `users/me.ts`, `v2http.ts` | Typed v2 API transport, uploads/polling, profile, and error parsing |
| `src/lib/api-types.ts` | Backend-aligned v2 DTOs; `types.ts` contains auth and liveness shapes |
| `src/app/globals.css` | Chalk tokens, local shadcn state variants, and shared styling |

The checked-in shadcn components use local CSS state variants and `tw-animate-css`. The frontend builds from its own `package.json` and `package-lock.json`.

Next.js and `eslint-config-next` are pinned to the same version. The scoped `minimatch` override supplies the patched release for TypeScript lint tooling while preserving older consumers' APIs. Review `npm audit` findings and apply targeted dependency updates; `npm audit fix --force` can downgrade packages across major versions and break these integrations.

Messages use JSON `content` and UUID `clientRequestId`, never filename selection. Cancellation resolves an optimistic request's persisted message ID, keeps new sends blocked while settling, and uses the server outcome rather than inventing cancelled state. See [the API contract](../docs/v2-contracts.md). The proxy preserves ranges/idempotency keys and buffers up to 26 MiB for 25 MiB multipart uploads.

## Verification

From `Frontend/`:

```powershell
npx next typegen
npm run lint
npm run build
npx tsc --noEmit --incremental false
```

Project unit/browser tests, fixtures, both Playwright configurations, test output, and `test:unit`/`test:e2e` scripts were removed by request on 2026-11-11. The direct `@playwright/test` development dependency was also removed. The commands above are the current static checks.

Earlier test results and outstanding live verification are recorded in [the acceptance matrix](../docs/acceptance-matrix.md#current-integration-status). Live Appwrite delivery/cookies and PDF-provider connectivity/answer quality require a configured backend. Backend implementation details are in the [mirrored Python reference](../docs/backend/README.md).
