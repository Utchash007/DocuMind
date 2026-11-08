import { NotebookLibrary } from "@/components/library/notebook-library";
import { SiteFooter } from "@/components/site-footer";

export default function LibraryPage() {
  return <div className="flex min-h-dvh flex-col"><NotebookLibrary /><SiteFooter /></div>;
}
