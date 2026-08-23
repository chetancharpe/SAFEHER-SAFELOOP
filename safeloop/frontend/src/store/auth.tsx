import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api } from "../services/api";
import type { User } from "../types/api";

type AuthContextValue = {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<User>;
  register: (name: string, email: string, password: string, role?: string) => Promise<User>;
  logout: () => void;
  setUser: (user: User | null) => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const raw = localStorage.getItem("safeloop_user");
    return raw ? JSON.parse(raw) : null;
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("safeloop_token"));
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) localStorage.setItem("safeloop_user", JSON.stringify(user));
    else localStorage.removeItem("safeloop_user");
  }, [user]);

  async function login(email: string, password: string) {
    setLoading(true);
    try {
      const data = await api<{ access_token: string; user: User }>("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password })
      });
      localStorage.setItem("safeloop_token", data.access_token);
      setToken(data.access_token);
      setUser(data.user);
      return data.user;
    } finally {
      setLoading(false);
    }
  }

  async function register(name: string, email: string, password: string, role = "user") {
    setLoading(true);
    try {
      const data = await api<{ access_token: string; user: User }>("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({ name, email, password, role })
      });
      localStorage.setItem("safeloop_token", data.access_token);
      setToken(data.access_token);
      setUser(data.user);
      return data.user;
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    localStorage.removeItem("safeloop_token");
    localStorage.removeItem("safeloop_user");
    setToken(null);
    setUser(null);
  }

  const value = useMemo(() => ({ user, token, loading, login, register, logout, setUser }), [user, token, loading]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
