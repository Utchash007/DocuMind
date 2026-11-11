import { cookies } from "next/headers";
import { AppwriteError, AuthConfigError, createSessionJwt, sameOrigin, sessionCookieName } from "@/lib/server/auth";
import { backendRoute, validBackendQuery } from "@/lib/server/backend-routes";

type ProxyContext = { params: Promise<{ path: string[] }> };

async function proxy(request: Request, context: ProxyContext) {
  const { path } = await context.params;
  const method = request.method.toUpperCase();
  const isRead = method === "GET";
  const health = isRead && path.length === 1 && path[0] === "health";
  const route = backendRoute(path);
  if (
    (!health && !route) ||
    path.some((part) => !part || part.includes("/") || part.includes("\\") || part === ".." || part === ".")
  ) {
    return Response.json({ detail: "API route not found." }, { status: 404 });
  }
  if (route && !route.methods.includes(method)) {
    return Response.json({ code: "method_not_allowed", message: "Method not allowed." }, { status: 405, headers: { Allow: route.methods.join(", ") } });
  }
  const search = new URL(request.url).searchParams;
  if (!validBackendQuery(search, isRead && !!route?.list)) {
    return Response.json({ code: "validation_error", message: "Unsupported query parameters." }, { status: 422 });
  }
  if (!isRead && !sameOrigin(request)) {
    return Response.json({ code: "forbidden", message: "Cross-origin request rejected." }, { status: 403 });
  }
  if (Number(request.headers.get("content-length")) > 26 * 1024 * 1024) {
    return Response.json({ code: "file_too_large", message: "Request exceeds the upload limit." }, { status: 413 });
  }

  const base = (process.env.BACKEND_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");
  const timeout = AbortSignal.timeout(180_000);
  const headers = new Headers();
  for (const name of ["content-type", "range", "idempotency-key"]) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }

  // Authenticated v2 calls: mint a short-lived JWT from the HttpOnly session
  // cookie server-side and forward it as Bearer. Never trust a client header.
  if (!health) {
    const cookieStore = await cookies();
    const secret = cookieStore.get(sessionCookieName())?.value ?? null;
    if (!secret) {
      return Response.json(
        { code: "unauthenticated", message: "Sign in required." },
        { status: 401 },
      );
    }
    try {
      const jwt = await createSessionJwt(secret);
      headers.set("authorization", `Bearer ${jwt}`);
    } catch (error) {
      const expired = error instanceof AppwriteError && (error.status === 401 || error.status === 403);
      return Response.json(
        { code: expired ? "unauthenticated" : "service_unavailable", message: expired ? "Session expired. Sign in again." : error instanceof AuthConfigError ? error.message : "Sign-in service temporarily unavailable. Please try again." },
        { status: expired ? 401 : 503, headers: { "Cache-Control": "no-store" } },
      );
    }
  }

  const query = new URL(request.url).search;
  try {
    const init: RequestInit & { duplex: "half" } = {
      method,
      headers,
      body: isRead ? undefined : request.body,
      duplex: "half",
      cache: "no-store",
      redirect: "manual",
      signal: AbortSignal.any([request.signal, timeout]),
    };
    const upstream = await fetch(
      `${base}/${path.map(encodeURIComponent).join("/")}${query}`,
      init,
    );
    const responseHeaders = new Headers({ "Cache-Control": "no-store" });
    for (const name of ["content-type", "content-disposition", "accept-ranges", "content-range"]) {
      const value = upstream.headers.get(name);
      if (value) responseHeaders.set(name, value);
    }
    return new Response(upstream.body, { status: upstream.status, headers: responseHeaders });
  } catch {
    return Response.json(
      { detail: timeout.aborted ? "The backend took too long to respond. Please try again." : "Could not reach the PDF API. Check that the backend is running." },
      { status: timeout.aborted ? 504 : 502 },
    );
  }
}

export async function GET(request: Request, context: ProxyContext) {
  return proxy(request, context);
}

export async function POST(request: Request, context: ProxyContext) {
  return proxy(request, context);
}

export async function PATCH(request: Request, context: ProxyContext) {
  return proxy(request, context);
}

export async function PUT(request: Request, context: ProxyContext) {
  return proxy(request, context);
}

export async function DELETE(request: Request, context: ProxyContext) {
  return proxy(request, context);
}
