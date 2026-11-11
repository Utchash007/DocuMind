import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { AppwriteError, AuthConfigError, deleteSession, loadSessionContext, sameOrigin, sessionCookieName } from "@/lib/server/auth";

const anonymous = () => NextResponse.json({ user: null, appUser: null });

export async function GET() {
  let secret: string | null = null;
  try {
    const cookieStore = await cookies();
    secret = cookieStore.get(sessionCookieName())?.value ?? null;
  } catch {
    return anonymous();
  }
  if (!secret) return anonymous();
  try {
    const context = await loadSessionContext(secret);
    if (!context) {
      try {
        const cookieStore = await cookies();
        cookieStore.delete(sessionCookieName());
      } catch {
        // best-effort: the browser treats the session as expired
      }
      return anonymous();
    }
    return NextResponse.json(context);
  } catch (error) {
    if (error instanceof AppwriteError && error.status === 401) return anonymous();
    if (error instanceof AuthConfigError) {
      return NextResponse.json(
        { detail: { code: "service_unavailable", message: "Email sign-in is not configured yet." } },
        { status: 503 },
      );
    }
    if (error instanceof AppwriteError && error.status >= 500) {
      return NextResponse.json(
        { detail: { code: "service_unavailable", message: error.message } },
        { status: 503 },
      );
    }
    return NextResponse.json(
      { detail: { code: "service_unavailable", message: "Could not restore your session. Please try again." } },
      { status: 503 },
    );
  }
}

export async function DELETE(request: Request) {
  if (!sameOrigin(request)) {
    return NextResponse.json(
      { detail: { code: "forbidden", message: "This request was rejected. Please try again." } },
      { status: 403 },
    );
  }
  const cookieStore = await cookies();
  const secret = cookieStore.get(sessionCookieName())?.value ?? null;
  if (secret) {
    try {
      await deleteSession(secret);
    } catch (error) {
      if (error instanceof AppwriteError && error.status !== 401) {
        return NextResponse.json(
          { detail: { code: "service_unavailable", message: error.message } },
          { status: 503 },
        );
      }
      if (error instanceof AuthConfigError) {
        return NextResponse.json(
          { detail: { code: "service_unavailable", message: "Email sign-in is not configured yet." } },
          { status: 503 },
        );
      }
      throw error;
    }
  }
  cookieStore.delete(sessionCookieName());
  return NextResponse.json({ ok: true });
}
