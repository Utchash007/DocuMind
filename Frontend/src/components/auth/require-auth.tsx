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
  const incomplete = authenticated && state.appUser !== null && !state.appUser.onboardingCompleted;

  useEffect(() => {
    if (state.loading) return;
    if (!authenticated) {
      router.replace("/sign-in");
    } else if (incomplete && pathname !== "/onboarding") {
      router.replace("/onboarding");
    } else if (!incomplete && pathname === "/onboarding") {
      router.replace("/");
    }
  }, [authenticated, incomplete, state.loading, pathname, router]);

  if (state.loading || !authenticated) {
    return <main id="main-content" className="flex min-h-dvh items-center justify-center px-6"><p role="status" className="flex items-center gap-2 text-sm text-muted-foreground"><Loader2 className="size-4 animate-spin" />{state.loading ? "Checking your session..." : "Redirecting to sign in..."}</p></main>;
  }

  if (incomplete && pathname !== "/onboarding") {
    return <main id="main-content" className="flex min-h-dvh items-center justify-center px-6"><p role="status" className="flex items-center gap-2 text-sm text-muted-foreground"><Loader2 className="size-4 animate-spin" />Completing your profile...</p></main>;
  }

  return children;
}
