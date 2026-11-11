import type { Document, ProcessingJob } from "@/lib/api-types";
import { projectScope } from "@/lib/projects";
import { deleteDocument, getDocument, listDocuments, retryDocument, uploadDocument, validatePdfFile } from "@/services/projects/documents";
import { getJob, isJobTerminal } from "@/services/projects/jobs";
import { fetchHealth } from "@/services/health/health";
import { isV2ApiError, newIdempotencyKey, v2ErrorMessage } from "@/services/v2http";
import { documentsReducer, emptyDocumentsPage, type DocumentsPage } from "@/store/documents/reducer";
import type { StoreSetter } from "@/store/types";
import type { WorkspaceStore } from "@/store/workspace-store";
import type { HealthResponse } from "@/lib/types";

export interface UploadTaskV2 {
  id: string;
  projectId: string;
  fileName: string;
  status: "waiting" | "uploading" | "processing" | "done" | "error";
  progress: number | null;
  jobId: string | null;
  documentId: string | null;
  message: string | null;
}

export interface DocumentsState {
  documentsByScope: Record<string, DocumentsPage>;
  jobsById: Record<string, ProcessingJob>;
  uploadQueue: UploadTaskV2[];
  isUploading: boolean;
  uploadingProjectId: string | null;
  connectionStatus: "checking" | "connected" | "offline";
  health: HealthResponse | null;
}

export const initialDocumentsState: DocumentsState = {
  documentsByScope: {},
  jobsById: {},
  uploadQueue: [],
  isUploading: false,
  uploadingProjectId: null,
  connectionStatus: "checking",
  health: null,
};

const TERMINAL_DOCUMENT: ReadonlySet<Document["status"]> = new Set(["Completed", "Failed"]);

export class DocumentsActions {
  readonly #set: StoreSetter<WorkspaceStore>;
  readonly #get: () => WorkspaceStore;
  readonly #requests = new Set<AbortController>();
  readonly #pollTimers = new Map<string, ReturnType<typeof setTimeout>>();
  readonly #pollAttempts = new Map<string, number>();
  readonly #pollControllers = new Map<string, AbortController>();
  readonly #uploadControllers = new Set<AbortController>();

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

