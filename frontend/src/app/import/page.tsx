"use client";

import { useState } from "react";
import { uploadExcel, validateData } from "@/lib/api";
import { ValidationReport } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Upload, FileSpreadsheet, CheckCircle2, AlertOctagon, AlertTriangle, RefreshCw } from "lucide-react";

export default function ImportPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [report, setReport] = useState<ValidationReport | null>(null);
  const [importSummary, setImportSummary] = useState<{ scenario_id: string; message: string; rows_imported: Record<string, number> } | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setErrorMsg(null);
      setReport(null);
      setImportSummary(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setErrorMsg(null);
    try {
      // 1. Upload and parse Excel workbook
      const res = await uploadExcel(file);
      setImportSummary(res);
      
      // 2. If it is a multiple scenario file, we validate PUB-A by default or validate the target scenario
      const targetId = res.scenario_id === "MULTIPLE" ? "PUB-A" : res.scenario_id;
      if (targetId !== "NONE" && targetId !== "MULTIPLE") {
        const reportData = await validateData(targetId);
        setReport(reportData);
      } else if (res.scenario_id === "MULTIPLE") {
        // Run validations for all public scenarios
        const repA = await validateData("PUB-A");
        setReport(repA); // Show PUB-A report as default
      }
    } catch (e) {
      console.error(e);
      setErrorMsg(e instanceof Error ? e.message : "Data import failed. Please verify the spreadsheet format.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Upload card */}
        <Card className="glass-card flex flex-col justify-between">
          <CardHeader>
            <CardTitle className="text-lg font-bold text-foreground">Spreadsheet Upload Terminal</CardTitle>
            <CardDescription className="text-xs">
              Upload the organizer public workbook (.xlsx) to load scenarios, appliances, and time-series records.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6 pb-6">
            {/* Drag & Drop mockup container */}
            <div className="border border-dashed border-border rounded-xl p-8 text-center bg-muted/5 hover:bg-muted/10 transition-all relative">
              <input
                type="file"
                accept=".xlsx, .xls"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                disabled={uploading}
              />
              <Upload className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
              <p className="text-sm text-foreground font-medium">
                {file ? file.name : "Select or drag Excel workbook"}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {file ? `${(file.size / 1024).toFixed(0)} KB` : "Supports .xlsx, .xls templates"}
              </p>
            </div>

            {errorMsg && (
              <div className="p-3 rounded-lg border border-rose-500/20 bg-rose-500/10 text-xs text-rose-600 dark:text-rose-400 flex items-center gap-2">
                <AlertOctagon className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            {importSummary && (
              <div className="p-4 rounded-lg border border-emerald-500/20 bg-emerald-500/10 text-xs text-emerald-600 dark:text-emerald-400 space-y-2">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span className="font-semibold">Import Complete: {importSummary.scenario_id}</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-foreground font-mono mt-2">
                  {Object.entries(importSummary.rows_imported).map(([key, val]) => (
                    <div key={key} className="flex justify-between border-b border-border pb-1">
                      <span>{key.replace("_", " ")}:</span>
                      <span className="font-bold text-foreground">{val} rows</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <Button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="w-full gradient-bg text-primary-foreground font-bold flex items-center justify-center gap-2"
            >
              {uploading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" /> Importing Sheet Data...
                </>
              ) : (
                <>
                  <FileSpreadsheet className="w-4 h-4" /> Run Import & Parse
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Validation report card */}
        <Card className="glass-card flex flex-col">
          <CardHeader className="border-b border-border">
            <CardTitle className="text-lg font-bold text-foreground">Real-Time Validation Dashboard</CardTitle>
            <CardDescription className="text-xs">Ensures input schemas, ranges, and constraints conform to target requirements.</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto max-h-[360px] p-6 space-y-4">
            {!report ? (
              <div className="h-full flex items-center justify-center text-muted-foreground text-xs p-6 text-center">
                Upload a dataset to run structural validation checks.
              </div>
            ) : (
              <div className="space-y-4">
                {/* Validation status badge */}
                <div className="flex items-center justify-between border-b border-border pb-3">
                  <span className="text-xs text-muted-foreground font-medium">Schema Status</span>
                  <Badge className={report.is_valid ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20" : "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20"}>
                    {report.is_valid ? "VALID" : "INVALID"}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-4 text-xs">
                  <div className="p-3 rounded-lg bg-muted/5 border border-border">
                    <span className="text-muted-foreground block">Total Intervals</span>
                    <span className="font-bold text-foreground font-mono text-sm mt-0.5 block">{report.interval_count}</span>
                  </div>
                  <div className="p-3 rounded-lg bg-muted/5 border border-border">
                    <span className="text-muted-foreground block">Energy Assets</span>
                    <span className="font-bold text-foreground text-sm mt-0.5 block">{report.has_assets ? "CONFIGURED" : "NONE"}</span>
                  </div>
                </div>

                {/* Errors display */}
                {report.errors.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold text-rose-400 flex items-center gap-1">
                      <AlertOctagon className="w-3.5 h-3.5" /> Errors (Blockers: {report.errors.length})
                    </h4>
                    <div className="space-y-1.5 max-h-[120px] overflow-y-auto pr-1">
                      {report.errors.map((err, i) => (
                        <div key={i} className="p-2 text-[10px] rounded border border-rose-500/15 bg-rose-500/5 text-rose-300 font-mono leading-relaxed">
                          {err}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Warnings display */}
                {report.warnings.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold text-amber-400 flex items-center gap-1">
                      <AlertTriangle className="w-3.5 h-3.5" /> Warnings (Non-Blockers: {report.warnings.length})
                    </h4>
                    <div className="space-y-1.5 max-h-[120px] overflow-y-auto pr-1">
                      {report.warnings.map((warn, i) => (
                        <div key={i} className="p-2 text-[10px] rounded border border-amber-500/15 bg-amber-500/5 text-amber-300 font-mono leading-relaxed">
                          {warn}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {report.is_valid && (
                  <div className="p-3 rounded-lg border border-emerald-500/20 bg-emerald-500/5 text-[11px] text-emerald-400 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Inputs satisfy all target domain validation checks. Ready for optimization.</span>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
