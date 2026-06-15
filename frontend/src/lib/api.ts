// CoolShift API Client Library
import {
  ScenarioProfile,
  Appliance,
  EnergyAsset,
  OutputSchedule,
  OutputSummary,
  ComparisonData,
  ValidationReport,
  OptimizationRunMeta,
} from './types';

// In Next.js with rewrite: '/api/*' proxies to backend 'http://localhost:8000/api/*'
const API_BASE = '/api';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const errorBody = await res.text();
    let message = res.statusText;
    try {
      const parsed = JSON.parse(errorBody);
      if (parsed.detail) message = parsed.detail;
    } catch {
      if (errorBody) message = errorBody;
    }
    throw new ApiError(res.status, message);
  }

  // Handle No Content (204)
  if (res.status === 204) {
    return {} as T;
  }

  return res.json();
}

// ============= Scenarios API =============

export async function getScenarios(): Promise<ScenarioProfile[]> {
  return request<ScenarioProfile[]>('/scenarios');
}

export async function getScenario(id: string): Promise<ScenarioProfile> {
  return request<ScenarioProfile>(`/scenarios/${id}`);
}

export async function createScenario(data: ScenarioProfile): Promise<ScenarioProfile> {
  return request<ScenarioProfile>('/scenarios', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateScenario(id: string, data: ScenarioProfile): Promise<ScenarioProfile> {
  return request<ScenarioProfile>(`/scenarios/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteScenario(id: string): Promise<void> {
  return request<void>(`/scenarios/${id}`, {
    method: 'DELETE',
  });
}

export async function getAppliances(scenarioId: string): Promise<Appliance[]> {
  return request<Appliance[]>(`/scenarios/${scenarioId}/appliances`);
}

export async function getAssets(scenarioId: string): Promise<EnergyAsset> {
  return request<EnergyAsset>(`/scenarios/${scenarioId}/assets`);
}

// ============= Import API =============

export async function uploadExcel(file: File): Promise<{ scenario_id: string; message: string; rows_imported: Record<string, number> }> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/import/excel`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorBody = await res.text();
    let message = res.statusText;
    try {
      const parsed = JSON.parse(errorBody);
      if (parsed.detail) message = parsed.detail;
    } catch {
      if (errorBody) message = errorBody;
    }
    throw new ApiError(res.status, message);
  }

  return res.json();
}

export async function validateData(scenarioId: string): Promise<ValidationReport> {
  return request<ValidationReport>(`/import/validate/${scenarioId}`);
}

// ============= Optimization API =============

export async function runOptimization(scenarioId: string, algorithmVersion: string = '1.0.0'): Promise<{ run_id: string; scenario_id: string; status: string; runtime_seconds: number; message: string }> {
  return request<{ run_id: string; scenario_id: string; status: string; runtime_seconds: number; message: string }>('/optimization/run', {
    method: 'POST',
    body: JSON.stringify({ scenario_id: scenarioId, algorithm_version: algorithmVersion }),
  });
}

export async function getRuns(): Promise<OptimizationRunMeta[]> {
  return request<OptimizationRunMeta[]>('/optimization/runs');
}

export async function getOptimizationStatus(runId: string): Promise<{ run_id: string; scenario_id: string; status: string; runtime_seconds: number | null; created_at: string }> {
  return request<{ run_id: string; scenario_id: string; status: string; runtime_seconds: number | null; created_at: string }>(`/optimization/status/${runId}`);
}

// ============= Results API =============

export async function getResults(runId: string): Promise<OutputSchedule[]> {
  return request<OutputSchedule[]>(`/results/${runId}`);
}

export async function getResultsSummary(runId: string): Promise<OutputSummary> {
  return request<OutputSummary>(`/results/${runId}/summary`);
}

export async function getComparison(scenarioId: string, runId?: string): Promise<ComparisonData> {
  let url = `/results/compare/${scenarioId}`;
  if (runId) url += `?run_id=${runId}`;
  return request<ComparisonData>(url);
}

// ============= Export API =============

export async function downloadCsv(runId: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}/export/${runId}/csv`);
  if (!res.ok) throw new ApiError(res.status, res.statusText);
  return res.blob();
}

export async function downloadXlsx(runId: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}/export/${runId}/xlsx`);
  if (!res.ok) throw new ApiError(res.status, res.statusText);
  return res.blob();
}

export function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
