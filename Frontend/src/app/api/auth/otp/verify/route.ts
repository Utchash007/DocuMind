import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { AppwriteError, AuthConfigError, OTP_LIMIT_WINDOW_MS, OTP_VERIFY_LIMIT, checkRateLimit, fetchSessionUser, isSecureRequest, sameOrigin, sessionCookieName, verifyOtp } from "@/lib/server/auth";

export async function POST(request: Request) {
  if (!sameOrigin(request)) {
    return NextResponse.json(
      { detail: { code: "forbidden", message: "This request was rejected. Please try again from the sign-in page." } },
      { status: 403 },
    );
  }
  const payload = (await request.json().catch(() => null)) as { userId?: unknown; code?: unknown } | null;
  const userId = typeof payload?.userId === "string" ? payload.userId.trim() : "";
  const code = typeof payload?.code === "string" ? payload.code : "";
  if (!userId || userId.length > 64) {
    return NextResponse.json(
      { detail: { code: "validation_error", message: "Could not verify the code. Please request a new code." } },
      { status: 422 },
    );
  }
  if (!/^[0-9]{6}$/.test(code)) {
    return NextResponse.json(
      { detail: { code: "validation_error", message: "Enter the six-digit code from your email." } },
      { status: 422 },
    );
  }
  if (!checkRateLimit(`otp-verify:user:${userId}`, OTP_VERIFY_LIMIT, OTP_LIMIT_WINDOW_MS)) {
    return NextResponse.json(
      { detail: { code: "rate_limited", message: "Too many sign-in attempts. Wait a few minutes before trying again." } },
      { status: 429 },
    );
  }
  try {
    const session = await verifyOtp(userId, code);
    const cookieStore = await cookies();
    cookieStore.set(sessionCookieName(), session.secret, {
      httpOnly: true,
      sameSite: "lax",
      path: "/",
      secure: await isSecureRequest(request),
      expires: new Date(session.expire),
    });
    const user = await fetchSessionUser(session.secret);
    return NextResponse.json({ user });
  } catch (error) {
    if (error instanceof AuthConfigError) {
      return NextResponse.json(
        { detail: { code: "service_unavailable", message: "Email sign-in is not configured yet." } },
        { status: 503 },
      );
    }
    if (error instanceof AppwriteError) {
      if (error.status === 401 || error.status === 403) {
        return NextResponse.json(
          { detail: { code: "invalid_code", message: "This code is invalid or has expired. Check the code or request a new one." } },
          { status: 401 },
        );
      }
      const status = error.status === 429 ? 429 : error.status >= 500 || error.status === 0 ? 503 : 502;
      return NextResponse.json(
        { detail: { code: status === 429 ? "rate_limited" : "service_unavailable", message: error.message } },
        { status },
      );
    }
    return NextResponse.json(
      { detail: { code: "service_unavailable", message: "Could not verify the code. Please try again." } },
      { status: 503 },
    );
  }
}
