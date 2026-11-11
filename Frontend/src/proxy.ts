import { NextResponse, type NextRequest } from "next/server";
import { appwriteProjectId, sessionCookieName } from "@/lib/server/auth-config";

/**
 * Early routing checks (owner: A2). Optimistic by design: it only checks
 * for session-cookie presence. Authoritative validation happens in the
 * server auth helpers, in the /api/backend proxy, and in FastAPI
 * dependencies -- cookie presence alone never authorizes anything.
 */
const PUBLIC_PATHS = ["/sign-in", "/help"];
const PUBLIC_PREFIXES = ["/api/auth", "/_next/static", "/_next/image", "/_next/data"];
const PUBLIC_EXACT = ["/favicon.ico", "/icon.svg", "/health", "/api/backend/health"];

export function proxy(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  if (PUBLIC_PATHS.includes(pathname)
    || PUBLIC_PREFIXES.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`))
    || PUBLIC_EXACT.includes(pathname)) {
    return NextResponse.next();
  }

  const projectId = appwriteProjectId();
  const name = sessionCookieName();
  const secret = projectId ? request.cookies.get(name)?.value : undefined;

  if (!secret) {
    if (pathname.startsWith("/api/")) {
      return NextResponse.json(
        { detail: { code: "unauthenticated", message: "Sign in to access NoteMind." } },
        { status: 401 },
      );
    }
    const url = new URL("/sign-in", request.url);
    url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api/auth (server auth lifecycle)
     * - _next/static, _next/image (static files)
     * - favicon.ico (metadata files)
     */
    "/((?!_next/static|_next/image|favicon.ico|api/auth).*)",
  ],
};
