export function riskTone(level: string) {
  if (level === "LOW") return "text-mint";
  if (level === "MODERATE") return "text-amber";
  return "text-coral";
}
