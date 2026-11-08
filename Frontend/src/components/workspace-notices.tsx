"use client";

import { HardDrive, RotateCcw, WifiOff } from "lucide-react";
import { useWorkspace } from "@/components/providers/workspace-provider";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

export function WorkspaceNotices() {
  const connection = useWorkspace((state) => state.connectionStatus);
  const storageError = useWorkspace((state) => state.storageError);
  const checkConnection = useWorkspace((state) => state.checkConnection);
  const refreshDocuments = useWorkspace((state) => state.refreshDocuments);
  return (
    <div className="space-y-3 empty:hidden">
      {storageError ? <Alert variant="destructive"><HardDrive /><AlertTitle>Changes could not be saved</AlertTitle><AlertDescription>{storageError}</AlertDescription></Alert> : null}
      {connection === "offline" ? <Alert className="bg-card"><WifiOff /><AlertTitle className="flex items-center justify-between gap-3">PDF API is offline<Button variant="ghost" size="sm" onClick={() => void Promise.all([checkConnection(), refreshDocuments()])}><RotateCcw />Retry connection</Button></AlertTitle><AlertDescription>Your saved notebooks are available. Connect the backend to upload PDFs and ask questions.</AlertDescription></Alert> : null}
    </div>
  );
}
