"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { CheckCircle, AlertTriangle, Moon, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";

const routeTitles: Record<string, string> = {
  "/": "System Dashboard",
  "/scenarios": "Scenario Profile Manager",
  "/import": "Data Import & Validation",
  "/optimize": "Optimization Dispatch Engine",
  "/results": "Comparative Analysis & Analytics",
  "/export": "Data Export Terminal",
};

export default function Header() {
  const pathname = usePathname();
  const [health, setHealth] = useState<"ok" | "error" | "checking">("checking");
  const [title, setTitle] = useState("System Dashboard");

  useEffect(() => {
    // Resolve page title
    const matched = Object.keys(routeTitles).find(
      (route) => pathname === route || (route !== "/" && pathname.startsWith(route))
    );
    setTitle(matched ? routeTitles[matched] : "System Dashboard");
  }, [pathname]);

  const checkHealth = async () => {
    setHealth("checking");
    try {
      const res = await fetch("/api/health");
      if (res.ok) {
        setHealth("ok");
      } else {
        setHealth("error");
      }
    } catch {
      setHealth("error");
    }
  };

  useEffect(() => {
    checkHealth();
    // Poll health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 border-b border-white/[0.06] bg-[#070b16]/50 backdrop-blur-md flex items-center justify-between px-6 shrink-0 z-10">
      {/* Title */}
      <h1 className="text-lg font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
        {title}
      </h1>

      {/* Health status & Quick actions */}
      <div className="flex items-center gap-4">
        {/* API connection status badge */}
        <button
          onClick={checkHealth}
          className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/[0.05] bg-white/[0.02] text-xs hover:bg-white/[0.05] transition-all group"
        >
          {health === "checking" && (
            <>
              <RefreshCw className="w-3.5 h-3.5 text-cyan-400 animate-spin" />
              <span className="text-slate-400">Syncing...</span>
            </>
          )}
          {health === "ok" && (
            <>
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400 font-medium group-hover:underline">Engine Connected</span>
            </>
          )}
          {health === "error" && (
            <>
              <AlertTriangle className="w-3.5 h-3.5 text-rose-400 animate-pulse" />
              <span className="text-rose-400 font-medium group-hover:underline">Engine Offline</span>
            </>
          )}
        </button>

        {/* Ambient Dark Mode Indicator */}
        <div className="w-8 h-8 rounded-full border border-white/[0.05] bg-white/[0.02] flex items-center justify-center">
          <Moon className="w-4 h-4 text-cyan-400" />
        </div>
      </div>
    </header>
  );
}
