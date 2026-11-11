import { v2Fetch } from "@/services/v2http";
import type { JobStatus, ProcessingJob } from "@/lib/api-types";

const TERMINAL: ReadonlySet<JobStatus> = new Set(["succeeded", "failed", "cancelled"]);

export function isJobTerminal(job: Pick<ProcessingJob, "status">): boolean {
  return TERMINAL.has(job.status);
}

export function getJob(jobId: string, signal?: AbortSignal): Promise<ProcessingJob> {
  return v2Fetch<ProcessingJob>(`/jobs/${encodeURIComponent(jobId)}`, { signal }, 15_000);
}

export function jobStageLabel(stage: ProcessingJob["stage"]): string {
  switch (stage) {
    case "uploading": return "Uploading";
    case "extracting": return "Extracting text";
    case "chunking": return "Chunking";
    case "embedding": return "Embedding";
    case "indexing": return "Indexing";
    case "publishing": return "Publishing";
    case "deleting": return "Deleting";
    default: return "Processing";
  }
}
