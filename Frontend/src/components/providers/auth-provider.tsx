"use client";

import { createContext, use, useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import type { ApplicationUser } from "@/lib/api-types";
import type { AuthUser } from "@/lib/types";
import { authErrorMessage, createEmailCodeSession, deleteCurrentSession, fetchSessionContext } from "@/services/auth/auth";

interface AuthState {
  user: AuthUser | null;
  appUser: ApplicationUser | null;
  loading: boolean;
  error: string | null;
}

interface AuthContextValue {
  state: AuthState;
  actions: {
    refreshSession: () => Promise<void>;
    signIn: (userId: string, code: string) => Promise<ApplicationUser | null>;
    signOut: () => Promise<void>;
  };
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  // Appwrite configuration is validated by the server. Always restore the
  // session, including deployments with only server-side environment values.
  const [state, setState] = useState<AuthState>({ user: null, appUser: null, loading: true, error: null });
  const generation = useRef(0);
  const mutating = useRef(false);

  const loadSession = useCallback(async () => {
    const request = ++generation.current;
    try {
      const context = await fetchSessionContext();
      if (request === generation.current) setState({ user: context.user, appUser: context.appUser, loading: false, error: null });
      return context;
    } catch (error) {
      if (request === generation.current) setState((current) => ({ ...current, loading: false, error: authErrorMessage(error) }));
      return null;
    }
  }, []);

  const refreshSession = useCallback(async () => {
    if (!mutating.current) await loadSession();
  }, [loadSession]);

  useEffect(() => {
    void refreshSession();
    const onFocus = () => { void refreshSession(); };
    window.addEventListener("focus", onFocus);
    return () => {
      generation.current += 1;
      window.removeEventListener("focus", onFocus);
    };
  }, [refreshSession]);

  const signIn = useCallback(async (userId: string, code: string) => {
    if (mutating.current) return null;
    mutating.current = true;
    generation.current += 1;
    try {
      await createEmailCodeSession(userId, code);
      const context = await loadSession();
      if (context?.user && !context.appUser) {
        setState((current) => ({ ...current, error: current.error || "Your code was accepted, but your workspace could not be restored. Check your session again." }));
        return null;
      }
      return context?.appUser ?? null;
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
      setState({ user: null, appUser: null, loading: false, error: null });
    } finally {
      mutating.current = false;
    }
  }, []);

  const value = useMemo(() => ({ state, actions: { refreshSession, signIn, signOut } }), [state, refreshSession, signIn, signOut]);
  return <AuthContext value={value}>{children}</AuthContext>;
}

export function useAuth() {
  const auth = use(AuthContext);
  if (!auth) throw new Error("Account components must be inside AuthProvider.");
  return auth;
}
