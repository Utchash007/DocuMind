import { ProjectLibrary } from "@/components/projects/project-library";
import { SiteFooter } from "@/components/site-footer";

export const metadata = { title: "Your projects" };

export default function ProjectsDashboardPage() {
  return <div className="flex min-h-dvh flex-col"><ProjectLibrary /><SiteFooter /></div>;
}
