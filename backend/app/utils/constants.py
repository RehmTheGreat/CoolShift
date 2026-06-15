"""Domain constants for the CoolShift optimisation engine."""

from __future__ import annotations

# ===================================================================
# Algorithm metadata
# ===================================================================
ALGORITHM_VERSION: str = "1.0.0"

# ===================================================================
# Reason codes
# ===================================================================
HEAT_RISK: str = "HEAT_RISK"
COMFORT_REQUIRED: str = "COMFORT_REQUIRED"
SOLAR_AVAILABLE: str = "SOLAR_AVAILABLE"
BATTERY_CHARGE: str = "BATTERY_CHARGE"
BATTERY_DISCHARGE: str = "BATTERY_DISCHARGE"
PEAK_TARIFF: str = "PEAK_TARIFF"
GRID_OUTAGE: str = "GRID_OUTAGE"
PRE_COOL: str = "PRE_COOL"
VENTILATION_WINDOW: str = "VENTILATION_WINDOW"
UNOCCUPIED: str = "UNOCCUPIED"
BUDGET_LIMIT: str = "BUDGET_LIMIT"
DEMAND_LIMIT: str = "DEMAND_LIMIT"
INSUFFICIENT_CAPACITY: str = "INSUFFICIENT_CAPACITY"
MISSING_DATA: str = "MISSING_DATA"

REASON_CODES: set[str] = {
    HEAT_RISK, COMFORT_REQUIRED, SOLAR_AVAILABLE, BATTERY_CHARGE,
    BATTERY_DISCHARGE, PEAK_TARIFF, GRID_OUTAGE, PRE_COOL,
    VENTILATION_WINDOW, UNOCCUPIED, BUDGET_LIMIT, DEMAND_LIMIT,
    INSUFFICIENT_CAPACITY, MISSING_DATA,
}

# ===================================================================
# Comfort status values
# ===================================================================
COMFORTABLE: str = "comfortable"
TOO_HOT: str = "too_hot"
TOO_COLD: str = "too_cold"
UNSAFE: str = "unsafe"

# ===================================================================
# Tariff types
# ===================================================================
PEAK: str = "peak"
OFF_PEAK: str = "off_peak"

# ===================================================================
# Thermal model defaults
# ===================================================================
# Insulation R-values (K·m² / W) – higher is more insulating
INSULATION_R_VALUES: dict[str, float] = {
    "high": 3.5,
    "medium": 2.0,
    "low": 1.0,
    "none": 0.5,
}

# Sun exposure solar gain multipliers (W/m²)
SUN_EXPOSURE_GAIN: dict[str, float] = {
    "high": 0.12,
    "medium": 0.07,
    "low": 0.03,
    "none": 0.0,
}

# Internal heat gain per occupant (kW)
OCCUPANT_HEAT_GAIN_KW: float = 0.10

# Thermal mass time constant multiplier (seconds per m²)
THERMAL_MASS_FACTOR: float = 120.0

# Default indoor temperature when no history (°C)
DEFAULT_INDOOR_TEMP_C: float = 28.0

# Fan cooling effect (°C reduction in perceived temperature)
FAN_COOLING_EFFECT_C: float = 2.0

# ===================================================================
# Battery
# ===================================================================
MIN_SOC_FRACTION: float = 0.0  # Absolute minimum is 0
EMERGENCY_SOC_OVERRIDE: bool = True  # Allow dipping below reserve in emergencies

# ===================================================================
# Optimiser weights (for greedy cost function)
# ===================================================================
WEIGHT_COST: float = 0.40
WEIGHT_COMFORT: float = 0.35
WEIGHT_EMISSIONS: float = 0.15
WEIGHT_SOLAR: float = 0.10

# ===================================================================
# Setpoint step size for optimiser search
# ===================================================================
SETPOINT_STEP_C: float = 0.5

# ===================================================================
# Pre-cooling window (number of intervals to look ahead)
# ===================================================================
PRE_COOL_INTERVALS: int = 4

# ===================================================================
# Validation case expected values (for unit testing)
# ===================================================================
VAL_01_EXPECTED: float = 1.35      # 1.35 kW × 1 unit × 1.0h
VAL_02_EXPECTED: float = 0.0375    # 0.075 kW × 2 units × 0.25h
VAL_03_EXPECTED: float = 110.0     # 2.5 kWh × 44 PKR/kWh
VAL_04_EXPECTED: float = 1.472     # 3.2 kWh × 0.46 kgCO2e/kWh
VAL_05_EXPECTED: float = 1.88      # 2.0 kWh × 0.94 efficiency
VAL_06_EXPECTED: float = 2.12766   # 2.0 kWh / 0.94 efficiency (approx)

# ===================================================================
# Export column ordering
# ===================================================================
OUTPUT_SCHEDULE_COLUMNS: list[str] = [
    "scenario_id", "run_id", "timestamp_local",
    "recommended_ac_units_on", "recommended_ac_setpoint_c",
    "recommended_fan_units_on",
    "grid_energy_kwh", "solar_energy_used_kwh",
    "battery_charge_kwh", "battery_discharge_kwh", "battery_soc_kwh",
    "cooling_energy_kwh", "estimated_indoor_temp_c", "comfort_status",
    "interval_cost_pkr", "interval_emissions_kgco2e",
    "reason_code", "explanation",
    "constraint_violation_count", "constraint_violation_details",
]

OUTPUT_SUMMARY_COLUMNS: list[str] = [
    "scenario_id", "run_id", "period_start", "period_end",
    "baseline_energy_kwh", "optimized_energy_kwh",
    "energy_saving_kwh", "energy_saving_pct",
    "baseline_cost_pkr", "optimized_cost_pkr",
    "cost_saving_pkr", "cost_saving_pct",
    "baseline_emissions_kgco2e", "optimized_emissions_kgco2e",
    "emissions_avoided_kgco2e",
    "peak_grid_demand_kw", "peak_period_grid_energy_kwh",
    "solar_available_kwh", "solar_used_kwh", "solar_utilization_pct",
    "comfort_compliance_pct", "unsafe_occupied_intervals",
    "constraint_violations", "runtime_seconds", "algorithm_version",
]
