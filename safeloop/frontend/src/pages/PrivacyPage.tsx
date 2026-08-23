import { useState } from "react";
import { api } from "../services/api";
import { useAuth } from "../store/auth";

export default function PrivacyPage() {
  const { logout } = useAuth();
  const [message, setMessage] = useState("");
  async function deleteData() {
    const data = await api<{ message: string }>("/api/privacy/delete-data", { method: "POST" });
    setMessage(data.message);
  }
  async function deleteAccount() {
    const data = await api<{ message: string }>("/api/privacy/delete-account", { method: "DELETE" });
    setMessage(data.message);
    logout();
  }
  return (
    <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
      <div>
        <h1 className="text-4xl font-black">Privacy</h1>
        <p className="mt-4 max-w-2xl text-lg leading-8 text-white/65">SAFELOOP collects location during route comparison, Safe Journey, and SOS response. Browser microphone access is used only while the Safe Journey page is active and only with permission. Trusted contacts are used for emergency notifications. Demo notifications are clearly labeled.</p>
      </div>
      <div className="glass rounded-[32px] p-6">
        <h2 className="text-2xl font-black">Data controls</h2>
        {message && <p className="mt-4 rounded-2xl bg-mint/10 p-3 text-mint">{message}</p>}
        <button onClick={deleteData} className="btn btn-ghost mt-6 w-full">DELETE MY DATA</button>
        <button onClick={deleteAccount} className="btn btn-danger mt-4 w-full">DELETE MY ACCOUNT</button>
      </div>
    </section>
  );
}
