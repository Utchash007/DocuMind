# NoteMind frontend

A browser-local research workspace for the DocuMind PDF API, with required Appwrite email-code sign-in. Built with Next.js 16 App Router, React 19, TypeScript, Tailwind CSS 4, shadcn/ui, and Zustand.

The interface follows [`notemind-ux-wireframe.md`](../notemind-ux-wireframe.md) and the [Chalk theme from tweakcn](https://tweakcn.com/r/themes/cmmjgn9pc000404lg7c2q0fl6), with light, dark, and system appearance settings.

## Run locally

Start the [FastAPI backend](../README.md#2-backend-setup-fastapi) in a separate terminal. Run these commands from `Frontend/`:

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
| `NEXT_PUBLIC_APPWRITE_ENDPOINT` | Unset | Appwrite API endpoint from project settings, including `/v1` |
| `NEXT_PUBLIC_APPWRITE_PROJECT_ID` | Unset | Appwrite project ID; required with the endpoint to enable email sign-in |

The default setup sends browser requests through `/api/backend`, including multipart uploads and PDF previews. Keep Chroma, Groq, and Hugging Face credentials in the backend's repository-root `.env`.

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
   NEXT_PUBLIC_APPWRITE_ENDPOINT=https://<REGION>.cloud.appwrite.io/v1
   NEXT_PUBLIC_APPWRITE_PROJECT_ID=your-project-id
   ```

4. Restart the development server, or rebuild for production. These two public settings are compiled into the browser bundle. This browser flow requires no Appwrite API key.
5. At `/sign-in`, enter an email, click **Send sign-in code**, then enter the six-digit code from your inbox. Use the account menu in the library or notebook sidebar to sign out.

The frontend uses `account.createEmailToken({ userId: ID.unique(), email, phrase: false })`, followed by `account.createSession({ userId: token.userId, secret: code })`. Appwrite creates an account when a new email requests a code; existing emails use the user ID returned by Appwrite. Codes expire after 15 minutes. The UI supports resend after 60 seconds, changing the email, and invalid/expired-code and rate-limit errors. Appwrite enforces its server-side limits.

Appwrite Cloud supplies email delivery out of the box. Self-hosted Appwrite needs working SMTP configuration; custom email content is managed in Appwrite’s email templates. See [Email OTP](https://appwrite.io/docs/products/auth/email-otp) and [message templates](https://appwrite.io/docs/products/auth/message-templates).

The Web SDK manages session cookies and its localStorage fallback. `AuthProvider` checks `account.get()` on startup and when the browser window regains focus. Only accounts with an email can open the workspace. Sign-out deletes the current Appwrite session and returns to sign-in. Code entry and pending challenge metadata stay in memory; reloading during verification starts the email step again. If the endpoint or project ID is missing, the welcome screen links to sign-in setup and keeps workspace access closed.

`RequireAuth` gates the library and notebook routes while sessions are loading, missing, or unavailable. The workspace restores browser data and starts PDF API requests only after authentication succeeds. Sign-out, session expiry, and failed session checks close the workspace and cancel pending questions and uploads. Retry session lookup from the sign-in page when Appwrite is temporarily unavailable.

## Screens and interactions

| Route | Features |
| --- | --- |
| `/sign-in` | Email-code sign-in, resend/change-email, and session recovery |
| `/` | Sign-in required; notebook creation, search (`Ctrl/Cmd + K`), sorting, renaming, and deletion |
| `/notebooks/[id]` | Sign-in required; notebook-scoped PDF sources, chat, citations, editable notes, guides, and Markdown export |
| `/help` | Getting started, storage/privacy information, and connection troubleshooting |

- Upload PDFs with extractable text, or attach existing PDFs from the connected backend.
- Uploads show per-file progress/errors and can continue while navigating between notebooks in the app.
- Questions use only the current notebook's sources. Enter sends; Shift + Enter inserts a newline.
- Answers arrive as complete responses. Pending requests can be stopped or retried.
- Citation chips show the supporting passage and open the source PDF at its one-based page number.
- Save answers as notes, write your own notes, and edit Markdown with a preview.
- Generate an overview, FAQ, or study guide in the notebook conversation.
- **Share** copies or downloads a Markdown export containing sources, notes, conversations, and citations.
- Desktop sidebars collapse; narrow screens use a navigation drawer.

## Workspace storage and authentication scope

Notebook metadata, conversations, notes, and retry state are saved in `localStorage` under `notemind-workspace` (version 1). A reload restores that workspace. Interrupted questions offer a retry, and storage failures are displayed in the UI.

Workspace data belongs to this browser and origin and becomes accessible in the workspace after sign-in. The same local workspace is preserved across account changes and sign-out; it is not account-scoped or synced across devices. Clearing browser data removes it. Export important research using **Share**. PDFs themselves remain on the configured backend, and filenames identify shared sources on that API deployment. Uploading a matching filename replaces that source; removing a notebook or source association affects the browser workspace only.

Appwrite authentication is required for the frontend workspace. The FastAPI API/proxy does not verify Appwrite sessions or isolate PDFs by user; the frontend route gate is not server-side API authorization. Billing, collaborative links, and non-PDF uploads are outside this implementation. Markdown exports do not embed the original PDFs.

## Code map

| Path | Responsibility |
| --- | --- |
| `src/app/(main)/` | Library and notebook routes |
| `src/app/api/backend/[...path]/route.ts` | Allowlisted FastAPI proxy, PDF range requests, timeouts, and HTTP error forwarding |
| `src/components/auth/email-sign-in-form.tsx` | Email/code forms, resend countdown, expiry, errors, and success navigation |
| `src/components/auth/require-auth.tsx` | Workspace route gate, session-loading state, and sign-in redirects |
| `src/components/providers/auth-provider.tsx` | Account session restoration, sign-in, sign-out, and shared account state |
| `src/components/account-menu.tsx` | Signed-in library/sidebar account identity and sign-out |
| `src/components/library/` | Library controls and notebook cards |
| `src/components/notebooks/` | Workspace shell, sidebar, shared UI state, and dialogs |
| `src/components/chat/` | Composer, Markdown answers, actions, and citations |
| `src/components/documents/` | PDF upload and existing-source selection |
| `src/components/ui/` | shadcn/ui primitives |
| `src/store/` | Notebook, document, and chat slices plus validated persistence |
| `src/services/` | Typed PDF API requests and Appwrite browser account operations |
| `src/lib/types.ts` | Auth, notebook, chat, note, and API data shapes |
| `src/app/globals.css` | Chalk tokens, local shadcn state variants, and shared styling |

The checked-in shadcn components use local CSS state variants and `tw-animate-css`. The frontend builds independently of the repository-root shadcn CLI tooling.

Next.js and `eslint-config-next` are pinned to the same version. The scoped `minimatch` override supplies the patched release for TypeScript lint tooling while preserving older consumers' APIs. Review `npm audit` findings and apply targeted dependency updates; `npm audit fix --force` can downgrade packages across major versions and break these integrations.

Queries use form field `query`, plus `filename` for one source or repeated `filenames` for multiple sources. The client rejects empty notebook queries. See the [API contract](../README.md#api-contract) for response shapes.

## Verification

From `Frontend/`:

```powershell
npx next typegen
npm run lint
npx tsc --noEmit --incremental false
npm run build
npx playwright install chromium
npm run test:e2e
```

The Playwright suite builds and starts the production frontend on port `3011` and an isolated FastAPI fixture on `8011`. It supplies the default `/api/backend` base and a local test-only Appwrite endpoint/project during that build. `e2e/appwrite.ts` intercepts account requests and simulates email tokens and HTTP-only session cookies; no emails are sent. The test build replaces `.next`, so run `npm run build` with your deployment environment before serving a normal production build.

PDF tests exercise real multipart uploads, PDF parsing, retrieval scoping, the proxy, and PDF serving, with deterministic in-memory Chroma, embedding, and Groq substitutes. Backend dependencies must be installed; the runner uses `Backend/.venv` when available, or the executable set by `PYTHON`.

Browser checks cover required sign-in for direct and history navigation, deferred workspace initialization, rejected anonymous accounts, pending-request cancellation on sign-out, email-code requests/verification, leading-zero codes, invalid/expired codes, resend, email changes, rate limits, account lookup recovery, cookie persistence, sign-out failures, and session expiry on refocus. They also cover desktop/mobile signed-in navigation, notebook CRUD, multi-source questions, citations, note editing, reload persistence, exports, background uploads, retry/stop, upload errors, storage failures, and keyboard focus. Screenshots and failure traces are written to ignored `test-results/`.

From `Backend/`, focused API and citation checks use Python's standard test runner:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

These checks use temporary PDFs and provider substitutes. Live Appwrite delivery/cookies require a configured project; live PDF-provider connectivity and semantic answer quality require a separately configured backend.
