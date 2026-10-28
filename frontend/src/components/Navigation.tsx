import React from "react";
import { Activity, Sparkles, FlaskConical } from "lucide-react";

export type ScreenId = "mission-control" | "investigation" | "simulation-lab";

interface NavigationProps {
  currentScreen: ScreenId;
  onSelectScreen: (screen: ScreenId) => void;
}

export const Navigation: React.FC<NavigationProps> = ({
  currentScreen,
  onSelectScreen,
}) => {
  const navItems = [
    {
      id: "mission-control" as const,
      label: "Mission Control",
      badge: "LIVE",
      icon: Activity,
    },
    {
      id: "investigation" as const,
      label: "AI Investigation",
      badge: "P4",
      icon: Sparkles,
    },
    {
      id: "simulation-lab" as const,
      label: "Simulation Lab",
      badge: "TWIN",
      icon: FlaskConical,
    },
  ];

  return (
    <nav 
      aria-label="Main application screens" 
      className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-md shadow-inner"
    >
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = currentScreen === item.id;
        return (
          <button
            key={item.id}
            onClick={() => onSelectScreen(item.id)}
            aria-current={isActive ? "page" : undefined}
            className={`group relative flex items-center gap-2.5 px-4 py-2 rounded-lg text-xs font-semibold tracking-wide transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 ${
              isActive
                ? "bg-gradient-to-r from-cyan-500/15 via-blue-500/10 to-indigo-500/10 text-cyan-300 border border-cyan-500/30 shadow-[0_0_20px_-3px_rgba(6,182,212,0.25)]"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent"
            }`}
          >
            <Icon 
              className={`w-3.5 h-3.5 transition-transform duration-200 ${
                isActive ? "text-cyan-400 scale-110" : "text-slate-500 group-hover:text-slate-300"
              }`} 
              aria-hidden="true" 
            />
            <span>{item.label}</span>
            <span
              className={`text-[9px] font-mono px-1.5 py-0.2 rounded border font-medium uppercase tracking-wider ${
                isActive
                  ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40"
                  : "bg-slate-800/80 text-slate-400 border-slate-700/60"
              }`}
            >
              {item.badge}
            </span>
          </button>
        );
      })}
    </nav>
  );
};
