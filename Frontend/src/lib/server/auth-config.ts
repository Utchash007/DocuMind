// Shared by the optimistic routing gate and authoritative server auth.
export function appwriteProjectId(): string {
  return process.env.APPWRITE_PROJECT_ID?.trim() || process.env.NEXT_PUBLIC_APPWRITE_PROJECT_ID?.trim() || "";
}

export function sessionCookieName(): string {
  return `a_session_${appwriteProjectId()}`;
}

export function sameOrigin(request: Request): boolean {
  const candidate = request.headers.get("origin") ?? request.headers.get("referer");
  if (!candidate) return false;
  try {
    const expected = new URL(request.url);
    const protocol = request.headers.get("x-forwarded-proto")?.split(",")[0].trim();
    if (protocol === "https" || protocol === "http") expected.protocol = `${protocol}:`;
    return new URL(candidate).origin === expected.origin;
  } catch {
    return false;
  }
}
