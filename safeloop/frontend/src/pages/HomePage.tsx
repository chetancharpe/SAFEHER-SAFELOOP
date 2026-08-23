import { FormEvent, useEffect, useMemo, useState } from "react";
import { AlertTriangle, Mic, Navigation, Star } from "lucide-react";
import RouteCard from "../components/RouteCard";
import SafeMap from "../components/SafeMap";
import SOSCountdown from "../components/SOSCountdown";
import StatusPill from "../components/StatusPill";
import { api } from "../services/api";
import { useAuth } from "../store/auth";
import type { EmergencyState, Journey, RouteOption } from "../types/api";
import { useWebSocket } from "../hooks/useWebSocket";

declare global {
  interface Window { webkitSpeechRecognition?: any; SpeechRecognition?: any }
}

export default function HomePage() {
  const { user } = useAuth();
  const events = useWebSocket();
  const [destination, setDestination] = useState("Home");
  const [routes, setRoutes] = useState<RouteOption[]>([]);
  const [selected, setSelected] = useState<RouteOption | null>(null);
  const [journey, setJourney] = useState<Journey | null>(null);
  const [countdown, setCountdown] = useState(false);
  const [emergency, setEmergency] = useState<EmergencyState | null>(null);
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState("");
  const [error, setError] = useState("");
  const [voiceStatus, setVoiceStatus] = useState("Not started");

  const accepted = useMemo(() => {
    const acceptedEvents = events.filter((event) => event.event === "sos_accepted");
    return acceptedEvents[acceptedEvents.length - 1];
  }, [events]);

  async function compare(event?: FormEvent) {
    event?.preventDefault();
    setError("");
    setLoading("Calculating routes...");
    try {
      const data = await api<{ routes: RouteOption[] }>("/api/routes/compare", { method: "POST", body: JSON.stringify({ destination, demo: destination.toLowerCase().includes("home") }) });
      setRoutes(data.routes);
      setSelected(data.routes.find((route) => route.recommended) ?? data.routes[0]);
    } catch (err: any) {
      setError(err.message || "Location permission is required to calculate your current route.");
    } finally {
      setLoading("");
    }
  }

  async function startJourney() {
    if (!selected) return;
    setLoading("Starting Safe Journey...");
    try {
      const data = await api<{ journey: Journey }>("/api/journeys", { method: "POST", body: JSON.stringify({ destination, selected_mode: selected.mode, route: selected }) });
      setJourney(data.journey);
      startVoiceMonitoring();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading("");
    }
  }

  function startVoiceMonitoring() {
    const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Speech || !user?.microphone_enabled) {
      setVoiceStatus("Demo trigger available");
      return;
    }
    try {
      const recognition = new Speech();
      recognition.continuous = true;
      recognition.onresult = (event: any) => {
        const transcript = Array.from(event.results).map((result: any) => result[0].transcript).join(" ").toLowerCase();
        if (transcript.includes(user.emergency_phrase.toLowerCase())) setCountdown(true);
      };
      recognition.start();
      setVoiceStatus("ACTIVE");
    } catch {
      setVoiceStatus("Demo trigger available");
    }
  }

  async function createSOS(trigger_type = "voice_command") {
    setCountdown(false);
    const data = await api<any>("/api/sos", { method: "POST", body: JSON.stringify({ trigger_type, journey_id: journey?.id }) });
    setEmergency({ id: data.event.id, status: data.event.status, trusted_contacts_notified: data.trusted_contacts_notified, nearby_responders: data.nearby_responders });
  }

  async function resolveSOS() {
    if (emergency) await api(`/api/sos/${emergency.id}/resolve`, { method: "POST" });
    if (journey) {
      const data = await api<any>(`/api/journeys/${journey.id}/complete`, { method: "POST", body: JSON.stringify({ status: "completed" }) });
      setReport(data.report);
    }
    setEmergency(null);
  }

  async function submitFeedback(rating: number) {
    await api("/api/feedback", { method: "POST", body: JSON.stringify({ journey_id: journey?.id, rating, route_useful: true, score_made_sense: true, would_use_again: true }) });
  }

  useEffect(() => { compare(); }, []);

  if (emergency) {
    return (
      <section className="grid gap-5 lg:grid-cols-[1fr_0.8fr]">
        <div className="rounded-[32px] border border-red-400/30 bg-red-950/70 p-7">
          <StatusPill tone="coral">SOS ACTIVE</StatusPill>
          <h1 className="mt-6 text-5xl font-black">Your location has been shared.</h1>
          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            <div className="glass rounded-3xl p-5"><p>Trusted contacts</p><strong className="text-3xl">{emergency.trusted_contacts_notified} notified</strong></div>
            <div className="glass rounded-3xl p-5"><p>Nearby responders</p><strong className="text-3xl">{emergency.nearby_responders.length} notified</strong></div>
          </div>
          <div className="mt-6 rounded-3xl bg-white/10 p-5">
            <p className="text-white/55">Responder status</p>
            <h2 className="mt-2 text-3xl font-black">{accepted ? "RESPONDER ACCEPTED" : "SEARCHING..."}</h2>
            <p className="mt-2">{accepted ? `Distance: ${accepted.payload.distance_m}m. ETA: ${accepted.payload.eta_min} min.` : "Smart responder prioritization is notifying verified responders."}</p>
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            <a className="btn btn-ghost" href="tel:+10000000001">CALL CONTACT</a>
            <button className="btn btn-primary" onClick={resolveSOS}>RESOLVE EMERGENCY</button>
          </div>
        </div>
        <SafeMap route={selected ?? undefined} />
      </section>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
      {countdown && <SOSCountdown onCancel={() => setCountdown(false)} onComplete={() => createSOS("voice_command")} />}
      <section className="glass rounded-[32px] p-6">
        <p className="font-black uppercase tracking-[0.35em] text-mint">AI Personal Safety Copilot</p>
        <h1 className="mt-5 text-4xl font-black">Good evening.</h1>
        <form onSubmit={compare} className="mt-6">
          <label className="text-sm font-bold text-white/55">Where are you going?</label>
          <input value={destination} onChange={(e) => setDestination(e.target.value)} className="mt-2 w-full rounded-3xl border border-white/10 bg-white/5 p-5 text-xl" />
          <button className="btn btn-primary mt-4 w-full" disabled={!!loading}>{loading || "START SAFE JOURNEY"}</button>
        </form>
        {error && <p className="mt-4 rounded-2xl bg-coral/15 p-3 text-coral">{error}</p>}
        {selected && (
          <div className="mt-6 grid grid-cols-2 gap-4">
            <div className="rounded-3xl bg-white/5 p-5"><p>Safety Score</p><strong className="text-3xl">{selected.safety_score}/100</strong></div>
            <div className="rounded-3xl bg-white/5 p-5"><p>Risk</p><strong className="text-3xl">{selected.risk_level}</strong></div>
          </div>
        )}
        {journey && (
          <div className="mt-6 rounded-3xl border border-mint/25 bg-mint/10 p-5">
            <StatusPill>SAFE JOURNEY ACTIVE</StatusPill>
            <p className="mt-4">MICROPHONE: <strong>{voiceStatus}</strong></p>
            <p>Phrase: <strong>"{user?.emergency_phrase ?? "Code Red"}"</strong></p>
            <div className="mt-4 flex flex-wrap gap-3">
              <button className="btn btn-danger inline-flex gap-2" onClick={() => createSOS("manual")}><AlertTriangle /> EMERGENCY SOS</button>
              <button className="btn btn-ghost inline-flex gap-2" onClick={() => setCountdown(true)}><Mic /> DEMO TRIGGER</button>
            </div>
          </div>
        )}
        {report && (
          <div className="mt-6 rounded-3xl bg-white/8 p-5">
            <h2 className="text-2xl font-black">JOURNEY COMPLETE</h2>
            <p className="mt-2">Distance: {report.distance_km} km. Duration: {report.duration_min} min.</p>
            <p>Safety Score: {report.safety_score}/100. Estimated Risk: {report.estimated_risk}</p>
            <p className="mt-2">Personal insight: Your SAFELOOP route completed with lower estimated environmental risk.</p>
            <div className="mt-4 flex gap-1">{[1,2,3,4,5].map((star) => <button key={star} onClick={() => submitFeedback(star)} aria-label={`${star} stars`}><Star className="fill-amber text-amber" /></button>)}</div>
          </div>
        )}
      </section>
      <section className="grid gap-5">
        <SafeMap route={selected ?? undefined} />
        <div className="grid gap-4 md:grid-cols-3">
          {routes.map((route) => <RouteCard key={route.mode} route={route} selected={selected?.mode === route.mode} onSelect={() => setSelected(route)} />)}
        </div>
        {selected && !journey && <button onClick={startJourney} className="btn btn-primary inline-flex items-center justify-center gap-2"><Navigation /> Start Safe Journey</button>}
      </section>
    </div>
  );
}
