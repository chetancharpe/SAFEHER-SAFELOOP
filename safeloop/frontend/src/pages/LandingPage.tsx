import { ArrowRight, Brain, LifeBuoy, Mic, Route, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";

const sections = [
  ["THE PROBLEM", "Students travelling alone need practical, fast safety support without unsupported guarantees."],
  ["HOW IT WORKS", "Enter a destination, compare lower-risk routes, start Safe Journey, and trigger emergency response when needed."],
  ["AI SAFER ROUTES", "RandomForest risk scoring or deterministic demo fallback estimates environmental risk from lighting, crowd, time, and environment factors."],
  ["ZERO-TOUCH SOS", "Browser-supported speech recognition listens only while Safe Journey is active, with a clearly labeled demo trigger."],
  ["EMERGENCY RESPONSE", "Trusted contacts receive DEMO NOTIFICATION messages and verified responders are prioritized by distance and response history."],
  ["SAFETY INTELLIGENCE", "Completed journeys become personal safety reports and stored-data insights."],
  ["PRIVACY", "Location, microphone, and contacts are scoped to the safety flow, with delete data and delete account controls."],
  ["FAQ", "SAFELOOP estimates environmental risk. It is not crime prediction and never guarantees safety."]
];

export default function LandingPage() {
  return (
    <div className="min-h-screen text-white">
      <header className="mx-auto flex max-w-7xl items-center justify-between px-5 py-6">
        <strong className="text-xl">SAFELOOP</strong>
        <nav className="flex gap-3">
          <Link to="/login" className="btn btn-ghost">Login</Link>
          <Link to="/demo" className="btn btn-primary">See Demo</Link>
        </nav>
      </header>
      <section className="mx-auto grid min-h-[82vh] max-w-7xl content-center gap-10 px-5 pb-12 lg:grid-cols-[1.1fr_0.9fr]">
        <div>
          <p className="font-black uppercase tracking-[0.35em] text-mint">Predict. Protect. Respond.</p>
          <h1 className="mt-5 max-w-4xl text-6xl font-black leading-[0.95] md:text-8xl">SAFELOOP</h1>
          <p className="mt-6 text-3xl font-bold text-white/85">Your AI Copilot for Safer Journeys.</p>
          <p className="mt-5 max-w-2xl text-xl leading-8 text-white/62">Choose safer routes. Detect potential emergencies. Get help when it matters.</p>
          <div className="mt-9 flex flex-wrap gap-4">
            <Link to="/app" className="btn btn-primary inline-flex items-center gap-2">START SAFE JOURNEY <ArrowRight size={18} /></Link>
            <Link to="/demo" className="btn btn-ghost">SEE DEMO</Link>
          </div>
        </div>
        <div className="glass grid content-between rounded-[32px] p-6">
          <div className="grid gap-4">
            {[
              [Route, "AI SafeRoute", "Lower estimated environmental risk route comparison."],
              [Mic, "Zero-Touch Voice SOS", "Code Red phrase while Safe Journey is active."],
              [LifeBuoy, "AI Emergency Response", "Trusted contacts and verified responder workflow."],
              [Brain, "Personal Safety Intelligence", "Journey report and stored-data insights."]
            ].map(([Icon, title, copy]) => (
              <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-5" key={String(title)}>
                <Icon className="text-mint" />
                <h3 className="mt-3 text-xl font-black">{String(title)}</h3>
                <p className="mt-2 text-white/58">{String(copy)}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      <section className="mx-auto grid max-w-7xl gap-4 px-5 pb-16 md:grid-cols-2">
        {sections.map(([title, copy]) => (
          <article className="glass rounded-[28px] p-6" key={title}>
            <ShieldCheck className="text-mint" />
            <h2 className="mt-4 text-xl font-black">{title}</h2>
            <p className="mt-2 leading-7 text-white/60">{copy}</p>
          </article>
        ))}
      </section>
      <section className="mx-auto max-w-7xl px-5 pb-20">
        <div className="glass rounded-[32px] p-8 text-center">
          <h2 className="text-4xl font-black">Start the hackathon story.</h2>
          <Link to="/demo" className="btn btn-primary mt-6 inline-flex">Run 3-minute demo</Link>
        </div>
      </section>
    </div>
  );
}
