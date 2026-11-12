import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, BookOpenText, FileUp, MessageCircle, NotebookPen } from "lucide-react";
import { Brand } from "@/components/brand";
import { SiteFooter } from "@/components/site-footer";
import { ThemeMenu } from "@/components/theme-menu";
import { Button } from "@/components/ui/button";

export const metadata: Metadata = { title: "Help & getting started" };

const steps = [
  { icon: NotebookPen, title: "Create a project", text: "Sign in, complete your profile, and give your project a name. Each project keeps its own sources and conversations." },
  { icon: FileUp, title: "Bring your sources", text: "Upload PDFs with selectable text, up to 25 MiB and 200 pages. Wait for background processing to finish before asking questions." },
  { icon: MessageCircle, title: "Ask, explore, and keep", text: "Ask a question or use a suggested prompt. Open page citations to check the original PDF, and save useful answers as editable notes." },
];

export default function HelpPage() {
  return (
    <div className="flex min-h-dvh flex-col">
      <header className="flex h-[76px] items-center justify-between border-b px-6 sm:px-10"><Brand /><ThemeMenu /></header>
      <main id="main-content" className="mx-auto w-full max-w-3xl flex-1 px-6 py-12 sm:py-16">
        <Button asChild variant="ghost" size="sm" className="mb-8 -ml-2 text-muted-foreground"><Link href="/"><ArrowLeft />Back to projects</Link></Button>
        <BookOpenText className="mb-4 size-8 text-muted-foreground" />
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Make room for understanding.</h1>
        <p className="mt-4 text-base leading-7 text-muted-foreground">DocuMind brings your documents, questions, and ideas into one focused workspace.</p>
        <div className="my-10 grid gap-4">
          {steps.map(({ icon: Icon, title, text }, index) => <section key={title} className="flex gap-4 rounded-xl border bg-card p-5"><span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-secondary"><Icon className="size-5" /></span><div><h2 className="font-medium">{index + 1}. {title}</h2><p className="mt-1.5 text-sm leading-6 text-muted-foreground">{text}</p></div></section>)}
        </div>
        <section id="sign-in" className="scroll-mt-8 border-t py-8"><h2 className="text-lg font-semibold">Sign in with an email code</h2><p className="mt-3 text-sm leading-7 text-muted-foreground">On the <Link href="/sign-in" className="underline underline-offset-2">welcome screen</Link>, enter your email to receive a six-digit Appwrite code. Enter it before the displayed expiry. If it doesn’t arrive, check spam and use Resend after the countdown. New emails create accounts. Complete your name and date of birth on the profile screen before opening projects. Use the account menu to sign out.</p><p className="mt-3 text-sm leading-7 text-muted-foreground">Setup requires server-only <code>APPWRITE_ENDPOINT</code>, <code>APPWRITE_PROJECT_ID</code>, and <code>APPWRITE_API_KEY</code> in the Next.js environment, matching the backend project. Register the website hostname and enable Email OTP. Never expose API keys with a <code>NEXT_PUBLIC_</code> prefix.</p></section>
        <section id="privacy" className="scroll-mt-8 border-t py-8"><h2 className="text-lg font-semibold">Privacy & your data</h2><div className="mt-3 space-y-3 text-sm leading-7 text-muted-foreground"><p>Projects and conversations are stored on the server for your account. Editable notes stay on this device in account-scoped browser storage and do not sync. Signing out clears the visible workspace, not saved server data or local notes. Clearing browser data removes local notes; use Share to export a Markdown copy.</p><p>Appwrite manages accounts and sessions. Next.js keeps the session secret in an HttpOnly cookie and forwards short-lived tokens to the backend, which checks account ownership.</p><p>Original PDFs live in private Appwrite Storage. Extracted text is indexed in Chroma and processed by the configured embedding and answer providers. Filenames are labels, not shared document identities.</p><p>Deleting a project or source hides it and queues PDF/index cleanup. Answers cite verified document IDs, index versions, and pages.</p></div></section>
        <section id="terms" className="scroll-mt-8 border-t py-8"><h2 className="text-lg font-semibold">About this preview</h2><p className="mt-3 text-sm leading-7 text-muted-foreground">This preview provides account-owned research projects with required email-code sign-in. Billing and collaborative sharing are not enabled. Generated answers can be incomplete or incorrect; check cited passages in the original PDFs. Cancelled questions are not retryable; submit a new question.</p></section>
        <section className="border-t py-8"><h2 className="text-lg font-semibold">Having trouble connecting?</h2><p className="mt-3 text-sm leading-7 text-muted-foreground">Start FastAPI and the PDF worker, verify PostgreSQL migrations, and check the frontend’s <code className="rounded bg-muted px-1.5 py-0.5 text-xs">BACKEND_URL</code>. Uploads require private storage, Chroma, and embeddings; answering also requires Groq. Scanned PDFs need text recognition before upload. A healthy liveness response does not prove provider connectivity.</p></section>
      </main>
      <SiteFooter />
    </div>
  );
}
