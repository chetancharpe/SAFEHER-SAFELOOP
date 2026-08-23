import { useState } from "react";
import { useNavigate } from "react-router-dom";
import RouteCard from "../components/RouteCard";
import SafeMap from "../components/SafeMap";
import SOSCountdown from "../components/SOSCountdown";
import StatusPill from "../components/StatusPill";
import { api } from "../services/api";
import { useAuth } from "../store/auth";
import type { RouteOption } from "../types/api";

export default function DemoPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [routes, setRoutes] = useState<RouteOption[]>([]);
  const [selected, setSelected] = useState<RouteOption | null>(null);
  const [journeyId, setJourneyId] = useState<number | null>(null);
  const [sosId, setSosId] = useState<number | null>(null);
  const [countdown, setCountdown] = useState(false);
  const [message, setMessage] = useState("");
  const [report, setReport] = useState<any>(null);

  async function runLogin() {
    await login("demo@example.com", "Password123!");
    setMessage("Logged in as demo user.");
    setStep(2);
  }
  async function compare() {
    const data = await api<{ routes: RouteOption[] }>("/api/routes/compare", { method: "POST", body: JSON.stringify({ origin: "College", destination: "Home", demo: true }) });
    setRoutes(data.routes);
    setSelected(data.routes.find((route) => route.mode === "safeloop") ?? data.routes[0]);
    setStep(3);
  }
  async function start() {
    const data = await api<any>("/api/journeys", { method: "POST", body: JSON.stringify({ destination: "Home", selected_mode: "safeloop", route: selected }) });
    setJourneyId(data.journey.id);
    setStep(4);
  }
  async function sos() {
    setCountdown(false);
    const data = await api<any>("/api/sos", { method: "POST", body: JSON.stringify({ trigger_type: "voice_command", journey_id: journeyId }) });
    setSosId(data.event.id);
    setMessage(`Location shared. ${data.trusted_contacts_notified} trusted contacts notified. ${data.nearby_responders.length} responders found.`);
    setStep(5);
  }
  async function responderAccept() {
    await login("responder@example.com", "Password123!");
    await api(`/api/responders/${sosId}/accept`, { method: "POST" });
    setMessage("RESPONDER EN ROUTE. ETA 3 min.");
    setStep(6);
  }
  async function resolve() {
    await api(`/api/sos/${sosId}/resolve`, { method: "POST" });
    await login("demo@example.com", "Password123!");
    const data = await api<any>(`/api/journeys/${journeyId}/complete`, { method: "POST", body: JSON.stringify({ status: "completed" }) });
    setReport(data.report);
    setStep(7);
  }

  return (
    <main className="min-h-screen px-4 py-6 text-white">
      {countdown && <SOSCountdown onCancel={() => setCountdown(false)} onComplete={sos} />}
      <div className="mx-auto max-w-7xl">
        <StatusPill>3-minute judge demo</StatusPill>
        <h1 className="mt-4 text-5xl font-black">SAFELOOP Demo: College → Home</h1>
        <p className="mt-3 text-white/60">All demo data is deterministic and labeled as demo environmental data.</p>
        {message && <p className="mt-5 rounded-3xl bg-mint/10 p-4 text-mint">{message}</p>}
        <div className="mt-8 grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <section className="glass rounded-[32px] p-6">
            <ol className="space-y-4 text-lg">
              <li className={step >= 1 ? "text-white" : "text-white/35"}>1. Login as demo user.</li>
              <li className={step >= 2 ? "text-white" : "text-white/35"}>2. Enter College → Home and compare routes.</li>
              <li className={step >= 3 ? "text-white" : "text-white/35"}>3. Select SAFELOOP route and start Safe Journey.</li>
              <li className={step >= 4 ? "text-white" : "text-white/35"}>4. Click DEMO VOICE TRIGGER and wait 5 seconds.</li>
              <li className={step >= 5 ? "text-white" : "text-white/35"}>5. Switch to responder and accept.</li>
              <li className={step >= 6 ? "text-white" : "text-white/35"}>6. Resolve SOS.</li>
              <li className={step >= 7 ? "text-white" : "text-white/35"}>7. Generate Journey Safety Report.</li>
            </ol>
            <div className="mt-8 grid gap-3">
              {step === 1 && <button className="btn btn-primary" onClick={runLogin}>Login as demo user</button>}
              {step === 2 && <button className="btn btn-primary" onClick={compare}>Compare routes</button>}
              {step === 3 && <button className="btn btn-primary" onClick={start}>Start Safe Journey</button>}
              {step === 4 && <button className="btn btn-danger" onClick={() => setCountdown(true)}>DEMO VOICE TRIGGER</button>}
              {step === 5 && <button className="btn btn-primary" onClick={responderAccept}>Open responder dashboard and accept</button>}
              {step === 6 && <button className="btn btn-ghost" onClick={resolve}>Resolve SOS</button>}
              {step === 7 && <button className="btn btn-primary" onClick={() => navigate("/insights")}>Show insights dashboard</button>}
            </div>
            {report && (
              <div className="mt-6 rounded-3xl bg-white/8 p-5">
                <h2 className="text-2xl font-black">JOURNEY COMPLETE</h2>
                <p>Safety Score: {report.safety_score}/100</p>
                <p>Estimated Risk: {report.estimated_risk}</p>
                <p>Risk factors: Lighting Good, Crowd Moderate, Time Moderate, Environment Good.</p>
                <p>Personal insight: This completed route had lower estimated environmental risk than the fastest option.</p>
              </div>
            )}
          </section>
          <section className="grid gap-5">
            <SafeMap route={selected ?? undefined} />
            <div className="grid gap-4 md:grid-cols-3">
              {routes.map((route) => <RouteCard key={route.mode} route={route} selected={selected?.mode === route.mode} onSelect={() => setSelected(route)} />)}
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
