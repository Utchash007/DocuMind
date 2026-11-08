import { createStore } from "zustand/vanilla";
import { createJSONStorage, persist } from "zustand/middleware";
import { ChatActions, initialChatState, type ChatAction, type ChatState } from "@/store/chat/slice";
import { DocumentsActions, initialDocumentsState, type DocumentsAction, type DocumentsState } from "@/store/documents/slice";
import { flattenActions } from "@/store/flatten-actions";
import { NotebooksActions, initialNotebooksState, type NotebooksAction, type NotebooksState } from "@/store/notebooks/slice";
import { restoreWorkspace } from "@/store/persistence";

export type WorkspaceStore = DocumentsState & DocumentsAction & ChatState & ChatAction & NotebooksState & NotebooksAction;

export function createWorkspaceStore() {
  let reportStorageError: () => void = () => {};
  const store = createStore<WorkspaceStore>()(
    persist(
      (set, get) => ({
        ...initialDocumentsState,
        ...initialChatState,
        ...initialNotebooksState,
        ...flattenActions(new DocumentsActions(set, get)),
        ...flattenActions(new ChatActions(set, get)),
        ...flattenActions(new NotebooksActions(set, get)),
      }),
      {
        name: "notemind-workspace",
        version: 1,
        storage: createJSONStorage(() => ({
          getItem: (name) => {
            try { return localStorage.getItem(name); } catch { reportStorageError(); return null; }
          },
          setItem: (name, value) => {
            try { localStorage.setItem(name, value); } catch { reportStorageError(); }
          },
          removeItem: (name) => {
            try { localStorage.removeItem(name); } catch { reportStorageError(); }
          },
        })),
        skipHydration: true,
        partialize: (state) => ({ notebooksMap: state.notebooksMap, threadsMap: state.threadsMap, notesMap: state.notesMap, errorsMap: state.errorsMap }),
        merge: restoreWorkspace,
        onRehydrateStorage: () => (_state, error) => { if (error) reportStorageError(); },
      },
    ),
  );
  reportStorageError = () => queueMicrotask(() => {
    if (!store.getState().storageError) store.getState().reportStorageError();
  });
  return store;
}

export type WorkspaceStoreApi = ReturnType<typeof createWorkspaceStore>;
