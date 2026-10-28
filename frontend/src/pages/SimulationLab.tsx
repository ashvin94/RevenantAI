import React from "react";
import { FlaskConical, GitBranch, CheckCheck, AlertCircle } from "lucide-react";

export const SimulationLab: React.FC = () => {
  return (
    <div className="space-y-6">
      <section 
        aria-label="Simulation Lab Overview"
        className="glass-panel rounded-2xl p-6 space-y-6 relative overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center space-x-4 border-b border-slate-800/80 pb-5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/15 via-blue-500/10 to-indigo-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-[0_0_15px_-3px_rgba(6,182,212,0.25)]">
            <FlaskConical className="w-5 h-5 text-cyan-300" aria-hidden="true" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wide">
                Digital Twin Simulation Lab
              </h2>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950/70 text-cyan-300 border border-cyan-800/50">
                LIVE DIGITAL TWIN
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">
              Isolated in-memory sandboxes, side-by-side plan evaluation, and human-in-the-loop recovery
            </p>
          </div>
        </div>

        {/* Phase 5 Notice */}
        <div className="p-4 rounded-xl bg-gradient-to-r from-blue-950/30 via-cyan-950/20 to-slate-950/50 border border-cyan-500/30 flex items-start space-x-3.5 text-cyan-200">
          <AlertCircle className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" aria-hidden="true" />
          <div className="space-y-1">
            <h3 className="text-xs font-bold uppercase tracking-wider text-cyan-300">Phase 5 Capability</h3>
            <p className="text-xs text-cyan-200/80 leading-relaxed">
              Candidates are tested against an isolated copy first. Only an explicit approval can commit the verified repair to SQLite.
            </p>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          
          <div className="glass-panel-interactive p-5 rounded-xl space-y-3">
            <div className="flex items-center space-x-2.5 text-cyan-400">
              <div className="w-7 h-7 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
                <GitBranch className="w-4 h-4 text-cyan-300" aria-hidden="true" />
              </div>
              <span className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Zero DB Writes in Simulation
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              All candidate repair simulations execute against isolated in-memory deep copies. 
              The live SQLite database remains unmodified during all exploratory simulations.
            </p>
            <div className="pt-1 flex items-center gap-2 font-mono text-[10px] text-cyan-400/80">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
              <span>PURE TRANSITION FUNCTIONS ONLY</span>
            </div>
          </div>

          <div className="glass-panel-interactive p-5 rounded-xl space-y-3">
            <div className="flex items-center space-x-2.5 text-emerald-400">
              <div className="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
                <CheckCheck className="w-4 h-4 text-emerald-300" aria-hidden="true" />
              </div>
              <span className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Two-Phase Human Approval
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Recovery execution requires explicit operator review, version comparison, and transactional 
              commit verification before any recovery is marked complete.
            </p>
            <div className="pt-1 flex items-center gap-2 font-mono text-[10px] text-emerald-400/80">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>STRICT AUDIT TRAIL & IDEMPOTENCY KEY</span>
            </div>
          </div>

        </div>
      </section>
    </div>
  );
};
