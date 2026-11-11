"use client";

import { createContext, use, useEffect, useRef, useState, type ReactNode } from "react";
import { useStore } from "zustand";
import { useAuth } from "@/components/providers/auth-provider";
import { createWorkspaceStore, type WorkspaceStore, type WorkspaceStoreApi } from "@/store/workspace-store";
import { fetchApplicationUser } from "@/services/users/me";
import { errorCodeOf } from "@/services/v2http";
import { projectScope } from "@/lib/projects";

const WorkspaceContext = createContext<WorkspaceStoreApi | null>(null);

function identityOf(state: { user: { id: string } | null; loading: boolean; error: string | null }): string | null {
  if (state.loading || state.error || !state.user) return null;
  return state.user.id;
}

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const { state } = useAuth();
  const userId = identityOf(state);
  const [store] = useState(createWorkspaceStore);
  const lastIdentity = useRef<string | null | undefined>(undefined);
  const onboarded = useRef(true);

  useEffect(() => {
    if (lastIdentity.current === undefined) {
      lastIdentity.current = userId;
      return;
    }
    if (lastIdentity.current !== userId) {
      lastIdentity.current = userId;
      store.getState().setIdentity(userId);
    }
  }, [store, userId]);

  // Initial identity (mount with an already-signed-in user).
  useEffect(() => {
    if (userId && !store.getState().identity) {
      store.getState().setIdentity(userId);
    }
  }, [store, userId]);

  useEffect(() => {
    if (!userId) {
      store.getState().setIdentity(null);
      return;
    }
    let cancelled = false;
    const controller = new AbortController();
    // Bootstrap the internal application user (A2 /me). Fail-open for the
    // Appwrite identity so the workspace still renders if /me is not yet
    // deployed; 403 onboarding_required is surfaced via the store.
    void (async () => {
      try {
        const applicationUser = await fetchApplicationUser(controller.signal);
        if (cancelled || controller.signal.aborted) return;
        if (store.getState().identity !== userId) return;
        onboarded.current = applicationUser.onboardingCompleted;
        store.getState().setApplicationUser(applicationUser);
      } catch (error) {
        if (cancelled || controller.signal.aborted) return;
        if (errorCodeOf(error) === "onboarding_required") {
          onboarded.current = false;
          store.getState().setApplicationUser(null);
        }
      }
    })();
    store.getState().checkConnection();
    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [store, userId]);

  useEffect(() => {
    return () => {
      store.getState().internal_cancelProjectRequests();
      store.getState().internal_cancelDocumentRequests();
      store.getState().internal_cancelConversations();
    };
  }, [store]);

  return <WorkspaceContext value={store}>{children}</WorkspaceContext>;
}

export function useWorkspace<T>(selector: (state: WorkspaceStore) => T): T {
  const store = use(WorkspaceContext);
  if (!store) throw new Error("Workspace components must be inside WorkspaceProvider.");
  return useStore(store, selector);
}

/** Narrow selector helpers (rerender-* / js-* best practices). */
export function useProjectsPage() {
  const identity = useWorkspace((state) => state.identity);
  return useWorkspace((state) => (identity ? state.projectsByUser[projectScope(identity, "list")] : undefined));
}

export function useProjectDetail(projectId: string) {
  const identity = useWorkspace((state) => state.identity);
  return useWorkspace((state) => (identity ? state.projectDetailByUser[projectScope(identity, projectId)] : undefined));
}
