"use client";

import Link from "next/link";
import { RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function ErrorPage({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return <main id="main-content" className="flex min-h-dvh flex-col items-center justify-center px-6 text-center"><h1 className="text-2xl font-semibold tracking-tight">Something interrupted your workspace.</h1><p className="mt-3 text-sm text-muted-foreground">Try loading the page again to continue.</p><div className="mt-6 flex gap-3"><Button onClick={reset}><RotateCcw />Try again</Button><Button variant="outline" asChild><Link href="/">Back to projects</Link></Button></div></main>;
}
