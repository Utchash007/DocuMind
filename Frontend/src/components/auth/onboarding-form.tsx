"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useRef, useState, type FormEvent } from "react";
import { ArrowRight, Loader2 } from "lucide-react";
import type { ApplicationUser } from "@/lib/api-types";
import { authErrorMessage, updateProfile } from "@/services/auth/auth";
import { useAuth } from "@/components/providers/auth-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

function todayIso() {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${now.getFullYear()}-${month}-${day}`;
}

export function OnboardingForm({ appUser }: { appUser: ApplicationUser }) {
  const { actions } = useAuth();
  const router = useRouter();
  const [name, setName] = useState(appUser.name ?? "");
  const [dateOfBirth, setDateOfBirth] = useState(appUser.dateOfBirth ?? "");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldError, setFieldError] = useState<{ name?: string; dateOfBirth?: string }>({});
  const nameRef = useRef<HTMLInputElement>(null);
  const dobRef = useRef<HTMLInputElement>(null);
  const today = todayIso();

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending) return;
    const nextErrors: { name?: string; dateOfBirth?: string } = {};
    if (!name.trim()) nextErrors.name = "Enter your name.";
    if (!dateOfBirth) nextErrors.dateOfBirth = "Enter your date of birth.";
    else if (dateOfBirth > today) nextErrors.dateOfBirth = "Date of birth cannot be in the future.";
    setFieldError(nextErrors);
    if (nextErrors.name) {
      nameRef.current?.focus();
      return;
    }
    if (nextErrors.dateOfBirth) {
      dobRef.current?.focus();
      return;
    }
    setPending(true);
    setError(null);
    try {
      const updated = await updateProfile(name.trim(), dateOfBirth);
      if (!updated.onboardingCompleted) throw new Error("Could not complete your profile. Please try again.");
      await actions.refreshSession();
      router.replace("/");
    } catch (cause) {
      setError(authErrorMessage(cause));
      nameRef.current?.focus();
    } finally {
      setPending(false);
    }
  }

  async function signOut() {
    if (pending) return;
    setPending(true);
    try {
      await actions.signOut();
      router.replace("/sign-in");
    } catch (cause) {
      setError(authErrorMessage(cause));
      setPending(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-4" aria-busy={pending}>
      <div className="text-center">
        <h2 className="font-medium">Complete your profile</h2>
        <p className="mt-2 text-xs leading-5 text-muted-foreground">
          Signed in as <span className="break-all font-medium text-foreground">{appUser.email}</span>. A name and date of birth are required to open your workspace.
        </p>
      </div>
      <div>
        <label htmlFor="onboarding-name" className="text-xs font-medium">Full name</label>
        <Input
          ref={nameRef}
          id="onboarding-name"
          name="name"
          type="text"
          autoComplete="name"
          maxLength={150}
          required
          value={name}
          onChange={(event) => { setName(event.target.value); setFieldError((current) => ({ ...current, name: undefined })); setError(null); }}
          readOnly={pending}
          aria-invalid={Boolean(fieldError.name)}
          aria-describedby={fieldError.name ? "onboarding-name-error" : undefined}
          placeholder="Ada Lovelace"
          className="mt-2 h-11"
        />
        {fieldError.name ? <p id="onboarding-name-error" role="alert" className="mt-1 text-xs text-destructive">{fieldError.name}</p> : null}
      </div>
      <div>
        <label htmlFor="onboarding-dob" className="text-xs font-medium">Date of birth</label>
        <Input
          ref={dobRef}
          id="onboarding-dob"
          name="dateOfBirth"
          type="date"
          autoComplete="bday"
          max={today}
          required
          value={dateOfBirth}
          onChange={(event) => { setDateOfBirth(event.target.value); setFieldError((current) => ({ ...current, dateOfBirth: undefined })); setError(null); }}
          readOnly={pending}
          aria-invalid={Boolean(fieldError.dateOfBirth)}
          aria-describedby={fieldError.dateOfBirth ? "onboarding-dob-error" : undefined}
          className="mt-2 h-11"
        />
        {fieldError.dateOfBirth ? <p id="onboarding-dob-error" role="alert" className="mt-1 text-xs text-destructive">{fieldError.dateOfBirth}</p> : null}
      </div>
      {error ? <p role="alert" className="text-sm leading-5 text-destructive">{error}</p> : null}
      <Button type="submit" disabled={pending} className="h-11 w-full">{pending ? <Loader2 className="animate-spin" /> : <ArrowRight />}{pending ? "Saving..." : "Continue to your workspace"}</Button>
      <div className="flex items-center justify-center">
        <Button type="button" variant="ghost" size="sm" disabled={pending} onClick={() => { void signOut(); }} className="text-xs">Sign out</Button>
      </div>
      <p className="text-center text-xs leading-5 text-muted-foreground">Only your name and date of birth are stored. Use a different account? <Link href="/sign-in" className="underline underline-offset-2">Go to sign in</Link>.</p>
    </form>
  );
}
