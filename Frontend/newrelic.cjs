'use strict';

/**
 * New Relic Node.js agent configuration for the NoteMind web tier.
 *
 * Next.js 16 emits native OpenTelemetry spans; the New Relic "Hybrid Agent"
 * reads them. The agent's own Next.js and HTTP instrumentation is disabled so
 * those spans are not counted twice, and `undici` instrumentation is disabled
 * because Next.js wraps `fetch` and creates its own client spans.
 *
 * The license key is deliberately absent: provide `NEW_RELIC_LICENSE_KEY`
 * through the runtime environment. Environment variables override anything
 * set here, so the same image can be promoted between environments.
 */
exports.config = {
  app_name: ['NoteMind Web'],

  // Hybrid agent: consume the OpenTelemetry spans Next.js already emits.
  opentelemetry: {
    enabled: true,
  },

  instrumentation: {
    http: { enabled: false },
    next: { enabled: false },
    undici: { enabled: false },
  },

  distributed_tracing: {
    enabled: true,
  },

  application_logging: {
    enabled: true,
  },

  logging: {
    enabled: true,
    level: 'info',
  },

  // The browser agent needs the application id and browser key that New Relic
  // hands back for the configured license key. Automatic injection is done by
  // the APM agent's HTTP instrumentation, which is disabled above for the
  // Hybrid Agent; add the browser snippet from the New Relic UI when real
  // user monitoring is required.
  browser_monitoring: {
    enabled: false,
  },

  // Server-side config keeps the agent aligned with the New Relic UI.
  server_side_config: {
    enabled: true,
  },
};