  loadDocuments = async (projectId: string, options: { cursor?: string; reset?: boolean } = {}) => {
    const identity = this.#identityNow();
    if (!identity) return;
    const scope = projectScope(identity.userId, projectId);
    const previous = this.#get().documentsByScope[scope];
    if (previous?.status === "loading" && !options.reset) return;
    const controller = new AbortController();
    this.#requests.add(controller);
    this.#set((state) => ({
      documentsByScope: documentsReducer(state.documentsByScope, { type: "set-loading", scope }),
    }));
    try {
      const page = await listDocuments(projectId, { cursor: options.cursor, limit: 50, signal: controller.signal });
      if (!this.#current(identity.generation) || controller.signal.aborted) return;
      const items = options.reset || !options.cursor ? page.items : [...(previous?.items ?? []), ...page.items.filter((item) => !(previous?.items ?? []).some((existing) => existing.id === item.id))];
      this.#set((state) => ({
        documentsByScope: documentsReducer(state.documentsByScope, { type: "set-page", scope, page: { items, nextCursor: page.nextCursor, status: "ready", error: null } }),
        connectionStatus: "connected",
      }));
      for (const document of page.items) {
        if (!TERMINAL_DOCUMENT.has(document.status) && document.id) {
          // Ensure a job poll is running for pending documents when we know a job id.
          void document;
        }
      }
    } catch (error) {
      if (!this.#current(identity.generation) || controller.signal.aborted) return;
      this.#set((state) => ({
        documentsByScope: documentsReducer(state.documentsByScope, { type: "set-error", scope, error: v2ErrorMessage(error) }),
      }));
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

  uploadDocuments = async (files: File[], projectId: string) => {
    const identity = this.#identityNow();
    if (!identity || !files.length || this.#get().isUploading) return;
    const unique = [...new Map(files.map((file) => [file.name.toLowerCase(), file])).values()];
    const tasks: UploadTaskV2[] = unique.map((file) => ({
      id: crypto.randomUUID(), projectId, fileName: file.name, status: "waiting", progress: null, jobId: null, documentId: null, message: null,
    }));
    const controller = new AbortController();
    this.#uploadControllers.add(controller);
    this.#set({ isUploading: true, uploadingProjectId: projectId, uploadQueue: tasks });
    const generation = identity.generation;
    try {
      for (const [index, file] of unique.entries()) {
        if (controller.signal.aborted || !this.#current(generation)) return;
        const taskId = tasks[index].id;
        this.internal_dispatchUpload(taskId, { status: "uploading", message: "Uploading…" });
        const validationError = validatePdfFile(file);
        if (validationError) {
          this.internal_dispatchUpload(taskId, { status: "error", message: validationError });
          continue;
        }
        try {
          const acceptance = await uploadDocument(projectId, file, {
            idempotencyKey: newIdempotencyKey(),
            signal: controller.signal,
            onProgress: (loaded, total) => {
              if (controller.signal.aborted || !this.#current(generation)) return;
              this.internal_dispatchUpload(taskId, { progress: total > 0 ? Math.round((loaded / total) * 100) : null });
            },
          });
          if (controller.signal.aborted || !this.#current(generation)) return;
          const scope = projectScope(identity.userId, projectId);
          this.#set((state) => ({
            documentsByScope: documentsReducer(state.documentsByScope, { type: "upsert-document", scope, document: acceptance.document }),
            jobsById: { ...state.jobsById, [acceptance.job.id]: acceptance.job },
          }));
          this.internal_dispatchUpload(taskId, {
            status: "processing", progress: 100, jobId: acceptance.job.id, documentId: acceptance.document.id,
            message: "Stored — processing in the background.",
          });
          this.startJobPolling(acceptance.job.id, projectId);
          // Task completes once the job is terminal (polling updates it); mark uploaded now.
          this.internal_dispatchUpload(taskId, { status: "done", message: "Stored — processing in the background." });
        } catch (error) {
          if (controller.signal.aborted || !this.#current(generation)) return;
          this.internal_dispatchUpload(taskId, { status: "error", message: v2ErrorMessage(error) });
        }
      }
    } finally {
      this.#uploadControllers.delete(controller);
      if (!controller.signal.aborted && this.#current(generation)) {
        this.#set({ isUploading: false, uploadingProjectId: null });
      }
    }
  };

  retryDocumentTask = async (projectId: string, documentId: string) => {
    const identity = this.#identityNow();
    if (!identity) return;
    const acceptance = await retryDocument(projectId, documentId);
    if (!this.#current(identity.generation)) return;
    const scope = projectScope(identity.userId, projectId);
    this.#set((state) => ({
      documentsByScope: documentsReducer(state.documentsByScope, { type: "upsert-document", scope, document: acceptance.document }),
      jobsById: { ...state.jobsById, [acceptance.job.id]: acceptance.job },
    }));
    this.startJobPolling(acceptance.job.id, projectId);
  };

  deleteDocumentTask = async (projectId: string, documentId: string) => {
    const identity = this.#identityNow();
    if (!identity) return false;
    const result = await deleteDocument(projectId, documentId);
    if (!this.#current(identity.generation)) return false;
    const scope = projectScope(identity.userId, projectId);
    this.#set((state) => ({
      documentsByScope: documentsReducer(state.documentsByScope, { type: "remove-document", scope, documentId }),
    }));
    if (result.jobId) {
      this.#set((state) => ({ jobsById: { ...state.jobsById } }));
      this.startJobPolling(result.jobId, projectId);
    }
    return true;
  };

  clearUploadQueue = () => {
    if (!this.#get().isUploading) this.#set({ uploadQueue: [], uploadingProjectId: null });
  };

  // ---- Job polling: refresh-safe, backoff, terminal/session-loss shutdown (FE-01) ----

  startJobPolling = (jobId: string, projectId: string) => {
    const identity = this.#identityNow();
    if (!identity || !jobId) return;
    if (this.#pollTimers.has(jobId)) return;
    this.#pollAttempts.set(jobId, 0);
    this.#schedulePoll(jobId, projectId, identity.generation, 1200);
  };

  stopJobPolling = (jobId: string) => {
    const timer = this.#pollTimers.get(jobId);
    if (timer) clearTimeout(timer);
    this.#pollTimers.delete(jobId);
    this.#pollAttempts.delete(jobId);
    this.#pollControllers.get(jobId)?.abort();
    this.#pollControllers.delete(jobId);
  };

  #schedulePoll = (jobId: string, projectId: string, generation: number, delay: number) => {
    if (this.#pollTimers.has(jobId)) return;
    const timer = setTimeout(() => {
      this.#pollTimers.delete(jobId);
      void this.#pollStep(jobId, projectId, generation);
    }, delay);
    this.#pollTimers.set(jobId, timer);
  };

  #pollStep = async (jobId: string, projectId: string, generation: number) => {
    if (!this.#current(generation) || !this.#get().identity) return; // session-loss shutdown
    const identity = this.#identityNow();
    if (!identity) return;
    const controller = new AbortController();
    this.#pollControllers.set(jobId, controller);
    try {
      const job = await getJob(jobId, controller.signal);
      if (!this.#current(generation) || controller.signal.aborted) return;
      this.#set((state) => ({ jobsById: { ...state.jobsById, [job.id]: job } }));
      let terminal = isJobTerminal(job);
      if (job.targetDocumentId) {
        try {
          const document = await getDocument(projectId, job.targetDocumentId, controller.signal);
          if (!this.#current(generation)) return;
          const scope = projectScope(identity.userId, projectId);
          this.#set((state) => ({
            documentsByScope: documentsReducer(state.documentsByScope, { type: "upsert-document", scope, document }),
          }));
          if (TERMINAL_DOCUMENT.has(document.status)) terminal = true;
          // Deletion jobs tombstone the document; absence (404) is terminal too.
        } catch (error) {
          if (isV2ApiError(error) && error.status === 404) terminal = true;
          else if (!isJobTerminal(job)) {
            // Transient: reschedule with backoff.
            const attempt = (this.#pollAttempts.get(jobId) ?? 0) + 1;
            this.#pollAttempts.set(jobId, attempt);
            this.#schedulePoll(jobId, projectId, generation, Math.min(2000 * 1.5 ** attempt, 15000));
            return;
          }
        }
      }
      if (terminal) {
        this.#pollAttempts.delete(jobId);
        // Sync upload task message for this job.
        const queue = this.#get().uploadQueue;
        for (const task of queue) {
          if (task.jobId === jobId && task.status !== "error") {
            this.internal_dispatchUpload(task.id, {
              status: job.status === "succeeded" ? "done" : "error",
              message: job.status === "succeeded" ? "Processing completed." : job.lastErrorMessage || "Processing failed. You can retry this document.",
            });
          }
        }
        return;
      }
      const attempt = (this.#pollAttempts.get(jobId) ?? 0) + 1;
      this.#pollAttempts.set(jobId, attempt);
      this.#schedulePoll(jobId, projectId, generation, Math.min(2000 * 1.5 ** attempt, 15000));
    } catch {
      if (!this.#current(generation) || controller.signal.aborted) return;
      const attempt = (this.#pollAttempts.get(jobId) ?? 0) + 1;
      this.#pollAttempts.set(jobId, attempt);
      this.#schedulePoll(jobId, projectId, generation, Math.min(2000 * 1.5 ** attempt, 15000));
    } finally {
      if (this.#pollControllers.get(jobId) === controller) this.#pollControllers.delete(jobId);
    }
  };

  internal_cancelDocumentRequests = () => {
    for (const controller of this.#requests) controller.abort();
    this.#requests.clear();
    for (const controller of this.#uploadControllers) controller.abort();
    this.#uploadControllers.clear();
    for (const jobId of [...this.#pollTimers.keys()]) this.stopJobPolling(jobId);
    this.#set({ ...initialDocumentsState, connectionStatus: this.#get().connectionStatus === "offline" ? "offline" : "checking" });
  };

  internal_dispatchDocuments = (action: Parameters<typeof documentsReducer>[1]) =>
    this.#set((state) => ({ documentsByScope: documentsReducer(state.documentsByScope, action) }));

  internal_dispatchUpload = (id: string, update: Partial<UploadTaskV2>) =>
    this.#set((state) => ({ uploadQueue: state.uploadQueue.map((task) => (task.id === id ? { ...task, ...update } : task)) }));
}

export type DocumentsAction = Pick<DocumentsActions, keyof DocumentsActions>;
export { emptyDocumentsPage };
