// TypeScript types matching backend schemas exactly

export interface ScenarioProfile {
  scenario_id: string;
  name: string;
  timezone: string;
  building_type: string;
  area_m2: number;
  room_count: number;
  max_occupancy: number;
  insulation_level: string;
  sun_exposure: string;
  comfort_min_c: number;
  comfort_max_c: number;
  vulnerable_occupants: boolean;
  budget_pkr_per_day: number;
  maximum_grid_demand_kw: number;
}

export interface Appliance {
  scenario_id: string;
  appliance_id: string;
  zone_id: string;
  appliance_type: string;
  quantity: number;
  rated_power_kw: number;
  cooling_capacity_kw: number;
  efficiency_label: string | null;
  min_runtime_minutes: number;
  min_setpoint_c: number | null;
  max_setpoint_c: number | null;
}

export interface EnergyAsset {
  scenario_id: string;
  solar_capacity_kw: number;
  solar_conversion_efficiency: number;
  battery_capacity_kwh: number;
  initial_soc_kwh: number;
  minimum_reserve_kwh: number;
  max_charge_kw: number;
  max_discharge_kw: number;
  charge_efficiency: number;
  discharge_efficiency: number;
}

export interface IntervalInput {
  scenario_id: string;
  timestamp_local: string;
  interval_minutes: number;
  temperature_c: number;
  relative_humidity_pct: number;
  heat_index_c: number;
  solar_irradiance_w_m2: number;
  solar_available_kw: number;
  occupancy_count: number;
  grid_available: boolean;
  tariff_type: string;
  tariff_pkr_per_kwh: number;
  grid_carbon_kgco2_per_kwh: number;
  non_cooling_load_kw: number;
  source_missing_flag: boolean;
}

export interface OutputSchedule {
  scenario_id: string;
  run_id: string;
  timestamp_local: string;
  recommended_ac_units_on: number;
  recommended_ac_setpoint_c: number | null;
  recommended_fan_units_on: number;
  grid_energy_kwh: number;
  solar_energy_used_kwh: number;
  battery_charge_kwh: number;
  battery_discharge_kwh: number;
  battery_soc_kwh: number;
  cooling_energy_kwh: number;
  estimated_indoor_temp_c: number;
  comfort_status: string;
  interval_cost_pkr: number;
  interval_emissions_kgco2e: number;
  reason_code: string;
  explanation: string;
  constraint_violation_count: number;
  constraint_violation_details: string | null;
}

export interface OutputSummary {
  scenario_id: string;
  run_id: string;
  period_start: string;
  period_end: string;
  baseline_energy_kwh: number;
  optimized_energy_kwh: number;
  energy_saving_kwh: number;
  energy_saving_pct: number;
  baseline_cost_pkr: number;
  optimized_cost_pkr: number;
  cost_saving_pkr: number;
  cost_saving_pct: number;
  baseline_emissions_kgco2e: number;
  optimized_emissions_kgco2e: number;
  emissions_avoided_kgco2e: number;
  peak_grid_demand_kw: number;
  peak_period_grid_energy_kwh: number;
  solar_available_kwh: number;
  solar_used_kwh: number;
  solar_utilization_pct: number;
  comfort_compliance_pct: number;
  unsafe_occupied_intervals: number;
  constraint_violations: number;
  runtime_seconds: number;
  algorithm_version: string;
}

export interface ComparisonTimelinePoint {
  timestamp_local: string;
  outdoor_temp: number;
  humidity_pct: number;
  heat_index_c: number;
  tariff_pkr_per_kwh: number;
  baseline_ac_units_on: number;
  recommended_ac_units_on: number;
  baseline_fan_units_on: number;
  recommended_fan_units_on: number;
  baseline_indoor_temp_c: number;
  optimized_indoor_temp_c: number;
  baseline_comfort_status: string;
  optimized_comfort_status: string;
  baseline_cooling_energy_kwh: number;
  optimized_cooling_energy_kwh: number;
  baseline_grid_energy_kwh: number;
  optimized_grid_energy_kwh: number;
  solar_energy_used_kwh: number;
  battery_charge_kwh: number;
  battery_discharge_kwh: number;
  battery_soc_kwh: number;
  baseline_cost_pkr: number;
  optimized_cost_pkr: number;
  baseline_emissions_kgco2e: number;
  optimized_emissions_kgco2e: number;
  reason_code: string;
  explanation: string;
}

export interface ComparisonData {
  scenario_id: string;
  run_id: string;
  summary: OutputSummary;
  timeline: ComparisonTimelinePoint[];
}

export interface ValidationReport {
  scenario_id: string;
  is_valid: boolean;
  errors: string[];
  warnings: string[];
  interval_count: number;
  appliance_count: number;
  has_assets: boolean;
}

export interface OptimizationRunMeta {
  id: number;
  run_id: string;
  scenario_id: string;
  algorithm_version: string;
  created_at: string;
  runtime_seconds: number | null;
  status: string;
}
