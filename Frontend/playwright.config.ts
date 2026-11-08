import { existsSync } from "node:fs";
import path from "node:path";
import { defineConfig } from "@playwright/test";

const backendDirectory = path.resolve(__dirname, "../Backend");
const localPython = path.join(backendDirectory, ".venv", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
const python = process.env.PYTHON || (existsSync(localPython) ? localPython : "python");

export default defineConfig({
  testDir: "./e2e",
  forbidOnly: !!process.env.CI,
  workers: 1,
  timeout: 45_000,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:3011",
    browserName: "chromium",
    viewport: { width: 1440, height: 960 },
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  webServer: [
    {
      command: `"${python}" -m tests.e2e_server`,
      cwd: backendDirectory,
      url: "http://127.0.0.1:8011/health",
      reuseExistingServer: false,
      timeout: 60_000,
    },
    {
      command: "npm run build && npm run start -- --hostname 127.0.0.1 --port 3011",
      url: "http://127.0.0.1:3011",
      env: {
        BACKEND_URL: "http://127.0.0.1:8011",
        NEXT_PUBLIC_API_BASE_URL: "/api/backend",
        NEXT_PUBLIC_APPWRITE_ENDPOINT: "http://127.0.0.1:3011/appwrite/v1",
        NEXT_PUBLIC_APPWRITE_PROJECT_ID: "notemind-e2e",
      },
      reuseExistingServer: false,
      timeout: 180_000,
    },
  ],
});
