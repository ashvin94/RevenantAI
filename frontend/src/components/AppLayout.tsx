import React from "react";
import { Navigation, type ScreenId } from "./Navigation";
import { ShieldCheck, Radio, Terminal } from "lucide-react";

interface AppLayoutProps {
  currentScreen: ScreenId;
  onSelectScreen: (screen: ScreenId) => void;
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  currentScreen,
  onSelectScreen,
  children,
}) => {
  return (
    <div className="min-h-screen cyber-grid text-slate-900 flex flex-col relative selection:bg-slate-200 selection:text-slate-900">
      {/* Ambient Top Glow */}
      <div className="glow-ambient" />

      {/* Primary Header */}
      <header className="border-b border-slate-200/80 sticky top-0 z-50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-wrap items-center justify-between gap-4">
          
          {/* Logo & Brand Identity */}
          <div className="flex items-center space-x-3.5">
            <div className="relative">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500/20 via-blue-500/20 to-indigo-500/30 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shadow-[0_0_20px_-3px_rgba(6,182,212,0.3)]">
                <ShieldCheck className="w-5 h-5 text-cyan-300" aria-hidden="true" />
              </div>
              <span className="absolute -bottom-0.5 -right-0.5 flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
            </div>

            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
                  MirrorHeal AI
                </h1>
                <span className="text-[10px] font-mono tracking-widest uppercase px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-300 border border-cyan-500/30 font-semibold shadow-[0_0_10px_rgba(6,182,212,0.2)]">
                  AUTONOMOUS TWIN
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">
                Self-Healing Digital Twin & Verified Transaction Recovery
              </p>
            </div>
          </div>

          {/* Navigation Controls */}
          <Navigation currentScreen={currentScreen} onSelectScreen={onSelectScreen} />

          {/* System Mode Pill */}
          <div className="hidden lg:flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-slate-900/60 border border-slate-800 text-[11px] text-slate-300">
            <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" aria-hidden="true" />
            <span className="font-mono text-slate-400">Node:</span>
            <span className="font-mono text-emerald-300 font-medium">LOCAL-ALPHA</span>
            <span className="h-3 w-px bg-slate-800" />
            <span className="font-mono text-slate-400">Invariants:</span>
            <span className="font-mono text-cyan-300 font-medium">ACTIVE</span>
          </div>

        </div>
      </header>

      {/* Main Workspace Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6 relative z-10">
        {children}
      </main>

      {/* Cybernetic Footer */}
      <footer className="border-t border-slate-200/60 py-4 text-xs text-slate-500 relative z-10 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-[11px]">
            <Terminal className="w-3.5 h-3.5 text-slate-400" aria-hidden="true" />
            <span>MirrorHeal AI Engine • Phase 1B Verified Shell</span>
            <span className="text-slate-700">•</span>
            <span className="text-slate-400">Strictly Isolated In-Memory Twin</span>
          </div>
          <div className="text-[11px] font-mono text-slate-500 flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span>ZERO FABRICATED METRICS</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
