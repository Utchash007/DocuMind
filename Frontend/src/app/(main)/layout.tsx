import type { ReactNode } from "react";
import { RequireAuth } from "@/components/auth/require-auth";

export default function MainLayout({ children }: { children: ReactNode }) {
  return <RequireAuth><div className="min-h-dvh">{children}</div></RequireAuth>;
}
