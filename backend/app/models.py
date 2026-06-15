"""SQLAlchemy ORM models for CoolShift."""

from datetime import datetime
import uuid

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ===================================================================
# Scenario Profile
# ===================================================================
class ScenarioProfile(Base):
    """Top-level scenario configuration."""

    __tablename__ = "scenario_profiles"

    scenario_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Karachi")
    building_type: Mapped[str] = mapped_column(String(64), nullable=False)
    area_m2: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False)
    room_count: Mapped[int] = mapped_column(Integer, nullable=False)
    max_occupancy: Mapped[int] = mapped_column(Integer, nullable=False)
    insulation_level: Mapped[str] = mapped_column(String(32), nullable=False)  # Low/Medium/High
    sun_exposure: Mapped[str] = mapped_column(String(32), nullable=False)      # Low/Medium/High
    comfort_min_c: Mapped[float] = mapped_column(Numeric(6, 2, asdecimal=False), nullable=False)
    comfort_max_c: Mapped[float] = mapped_column(Numeric(6, 2, asdecimal=False), nullable=False)
    vulnerable_occupants: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    budget_pkr_per_day: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False)
    maximum_grid_demand_kw: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False)

    # Relationships
    appliances: Mapped[list["Appliance"]] = relationship(back_populates="scenario", cascade="all, delete-orphan")
    energy_assets: Mapped["EnergyAsset"] = relationship(back_populates="scenario", cascade="all, delete-orphan", uselist=False)
    interval_inputs: Mapped[list["IntervalInput"]] = relationship(back_populates="scenario", cascade="all, delete-orphan")
    baseline_schedules: Mapped[list["BaselineSchedule"]] = relationship(back_populates="scenario", cascade="all, delete-orphan")
    optimization_runs: Mapped[list["OptimizationRun"]] = relationship(back_populates="scenario", cascade="all, delete-orphan")


# ===================================================================
# Appliance
# ===================================================================
class Appliance(Base):
    """Cooling appliance within a scenario."""

    __tablename__ = "appliances"

    scenario_id: Mapped[str] = mapped_column(String(64), ForeignKey("scenario_profiles.scenario_id", ondelete="CASCADE"), nullable=False)
    appliance_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    zone_id: Mapped[str] = mapped_column(String(64), nullable=False)
    appliance_type: Mapped[str] = mapped_column(String(64), nullable=False)  # "Inverter AC" or "Ceiling fan"
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    rated_power_kw: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False)
    cooling_capacity_kw: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False)
    efficiency_label: Mapped[str] = mapped_column(String(64), nullable=True)
    min_runtime_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    min_setpoint_c: Mapped[float] = mapped_column(Numeric(6, 2, asdecimal=False), nullable=True)
    max_setpoint_c: Mapped[float] = mapped_column(Numeric(6, 2, asdecimal=False), nullable=True)

    # Relationships
    scenario: Mapped["ScenarioProfile"] = relationship(back_populates="appliances")


# ===================================================================
# Energy Asset
# ===================================================================
class EnergyAsset(Base):
    """Solar + battery configuration for a scenario."""

    __tablename__ = "energy_assets"

    scenario_id: Mapped[str] = mapped_column(String(64), ForeignKey("scenario_profiles.scenario_id", ondelete="CASCADE"), primary_key=True)
    solar_capacity_kw: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    solar_conversion_efficiency: Mapped[float] = mapped_column(Numeric(6, 4, asdecimal=False), nullable=False, default=0.0)
    battery_capacity_kwh: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    initial_soc_kwh: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    minimum_reserve_kwh: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    max_charge_kw: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    max_discharge_kw: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    charge_efficiency: Mapped[float] = mapped_column(Numeric(6, 4, asdecimal=False), nullable=False, default=1.0)
    discharge_efficiency: Mapped[float] = mapped_column(Numeric(6, 4, asdecimal=False), nullable=False, default=1.0)

    # Relationships
    scenario: Mapped["ScenarioProfile"] = relationship(back_populates="energy_assets")


# ===================================================================
# Interval Input
# ===================================================================
class IntervalInput(Base):
    """Time-series input data for each interval."""

    __tablename__ = "interval_inputs"
    __table_args__ = (
        Index("idx_interval_inputs_scenario_timestamp", "scenario_id", "timestamp_local"),
    )

    scenario_id: Mapped[str] = mapped_column(String(64), ForeignKey("scenario_profiles.scenario_id", ondelete="CASCADE"), primary_key=True)
    timestamp_local: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    interval_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
    temperature_c: Mapped[float] = mapped_column(Numeric(6, 2, asdecimal=False), nullable=False)
    relative_humidity_pct: Mapped[float] = mapped_column(Numeric(6, 2, asdecimal=False), nullable=False)
    heat_index_c: Mapped[float] = mapped_column(Numeric(6, 2, asdecimal=False), nullable=False)
    solar_irradiance_w_m2: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    solar_available_kw: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    occupancy_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    grid_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)  # boolean 0/1
    tariff_type: Mapped[str] = mapped_column(String(32), nullable=False)  # PEAK/OFF_PEAK
    tariff_pkr_per_kwh: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False)
    grid_carbon_kgco2_per_kwh: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.46)
    non_cooling_load_kw: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    source_missing_flag: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # int 0/1

    # Relationships
    scenario: Mapped["ScenarioProfile"] = relationship(back_populates="interval_inputs")


