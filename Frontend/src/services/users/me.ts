import { v2Fetch } from "@/services/v2http";
import type { ApplicationUser, ProfileUpdateRequest } from "@/lib/api-types";

/** A2 owns /me semantics; this is the A6 client for the frozen DTO. */
export function fetchApplicationUser(signal?: AbortSignal): Promise<ApplicationUser> {
  return v2Fetch<ApplicationUser>("/me", { signal }, 15_000);
}

export function updateApplicationUser(input: ProfileUpdateRequest, signal?: AbortSignal): Promise<ApplicationUser> {
  return v2Fetch<ApplicationUser>("/me", { method: "PATCH", body: JSON.stringify(input), signal }, 15_000);
}
