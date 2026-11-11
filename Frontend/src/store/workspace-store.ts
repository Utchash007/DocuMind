import { createStore } from "zustand/vanilla";
import type { ApplicationUser } from "@/lib/api-types";
import { ConversationsActions, initialConversationsState, type ConversationsAction, type ConversationsState } from "@/store/conversations/slice";
import { DocumentsActions, initialDocumentsState, type DocumentsAction, type DocumentsState } from "@/store/documents/slice";
import { flattenActions } from "@/store/flatten-actions";
import { NotesActions, initialNotesState, type NotesAction, type NotesState } from "@/store/notes/slice";
import { ProjectsActions, initialProjectsState, type ProjectsAction, type ProjectsState } from "@/store/projects/slice";
import type { StoreSetter } from "@/store/types";

export interface IdentityState {
  identity: string | null;
  identityGeneration: number;
  applicationUser: ApplicationUser | null;
}

export const initialIdentityState: IdentityState = {
  identity: null,
  identityGeneration: 0,
  applicationUser: null,
};

export type WorkspaceStore =
  IdentityState & ProjectsState & ProjectsAction & DocumentsState & DocumentsAction &
  ConversationsState & ConversationsAction & NotesState & NotesAction & {
    setIdentity: (identity: string | null) => void;
    setApplicationUser: (user: ApplicationUser | null) => void;
    resetWorkspaceForIdentity: (identity: string | null) => void;
  };

export function createWorkspaceStore() {
  const identityActions = (set: StoreSetter<WorkspaceStore>, get: () => WorkspaceStore) => ({
    setIdentity: (identity: string | null) => {
      const current = get().identity;
      if (current === identity) return;
      // Synchronous isolation (FE-02): abort everything, bump generation so
      // late completions are rejected, and clear all in-memory server data
      // BEFORE any new fetch can start for the next identity.
      get().internal_cancelProjectRequests();
      get().internal_cancelDocumentRequests();
      get().internal_cancelConversations();
      set({
        ...initialProjectsState,
        ...initialDocumentsState,
        ...initialConversationsState,
        notes: [],
        drafts: {},
        notesOwner: null,
        identity,
        identityGeneration: get().identityGeneration + 1,
      });
      get().loadNotesForUser(identity);
    },
    setApplicationUser: (user: ApplicationUser | null) => set({ applicationUser: user }),
    resetWorkspaceForIdentity: (identity: string | null) => get().setIdentity(identity),
  });

  const store = createStore<WorkspaceStore>()((set, get) => ({
    ...initialIdentityState,
    ...initialProjectsState,
    ...initialDocumentsState,
    ...initialConversationsState,
    ...initialNotesState,
    ...flattenActions(new ProjectsActions(set, get)),
    ...flattenActions(new DocumentsActions(set, get)),
    ...flattenActions(new ConversationsActions(set, get)),
    ...flattenActions(new NotesActions(set, get)),
    ...identityActions(set, get),
  }));
  return store;
}

export type WorkspaceStoreApi = ReturnType<typeof createWorkspaceStore>;
