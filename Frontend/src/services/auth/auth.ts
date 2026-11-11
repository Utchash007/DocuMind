import type { ApplicationUser } from "@/lib/api-types";
import type { AuthUser, EmailCodeChallenge } from "@/lib/types";
import { apiFetch } from "@/services/api/api";

export interface SessionContext {
  user: AuthUser | null;
  appUser: ApplicationUser | null;
}

interface DetailError {
  detail?: { code?: string; message?: string } | string | Array<{ msg?: string }>;
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(path, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  const payload = (await response.json().catch(() => null)) as T & DetailError | null;
  if (!response.ok) throw new AuthRequestError(payload, response.status);
  if (payload === null) throw new TypeError("Could not connect to the sign-in service. Check your connection and try again.");
  return payload as T;
}

export class AuthRequestError extends Error {
  readonly status: number;
  readonly code: string;
  constructor(payload: DetailError | null, status: number) {
    const detail = payload?.detail;
    let message = "Could not complete sign-in. Please try again.";
    let code = "request_failed";
    if (detail && typeof detail === "object" && !Array.isArray(detail)) {
      code = detail.code ?? code;
      message = detail.message ?? message;
    } else if (typeof detail === "string") {
      message = detail;
    } else if (Array.isArray(detail)) {
      const text = detail.map((item) => item?.msg).filter(Boolean).join(". ");
      if (text) message = text;
    }
    super(message);
    this.name = "AuthRequestError";
    this.status = status;
    this.code = code;
  }
}

export async function fetchCurrentUser(): Promise<AuthUser | null> {
  const context = await fetchSessionContext();
  return context.user;
}

export async function fetchSessionContext(): Promise<SessionContext> {
  const response = await fetch("/api/auth/session", { cache: "no-store" });
  const payload = (await response.json().catch(() => null)) as (SessionContext & DetailError) | null;
  if (!response.ok) throw new AuthRequestError(payload, response.status);
  if (!payload) throw new TypeError("Could not connect to the sign-in service. Check your connection and try again.");
  return { user: payload.user ?? null, appUser: payload.appUser ?? null };
}

export async function requestEmailCode(email: string): Promise<EmailCodeChallenge> {
  const normalizedEmail = email.trim();
  const payload = await postJson<{ userId: string; email: string; expiresAt: number }>("/api/auth/otp/request", { email: normalizedEmail });
  if (!payload.userId || !Number.isFinite(payload.expiresAt)) throw new Error("Could not start code verification. Please request a new code.");
  return { userId: payload.userId, email: normalizedEmail, expiresAt: payload.expiresAt };
}

export async function createEmailCodeSession(userId: string, code: string): Promise<AuthUser> {
  if (!/^[0-9]{6}$/.test(code)) throw new Error("Enter the six-digit code from your email.");
  const payload = await postJson<{ user: AuthUser }>("/api/auth/otp/verify", { userId, code });
  if (!payload.user?.email) throw new Error("Could not restore your session. Please try again.");
  return payload.user;
}

export async function deleteCurrentSession(): Promise<void> {
  const response = await fetch("/api/auth/session", { method: "DELETE", cache: "no-store" });
  if (response.ok) return;
  const payload = (await response.json().catch(() => null)) as DetailError | null;
  if (response.status === 401) return;
  throw new AuthRequestError(payload, response.status);
}

export async function updateProfile(name: string, dateOfBirth: string): Promise<ApplicationUser> {
  return apiFetch<ApplicationUser>("/me", {
    method: "PATCH",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ name, dateOfBirth }),
  }, 30_000);
}

export function authErrorMessage(error: unknown): string {
  if (error instanceof TypeError) return "Could not connect to the sign-in service. Check your connection and try again.";
  if (error instanceof AuthRequestError) {
    if (error.code === "invalid_code") return "This code is invalid or has expired. Check the code or request a new one.";
    if (error.code === "rate_limited") return "Too many attempts. Wait a few minutes before trying again.";
    if (error.code === "service_unavailable") return "Email sign-in is temporarily unavailable. Please try again.";
    if (error.code === "validation_error") return error.message;
    if (error.status === 0) return "Could not connect to the sign-in service. Check your connection and try again.";
    if (error.status >= 500) return "Email sign-in is temporarily unavailable. Please try again.";
  }
  return error instanceof Error ? error.message : "Could not complete sign-in. Please try again.";
}
