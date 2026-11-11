import "server-only";

import { Account, AppwriteException, Client, ID, Users } from "node-appwrite";
import { headers } from "next/headers";
import { appwriteProjectId } from "@/lib/server/auth-config";
export { sameOrigin, sessionCookieName } from "@/lib/server/auth-config";

/**
 * Server-side Appwrite auth (owner: A2).
 *
 * The browser never talks to Appwrite. This module owns the OTP/session
 * lifecycle: an admin client obtains session secrets, a fresh session-bound
 * client is created per request (never shared), and the secret lives only in
 * a host-only HttpOnly cookie. Only safe DTOs reach the browser.
 *
 * JWT exchange: node-appwrite's Account service has no createJWT method, so
 * the JWT is minted through POST /account/jwts on the session-bound client
 * (the session header is attached automatically from setSession). The JWT is
 * short-lived and forwarded to FastAPI as `Authorization: Bearer ...`.
 */

export const JWT_DURATION_SECONDS = 900;

function envLimit(name: string, fallback: number): number {
  const parsed = Number.parseInt(process.env[name] ?? "", 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

// Server-side throttling defaults are production-safe; E2E overrides them
// through the environment because one Next.js server serves the whole run.
export const OTP_REQUEST_LIMIT = envLimit("OTP_REQUEST_LIMIT", 5);
export const OTP_VERIFY_LIMIT = envLimit("OTP_VERIFY_LIMIT", 10);
export const OTP_LIMIT_WINDOW_MS = envLimit("OTP_LIMIT_WINDOW_MS", 10 * 60_000);

export interface SessionUser {
  id: string;
  email: string;
  name: string;
}

export class AuthConfigError extends Error {
  readonly status = 503;
  readonly code = "service_unavailable" as const;
  constructor() {
    super("Email sign-in is not configured yet.");
  }
}

export class AppwriteError extends Error {
  readonly status: number;
  readonly type: string;
  constructor(status: number, type: string, message: string) {
    super(message);
    this.status = status;
    this.type = type;
  }
}

function endpoint(): string {
  const value =
    process.env.APPWRITE_ENDPOINT?.trim() || process.env.NEXT_PUBLIC_APPWRITE_ENDPOINT?.trim() || "https://cloud.appwrite.io/v1";
  return value.trim().replace(/\/+$/, "");
}

function projectId(): string {
  return appwriteProjectId();
}

function apiKey(): string {
  return (process.env.APPWRITE_API_KEY ?? "").trim();
}

function requireConfig(): { endpoint: string; project: string } {
  const project = projectId();
  if (!project) throw new AuthConfigError();
  return { endpoint: endpoint(), project };
}

export function createAdminAccount(): Account {
  const { endpoint: endpointValue, project } = requireConfig();
  const key = apiKey();
  if (!key) throw new AuthConfigError();
  const client = new Client().setEndpoint(endpointValue).setProject(project).setKey(key);
  return new Account(client);
}

export function createSessionAccount(secret: string): Account {
  const { endpoint: endpointValue, project } = requireConfig();
  const client = new Client().setEndpoint(endpointValue).setProject(project).setSession(secret);
  return new Account(client);
}

export async function requestOtp(email: string) {
  const account = createAdminAccount();
  try {
    const token = await account.createEmailToken({ userId: ID.unique(), email, phrase: false });
    const expiresAt = Date.parse(token.expire);
    if (!token.userId || !Number.isFinite(expiresAt)) {
      throw new AppwriteError(502, "bad_gateway", "Could not start code verification. Please request a new code.");
    }
    return { userId: token.userId, expiresAt };
  } catch (error) {
    throw toAppwriteError(error, "Could not send the sign-in code. Please try again.");
  }
}

export async function verifyOtp(userId: string, code: string) {
  const account = createAdminAccount();
  try {
    const session = await account.createSession({ userId, secret: code });
    if (!session.secret || !session.expire) {
      throw new AppwriteError(502, "bad_gateway", "Could not create a session. Please try again.");
    }
    return session;
  } catch (error) {
    throw toAppwriteError(error, "Could not verify the code. Please try again.");
  }
}

export async function fetchSessionUser(secret: string): Promise<SessionUser> {
  const account = createSessionAccount(secret);
  try {
    const user = await account.get();
    if (!user.email) {
      throw new AppwriteError(401, "unauthenticated", "An email account is required to access NoteMind.");
    }
    return { id: user.$id, email: user.email, name: user.name ?? "" };
  } catch (error) {
    throw toAppwriteError(error, "Could not restore your session. Please try again.");
  }
}

export async function deleteSession(secret: string): Promise<void> {
  const account = createSessionAccount(secret);
  try {
    await account.deleteSession({ sessionId: "current" });
  } catch (error) {
    throw toAppwriteError(error, "Could not sign out. Please try again.");
  }
}

export async function createSessionJwt(secret: string): Promise<string> {
  const { endpoint: endpointValue, project } = requireConfig();
  const client = new Client().setEndpoint(endpointValue).setProject(project).setSession(secret);
  try {
    const uri = new URL(`${endpointValue}/account/jwts`);
    // `client.call` bypasses the SDK service methods, which are the layer
    // that attaches the project header. Without it Appwrite treats the
    // request as a guest and rejects the session with 401.
    const payload = await client.call("post", uri, {
      "content-type": "application/json",
      accept: "application/json",
      "X-Appwrite-Project": project,
    }, { duration: JWT_DURATION_SECONDS });
    const jwt = payload && typeof payload === "object" && "jwt" in payload ? String(payload.jwt) : "";
    if (!jwt) throw new AppwriteError(502, "bad_gateway", "Could not create a session token. Please try again.");
    return jwt;
  } catch (error) {
    throw toAppwriteError(error, "Could not create a session token. Please try again.");
  }
}

export async function createAdminUsersJwt(userId: string, sessionId: string): Promise<string> {
  const { endpoint: endpointValue, project } = requireConfig();
  const key = apiKey();
  if (!key) throw new AuthConfigError();
  const client = new Client().setEndpoint(endpointValue).setProject(project).setKey(key);
  const users = new Users(client);
  try {
    const jwt = await users.createJWT({ userId, sessionId, duration: JWT_DURATION_SECONDS });
    if (!jwt.jwt) throw new AppwriteError(502, "bad_gateway", "Could not create a session token. Please try again.");
    return jwt.jwt;
  } catch (error) {
    throw toAppwriteError(error, "Could not create a session token. Please try again.");
  }
}

function toAppwriteError(error: unknown, fallback: string): AppwriteError {
  if (error instanceof AuthConfigError) throw error;
  if (error instanceof AppwriteError) throw error;
  if (error instanceof AppwriteException) {
    const status = error.code || 502;
    if (status === 401 || status === 403) {
      return new AppwriteError(status, error.type || "unauthenticated", error.message || fallback);
    }
    if (status === 429) {
      return new AppwriteError(429, error.type || "rate_limited", "Too many attempts. Wait a few minutes before trying again.");
    }
    if (status >= 500 || status === 0) {
      return new AppwriteError(503, error.type || "service_unavailable", "Email sign-in is temporarily unavailable. Please try again.");
    }
    return new AppwriteError(status, error.type || "invalid_request", error.message || fallback);
  }
  if (error instanceof TypeError) {
    return new AppwriteError(503, "service_unavailable", "Could not connect to the sign-in service. Check your connection and try again.");
  }
  return new AppwriteError(502, "bad_gateway", fallback);
}

export async function isSecureRequest(request?: Request): Promise<boolean> {
  if (request) {
    const forwarded = request.headers.get("x-forwarded-proto");
    if (forwarded) return forwarded.split(",")[0].trim() === "https";
    try {
      return new URL(request.url).protocol === "https:";
    } catch {
      return false;
    }
  }
  const headersList = await headers();
  const forwarded = headersList.get("x-forwarded-proto");
  if (forwarded) return forwarded.split(",")[0].trim() === "https";
  return process.env.NODE_ENV === "production" && process.env.VERCEL === "1";
}

interface Bucket {
  count: number;
  resetAt: number;
}

const buckets = new Map<string, Bucket>();

export function checkRateLimit(key: string, max: number, windowMs: number): boolean {
  const now = Date.now();
  for (const [name, bucket] of buckets) {
    if (bucket.resetAt <= now) buckets.delete(name);
  }
  const bucket = buckets.get(key);
  if (!bucket || bucket.resetAt <= now) {
    buckets.set(key, { count: 1, resetAt: now + windowMs });
    return true;
  }
  bucket.count += 1;
  return bucket.count <= max;
}

export function clientIp(request: Request): string {
  const forwarded = request.headers.get("x-forwarded-for");
  if (forwarded) return forwarded.split(",")[0].trim() || "unknown";
  return request.headers.get("x-client-ip")?.trim() || "unknown";
}

/**
 * Totally-transport errors from the FastAPI side (unreachable backend),
 * returned as a null DTO path by callers that treat them as retryable.
 */
export interface BackendResult<T> {
  ok: boolean;
  status: number;
  data: T | null;
}

export async function callBackendMe<T>(jwt: string, method: "GET" | "PATCH", body?: unknown): Promise<BackendResult<T>> {
  const base = (process.env.BACKEND_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");
  try {
    const response = await fetch(`${base}/me`, {
      method,
      headers: {
        authorization: `Bearer ${jwt}`,
        ...(body === undefined ? {} : { "content-type": "application/json" }),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
      cache: "no-store",
      redirect: "manual",
      signal: AbortSignal.timeout(15_000),
    });
    const data = (await response.json().catch(() => null)) as T | null;
    return { ok: response.ok, status: response.status, data };
  } catch {
    return { ok: false, status: 0, data: null };
  }
}

export type SessionContext = { user: SessionUser; appUser: import("@/lib/api-types").ApplicationUser } | null;

export async function loadSessionContext(secret: string | null): Promise<SessionContext> {
  if (!secret) return null;
  const user = await fetchSessionUser(secret);
  const jwt = await createSessionJwt(secret);
  const me = await callBackendMe<import("@/lib/api-types").ApplicationUser>(jwt, "GET");
  if (!me.ok) {
    if (me.status === 401) return null;
    throw new AppwriteError(503, "service_unavailable", "Could not restore your workspace. Please try again.");
  }
  if (!me.data) throw new AppwriteError(503, "service_unavailable", "Could not restore your workspace. Please try again.");
  return { user, appUser: me.data };
}
