import { useEffect, useState } from "react";
import SafeMap from "../components/SafeMap";
import StatusPill from "../components/StatusPill";
import { api } from "../services/api";
import { useWebSocket } from "../hooks/useWebSocket";

export default function ResponderDashboard() {
  const [events, setEvents] = useState<any[]>([]);
  const [status, setStatus] = useState("");
  const liveEvents = useWebSocket();

  async function load() {
    const data = await api<any[]>("/api/responders/emergencies");
    setEvents(data);
  }
  async function accept(id: number) {
    const data = await api<any>(`/api/responders/${id}/accept`, { method: "POST" });
    setStatus(`RESPONDER EN ROUTE: ${data.eta_min} min ETA`);
    await load();
  }
  async function resolve(id: number) {
    await api(`/api/sos/${id}/resolve`, { method: "POST" });
    setStatus("SOS resolved");
    await load();
  }
  useEffect(() => { load(); }, [liveEvents.length]);

  return (
    <section className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
      <div>
        <StatusPill tone="amber">Responder Dashboard</StatusPill>
        <h1 className="mt-4 text-4xl font-black">ACTIVE EMERGENCIES</h1>
        {status && <p className="mt-4 rounded-2xl bg-mint/10 p-3 text-mint">{status}</p>}
        <div className="mt-6 grid gap-4">
          {events.length === 0 && <p className="glass rounded-3xl p-5 text-white/60">No active emergencies.</p>}
          {events.map((event) => (
            <article className="glass rounded-[28px] p-5" key={event.id}>
              <p className="text-white/50">Emergency</p>
              <h2 className="mt-2 text-2xl font-black">User: Anonymous Student</h2>
              <p className="mt-2">Distance: {event.distance_m}m</p>
              <p>Status: {event.status.toUpperCase()}</p>
              <div className="mt-4 flex gap-3">
                <button className="btn btn-primary" onClick={() => accept(event.id)}>ACCEPT SOS</button>
                <button className="btn btn-ghost" onClick={() => resolve(event.id)}>RESOLVE</button>
              </div>
            </article>
          ))}
        </div>
      </div>
      <SafeMap />
    </section>
  );
}
