import type {
  CursorPageParams, PaginatedResponse, Project, ProjectCreateRequest,
  ProjectDeleteAccepted, ProjectUpdateRequest,
} from "@/lib/api-types";
import { queryString, v2Fetch } from "@/services/v2http";

const seg = (id: string) => encodeURIComponent(id);

export function listProjects(params: CursorPageParams & { signal?: AbortSignal } = {}): Promise<PaginatedResponse<Project>> {
  return v2Fetch<PaginatedResponse<Project>>(`/projects${queryString({ cursor: params.cursor, limit: params.limit ?? 50 })}`, { signal: params.signal });
}

export function createProject(input: ProjectCreateRequest, signal?: AbortSignal): Promise<Project> {
  return v2Fetch<Project>("/projects", { method: "POST", body: JSON.stringify(input), signal }, 30_000);
}

export function getProject(projectId: string, signal?: AbortSignal): Promise<Project> {
  return v2Fetch<Project>(`/projects/${seg(projectId)}`, { signal });
}

export function updateProject(projectId: string, input: ProjectUpdateRequest, signal?: AbortSignal): Promise<Project> {
  return v2Fetch<Project>(`/projects/${seg(projectId)}`, { method: "PATCH", body: JSON.stringify(input), signal }, 30_000);
}

/** 202 while cleanup is pending; allow a 204-style empty success as accepted. */
export async function deleteProject(projectId: string, signal?: AbortSignal): Promise<ProjectDeleteAccepted> {
  const result = await v2Fetch<ProjectDeleteAccepted | undefined>(`/projects/${seg(projectId)}`, { method: "DELETE", signal }, 30_000);
  return result ?? { projectId, accepted: true };
}
