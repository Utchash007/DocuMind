"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";
import { CircleHelp, HardDrive, Loader2, LogOut, MoreVertical } from "lucide-react";
import { toast } from "sonner";
import { authErrorMessage } from "@/services/auth/auth";
import { useAuth } from "@/components/providers/auth-provider";
import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";

export function AccountMenu({ variant = "compact" }: { variant?: "compact" | "sidebar" }) {
  const { state, actions } = useAuth();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [pending, startTransition] = useTransition();
  if (!state.user) return null;
  const label = state.user.name || state.user.email;
  const initial = Array.from(label)[0]?.toUpperCase() || "U";

  function signOut() {
    startTransition(async () => {
      try {
        await actions.signOut();
        setOpen(false);
        router.replace("/sign-in");
        toast.success("Signed out.");
      } catch (error) {
        toast.error(authErrorMessage(error));
      }
    });
  }

  return (
    <>
      <DropdownMenu open={open} onOpenChange={setOpen}>
        <DropdownMenuTrigger asChild>
          {variant === "sidebar" ? (
            <Button variant="ghost" aria-label="Account menu" className="h-auto w-full justify-start gap-3 rounded-xl p-2.5 text-left"><span className="flex size-9 shrink-0 items-center justify-center rounded-full border border-sidebar-border bg-secondary text-xs font-medium">{initial}</span><span className="min-w-0 flex-1"><span className="block truncate text-xs font-medium">{label}</span><span className="mt-1 block text-[10px] font-normal text-muted-foreground">Your account</span></span><MoreVertical className="size-4 text-muted-foreground" /></Button>
          ) : (
            <Button variant="outline" size="icon" aria-label="Account menu" className="ml-1 size-9 rounded-full bg-secondary font-medium text-foreground/75">{initial}</Button>
          )}
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-64 p-1.5">
          <DropdownMenuLabel className="px-2 py-2.5">
            <span className="block truncate text-sm font-semibold text-foreground" title={label}>{label}</span>
            {state.user.name ? <span className="mt-1 block truncate font-normal">{state.user.email}</span> : null}
            <span className="mt-1 flex items-center gap-1.5 font-normal"><HardDrive className="size-3" />Projects on server · notes on this device</span>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem asChild className="py-2"><Link href="/help"><CircleHelp />Help & getting started</Link></DropdownMenuItem>
          <DropdownMenuItem disabled={pending} onSelect={(event) => { event.preventDefault(); signOut(); }} className="py-2">{pending ? <Loader2 className="animate-spin" /> : <LogOut />}{pending ? "Signing out..." : "Sign out"}</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </>
  );
}
