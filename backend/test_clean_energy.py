"""Verification test script for CleanEnergyManager."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import ScenarioProfile, Appliance, EnergyAsset, IntervalInput, BaselineSchedule
from app.services.clean_energy import CleanEnergyManager

def test_validation_cases():
    print("--- Running VAL-05 and VAL-06 Verification ---")
    
    # VAL-05: 2.0 kWh charge * 0.94 efficiency = 1.88 kWh added to SOC
    manager = CleanEnergyManager(
        battery_capacity_kwh=10.0,
        initial_soc_kwh=5.0,
        charge_efficiency=0.94,
        max_charge_kw=10.0
    )
    
    # 8 kW excess solar * 0.25h = 2.0 kWh energy available to charge
    res = manager.process_interval(
        demand_kw=0.0,
        solar_irradiance_w_m2=8000.0, # Will generate 8 kW if capacity=1 and efficiency=1
        grid_available=True,
        tariff_type="off-peak",
        interval_minutes=15
    )
    # But wait, to be precise, let's just bypass the solar generation and feed it excess solar.
    # To do that, we can configure solar capacity = 8.0 kW, efficiency = 1.0, irradiance = 1000 W/m2.
    # solar_output = (1000/1000) * 8 * 1 = 8 kW. 8 kW * 0.25h = 2.0 kWh.
    manager.solar_capacity_kw = 8.0
    manager.solar_conversion_efficiency = 1.0
    
    res = manager.process_interval(
        demand_kw=0.0,
        solar_irradiance_w_m2=1000.0,
        grid_available=True,
        tariff_type="off-peak",
        interval_minutes=15
    )
    
    assert abs(res["battery_charge_kwh"] - 2.0) < 1e-5, f"VAL-05 charge input failed: expected 2.0, got {res['battery_charge_kwh']}"
    assert abs(res["battery_soc_kwh"] - (5.0 + 1.88)) < 1e-5, f"VAL-05 SOC failed: expected 6.88, got {res['battery_soc_kwh']}"
    print("VAL-05 passed successfully!")
    
    # VAL-06: 2.0 kWh delivered needs 2.0/0.94 = 2.12766 kWh from SOC
    manager = CleanEnergyManager(
        battery_capacity_kwh=10.0,
        initial_soc_kwh=5.0,
        discharge_efficiency=0.94,
        max_discharge_kw=10.0,
        minimum_reserve_kwh=0.0 # Make sure reserve doesn't block it
    )
    
    # Demand = 8 kW (8 kW * 0.25h = 2.0 kWh demand)
    # No solar, grid unavailable (emergency)
    res = manager.process_interval(
        demand_kw=8.0,
        solar_irradiance_w_m2=0.0,
        grid_available=False,
        tariff_type="peak",
        is_emergency=True,
        interval_minutes=15
    )
    
    expected_soc_reduction = 2.0 / 0.94
    expected_soc = 5.0 - expected_soc_reduction
    assert abs(res["battery_discharge_kwh"] - 2.0) < 1e-5, f"VAL-06 discharge delivered failed: expected 2.0, got {res['battery_discharge_kwh']}"
    assert abs(res["battery_soc_kwh"] - expected_soc) < 1e-5, f"VAL-06 SOC failed: expected {expected_soc}, got {res['battery_soc_kwh']}"
    print("VAL-06 passed successfully!")
    print("")

def run_scenario_simulation(scenario_id: str):
    print(f"--- Simulating Scenario {scenario_id} ---")
    db = SessionLocal()
    try:
        profile = db.query(ScenarioProfile).filter_by(scenario_id=scenario_id).first()
        if not profile:
            print(f"Scenario {scenario_id} not found in database.")
            return
            
        asset = db.query(EnergyAsset).filter_by(scenario_id=scenario_id).first()
        if not asset:
            asset_params = {
                "solar_capacity_kw": 0.0,
                "solar_conversion_efficiency": 0.0,
                "battery_capacity_kwh": 0.0,
                "initial_soc_kwh": 0.0,
                "minimum_reserve_kwh": 0.0,
                "max_charge_kw": 0.0,
                "max_discharge_kw": 0.0,
                "charge_efficiency": 1.0,
                "discharge_efficiency": 1.0
            }
        else:
            asset_params = {
                "solar_capacity_kw": asset.solar_capacity_kw,
                "solar_conversion_efficiency": asset.solar_conversion_efficiency,
                "battery_capacity_kwh": asset.battery_capacity_kwh,
                "initial_soc_kwh": asset.initial_soc_kwh,
                "minimum_reserve_kwh": asset.minimum_reserve_kwh,
                "max_charge_kw": asset.max_charge_kw,
                "max_discharge_kw": asset.max_discharge_kw,
                "charge_efficiency": asset.charge_efficiency,
                "discharge_efficiency": asset.discharge_efficiency
            }
            
        print("Asset Parameters:")
        for k, v in asset_params.items():
            print(f"  {k}: {v}")
            
        # Get appliances
        appliances = db.query(Appliance).filter_by(scenario_id=scenario_id).all()
        ac_app = next((a for a in appliances if "ac" in a.appliance_type.lower()), None)
        fan_app = next((a for a in appliances if "fan" in a.appliance_type.lower()), None)
        
        ac_rated_power = ac_app.rated_power_kw if ac_app else 0.0
        fan_rated_power = fan_app.rated_power_kw if fan_app else 0.0
        
        # Load intervals and schedules
        intervals = db.query(IntervalInput).filter_by(scenario_id=scenario_id).order_by(IntervalInput.timestamp_local).all()
        baseline_schedules = db.query(BaselineSchedule).filter_by(scenario_id=scenario_id).order_by(BaselineSchedule.timestamp_local).all()
        sched_map = {s.timestamp_local: s for s in baseline_schedules}
        
        # Initialize Manager
        manager = CleanEnergyManager(**asset_params)
        
        # Aggregators
        total_demand_kwh = 0.0
        total_solar_generated_kwh = 0.0
        total_solar_used_kwh = 0.0
        total_solar_curtailed_kwh = 0.0
        total_battery_charge_kwh = 0.0
        total_battery_discharge_kwh = 0.0
        total_grid_energy_kwh = 0.0
        total_unserved_energy_kwh = 0.0
        
        interval_count = 0
        
        for val in intervals:
            dt = val.interval_minutes / 60.0
            sched = sched_map.get(val.timestamp_local)
            
            ac_on = sched.baseline_ac_units_on if sched else 0
            fan_on = sched.baseline_fan_units_on if sched else 0
            other_kw = sched.baseline_other_cooling_kw if (sched and sched.baseline_other_cooling_kw) else 0.0
            
            cooling_kw = (ac_on * ac_rated_power) + (fan_on * fan_rated_power) + other_kw
            demand_kw = cooling_kw + val.non_cooling_load_kw
            
            # Run manager step
            res = manager.process_interval(
                demand_kw=demand_kw,
                solar_irradiance_w_m2=val.solar_irradiance_w_m2,
                grid_available=val.grid_available,
                tariff_type=val.tariff_type.lower(), # Ensure case-insensitivity
                interval_minutes=val.interval_minutes
            )
            
            # Aggregate
            total_demand_kwh += demand_kw * dt
            total_solar_generated_kwh += res["solar_generated_kw"] * dt
            total_solar_used_kwh += res["solar_used_kwh"]
            total_solar_curtailed_kwh += res["solar_curtailed_kwh"]
            total_battery_charge_kwh += res["battery_charge_kwh"]
            total_battery_discharge_kwh += res["battery_discharge_kwh"]
            total_grid_energy_kwh += res["grid_energy_kwh"]
            total_unserved_energy_kwh += res["unserved_energy_kwh"]
            
            interval_count += 1
            
        print(f"Simulated {interval_count} intervals successfully.")
        print(f"Results Summary:")
        print(f"  Total Demand: {total_demand_kwh:.3f} kWh")
        print(f"  Total Solar Generated: {total_solar_generated_kwh:.3f} kWh")
        print(f"  Total Solar Used: {total_solar_used_kwh:.3f} kWh")
        print(f"  Total Solar Curtailed: {total_solar_curtailed_kwh:.3f} kWh")
        print(f"  Total Battery Charge: {total_battery_charge_kwh:.3f} kWh")
        print(f"  Total Battery Discharge: {total_battery_discharge_kwh:.3f} kWh")
        print(f"  Ending Battery SOC: {manager.battery_soc_kwh:.3f} kWh")
        print(f"  Total Grid Energy Used: {total_grid_energy_kwh:.3f} kWh")
        print(f"  Total Unserved Energy: {total_unserved_energy_kwh:.3f} kWh")
        
        # Energy balance check:
        # grid + solar_used - battery_charge (from solar/grid) + battery_discharge = demand + grid_charging_part?
        # Wait, grid_energy = demand_met_by_grid + grid_charge_energy.
        # solar_used = solar_to_demand + solar_to_charge.
        # total charge = solar_to_charge + grid_charge.
        # So:
        # grid_energy + solar_used = (demand_met_by_grid + grid_charge_energy) + (solar_to_demand + solar_to_charge)
        #                          = (demand_met_by_grid + solar_to_demand) + (grid_charge_energy + solar_to_charge)
        #                          = demand_met_by_generation + total_charge
        # And demand_met_by_generation + battery_discharge_delivered = total_demand - unserved_energy.
        # So:
        # grid_energy + solar_used + battery_discharge_delivered = (total_demand - unserved_energy) + total_charge
        # => (grid_energy + solar_used + battery_discharge_delivered) - (total_demand + total_charge) + unserved_energy = 0
        diff = (total_grid_energy_kwh + total_solar_used_kwh + total_battery_discharge_kwh) - (total_demand_kwh + total_battery_charge_kwh) + total_unserved_energy_kwh
        print(f"  Energy Balance Check (should be 0): {diff:.6f}")
        assert abs(diff) < 1e-4, f"Energy balance check failed! Diff: {diff}"
        print(f"Scenario {scenario_id} simulated and verified successfully!\n")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_validation_cases()
    run_scenario_simulation("PUB-A")
    run_scenario_simulation("PUB-B")
    run_scenario_simulation("PUB-C")
