"""Export service for generating CSV/XLSX results."""

import io
from typing import Tuple
import pandas as pd
from sqlalchemy.orm import Session
from app.models import OutputSchedule, OutputSummary
from app.utils.constants import OUTPUT_SCHEDULE_COLUMNS, OUTPUT_SUMMARY_COLUMNS

def export_run_to_csv(run_id: str, db: Session) -> str:
    """Generates a CSV string containing the optimization interval schedule."""
    rows = db.query(OutputSchedule).filter_by(run_id=run_id).order_by(OutputSchedule.timestamp_local).all()
    if not rows:
        raise ValueError(f"No output schedule found for run '{run_id}'.")
        
    data = []
    for r in rows:
        data.append({
            "scenario_id": r.scenario_id,
            "run_id": r.run_id,
            "timestamp_local": r.timestamp_local,
            "recommended_ac_units_on": r.recommended_ac_units_on,
            "recommended_ac_setpoint_c": r.recommended_ac_setpoint_c if r.recommended_ac_setpoint_c is not None else "",
            "recommended_fan_units_on": r.recommended_fan_units_on,
            "grid_energy_kwh": r.grid_energy_kwh,
            "solar_energy_used_kwh": r.solar_energy_used_kwh,
            "battery_charge_kwh": r.battery_charge_kwh,
            "battery_discharge_kwh": r.battery_discharge_kwh,
            "battery_soc_kwh": r.battery_soc_kwh,
            "cooling_energy_kwh": r.cooling_energy_kwh,
            "estimated_indoor_temp_c": r.estimated_indoor_temp_c,
            "comfort_status": r.comfort_status,
            "interval_cost_pkr": r.interval_cost_pkr,
            "interval_emissions_kgco2e": r.interval_emissions_kgco2e,
            "reason_code": r.reason_code,
            "explanation": r.explanation,
            "constraint_violation_count": r.constraint_violation_count,
            "constraint_violation_details": r.constraint_violation_details if r.constraint_violation_details else "",
        })
        
    df = pd.DataFrame(data)
    # Ensure correct column ordering
    df = df[OUTPUT_SCHEDULE_COLUMNS]
    
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()

def export_run_to_xlsx(run_id: str, db: Session) -> bytes:
    """Generates an Excel workbook (bytes) containing Schedule and Summary sheets."""
    rows = db.query(OutputSchedule).filter_by(run_id=run_id).order_by(OutputSchedule.timestamp_local).all()
    summary_row = db.query(OutputSummary).filter_by(run_id=run_id).first()
    
    if not rows:
        raise ValueError(f"No output schedule found for run '{run_id}'.")
        
    # Schedule Sheet Data
    sched_data = []
    for r in rows:
        sched_data.append({
            "scenario_id": r.scenario_id,
            "run_id": r.run_id,
            "timestamp_local": r.timestamp_local,
            "recommended_ac_units_on": r.recommended_ac_units_on,
            "recommended_ac_setpoint_c": r.recommended_ac_setpoint_c,
            "recommended_fan_units_on": r.recommended_fan_units_on,
            "grid_energy_kwh": r.grid_energy_kwh,
            "solar_energy_used_kwh": r.solar_energy_used_kwh,
            "battery_charge_kwh": r.battery_charge_kwh,
            "battery_discharge_kwh": r.battery_discharge_kwh,
            "battery_soc_kwh": r.battery_soc_kwh,
            "cooling_energy_kwh": r.cooling_energy_kwh,
            "estimated_indoor_temp_c": r.estimated_indoor_temp_c,
            "comfort_status": r.comfort_status,
            "interval_cost_pkr": r.interval_cost_pkr,
            "interval_emissions_kgco2e": r.interval_emissions_kgco2e,
            "reason_code": r.reason_code,
            "explanation": r.explanation,
            "constraint_violation_count": r.constraint_violation_count,
            "constraint_violation_details": r.constraint_violation_details if r.constraint_violation_details else "",
        })
    df_sched = pd.DataFrame(sched_data)
    df_sched = df_sched[OUTPUT_SCHEDULE_COLUMNS]
    
    # Summary Sheet Data
    sum_data = []
    if summary_row:
        sum_data.append({
            "scenario_id": summary_row.scenario_id,
            "run_id": summary_row.run_id,
            "period_start": summary_row.period_start,
            "period_end": summary_row.period_end,
            "baseline_energy_kwh": summary_row.baseline_energy_kwh,
            "optimized_energy_kwh": summary_row.optimized_energy_kwh,
            "energy_saving_kwh": summary_row.energy_saving_kwh,
            "energy_saving_pct": summary_row.energy_saving_pct,
            "baseline_cost_pkr": summary_row.baseline_cost_pkr,
            "optimized_cost_pkr": summary_row.optimized_cost_pkr,
            "cost_saving_pkr": summary_row.cost_saving_pkr,
            "cost_saving_pct": summary_row.cost_saving_pct,
            "baseline_emissions_kgco2e": summary_row.baseline_emissions_kgco2e,
            "optimized_emissions_kgco2e": summary_row.optimized_emissions_kgco2e,
            "emissions_avoided_kgco2e": summary_row.emissions_avoided_kgco2e,
            "peak_grid_demand_kw": summary_row.peak_grid_demand_kw,
            "peak_period_grid_energy_kwh": summary_row.peak_period_grid_energy_kwh,
            "solar_available_kwh": summary_row.solar_available_kwh,
            "solar_used_kwh": summary_row.solar_used_kwh,
            "solar_utilization_pct": summary_row.solar_utilization_pct,
            "comfort_compliance_pct": summary_row.comfort_compliance_pct,
            "unsafe_occupied_intervals": summary_row.unsafe_occupied_intervals,
            "constraint_violations": summary_row.constraint_violations,
            "runtime_seconds": summary_row.runtime_seconds,
            "algorithm_version": summary_row.algorithm_version,
        })
    df_sum = pd.DataFrame(sum_data)
    if not df_sum.empty:
        df_sum = df_sum[OUTPUT_SUMMARY_COLUMNS]
        
    # Create excel in memory
    excel_io = io.BytesIO()
    with pd.ExcelWriter(excel_io, engine="openpyxl") as writer:
        df_sched.to_excel(writer, sheet_name="Output_Schedule", index=False)
        if not df_sum.empty:
            df_sum.to_excel(writer, sheet_name="Output_Summary", index=False)
            
    return excel_io.getvalue()
