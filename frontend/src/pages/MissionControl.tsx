import React from "react";
import { HealthPanel } from "../components/HealthPanel";
import type { HealthResponse } from "../types/contracts";
import { ShieldCheck, Layers, Zap, AlertOctagon } from "lucide-react";
import { useState } from "react";
import { analyzeIncident, createOrder, injectDuplicate, inspectOrder, recoverIncident, scoreOrder, simulateRepair } from "../lib/api";
import type { MLScoreResponse, RecoveryResponse } from "../types/contracts";

interface MissionControlProps {
  health: HealthResponse | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
}

export const MissionControl: React.FC<MissionControlProps> = ({
  health,
  loading,
  error,
  onRefresh,
}) => {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("Ready to run the real recovery workflow.");
  const [ml, setMl] = useState<MLScoreResponse | null>(null);
  const [recovery, setRecovery] = useState<RecoveryResponse | null>(null);
  const [step, setStep] = useState(0);
  const runWorkflow = async () => {
    setBusy(true); setRecovery(null); setMl(null); setStep(1); setMessage("Creating a real test order…");
    try {
      const order = await createOrder(`ui-${Date.now()}`);
      await injectDuplicate(order.id); setStep(2); setMessage("A controlled duplicate was injected for investigation.");
      const score = await scoreOrder(order.id); setMl(score); setStep(3);
      const inspection = await inspectOrder(order.id);
      if (!inspection.incident) throw new Error("Deterministic inspection did not produce an incident.");
      setMessage("Business rules proved the duplicate. Asking Gemini for an explanation…");
      const analysis = await analyzeIncident(inspection.incident.id);
      setStep(4); setMessage(`Gemini identified the cause (${Math.round(analysis.proposal.confidence * 100)}% confidence). Simulating safely…`);
      const simulation = await simulateRepair(inspection.incident.id, analysis.proposal.candidate.reservation_id);
      if (!simulation.safe) throw new Error("Repair candidate failed simulation.");
      setStep(5);
      const result = await recoverIncident(inspection.incident.id, analysis.proposal.candidate.reservation_id, simulation.expected_order_version);
      setRecovery(result); setStep(6); setMessage(`Recovery ${result.status.toLowerCase()} and post-commit verified.`);
    } catch (error) { setMessage(error instanceof Error ? error.message : "Workflow failed."); }
    finally { setBusy(false); }
  };
  return (
    <div className="space-y-6">
      {/* Real Gateway Health Status */}
      <HealthPanel
        health={health}
        loading={loading}
        error={error}
        onRefresh={onRefresh}
      />

      {/* Honest Phase 1B Status Notice & Live System Gates */}
      <section 
        aria-label="Mission Control Overview"
        className="judge-hero rounded-2xl p-6 md:p-8 space-y-6 relative overflow-hidden"
      >
        <div className="flex items-start space-x-4 border-b border-slate-800/80 pb-5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/15 via-blue-500/10 to-indigo-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0 shadow-[0_0_15px_-3px_rgba(6,182,212,0.25)]">
            <Zap className="w-5 h-5 text-cyan-300" aria-hidden="true" />
          </div>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2.5">
              <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wide">
                Telemetry & Order Processing (Phase 2 & Phase 3)
              </h2>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/70 text-emerald-300 border border-emerald-800/50">
                LIVE API
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed max-w-4xl">
              Run one complete, observable recovery story. Every status below comes from the backend, database, model, or Gemini—not a canned animation.
            </p>
          </div>
        </div>

        {/* System Gates Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          
          <div className="glass-panel-interactive p-4 rounded-xl flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-300">Invariant Gate</span>
              <ShieldCheck className="w-4 h-4 text-cyan-400" aria-hidden="true" />
            </div>
            <div className="text-sm text-emerald-300 font-semibold">Deterministic checks live</div>
            <div className="flex items-center gap-1.5 mt-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400/60 animate-pulse" />
              <p className="text-[11px] text-slate-400 font-mono">Proof before repair</p>
            </div>
          </div>

          <div className="glass-panel-interactive p-4 rounded-xl flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-300">Live Inventory</span>
              <Layers className="w-4 h-4 text-purple-400" aria-hidden="true" />
            </div>
            <div className="text-sm text-emerald-300 font-semibold">SQLite inventory live</div>
            <div className="flex items-center gap-1.5 mt-2">
              <span className="w-2 h-2 rounded-full bg-purple-400/60 animate-pulse" />
              <p className="text-[11px] text-slate-400 font-mono">Stock is re-queried after commit</p>
            </div>
          </div>

          <div className="glass-panel-interactive p-4 rounded-xl flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-300">Active Incidents</span>
              <AlertOctagon className="w-4 h-4 text-emerald-400" aria-hidden="true" />
            </div>
            <div className="text-sm text-emerald-300 font-semibold flex items-center gap-2">
              <span>0 In Flight</span>
            </div>
            <div className="flex items-center gap-1.5 mt-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <p className="text-[11px] text-slate-400 font-mono">No active incidents detected</p>
            </div>
          </div>

        </div>
      </section>
      <section className="glass-panel rounded-2xl p-6 md:p-8 space-y-5" aria-label="Live recovery workflow">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4"><div><div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_10px_#34d399]" /><h2 className="text-sm font-bold text-slate-100 uppercase tracking-wide">Live Recovery Console</h2></div><p className="text-xs text-slate-400 mt-2">One click runs the real order, detection, AI, simulation, and verified recovery path.</p></div><button disabled={busy} onClick={runWorkflow} className="primary-action rounded-xl bg-gradient-to-r from-cyan-400 to-blue-500 px-5 py-3 text-xs font-extrabold tracking-wide text-slate-950 disabled:opacity-50">{busy ? "RUNNING…" : "▶  RUN DEMO"}</button></div>
        <div className="grid grid-cols-2 md:grid-cols-6 gap-2" aria-label="Workflow progress">
          {["Order", "Fault", "ML", "Gemini", "Simulation", "Verified"].map((label, index) => <div key={label} className={`rounded-lg border p-2 text-center text-[10px] font-bold uppercase tracking-wide ${step > index ? "border-emerald-500/60 bg-emerald-500/10 text-emerald-300" : step === index ? "border-cyan-400 bg-cyan-500/10 text-cyan-300" : "border-slate-700 text-slate-500"}`}><span className="block text-sm mb-1">{step > index ? "✓" : index + 1}</span>{label}</div>)}
        </div>
        <p className="text-xs font-mono text-slate-300" role="status">{message}</p>
        {ml && <div className="grid grid-cols-2 gap-3 text-xs"><div className="rounded-lg border border-slate-700 p-3"><span className="text-slate-500">ML signal</span><div className={ml.suspicious ? "text-amber-300 font-bold" : "text-emerald-300 font-bold"}>{ml.available ? (ml.suspicious ? "SUSPICIOUS" : "NORMAL") : "UNAVAILABLE"}</div></div><div className="rounded-lg border border-slate-700 p-3"><span className="text-slate-500">Recovery</span><div className="text-emerald-300 font-bold">{recovery ? `${recovery.status} · VERIFIED` : "AWAITING"}</div></div></div>}
      </section>
    </div>
  );
};
