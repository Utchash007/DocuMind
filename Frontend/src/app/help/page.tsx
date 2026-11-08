import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, BookOpenText, FileUp, MessageCircle, NotebookPen } from "lucide-react";
import { Brand } from "@/components/brand";
import { SiteFooter } from "@/components/site-footer";
import { ThemeMenu } from "@/components/theme-menu";
import { Button } from "@/components/ui/button";

export const metadata: Metadata = { title: "Help & getting started" };

const steps = [
  { icon: NotebookPen, title: "Create a notebook", text: "Give your project a name. Each notebook keeps its own sources, conversation, and saved notes." },
  { icon: FileUp, title: "Bring your sources", text: "Upload PDFs with selectable text, or choose PDFs already available on this API. Wait for indexing to finish before asking questions." },
  { icon: MessageCircle, title: "Ask, explore, and keep", text: "Ask a question or use a suggested prompt. Open page citations to check the original PDF, and save useful answers as editable notes." },
];

export default function HelpPage() {
  return (
    <div className="flex min-h-dvh flex-col">
      <header className="flex h-[76px] items-center justify-between border-b px-6 sm:px-10"><Brand /><ThemeMenu /></header>
      <main id="main-content" className="mx-auto w-full max-w-3xl flex-1 px-6 py-12 sm:py-16">
        <Button asChild variant="ghost" size="sm" className="mb-8 -ml-2 text-muted-foreground"><Link href="/"><ArrowLeft />Back to notebooks</Link></Button>
        <BookOpenText className="mb-4 size-8 text-muted-foreground" />
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Make room for understanding.</h1>
        <p className="mt-4 text-base leading-7 text-muted-foreground">NoteMind brings your documents, questions, and ideas into one focused workspace.</p>
        <div className="my-10 grid gap-4">
          {steps.map(({ icon: Icon, title, text }, index) => <section key={title} className="flex gap-4 rounded-xl border bg-card p-5"><span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-secondary"><Icon className="size-5" /></span><div><h2 className="font-medium">{index + 1}. {title}</h2><p className="mt-1.5 text-sm leading-6 text-muted-foreground">{text}</p></div></section>)}
        </div>
        <section id="sign-in" className="scroll-mt-8 border-t py-8"><h2 className="text-lg font-semibold">Sign in with an email code</h2><p className="mt-3 text-sm leading-7 text-muted-foreground">Sign-in is required to use your notebooks. On the <Link href="/sign-in" className="underline underline-offset-2">welcome screen</Link>, enter your email to receive a six-digit sign-in code from Appwrite. Enter the code within 15 minutes. If it doesn’t arrive, check your spam folder and use Resend code after the countdown. Appwrite creates an account when you request a code for a new email address. Use the account menu to sign out; you’ll need to sign in again to reopen the workspace.</p><p className="mt-3 text-sm leading-7 text-muted-foreground">If email sign-in is not configured, set <code>NEXT_PUBLIC_APPWRITE_ENDPOINT</code> and <code>NEXT_PUBLIC_APPWRITE_PROJECT_ID</code> in the frontend environment, register the website hostname in Appwrite, and enable Email OTP in the project’s Auth settings.</p></section>
        <section id="privacy" className="scroll-mt-8 border-t py-8"><h2 className="text-lg font-semibold">Privacy & your data</h2><div className="mt-3 space-y-3 text-sm leading-7 text-muted-foreground"><p>Notebook titles, conversations, and notes are saved in this browser’s local storage and are available in the workspace after signing in. The workspace is shared by signed-in people using this browser profile; signing out does not remove it or assign it to an account. Notebooks do not sync to other devices. Clearing browser data removes them; use Share in a notebook to export a Markdown copy.</p><p>Appwrite manages your email address and sign-in session. Its browser SDK persists the session with a cookie, using browser storage as a fallback.</p><p>PDFs are uploaded to the configured DocuMind backend. Extracted text is indexed in Chroma and processed by the configured embedding and answer providers. Uploaded filenames are shared by this API deployment, and uploading the same filename replaces that source.</p><p>Removing a source or notebook removes its local organization. It does not delete the original PDF from the backend.</p></div></section>
        <section id="terms" className="scroll-mt-8 border-t py-8"><h2 className="text-lg font-semibold">About this preview</h2><p className="mt-3 text-sm leading-7 text-muted-foreground">This version provides a browser-local research workspace with required Appwrite email-code sign-in. Billing and collaborative notebook sharing are not enabled. Generated answers can be incomplete or incorrect; check the cited passages in your original documents.</p></section>
        <section className="border-t py-8"><h2 className="text-lg font-semibold">Having trouble connecting?</h2><p className="mt-3 text-sm leading-7 text-muted-foreground">Start the FastAPI backend and check the frontend’s <code className="rounded bg-muted px-1.5 py-0.5 text-xs">BACKEND_URL</code> setting. Uploads need Chroma and embedding access; answering also needs a Groq API key. Scanned PDFs need text recognition before they can be used here.</p></section>
      </main>
      <SiteFooter />
    </div>
  );
}
