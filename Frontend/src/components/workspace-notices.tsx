"use client";

import { HardDrive, RotateCcw, WifiOff } from "lucide-react";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

export function WorkspaceNotices() {
  const connection = useWorkspace((state) => state.connectionStatus);
  const storageError = useWorkspace((state) => state.storageError);
  const checkConnection = useWorkspace((state) => state.checkConnection);
  const refreshProjects = useWorkspace((state) => state.refreshProjects);
  return (
    <div className="space-y-3 empty:hidden">
      {storageError ? <Alert variant="destructive"><HardDrive /><AlertTitle>Notes could not be saved</AlertTitle><AlertDescription>{storageError}</AlertDescription></Alert> : null}
      {connection === "offline" ? <Alert className="bg-card"><WifiOff /><AlertTitle className="flex items-center justify-between gap-3">API is offline<Button variant="ghost" size="sm" onClick={() => void Promise.all([checkConnection(), refreshProjects()])}><RotateCcw />Retry connection</Button></AlertTitle><AlertDescription>Your projects and conversations need the server. Local notes and drafts remain available on this device.</AlertDescription></Alert> : null}
    </div>
  );
}
