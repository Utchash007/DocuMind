import type { HealthResponse } from "@/lib/types";
import { apiFetch } from "@/services/api/api";

export function fetchHealth(signal?: AbortSignal) {
  return apiFetch<HealthResponse>("/health", { signal }, 5_000);
}
