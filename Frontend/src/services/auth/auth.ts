import { Account, AppwriteException, Client, ID } from "appwrite";
import type { AuthUser, EmailCodeChallenge } from "@/lib/types";

const endpoint = (process.env.NEXT_PUBLIC_APPWRITE_ENDPOINT || "").trim().replace(/\/+$/, "");
const projectId = (process.env.NEXT_PUBLIC_APPWRITE_PROJECT_ID || "").trim();
export const authConfigured = Boolean(endpoint && projectId);

let account: Account | undefined;

function getAccount() {
  if (!authConfigured) throw new Error("Email sign-in is not configured yet.");
  if (typeof window === "undefined") throw new Error("Account requests must run in the browser.");
  account ??= new Account(new Client().setEndpoint(endpoint).setProject(projectId));
  return account;
}

export async function fetchCurrentUser(): Promise<AuthUser | null> {
  try {
    const user = await getAccount().get();
    if (!user.email) return null;
    return { id: user.$id, email: user.email, name: user.name };
  } catch (error) {
    if (error instanceof AppwriteException && error.code === 401) return null;
    throw error;
  }
}

export async function requestEmailCode(email: string): Promise<EmailCodeChallenge> {
  const normalizedEmail = email.trim();
  const token = await getAccount().createEmailToken({ userId: ID.unique(), email: normalizedEmail, phrase: false });
  const expiresAt = Date.parse(token.expire);
  if (!token.userId || !Number.isFinite(expiresAt)) throw new Error("Could not start code verification. Please request a new code.");
  return { userId: token.userId, email: normalizedEmail, expiresAt };
}

export async function createEmailCodeSession(userId: string, code: string): Promise<void> {
  if (!/^[0-9]{6}$/.test(code)) throw new Error("Enter the six-digit code from your email.");
  await getAccount().createSession({ userId, secret: code });
}

export async function deleteCurrentSession(): Promise<void> {
  try {
    await getAccount().deleteSession({ sessionId: "current" });
  } catch (error) {
    if (error instanceof AppwriteException && (error.code === 401 || error.type === "user_session_not_found")) return;
    throw error;
  }
}

export function authErrorMessage(error: unknown): string {
  if (error instanceof TypeError) return "Could not connect to Appwrite. Check your connection and try again.";
  if (error instanceof AppwriteException) {
    if (error.code === 429) return "Too many attempts. Wait a few minutes before trying again.";
    if (error.type === "user_invalid_token") return "This code is invalid or has expired. Check the code or request a new one.";
    if (error.type === "user_session_already_exists") return "You already have an active session. Refresh the page to continue.";
    if (error.code === 0) return "Could not connect to Appwrite. Check your connection and try again.";
    if (error.code >= 500) return "Email sign-in is temporarily unavailable. Please try again.";
  }
  return error instanceof Error ? error.message : "Could not complete sign-in. Please try again.";
}
