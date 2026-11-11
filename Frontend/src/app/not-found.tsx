import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { BrandMark } from "@/components/brand";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return <main id="main-content" className="flex min-h-dvh flex-col items-center justify-center px-6 text-center"><BrandMark className="mb-6 size-12" /><p className="text-xs font-medium tracking-widest text-muted-foreground">PAGE NOT FOUND</p><h1 className="mt-3 text-3xl font-semibold tracking-tight">Let’s get you back to your ideas.</h1><p className="mt-3 text-sm text-muted-foreground">This page may have moved, or the link may be incomplete.</p><Button asChild className="mt-7 h-10"><Link href="/"><ArrowLeft />Back to projects</Link></Button></main>;
}
