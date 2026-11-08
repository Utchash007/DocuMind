"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { ArrowLeft, ArrowRight, Loader2, Mail, RefreshCw } from "lucide-react";
import type { EmailCodeChallenge } from "@/lib/types";
import { authErrorMessage, requestEmailCode } from "@/services/auth/auth";
import { useAuth } from "@/components/providers/auth-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const RESEND_DELAY = 60_000;

export function EmailSignInForm() {
  const { state, actions, meta } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [challenge, setChallenge] = useState<(EmailCodeChallenge & { resendAt: number }) | null>(null);
  const [now, setNow] = useState(0);
  const [pending, setPending] = useState<"send" | "verify" | "resend" | "refresh" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState("");
  const emailRef = useRef<HTMLInputElement>(null);
  const codeRef = useRef<HTMLInputElement>(null);
  const active = useRef(true);
  const remaining = challenge ? Math.max(0, Math.ceil((challenge.resendAt - now) / 1000)) : 0;
  const expired = challenge !== null && now >= challenge.expiresAt;

  useEffect(() => {
    active.current = true;
    return () => { active.current = false; };
  }, []);

  useEffect(() => {
    if (!state.loading && !state.error && !state.user) {
      if (challenge) codeRef.current?.focus();
      else emailRef.current?.focus();
    }
  }, [challenge, state.loading, state.error, state.user]);

  useEffect(() => {
    if (!challenge) return;
    const timer = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, [challenge]);

  async function sendCode(resend = false) {
    if (pending || (resend && remaining > 0)) return;
    setPending(resend ? "resend" : "send");
    setError(null);
    setNotice("");
    try {
      const next = await requestEmailCode(resend && challenge ? challenge.email : email);
      const sentAt = Date.now();
      setNow(sentAt);
      setChallenge({ ...next, resendAt: sentAt + RESEND_DELAY });
      setCode("");
      setNotice(resend ? "A new code has been sent. Check your inbox." : "");
    } catch (error) {
      setError(authErrorMessage(error));
    } finally {
      setPending(null);
    }
  }

  async function verifyCode(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending || !challenge || expired) return;
    setPending("verify");
    setError(null);
    setNotice("");
    try {
      const signedIn = await actions.signIn(challenge.userId, code);
      setCode("");
      if (signedIn) {
        setChallenge(null);
        if (active.current) router.replace("/");
      }
    } catch (error) {
      setError(authErrorMessage(error));
      codeRef.current?.focus();
      codeRef.current?.select();
    } finally {
      setPending(null);
    }
  }

  async function refreshSession() {
    setPending("refresh");
    await actions.refreshSession();
    setPending(null);
  }

  return (
    <>
      {state.loading ? <p role="status" className="flex items-center justify-center gap-2 py-6 text-sm text-muted-foreground"><Loader2 className="size-4 animate-spin" />Checking your session...</p> : state.error ? (
        <div className="space-y-3">
          <p role="alert" className="text-sm leading-6 text-destructive">{state.error}</p>
          <Button variant="outline" className="h-11 w-full" disabled={pending !== null} onClick={() => { void refreshSession(); }}><RefreshCw className={pending === "refresh" ? "animate-spin" : ""} />Check session again</Button>
        </div>
      ) : state.user ? (
        <div className="space-y-4 text-center">
          <p className="text-sm text-muted-foreground">Signed in as <span className="block break-all font-medium text-foreground">{state.user.email}</span></p>
          <Button asChild className="h-11 w-full justify-between px-4"><Link href="/">Continue to notebooks<ArrowRight /></Link></Button>
          <p className="text-xs leading-5 text-muted-foreground">Your notebooks are saved in this browser.</p>
        </div>
      ) : !meta.configured ? (
        <p role="status" className="rounded-lg border bg-muted/40 p-4 text-center text-sm leading-6 text-muted-foreground">Sign-in is required to access your notebooks. Email sign-in is not configured yet. See <Link href="/help#sign-in" className="underline underline-offset-2">sign-in setup</Link> to enable access.</p>
      ) : (
        <div className="space-y-4">
          {challenge ? (
            <form onSubmit={verifyCode} className="space-y-4" aria-busy={pending !== null}>
              <div className="text-center"><h2 className="font-medium">Check your email</h2><p id="code-hint" className="mt-2 text-xs leading-5 text-muted-foreground">Enter the six-digit code sent to <span className="break-all font-medium text-foreground">{challenge.email}</span>.</p></div>
              <div>
                <label htmlFor="sign-in-code" className="text-xs font-medium">Sign-in code</label>
                <Input ref={codeRef} id="sign-in-code" name="code" type="text" inputMode="numeric" autoComplete="one-time-code" pattern="[0-9]{6}" minLength={6} maxLength={6} required value={code} onChange={(event) => { setCode(event.target.value.replace(/\D/g, "").slice(0, 6)); setError(null); }} readOnly={pending !== null} aria-describedby={error || expired ? "code-hint sign-in-error" : "code-hint"} aria-invalid={Boolean(error) || expired} placeholder="000000" className="mt-2 h-12 text-center text-2xl font-medium tracking-[0.4em] tabular-nums md:text-2xl" />
              </div>
              <Button type="submit" disabled={pending !== null || code.length !== 6 || expired} className="h-11 w-full">{pending === "verify" ? <Loader2 className="animate-spin" /> : <ArrowRight />}{pending === "verify" ? "Signing in..." : "Verify and sign in"}</Button>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <Button type="button" variant="ghost" size="sm" disabled={pending !== null} onClick={() => { setChallenge(null); setCode(""); setError(null); setNotice(""); }} className="-ml-2 text-xs"><ArrowLeft />Change email</Button>
                <Button type="button" variant="ghost" size="sm" disabled={pending !== null || remaining > 0} onClick={() => { void sendCode(true); }} className="-mr-2 text-xs">{pending === "resend" ? <Loader2 className="animate-spin" /> : null}{remaining > 0 ? `Resend code in ${remaining}s` : "Resend code"}</Button>
              </div>
              <p className="text-center text-xs leading-5 text-muted-foreground">Check your spam folder too. Codes expire after 15 minutes.</p>
            </form>
          ) : (
            <form onSubmit={(event) => { event.preventDefault(); void sendCode(); }} className="space-y-3" aria-busy={pending !== null}>
              <div><label htmlFor="sign-in-email" className="text-xs font-medium">Email address</label><Input ref={emailRef} id="sign-in-email" name="email" type="email" autoComplete="email" autoCapitalize="none" spellCheck={false} maxLength={320} required value={email} onChange={(event) => { setEmail(event.target.value); setError(null); }} readOnly={pending !== null} aria-describedby={error ? "email-hint sign-in-error" : "email-hint"} placeholder="name@company.com" className="mt-2 h-11" /></div>
              <Button type="submit" disabled={pending !== null || !email.trim()} className="h-11 w-full">{pending === "send" ? <Loader2 className="animate-spin" /> : <Mail />}{pending === "send" ? "Sending code..." : "Send sign-in code"}</Button>
              <p id="email-hint" className="text-center text-xs leading-5 text-muted-foreground">We’ll email you a six-digit code to sign in or create an account.</p>
            </form>
          )}
          {error || expired ? <p id="sign-in-error" role="alert" className="text-sm leading-5 text-destructive">{error || "This code has expired. Request a new code to continue."}</p> : null}
          <p role="status" className="text-center text-xs leading-5 text-muted-foreground">{notice}</p>
        </div>
      )}
    </>
  );
}
