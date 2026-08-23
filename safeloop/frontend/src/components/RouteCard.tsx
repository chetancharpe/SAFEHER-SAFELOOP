import { CheckCircle2 } from "lucide-react";
import type { RouteOption } from "../types/api";
import { riskTone } from "../utils/format";

export default function RouteCard({ route, selected, onSelect }: { route: RouteOption; selected: boolean; onSelect: () => void }) {
  return (
    <button onClick={onSelect} className={`glass w-full rounded-[28px] p-5 text-left ${selected ? "border-mint/70 shadow-glow" : ""}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-black uppercase tracking-[0.25em] text-white/50">{route.label}</p>
          <div className="mt-3 flex items-end gap-3">
            <strong className="text-3xl">{route.duration_min} min</strong>
            <span className="pb-1 text-white/55">{route.distance_km} km</span>
          </div>
        </div>
        {route.recommended && <CheckCircle2 className="text-mint" />}
      </div>
      <div className="mt-5 grid grid-cols-2 gap-3">
        <div>
          <p className="text-xs uppercase text-white/45">Estimated Risk</p>
          <p className={`text-xl font-black ${riskTone(route.risk_level)}`}>{route.risk_level}</p>
        </div>
        <div>
          <p className="text-xs uppercase text-white/45">Safety Score</p>
          <p className="text-xl font-black">{route.safety_score}/100</p>
        </div>
      </div>
      <p className="mt-4 text-sm leading-6 text-white/62">{route.explanation}</p>
      <p className="mt-3 text-xs font-bold uppercase tracking-[0.18em] text-white/38">{route.data_label}</p>
    </button>
  );
}
