/**
 * Ambient typings for the New Relic Node.js agent (`newrelic`).
 *
 * The published package ships no type declarations, and the agent is loaded
 * with a dynamic import from server-only code, so the small surface this
 * application uses is declared here instead of pulling in an extra typings
 * dependency.
 */
declare module "newrelic" {
  export interface NewRelicAgent {
    collector?: { isConnected?: () => boolean };
    on(event: string, listener: (...args: unknown[]) => void): void;
    once(event: string, listener: (...args: unknown[]) => void): void;
    removeListener(event: string, listener: (...args: unknown[]) => void): void;
  }

  export interface NewRelicBrowserTimingOptions {
    /** Emit the raw browser-agent JavaScript without a wrapping <script> tag. */
    hasToRemoveScriptWrapper?: boolean;
    /** Allow header generation outside of an active web transaction. */
    allowTransactionlessInjection?: boolean;
  }

  export interface NewRelicApi {
    agent?: NewRelicAgent;
    /** Inline browser (real user monitoring) agent, or `null` when unavailable. */
    getBrowserTimingHeader(options?: NewRelicBrowserTimingOptions): string | null;
  }

  const newrelic: NewRelicApi;
  export default newrelic;
}
