import React from "react";
import type { HealthResponse } from "../types/contracts";
import { 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Database, 
  BrainCircuit, 
  Sparkles, 
  RefreshCw,
  Bug,
  Server,
  Activity,
  ShieldAlert
} from "lucide-react";

interface HealthPanelProps {
  health: HealthResponse | null;
  loading: boolean;
  error: string | null;
  onRefresh?: () => void;
}

export const HealthPanel: React.FC<HealthPanelProps> = ({
  health,
  loading,
  error,
  onRefresh,
}) => {
  return (
    <section 
      aria-label="System Health Status" 
      className="glass-panel rounded-2xl p-6 relative overflow-hidden"
    >
      {/* Subtle Corner Glow Accent */}
      <div className="absolute top-0 right-0 w-72 h-72 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Panel Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-4 mb-5">
        <div className="flex items-center space-x-3.5">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Server className="w-4 h-4" aria-hidden="true" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-slate-100 tracking-wide uppercase">
                Backend Gateway Health
              </h2>
              <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-800/60 px-1.5 py-0.2 rounded">
                REST API
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">
              Real-time connectivity and dependency health probe
            </p>
          </div>
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={loading}
            aria-label="Refresh health status"
            className="flex items-center gap-2 px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 transition-all duration-200 disabled:opacity-50 border border-slate-700/80 hover:border-cyan-500/40 shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50 cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${loading ? "animate-spin" : ""}`} aria-hidden="true" />
            <span>Refresh</span>
          </button>
        )}
      </div>

      {/* Loading Skeleton */}
      {loading && (
        <div 
          role="status" 
          aria-live="polite"
          className="py-12 flex flex-col items-center justify-center space-y-3.5 text-slate-400"
        >
          <div className="relative">
            <div className="w-10 h-10 rounded-full border-2 border-cyan-500/20 border-t-cyan-400 animate-spin" />
            <Activity className="w-4 h-4 text-cyan-400 absolute inset-0 m-auto animate-pulse" aria-hidden="true" />
          </div>
          <div className="text-center">
            <p className="text-sm font-semibold text-slate-300">Checking backend status...</p>
            <p className="text-xs text-slate-500">Querying /api/health telemetry</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div 
          role="alert" 
          className="p-4 rounded-xl bg-gradient-to-r from-red-950/40 via-red-900/20 to-slate-950/60 border border-red-500/40 flex items-start space-x-3.5 text-red-200 shadow-lg"
        >
          <div className="w-8 h-8 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center justify-center shrink-0">
            <ShieldAlert className="w-4 h-4 text-red-400" aria-hidden="true" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-red-300 tracking-wide">Connection Error</h3>
            <p className="text-xs text-red-300/80 mt-1 leading-relaxed">{error}</p>
          </div>
        </div>
      )}

      {/* Active Health Telemetry */}
      {!loading && !error && health && (
        <div className="space-y-4">
          
          {/* Top Banner Status */}
          <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/90 shadow-inner">
            <div className="flex items-center space-x-3">
              <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">
                Overall Status
              </span>
              <span
                className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                  health.status === "ok"
                    ? "bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 shadow-[0_0_12px_rgba(16,185,129,0.2)]"
                    : "bg-amber-950/80 text-amber-300 border border-amber-500/40 shadow-[0_0_12px_rgba(245,158,11,0.2)]"
                }`}
              >
                {health.status === "ok" ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" aria-hidden="true" />
                ) : (
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-400" aria-hidden="true" />
                )}
                {health.status}
              </span>
            </div>

            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span>Backend Version:</span>
              <span className="font-mono text-cyan-300 font-semibold bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                {health.version}
              </span>
            </div>
          </div>

          {/* Dependency Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
            
            {/* Database Card */}
            <div className="glass-panel-interactive p-4 rounded-xl flex flex-col justify-between">
              <div className="flex items-center justify-between text-slate-400 mb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Database</span>
                <div className="w-7 h-7 rounded-md bg-slate-800/80 border border-slate-700/60 flex items-center justify-center">
                  <Database className="w-3.5 h-3.5 text-slate-300" aria-hidden="true" />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {health.database === "available" ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" aria-hidden="true" />
                    <span className="text-sm font-semibold text-emerald-300">available</span>
                  </>
                ) : (
                  <>
                    <XCircle className="w-4 h-4 text-red-400 shrink-0" aria-hidden="true" />
                    <span className="text-sm font-semibold text-red-300">unavailable</span>
                  </>
                )}
              </div>
              <div className="text-[10px] text-slate-500 font-mono mt-2">SQLite Foreign Keys: ON</div>
            </div>

            {/* Machine Learning Engine */}
            <div className="glass-panel-interactive p-4 rounded-xl flex flex-col justify-between">
              <div className="flex items-center justify-between text-slate-400 mb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">ML Anomaly Model</span>
                <div className="w-7 h-7 rounded-md bg-slate-800/80 border border-slate-700/60 flex items-center justify-center">
                  <BrainCircuit className="w-3.5 h-3.5 text-purple-400" aria-hidden="true" />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {health.ml === "available" ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" aria-hidden="true" />
                    <span className="text-sm font-semibold text-emerald-300">available</span>
                  </>
                ) : (
                  <>
                    <XCircle className="w-4 h-4 text-amber-400 shrink-0" aria-hidden="true" />
                    <span className="text-sm font-semibold text-amber-300">unavailable</span>
                  </>
                )}
              </div>
              <div className="text-[10px] text-slate-500 font-mono mt-2">IsolationForest Pipeline</div>
            </div>

            {/* AI Provider */}
            <div className="glass-panel-interactive p-4 rounded-xl flex flex-col justify-between">
              <div className="flex items-center justify-between text-slate-400 mb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">AI Provider</span>
                <div className="w-7 h-7 rounded-md bg-slate-800/80 border border-slate-700/60 flex items-center justify-center">
                  <Sparkles className="w-3.5 h-3.5 text-cyan-400" aria-hidden="true" />
                </div>
              </div>
              <div className="space-y-1">
                <div className="text-sm font-semibold capitalize text-slate-100 flex items-center gap-1.5">
                  <span>{health.ai_provider}</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span
                    className={`inline-block w-2 h-2 rounded-full ${
                      health.ai_configured ? "bg-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.5)]" : "bg-amber-400"
                    }`}
                    aria-hidden="true"
                  />
                  <span className="text-xs text-slate-400 font-medium">
                    {health.ai_configured ? "Configured" : "Unconfigured"}
                  </span>
                </div>
              </div>
              <div className="text-[10px] text-slate-500 font-mono mt-2">Strict JSON Schema Output</div>
            </div>

            {/* Fault Injection */}
            <div className="glass-panel-interactive p-4 rounded-xl flex flex-col justify-between">
              <div className="flex items-center justify-between text-slate-400 mb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Fault Injection</span>
                <div className="w-7 h-7 rounded-md bg-slate-800/80 border border-slate-700/60 flex items-center justify-center">
                  <Bug className="w-3.5 h-3.5 text-amber-400" aria-hidden="true" />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span
                  className={`text-xs px-2.5 py-0.5 rounded font-mono font-bold tracking-wider ${
                    health.fault_injection_enabled
                      ? "bg-cyan-950/80 text-cyan-300 border border-cyan-700/60 shadow-[0_0_10px_rgba(6,182,212,0.2)]"
                      : "bg-slate-800 text-slate-400 border border-slate-700"
                  }`}
                >
                  {health.fault_injection_enabled ? "ENABLED" : "DISABLED"}
                </span>
              </div>
              <div className="text-[10px] text-slate-500 font-mono mt-2">Double-Reservation Probe</div>
            </div>

          </div>
        </div>
      )}
    </section>
  );
};
