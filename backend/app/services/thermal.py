"""Thermal indoor temperature model."""

from app.utils.constants import (
    INSULATION_R_VALUES,
    SUN_EXPOSURE_GAIN,
    OCCUPANT_HEAT_GAIN_KW,
    THERMAL_MASS_FACTOR,
    DEFAULT_INDOOR_TEMP_C,
    FAN_COOLING_EFFECT_C,
)

def estimate_indoor_temperature(
    outdoor_temp: float,
    humidity_pct: float,
    solar_irradiance: float,
    occupancy: int,
    insulation_level: str,
    sun_exposure: str,
    area_m2: float,
    ac_units_on: int,
    ac_setpoint_c: float | None,
    fan_units_on: int,
    ac_cooling_capacity_kw: float,  # rated cooling capacity per unit
    ac_rated_power_kw: float,       # rated electrical power per unit
    prev_indoor_temp: float | None = None,
    interval_minutes: int = 15,
    heat_index_c: float | None = None,
    non_cooling_load_kw: float = 0.0,
    grid_available: bool = True,
    solar_available_kw: float = 0.0,
    battery_soc_kwh: float = 0.0,
    fan_rated_power_kw: float = 0.075,
) -> float:
    """Estimates the indoor temperature for the next interval.
    
    Using a simplified resistance-capacitance (RC) thermal model.
    """
    # 1. Initialize T_indoor from outdoor temp at start (or from a sensible default like 28°C)
    if prev_indoor_temp is None:
        if heat_index_c is not None:
            prev_indoor_temp = heat_index_c
        elif outdoor_temp is not None:
            prev_indoor_temp = outdoor_temp
        else:
            prev_indoor_temp = DEFAULT_INDOOR_TEMP_C
            
    dt = interval_minutes / 60.0  # in hours
    
    # 2. Get R (thermal resistance) based on insulation_level:
    # Low = 0.8, Medium = 1.2, High = 1.8 (°C·h/kW)
    ins_lower = insulation_level.lower() if insulation_level else "medium"
    if "low" in ins_lower:
        r = 0.8
    elif "high" in ins_lower:
        r = 1.8
    else:  # medium or other
        r = 1.2
        
    # 3. Get C (thermal capacitance) = area_m2 * 0.05 (kWh/°C)
    c = area_m2 * 0.05 if area_m2 > 0.0 else 2.5
    
    # 4. Handle outage and scale down/disable cooling if backup power is insufficient
    ac_units_effective = float(ac_units_on)
    fan_units_effective = float(fan_units_on)
    if not grid_available:
        # Outage: cooling appliances must run on solar and battery power
        available_power_kw = solar_available_kw + (battery_soc_kwh / dt if battery_soc_kwh is not None else 0.0)
        
        fan_power_needed = fan_units_on * fan_rated_power_kw
        ac_power_needed = ac_units_on * ac_rated_power_kw
        total_power_needed = fan_power_needed + ac_power_needed
        
        if total_power_needed > 0.0 and available_power_kw < total_power_needed:
            # Prioritize powering fans first (very low power draw)
            if available_power_kw >= fan_power_needed:
                fan_units_effective = float(fan_units_on)
                remaining_power_kw = available_power_kw - fan_power_needed
                if ac_power_needed > 0.0:
                    ac_units_effective = ac_units_on * (remaining_power_kw / ac_power_needed)
                else:
                    ac_units_effective = 0.0
            else:
                fan_units_effective = fan_units_on * (available_power_kw / fan_power_needed) if fan_power_needed > 0.0 else 0.0
                ac_units_effective = 0.0
                
    # 5. Q_solar = solar_gain_factor * solar_irradiance * window_area_fraction
    # sun_exposure: Low=0.1, Medium=0.2, High=0.3 (fraction)
    sun_lower = sun_exposure.lower() if sun_exposure else "medium"
    if "low" in sun_lower:
        window_area_fraction = 0.1
    elif "high" in sun_lower:
        window_area_fraction = 0.3
    else:  # medium or other
        window_area_fraction = 0.2
        
    solar_irradiance_kw = solar_irradiance / 1000.0 if solar_irradiance is not None else 0.0
    solar_gain_factor = 0.7  # Typical Solar Heat Gain Coefficient (SHGC)
    q_solar = solar_gain_factor * solar_irradiance_kw * (area_m2 * window_area_fraction)
    
    # 6. Q_occupants = occupancy_count * 0.12 (kW)
    q_occupants = occupancy * 0.12 if occupancy is not None else 0.0
    
    # 7. Q_equipment = other internal gains (kW)
    q_equipment = non_cooling_load_kw if non_cooling_load_kw is not None else 0.0
    
    # 8. Q_cooling = sum(cooling_capacity_kw * units_on) for ACs
    q_cooling = 0.0
    if ac_units_effective > 0.0 and ac_setpoint_c is not None:
        if prev_indoor_temp > ac_setpoint_c:
            q_cooling = ac_units_effective * ac_cooling_capacity_kw
            
    # 9. T_outdoor
    t_outdoor = heat_index_c if heat_index_c is not None else outdoor_temp
    if t_outdoor is None:
        t_outdoor = DEFAULT_INDOOR_TEMP_C
        
    # 10. Solve RC thermal equation:
    # T_indoor(t) = T_indoor(t-1) + Δt * [ (T_outdoor - T_indoor(t-1)) / (R * C) + Q_solar / C + Q_occupants / C + Q_equipment / C - Q_cooling / C ]
    walls_heat_transfer = (t_outdoor - prev_indoor_temp) / (r * c)
    temp_change = dt * (
        walls_heat_transfer
        + (q_solar / c)
        + (q_occupants / c)
        + (q_equipment / c)
        - (q_cooling / c)
    )
    next_indoor_temp = prev_indoor_temp + temp_change
    
    # 11. Clamping to prevent numerical instability or unphysical values
    max_clamp = max(50.0, t_outdoor + 5.0)
    min_clamp = 10.0
    next_indoor_temp = max(min_clamp, min(max_clamp, next_indoor_temp))
    
    # AC shouldn't cool below the setpoint
    if ac_units_effective > 0.0 and ac_setpoint_c is not None:
        if next_indoor_temp < ac_setpoint_c:
            next_indoor_temp = ac_setpoint_c
            
    return next_indoor_temp

def get_perceived_temperature(indoor_temp: float, fan_units_on: int) -> float:
    """Calculates perceived temperature considering fan cooling effect."""
    cooling_effect = min(fan_units_on * FAN_COOLING_EFFECT_C, 4.0)  # Max fan effect of 4°C
    return indoor_temp - cooling_effect

def get_comfort_status(perceived_temp: float, comfort_min: float, comfort_max: float) -> str:
    """Determines comfort status based on perceived temperature."""
    if perceived_temp < comfort_min:
        return "too_cold"
    elif perceived_temp > comfort_max + 2.0:
        return "unsafe"
    elif perceived_temp > comfort_max:
        return "too_hot"
    else:
        return "comfortable"
