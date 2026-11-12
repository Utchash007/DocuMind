import Link from "next/link";
import { BookOpenText } from "lucide-react";
import { cn } from "@/lib/utils";

export function BrandMark({ className }: { className?: string }) {
  return (
    <span aria-hidden="true" className={cn("inline-flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-xs", className)}>
      <BookOpenText className="size-[55%]" strokeWidth={1.65} />
    </span>
  );
}

export function Brand({ className }: { className?: string }) {
  return (
    <Link href="/" aria-label="DocuMind project library" className={cn("inline-flex w-fit shrink-0 items-center gap-2.5 rounded-lg", className)}>
      <BrandMark />
      <span className="text-xl font-semibold tracking-[-0.055em]">DocuMind<span className="text-muted-foreground">.</span></span>
    </Link>
  );
}
