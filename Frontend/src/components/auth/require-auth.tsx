"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/components/providers/auth-provider";

export function RequireAuth({ children }: { children: ReactNode }) {
  const { state } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const authenticated = Boolean(state.user) && !state.error;

  useEffect(() => {
    if (!state.loading && !authenticated) router.replace("/sign-in");
  }, [authenticated, state.loading, pathname, router]);

  if (state.loading || !authenticated) {
    return <main id="main-content" className="flex min-h-dvh items-center justify-center px-6"><p role="status" className="flex items-center gap-2 text-sm text-muted-foreground"><Loader2 className="size-4 animate-spin" />{state.loading ? "Checking your session..." : "Redirecting to sign in..."}</p></main>;
  }

  return children;
}
