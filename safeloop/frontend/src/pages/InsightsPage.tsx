import { useEffect, useState } from "react";
import { api } from "../services/api";

export default function InsightsPage() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    api("/api/insights").then(setData).catch((err) => setError(err.message));
  }, []);
  if (error) return <p className="rounded-3xl bg-coral/15 p-5 text-coral">{error}</p>;
  if (!data) return <p className="glass rounded-3xl p-5">Loading safety overview...</p>;
  const stats = [
    ["Average Safety Score", `${data.average_safety_score}/100`],
    ["Journeys Completed", data.journeys_completed],
    ["High-Risk Segments", data.high_risk_segments],
    ["SOS Events", data.sos_events]
  ];
  return (
    <section>
      <h1 className="text-4xl font-black">SAFETY OVERVIEW</h1>
      <div className="mt-6 grid gap-4 md:grid-cols-4">
        {stats.map(([label, value]) => (
          <div className="glass rounded-[28px] p-5" key={label}>
            <p className="text-white/50">{label}</p>
            <strong className="mt-3 block text-3xl">{value}</strong>
            <div className="mt-5 h-2 rounded-full bg-white/10"><div className="h-2 rounded-full bg-mint" style={{ width: `${Math.min(100, Number.parseInt(String(value)) || 24)}%` }} /></div>
          </div>
        ))}
      </div>
      <div className="glass mt-6 rounded-[28px] p-6">
        <h2 className="text-2xl font-black">Personalized insights</h2>
        {data.insights.map((item: string) => <p className="mt-3 text-lg text-white/70" key={item}>{item}</p>)}
      </div>
    </section>
  );
}