# ===================================================================
# Baseline Schedule
# ===================================================================
class BaselineSchedule(Base):
    """Baseline (unoptimised) cooling schedule."""

    __tablename__ = "baseline_schedule"
    __table_args__ = (
        Index("idx_baseline_schedule_scenario_timestamp", "scenario_id", "timestamp_local"),
    )

    scenario_id: Mapped[str] = mapped_column(String(64), ForeignKey("scenario_profiles.scenario_id", ondelete="CASCADE"), primary_key=True)
    timestamp_local: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    baseline_ac_units_on: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    baseline_ac_setpoint_c: Mapped[float] = mapped_column(Numeric(6, 2, asdecimal=False), nullable=True)
    baseline_fan_units_on: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    baseline_other_cooling_kw: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    baseline_rule: Mapped[str] = mapped_column(String(256), nullable=True)

    # Relationships
    scenario: Mapped["ScenarioProfile"] = relationship(back_populates="baseline_schedules")


# ===================================================================
# Optimization Run
# ===================================================================
class OptimizationRun(Base):
    """Metadata for a single optimization run."""

    __tablename__ = "optimization_runs"

    run_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    scenario_id: Mapped[str] = mapped_column(String(64), ForeignKey("scenario_profiles.scenario_id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    algorithm_version: Mapped[str] = mapped_column(String(32), nullable=False)
    runtime_seconds: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")  # pending, running, completed, failed
    parameters_json: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    scenario: Mapped["ScenarioProfile"] = relationship(back_populates="optimization_runs")
    schedule_rows: Mapped[list["OutputSchedule"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    summary: Mapped["OutputSummary"] = relationship(back_populates="run", cascade="all, delete-orphan", uselist=False)


# ===================================================================
# Output Schedule
# ===================================================================
class OutputSchedule(Base):
    """Per-interval optimisation result."""

    __tablename__ = "output_schedule"
    __table_args__ = (
        Index("idx_output_schedule_scenario_timestamp", "scenario_id", "timestamp_local"),
    )

    run_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("optimization_runs.run_id", ondelete="CASCADE"), primary_key=True)
    timestamp_local: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    scenario_id: Mapped[str] = mapped_column(String(64), ForeignKey("scenario_profiles.scenario_id", ondelete="CASCADE"), nullable=False)
    recommended_ac_units_on: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    recommended_ac_setpoint_c: Mapped[float] = mapped_column(Numeric(6, 2, asdecimal=False), nullable=True)
    recommended_fan_units_on: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    grid_energy_kwh: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    solar_energy_used_kwh: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    battery_charge_kwh: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    battery_discharge_kwh: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    battery_soc_kwh: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    cooling_energy_kwh: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    estimated_indoor_temp_c: Mapped[float] = mapped_column(Numeric(6, 2, asdecimal=False), nullable=False)
    comfort_status: Mapped[str] = mapped_column(String(64), nullable=False)
    interval_cost_pkr: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    interval_emissions_kgco2e: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    reason_code: Mapped[str] = mapped_column(String(64), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    constraint_violation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    constraint_violation_details: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    run: Mapped["OptimizationRun"] = relationship(back_populates="schedule_rows")


# ===================================================================
# Output Summary
# ===================================================================
class OutputSummary(Base):
    """Aggregated summary for an optimization run."""

    __tablename__ = "output_summary"

    run_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("optimization_runs.run_id", ondelete="CASCADE"), primary_key=True)
    scenario_id: Mapped[str] = mapped_column(String(64), ForeignKey("scenario_profiles.scenario_id", ondelete="CASCADE"), nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    baseline_energy_kwh: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    optimized_energy_kwh: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    energy_saving_kwh: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    energy_saving_pct: Mapped[float] = mapped_column(Numeric(6, 2, asdecimal=False), nullable=False, default=0.0)
    baseline_cost_pkr: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    optimized_cost_pkr: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    cost_saving_pkr: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    cost_saving_pct: Mapped[float] = mapped_column(Numeric(6, 2, asdecimal=False), nullable=False, default=0.0)
    baseline_emissions_kgco2e: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    optimized_emissions_kgco2e: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    emissions_avoided_kgco2e: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    peak_grid_demand_kw: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    peak_period_grid_energy_kwh: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    solar_available_kwh: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    solar_used_kwh: Mapped[float] = mapped_column(Numeric(12, 4, asdecimal=False), nullable=False, default=0.0)
    solar_utilization_pct: Mapped[float] = mapped_column(Numeric(6, 2, asdecimal=False), nullable=False, default=0.0)
    comfort_compliance_pct: Mapped[float] = mapped_column(Numeric(6, 2, asdecimal=False), nullable=False, default=0.0)
    unsafe_occupied_intervals: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    constraint_violations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    runtime_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    algorithm_version: Mapped[str] = mapped_column(String(32), nullable=False)

    # Relationships
    run: Mapped["OptimizationRun"] = relationship(back_populates="summary")
