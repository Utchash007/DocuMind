"use client";

import { createContext, use, useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import type { AuthUser } from "@/lib/types";
import { authConfigured, authErrorMessage, createEmailCodeSession, deleteCurrentSession, fetchCurrentUser } from "@/services/auth/auth";

interface AuthState {
  user: AuthUser | null;
  loading: boolean;
  error: string | null;
}

interface AuthContextValue {
  state: AuthState;
  actions: {
    refreshSession: () => Promise<void>;
    signIn: (userId: string, code: string) => Promise<boolean>;
    signOut: () => Promise<void>;
  };
  meta: { configured: boolean };
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ user: null, loading: authConfigured, error: null });
  const generation = useRef(0);
  const mutating = useRef(false);

  const loadSession = useCallback(async () => {
    const request = ++generation.current;
    try {
      const user = await fetchCurrentUser();
      if (request === generation.current) setState({ user, loading: false, error: null });
      return user;
    } catch (error) {
      if (request === generation.current) setState((current) => ({ ...current, loading: false, error: authErrorMessage(error) }));
      return null;
    }
  }, []);

  const refreshSession = useCallback(async () => {
    if (authConfigured && !mutating.current) await loadSession();
  }, [loadSession]);

  useEffect(() => {
    if (!authConfigured) return;
    void refreshSession();
    const onFocus = () => { void refreshSession(); };
    window.addEventListener("focus", onFocus);
    return () => {
      generation.current += 1;
      window.removeEventListener("focus", onFocus);
    };
  }, [refreshSession]);

  const signIn = useCallback(async (userId: string, code: string) => {
    if (mutating.current) return false;
    mutating.current = true;
    generation.current += 1;
    try {
      await createEmailCodeSession(userId, code);
      const user = await loadSession();
      if (!user) setState((current) => ({ ...current, error: current.error || "Your code was accepted, but the session could not be restored. Check your session again." }));
      return Boolean(user);
    } finally {
      mutating.current = false;
    }
  }, [loadSession]);

  const signOut = useCallback(async () => {
    if (mutating.current) throw new Error("Please wait for the current account request to finish.");
    mutating.current = true;
    generation.current += 1;
    try {
      await deleteCurrentSession();
      setState({ user: null, loading: false, error: null });
    } finally {
      mutating.current = false;
    }
  }, []);

  const value = useMemo(() => ({ state, actions: { refreshSession, signIn, signOut }, meta: { configured: authConfigured } }), [state, refreshSession, signIn, signOut]);
  return <AuthContext value={value}>{children}</AuthContext>;
}

export function useAuth() {
  const auth = use(AuthContext);
  if (!auth) throw new Error("Account components must be inside AuthProvider.");
  return auth;
}
