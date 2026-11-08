import type { DocumentInfo, HealthResponse, UploadTask } from "@/lib/types";
import { uploadFilename } from "@/lib/documents";
import { errorMessage } from "@/services/api/api";
import { fetchDocuments, uploadDocument } from "@/services/documents/documents";
import { fetchHealth } from "@/services/health/health";
import type { StoreSetter } from "@/store/types";
import type { WorkspaceStore } from "@/store/workspace-store";

export interface DocumentsState {
  documents: DocumentInfo[];
  documentsStatus: "idle" | "loading" | "ready" | "error";
  documentsError: string | null;
  connectionStatus: "checking" | "connected" | "offline";
  health: HealthResponse | null;
  uploadDialogOpen: boolean;
  isUploading: boolean;
  uploadQueue: UploadTask[];
  uploadNotebookId: string | null;
}

export const initialDocumentsState: DocumentsState = {
  documents: [],
  documentsStatus: "idle",
  documentsError: null,
  connectionStatus: "checking",
  health: null,
  uploadDialogOpen: false,
  isUploading: false,
  uploadQueue: [],
  uploadNotebookId: null,
};

type DocumentsUpdate = { type: "replace"; documents: DocumentInfo[] } | { type: "upsert"; document: DocumentInfo };

function documentsReducer(documents: DocumentInfo[], action: DocumentsUpdate) {
  if (action.type === "replace") {
    return action.documents.map((document) => ({ ...documents.find((item) => item.filename === document.filename), ...document }));
  }
  return [action.document, ...documents.filter((document) => document.filename !== action.document.filename)];
}

export class DocumentsActions {
  readonly #set: StoreSetter<WorkspaceStore>;
  readonly #get: () => WorkspaceStore;
  readonly #requests = new Set<AbortController>();

  constructor(set: StoreSetter<WorkspaceStore>, get: () => WorkspaceStore) {
    this.#set = set;
    this.#get = get;
  }

  setUploadDialogOpen = (open: boolean) => this.#set({ uploadDialogOpen: open });

  refreshDocuments = async () => {
    if (this.#get().documentsStatus === "loading" || this.#get().isUploading) return;
    const controller = new AbortController();
    this.#requests.add(controller);
    this.#set({ documentsStatus: "loading", documentsError: null });
    try {
      const documents = await fetchDocuments(controller.signal);
      if (controller.signal.aborted) return;
      this.internal_dispatchDocuments({ type: "replace", documents });
      this.#set({ documentsStatus: "ready", connectionStatus: "connected" });
    } catch (error) {
      if (controller.signal.aborted) return;
      this.#set({ documentsStatus: "error", documentsError: errorMessage(error) });
    } finally {
      this.#requests.delete(controller);
    }
  };

  checkConnection = async () => {
    const controller = new AbortController();
    this.#requests.add(controller);
    this.#set({ connectionStatus: "checking" });
    try {
      const health = await fetchHealth(controller.signal);
      if (controller.signal.aborted) return;
      this.#set({ connectionStatus: "connected", health });
    } catch {
      if (controller.signal.aborted) return;
      this.#set({ connectionStatus: "offline", health: null });
    } finally {
      this.#requests.delete(controller);
    }
  };

  uploadDocuments = async (files: File[], notebookId: string) => {
    if (!files.length || this.#get().isUploading || !this.#get().notebooksMap[notebookId]) return;
    const unique = [...new Map(files.map((file) => [uploadFilename(file.name), file])).values()];
    const uploadQueue: UploadTask[] = unique.map((file) => ({ id: crypto.randomUUID(), filename: uploadFilename(file.name), status: "waiting" }));
    const controller = new AbortController();
    this.#requests.add(controller);
    this.#set({ isUploading: true, uploadQueue, uploadNotebookId: notebookId });

    try {
      for (const [index, file] of unique.entries()) {
        if (controller.signal.aborted) return;
        const id = uploadQueue[index].id;
        this.internal_dispatchUpload(id, { status: "processing" });
        try {
          if (!/\.pdf$/i.test(file.name)) throw new Error("Only PDF documents are supported.");
          if (file.size === 0) throw new Error("This file is empty. Choose a PDF with text.");
          const document = await uploadDocument(file, controller.signal);
          if (controller.signal.aborted) return;
          this.internal_dispatchDocuments({ type: "upsert", document });
          this.#get().addNotebookSources(notebookId, [document.filename]);
          this.internal_dispatchUpload(id, { status: "done", message: `${document.chunksCount ?? 0} text chunks indexed` });
          this.#set({ documentsStatus: "ready", documentsError: null, connectionStatus: "connected" });
        } catch (error) {
          if (controller.signal.aborted) return;
          this.internal_dispatchUpload(id, { status: "error", message: errorMessage(error) });
        }
      }
    } finally {
      this.#requests.delete(controller);
      if (!controller.signal.aborted) this.#set({ isUploading: false });
    }
  };

  internal_cancelDocumentRequests = () => {
    for (const controller of this.#requests) controller.abort();
    this.#requests.clear();
    this.#set(initialDocumentsState);
  };

  clearUploadQueue = () => {
    if (!this.#get().isUploading) this.#set({ uploadQueue: [], uploadNotebookId: null });
  };

  internal_dispatchDocuments = (action: DocumentsUpdate) => {
    this.#set((state) => ({ documents: documentsReducer(state.documents, action) }));
  };

  internal_dispatchUpload = (id: string, update: Partial<UploadTask>) => {
    this.#set((state) => ({ uploadQueue: state.uploadQueue.map((task) => task.id === id ? { ...task, ...update } : task) }));
  };
}

export type DocumentsAction = Pick<DocumentsActions, keyof DocumentsActions>;
