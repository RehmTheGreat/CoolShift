"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Zap,
  TrendingDown,
  Globe,
  Play,
  FileSpreadsheet,
  AlertTriangle,
  Building,
  Info,
} from "lucide-react";
import { getScenarios, getRuns, getResultsSummary } from "@/lib/api";
import { ScenarioProfile, OptimizationRunMeta } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function Dashboard() {
  const [scenarios, setScenarios] = useState<ScenarioProfile[]>([]);
  const [runs, setRuns] = useState<OptimizationRunMeta[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    energySaved: 0,
    costSaved: 0,
    carbonReduced: 0,
  });

  useEffect(() => {
    async function loadData() {
      try {
        const list = await getScenarios();
        setScenarios(list);
        const runsList = await getRuns();
        setRuns(runsList);

        const completedRuns = runsList.filter((r) => r.status === "completed");
        if (completedRuns.length > 0) {
          const summaries = await Promise.all(
            completedRuns.map((r) => getResultsSummary(r.run_id).catch(() => null))
          );
          
          let totalEnergySaved = 0;
          let totalCostSaved = 0;
          let totalCarbonReduced = 0;
          
          summaries.forEach((s) => {
            if (s) {
              totalEnergySaved += s.energy_saving_kwh;
              totalCostSaved += s.cost_saving_pkr;
              totalCarbonReduced += s.emissions_avoided_kgco2e;
            }
          });
          
          setStats({
            energySaved: totalEnergySaved,
            costSaved: totalCostSaved,
            carbonReduced: totalCarbonReduced,
          });
        }
      } catch (e) {
        console.error("Failed to load dashboard data:", e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-8">
      {/* Hero Welcome banner */}
      <div className="relative rounded-2xl overflow-hidden glass-card p-8 md:p-10 border border-border shadow-sm">
        <div className="absolute top-0 right-0 w-80 h-80 bg-gradient-to-br from-primary/5 to-secondary/5 blur-3xl rounded-full" />
        
        <div className="relative z-10 max-w-3xl space-y-4">
          <Badge className="bg-primary/10 text-primary border-primary/20 px-3 py-1 text-xs">
            SDG 7 & SDG 13 Cooling Platform
          </Badge>
          <h2 className="text-3xl md:text-4xl font-extrabold tracking-tight text-foreground">
            Optimize Building Cooling for <span className="gradient-text">Affordability</span> and <span className="gradient-text">Sustainability</span>.
          </h2>
          <p className="text-muted-foreground text-sm md:text-base leading-relaxed">
            CoolShift is a decision support and optimization platform that estimates baseline cooling performance,
            models thermal dynamics, and schedules AC/fan cooling appliances to minimize grid costs, emissions, and peak demands.
          </p>
          <div className="flex flex-wrap gap-4 pt-2">
            <Link href="/optimize">
              <Button className="gradient-bg hover:opacity-90 text-primary-foreground font-semibold flex items-center gap-2">
                <Play className="w-4 h-4 fill-current" /> Dispatch Optimizer
              </Button>
            </Link>
            <Link href="/import">
              <Button variant="outline" className="border-border hover:bg-muted/50 flex items-center gap-2">
                <FileSpreadsheet className="w-4 h-4" /> Upload Dataset
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Aggregate metrics grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <Card className="glass-card-hover">
          <CardContent className="pt-6 flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/20">
              <Zap className="w-6 h-6 text-primary" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground font-medium">Cooling Energy Shifted</p>
              <h3 className="text-2xl font-bold tracking-tight text-foreground mt-0.5">
                {stats.energySaved.toLocaleString()} <span className="text-sm text-muted-foreground font-normal">kWh</span>
              </h3>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card-hover">
          <CardContent className="pt-6 flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
              <TrendingDown className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground font-medium">Financial Cost Saved</p>
              <h3 className="text-2xl font-bold tracking-tight text-foreground mt-0.5">
                {stats.costSaved.toLocaleString()} <span className="text-sm text-muted-foreground font-normal">PKR</span>
              </h3>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card-hover">
          <CardContent className="pt-6 flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-violet-500/10 flex items-center justify-center border border-violet-500/20">
              <Globe className="w-6 h-6 text-violet-600 dark:text-violet-400" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground font-medium">Carbon Emissions Reduced</p>
              <h3 className="text-2xl font-bold tracking-tight text-foreground mt-0.5">
                {stats.carbonReduced.toLocaleString()} <span className="text-sm text-muted-foreground font-normal">kgCO₂e</span>
              </h3>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Scenarios overview */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-foreground">Active Building Scenarios</h3>
          <Link href="/scenarios" className="text-xs text-primary hover:underline font-semibold">
            Manage Scenarios →
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-44 rounded-xl bg-muted/10 border border-border animate-pulse" />
            ))}
          </div>
        ) : scenarios.length === 0 ? (
          <div className="rounded-xl border border-dashed border-border p-8 text-center bg-card">
            <Building className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
            <p className="text-sm text-foreground font-medium">No scenarios loaded yet</p>
            <p className="text-xs text-muted-foreground mt-1">Please import the public dataset workbook to populate active scenarios.</p>
            <Link href="/import" className="mt-4 inline-block">
              <Button size="sm" variant="outline" className="border-border hover:bg-muted/50">
                Import Dataset Now
              </Button>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {scenarios.map((s) => (
              <Card key={s.scenario_id} className="glass-card-hover border border-border flex flex-col justify-between">
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-start">
                    <Badge variant="secondary" className="bg-muted text-foreground text-[10px] font-mono">
                      {s.scenario_id}
                    </Badge>
                    <span className="text-[10px] text-muted-foreground font-mono">{s.timezone}</span>
                  </div>
                  <CardTitle className="text-base font-bold text-foreground mt-2">{s.name}</CardTitle>
                  <CardDescription className="text-xs text-muted-foreground">{s.building_type} • {s.area_m2} m²</CardDescription>
                </CardHeader>
                <CardContent className="pt-0 pb-5 space-y-3">
                  <div className="grid grid-cols-2 gap-2 text-xs border-t border-border pt-3">
                    <div>
                      <p className="text-muted-foreground">Rooms / Max Occupancy</p>
                      <p className="font-semibold text-foreground">{s.room_count} R / {s.max_occupancy} Pax</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Comfort Band</p>
                      <p className="font-semibold text-foreground">{s.comfort_min_c} - {s.comfort_max_c} °C</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <p className="text-muted-foreground">Peak demand limit</p>
                      <p className="font-semibold text-foreground">{s.maximum_grid_demand_kw} kW</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Daily budget</p>
                      <p className="font-semibold text-foreground">{s.budget_pkr_per_day} PKR</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Recent optimization runs */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-foreground">Recent Run Execution Log</h3>
        
        {loading ? (
          <div className="h-48 rounded-xl bg-muted/10 border border-border animate-pulse" />
        ) : runs.length === 0 ? (
          <div className="rounded-xl border border-border p-6 text-center bg-card">
            <Info className="w-6 h-6 text-muted-foreground mx-auto mb-2" />
            <p className="text-xs text-muted-foreground">No optimization runs logged. Go to the dispatch engine to execute runs.</p>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-border bg-card">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-border bg-muted/20 text-muted-foreground font-medium">
                  <th className="p-4">Run ID</th>
                  <th className="p-4">Scenario</th>
                  <th className="p-4">Created Time</th>
                  <th className="p-4">Runtime (s)</th>
                  <th className="p-4">Algorithm</th>
                  <th className="p-4 text-right">Status</th>
                </tr>
              </thead>
              <tbody>
                {runs.slice(0, 5).map((r) => (
                  <tr key={r.run_id} className="border-b border-border hover:bg-muted/10 transition-all text-foreground">
                    <td className="p-4 font-mono font-semibold text-primary">{r.run_id}</td>
                    <td className="p-4"><Badge variant="outline" className="border-border text-muted-foreground">{r.scenario_id}</Badge></td>
                    <td className="p-4">{new Date(r.created_at).toLocaleString()}</td>
                    <td className="p-4 font-mono">{r.runtime_seconds ? r.runtime_seconds.toFixed(3) : "—"}</td>
                    <td className="p-4 font-mono text-muted-foreground">v{r.algorithm_version}</td>
                    <td className="p-4 text-right">
                      <Badge className={r.status === "completed" ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20" : "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20"}>
                        {r.status}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
