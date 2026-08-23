import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../store/auth";

export default function RegisterPage() {
  const { register, loading } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "user" });
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const user = await register(form.name, form.email, form.password, form.role);
      navigate(user.role === "responder" ? "/responder" : "/app");
    } catch (err: any) {
      setError(err.message);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center px-4 text-white">
      <form onSubmit={submit} className="glass w-full max-w-md rounded-[32px] p-7">
        <h1 className="text-4xl font-black">Create account.</h1>
        {error && <p className="mt-4 rounded-2xl bg-coral/15 p-3 text-coral">{error}</p>}
        {["name", "email", "password"].map((field) => (
          <label key={field} className="mt-4 block text-sm font-bold capitalize text-white/55">
            {field}
            <input className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 p-4" type={field === "password" ? "password" : "text"} value={(form as any)[field]} onChange={(e) => setForm({ ...form, [field]: e.target.value })} />
          </label>
        ))}
        <select className="mt-5 w-full rounded-2xl border border-white/10 bg-panel p-4" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
          <option value="user">Student user</option>
          <option value="responder">Verified responder</option>
        </select>
        <button className="btn btn-primary mt-6 w-full" disabled={loading}>{loading ? "Creating..." : "Register"}</button>
      </form>
    </main>
  );
}
