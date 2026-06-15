"""Data validation engine for CoolShift inputs."""

from datetime import datetime
from typing import Any, Dict, List, Tuple
from sqlalchemy.orm import Session
from app.models import ScenarioProfile, Appliance, EnergyAsset, IntervalInput, BaselineSchedule

def validate_scenario_data(scenario_id: str, db: Session) -> Dict[str, Any]:
    """Runs database validations for a scenario and returns a validation report.
    
    Includes errors (blockers) and warnings (non-blockers).
    """
    errors: List[str] = []
    warnings: List[str] = []
    
    # 1. Fetch Scenario Profile
    profile = db.query(ScenarioProfile).filter_by(scenario_id=scenario_id).first()
    if not profile:
        errors.append(f"Scenario profile '{scenario_id}' not found in database.")
        return {"scenario_id": scenario_id, "is_valid": False, "errors": errors, "warnings": warnings}
        
    # Profile field validation
    if profile.comfort_min_c >= profile.comfort_max_c:
        errors.append(f"Comfort range invalid: comfort_min_c ({profile.comfort_min_c}°C) must be less than comfort_max_c ({profile.comfort_max_c}°C).")
    if profile.area_m2 <= 0:
        errors.append(f"Building area must be positive: got {profile.area_m2} m2.")
    if profile.room_count <= 0:
        errors.append(f"Room count must be positive: got {profile.room_count}.")
    if profile.budget_pkr_per_day <= 0:
        warnings.append(f"Daily budget is zero or negative: got {profile.budget_pkr_per_day} PKR.")
    if profile.maximum_grid_demand_kw <= 0:
        errors.append(f"Maximum grid demand must be positive: got {profile.maximum_grid_demand_kw} kW.")
        
    # 2. Fetch & Validate Appliances
    appliances = db.query(Appliance).filter_by(scenario_id=scenario_id).all()
    if not appliances:
        errors.append(f"No cooling appliances defined for scenario '{scenario_id}'.")
    else:
        ac_count = 0
        fan_count = 0
        for app in appliances:
            if app.quantity <= 0:
                errors.append(f"Appliance '{app.appliance_id}' quantity must be positive: got {app.quantity}.")
            if app.rated_power_kw <= 0:
                errors.append(f"Appliance '{app.appliance_id}' rated power must be positive: got {app.rated_power_kw} kW.")
            
            if "ac" in app.appliance_type.lower():
                ac_count += app.quantity
                if app.cooling_capacity_kw <= 0:
                    errors.append(f"AC '{app.appliance_id}' must have positive cooling capacity: got {app.cooling_capacity_kw} kW.")
                if app.min_setpoint_c is not None and app.max_setpoint_c is not None:
                    if app.min_setpoint_c >= app.max_setpoint_c:
                        errors.append(f"AC setpoint limits invalid: min ({app.min_setpoint_c}°C) >= max ({app.max_setpoint_c}°C).")
            elif "fan" in app.appliance_type.lower():
                fan_count += app.quantity
                
        if ac_count == 0 and fan_count == 0:
            warnings.append("No active ACs or fans defined for this scenario.")
            
    # 3. Fetch & Validate Energy Assets
    asset = db.query(EnergyAsset).filter_by(scenario_id=scenario_id).first()
    if asset:
        if asset.solar_capacity_kw < 0:
            errors.append(f"Solar capacity cannot be negative: got {asset.solar_capacity_kw} kW.")
        if asset.battery_capacity_kwh < 0:
            errors.append(f"Battery capacity cannot be negative: got {asset.battery_capacity_kwh} kWh.")
            
        if asset.battery_capacity_kwh > 0:
            if asset.minimum_reserve_kwh < 0 or asset.minimum_reserve_kwh > asset.battery_capacity_kwh:
                errors.append(f"Battery reserve ({asset.minimum_reserve_kwh} kWh) must be between 0 and battery capacity ({asset.battery_capacity_kwh} kWh).")
            if asset.initial_soc_kwh < 0 or asset.initial_soc_kwh > asset.battery_capacity_kwh:
                errors.append(f"Battery initial SOC ({asset.initial_soc_kwh} kWh) must be between 0 and battery capacity ({asset.battery_capacity_kwh} kWh).")
            if asset.max_charge_kw <= 0 or asset.max_discharge_kw <= 0:
                errors.append("Battery charge/discharge rates must be positive.")
            if not (0.0 < asset.charge_efficiency <= 1.0) or not (0.0 < asset.discharge_efficiency <= 1.0):
                errors.append("Battery efficiencies must be between 0 and 1.")
                
    # 4. Fetch & Validate Interval Inputs
    intervals = db.query(IntervalInput).filter_by(scenario_id=scenario_id).order_by(IntervalInput.timestamp_local).all()
    if not intervals:
        errors.append(f"No time-series interval inputs found for scenario '{scenario_id}'.")
    else:
        # Check range and timestamp completeness
        num_intervals = len(intervals)
        
        # Check timestamp intervals
        timestamps = []
        for i, val in enumerate(intervals):
            timestamps.append(val.timestamp_local)
            
            # Range validations
            if not (0 <= val.temperature_c <= 60.0):
                errors.append(f"Temperature outside bounds at {val.timestamp_local}: got {val.temperature_c}°C.")
            if not (0 <= val.relative_humidity_pct <= 100.0):
                errors.append(f"Relative humidity outside bounds at {val.timestamp_local}: got {val.relative_humidity_pct}%.")
            if val.solar_irradiance_w_m2 < 0:
                errors.append(f"Solar irradiance is negative at {val.timestamp_local}: got {val.solar_irradiance_w_m2} W/m2.")
            if val.occupancy_count < 0:
                errors.append(f"Occupancy is negative at {val.timestamp_local}: got {val.occupancy_count}.")
            if val.tariff_pkr_per_kwh < 0:
                errors.append(f"Tariff is negative at {val.timestamp_local}: got {val.tariff_pkr_per_kwh} PKR/kWh.")
            if val.non_cooling_load_kw < 0:
                errors.append(f"Non-cooling load is negative at {val.timestamp_local}: got {val.non_cooling_load_kw} kW.")
                
        # Time continuity check
        parsed_times = []
        for ts in timestamps:
            try:
                # Handle potential formats
                if "T" in ts:
                    parsed_times.append(datetime.fromisoformat(ts))
                else:
                    parsed_times.append(datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"))
            except ValueError:
                errors.append(f"Invalid timestamp format: '{ts}'. Must be ISO 8601.")
                
        if len(parsed_times) == num_intervals and num_intervals > 1:
            gaps = 0
            for i in range(1, num_intervals):
                diff = (parsed_times[i] - parsed_times[i-1]).total_seconds() / 60.0
                if diff != 15.0:
                    gaps += 1
                    if gaps <= 5:  # Limit warnings
                        errors.append(f"Timestamp gap detected: interval from {timestamps[i-1]} to {timestamps[i]} is {diff} mins (expected 15 mins).")
            if gaps > 5:
                errors.append(f"Total of {gaps} timestamp gaps detected. Optimization requires fully continuous data.")
                
        # Total volumes
        # Challenge requires 2880 rows (30 days) or 672 rows (7 days)
        if num_intervals not in (96, 672, 2880):
            warnings.append(f"Interval count is {num_intervals}, which is not standard. Expected 96 (24-hour), 672 (7-day), or 2880 (30-day).")
            
    # 5. Baseline Schedule Validation
    baseline_rows = db.query(BaselineSchedule).filter_by(scenario_id=scenario_id).count()
    if baseline_rows == 0:
        warnings.append("No baseline schedule found. Baseline performance will be assumed as zero-cooling or calculated using fallback rules.")
    elif baseline_rows != len(intervals):
        errors.append(f"Baseline schedule rows ({baseline_rows}) does not match interval input rows ({len(intervals)}).")
        
    is_valid = len(errors) == 0
    return {
        "scenario_id": scenario_id,
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "interval_count": len(intervals) if intervals else 0,
        "appliance_count": len(appliances) if appliances else 0,
        "has_assets": asset is not None,
    }
