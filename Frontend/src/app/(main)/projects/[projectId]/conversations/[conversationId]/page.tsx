import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ProjectWorkspace } from "@/components/projects/project-workspace";
import { isUuid } from "@/lib/projects";

export const metadata: Metadata = { title: "Conversation" };

export default async function ConversationPage({ params }: { params: Promise<{ projectId: string; conversationId: string }> }) {
  const { projectId, conversationId } = await params;
  if (!isUuid(projectId) || !isUuid(conversationId)) notFound();
  return <ProjectWorkspace projectId={projectId} conversationId={conversationId} />;
}
