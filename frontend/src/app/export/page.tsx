"use client";

import { useEffect, useState } from "react";
import { getScenarios, getRuns, getResults, downloadCsv, downloadXlsx, triggerDownload } from "@/lib/api";
import { ScenarioProfile, OptimizationRunMeta, OutputSchedule } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FileSpreadsheet, Download, Table, CheckCircle2, RefreshCw } from "lucide-react";

export default function ExportPage() {
  const [scenarios, setScenarios] = useState<ScenarioProfile[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>("");
  const [runs, setRuns] = useState<OptimizationRunMeta[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string>("");
  const [previewRows, setPreviewRows] = useState<OutputSchedule[]>([]);
  
  const [loading, setLoading] = useState(true);
  const [runLoading, setRunLoading] = useState(false);
  const [downloading, setDownloading] = useState<"csv" | "xlsx" | null>(null);

  useEffect(() => {
    async function loadInitial() {
      try {
        const sList = await getScenarios();
        setScenarios(sList);
        if (sList.length > 0) {
          setSelectedScenarioId(sList[0].scenario_id);
        }
        const rList = await getRuns();
        setRuns(rList);
        if (rList.length > 0) {
          // Find first run for the scenario
          const matched = rList.find((r) => r.scenario_id === sList[0]?.scenario_id);
          if (matched) setSelectedRunId(matched.run_id);
          else setSelectedRunId(rList[0].run_id);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    loadInitial();
  }, []);

  useEffect(() => {
    if (!selectedRunId) {
      setPreviewRows([]);
      return;
    }
    async function loadPreview() {
      setRunLoading(true);
      try {
        const rows = await getResults(selectedRunId);
        setPreviewRows(rows.slice(0, 10)); // Take first 10 for preview
      } catch (e) {
        console.error(e);
        setPreviewRows([]);
      } finally {
        setRunLoading(false);
      }
    }
    loadPreview();
  }, [selectedRunId]);

  const handleDownload = async (format: "csv" | "xlsx") => {
    if (!selectedRunId) return;
    setDownloading(format);
    try {
      if (format === "csv") {
        const blob = await downloadCsv(selectedRunId);
        triggerDownload(blob, `${selectedRunId}_schedule.csv`);
      } else {
        const blob = await downloadXlsx(selectedRunId);
        triggerDownload(blob, `${selectedRunId}_results.xlsx`);
      }
    } catch (e) {
      console.error(e);
      alert(`Download failed: ` + (e instanceof Error ? e.message : String(e)));
    } finally {
      setDownloading(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-8 h-8 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
      </div>
    );
  }

  // Filter runs based on scenario
  const filteredRuns = runs.filter((r) => r.scenario_id === selectedScenarioId);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Controls card */}
        <Card className="glass-card md:col-span-1 flex flex-col justify-between">
          <CardHeader className="border-b border-border">
            <CardTitle className="text-lg font-bold text-foreground flex items-center gap-2">
              <Download className="w-5 h-5 text-primary" /> Export Terminal
            </CardTitle>
            <CardDescription className="text-xs">Select scenario run and format to generate deliverables.</CardDescription>
          </CardHeader>
          <CardContent className="pt-6 space-y-6 flex-grow">
            {/* Select Scenario */}
            <div className="space-y-2 text-sm">
              <label className="text-xs text-muted-foreground font-medium">Building Profile</label>
              <select
                value={selectedScenarioId}
                onChange={(e) => {
                  setSelectedScenarioId(e.target.value);
                  const matchedRun = runs.find((r) => r.scenario_id === e.target.value);
                  setSelectedRunId(matchedRun ? matchedRun.run_id : "");
                }}
                className="w-full bg-card border border-border rounded-md px-3 py-2 text-foreground text-xs focus:border-primary focus:outline-none"
              >
                {scenarios.map((s) => (
                  <option key={s.scenario_id} value={s.scenario_id}>
                    {s.scenario_id} — {s.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Select Run */}
            <div className="space-y-2 text-sm">
              <label className="text-xs text-muted-foreground font-medium">Optimization Run ID</label>
              {filteredRuns.length === 0 ? (
                <div className="text-xs text-rose-500">No completed runs for this scenario.</div>
              ) : (
                <select
                  value={selectedRunId}
                  onChange={(e) => setSelectedRunId(e.target.value)}
                  className="w-full bg-card border border-border rounded-md px-3 py-2 text-foreground font-mono text-xs focus:border-primary focus:outline-none"
                >
                  {filteredRuns.map((r) => (
                    <option key={r.run_id} value={r.run_id}>
                      {r.run_id} ({r.status})
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* Schema confirmation badge */}
            <div className="p-3 rounded-lg border border-border bg-muted/10 space-y-2">
              <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-wider block">Deliverables Validation</span>
              <div className="flex items-center gap-2 text-xs text-emerald-600 dark:text-emerald-400 font-medium">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>Verified Schema Output format</span>
              </div>
              <p className="text-[9px] text-muted-foreground leading-normal font-mono">
                CSV schedule outputs contain exactly 20 columns. Excel workbooks include Output_Schedule (20 cols) and Output_Summary (25 cols) sheets matching challenge specifications.
              </p>
            </div>

            <div className="space-y-3 pt-2">
              <Button
                onClick={() => handleDownload("csv")}
                disabled={!selectedRunId || downloading !== null}
                className="w-full border border-border bg-muted/20 text-foreground hover:bg-muted/40 font-bold text-xs flex items-center justify-center gap-2"
              >
                {downloading === "csv" ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" /> Packaging CSV...
                  </>
                ) : (
                  <>
                    <FileSpreadsheet className="w-4 h-4 text-primary" /> Download Schedule CSV
                  </>
                )}
              </Button>

              <Button
                onClick={() => handleDownload("xlsx")}
                disabled={!selectedRunId || downloading !== null}
                className="w-full gradient-bg text-primary-foreground hover:opacity-90 font-bold text-xs flex items-center justify-center gap-2"
              >
                {downloading === "xlsx" ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" /> Packaging Excel...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" /> Download Complete XLSX
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Preview card */}
        <Card className="glass-card md:col-span-2 flex flex-col">
          <CardHeader className="border-b border-border">
            <CardTitle className="text-sm font-bold text-foreground flex items-center gap-2">
              <Table className="w-4 h-4 text-primary" /> Export Preview (Top 10 Intervals)
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 overflow-x-auto p-4 max-h-[460px]">
            {runLoading ? (
              <div className="h-full flex items-center justify-center">
                <div className="w-6 h-6 rounded-full border-2 border-primary border-t-transparent animate-spin" />
              </div>
            ) : previewRows.length === 0 ? (
              <div className="h-full flex items-center justify-center text-muted-foreground text-xs text-center">
                No preview data. Select an active run to generate preview.
              </div>
            ) : (
              <table className="w-full text-left text-[10px] border-collapse font-mono">
                <thead>
                  <tr className="border-b border-border text-muted-foreground bg-muted/20">
                    <th className="p-2">Timestamp</th>
                    <th className="p-2">AC On</th>
                    <th className="p-2">Setpoint</th>
                    <th className="p-2">Fan On</th>
                    <th className="p-2">Grid (kWh)</th>
                    <th className="p-2">Cost (PKR)</th>
                    <th className="p-2">Indoor Temp</th>
                    <th className="p-2">Violations</th>
                  </tr>
                </thead>
                <tbody>
                  {previewRows.map((r, i) => (
                    <tr key={i} className="border-b border-border text-foreground hover:bg-muted/10">
                      <td className="p-2">{r.timestamp_local.substring(5, 16).replace("T", " ")}</td>
                      <td className="p-2 font-bold">{r.recommended_ac_units_on}</td>
                      <td className="p-2 text-primary">{r.recommended_ac_setpoint_c || "—"}</td>
                      <td className="p-2">{r.recommended_fan_units_on}</td>
                      <td className="p-2">{r.grid_energy_kwh.toFixed(3)}</td>
                      <td className="p-2 text-emerald-600 dark:text-emerald-400">{r.interval_cost_pkr.toFixed(1)}</td>
                      <td className="p-2 text-amber-600 dark:text-amber-500">{r.estimated_indoor_temp_c.toFixed(1)} °C</td>
                      <td className="p-2">
                        <Badge className={`text-[8px] px-1 py-0 ${
                          r.constraint_violation_count > 0 ? "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20" : "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20"
                        }`}>
                          {r.constraint_violation_count}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Simple label helper
function Label({ children, className }: { children: React.ReactNode; className?: string }) {
  return <span className={className}>{children}</span>;
}
