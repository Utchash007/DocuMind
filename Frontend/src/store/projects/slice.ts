import type {
  Project, ProjectCreateRequest,
} from "@/lib/api-types";
import { projectScope } from "@/lib/projects";
import { createProject, deleteProject, getProject, listProjects, updateProject } from "@/services/projects/projects";
import { isV2ApiError, v2ErrorMessage } from "@/services/v2http";
import { emptyProjectsPage, projectsReducer, removeProjectMaps, type ProjectsPage } from "@/store/projects/reducer";
import type { StoreSetter } from "@/store/types";
import type { WorkspaceStore } from "@/store/workspace-store";

export interface ProjectsState {
  projectsByUser: Record<string, ProjectsPage>;
  projectDetailByUser: Record<string, Project>;
}

export const initialProjectsState: ProjectsState = {
  projectsByUser: {},
  projectDetailByUser: {},
};

export class ProjectsActions {
  readonly #set: StoreSetter<WorkspaceStore>;
  readonly #get: () => WorkspaceStore;
  readonly #requests = new Map<string, AbortController>();

  constructor(set: StoreSetter<WorkspaceStore>, get: () => WorkspaceStore) {
    this.#set = set;
    this.#get = get;
  }

  #identityNow(): { userId: string; generation: number } | null {
    const { identity, identityGeneration } = this.#get();
    return identity ? { userId: identity, generation: identityGeneration } : null;
  }

  #current(generation: number): boolean {
    return this.#get().identityGeneration === generation;
  }

  loadProjects = async (options: { cursor?: string; reset?: boolean } = {}) => {
    const identity = this.#identityNow();
    if (!identity) return;
    const scope = projectScope(identity.userId, "list");
    const previous = this.#get().projectsByUser[scope];
    if (previous?.status === "loading" && !options.reset) return;
    const controller = new AbortController();
    this.#requests.set(scope, controller);
    this.#set((state) => ({
      projectsByUser: projectsReducer(state.projectsByUser, { type: "set-loading", scope }),
    }));
    try {
      const page = await listProjects({ cursor: options.cursor, limit: 50, signal: controller.signal });
      if (!this.#current(identity.generation) || controller.signal.aborted) return;
      const items = options.reset || !options.cursor ? page.items : [...(previous?.items ?? []), ...page.items.filter((item) => !(previous?.items ?? []).some((existing) => existing.id === item.id))];
      this.#set((state) => ({
        projectsByUser: projectsReducer(state.projectsByUser, {
          type: "set-page", scope, page: { items, nextCursor: page.nextCursor, status: "ready", error: null },
        }),
      }));
    } catch (error) {
      if (!this.#current(identity.generation) || controller.signal.aborted) return;
      this.#set((state) => ({
        projectsByUser: projectsReducer(state.projectsByUser, { type: "set-error", scope, error: v2ErrorMessage(error) }),
      }));
    } finally {
      if (this.#requests.get(scope) === controller) this.#requests.delete(scope);
    }
  };

  refreshProjects = () => this.loadProjects({ reset: true });

  loadProjectDetail = async (projectId: string) => {
    const identity = this.#identityNow();
    if (!identity) return null;
    const key = projectScope(identity.userId, projectId);
    const controller = new AbortController();
    this.#requests.set(key, controller);
    try {
      const project = await getProject(projectId, controller.signal);
      if (!this.#current(identity.generation) || controller.signal.aborted) return null;
      this.#set((state) => ({
        projectDetailByUser: { ...state.projectDetailByUser, [key]: project },
        projectsByUser: projectsReducer(state.projectsByUser, { type: "upsert", scope: projectScope(identity.userId, "list"), project }),
      }));
      return project;
    } catch (error) {
      if (!this.#current(identity.generation) || controller.signal.aborted) return null;
      throw new Error(v2ErrorMessage(error));
    } finally {
      if (this.#requests.get(key) === controller) this.#requests.delete(key);
    }
  };

  createProject = async (input: ProjectCreateRequest): Promise<Project | null> => {
    const identity = this.#identityNow();
    if (!identity) return null;
    const name = input.name.trim().slice(0, 255);
    if (!name) return null;
    try {
      const project = await createProject({ name, description: input.description ?? null });
      if (!this.#current(identity.generation)) return null;
      this.#set((state) => ({
        projectDetailByUser: { ...state.projectDetailByUser, [projectScope(identity.userId, project.id)]: project },
        projectsByUser: projectsReducer(state.projectsByUser, { type: "upsert", scope: projectScope(identity.userId, "list"), project }),
      }));
      return project;
    } catch (error) {
      if (isV2ApiError(error) && (error.code === "onboarding_required" || error.code === "unauthenticated")) throw error;
      throw new Error(v2ErrorMessage(error));
    }
  };

  renameProject = async (projectId: string, name: string): Promise<Project | null> => {
    const identity = this.#identityNow();
    if (!identity) return null;
    const trimmed = name.trim().slice(0, 255);
    if (!trimmed) return null;
    const project = await updateProject(projectId, { name: trimmed });
    if (!this.#current(identity.generation)) return null;
    this.#set((state) => ({
      projectDetailByUser: { ...state.projectDetailByUser, [projectScope(identity.userId, project.id)]: project },
      projectsByUser: projectsReducer(state.projectsByUser, { type: "upsert", scope: projectScope(identity.userId, "list"), project }),
    }));
    return project;
  };

  updateProjectDescription = async (projectId: string, description: string | null): Promise<Project | null> => {
    const identity = this.#identityNow();
    if (!identity) return null;
    const project = await updateProject(projectId, { description });
    if (!this.#current(identity.generation)) return null;
    this.#set((state) => ({
      projectDetailByUser: { ...state.projectDetailByUser, [projectScope(identity.userId, project.id)]: project },
      projectsByUser: projectsReducer(state.projectsByUser, { type: "upsert", scope: projectScope(identity.userId, "list"), project }),
    }));
    return project;
  };

  deleteProject = async (projectId: string): Promise<boolean> => {
    const identity = this.#identityNow();
    if (!identity) return false;
    await deleteProject(projectId);
    if (!this.#current(identity.generation)) return false;
    this.#set((state) => ({
      projectsByUser: projectsReducer(state.projectsByUser, { type: "remove", scope: projectScope(identity.userId, "list"), projectId }),
      projectDetailByUser: removeProjectMaps(state.projectDetailByUser, projectId),
    }));
    return true;
  };

  internal_cancelProjectRequests = () => {
    for (const controller of this.#requests.values()) controller.abort();
    this.#requests.clear();
  };

  internal_dispatchProjects = (action: Parameters<typeof projectsReducer>[1]) =>
    this.#set((state) => ({ projectsByUser: projectsReducer(state.projectsByUser, action) }));
}

export type ProjectsAction = Pick<ProjectsActions, keyof ProjectsActions>;
export { emptyProjectsPage };
