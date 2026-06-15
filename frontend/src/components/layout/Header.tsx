"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { CheckCircle, AlertTriangle, Moon, Sun, RefreshCw } from "lucide-react";
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
  const [theme, setTheme] = useState<"light" | "dark">("dark");

  useEffect(() => {
    // Read theme from localStorage or document class
    const isDark = document.documentElement.classList.contains("dark");
    setTheme(isDark ? "dark" : "light");
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
    if (nextTheme === "dark") {
      document.documentElement.classList.add("dark");
      document.documentElement.style.colorScheme = "dark";
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      document.documentElement.style.colorScheme = "light";
      localStorage.setItem("theme", "light");
    }
  };

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
    <header className="h-16 border-b border-border bg-card/50 backdrop-blur-md flex items-center justify-between px-6 shrink-0 z-10">
      {/* Title */}
      <h1 className="text-lg font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground to-muted-foreground">
        {title}
      </h1>

      {/* Health status & Quick actions */}
      <div className="flex items-center gap-4">
        {/* API connection status badge */}
        <button
          onClick={checkHealth}
          className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-border bg-muted/30 text-xs hover:bg-muted/50 transition-all group"
        >
          {health === "checking" && (
            <>
              <RefreshCw className="w-3.5 h-3.5 text-blue-500 animate-spin" />
              <span className="text-muted-foreground">Syncing...</span>
            </>
          )}
          {health === "ok" && (
            <>
              <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
              <span className="text-emerald-500 font-medium group-hover:underline">Engine Connected</span>
            </>
          )}
          {health === "error" && (
            <>
              <AlertTriangle className="w-3.5 h-3.5 text-rose-500 animate-pulse" />
              <span className="text-rose-500 font-medium group-hover:underline">Engine Offline</span>
            </>
          )}
        </button>

        {/* Dark Mode Toggle Button */}
        <button
          onClick={toggleTheme}
          aria-label="Toggle theme"
          className="w-8 h-8 rounded-full border border-border bg-muted/30 flex items-center justify-center hover:bg-muted/50 transition-all cursor-pointer"
        >
          {theme === "dark" ? (
            <Moon className="w-4 h-4 text-blue-400" />
          ) : (
            <Sun className="w-4 h-4 text-amber-500" />
          )}
        </button>
      </div>
    </header>
  );
}
