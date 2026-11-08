"use client";

import { createContext, use, useEffect, useRef, useState, type ReactNode } from "react";
import { useStore } from "zustand";
import { useAuth } from "@/components/providers/auth-provider";
import { createWorkspaceStore, type WorkspaceStore, type WorkspaceStoreApi } from "@/store/workspace-store";

const WorkspaceContext = createContext<WorkspaceStoreApi | null>(null);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const { state } = useAuth();
  const userId = !state.loading && !state.error ? state.user?.id : undefined;
  const [store] = useState(createWorkspaceStore);
  const hydration = useRef<Promise<void> | null>(null);

  useEffect(() => {
    if (!userId) return;
    let active = true;
    hydration.current ??= Promise.resolve(store.persist.rehydrate());
    void hydration.current.catch(() => { if (active) store.getState().reportStorageError(); }).finally(() => { if (active) store.getState().finishHydration(); });
    void store.getState().refreshDocuments();
    void store.getState().checkConnection();
    return () => {
      active = false;
      store.getState().internal_cancelDocumentRequests();
      store.getState().internal_cancelChatRequests();
    };
  }, [store, userId]);

  return <WorkspaceContext value={store}>{children}</WorkspaceContext>;
}

export function useWorkspace<T>(selector: (state: WorkspaceStore) => T): T {
  const store = use(WorkspaceContext);
  if (!store) throw new Error("Workspace components must be inside WorkspaceProvider.");
  return useStore(store, selector);
}
