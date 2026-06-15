"""Pydantic v2 schemas for request / response validation."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ===================================================================
# Scenario Profile
# ===================================================================
class ScenarioProfileSchema(BaseModel):
    """Schema for a scenario profile."""

    scenario_id: str
    name: str
    timezone: str = "Asia/Karachi"
    building_type: str
    area_m2: float
    room_count: int
    max_occupancy: int
    insulation_level: str
    sun_exposure: str
    comfort_min_c: float
    comfort_max_c: float
    vulnerable_occupants: bool = False
    budget_pkr_per_day: float
    maximum_grid_demand_kw: float

    model_config = {"from_attributes": True}


# ===================================================================
# Appliance
# ===================================================================
class ApplianceSchema(BaseModel):
    """Schema for a cooling appliance."""

    scenario_id: str
    appliance_id: str
    zone_id: str
    appliance_type: str
    quantity: int
    rated_power_kw: float
    cooling_capacity_kw: float
    efficiency_label: str | None = None
    min_runtime_minutes: int = 0
    min_setpoint_c: float | None = None
    max_setpoint_c: float | None = None

    model_config = {"from_attributes": True}


# ===================================================================
# Energy Asset
# ===================================================================
class EnergyAssetSchema(BaseModel):
    """Schema for solar + battery configuration."""

    scenario_id: str
    solar_capacity_kw: float = 0.0
    solar_conversion_efficiency: float = 0.0
    battery_capacity_kwh: float = 0.0
    initial_soc_kwh: float = 0.0
    minimum_reserve_kwh: float = 0.0
    max_charge_kw: float = 0.0
    max_discharge_kw: float = 0.0
    charge_efficiency: float = 1.0
    discharge_efficiency: float = 1.0

    model_config = {"from_attributes": True}


# ===================================================================
# Interval Input
# ===================================================================
class IntervalInputSchema(BaseModel):
    """Schema for time-series interval data."""

    scenario_id: str
    timestamp_local: str
    interval_minutes: int = 15
    temperature_c: float
    relative_humidity_pct: float
    heat_index_c: float
    solar_irradiance_w_m2: float = 0.0
    solar_available_kw: float = 0.0
    occupancy_count: int = 0
    grid_available: bool = True
    tariff_type: str = "off_peak"
    tariff_pkr_per_kwh: float = 0.0
    grid_carbon_kgco2_per_kwh: float = 0.46
    non_cooling_load_kw: float = 0.0
    source_missing_flag: bool = False

    model_config = {"from_attributes": True}


# ===================================================================
# Baseline Schedule
# ===================================================================
class BaselineScheduleSchema(BaseModel):
    """Schema for baseline cooling schedule."""

    scenario_id: str
    timestamp_local: str
    baseline_ac_units_on: int = 0
    baseline_ac_setpoint_c: float | None = None
    baseline_fan_units_on: int = 0
    baseline_other_cooling_kw: float = 0.0
    baseline_rule: str | None = None

    model_config = {"from_attributes": True}


# ===================================================================
# Output Schedule
# ===================================================================
class OutputScheduleSchema(BaseModel):
    """Schema for per-interval optimisation result."""

    scenario_id: str
    run_id: str
    timestamp_local: str
    recommended_ac_units_on: int = 0
    recommended_ac_setpoint_c: float | None = None
    recommended_fan_units_on: int = 0
    grid_energy_kwh: float = 0.0
    solar_energy_used_kwh: float = 0.0
    battery_charge_kwh: float = 0.0
    battery_discharge_kwh: float = 0.0
    battery_soc_kwh: float = 0.0
    cooling_energy_kwh: float = 0.0
    estimated_indoor_temp_c: float = 0.0
    comfort_status: str = "comfortable"
    interval_cost_pkr: float = 0.0
    interval_emissions_kgco2e: float = 0.0
    reason_code: str = ""
    explanation: str = ""
    constraint_violation_count: int = 0
    constraint_violation_details: str | None = None

    model_config = {"from_attributes": True}


# ===================================================================
# Output Summary
# ===================================================================
class OutputSummarySchema(BaseModel):
    """Schema for run-level aggregated summary."""

    scenario_id: str
    run_id: str
    period_start: str
    period_end: str
    baseline_energy_kwh: float = 0.0
    optimized_energy_kwh: float = 0.0
    energy_saving_kwh: float = 0.0
    energy_saving_pct: float = 0.0
    baseline_cost_pkr: float = 0.0
    optimized_cost_pkr: float = 0.0
    cost_saving_pkr: float = 0.0
    cost_saving_pct: float = 0.0
    baseline_emissions_kgco2e: float = 0.0
    optimized_emissions_kgco2e: float = 0.0
    emissions_avoided_kgco2e: float = 0.0
    peak_grid_demand_kw: float = 0.0
    peak_period_grid_energy_kwh: float = 0.0
    solar_available_kwh: float = 0.0
    solar_used_kwh: float = 0.0
    solar_utilization_pct: float = 0.0
    comfort_compliance_pct: float = 0.0
    unsafe_occupied_intervals: int = 0
    constraint_violations: int = 0
    runtime_seconds: float = 0.0
    algorithm_version: str = "1.0.0"

    model_config = {"from_attributes": True}


# ===================================================================
# API request / response wrappers
# ===================================================================
class ImportResponse(BaseModel):
    """Response after data import."""

    scenario_id: str
    message: str
    rows_imported: dict[str, int] = Field(default_factory=dict)


class OptimizationRequest(BaseModel):
    """Request to trigger an optimization run."""

    scenario_id: str
    algorithm_version: str = "1.0.0"


class OptimizationResponse(BaseModel):
    """Response after optimization completes."""

    run_id: str
    scenario_id: str
    status: str
    runtime_seconds: float
    message: str


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str


class HealthResponse(BaseModel):
    """Health-check response."""

    status: str = "ok"
    version: str = "1.0.0"
