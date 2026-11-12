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
    // Do not derive the expected origin from request.url: a self-hosted
    // standalone server builds request.url from its bind address
    // (`https://0.0.0.0:$PORT/path`), not from the public Host header, so every
    // same-origin mutation would compare against the wrong origin. Compare
    // against Host (or x-forwarded-host) plus x-forwarded-proto instead.
    const rawHost = request.headers.get("x-forwarded-host")?.split(",")[0]?.trim()
      || request.headers.get("host")?.trim();
    if (!rawHost || !/^[a-z0-9.-]+(:\d{1,5})?$|^\[[0-9a-f:]+\](:\d{1,5})?$/i.test(rawHost)) {
      return false;
    }
    const rawProto = request.headers.get("x-forwarded-proto")?.split(",")[0]?.trim();
    const protocol = rawProto === "https" || rawProto === "http"
      ? rawProto
      : new URL(request.url).protocol.replace(/:$/, "");
    if (protocol !== "https" && protocol !== "http") return false;
    const expected = new URL(`${protocol}://${rawHost}`);
    return new URL(candidate).origin === expected.origin;
  } catch {
    return false;
  }
}
