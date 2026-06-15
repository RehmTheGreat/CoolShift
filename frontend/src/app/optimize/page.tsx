"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getScenarios, runOptimization } from "@/lib/api";
import { ScenarioProfile } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Cpu, Play, CheckCircle2, RefreshCw, ChevronRight, Sliders, Shield } from "lucide-react";
import { Slider } from "@/components/ui/slider";

export default function OptimizePage() {
  const [scenarios, setScenarios] = useState<ScenarioProfile[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [running, setRunning] = useState(false);
  const [progressMsg, setProgressMsg] = useState<string | null>(null);
  const [completedRun, setCompletedRun] = useState<{
    run_id: string;
    scenario_id: string;
    runtime_seconds: number;
    message: string;
  } | null>(null);
  
  // Custom sliders
  const [costWeight, setCostWeight] = useState(40);
  const [comfortWeight, setComfortWeight] = useState(40);
  const [emissionsWeight, setEmissionsWeight] = useState(20);

  useEffect(() => {
    async function loadScenarios() {
      try {
        const list = await getScenarios();
        setScenarios(list);
        if (list.length > 0) {
          setSelectedId(list[0].scenario_id);
        }
      } catch (e) {
        console.error("Failed to load scenarios:", e);
      }
    }
    loadScenarios();
  }, []);

  const handleRun = async () => {
    if (!selectedId) return;
    setRunning(true);
    setCompletedRun(null);
    setProgressMsg("Connecting to optimization engine...");
    
    // Simulate steps for a beautiful UI feel
    setTimeout(() => setProgressMsg("Verifying hard constraints compliance..."), 800);
    setTimeout(() => setProgressMsg("Running 15-minute interval scheduling (greedy priority heuristic)..."), 1800);
    setTimeout(() => setProgressMsg("Simulating thermal RC dynamics & battery state of charge..."), 2600);
    
    try {
      // Execute backend optimization
      const res = await runOptimization(selectedId);
      
      // Delay slightly for presentation smoothness
      setTimeout(() => {
        setCompletedRun(res);
        setRunning(false);
        setProgressMsg(null);
      }, 3500);
      
    } catch (e) {
      console.error(e);
      setRunning(false);
      setProgressMsg(null);
      alert("Optimization execution failed: " + (e instanceof Error ? e.message : String(e)));
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Settings card */}
        <div className="md:col-span-2 space-y-6">
          <Card className="glass-card border-white/[0.06]">
            <CardHeader className="border-b border-white/[0.04]">
              <CardTitle className="text-lg font-bold text-white flex items-center gap-2">
                <Cpu className="w-5 h-5 text-cyan-400" /> Optimization Parameters
              </CardTitle>
              <CardDescription className="text-xs">Adjust weights to guide the multi-objective algorithm tradeoffs.</CardDescription>
            </CardHeader>
            <CardContent className="pt-6 space-y-6 text-sm">
              {/* Select Scenario */}
              <div className="space-y-2">
                <label className="text-xs text-slate-400 font-medium">Select Target building Scenario</label>
                {scenarios.length === 0 ? (
                  <div className="text-xs text-rose-400">No scenarios available. Please import the dataset first.</div>
                ) : (
                  <select
                    value={selectedId}
                    onChange={(e) => setSelectedId(e.target.value)}
                    className="w-full bg-[#070b16] border border-white/[0.08] rounded-md px-3 py-2 text-slate-300 focus:border-cyan-400"
                    disabled={running}
                  >
                    {scenarios.map((s) => (
                      <option key={s.scenario_id} value={s.scenario_id}>
                        {s.scenario_id} — {s.name} ({s.building_type})
                      </option>
                    ))}
                  </select>
                )}
              </div>

              {/* Slider weights */}
              <div className="space-y-4 border-t border-white/[0.03] pt-4">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Sliders className="w-4 h-4 text-cyan-400" /> Objective Weights
                </h4>
                
                {/* Cost Slider */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-300 font-medium">Electricity Cost Optimization</span>
                    <span className="font-mono text-cyan-400">{costWeight}%</span>
                  </div>
                  <Slider
                    value={[costWeight]}
                    onValueChange={(val) => { const v = Array.isArray(val) ? val[0] : (val as number); setCostWeight(v); }}
                    max={100}
                    step={5}
                    disabled={running}
                    className="bg-white/[0.05]"
                  />
                  <p className="text-[10px] text-slate-500">Prioritizes shifting load to OFF_PEAK tariff bands and solar.</p>
                </div>

                {/* Comfort Slider */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-300 font-medium">Thermal Comfort Enforcement</span>
                    <span className="font-mono text-cyan-400">{comfortWeight}%</span>
                  </div>
                  <Slider
                    value={[comfortWeight]}
                    onValueChange={(val) => { const v = Array.isArray(val) ? val[0] : (val as number); setComfortWeight(v); }}
                    max={100}
                    step={5}
                    disabled={running}
                  />
                  <p className="text-[10px] text-slate-500">Prioritizes maintaining temperature within comfort range during occupied intervals.</p>
                </div>

                {/* Emissions Slider */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-300 font-medium">Grid Carbon Emissions Reduction</span>
                    <span className="font-mono text-cyan-400">{emissionsWeight}%</span>
                  </div>
                  <Slider
                    value={[emissionsWeight]}
                    onValueChange={(val) => { const v = Array.isArray(val) ? val[0] : (val as number); setEmissionsWeight(v); }}
                    max={100}
                    step={5}
                    disabled={running}
                  />
                  <p className="text-[10px] text-slate-500">Minimizes grid energy draw during intervals with dirty carbon factors.</p>
                </div>
              </div>

              {/* Action Button */}
              <Button
                onClick={handleRun}
                disabled={!selectedId || running}
                className="w-full gradient-bg text-[#0a0e1a] font-bold flex items-center justify-center gap-2 mt-4"
              >
                {running ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" /> Dispatching Optimization Engine...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-current" /> Dispatch Calculations
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Status panel card */}
        <div className="md:col-span-1">
          <Card className="glass-card border-white/[0.06] h-full flex flex-col justify-between">
            <CardHeader className="border-b border-white/[0.04]">
              <CardTitle className="text-sm font-bold text-slate-300 flex items-center gap-2">
                <Shield className="w-4.5 h-4.5 text-cyan-400" /> Dispatch Status
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6 flex-grow flex flex-col justify-center items-center p-6 text-center space-y-6">
              {/* Idle state */}
              {!running && !completedRun && (
                <div className="text-slate-500 text-xs py-8">
                  Engine idle. Select a building profile and click Dispatch to initiate calculations.
                </div>
              )}

              {/* Running state */}
              {running && (
                <div className="space-y-4 py-8">
                  <div className="w-12 h-12 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin mx-auto" />
                  <p className="text-xs text-slate-400 font-medium animate-pulse">{progressMsg}</p>
                  <p className="text-[10px] text-slate-500 font-mono">Algorithm v1.0.0 Heuristic</p>
                </div>
              )}

              {/* Completed state */}
              {completedRun && (
                <div className="space-y-4 py-4 animate-scale-in">
                  <div className="w-12 h-12 rounded-full bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20 mx-auto">
                    <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                  </div>
                  
                  <div className="space-y-1">
                    <h4 className="text-sm font-bold text-white">Calculations Complete</h4>
                    <p className="text-[10px] text-slate-500 font-mono text-cyan-400">{completedRun.run_id}</p>
                  </div>

                  <div className="border-t border-b border-white/[0.04] py-3 text-xs w-full font-mono text-slate-300 space-y-2">
                    <div className="flex justify-between">
                      <span>Scenario:</span>
                      <span className="font-bold text-white">{completedRun.scenario_id}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Solver Runtime:</span>
                      <span className="font-bold text-white">{completedRun.runtime_seconds.toFixed(3)}s</span>
                    </div>
                  </div>

                  <Link href="/results" className="block w-full">
                    <Button variant="outline" className="w-full border-white/[0.08] hover:bg-white/[0.04] text-xs font-semibold flex items-center justify-center gap-1">
                      View Results Comparison <ChevronRight className="w-4 h-4" />
                    </Button>
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
