/**
 * New Relic Node.js agent bootstrap.
 *
 * Next.js 16 emits native OpenTelemetry spans. The New Relic "Hybrid Agent"
 * intercepts those spans and turns them into APM transactions, so the agent
 * has to be loaded before the server starts handling requests. The
 * `register()` hook below is called exactly once per server instance, which
 * makes it the earliest supported entry point.
 *
 * The agent is only loaded when a license key is configured: without one the
 * agent refuses to start, which would take the whole server down. Never bake
 * a license key into the image; provide `NEW_RELIC_LICENSE_KEY` through the
 * runtime environment.
 */

const CONNECT_TIMEOUT_MS = 8_000;

export async function register() {
  // The agent only instruments the Node.js runtime. The edge runtime used by
  // `src/proxy.ts` is not supported.
  if (process.env.NEXT_RUNTIME !== "nodejs") return;
  if (!process.env.NEW_RELIC_LICENSE_KEY?.trim()) return;

  const { newRelicAgent } = await import("@/lib/server/newrelic-agent");
  const newrelic = newRelicAgent();
  const agent = newrelic?.agent;
  if (!newrelic || !agent) return;
  if (agent.collector?.isConnected?.()) return;

  // Give the agent a bounded window to reach the collector so the first
  // requests are already attached to a connected agent.
  await new Promise<void>((resolve) => {
    const done = () => {
      clearTimeout(timer);
      agent.removeListener("started", done);
      agent.removeListener("errored", done);
      resolve();
    };
    const timer = setTimeout(done, CONNECT_TIMEOUT_MS);
    agent.once("started", done);
    agent.once("errored", done);
  });
}
