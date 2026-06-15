"use client";

import { useEffect, useState } from "react";
import { getScenarios, getComparison } from "@/lib/api";
import { ScenarioProfile, ComparisonData } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from "recharts";
import { Building2, TrendingDown, Thermometer, ShieldAlert, Sparkles, Activity } from "lucide-react";

export default function ResultsPage() {
  const [scenarios, setScenarios] = useState<ScenarioProfile[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [compareData, setCompareData] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [compareLoading, setCompareLoading] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    async function loadScenarios() {
      try {
        const list = await getScenarios();
        setScenarios(list);
        if (list.length > 0) {
          setSelectedId(list[0].scenario_id);
        }
      } catch (e) {
        console.error("Failed to load scenarios:", e);
      } finally {
        setLoading(false);
      }
    }
    loadScenarios();
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    
    async function loadComparison() {
      setCompareLoading(true);
      try {
        const res = await getComparison(selectedId);
        setCompareData(res);
      } catch (e) {
        console.error("Failed to load comparison data:", e);
        setCompareData(null);
      } finally {
        setCompareLoading(false);
      }
    }
    loadComparison();
  }, [selectedId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-8 h-8 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
      </div>
    );
  }

  const hasTimeline = compareData && compareData.timeline && compareData.timeline.length > 0;
  const summary = compareData?.summary;

  return (
    <div className="space-y-6">
      {/* Selector */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h2 className="text-xl font-bold text-foreground">Scenario Comparison Panel</h2>
          <p className="text-xs text-muted-foreground">View savings and parameters baseline vs optimized schedules.</p>
        </div>
        <div className="flex items-center gap-3">
          <Label className="text-xs text-muted-foreground font-medium">Select Scenario</Label>
          <select
            value={selectedId}
            onChange={(e) => setSelectedId(e.target.value)}
            className="bg-card border border-border rounded-md px-3 py-1.5 text-xs text-foreground focus:border-primary focus:outline-none"
            disabled={compareLoading}
          >
            {scenarios.map((s) => (
              <option key={s.scenario_id} value={s.scenario_id}>
                {s.scenario_id} — {s.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {compareLoading ? (
        <div className="flex items-center justify-center h-80">
          <div className="w-6 h-6 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        </div>
      ) : !compareData || !hasTimeline || !summary ? (
        <div className="rounded-xl border border-dashed border-border p-12 text-center bg-card">
          <Building2 className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-base text-foreground font-semibold">No Optimization Records Found</p>
          <p className="text-xs text-muted-foreground mt-1">Please dispatch the optimizer for this scenario first to generate comparison results.</p>
        </div>
      ) : (
        <div className="space-y-8 animate-fade-in">
          {/* Key metrics grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="glass-card">
              <CardContent className="pt-6">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-xs text-muted-foreground font-medium">Electricity Cost Saved</p>
                    <h3 className="text-2xl font-bold tracking-tight text-foreground mt-1">
                      {summary.cost_saving_pkr.toLocaleString(undefined, { maximumFractionDigits: 0 })}{" "}
                      <span className="text-xs text-muted-foreground font-normal">PKR</span>
                    </h3>
                    <p className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium mt-1">
                      Reduced by {summary.cost_saving_pct.toFixed(1)}%
                    </p>
                  </div>
                  <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20 text-emerald-600 dark:text-emerald-400">
                    <TrendingDown className="w-5 h-5" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="glass-card">
              <CardContent className="pt-6">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-xs text-muted-foreground font-medium">Cooling Energy Saved</p>
                    <h3 className="text-2xl font-bold tracking-tight text-foreground mt-1">
                      {summary.energy_saving_kwh.toFixed(1)}{" "}
                      <span className="text-xs text-muted-foreground font-normal">kWh</span>
                    </h3>
                    <p className="text-[10px] text-primary font-medium mt-1">
                      Reduced by {summary.energy_saving_pct.toFixed(1)}%
                    </p>
                  </div>
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center border border-primary/20 text-primary">
                    <Thermometer className="w-5 h-5" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="glass-card">
              <CardContent className="pt-6">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-xs text-muted-foreground font-medium">Carbon Emissions Avoided</p>
                    <h3 className="text-2xl font-bold tracking-tight text-foreground mt-1">
                      {summary.emissions_avoided_kgco2e.toFixed(1)}{" "}
                      <span className="text-xs text-muted-foreground font-normal">kgCO₂e</span>
                    </h3>
                    <p className="text-[10px] text-muted-foreground mt-1">
                      Optimized: {summary.optimized_emissions_kgco2e.toFixed(1)} kgCO₂e
                    </p>
                  </div>
                  <div className="w-10 h-10 rounded-lg bg-violet-500/10 flex items-center justify-center border border-violet-500/20 text-violet-600 dark:text-violet-400">
                    <Activity className="w-5 h-5" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="glass-card">
              <CardContent className="pt-6">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-xs text-muted-foreground font-medium">Comfort Compliance Rate</p>
                    <h3 className="text-2xl font-bold tracking-tight text-foreground mt-1">
                      {summary.comfort_compliance_pct.toFixed(0)}%
                    </h3>
                    <p className="text-[10px] text-rose-600 dark:text-rose-400 font-medium mt-1">
                      {summary.unsafe_occupied_intervals} unsafe period(s)
                    </p>
                  </div>
                  <div className="w-10 h-10 rounded-lg bg-rose-500/10 flex items-center justify-center border border-rose-500/20 text-rose-600 dark:text-rose-400">
                    <ShieldAlert className="w-5 h-5" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts container */}
          {mounted && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Temperature Line Chart */}
              <Card className="glass-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-bold text-foreground">Indoor & Outdoor Temperature Dynamics</CardTitle>
                  <CardDescription className="text-[10px] text-muted-foreground">Comparing baseline and optimized temperatures against weather.</CardDescription>
                </CardHeader>
                <CardContent className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={compareData.timeline.slice(0, 96)} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="timestamp_local" tickFormatter={(t) => t.substring(11, 16)} />
                      <YAxis domain={["auto", "auto"]} />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="outdoor_temp" stroke="#d97706" strokeWidth={1.5} dot={false} name="Outdoor Weather" />
                      <Line type="monotone" dataKey="baseline_indoor_temp_c" stroke="#ef4444" strokeWidth={1.5} dot={false} name="Baseline Temp" />
                      <Line type="monotone" dataKey="optimized_indoor_temp_c" stroke="#2563eb" strokeWidth={2} dot={false} name="Optimized Temp" />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Energy Dispatch Area Chart */}
              <Card className="glass-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-bold text-foreground">Optimized Electrical Energy Balance</CardTitle>
                  <CardDescription className="text-[10px] text-muted-foreground">Stacked dispatch allocation of solar, battery, and grid imports.</CardDescription>
                </CardHeader>
                <CardContent className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={compareData.timeline.slice(0, 96)} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="timestamp_local" tickFormatter={(t) => t.substring(11, 16)} />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Area type="monotone" dataKey="solar_energy_used_kwh" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.4} name="Solar Used" />
                      <Area type="monotone" dataKey="battery_discharge_kwh" stackId="1" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.4} name="Battery Used" />
                      <Area type="monotone" dataKey="optimized_grid_energy_kwh" stackId="1" stroke="#2563eb" fill="#2563eb" fillOpacity={0.4} name="Grid Import" />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          )}

          {mounted && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Battery SOC Chart (only if BESS is configured) */}
              {summary.solar_available_kwh > 0 && (
                <Card className="glass-card">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-bold text-foreground">Battery State of Charge Profile</CardTitle>
                    <CardDescription className="text-[10px] text-muted-foreground">Charging and discharging BESS patterns.</CardDescription>
                  </CardHeader>
                  <CardContent className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={compareData.timeline.slice(0, 96)} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="timestamp_local" tickFormatter={(t) => t.substring(11, 16)} />
                        <YAxis domain={[0, "auto"]} />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="battery_soc_kwh" stroke="#10b981" strokeWidth={2} dot={false} name="Battery SOC (kWh)" />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              )}

              {/* Cost Shift comparison Bar Chart */}
              <Card className="glass-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-bold text-foreground">Baseline vs Optimized Costs (Hourly)</CardTitle>
                  <CardDescription className="text-[10px] text-muted-foreground">Aggregated hourly costs comparison.</CardDescription>
                </CardHeader>
                <CardContent className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={compareData.timeline.slice(0, 96)} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="timestamp_local" tickFormatter={(t) => t.substring(11, 16)} />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="baseline_cost_pkr" fill="#ef4444" name="Baseline Cost (PKR)" />
                      <Bar dataKey="optimized_cost_pkr" fill="#2563eb" name="Optimized Cost (PKR)" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Simple label helper
function Label({ children, className }: { children: React.ReactNode; className?: string }) {
  return <span className={className}>{children}</span>;
}
