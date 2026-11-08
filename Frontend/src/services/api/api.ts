export const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || "/api/backend").replace(/\/+$/, "");

export class ApiError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
    this.name = "ApiError";
  }
}

function responseError(payload: unknown, status: number) {
  if (payload && typeof payload === "object" && "detail" in payload) {
    if (typeof payload.detail === "string") return payload.detail;
    if (Array.isArray(payload.detail)) {
      return payload.detail.map((item: { msg?: string }) => item.msg).filter(Boolean).join(". ");
    }
  }
  return `The server could not complete this request (${status}). Please try again.`;
}

export async function apiFetch<T>(path: string, init: RequestInit = {}, timeoutMs = 15_000): Promise<T> {
  const timeout = AbortSignal.timeout(timeoutMs);
  const signal = init.signal ? AbortSignal.any([init.signal, timeout]) : timeout;

  try {
    const response = await fetch(`${API_BASE}${path}`, { ...init, signal, cache: "no-store" });
    const payload: unknown = await response.json().catch(() => null);

    if (!response.ok) throw new ApiError(responseError(payload, response.status), response.status);
    if (payload === null) throw new ApiError("The server returned an unreadable response. Please try again.", 502);
    return payload as T;
  } catch (error) {
    if (error instanceof ApiError || init.signal?.aborted) throw error;
    if (timeout.aborted) throw new ApiError("This is taking longer than expected. Please try again.", 408);
    throw new ApiError("Could not connect to the backend. Check that the API server is running and try again.", 0);
  }
}

export function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : "Something went wrong. Please try again.";
}
