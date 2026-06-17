<?php

namespace App\Services;

use App\Models\Appliance;
use App\Models\EnergyAsset;
use App\Models\IntervalInput;
use App\Models\OutputSchedule;
use App\Models\OutputSummary;
use App\Models\Scenario;
use Illuminate\Support\Facades\DB;

class OptimizationEngine
{
    /**
     * Create a new class instance.
     */
    public function run(string $scenarioId, string $startDate, string $endDate, string $mode)
    {
        // 1. Fetch Master Data
        $scenario = Scenario::where('scenario_id', $scenarioId)->firstOrFail();

        $inputs = IntervalInput::where('scenario_id', $scenarioId)
            ->whereBetween('timestamp_local', [$startDate, $endDate])
            ->orderBy('timestamp_local')
            ->get();

        $appliances = Appliance::where('scenario_id', $scenarioId)->get();
        $energyAssets = EnergyAsset::where('scenario_id', $scenarioId)->first();

        // 2. Pre-calculate Appliance Stats (Outside loop for maximum performance)
        $acUnits = $appliances->filter(function ($item) {
            return stripos($item->appliance_type, 'AC') !== false;
        });
        
        // FIX #1: Correct AC Power/Capacity Calculation
        $totalCoolingCapacity = $acUnits->sum(fn($ac) => $ac->cooling_capacity_kw * $ac->quantity);
        $totalAcPowerKw = $acUnits->sum(fn($ac) => $ac->rated_power_kw * $ac->quantity);
        
        $avgAcPowerKw = max(0.1, $acUnits->avg('rated_power_kw')); // Avoid division by zero
        $acCop = 3.0; // Coefficient of Performance (Efficiency)

        $fanUnits = $appliances->filter(function ($item) {
            return stripos($item->appliance_type, 'fan') !== false;
        });
        $totalFanCount = $fanUnits->sum('quantity');
        $fanPowerPerUnitKw = $fanUnits->avg('rated_power_kw') ?? 0.075;
        $totalFanPowerKw = $totalFanCount * $fanPowerPerUnitKw;

        // 3. Initialize States & Metrics
        $currentIndoorTemp = $scenario->comfort_max_c;
        // FIX #2: Independent baseline tracking
        $baselineIndoorTemp = $scenario->comfort_max_c;
        
        $batterySoc = $energyAssets ? $energyAssets->initial_soc_kwh : 0;

        // FIX #14: Run ID unique collision risk
        $runId = 'RUN_' . $scenarioId . '_' . now()->timestamp . '_' . substr(md5(uniqid()), 0, 6);
        $schedules = [];

        // Output Summary Accumulators
        $totalGridEnergy = 0;
        $totalCost = 0;
        $totalEmissions = 0;
        $peakGridDemand = 0;
        $comfortViolations = 0;
        
        // FIX #5: Track total optimized energy separately
        $totalOptimizedEnergy = 0;

        // FIX #4: Track daily cost accumulation
        $currentDate = null;
        $dailyCostAccumulator = 0;

        // Baseline Accumulators (For comparing savings)
        $baselineEnergyKwh = 0;
        $baselineCostPkr = 0;
        $baselineEmissions = 0;

        DB::beginTransaction();

        try {
            // 4. Core 15-Minute Loop
            foreach ($inputs as $index => $input) {
                $inputDate = date('Y-m-d', strtotime($input->timestamp_local));
                if ($currentDate !== $inputDate) {
                    $currentDate = $inputDate;
                    $dailyCostAccumulator = 0; // Reset daily budget
                }

                $reasonCode = 'NORMAL_OP';
                $explanation = 'Operating under normal conditions maintaining balanced comfort.';

                // --- STEP A: Baseline Simulation (For hackathon comparison) ---
                // FIX #2: Baseline independent tracking + properties
                $baselineHeatGain = (($input->temperature_c - $baselineIndoorTemp) * 0.05) 
                                    + ($input->occupancy_count * 0.02);
                $baselineIndoorTemp += $baselineHeatGain;

                $baselineGridDrawKw = $input->non_cooling_load_kw;
                if ($input->occupancy_count > 0 && $input->grid_available == 1) {
                    $baselineGridDrawKw += $totalFanPowerKw; // Fans on
                    if ($baselineIndoorTemp >= 26) {
                        $baselineGridDrawKw += $totalAcPowerKw; // All ACs on if hot
                        // Apply cooling effect to baseline temp too
                        $baselineCooling = $totalAcPowerKw * $acCop * 0.15;
                        $baselineIndoorTemp = max(24, $baselineIndoorTemp - $baselineCooling);
                    }
                }
                $bEnergy = $baselineGridDrawKw * 0.25;
                $baselineEnergyKwh += $bEnergy;
                $baselineCostPkr += ($bEnergy * $input->tariff_pkr_per_kwh);
                $baselineEmissions += ($bEnergy * $input->grid_carbon_kgco2_per_kwh);


                // --- STEP B: Target Setpoint & Mode Logic ---
                $targetTemp = $scenario->comfort_max_c ; // Default

                if ($mode === 'smart_balanced') {
                    $targetTemp = ($scenario->comfort_max_c + $scenario->comfort_min_c) / 2;
                } elseif ($mode === 'eco_savings') {
                    if ($scenario->vulnerable_occupants == 1) {
                        $targetTemp = $scenario->comfort_max_c - 1.5; // Protect vulnerables
                    } else {
                        $targetTemp = $scenario->comfort_max_c;
                    }

                    if ($input->tariff_type === 'PEAK') {
                        $targetTemp = $scenario->comfort_max_c; // Shift load during peak
                        $reasonCode = 'PEAK_TARIFF';
                        $explanation = 'AC cooling reduced to avoid expensive peak tariff rates.';
                    }
                } elseif ($mode === 'comfort_priority') {
                    $targetTemp = $scenario->comfort_min_c + 0.5;
                    $reasonCode = 'COMFORT_PRIORITY';
                    $explanation = 'Maximized cooling to prioritize optimal thermal comfort.';
                }

                if ($input->occupancy_count == 0) {
                    $targetTemp = $scenario->comfort_max_c + 2; // Let room heat up slightly if empty
                    $reasonCode = 'UNOCCUPIED';
                    $explanation = 'Reduced cooling load because the zone is currently unoccupied.';
                }

                // FIX #8: Pre-Cooling Strategy
                if ($mode !== 'comfort_priority') {
                    $nextInput = $inputs->get($index + 1);
                    if ($nextInput && $nextInput->tariff_type === 'PEAK' && $input->tariff_type !== 'PEAK') {
                        $targetTemp -= 1.5; // Pre-cool by 1.5°C
                        $reasonCode = 'PRE_COOL';
                        $explanation = 'Pre-cooling before peak tariff period to reduce peak costs.';
                    }
                }

                // --- SMART BUDGET PACING (Predictive Load Shifting) ---
                // Agar subha ke waqt hi budget tezi se khtam horaha hai, to temp limit thori barha do
                // taake dopahar ki shaded garmi ke liye budget bacha rahay.
                if ($mode !== 'comfort_priority' && $scenario->budget_pkr_per_day > 0) {
                    $hour = (int) date('H', strtotime($input->timestamp_local));
                    $budgetUsedPct = $dailyCostAccumulator / $scenario->budget_pkr_per_day;
                    
                    $pacingActive = false;
                    if ($hour < 12 && $budgetUsedPct > 0.30) { 
                        // Dopaher 12 baje se pehle 30% se zyada budget lag gaya
                        $targetTemp += 1.5; // Thora garam hone do
                        $pacingActive = true;
                    } elseif ($hour >= 12 && $hour < 15 && $budgetUsedPct > 0.60) { 
                        // 3 baje se pehle 60% se zyada lag gaya
                        $targetTemp += 1.0; 
                        $pacingActive = true;
                    }
                    
                    if ($pacingActive && $reasonCode === 'NORMAL_OP') {
                        $reasonCode = 'BUDGET_CAP';
                        $explanation = 'Smart Budget Pacing: Conserving budget in the morning to handle afternoon peak heat.';
                    }
                }

                // --- STEP C: Thermodynamic Model ---
                // FIX #6: Factor in building properties for natural Heat Gain
                $insulationFactor = match($scenario->insulation_level) {
                    'High'   => 0.03,
                    'Medium' => 0.05,
                    'Low'    => 0.08,
                    default  => 0.05,
                };
                
                $sunExposureFactor = match($scenario->sun_exposure) {
                    'High'   => 0.02,
                    'Medium' => 0.01,
                    'Low'    => 0.005,
                    default  => 0.01,
                };
                
                $solarHeatGain = ($input->solar_irradiance_w_m2 / 1000) * $sunExposureFactor * ($scenario->area_m2 / 100);
                
                $heatGain = (($input->temperature_c - $currentIndoorTemp) * $insulationFactor)
                          + ($input->occupancy_count * 0.02)
                          + $solarHeatGain;

                $projectedTemp = $currentIndoorTemp + $heatGain;

                // FIX #7: Factor in humidity
                $humidityPenalty = 0;
                if ($input->relative_humidity_pct > 60) {
                    $humidityPenalty = ($input->relative_humidity_pct - 60) * 0.015;
                }
                $projectedTemp += $humidityPenalty;

                $electricalPowerNeededKw = 0;
                $acUnitsOn = 0;
                $acSetpoint = null;

                // Do we need AC?
                if ($projectedTemp > $targetTemp && $totalCoolingCapacity > 0) {
                    $tempDiff = $projectedTemp - $targetTemp;
                    $coolingRequiredKw = min($tempDiff * 2.5, $totalCoolingCapacity);

                    $electricalPowerNeededKw = min(($coolingRequiredKw / $acCop), $totalAcPowerKw);
                    $acUnitsOn = ceil($electricalPowerNeededKw / $avgAcPowerKw);
                    $acSetpoint = round($targetTemp, 1);
                }

                // Fans logic
                $fanUnitsOn = ($input->occupancy_count > 0) ? $totalFanCount : 0;
                $activeFanPowerKw = ($fanUnitsOn > 0) ? $totalFanPowerKw : 0;

                // Total Building Load
                $totalPowerNeededKw = $electricalPowerNeededKw + $activeFanPowerKw + $input->non_cooling_load_kw;

                // --- STEP D: Energy Routing ---
                $gridDrawKw = 0;
                $solarUsedKw = 0;
                $batteryDischargeKw = 0;
                $batteryChargeKw = 0;

                $solarAvailableKw = ($input->solar_irradiance_w_m2 > 0 && $energyAssets)
                    ? ($energyAssets->solar_capacity_kw * ($input->solar_irradiance_w_m2 / 1000) * $energyAssets->solar_conversion_efficiency)
                    : 0;

                if ($input->grid_available == 0) {
                    // GRID OUTAGE
                    $reasonCode = 'GRID_OUTAGE';
                    $explanation = 'Grid offline. Operating purely on solar and battery reserves.';

                    if ($solarAvailableKw >= $totalPowerNeededKw) {
                        $solarUsedKw = $totalPowerNeededKw;
                        $excessSolar = $solarAvailableKw - $totalPowerNeededKw;
                        if ($energyAssets) {
                            $batteryChargeKw = min($excessSolar, $energyAssets->max_charge_kw) * $energyAssets->charge_efficiency;
                        }
                    } else {
                        $solarUsedKw = $solarAvailableKw;
                        $shortfall = $totalPowerNeededKw - $solarAvailableKw;

                        if ($energyAssets && $batterySoc > $energyAssets->minimum_reserve_kwh) {
                            $batteryDischargeKw = min($shortfall, $energyAssets->max_discharge_kw);
                        }

                        // Load Shedding check
                        if (($solarUsedKw + $batteryDischargeKw) < $totalPowerNeededKw) {
                            // FIX #10: Load Shedding Logic Recalculate Total Power
                            $electricalPowerNeededKw = max(0, ($solarUsedKw + $batteryDischargeKw) - $input->non_cooling_load_kw - $activeFanPowerKw);
                            $totalPowerNeededKw = $electricalPowerNeededKw + $activeFanPowerKw + $input->non_cooling_load_kw;
                            $acUnitsOn = ($electricalPowerNeededKw > 0) ? ceil($electricalPowerNeededKw / $avgAcPowerKw) : 0;
                            
                            $reasonCode = 'LOAD_SHEDDING';
                            $explanation = 'Insufficient off-grid power. Dropped AC load to prevent system blackout.';
                        }
                    }
                } else {
                    // GRID AVAILABLE
                    if ($solarAvailableKw >= $totalPowerNeededKw) {
                        $solarUsedKw = $totalPowerNeededKw;
                        $excessSolar = $solarAvailableKw - $totalPowerNeededKw;
                        // FIX #11: Set reason code regardless of battery
                        $reasonCode = 'SOLAR_AVAILABLE';
                        $explanation = 'Demand met entirely by solar energy.';
                        if ($energyAssets) {
                            $batteryChargeKw = min($excessSolar, $energyAssets->max_charge_kw) * $energyAssets->charge_efficiency;
                            $explanation .= ' Excess energy charging battery.';
                        }
                    } else {
                        $solarUsedKw = $solarAvailableKw;
                        $shortfall = $totalPowerNeededKw - $solarAvailableKw;

                        // Smart Peak Discharge
                        if ($input->tariff_type === 'PEAK' && $energyAssets && $batterySoc > $energyAssets->minimum_reserve_kwh) {
                            $batteryDischargeKw = min($shortfall, $energyAssets->max_discharge_kw);
                            $shortfall -= $batteryDischargeKw;
                        }

                        $gridDrawKw = max(0, $shortfall);
                    }
                }

                // FIX #3: Grid Demand Constraint Enforcement
                if ($gridDrawKw > $scenario->maximum_grid_demand_kw) {
                    $excessKw = $gridDrawKw - $scenario->maximum_grid_demand_kw;
                    $gridDrawKw = $scenario->maximum_grid_demand_kw;
                    
                    // Reduce AC load to compensate
                    $electricalPowerNeededKw = max(0, $electricalPowerNeededKw - $excessKw);
                    $totalPowerNeededKw = $electricalPowerNeededKw + $activeFanPowerKw + $input->non_cooling_load_kw;
                    $acUnitsOn = ($electricalPowerNeededKw > 0) ? ceil($electricalPowerNeededKw / $avgAcPowerKw) : 0;
                    
                    if ($reasonCode === 'NORMAL_OP' || $reasonCode === 'PEAK_TARIFF') {
                        $reasonCode = 'LOAD_SHEDDING'; 
                        $explanation = 'Grid draw capped at maximum allowed demand. AC load reduced.';
                    }
                }

                // FIX #9: Battery Discharge Reason Code
                if ($batteryDischargeKw > 0 && $reasonCode === 'NORMAL_OP') {
                    $reasonCode = 'BATTERY_DISCHARGE';
                    $explanation = 'Battery discharging to supplement grid/solar supply.';
                }

                // --- STEP E: Conversions & State Updates ---
                $intervalMultiplier = 0.25; // 15 mins = 0.25 hours

                if ($energyAssets) {
                    $dischargeEfficiency = $energyAssets->discharge_efficiency ?? 1; // Prevent division by zero
                    $actualBatteryDrainKwh = ($batteryDischargeKw * $intervalMultiplier) / max(0.1, $dischargeEfficiency);

                    $batterySoc += ($batteryChargeKw * $intervalMultiplier) - $actualBatteryDrainKwh;
                    $batterySoc = max(0, min($batterySoc, $energyAssets->battery_capacity_kwh));
                }

                $intervalGridEnergy = $gridDrawKw * $intervalMultiplier;
                $intervalCost = $intervalGridEnergy * $input->tariff_pkr_per_kwh;
                
                // FIX #4: Budget Constraint Enforcement
                // Only reduce AC if interval actually has a cost (running on grid) AND we are not in comfort priority mode
                if ($mode !== 'comfort_priority' && ($dailyCostAccumulator + $intervalCost) > $scenario->budget_pkr_per_day && $electricalPowerNeededKw > 0 && $intervalCost > 0) {
                    // Turn off AC completely to save budget
                    $electricalPowerNeededKw = 0;
                    $acUnitsOn = 0;
                    $acSetpoint = null;
                    
                    $reasonCode = 'BUDGET_CAP';
                    $explanation = 'Daily budget limit reached. AC cooling suspended to stay within budget.';
                    
                    // Recalculate grid draw without AC
                    $totalPowerNeededKw = $activeFanPowerKw + $input->non_cooling_load_kw;
                    $shortfall = $totalPowerNeededKw - $solarAvailableKw;
                    $gridDrawKw = max(0, $shortfall);
                    
                    // Recalculate cost
                    $intervalGridEnergy = $gridDrawKw * $intervalMultiplier;
                    $intervalCost = $intervalGridEnergy * $input->tariff_pkr_per_kwh;
                }
                $dailyCostAccumulator += $intervalCost;
                
                $intervalEmissions = $intervalGridEnergy * $input->grid_carbon_kgco2_per_kwh;

                // Dynamic Temperature Recalculation (Refined logic)
                $coolingProvidedKw = $electricalPowerNeededKw * $acCop;
                $tempDrop = $coolingProvidedKw * 0.15; // Realistic conversion factor
                $currentIndoorTemp = max($targetTemp, $projectedTemp - $tempDrop); // Won't drop below target

                // Track Comfort Violations
                $comfortStatus = 'WITHIN_RANGE';
                $constraintViolationCount = 0;
                $violationDetails = null;

                // FIX #12: Vulnerable Occupants Check
                if ($input->occupancy_count > 0 || $scenario->vulnerable_occupants == 1) {
                    if ($currentIndoorTemp > $scenario->comfort_max_c) {
                        $comfortStatus = 'UNSAFE_HOT';
                        $comfortViolations++;
                        $constraintViolationCount = 1;
                        $violationDetails = 'Exceeded maximum comfort threshold.';
                        $reasonCode = 'HEAT_RISK';
                    } elseif ($currentIndoorTemp < $scenario->comfort_min_c) {
                        $comfortStatus = 'UNSAFE_COLD';
                        $constraintViolationCount = 1;
                        $violationDetails = 'Dropped below minimum comfort threshold.';
                    }
                }

                // Global Summaries
                $totalGridEnergy += $intervalGridEnergy;
                $totalCost += $intervalCost;
                $totalEmissions += $intervalEmissions;
                if ($gridDrawKw > $peakGridDemand) {
                    $peakGridDemand = $gridDrawKw;
                }
                
                // FIX #5: Track total optimized energy separately
                $totalOptimizedEnergy += ($gridDrawKw + $solarUsedKw + $batteryDischargeKw) * $intervalMultiplier;

                // --- STEP F: Record Generation ---
                $schedules[] = [
                    'scenario_id' => $scenarioId,
                    'run_id' => $runId,
                    'timestamp_local' => $input->timestamp_local,
                    'recommended_ac_units_on' => $acUnitsOn,
                    'recommended_ac_setpoint_c' => $acSetpoint,
                    'recommended_fan_units_on' => $fanUnitsOn,
                    'grid_energy_kwh' => $intervalGridEnergy,
                    'solar_energy_used_kwh' => $solarUsedKw * $intervalMultiplier,
                    'battery_charge_kwh' => $batteryChargeKw * $intervalMultiplier,
                    'battery_discharge_kwh' => $batteryDischargeKw * $intervalMultiplier,
                    'battery_soc_kwh' => $batterySoc,
                    'cooling_energy_kwh' => $electricalPowerNeededKw * $intervalMultiplier,
                    'estimated_indoor_temp_c' => round($currentIndoorTemp, 2),
                    'comfort_status' => $comfortStatus,
                    'interval_cost_pkr' => $intervalCost,
                    'interval_emissions_kgco2e' => $intervalEmissions,
                    'reason_code' => $reasonCode,
                    'explanation' => $explanation,
                    'constraint_violation_count' => $constraintViolationCount,
                    'constraint_violation_details' => $violationDetails,
                    'created_at' => now(),
                    'updated_at' => now(),
                ];
            }

            // 5. Batch Insert into DB
            $chunks = array_chunk($schedules, 500);
            foreach ($chunks as $chunk) {
                OutputSchedule::insert($chunk);
            }

            // 6. Calculate Savings Percentages
            // Using totalGridEnergy instead of totalOptimizedEnergy so free solar/battery isn't penalized
            $energySavingKwh = $baselineEnergyKwh - $totalGridEnergy;
            $energySavingPct = $baselineEnergyKwh > 0 ? ($energySavingKwh / $baselineEnergyKwh) * 100 : 0;

            $costSavingPkr = $baselineCostPkr - $totalCost;
            $costSavingPct = $baselineCostPkr > 0 ? ($costSavingPkr / $baselineCostPkr) * 100 : 0;

            $emissionsAvoided = $baselineEmissions - $totalEmissions;

            // 7. Save Summary Output
            $summary = OutputSummary::create([
                'scenario_id' => $scenarioId,
                'run_id' => $runId,
                'period_start' => $startDate,
                'period_end' => $endDate,

                // Baseline vs Optimized Metrics
                'baseline_energy_kwh' => $baselineEnergyKwh,
                // Use totalOptimizedEnergy here for accurate reporting of overall building load
                'optimized_energy_kwh' => $totalOptimizedEnergy, 
                'energy_saving_kwh' => $energySavingKwh,
                'energy_saving_pct' => $energySavingPct,

                'baseline_cost_pkr' => $baselineCostPkr,
                'optimized_cost_pkr' => $totalCost,
                'cost_saving_pkr' => $costSavingPkr,
                'cost_saving_pct' => $costSavingPct,

                'baseline_emissions_kgco2e' => $baselineEmissions,
                'optimized_emissions_kgco2e' => $totalEmissions,
                'emissions_avoided_kgco2e' => $emissionsAvoided,

                // General Metrics
                'peak_grid_demand_kw' => $peakGridDemand,
                // FIX #13: Division by zero in compliance %
                'comfort_compliance_pct' => count($inputs) > 0 
                    ? round(100 - (($comfortViolations / count($inputs)) * 100), 2) 
                    : 100,
                'unsafe_occupied_intervals' => $comfortViolations,
                'constraint_violations' => $comfortViolations,
                'algorithm_version' => '2.0_' . $mode,
            ]);

            DB::commit();

            return [
                'status' => 'success',
                'run_id' => $runId,
                'summary' => $summary
            ];
        } catch (\Exception $e) {
            DB::rollBack();
            throw $e;
        }
    }
}
