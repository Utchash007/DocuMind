import type { Metadata } from "next";
import type { ReactNode } from "react";
import { AppProviders } from "@/components/providers/app-providers";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "NoteMind — Your research, connected", template: "%s | NoteMind" },
  description: "A thoughtful home for your research. Bring your sources together, ask better questions, and keep what matters.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="font-sans antialiased">
        <a href="#main-content" className="fixed top-3 left-3 z-[100] -translate-y-24 rounded-lg bg-primary px-4 py-2 text-primary-foreground focus:translate-y-0">Skip to content</a>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
