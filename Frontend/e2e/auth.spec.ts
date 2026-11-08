import { expect, test, type Page } from "@playwright/test";
import { mockAppwrite } from "./appwrite";

const browserErrors = new WeakMap<Page, string[]>();

test.beforeEach(async ({ page }) => {
  const errors: string[] = [];
  browserErrors.set(page, errors);
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error" && /hydration|didn't match/i.test(message.text())) errors.push(message.text());
  });
});

test.afterEach(async ({ page }) => {
  expect(browserErrors.get(page)).toEqual([]);
});

async function sendCode(page: Page, email = "researcher@example.com") {
  await page.getByRole("textbox", { name: "Email address" }).fill(email);
  await page.getByRole("button", { name: "Send sign-in code" }).click();
  await expect(page.getByRole("textbox", { name: "Sign-in code" })).toBeFocused();
}

async function verifyCode(page: Page, code = "012345") {
  await page.getByRole("textbox", { name: "Sign-in code" }).fill(code);
  await page.getByRole("button", { name: "Verify and sign in" }).click();
}

test("signed-out direct links require sign-in before loading the workspace", async ({ page, context }) => {
  await mockAppwrite(context);
  const backendRequests: string[] = [];
  page.on("request", (request) => { if (request.url().includes("/api/backend/")) backendRequests.push(request.url()); });

  for (const path of ["/", "/notebooks/11111111-1111-4111-8111-111111111111"]) {
    await page.goto(path);
    await expect(page).toHaveURL("/sign-in");
    await expect(page.getByRole("textbox", { name: "Email address" })).toBeVisible();
    await expect(page.getByRole("link", { name: /guest/i })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "New Notebook", exact: true })).toHaveCount(0);
    expect(await page.evaluate(() => localStorage.getItem("notemind-workspace"))).toBeNull();
  }

  await page.getByRole("link", { name: "Privacy notes" }).click();
  await expect(page).toHaveURL("/help#privacy");
  expect(backendRequests).toEqual([]);
});

test("workspace initialization waits for session restoration", async ({ page, context }) => {
  await mockAppwrite(context, { signedIn: true });
  const backendRequests: string[] = [];
  page.on("request", (request) => { if (request.url().includes("/api/backend/")) backendRequests.push(request.url()); });
  let release!: () => void;
  const gate = new Promise<void>((resolve) => { release = resolve; });
  await page.route("**/appwrite/v1/account", async (route) => { await gate; await route.fallback(); });

  try {
    await page.goto("/");
    await expect(page.getByRole("status")).toHaveText("Checking your session...");
    await expect(page.getByRole("heading", { name: "Your Notebooks" })).toHaveCount(0);
    expect(await page.evaluate(() => localStorage.getItem("notemind-workspace"))).toBeNull();
    expect(backendRequests).toEqual([]);
  } finally {
    release();
  }

  await expect(page.getByRole("heading", { name: "Your Notebooks" })).toBeVisible();
  await expect.poll(() => backendRequests.length).toBeGreaterThanOrEqual(2);
});

test("session lookup errors close the workspace until recovery", async ({ page, context }) => {
  const appwrite = await mockAppwrite(context, { signedIn: true });
  appwrite.accountError = { status: 503, type: "general_server_error", message: "Account unavailable" };
  await page.goto("/");
  await expect(page).toHaveURL("/sign-in");
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Email sign-in is temporarily unavailable.");
  expect(await page.evaluate(() => localStorage.getItem("notemind-workspace"))).toBeNull();

  appwrite.accountError = null;
  await page.getByRole("button", { name: "Check session again" }).click();
  await page.getByRole("link", { name: "Continue to notebooks" }).click();
  await expect(page.getByRole("heading", { name: "Your Notebooks" })).toBeVisible();

  appwrite.accountError = { status: 503, type: "general_server_error", message: "Account unavailable" };
  await page.evaluate(() => window.dispatchEvent(new Event("focus")));
  await expect(page).toHaveURL("/sign-in");
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Email sign-in is temporarily unavailable.");
  await expect(page.getByRole("heading", { name: "Your Notebooks" })).toHaveCount(0);
});

