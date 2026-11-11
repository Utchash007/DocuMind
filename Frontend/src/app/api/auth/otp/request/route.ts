import { NextResponse } from "next/server";
import {
  AppwriteError,
  AuthConfigError,
  OTP_LIMIT_WINDOW_MS,
  OTP_REQUEST_LIMIT,
  checkRateLimit,
  clientIp,
  requestOtp,
  sameOrigin,
} from "@/lib/server/auth";

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export async function POST(request: Request) {
  if (!sameOrigin(request)) {
    return NextResponse.json(
      { detail: { code: "forbidden", message: "This request was rejected. Please try again from the sign-in page." } },
      { status: 403 },
    );
  }
  const payload = (await request.json().catch(() => null)) as { email?: unknown } | null;
  const email = typeof payload?.email === "string" ? payload.email.trim() : "";
  if (!email || email.length > 320 || !EMAIL_PATTERN.test(email)) {
    return NextResponse.json(
      { detail: { code: "validation_error", message: "Enter a valid email address." } },
      { status: 422 },
    );
  }
  const ip = clientIp(request);
  if (!checkRateLimit(`otp-request:email:${email.toLowerCase()}`, OTP_REQUEST_LIMIT, OTP_LIMIT_WINDOW_MS)
    || !checkRateLimit(`otp-request:ip:${ip}`, OTP_REQUEST_LIMIT * 2, OTP_LIMIT_WINDOW_MS)) {
    return NextResponse.json(
      { detail: { code: "rate_limited", message: "Too many sign-in attempts. Wait a few minutes before trying again." } },
      { status: 429 },
    );
  }
  try {
    const challenge = await requestOtp(email);
    return NextResponse.json({ userId: challenge.userId, email, expiresAt: challenge.expiresAt });
  } catch (error) {
    if (error instanceof AuthConfigError) {
      return NextResponse.json(
        { detail: { code: "service_unavailable", message: "Email sign-in is not configured yet." } },
        { status: 503 },
      );
    }
    if (error instanceof AppwriteError) {
      const status = error.status === 429 ? 429 : error.status >= 500 || error.status === 0 ? 503 : 502;
      return NextResponse.json(
        { detail: { code: status === 429 ? "rate_limited" : "service_unavailable", message: error.message } },
        { status },
      );
    }
    return NextResponse.json(
      { detail: { code: "service_unavailable", message: "Could not send the sign-in code. Please try again." } },
      { status: 503 },
    );
  }
}
