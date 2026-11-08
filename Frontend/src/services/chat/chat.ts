import type { AnswerResponse } from "@/lib/types";
import { apiFetch } from "@/services/api/api";

export async function sendQuery(query: string, filenames: string[], signal?: AbortSignal) {
  if (!filenames.length) throw new Error("Add a PDF source to this notebook before asking a question.");
  const form = new FormData();
  form.append("query", query);
  for (const filename of filenames) form.append(filenames.length === 1 ? "filename" : "filenames", filename);

  const result = await apiFetch<AnswerResponse>("/query", { method: "POST", body: form, signal }, 120_000);
  if (typeof result.answer !== "string" || !Array.isArray(result.citations) || result.citations.some((citation) =>
    !citation || typeof citation.sentence !== "string" || !Number.isInteger(citation.page) || citation.page < 1 ||
    (citation.filename != null && typeof citation.filename !== "string"),
  )) {
    throw new Error("The answer could not be read. Please try your question again.");
  }
  return result;
}
