import { readFile } from "node:fs/promises";
import { expect, test, type APIRequestContext, type Page } from "@playwright/test";
import { mockAppwrite } from "./appwrite";

const browserErrors = new WeakMap<Page, string[]>();

test.beforeEach(async ({ page, context }) => {
  await mockAppwrite(context, { signedIn: true });
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

async function createNotebook(page: Page, title: string) {
  await page.getByRole("button", { name: "New Notebook", exact: true }).click();
  await page.getByRole("textbox", { name: "Notebook name" }).fill(title);
  await page.getByRole("button", { name: "Create notebook", exact: true }).click();
  await expect(page.getByRole("heading", { level: 1 })).toContainText(title);
  return page.url();
}

async function openSidebar(page: Page) {
  await page.getByRole("button", { name: "Open notebook sidebar", exact: true }).click();
  await expect(page.getByRole("dialog", { name: "Notebook navigation", exact: true })).toBeVisible();
}

async function addExistingSource(page: Page, filename = "Reference research.pdf") {
  await page.getByRole("button", { name: "Add your first PDF", exact: true }).click();
  await page.getByRole("tab", { name: "Existing sources" }).click();
  await page.getByRole("checkbox", { name: filename, exact: true }).check();
  await page.getByRole("button", { name: "Add 1 source", exact: true }).click();
}

async function referencePdf(request: APIRequestContext) {
  const response = await request.get("/api/backend/files/Reference%20research.pdf");
  expect(response.ok()).toBeTruthy();
  return response.body();
}

test("signed-in notebooks upload PDFs, answer with citations, persist notes, and export", async ({ page, request }, testInfo) => {
  await page.goto("/sign-in");
  await expect(page.getByText("Signed in as")).toContainText("researcher@example.com");
  await page.screenshot({ path: testInfo.outputPath("welcome-desktop.png"), fullPage: true, animations: "disabled" });
  await page.getByRole("link", { name: "Continue to notebooks" }).click();
  await expect(page.getByRole("heading", { name: "Your Notebooks" })).toBeVisible();
  const notebookUrl = await createNotebook(page, "Quantum Computing Basics");
  await expect(page.getByRole("textbox", { name: "Ask a question", exact: true })).toBeDisabled();
  await page.screenshot({ path: testInfo.outputPath("empty-workspace-desktop.png"), fullPage: true, animations: "disabled" });
  await page.getByRole("button", { name: "Add your first PDF" }).click();
  await page.locator('input[type="file"]').setInputFiles({ name: "Research paper.pdf", mimeType: "application/pdf", buffer: await referencePdf(request) });
  await expect(page.getByText("2 text chunks indexed", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Done", exact: true }).click();
  await page.getByRole("button", { name: "Add sources", exact: true }).click();
  await page.getByRole("tab", { name: "Existing sources" }).click();
  await page.getByRole("checkbox", { name: "Lab notes.pdf", exact: true }).check();
  await page.getByRole("button", { name: "Add 1 source", exact: true }).click();
  const queryRequest = page.waitForRequest((request) => request.url().endsWith("/api/backend/query"));
  await page.getByRole("textbox", { name: "Ask a question", exact: true }).fill("How is quantum information protected?");
  await page.getByRole("button", { name: "Send question" }).click();
  const payload = (await queryRequest).postData() ?? "";
  expect(payload).toContain('name="filenames"');
  expect(payload).toContain("Research paper.pdf");
  expect(payload).toContain("Lab notes.pdf");
  expect(payload).not.toContain("Reference research.pdf");
  const response = page.getByRole("article", { name: "NoteMind response", exact: true });
  await expect(response).toContainText("Error correction protects quantum information.");
  await response.getByRole("button", { name: "View citation from Research paper.pdf, page 2", exact: true }).click();
  const passage = page.getByRole("dialog", { name: "Source passage" });
  await expect(passage).toContainText("Error correction protects quantum information.");
  await expect(passage.getByRole("link", { name: "Open PDF at page 2" })).toHaveAttribute("href", "/api/backend/files/Research%20paper.pdf#page=2");
  const pdf = await request.get("/api/backend/files/Research%20paper.pdf", { headers: { Range: "bytes=0-4" } });
  expect(pdf.status()).toBe(206);
  expect(await pdf.text()).toBe("%PDF-");
  await passage.getByRole("button", { name: "Close", exact: true }).click();
  await expect(response.getByRole("button", { name: "View citation from Research paper.pdf, page 2", exact: true })).toBeFocused();
  await response.getByRole("button", { name: "Save to notes", exact: true }).click();
  await page.getByRole("button", { name: "Source overview", exact: true }).click();
  const note = page.getByRole("dialog", { name: "Your saved note" });
  await note.getByRole("textbox", { name: "Title", exact: true }).fill("Key takeaways");
  await note.getByRole("textbox", { name: "Note content" }).fill("**Error correction** is essential to preserving quantum information.");
  await note.getByRole("tab", { name: "Preview" }).click();
  await expect(note.getByRole("tabpanel")).toContainText("Error correction is essential");
  await note.getByRole("button", { name: "Save note", exact: true }).click();
  await page.reload();
  await expect(page.getByRole("button", { name: "Key takeaways", exact: true })).toBeVisible();
  await expect(page.getByRole("article", { name: "NoteMind response", exact: true })).toContainText("Error correction protects quantum information.");
  await page.screenshot({ path: testInfo.outputPath("workspace-desktop.png"), fullPage: true, animations: "disabled" });
  await page.getByRole("button", { name: "Share", exact: true }).click();
  const downloadEvent = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download Markdown" }).click();
  const download = await downloadEvent;
  const output = testInfo.outputPath("notebook.md");
  await download.saveAs(output);
  const markdown = await readFile(output, "utf8");
  expect(markdown).toContain("# Quantum Computing Basics");
  expect(markdown).toContain("### Key takeaways");
  expect(markdown).toContain("Research paper.pdf, page 2");
  await page.getByRole("dialog").getByRole("button", { name: "Close", exact: true }).click();
  await page.getByRole("link", { name: "All notebooks" }).click();
  await createNotebook(page, "A separate notebook");
  await expect(page.getByRole("article", { name: "NoteMind response", exact: true })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Key takeaways", exact: true })).toHaveCount(0);
  await expect(page.getByRole("textbox", { name: "Ask a question", exact: true })).toBeDisabled();
  await page.goto(notebookUrl);
  await expect(page.getByRole("button", { name: "Key takeaways", exact: true })).toBeVisible();
});

test("library search, sorting, renaming, and deletion are keyboard accessible", async ({ page }, testInfo) => {
  await page.goto("/");
  const create = page.getByRole("button", { name: "New Notebook", exact: true });
  await create.focus();
  await create.press("Enter");
  await expect(page.getByRole("textbox", { name: "Notebook name" })).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(create).toBeFocused();
  for (const title of ["Quantum Computing Basics", "Genetics & CRISPR Research", "Legal Case Analysis"]) {
    await createNotebook(page, title);
    await page.getByRole("link", { name: "All notebooks" }).click();
  }
  await page.screenshot({ path: testInfo.outputPath("library-desktop.png"), fullPage: true, animations: "disabled" });
  await page.keyboard.press("ControlOrMeta+k");
  const search = page.getByRole("searchbox", { name: "Search notebooks" });
  await expect(search).toBeFocused();
  await search.fill("genetics");
  await expect(page.getByRole("link", { name: /^Open notebook / })).toHaveCount(1);
  await search.fill("no matching notebook");
  await expect(page.getByRole("heading", { name: "No notebooks found" })).toBeVisible();
  await page.getByRole("button", { name: "Clear search", exact: true }).first().click();
  await page.getByRole("combobox", { name: "Sort notebooks" }).click();
  await page.getByRole("option", { name: "Name A–Z" }).click();
  await expect(page.getByRole("link", { name: /^Open notebook / })).toHaveText(["Genetics & CRISPR Research", "Legal Case Analysis", "Quantum Computing Basics"]);
  await page.getByRole("button", { name: "Notebook options for Legal Case Analysis", exact: true }).click();
  await page.getByRole("menuitem", { name: "Rename", exact: true }).click();
  await page.getByRole("textbox", { name: "Notebook name" }).fill("Case notes");
  await page.getByRole("textbox", { name: "Notebook name" }).press("Enter");
  await expect(page.getByRole("link", { name: "Open notebook Case notes", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Notebook options for Case notes", exact: true })).toBeFocused();
  await page.getByRole("button", { name: "Notebook options for Case notes", exact: true }).click();
  await page.getByRole("menuitem", { name: "Delete notebook", exact: true }).click();
  await page.getByRole("dialog").getByRole("button", { name: "Delete notebook", exact: true }).click();
  await expect(create).toBeFocused();
  await page.reload();
  await expect(page.getByRole("link", { name: /^Open notebook / })).toHaveCount(2);
  await expect(page.getByRole("link", { name: "Open notebook Case notes", exact: true })).toHaveCount(0);
});

test("failed, stopped, and interrupted questions can be retried without duplicate messages", async ({ page }) => {
  await page.goto("/");
  await createNotebook(page, "Retry research");
  await addExistingSource(page);
  await page.route("**/api/backend/query", (route) => route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ detail: "Answer provider is temporarily unavailable." }) }));
  await page.getByRole("textbox", { name: "Ask a question", exact: true }).fill("Summarize quantum information.");
  await page.getByRole("button", { name: "Send question" }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Answer provider is temporarily unavailable.");
  await page.unroute("**/api/backend/query");
  await page.getByRole("button", { name: "Retry question" }).click();
  await expect(page.getByRole("article", { name: "NoteMind response", exact: true })).toHaveCount(1);
  await expect(page.getByRole("article", { name: "Your question", exact: true })).toHaveCount(1);

  let release!: () => void;
  let gate = new Promise<void>((resolve) => { release = resolve; });
  await page.route("**/api/backend/query", async (route) => { await gate; await route.abort().catch(() => {}); });
  await page.getByRole("textbox", { name: "Ask a question", exact: true }).fill("A question to stop.");
  await page.getByRole("button", { name: "Send question" }).click();
  await page.getByRole("button", { name: "Stop response" }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Response stopped.");
  release();
  await page.unroute("**/api/backend/query");
  await page.getByRole("button", { name: "Retry question" }).click();
  await expect(page.getByRole("article", { name: "NoteMind response", exact: true })).toHaveCount(2);
  await expect(page.getByRole("article", { name: "Your question", exact: true })).toHaveCount(2);

  gate = new Promise<void>((resolve) => { release = resolve; });
  await page.route("**/api/backend/query", async (route) => { await gate; await route.abort().catch(() => {}); });
  await page.getByRole("textbox", { name: "Ask a question", exact: true }).fill("A question interrupted by reloading.");
  await page.getByRole("button", { name: "Send question" }).click();
  await expect(page.getByRole("button", { name: "Stop response" })).toBeVisible();
  await page.reload();
  await expect(page.getByRole("button", { name: "Retry question" })).toBeVisible();
  await expect(page.getByRole("article", { name: "Your question", exact: true }).last()).toContainText("A question interrupted by reloading.");
  release();
  await page.unroute("**/api/backend/query");
  await page.getByRole("button", { name: "Retry question" }).click();
  await expect(page.getByRole("article", { name: "NoteMind response", exact: true })).toHaveCount(3);
  await expect(page.getByRole("article", { name: "Your question", exact: true })).toHaveCount(3);
});

test("background uploads stay associated with their original notebook", async ({ page, request }) => {
  await page.goto("/");
  const firstNotebook = await createNotebook(page, "Uploading notebook");
  let release!: () => void;
  const gate = new Promise<void>((resolve) => { release = resolve; });
  await page.route("**/api/backend/upload", async (route) => { await gate; await route.continue(); });
  await page.getByRole("button", { name: "Add your first PDF" }).click();
  await page.locator('input[type="file"]').setInputFiles({ name: "Background upload.pdf", mimeType: "application/pdf", buffer: await referencePdf(request) });
  await page.getByRole("button", { name: "Continue in background" }).click();
  await page.getByRole("button", { name: "Account menu", exact: true }).click();
  await page.getByRole("menuitem", { name: "Help & getting started" }).click();
  await expect(page).toHaveURL("/help");
  await page.getByRole("link", { name: "Back to notebooks" }).click();
  await createNotebook(page, "Other notebook");
  const upload = page.waitForResponse((response) => response.url().endsWith("/api/backend/upload"));
  release();
  expect((await upload).ok()).toBeTruthy();
  await expect(page.getByRole("textbox", { name: "Ask a question", exact: true })).toBeDisabled();
  await page.getByRole("link", { name: "All notebooks" }).click();
  await page.getByRole("link", { name: "Open notebook Uploading notebook", exact: true }).click();
  await expect(page).toHaveURL(firstNotebook);
  await expect(page.getByRole("button", { name: "Background upload.pdf PDF source", exact: true })).toBeVisible();
  await expect(page.getByRole("textbox", { name: "Ask a question", exact: true })).toBeEnabled();
});

test("invalid uploads show actionable errors and leave the notebook empty", async ({ page }) => {
  await page.goto("/");
  await createNotebook(page, "Upload validation");
  await page.getByRole("button", { name: "Add your first PDF" }).click();
  await page.locator('input[type="file"]').setInputFiles({ name: "Empty.pdf", mimeType: "application/pdf", buffer: Buffer.alloc(0) });
  await expect(page.getByText("This file is empty. Choose a PDF with text.", { exact: true })).toBeVisible();
  await page.locator('input[type="file"]').setInputFiles({ name: "Unreadable.pdf", mimeType: "application/pdf", buffer: Buffer.from("not a PDF") });
  await expect(page.getByText("No extractable text found in PDF.", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Done", exact: true }).click();
  await expect(page.getByRole("textbox", { name: "Ask a question", exact: true })).toBeDisabled();
});

test("storage failures are visible while the signed-in workspace remains usable", async ({ page }) => {
  await page.addInitScript(() => {
    const setItem = Storage.prototype.setItem;
    Storage.prototype.setItem = function (key: string, value: string) {
      if (key === "notemind-workspace") throw new DOMException("Storage is full", "QuotaExceededError");
      setItem.call(this, key, value);
    };
  });
  await page.goto("/");
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Changes could not be saved");
  await createNotebook(page, "Unsaved research");
  await expect(page.getByText("Not saved", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "What would you like to know?" })).toBeVisible();
});

test("saved notebooks remain available offline and connection retry recovers", async ({ page }) => {
  await page.goto("/");
  await createNotebook(page, "Offline research");
  await addExistingSource(page);
  await page.getByRole("link", { name: "All notebooks" }).click();
  await page.route("**/api/backend/health", (route) => route.abort());
  await page.route("**/api/backend/files", (route) => route.abort());
  await page.reload();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("PDF API is offline");
  await expect(page.getByRole("link", { name: "Open notebook Offline research", exact: true })).toBeVisible();
  await page.unroute("**/api/backend/health");
  await page.unroute("**/api/backend/files");
  await page.getByRole("button", { name: "Retry connection" }).click();
  await expect(page.getByRole("main").getByRole("alert")).toHaveCount(0);
  await page.getByRole("link", { name: "Open notebook Offline research", exact: true }).click();
  await expect(page.getByRole("button", { name: "Reference research.pdf PDF source", exact: true })).toBeVisible();
});

test.describe("mobile workspace", () => {
  test.use({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });

  test("dark appearance, navigation, source previews, and guide generation", async ({ page }, testInfo) => {
    await page.goto("/sign-in");
    await page.screenshot({ path: testInfo.outputPath("welcome-mobile.png"), fullPage: true, animations: "disabled" });
    await page.getByRole("button", { name: "Change appearance" }).click();
    await page.getByRole("menuitemradio", { name: "Dark", exact: true }).click();
    await page.getByRole("link", { name: "Continue to notebooks" }).click();
    await expect(page.locator("html")).toHaveClass(/dark/);
    await createNotebook(page, "Quantum Computing Basics");
    await addExistingSource(page);
    const menu = page.getByRole("button", { name: "Open notebook sidebar", exact: true });
    await openSidebar(page);
    await page.keyboard.press("Escape");
    await expect(menu).toBeFocused();
    await openSidebar(page);
    await page.getByRole("button", { name: "Reference research.pdf PDF source", exact: true }).click();
    await expect(page.getByTitle("PDF preview of Reference research.pdf")).toHaveAttribute("src", "/api/backend/files/Reference%20research.pdf");
    await page.getByRole("dialog").getByRole("button", { name: "Close", exact: true }).click();
    await expect(menu).toBeFocused();
    await openSidebar(page);
    await page.getByRole("button", { name: "Generate Guide", exact: true }).click();
    await page.getByRole("radio", { name: /Study guide/ }).check();
    await page.getByRole("button", { name: "Generate guide", exact: true }).click();
    await expect(page.getByRole("article", { name: "NoteMind response", exact: true })).toContainText("Source overview");
    await openSidebar(page);
    await page.getByRole("button", { name: "Add note", exact: true }).click();
    await page.getByRole("textbox", { name: "Title", exact: true }).fill("A connection to explore");
    await page.getByRole("textbox", { name: "Note content" }).fill("Compare error correction approaches.");
    await page.getByRole("button", { name: "Save note", exact: true }).click();
    await expect(menu).toBeFocused();
    await page.getByRole("button", { name: "Close toast", exact: true }).click();
    await expect(page.getByText("Note saved.", { exact: true })).toHaveCount(0);
    await page.screenshot({ path: testInfo.outputPath("workspace-mobile-dark.png"), fullPage: true, animations: "disabled" });
    expect(await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)).toBeLessThanOrEqual(1);
    await openSidebar(page);
    await expect(page.getByRole("button", { name: "A connection to explore", exact: true })).toBeVisible();
    await page.screenshot({ path: testInfo.outputPath("sidebar-mobile-dark.png"), fullPage: true, animations: "disabled" });
    await page.getByRole("link", { name: "All notebooks" }).click();
    await page.screenshot({ path: testInfo.outputPath("library-mobile-dark.png"), fullPage: true, animations: "disabled" });
    expect(await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)).toBeLessThanOrEqual(1);
    await page.reload();
    await expect(page.locator("html")).toHaveClass(/dark/);
    await expect(page.getByRole("link", { name: "Open notebook Quantum Computing Basics", exact: true })).toBeVisible();
  });
});
