type ProxyContext = { params: Promise<{ path: string[] }> };

async function proxy(request: Request, context: ProxyContext) {
  const { path } = await context.params;
  const isRead = request.method === "GET";
  const allowed = isRead
    ? (path.length === 1 && ["health", "files"].includes(path[0])) || (path.length === 2 && path[0] === "files")
    : path.length === 1 && ["upload", "query"].includes(path[0]);
  if (!allowed || path.some((part) => part.includes("/") || part.includes("\\") || part === "..")) {
    return Response.json({ detail: "API route not found." }, { status: 404 });
  }

  const base = (process.env.BACKEND_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");
  const timeout = AbortSignal.timeout(180_000);
  const headers = new Headers();
  for (const name of ["content-type", "range"]) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }

  try {
    const init: RequestInit & { duplex: "half" } = {
      method: request.method, headers, body: isRead ? undefined : request.body, duplex: "half",
      cache: "no-store", redirect: "manual", signal: AbortSignal.any([request.signal, timeout]),
    };
    const upstream = await fetch(`${base}/${path.map(encodeURIComponent).join("/")}`, init);
    const responseHeaders = new Headers({ "Cache-Control": "no-store" });
    for (const name of ["content-type", "content-disposition", "accept-ranges", "content-range"]) {
      const value = upstream.headers.get(name);
      if (value) responseHeaders.set(name, value);
    }
    return new Response(upstream.body, { status: upstream.status, headers: responseHeaders });
  } catch {
    return Response.json({ detail: timeout.aborted ? "The backend took too long to respond. Please try again." : "Could not reach the PDF API. Check that the backend is running." }, { status: timeout.aborted ? 504 : 502 });
  }
}

export async function GET(request: Request, context: ProxyContext) {
  return proxy(request, context);
}

export async function POST(request: Request, context: ProxyContext) {
  return proxy(request, context);
}