test("an anonymous Appwrite account cannot open notebooks", async ({ page, context }) => {
  await mockAppwrite(context, { signedIn: true, email: "" });
  await page.goto("/");
  await expect(page).toHaveURL("/sign-in");
  await expect(page.getByRole("textbox", { name: "Email address" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Continue to notebooks" })).toHaveCount(0);
  expect(await page.evaluate(() => localStorage.getItem("notemind-workspace"))).toBeNull();
});

test("email codes restore a session and sign-out locks saved browser notebooks", async ({ page, context }, testInfo) => {
  const appwrite = await mockAppwrite(context);
  await page.goto("/");
  await expect(page).toHaveURL("/sign-in");
  await sendCode(page);
  expect(appwrite.tokens).toHaveLength(1);
  expect(appwrite.tokens[0]).toMatchObject({ email: "researcher@example.com", phrase: false });
  expect(appwrite.tokens[0].userId).not.toBe("existing-user");
  await page.screenshot({ path: testInfo.outputPath("email-code-desktop.png"), fullPage: true, animations: "disabled" });
  await verifyCode(page);
  await expect(page).toHaveURL("/");
  expect(appwrite.sessions).toEqual([{ userId: "existing-user", secret: "012345" }]);
  await page.getByRole("button", { name: "New Notebook", exact: true }).click();
  await page.getByRole("textbox", { name: "Notebook name" }).fill("Local research");
  await page.getByRole("button", { name: "Create notebook", exact: true }).click();
  await expect(page.getByRole("heading", { level: 1 })).toContainText("Local research");
  const notebookUrl = page.url();
  await page.reload();
  await page.getByRole("button", { name: "Account menu", exact: true }).click();
  await expect(page.getByRole("menu")).toContainText("researcher@example.com");
  await page.keyboard.press("Escape");
  await page.goto(notebookUrl);
  await page.getByRole("button", { name: "Account menu", exact: true }).click();
  await expect(page.getByRole("menu")).toContainText("researcher@example.com");

  appwrite.signOutError = { status: 503, type: "general_server_error", message: "Temporarily unavailable" };
  await page.getByRole("menuitem", { name: "Sign out", exact: true }).click();
  await expect(page.getByText("Email sign-in is temporarily unavailable. Please try again.", { exact: true })).toBeVisible();
  await expect(page.getByRole("menuitem", { name: "Sign out", exact: true })).toBeEnabled();
  expect(appwrite.sessionActive).toBe(true);
  appwrite.signOutError = null;
  await page.getByRole("menuitem", { name: "Sign out", exact: true }).click();
  await expect(page).toHaveURL("/sign-in");
  await page.reload();
  await expect(page.getByRole("textbox", { name: "Email address" })).toBeVisible();
  await expect(page.getByRole("link", { name: /guest/i })).toHaveCount(0);
  await page.goBack();
  await expect(page).toHaveURL("/sign-in");
  await page.goto(notebookUrl);
  await expect(page).toHaveURL("/sign-in");
  await expect(page.getByRole("heading", { name: "Local research", exact: true })).toHaveCount(0);
  expect((await context.cookies()).some((cookie) => cookie.name === "a_session_notemind-e2e")).toBe(false);
  expect(await page.evaluate(() => JSON.stringify({ ...localStorage, ...sessionStorage }))).not.toContain("012345");
  await sendCode(page);
  await verifyCode(page, "654321");
  await expect(page).toHaveURL("/");
  await expect(page.getByRole("link", { name: "Open notebook Local research" })).toBeVisible();
});

test("sign-out cancels pending questions and the remaining upload queue", async ({ page, context }) => {
  await mockAppwrite(context, { signedIn: true });
  await page.goto("/");
  await page.getByRole("button", { name: "New Notebook", exact: true }).click();
  await page.getByRole("textbox", { name: "Notebook name" }).fill("Paused research");
  await page.getByRole("button", { name: "Create notebook", exact: true }).click();
  await page.getByRole("button", { name: "Add your first PDF", exact: true }).click();
  await page.getByRole("tab", { name: "Existing sources" }).click();
  await page.getByRole("checkbox", { name: "Reference research.pdf", exact: true }).check();
  await page.getByRole("button", { name: "Add 1 source", exact: true }).click();

  let release!: () => void;
  const gate = new Promise<void>((resolve) => { release = resolve; });
  let uploads = 0;
  await page.route("**/api/backend/query", async (route) => { await gate; await route.fulfill({ json: { answer: "Late response", citations: [] } }).catch(() => {}); });
  await page.route("**/api/backend/upload", async (route) => { uploads += 1; await gate; await route.fulfill({ json: { message: "Uploaded", chunks_count: 1 } }).catch(() => {}); });

  const question = page.waitForRequest("**/api/backend/query");
  await page.getByRole("textbox", { name: "Ask a question", exact: true }).fill("A question interrupted by sign-out.");
  await page.getByRole("button", { name: "Send question" }).click();
  await question;
  const upload = page.waitForRequest("**/api/backend/upload");
  await page.getByRole("button", { name: "Add sources", exact: true }).click();
  await page.locator('input[type="file"]').setInputFiles([
    { name: "Interrupted.pdf", mimeType: "application/pdf", buffer: Buffer.from("%PDF-interrupted") },
    { name: "Queued.pdf", mimeType: "application/pdf", buffer: Buffer.from("%PDF-queued") },
  ]);
  await upload;
  await page.getByRole("button", { name: "Continue in background" }).click();

  const questionCancelled = page.waitForEvent("requestfailed", (request) => request.url().endsWith("/api/backend/query"));
  const uploadCancelled = page.waitForEvent("requestfailed", (request) => request.url().endsWith("/api/backend/upload"));
  try {
    await page.getByRole("button", { name: "Account menu", exact: true }).click();
    await page.getByRole("menuitem", { name: "Sign out", exact: true }).click();
    await expect(page).toHaveURL("/sign-in");
  } finally {
    release();
  }
  await Promise.all([questionCancelled, uploadCancelled]);
  expect(uploads).toBe(1);

  await sendCode(page);
  await verifyCode(page);
  await page.getByRole("link", { name: "Open notebook Paused research" }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("The previous response was interrupted.");
  await expect(page.getByRole("article", { name: "NoteMind response", exact: true })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Interrupted.pdf PDF source", exact: true })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Queued.pdf PDF source", exact: true })).toHaveCount(0);
});

test("invalid codes can be retried, resent, and sent to a different email", async ({ page, context }) => {
  const appwrite = await mockAppwrite(context);
  await page.clock.install();
  await page.goto("/sign-in");
  await sendCode(page);
  const input = page.getByRole("textbox", { name: "Sign-in code" });
  await input.fill("01234");
  await expect(page.getByRole("button", { name: "Verify and sign in" })).toBeDisabled();
  await verifyCode(page, "111111");
  await expect(page.getByRole("main").getByRole("alert")).toContainText("This code is invalid or has expired.");
  await expect(input).toBeFocused();
  await expect(page.getByRole("button", { name: /Resend code in/ })).toBeDisabled();
  await page.clock.fastForward(61_000);
  await page.getByRole("button", { name: "Resend code", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("A new code has been sent.");
  await expect(input).toHaveValue("");
  expect(appwrite.tokens).toHaveLength(2);
  await page.getByRole("button", { name: "Change email" }).click();
  await expect(page.getByRole("textbox", { name: "Email address" })).toBeFocused();
  await sendCode(page, "other@example.com");
  await verifyCode(page, "654321");
  await expect(page).toHaveURL("/");
  expect(appwrite.sessions.at(-1)).toEqual({ userId: "other-existing-user", secret: "654321" });
  await page.getByRole("button", { name: "Account menu", exact: true }).click();
  await expect(page.getByRole("menu")).toContainText("other@example.com");
});

test("delivery errors and rate limits preserve a retryable sign-in flow", async ({ page, context }) => {
  const appwrite = await mockAppwrite(context);
  await page.clock.install();
  await page.goto("/sign-in");
  await page.getByRole("textbox", { name: "Email address" }).fill("invalid-email");
  await page.getByRole("button", { name: "Send sign-in code" }).click();
  expect(appwrite.tokens).toHaveLength(0);
  appwrite.sendError = { status: 503, type: "general_server_error", message: "Mail unavailable" };
  await page.getByRole("textbox", { name: "Email address" }).fill("researcher@example.com");
  await page.getByRole("button", { name: "Send sign-in code" }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Email sign-in is temporarily unavailable.");
  await expect(page.getByRole("textbox", { name: "Email address" })).toHaveValue("researcher@example.com");
  appwrite.sendError = null;
  await page.getByRole("button", { name: "Send sign-in code" }).click();
  await page.getByRole("textbox", { name: "Sign-in code" }).fill("012345");
  await page.clock.fastForward(61_000);
  appwrite.sendError = { status: 429, type: "general_rate_limit_exceeded", message: "Rate limit exceeded" };
  await page.getByRole("button", { name: "Resend code", exact: true }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Too many attempts.");
  await expect(page.getByRole("textbox", { name: "Sign-in code" })).toHaveValue("012345");
  await verifyCode(page);
  await expect(page).toHaveURL("/");
});

test("expired codes prompt a new request instead of submitting", async ({ page, context }) => {
  const appwrite = await mockAppwrite(context);
  appwrite.expiresAt = Date.now() + 5_000;
  await page.clock.install();
  await page.goto("/sign-in");
  await sendCode(page);
  await page.getByRole("textbox", { name: "Sign-in code" }).fill("012345");
  await page.clock.fastForward(6_000);
  await expect(page.getByRole("main").getByRole("alert")).toHaveText("This code has expired. Request a new code to continue.");
  await expect(page.getByRole("button", { name: "Verify and sign in" })).toBeDisabled();
  expect(appwrite.sessions).toHaveLength(0);
});

test("session lookup failures recover without submitting a used code again", async ({ page, context }) => {
  const appwrite = await mockAppwrite(context);
  await page.goto("/sign-in");
  await sendCode(page);
  appwrite.accountError = { status: 503, type: "general_server_error", message: "Account unavailable" };
  await verifyCode(page);
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Email sign-in is temporarily unavailable.");
  await expect(page.getByRole("button", { name: "Check session again" })).toBeVisible();
  appwrite.accountError = null;
  await page.getByRole("button", { name: "Check session again" }).click();
  await expect(page.getByText("Signed in as")).toContainText("researcher@example.com");
  expect(appwrite.sessions).toHaveLength(1);
  await page.getByRole("link", { name: "Continue to notebooks" }).click();
  appwrite.sessionActive = false;
  await page.evaluate(() => window.dispatchEvent(new Event("focus")));
  await expect(page).toHaveURL("/sign-in");
  await expect(page.getByRole("textbox", { name: "Email address" })).toBeVisible();
  await expect(page.getByRole("button", { name: "New Notebook", exact: true })).toHaveCount(0);
});

test("finishing verification after leaving sign-in preserves the public help page", async ({ page, context }) => {
  const appwrite = await mockAppwrite(context);
  await page.goto("/sign-in");
  await sendCode(page);
  let release!: () => void;
  const gate = new Promise<void>((resolve) => { release = resolve; });
  await page.route("**/appwrite/v1/account/sessions/token", async (route) => { await gate; await route.fallback(); });
  await verifyCode(page);
  await expect(page.getByRole("button", { name: "Signing in..." })).toBeDisabled();
  await page.getByRole("link", { name: "Terms", exact: true }).click();
  await expect(page).toHaveURL("/help#terms");
  const restored = page.waitForResponse((response) => response.url().endsWith("/appwrite/v1/account") && response.ok());
  release();
  await restored;
  await expect(page).toHaveURL("/help#terms");
  expect(appwrite.sessions).toHaveLength(1);
  await page.getByRole("link", { name: "Back to notebooks" }).click();
  await expect(page.getByRole("button", { name: "Account menu", exact: true })).toBeVisible();
});

test.describe("mobile email sign-in", () => {
  test.use({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });

  test("code entry supports the numeric keyboard and dark appearance", async ({ page, context }, testInfo) => {
    await mockAppwrite(context);
    await page.goto("/sign-in");
    await page.getByRole("button", { name: "Change appearance" }).click();
    await page.getByRole("menuitemradio", { name: "Dark", exact: true }).click();
    await sendCode(page);
    const input = page.getByRole("textbox", { name: "Sign-in code" });
    await expect(input).toHaveAttribute("inputmode", "numeric");
    await expect(input).toHaveAttribute("autocomplete", "one-time-code");
    await input.fill("012345");
    await page.screenshot({ path: testInfo.outputPath("email-code-mobile-dark.png"), fullPage: true, animations: "disabled" });
    expect(await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)).toBeLessThanOrEqual(1);
    await input.press("Enter");
    await expect(page).toHaveURL("/");
    await expect(page.getByRole("button", { name: "Account menu", exact: true })).toBeVisible();
    await expect(page.locator("html")).toHaveClass(/dark/);
  });
});
