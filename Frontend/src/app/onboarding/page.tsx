import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { OnboardingForm } from "@/components/auth/onboarding-form";
import { Brand, BrandMark } from "@/components/brand";
import { ThemeMenu } from "@/components/theme-menu";
import { Card } from "@/components/ui/card";
import { loadSessionContext, sessionCookieName, AppwriteError } from "@/lib/server/auth";

export const metadata: Metadata = { title: "Complete your profile" };

export default async function OnboardingPage() {
  const cookieStore = await cookies();
  const secret = cookieStore.get(sessionCookieName())?.value ?? null;
  let context = null;
  try {
    context = secret ? await loadSessionContext(secret) : null;
  } catch (error) {
    if (error instanceof AppwriteError && error.status === 401) context = null;
    else throw error;
  }
  if (!context) redirect("/sign-in");
  if (context.appUser.onboardingCompleted) redirect("/");

  return (
    <div className="flex min-h-dvh flex-col">
      <header className="flex items-center justify-between px-6 py-5 sm:px-10"><Brand /><ThemeMenu /></header>
      <main id="main-content" className="flex flex-1 flex-col items-center justify-center px-5 py-8 sm:py-12">
        <Card className="w-full max-w-[420px] gap-0 rounded-2xl p-7 shadow-sm sm:p-9">
          <div className="mb-7 text-center">
            <BrandMark className="mb-5 size-12 rounded-2xl" />
            <h1 className="text-[26px] font-semibold tracking-tight">Welcome to NoteMind</h1>
            <p className="mt-2 text-sm text-muted-foreground">One last step before your research workspace opens.</p>
          </div>
          <OnboardingForm appUser={context.appUser} />
          <p className="mt-6 text-center text-[11px] leading-relaxed text-muted-foreground">Learn about this preview in our <Link href="/help#terms" className="underline underline-offset-2">Terms</Link> and <Link href="/help#privacy" className="underline underline-offset-2">Privacy notes</Link>.</p>
        </Card>
        <p className="mt-6 text-xs text-muted-foreground">A little less searching. A little more understanding.</p>
      </main>
    </div>
  );
}
