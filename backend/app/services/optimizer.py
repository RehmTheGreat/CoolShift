"""CoolShift multi-objective optimization engine."""

import time
from typing import Any, Dict, List, Tuple
from sqlalchemy.orm import Session

from app.models import ScenarioProfile, Appliance, EnergyAsset, IntervalInput, BaselineSchedule, OptimizationRun, OutputSchedule, OutputSummary
from app.services.thermal import estimate_indoor_temperature, get_perceived_temperature, get_comfort_status
from app.services.battery import calculate_solar_available, dispatch_battery_charge, dispatch_battery_discharge
from app.utils.constants import (
    ALGORITHM_VERSION,
    GRID_OUTAGE,
    HEAT_RISK,
    COMFORT_REQUIRED,
    SOLAR_AVAILABLE,
    BATTERY_CHARGE,
    BATTERY_DISCHARGE,
    PEAK_TARIFF,
    PRE_COOL,
    VENTILATION_WINDOW,
    UNOCCUPIED,
    BUDGET_LIMIT,
    DEMAND_LIMIT,
    INSUFFICIENT_CAPACITY,
    COMFORTABLE,
    TOO_HOT,
    TOO_COLD,
    UNSAFE,
    PEAK,
    OFF_PEAK,
)

def run_optimization(scenario_id: str, db: Session, algorithm_version: str = ALGORITHM_VERSION) -> str:
    """Runs the optimization calculation for a scenario.
    
    Returns the run_id of the completed run.
    """
    start_time = time.time()
    
    profile = db.query(ScenarioProfile).filter_by(scenario_id=scenario_id).first()
    if not profile:
        raise ValueError(f"Scenario profile '{scenario_id}' not found.")
        
    appliances = db.query(Appliance).filter_by(scenario_id=scenario_id).all()
    ac_app = next((a for a in appliances if "ac" in a.appliance_type.lower()), None)
    fan_app = next((a for a in appliances if "fan" in a.appliance_type.lower()), None)
    
    ac_qty = ac_app.quantity if ac_app else 0
    ac_rated_power = ac_app.rated_power_kw if ac_app else 0.0
    ac_cooling_cap = ac_app.cooling_capacity_kw if ac_app else 0.0
    ac_min_sp = ac_app.min_setpoint_c if ac_app else 24.0
    ac_max_sp = ac_app.max_setpoint_c if ac_app else 30.0
    
    fan_qty = fan_app.quantity if fan_app else 0
    fan_rated_power = fan_app.rated_power_kw if fan_app else 0.0
    
    asset = db.query(EnergyAsset).filter_by(scenario_id=scenario_id).first()
    intervals = db.query(IntervalInput).filter_by(scenario_id=scenario_id).order_by(IntervalInput.timestamp_local).all()
    
    # Pre-calculate baseline metrics to generate summary savings later
    from app.services.baseline import calculate_baseline
    baseline_results = calculate_baseline(scenario_id, db)
    baseline_map = {b["timestamp_local"]: b for b in baseline_results}
    
    # 1. Create a pending optimization run record
    import uuid
    run_id = str(uuid.uuid4())
    opt_run = OptimizationRun(
        run_id=run_id,
        scenario_id=scenario_id,
        algorithm_version=algorithm_version,
        status="running",
    )
    db.add(opt_run)
    db.commit()
    
    # Heuristic optimization algorithm state
    current_soc = asset.initial_soc_kwh if asset else 0.0
    prev_indoor_temp = None
    peak_grid_demand = 0.0
    
    output_rows = []
    
    # Lookahead pre-cooling settings
    lookahead_intervals = 4  # 1 hour
    
    for idx, val in enumerate(intervals):
        dt = val.interval_minutes / 60.0
        
        # Determine if pre-cooling is needed
        # Check lookahead intervals for:
        # - Upcoming grid outage
        # - Upcoming PEAK tariff
        # - Upcoming occupancy starting
        precool_trigger = False
        for l in range(1, lookahead_intervals + 1):
            next_idx = idx + l
            if next_idx < len(intervals):
                next_val = intervals[next_idx]
                # Outage coming soon
                if val.grid_available and not next_val.grid_available:
                    precool_trigger = True
                    break
                # Tariff hike coming soon
                if val.tariff_type == OFF_PEAK and next_val.tariff_type == PEAK:
                    precool_trigger = True
                    break
                # Occupants coming soon
                if val.occupancy_count == 0 and next_val.occupancy_count > 0:
                    precool_trigger = True
                    break
                    
        # Define current comfort target bounds
        is_occupied = val.occupancy_count > 0
        c_min = profile.comfort_min_c
        c_max = profile.comfort_max_c
        
        # If pre-cooling, we pull target lower to store cooling
        if precool_trigger and val.grid_available:
            c_max = min(c_max, c_min + 1.0)
            
        # Search for best action (ac_on, setpoint, fan_on) for this interval
        best_action = None
        best_cost = float("inf")
        best_metrics = {}
        
        # Candidate actions:
        # Loop through possible AC counts
        ac_options = list(range(0, ac_qty + 1))
        # Loop through setpoints (coarse grid)
        sp_options = [None] if ac_qty == 0 else [None] + list(range(int(ac_min_sp), int(ac_max_sp) + 1))
        # Loop through fan counts
        fan_options = list(range(0, fan_qty + 1))
        
        for ac_on in ac_options:
            for sp in sp_options:
                # setpoint only valid if AC is on
                if ac_on == 0 and sp is not None:
                    continue
                if ac_on > 0 and sp is None:
                    continue
                    
                for fan_on in fan_options:
                    # Evaluate this candidate
                    temp_ind = estimate_indoor_temperature(
                        outdoor_temp=val.temperature_c,
                        humidity_pct=val.relative_humidity_pct,
                        solar_irradiance=val.solar_irradiance_w_m2,
                        occupancy=val.occupancy_count,
                        insulation_level=profile.insulation_level,
                        sun_exposure=profile.sun_exposure,
                        area_m2=profile.area_m2,
                        ac_units_on=ac_on,
                        ac_setpoint_c=sp,
                        fan_units_on=fan_on,
                        ac_cooling_capacity_kw=ac_cooling_cap,
                        ac_rated_power_kw=ac_rated_power,
                        prev_indoor_temp=prev_indoor_temp,
                        interval_minutes=val.interval_minutes,
                        heat_index_c=val.heat_index_c,
                        non_cooling_load_kw=val.non_cooling_load_kw,
                        grid_available=val.grid_available,
                        solar_available_kw=val.solar_available_kw,
                        battery_soc_kwh=current_soc,
                        fan_rated_power_kw=fan_rated_power,
                    )
                    
                    perceived = get_perceived_temperature(temp_ind, fan_on)
                    c_status = get_comfort_status(perceived, profile.comfort_min_c, profile.comfort_max_c)
                    
                    # Energy loads
                    ac_eng = ac_on * ac_rated_power * dt
                    fan_eng = fan_on * fan_rated_power * dt
                    cool_eng = ac_eng + fan_eng
                    tot_load_kw = (cool_eng + (val.non_cooling_load_kw * dt)) / dt
                    
                    # Solar availability
                    sol_av = val.solar_available_kw
                    if sol_av == 0.0 and asset and asset.solar_capacity_kw > 0:
                        sol_av = calculate_solar_available(
                            asset.solar_capacity_kw,
                            asset.solar_conversion_efficiency,
                            val.solar_irradiance_w_m2,
                        )
                    sol_av_kwh = sol_av * dt
                    
                    # Solar dispatch
                    sol_used = min(sol_av_kwh, tot_load_kw * dt)
                    rem_load = (tot_load_kw * dt) - sol_used
                    exc_sol = sol_av_kwh - sol_used
                    
                    # Battery SOC and dispatch
                    cand_soc = current_soc
                    b_charge = 0.0
                    b_discharge = 0.0
                    
                    if asset and asset.battery_capacity_kwh > 0:
                        # Charge from excess solar
                        if exc_sol > 0:
                            b_charge, soc_inc = dispatch_battery_charge(
                                cand_soc,
                                asset.battery_capacity_kwh,
                                asset.max_charge_kw,
                                asset.charge_efficiency,
                                exc_sol / dt,
                                val.interval_minutes,
                            )
                            cand_soc += soc_inc
                            
                        # Discharge if grid unavailable or during peak tariff
                        if rem_load > 0 and (not val.grid_available or val.tariff_type == PEAK):
                            b_discharge, soc_red = dispatch_battery_discharge(
                                cand_soc,
                                asset.minimum_reserve_kwh,
                                asset.max_discharge_kw,
                                asset.discharge_efficiency,
                                rem_load / dt,
                                emergency_mode=(not val.grid_available),
                                interval_minutes=val.interval_minutes,
                            )
                            cand_soc -= soc_red
                            rem_load -= b_discharge
                            
                    # Grid draw
                    g_energy = 0.0
                    unserved = 0.0
                    
                    if val.grid_available:
                        g_energy = rem_load
                    else:
                        unserved = rem_load  # outage & no power
                        
                    # Calculate cost & emissions
                    cost_val = g_energy * val.tariff_pkr_per_kwh
                    emissions_val = g_energy * val.grid_carbon_kgco2_per_kwh
                    
                    # Penalty functions for multi-objective cost minimizing
                    # 1. Unserved energy penalty (very high)
                    unserved_penalty = unserved * 2000.0
                    
                    # 2. Comfort penalty
                    comfort_penalty = 0.0
                    if is_occupied:
                        if c_status == UNSAFE:
                            comfort_penalty = 5000.0
                        elif c_status == TOO_HOT:
                            comfort_penalty = 300.0 * (perceived - profile.comfort_max_c)
                        elif c_status == TOO_COLD:
                            comfort_penalty = 150.0 * (profile.comfort_min_c - perceived)
                    else:
                        # Unoccupied comfort penalties are tiny
                        if perceived > profile.comfort_max_c + 5.0:
                            comfort_penalty = 50.0
                            
                    # 3. Peak grid demand penalty
                    demand_power = g_energy / dt
                    demand_penalty = 0.0
                    if demand_power > profile.maximum_grid_demand_kw:
                        # Severe violation penalty
                        demand_penalty = (demand_power - profile.maximum_grid_demand_kw) * 1000.0
                    elif demand_power > peak_grid_demand:
                        # Small penalty to avoid raising peak demand
                        demand_penalty = (demand_power - peak_grid_demand) * 10.0
                        
                    # 4. Energy cost
                    cost_penalty = cost_val
                    
                    # 5. Grid emissions
                    emissions_penalty = emissions_val * 100.0
                    
                    # 6. Pre-cooling bonus (negative penalty)
                    precool_bonus = 0.0
                    if precool_trigger and perceived <= profile.comfort_max_c - 0.5:
                        precool_bonus = -50.0
                        
                    total_cand_cost = (
                        unserved_penalty
                        + comfort_penalty
                        + demand_penalty
                        + cost_penalty
                        + emissions_penalty
                        + precool_bonus
                    )
                    
                    if total_cand_cost < best_cost:
                        best_cost = total_cand_cost
                        best_action = (ac_on, sp, fan_on)
                        best_metrics = {
                            "estimated_indoor_temp_c": temp_ind,
                            "comfort_status": c_status,
                            "cooling_energy_kwh": cool_eng,
                            "grid_energy_kwh": g_energy,
                            "solar_energy_used_kwh": sol_used,
                            "battery_charge_kwh": b_charge,
                            "battery_discharge_kwh": b_discharge,
                            "battery_soc_kwh": cand_soc,
                            "interval_cost_pkr": cost_val,
                            "interval_emissions_kgco2e": emissions_val,
                            "unserved_energy_kwh": unserved,
                        }
                        
        # Commit the best action and update state
        ac_on, sp, fan_on = best_action
        prev_indoor_temp = best_metrics["estimated_indoor_temp_c"]
        current_soc = best_metrics["battery_soc_kwh"]
        peak_grid_demand = max(peak_grid_demand, best_metrics["grid_energy_kwh"] / dt)
        
        # Decide the reason code
        reason = COMFORT_REQUIRED
        explanation = "Maintaining occupied comfort target."
        
        if not val.grid_available:
            reason = GRID_OUTAGE
            explanation = "Grid is down; running in backup mode."
        elif not is_occupied:
            reason = UNOCCUPIED
            explanation = "Space unoccupied; cooling minimized."
        elif precool_trigger:
            reason = PRE_COOL
            explanation = "Pre-cooling to store thermal capacity ahead of grid change."
        elif best_metrics["battery_discharge_kwh"] > 0:
            reason = BATTERY_DISCHARGE
            explanation = "Discharging battery to offset peak grid cost."
        elif best_metrics["battery_charge_kwh"] > 0:
            reason = BATTERY_CHARGE
            explanation = "Charging battery using available excess solar."
        elif best_metrics["solar_energy_used_kwh"] > 0:
            reason = SOLAR_AVAILABLE
            explanation = "Powering cooling via active solar generation."
        elif val.tariff_type == PEAK:
            reason = PEAK_TARIFF
            explanation = "Shifting cooling to minimize peak rate usage."
            
        # Check constraint violations
        violations = []
        if best_metrics["grid_energy_kwh"] / dt > profile.maximum_grid_demand_kw:
            violations.append(f"Grid demand ({best_metrics['grid_energy_kwh']/dt:.2f} kW) exceeded limit ({profile.maximum_grid_demand_kw} kW)")
        if not val.grid_available and best_metrics["grid_energy_kwh"] > 0:
            violations.append("Grid draw occurred during outage")
        if best_metrics["unserved_energy_kwh"] > 0:
            violations.append(f"Unserved load of {best_metrics['unserved_energy_kwh']:.2f} kWh due to outage and lack of battery power")
            
        row = OutputSchedule(
            scenario_id=scenario_id,
            run_id=run_id,
            timestamp_local=val.timestamp_local,
            recommended_ac_units_on=ac_on,
            recommended_ac_setpoint_c=sp,
            recommended_fan_units_on=fan_on,
            grid_energy_kwh=best_metrics["grid_energy_kwh"],
            solar_energy_used_kwh=best_metrics["solar_energy_used_kwh"],
            battery_charge_kwh=best_metrics["battery_charge_kwh"],
            battery_discharge_kwh=best_metrics["battery_discharge_kwh"],
            battery_soc_kwh=best_metrics["battery_soc_kwh"],
            cooling_energy_kwh=best_metrics["cooling_energy_kwh"],
            estimated_indoor_temp_c=best_metrics["estimated_indoor_temp_c"],
            comfort_status=best_metrics["comfort_status"],
            interval_cost_pkr=best_metrics["interval_cost_pkr"],
            interval_emissions_kgco2e=best_metrics["interval_emissions_kgco2e"],
            reason_code=reason,
            explanation=explanation,
            constraint_violation_count=len(violations),
            constraint_violation_details="; ".join(violations) if violations else None,
        )
        output_rows.append(row)
        
    db.bulk_save_objects(output_rows)
    db.commit()
    
    # Calculate Run Aggregated Summary Metrics
    runtime = time.time() - start_time
    
    period_start = intervals[0].timestamp_local
    period_end = intervals[-1].timestamp_local
    
    baseline_energy = sum(b["cooling_energy_kwh"] for b in baseline_results)
    opt_energy = sum(r.cooling_energy_kwh for r in output_rows)
    energy_saving = baseline_energy - opt_energy
    energy_saving_pct = (energy_saving / baseline_energy * 100.0) if baseline_energy > 0 else 0.0
    
    baseline_cost = sum(b["cost_pkr"] for b in baseline_results)
    opt_cost = sum(r.interval_cost_pkr for r in output_rows)
    cost_saving = baseline_cost - opt_cost
    cost_saving_pct = (cost_saving / baseline_cost * 100.0) if baseline_cost > 0 else 0.0
    
    baseline_emissions = sum(b["emissions_kgco2"] for b in baseline_results)
    opt_emissions = sum(r.interval_emissions_kgco2e for r in output_rows)
    emissions_avoided = baseline_emissions - opt_emissions
    
    # Peak grid energy and demand
    peak_grid = max(r.grid_energy_kwh / dt for r in output_rows)
    # Peak period energy
    peak_period_grid_energy = sum(r.grid_energy_kwh for r in output_rows if intervals[output_rows.index(r)].tariff_type == PEAK)
    
    # Solar capacity utilization
    solar_avail_total = sum(calculate_solar_available(asset.solar_capacity_kw if asset else 0.0, asset.solar_conversion_efficiency if asset else 0.0, r.solar_irradiance_w_m2) * dt for r in intervals)
    solar_used_total = sum(r.solar_energy_used_kwh for r in output_rows)
    solar_util_pct = (solar_used_total / solar_avail_total * 100.0) if solar_avail_total > 0 else 0.0
    
    # Comfort compliance
    occupied_intervals = [r for r in output_rows if intervals[output_rows.index(r)].occupancy_count > 0]
    num_occupied = len(occupied_intervals)
    compliant_occupied = sum(1 for r in occupied_intervals if r.comfort_status == COMFORTABLE)
    comfort_pct = (compliant_occupied / num_occupied * 100.0) if num_occupied > 0 else 100.0
    
    unsafe_occupied = sum(1 for r in occupied_intervals if r.comfort_status == UNSAFE)
    total_violations = sum(r.constraint_violation_count for r in output_rows)
    
    summary = OutputSummary(
        scenario_id=scenario_id,
        run_id=run_id,
        period_start=period_start,
        period_end=period_end,
        baseline_energy_kwh=baseline_energy,
        optimized_energy_kwh=opt_energy,
        energy_saving_kwh=energy_saving,
        energy_saving_pct=energy_saving_pct,
        baseline_cost_pkr=baseline_cost,
        optimized_cost_pkr=opt_cost,
        cost_saving_pkr=cost_saving,
        cost_saving_pct=cost_saving_pct,
        baseline_emissions_kgco2e=baseline_emissions,
        optimized_emissions_kgco2e=opt_emissions,
        emissions_avoided_kgco2e=emissions_avoided,
        peak_grid_demand_kw=peak_grid,
        peak_period_grid_energy_kwh=peak_period_grid_energy,
        solar_available_kwh=solar_avail_total,
        solar_used_kwh=solar_used_total,
        solar_utilization_pct=solar_util_pct,
        comfort_compliance_pct=comfort_pct,
        unsafe_occupied_intervals=unsafe_occupied,
        constraint_violations=total_violations,
        runtime_seconds=runtime,
        algorithm_version=algorithm_version,
    )
    
    db.add(summary)
    
    # Update optimization run record
    opt_run.status = "completed"
    opt_run.runtime_seconds = runtime
    db.commit()
    
    return run_id
