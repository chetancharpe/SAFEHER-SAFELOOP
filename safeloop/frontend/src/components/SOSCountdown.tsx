import { useEffect, useState } from "react";

export default function SOSCountdown({ onCancel, onComplete }: { onCancel: () => void; onComplete: () => void }) {
  const [count, setCount] = useState(5);
  useEffect(() => {
    if (count === 0) {
      onComplete();
      return;
    }
    const timer = window.setTimeout(() => setCount((value) => value - 1), 1000);
    return () => window.clearTimeout(timer);
  }, [count, onComplete]);

  return (
    <div className="fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-red-950/95 p-6 text-center">
      <p className="text-sm font-black uppercase tracking-[0.35em] text-red-200">Possible Emergency Detected</p>
      <h1 className="mt-8 text-7xl font-black">{count}</h1>
      <p className="mt-4 text-xl font-bold">SOS activates in</p>
      <button onClick={onCancel} className="btn btn-ghost mt-10 min-w-52">I'M SAFE</button>
    </div>
  );
}
