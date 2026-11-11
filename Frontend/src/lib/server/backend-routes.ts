const id = "[\\da-f]{8}-[\\da-f]{4}-[\\da-f]{4}-[\\da-f]{4}-[\\da-f]{12}";
const project = `projects/${id}`;
const conversation = `${project}/conversations/${id}`;
const routes = [
  { path: "me", methods: ["GET", "PATCH"] },
  { path: `jobs/${id}`, methods: ["GET"] },
  { path: "projects", methods: ["GET", "POST"], list: true },
  { path: project, methods: ["GET", "PATCH", "DELETE"] },
  { path: `${project}/documents`, methods: ["GET", "POST"], list: true },
  { path: `${project}/documents/${id}`, methods: ["GET", "DELETE"] },
  { path: `${project}/documents/${id}/file`, methods: ["GET"] },
  { path: `${project}/documents/${id}/retry`, methods: ["POST"] },
  { path: `${project}/conversations`, methods: ["GET", "POST"], list: true },
  { path: conversation, methods: ["GET", "PATCH", "DELETE"] },
  { path: `${conversation}/messages`, methods: ["GET", "POST"], list: true },
  { path: `${conversation}/messages/${id}/(?:retry|cancel)`, methods: ["POST"] },
].map((route) => ({ ...route, pattern: new RegExp(`^${route.path}$`, "i") }));

export function backendRoute(path: string[]) {
  if (path.some((part) => !part || part === "." || part === ".." || /[\\/\x00-\x1f]/.test(part))) return undefined;
  return routes.find((route) => route.pattern.test(path.join("/")));
}

export function validBackendQuery(query: URLSearchParams, list: boolean): boolean {
  const seen = new Set<string>();
  for (const [name, value] of query) {
    if (!list || !["cursor", "limit"].includes(name) || seen.has(name)) return false;
    if (name === "limit" && (!/^\d+$/.test(value) || Number(value) < 1 || Number(value) > 100)) return false;
    seen.add(name);
  }
  return true;
}
