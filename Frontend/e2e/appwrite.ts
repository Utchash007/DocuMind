import type { BrowserContext, Route } from "@playwright/test";

interface AppwriteError {
  status: number;
  type: string;
  message: string;
}

const sessionCookie = "a_session_notemind-e2e=e2e-session";
const unauthorized = { status: 401, type: "general_unauthorized_scope", message: "Sign in to access your account." };

async function reject(route: Route, error: AppwriteError) {
  await route.fulfill({ status: error.status, json: { code: error.status, type: error.type, message: error.message } });
}

export async function mockAppwrite(context: BrowserContext, { signedIn = false, email: sessionEmail = "researcher@example.com" }: { signedIn?: boolean; email?: string } = {}) {
  const mock = {
    tokens: [] as { userId: string; email: string; phrase: boolean }[],
    sessions: [] as { userId: string; secret: string }[],
    sendError: null as AppwriteError | null,
    accountError: null as AppwriteError | null,
    signOutError: null as AppwriteError | null,
    expiresAt: Date.now() + 15 * 60_000,
    sessionActive: signedIn,
  };
  let email = signedIn ? sessionEmail : "";
  let userId = signedIn ? "existing-user" : "";
  let code = "";

  if (signedIn) {
    await context.addCookies([{ name: "a_session_notemind-e2e", value: "e2e-session", domain: "127.0.0.1", path: "/appwrite/v1", httpOnly: true, sameSite: "Lax" }]);
  }

  await context.route("**/appwrite/v1/**", async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname.replace("/appwrite/v1", "");
    const method = request.method();
    const hasSession = mock.sessionActive && (await request.headerValue("cookie"))?.includes(sessionCookie);

    if (path === "/account" && method === "GET") {
      if (mock.accountError) return reject(route, mock.accountError);
      if (!hasSession) return reject(route, unauthorized);
      return route.fulfill({ json: { $id: userId, name: "", email, emailVerification: true, status: true, prefs: {} } });
    }

    if (path === "/account/tokens/email" && method === "POST") {
      if (mock.sendError) return reject(route, mock.sendError);
      const payload = request.postDataJSON() as { userId: string; email: string; phrase: boolean };
      mock.tokens.push(payload);
      email = payload.email;
      userId = email === "other@example.com" ? "other-existing-user" : "existing-user";
      code = mock.tokens.length === 1 ? "012345" : "654321";
      return route.fulfill({ status: 201, json: { $id: `token-${mock.tokens.length}`, $createdAt: new Date().toISOString(), userId, secret: "", expire: new Date(mock.expiresAt).toISOString(), phrase: "" } });
    }

    if (path === "/account/sessions/token" && method === "POST") {
      const payload = request.postDataJSON() as { userId: string; secret: string };
      mock.sessions.push(payload);
      if (payload.userId !== userId || payload.secret !== code) return reject(route, { status: 401, type: "user_invalid_token", message: "Invalid token passed in the request." });
      mock.sessionActive = true;
      code = "";
      return route.fulfill({ status: 201, headers: { "set-cookie": `${sessionCookie}; Path=/appwrite/v1; HttpOnly; SameSite=Lax` }, json: { $id: "e2e-session", userId, current: true, expire: new Date(Date.now() + 86_400_000).toISOString() } });
    }

    if (path === "/account/sessions/current" && method === "DELETE") {
      if (mock.signOutError) return reject(route, mock.signOutError);
      if (!hasSession) return reject(route, unauthorized);
      mock.sessionActive = false;
      return route.fulfill({ status: 204, headers: { "set-cookie": "a_session_notemind-e2e=; Path=/appwrite/v1; HttpOnly; SameSite=Lax; Max-Age=0" } });
    }

    return reject(route, { status: 404, type: "general_route_not_found", message: "Unexpected Appwrite fixture request." });
  });

  return mock;
}
