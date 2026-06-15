"""Solar and battery dispatch service."""

def calculate_solar_available(
    solar_capacity_kw: float | None,
    solar_conversion_efficiency: float | None,
    solar_irradiance_w_m2: float | None,
) -> float:
    """Calculates available solar power in kW.
    
    Formula: capacity * efficiency * (irradiance / 1000)
    """
    if not solar_capacity_kw or not solar_conversion_efficiency or not solar_irradiance_w_m2:
        return 0.0
    return solar_capacity_kw * solar_conversion_efficiency * (solar_irradiance_w_m2 / 1000.0)

def dispatch_battery_charge(
    current_soc_kwh: float,
    battery_capacity_kwh: float,
    max_charge_kw: float,
    charge_efficiency: float,
    excess_power_kw: float,
    interval_minutes: int = 15,
) -> tuple[float, float]:
    """Calculates battery charging for the interval.
    
    VAL-05: 2.0 kWh charge * 94% efficiency = 1.88 kWh SOC increase.
    Wait, in VAL-05, the input is 2.0 kWh of energy delivered to the battery charger,
    or is it 2.0 kWh of power? It says: "2.0 kWh charge * 94% efficiency = 1.88 kWh SOC increase".
    This means:
    - energy_into_charger = 2.0 kWh
    - energy_added_to_soc = 2.0 * charge_efficiency = 1.88 kWh.
    
    Let's implement this:
    - Max energy we can charge (limited by remaining capacity in battery):
      max_soc_increase = battery_capacity_kwh - current_soc_kwh
      max_energy_into_charger = max_soc_increase / charge_efficiency
    - Max energy we can charge (limited by max_charge_kw):
      max_charger_energy = max_charge_kw * (interval_minutes / 60.0)
    - Available excess energy:
      available_excess_energy = excess_power_kw * (interval_minutes / 60.0)
      
    - Actual energy into charger:
      energy_into_charger = min(available_excess_energy, max_charger_energy, max_energy_into_charger)
      
    - SOC increase:
      soc_increase = energy_into_charger * charge_efficiency
      
    Returns: (energy_into_charger, soc_increase)
    """
    if battery_capacity_kwh <= 0.0 or excess_power_kw <= 0.0:
        return 0.0, 0.0
        
    dt = interval_minutes / 60.0
    
    max_soc_increase = max(0.0, battery_capacity_kwh - current_soc_kwh)
    max_energy_into_charger = max_soc_increase / charge_efficiency if charge_efficiency > 0 else 0.0
    
    max_charger_energy = max_charge_kw * dt
    available_excess_energy = excess_power_kw * dt
    
    energy_into_charger = min(available_excess_energy, max_charger_energy, max_energy_into_charger)
    soc_increase = energy_into_charger * charge_efficiency
    
    return energy_into_charger, soc_increase

def dispatch_battery_discharge(
    current_soc_kwh: float,
    minimum_reserve_kwh: float,
    max_discharge_kw: float,
    discharge_efficiency: float,
    required_power_kw: float,
    emergency_mode: bool = False,
    interval_minutes: int = 15,
) -> tuple[float, float]:
    """Calculates battery discharging for the interval.
    
    VAL-06: 2.0 kWh delivered from battery (to load) at 94% efficiency:
    requires 2.0 / 0.94 = 2.12766 kWh decrease in SOC.
    
    Formula:
    - Required energy (at load):
      required_energy = required_power_kw * (interval_minutes / 60.0)
    - Max energy we can discharge (limited by SOC and reserve):
      usable_soc = current_soc_kwh - (0.0 if emergency_mode else minimum_reserve_kwh)
      usable_soc = max(0.0, usable_soc)
      max_energy_delivered = usable_soc * discharge_efficiency
    - Max energy we can discharge (limited by max_discharge_kw):
      max_discharge_energy = max_discharge_kw * (interval_minutes / 60.0)
      
    - Actual energy delivered:
      energy_delivered = min(required_energy, max_energy_delivered, max_discharge_energy)
    - SOC reduction:
      soc_reduction = energy_delivered / discharge_efficiency if discharge_efficiency > 0 else 0.0
      
    Returns: (energy_delivered, soc_reduction)
    """
    if current_soc_kwh <= 0.0 or required_power_kw <= 0.0 or discharge_efficiency <= 0.0:
        return 0.0, 0.0
        
    dt = interval_minutes / 60.0
    
    reserve = 0.0 if emergency_mode else minimum_reserve_kwh
    usable_soc = max(0.0, current_soc_kwh - reserve)
    
    max_energy_delivered = usable_soc * discharge_efficiency
    max_discharge_energy = max_discharge_kw * dt
    required_energy = required_power_kw * dt
    
    energy_delivered = min(required_energy, max_energy_delivered, max_discharge_energy)
    soc_reduction = energy_delivered / discharge_efficiency
    
    return energy_delivered, soc_reduction
