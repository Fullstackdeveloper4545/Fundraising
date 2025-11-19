"use client";
import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { AuthAPI, LoginResponse } from "@/lib/api";

interface AuthState {
  token: string | null;
  user: LoginResponse["user"] | null;
  loading: boolean;
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  loginWithResponse: (response: LoginResponse) => void;
  register: (data: { email: string; password: string; first_name: string; last_name: string; phone?: string; referral_code?: string }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<LoginResponse["user"] | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const stored = typeof window !== "undefined" ? window.localStorage.getItem("auth") : null;
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as { token: string; user: LoginResponse["user"] };
        setToken(parsed.token);
        setUser(parsed.user);
      } catch {
        // ignore
      }
    }
    setLoading(false);
  }, []);

  const persist = useCallback((next: { token: string; user: LoginResponse["user"] } | null) => {
    if (next) {
      window.localStorage.setItem("auth", JSON.stringify(next));
    } else {
      window.localStorage.removeItem("auth");
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await AuthAPI.login({ email, password });
    setToken(res.access_token);
    setUser(res.user);
    persist({ token: res.access_token, user: res.user });
  }, [persist]);

  const loginWithResponse = useCallback((response: LoginResponse) => {
    setToken(response.access_token);
    setUser(response.user);
    persist({ token: response.access_token, user: response.user });
  }, [persist]);

  const register = useCallback(async (data: { email: string; password: string; first_name: string; last_name: string; phone?: string; referral_code?: string }) => {
    await AuthAPI.register(data);
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    persist(null);
  }, [persist]);

  const value = useMemo<AuthContextValue>(() => ({ token, user, loading, login, loginWithResponse, register, logout }), [token, user, loading, login, loginWithResponse, register, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}


