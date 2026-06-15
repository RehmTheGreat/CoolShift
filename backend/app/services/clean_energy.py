"""CleanEnergyManager class for solar production and battery dispatch management."""

from typing import Dict

class CleanEnergyManager:
    """Manages solar production estimation and battery state-of-charge tracking.
    
    Supports rule-based energy dispatch priorities for 15-minute intervals.
    """
    
    def __init__(
        self,
        solar_capacity_kw: float = 0.0,
        solar_conversion_efficiency: float = 0.0,
        battery_capacity_kwh: float = 0.0,
        initial_soc_kwh: float = 0.0,
        minimum_reserve_kwh: float = 0.0,
        max_charge_kw: float = 0.0,
        max_discharge_kw: float = 0.0,
        charge_efficiency: float = 1.0,
        discharge_efficiency: float = 1.0,
        charge_from_grid_off_peak: bool = False,
    ):
        """Initializes the manager with energy asset constraints.
        
        Args:
            solar_capacity_kw: Rated solar panel capacity in kW.
            solar_conversion_efficiency: Efficiency of solar generation.
            battery_capacity_kwh: Total battery capacity in kWh.
            initial_soc_kwh: Starting state of charge of the battery in kWh.
            minimum_reserve_kwh: Minimum SOC reserve in kWh (soft constraint).
            max_charge_kw: Maximum battery charging power in kW.
            max_discharge_kw: Maximum battery discharging power in kW.
            charge_efficiency: Battery charging efficiency.
            discharge_efficiency: Battery discharging efficiency.
            charge_from_grid_off_peak: Toggle to enable grid charging during off-peak.
        """
        self.solar_capacity_kw = max(0.0, float(solar_capacity_kw or 0.0))
        self.solar_conversion_efficiency = max(0.0, float(solar_conversion_efficiency or 0.0))
        self.battery_capacity_kwh = max(0.0, float(battery_capacity_kwh or 0.0))
        
        # Ensure initial SOC is clamped within [0, battery_capacity]
        init_soc = float(initial_soc_kwh or 0.0)
        self.battery_soc_kwh = min(self.battery_capacity_kwh, max(0.0, init_soc))
        
        # Reserve should be within [0, battery_capacity]
        reserve = float(minimum_reserve_kwh or 0.0)
        self.minimum_reserve_kwh = min(self.battery_capacity_kwh, max(0.0, reserve))
        
        self.max_charge_kw = max(0.0, float(max_charge_kw or 0.0))
        self.max_discharge_kw = max(0.0, float(max_discharge_kw or 0.0))
        self.charge_efficiency = max(0.0, float(charge_efficiency or 1.0))
        self.discharge_efficiency = max(0.0, float(discharge_efficiency or 1.0))
        self.charge_from_grid_off_peak = bool(charge_from_grid_off_peak)

    def process_interval(
        self,
        demand_kw: float,
        solar_irradiance_w_m2: float,
        grid_available: bool,
        tariff_type: str,
        is_emergency: bool = False,
        interval_minutes: int = 15,
    ) -> Dict[str, float]:
        """Processes a single interval, running the solar and battery dispatch logic.
        
        Args:
            demand_kw: Immediate load demand in kW during the interval.
            solar_irradiance_w_m2: Solar irradiance in W/m^2.
            grid_available: True if the utility grid is available.
            tariff_type: Tariff period e.g. "peak", "off-peak", or "standard".
            is_emergency: If True, battery reserve is ignored (can discharge to 0).
            interval_minutes: Number of minutes in this interval (default 15).
            
        Returns:
            Dict containing the dispatched flows and states in kW/kWh.
        """
        dt = interval_minutes / 60.0
        
        # 1. Solar Production Estimation
        # solar_output_kw = (solar_irradiance_w_m2 / 1000) * solar_capacity_kw * solar_conversion_efficiency
        # Clamped to [0, solar_capacity_kw]
        if self.solar_capacity_kw > 0.0 and solar_irradiance_w_m2 > 0.0:
            raw_output = (solar_irradiance_w_m2 / 1000.0) * self.solar_capacity_kw * self.solar_conversion_efficiency
            solar_generated_kw = min(raw_output, self.solar_capacity_kw)
        else:
            solar_generated_kw = 0.0
            
        solar_generated_kwh = solar_generated_kw * dt
        
        demand_kwh = max(0.0, float(demand_kw)) * dt
        remaining_demand_kwh = demand_kwh
        
        # Initialize tracking vars
        solar_used_kwh = 0.0
        solar_curtailed_kwh = 0.0
        battery_charge_kwh = 0.0
        battery_discharge_kwh = 0.0
        grid_energy_kwh = 0.0
        unserved_energy_kwh = 0.0
        
        # Priority 1: Use solar for immediate demand first
        solar_to_demand = min(solar_generated_kwh, remaining_demand_kwh)
        solar_used_kwh += solar_to_demand
        remaining_demand_kwh -= solar_to_demand
        excess_solar_kwh = solar_generated_kwh - solar_to_demand
        
        # Priority 2: Excess solar -> charge battery (if not full)
        charge_solar_kwh = 0.0
        if self.battery_capacity_kwh > 0.0 and excess_solar_kwh > 0.0:
            max_soc_increase = max(0.0, self.battery_capacity_kwh - self.battery_soc_kwh)
            max_charge_energy = self.max_charge_kw * dt
            max_energy_into_charger = max_soc_increase / self.charge_efficiency if self.charge_efficiency > 0.0 else 0.0
            
            charge_solar_kwh = min(excess_solar_kwh, max_charge_energy, max_energy_into_charger)
            
            self.battery_soc_kwh += charge_solar_kwh * self.charge_efficiency
            excess_solar_kwh -= charge_solar_kwh
            solar_used_kwh += charge_solar_kwh
            
        solar_curtailed_kwh = excess_solar_kwh
        battery_charge_kwh += charge_solar_kwh
        
        # Priority 3 & 4: Battery Discharge
        # Can only discharge if we have demand left, a battery, and did not charge in this interval
        # (Though charge_solar_kwh would be 0 if remaining_demand_kwh > 0, we verify battery_charge_kwh is 0)
        discharged_to_load = 0.0
        
        if remaining_demand_kwh > 0.0 and self.battery_capacity_kwh > 0.0 and battery_charge_kwh == 0.0:
            # Determine if we can discharge
            should_discharge = False
            allow_below_reserve = False
            
            if not grid_available or is_emergency:
                # Priority 3: If grid unavailable -> discharge battery (emergency mode)
                should_discharge = True
                allow_below_reserve = True
            elif tariff_type == "peak":
                # Priority 4: If peak tariff -> prefer battery over grid
                should_discharge = True
                allow_below_reserve = False
                
            if should_discharge:
                min_soc = 0.0 if allow_below_reserve else self.minimum_reserve_kwh
                usable_soc = max(0.0, self.battery_soc_kwh - min_soc)
                
                max_discharge_energy = self.max_discharge_kw * dt
                max_energy_delivered = usable_soc * self.discharge_efficiency
                
                discharged_to_load = min(remaining_demand_kwh, max_discharge_energy, max_energy_delivered)
                
                soc_reduction = discharged_to_load / self.discharge_efficiency if self.discharge_efficiency > 0.0 else 0.0
                self.battery_soc_kwh -= soc_reduction
                remaining_demand_kwh -= discharged_to_load
                battery_discharge_kwh = discharged_to_load

        # Grid energy draw to meet remaining demand
        if remaining_demand_kwh > 0.0:
            if grid_available:
                grid_energy_kwh += remaining_demand_kwh
                remaining_demand_kwh = 0.0
            else:
                # Outage: demand is unserved
                unserved_energy_kwh = remaining_demand_kwh
                remaining_demand_kwh = 0.0

        # Priority 5: If off-peak + battery not full -> charge from grid (optional strategy)
        # We can only charge if grid is available, option is enabled, battery is not full,
        # and we did NOT discharge in this interval.
        if (
            self.charge_from_grid_off_peak
            and grid_available
            and tariff_type == "off-peak"
            and self.battery_capacity_kwh > 0.0
            and self.battery_soc_kwh < self.battery_capacity_kwh
            and battery_discharge_kwh == 0.0
        ):
            max_soc_increase = max(0.0, self.battery_capacity_kwh - self.battery_soc_kwh)
            max_charge_energy = self.max_charge_kw * dt
            max_energy_into_charger = max_soc_increase / self.charge_efficiency if self.charge_efficiency > 0.0 else 0.0
            
            charge_grid_kwh = min(max_charge_energy, max_energy_into_charger)
            
            self.battery_soc_kwh += charge_grid_kwh * self.charge_efficiency
            battery_charge_kwh += charge_grid_kwh
            grid_energy_kwh += charge_grid_kwh
            
        return {
            "solar_generated_kw": solar_generated_kw,
            "solar_used_kwh": solar_used_kwh,
            "solar_curtailed_kwh": solar_curtailed_kwh,
            "battery_charge_kwh": battery_charge_kwh,
            "battery_discharge_kwh": battery_discharge_kwh,
            "battery_soc_kwh": self.battery_soc_kwh,
            "grid_energy_kwh": grid_energy_kwh,
            "unserved_energy_kwh": unserved_energy_kwh,
        }
