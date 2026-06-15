"""Router for retrieving optimization schedules and summaries."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models import OutputSchedule, OutputSummary, OptimizationRun
from app.schemas import OutputScheduleSchema, OutputSummarySchema
from app.services.baseline import calculate_baseline

router = APIRouter(prefix="/results", tags=["Results"])

@router.get("/{run_id}", response_model=List[OutputScheduleSchema])
def get_run_schedule(run_id: str, db: Session = Depends(get_db)):
    """Retrieves the full 15-minute resolution optimized schedule for a run."""
    rows = db.query(OutputSchedule).filter_by(run_id=run_id).order_by(OutputSchedule.timestamp_local).all()
    if not rows:
        raise HTTPException(status_code=404, detail=f"No output schedule found for run '{run_id}'.")
    return rows

@router.get("/{run_id}/summary", response_model=OutputSummarySchema)
def get_run_summary(run_id: str, db: Session = Depends(get_db)):
    """Retrieves the aggregated summary metrics for a run."""
    summary = db.query(OutputSummary).filter_by(run_id=run_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail=f"No summary found for run '{run_id}'.")
    return summary

@router.get("/compare/{scenario_id}", response_model=Dict[str, Any])
def get_comparison(scenario_id: str, run_id: str | None = None, db: Session = Depends(get_db)):
    """Retrieves baseline vs optimized time-series and summary comparative data.
    
    If run_id is omitted, the most recent completed run for the scenario is used.
    """
    # 1. Resolve run_id
    if not run_id:
        latest_run = db.query(OptimizationRun).filter_by(scenario_id=scenario_id, status="completed").order_by(OptimizationRun.created_at.desc()).first()
        if not latest_run:
            raise HTTPException(status_code=404, detail=f"No completed runs found for scenario '{scenario_id}'.")
        run_id = latest_run.run_id
        
    run = db.query(OptimizationRun).filter_by(run_id=run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
        
    # 2. Get summaries
    opt_summary = db.query(OutputSummary).filter_by(run_id=run_id).first()
    
    # 3. Get schedules
    opt_scheds = db.query(OutputSchedule).filter_by(run_id=run_id).order_by(OutputSchedule.timestamp_local).all()
    
    # 4. Get baseline data
    try:
        baseline_results = calculate_baseline(scenario_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate baseline for comparison: {str(e)}")
        
    # 5. Merge time series side by side
    merged_timeline = []
    base_map = {b["timestamp_local"]: b for b in baseline_results}
    
    for opt in opt_scheds:
        ts = opt.timestamp_local
        base = base_map.get(ts, {})
        
        merged_timeline.append({
            "timestamp_local": ts,
            
            # Temperatures
            "outdoor_temp": opt.run.scenario.interval_inputs[0].temperature_c, # fallback, we will fetch directly
            
            # AC and fan counts
            "baseline_ac_units_on": base.get("ac_units_on", 0),
            "recommended_ac_units_on": opt.recommended_ac_units_on,
            "baseline_fan_units_on": base.get("fan_units_on", 0),
            "recommended_fan_units_on": opt.recommended_fan_units_on,
            
            # Indoor temperatures
            "baseline_indoor_temp_c": base.get("estimated_indoor_temp_c", 0.0),
            "optimized_indoor_temp_c": opt.estimated_indoor_temp_c,
            
            # Comfort statuses
            "baseline_comfort_status": base.get("comfort_status", "comfortable"),
            "optimized_comfort_status": opt.comfort_status,
            
            # Energies (cooling & grid)
            "baseline_cooling_energy_kwh": base.get("cooling_energy_kwh", 0.0),
            "optimized_cooling_energy_kwh": opt.cooling_energy_kwh,
            "baseline_grid_energy_kwh": base.get("grid_energy_kwh", 0.0),
            "optimized_grid_energy_kwh": opt.grid_energy_kwh,
            
            # Solar & Battery flows
            "solar_energy_used_kwh": opt.solar_energy_used_kwh,
            "battery_charge_kwh": opt.battery_charge_kwh,
            "battery_discharge_kwh": opt.battery_discharge_kwh,
            "battery_soc_kwh": opt.battery_soc_kwh,
            
            # Cost & Emissions
            "baseline_cost_pkr": base.get("cost_pkr", 0.0),
            "optimized_cost_pkr": opt.interval_cost_pkr,
            "baseline_emissions_kgco2e": base.get("emissions_kgco2", 0.0),
            "optimized_emissions_kgco2e": opt.interval_emissions_kgco2e,
            
            "reason_code": opt.reason_code,
            "explanation": opt.explanation,
        })
        
    # Update outdoor_temp properly in merged timeline
    from app.models import IntervalInput
    intervals = db.query(IntervalInput).filter_by(scenario_id=scenario_id).order_by(IntervalInput.timestamp_local).all()
    int_map = {i.timestamp_local: i for i in intervals}
    for item in merged_timeline:
        ts = item["timestamp_local"]
        i_data = int_map.get(ts)
        if i_data:
            item["outdoor_temp"] = i_data.temperature_c
            item["humidity_pct"] = i_data.relative_humidity_pct
            item["heat_index_c"] = i_data.heat_index_c
            item["tariff_pkr_per_kwh"] = i_data.tariff_pkr_per_kwh
            
    return {
        "scenario_id": scenario_id,
        "run_id": run_id,
        "summary": OutputSummarySchema.model_validate(opt_summary),
        "timeline": merged_timeline,
    }
