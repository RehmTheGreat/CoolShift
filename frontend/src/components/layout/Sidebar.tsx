"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Building2,
  FileSpreadsheet,
  Cpu,
  BarChart3,
  Download,
  Activity,
} from "lucide-react";
import { cn } from "@/lib/utils";

const links = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/scenarios", label: "Scenario Manager", icon: Building2 },
  { href: "/import", label: "Data Import", icon: FileSpreadsheet },
  { href: "/optimize", label: "Optimization Engine", icon: Cpu },
  { href: "/results", label: "Results Comparison", icon: BarChart3 },
  { href: "/export", label: "Export Results", icon: Download },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex flex-col w-64 border-r border-white/[0.06] bg-[#070b16] h-full shrink-0">
      {/* Brand logo */}
      <div className="h-16 flex items-center px-6 border-b border-white/[0.06]">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Activity className="w-5 h-5 text-[#0a0e1a] stroke-[2.5]" />
          </div>
          <span className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400">
            CoolShift
          </span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-grow py-6 px-4 space-y-1">
        {links.map((link) => {
          const Icon = link.icon;
          const isActive =
            pathname === link.href ||
            (link.href !== "/" && pathname.startsWith(link.href));

          return (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 group relative",
                isActive
                  ? "bg-white/[0.04] text-cyan-400 border-l-2 border-cyan-400 pl-3.5 shadow-md shadow-cyan-500/5"
                  : "text-slate-400 hover:text-white hover:bg-white/[0.02]"
              )}
            >
              <Icon
                className={cn(
                  "w-5 h-5 transition-transform duration-200 group-hover:scale-105",
                  isActive ? "text-cyan-400" : "text-slate-400 group-hover:text-white"
                )}
              />
              {link.label}
              
              {isActive && (
                <span className="absolute right-3 w-1.5 h-1.5 rounded-full bg-cyan-400 pulse-dot" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer info */}
      <div className="p-4 border-t border-white/[0.06]">
        <div className="rounded-lg p-3 bg-white/[0.02] border border-white/[0.04] text-center">
          <p className="text-xs text-slate-500">Optimization Engine</p>
          <p className="text-sm font-semibold text-slate-300 mt-0.5">Active — v1.0.0</p>
        </div>
      </div>
    </aside>
  );
}
