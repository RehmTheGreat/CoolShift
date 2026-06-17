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
    <aside className="hidden md:flex flex-col w-64 border-r border-sidebar-border bg-sidebar h-full shrink-0">
      {/* Brand logo */}
      <div className="h-16 flex items-center px-6 border-b border-sidebar-border justify-center">
        <Link href="/" className="flex items-center justify-center hover:opacity-85 transition-opacity">
          <img src="/coolshift_logo.png" alt="CoolShift Logo" className="h-10 w-auto object-contain" />
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
                  ? "bg-sidebar-accent text-primary border-l-2 border-primary pl-3.5 shadow-sm"
                  : "text-sidebar-foreground/75 hover:text-sidebar-foreground hover:bg-sidebar-accent/50"
              )}
            >
              <Icon
                className={cn(
                  "w-5 h-5 transition-transform duration-200 group-hover:scale-105",
                  isActive ? "text-primary" : "text-sidebar-foreground/60 group-hover:text-sidebar-foreground"
                )}
              />
              {link.label}
              
              {isActive && (
                <span className="absolute right-3 w-1.5 h-1.5 rounded-full bg-primary" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer info */}
      <div className="p-4 border-t border-sidebar-border">
        <div className="rounded-lg p-3 bg-sidebar-accent/30 border border-sidebar-border text-center">
          <p className="text-xs text-sidebar-foreground/50">Optimization Engine</p>
          <p className="text-sm font-semibold text-sidebar-foreground/80 mt-0.5">Active — v1.0.0</p>
        </div>
      </div>
    </aside>
  );
}
