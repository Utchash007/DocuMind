import { createRequire } from "node:module";
import type { NewRelicApi } from "newrelic";

/**
 * Runtime access to the New Relic Node.js agent.
 *
 * The agent is deliberately loaded through Node's own resolver instead of a
 * static `import`. Two reasons:
 *
 * 1. The bundler never sees the agent, so it cannot be traced into the
 *    server bundle. Tracing the package fails because the optional security
 *    agent resolves its own version through a dynamic `require`.
 * 2. The agent must be loaded before the server starts handling requests to
 *    instrument them. `src/instrumentation.ts` performs that load; this
 *    module only exposes the already-loaded instance.
 *
 * The specifier is assembled at runtime so no bundler can statically resolve
 * it. Node still resolves it normally, from the application directory.
 */

const AGENT_SPECIFIER = ["new", "relic"].join("");

let cached: NewRelicApi | null | undefined;

function resolutionBases(): string[] {
  return [
    process.argv[1],
    `${process.cwd()}/package.json`,
    `${process.cwd()}/server.js`,
  ].filter((value): value is string => Boolean(value));
}

function agentRequire(): NewRelicApi | null {
  for (const base of resolutionBases()) {
    try {
      const requireFromApp = createRequire(base);
      return requireFromApp(AGENT_SPECIFIER) as NewRelicApi;
    } catch {
      // Try the next resolution base.
    }
  }
  return null;
}

/**
 * Return the New Relic agent API, or `null` when the agent is not
 * installed, not configured, or failed to start.
 */
export function newRelicAgent(): NewRelicApi | null {
  if (cached !== undefined) return cached;
  cached = agentRequire();
  return cached;
}
