import Link from "next/link";
import { FeedbackButton } from "@/components/feedback-button";

export function SiteFooter() {
  return (
    <footer className="mx-auto flex w-full max-w-6xl flex-col items-center justify-between gap-4 px-6 py-7 text-xs text-muted-foreground sm:flex-row lg:px-10">
      <nav aria-label="Footer" className="flex items-center gap-6">
        <Link href="/help#privacy" className="rounded-sm hover:text-foreground">Privacy</Link>
        <Link href="/help#terms" className="rounded-sm hover:text-foreground">Terms</Link>
        <Link href="/help" className="rounded-sm hover:text-foreground">Help</Link>
      </nav>
      <div className="flex items-center gap-3"><span>NoteMind © 2026</span><span aria-hidden="true">·</span><FeedbackButton /></div>
    </footer>
  );
}
