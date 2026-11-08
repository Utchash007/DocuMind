import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { NotebookWorkspace } from "@/components/notebooks/notebook-workspace";

export const metadata: Metadata = { title: "Notebook workspace" };

export default async function NotebookPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!/^[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12}$/i.test(id)) notFound();
  return <NotebookWorkspace notebookId={id} />;
}
