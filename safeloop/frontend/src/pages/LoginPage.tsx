import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../store/auth";

export default function LoginPage() {
  const { login, loading } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("Password123!");
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const user = await login(email, password);
      navigate(user.role === "responder" ? "/responder" : "/app");
    } catch (err: any) {
      setError(err.message);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center px-4 text-white">
      <form onSubmit={submit} className="glass w-full max-w-md rounded-[32px] p-7">
        <h1 className="text-4xl font-black">Welcome back.</h1>
        <p className="mt-2 text-white/55">Login to continue your SAFELOOP journey.</p>
        {error && <p className="mt-4 rounded-2xl bg-coral/15 p-3 text-coral">{error}</p>}
        <label className="mt-6 block text-sm font-bold text-white/55">Email</label>
        <input className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 p-4" value={email} onChange={(e) => setEmail(e.target.value)} />
        <label className="mt-4 block text-sm font-bold text-white/55">Password</label>
        <input className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 p-4" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button className="btn btn-primary mt-6 w-full" disabled={loading}>{loading ? "Signing in..." : "Login"}</button>
        <p className="mt-5 text-center text-sm text-white/55">No account? <Link className="text-mint" to="/register">Register</Link></p>
      </form>
    </main>
  );
}
