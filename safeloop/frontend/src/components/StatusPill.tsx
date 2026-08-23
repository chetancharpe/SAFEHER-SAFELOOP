export default function StatusPill({ children, tone = "mint" }: { children: React.ReactNode; tone?: "mint" | "coral" | "amber" | "white" }) {
  const tones = {
    mint: "border-mint/35 bg-mint/10 text-mint",
    coral: "border-coral/35 bg-coral/10 text-coral",
    amber: "border-amber/35 bg-amber/10 text-amber",
    white: "border-white/20 bg-white/10 text-white"
  };
  return <span className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-black uppercase tracking-[0.2em] ${tones[tone]}`}>{children}</span>;
}
