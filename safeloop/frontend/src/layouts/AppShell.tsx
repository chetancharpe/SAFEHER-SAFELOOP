import { Link, NavLink, Outlet } from "react-router-dom";
import { LogOut, Shield } from "lucide-react";
import { useAuth } from "../store/auth";

export default function AppShell() {
  const { user, logout } = useAuth();
  return (
    <div className="min-h-screen text-white">
      <header className="sticky top-0 z-50 border-b border-white/10 bg-ink/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4">
          <Link to="/app" className="flex items-center gap-3">
            <span className="rounded-2xl bg-mint/15 p-2 text-mint"><Shield /></span>
            <span><strong>SAFELOOP</strong><small className="block text-xs text-white/45">Predict. Protect. Respond.</small></span>
          </Link>
          <nav className="hidden items-center gap-4 text-sm font-bold text-white/60 md:flex">
            <NavLink to="/app">Journey</NavLink>
            <NavLink to="/insights">Insights</NavLink>
            <NavLink to="/privacy">Privacy</NavLink>
            {user?.role !== "user" && <NavLink to="/responder">Responder</NavLink>}
          </nav>
          <button onClick={logout} className="rounded-full border border-white/15 p-3" aria-label="Logout"><LogOut size={18} /></button>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6"><Outlet /></main>
    </div>
  );
}
