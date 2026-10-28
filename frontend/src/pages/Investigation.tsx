import React from "react";
import { Sparkles, BrainCircuit, AlertCircle, ShieldCheck } from "lucide-react";

export const Investigation: React.FC = () => {
  return (
    <div className="space-y-6">
      <section 
        aria-label="AI Investigation Overview"
        className="glass-panel rounded-2xl p-6 space-y-6 relative overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center space-x-4 border-b border-slate-800/80 pb-5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500/15 via-indigo-500/10 to-cyan-500/20 border border-purple-500/30 flex items-center justify-center text-purple-400 shadow-[0_0_15px_-3px_rgba(168,85,247,0.25)]">
            <Sparkles className="w-5 h-5 text-purple-300" aria-hidden="true" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wide">
                AI Investigation Lab
              </h2>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-950/70 text-purple-300 border border-purple-800/50">
                LIVE GEMINI + RULES
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">
              Root-cause proposals and strictly typed Pydantic candidate repair plans
            </p>
          </div>
        </div>

        {/* Phase 4 Capability Notice */}
        <div className="p-4 rounded-xl bg-gradient-to-r from-amber-950/30 via-amber-900/10 to-slate-950/50 border border-amber-500/30 flex items-start space-x-3.5 text-amber-200">
          <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" aria-hidden="true" />
          <div className="space-y-1">
            <h3 className="text-xs font-bold uppercase tracking-wider text-amber-300">Phase 4 Capability</h3>
            <p className="text-xs text-amber-200/80 leading-relaxed">
              Gemini receives only the verified incident evidence and returns a strictly typed, allowlisted proposal. The model never executes the repair.
            </p>
          </div>
        </div>

        {/* Investigation Architecture Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          
          <div className="glass-panel-interactive p-5 rounded-xl space-y-3">
            <div className="flex items-center space-x-2.5 text-cyan-400">
              <div className="w-7 h-7 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
                <BrainCircuit className="w-4 h-4 text-cyan-300" aria-hidden="true" />
              </div>
              <span className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Trained ML Suspicion Gate
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              IsolationForest anomaly detector signals suspicion based on synthetic telemetry. 
              Per safety invariants, ML score acts as suspicion only, not proof of corruption.
            </p>
            <div className="pt-1 flex items-center gap-2 font-mono text-[10px] text-cyan-400/80">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
              <span>ISOLATION FOREST CONTAMINATION BOUNDED</span>
            </div>
          </div>

          <div className="glass-panel-interactive p-5 rounded-xl space-y-3">
            <div className="flex items-center space-x-2.5 text-purple-400">
              <div className="w-7 h-7 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center">
                <ShieldCheck className="w-4 h-4 text-purple-300" aria-hidden="true" />
              </div>
              <span className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Deterministic Verification
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Corrupted reservation anomalies must be verified by explicit business invariant checks 
              before any repair plan is considered for simulation.
            </p>
            <div className="pt-1 flex items-center gap-2 font-mono text-[10px] text-purple-400/80">
              <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
              <span>INVARIANT GATES: RESERVATION & STOCK CONSERVATION</span>
            </div>
          </div>

        </div>
      </section>
    </div>
  );
};
