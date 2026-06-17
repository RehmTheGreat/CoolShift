<?php

namespace Database\Seeders;

use App\Models\OutputSummary;
use App\Models\User;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        // User::factory(10)->create();

        // User::factory()->create([
        //     'name' => 'Test User',
        //     'email' => 'test@example.com',
        // ]);
        OutputSummary::create([
        'scenario_id' => 'PUB-A',
        'run_id' => 'RUN-001',
        'period_start' => '2026-05-01 00:00:00',
        'period_end' => '2026-05-01 23:45:00',
        
        // Graph ki lines in dono columns se banengi:
        'baseline_energy_kwh' => 45.2,   // Red Line ke liye value
        'optimized_energy_kwh' => 32.8,  // Green Line ke liye value
        
        'energy_saving_kwh' => 12.4,
        'energy_saving_pct' => 27.43,
        'baseline_cost_pkr' => 1900.00,
        'optimized_cost_pkr' => 1375.50,
        'cost_saving_pkr' => 524.50,
        'cost_saving_pct' => 27.61,
        'baseline_emissions_kgco2e' => 20.79,
        'optimized_emissions_kgco2e' => 15.08,
        'emissions_avoided_kgco2e' => 5.71,
        'peak_grid_demand_kw' => 3.0,
        'peak_period_grid_energy_kwh' => 2.8,
        'solar_available_kwh' => 0.0,
        'solar_used_kwh' => 0.0,
        'solar_utilization_pct' => 0.0,
        'comfort_compliance_pct' => 98.5,
        'unsafe_occupied_intervals' => 0,
        'constraint_violations' => 0,
        'runtime_seconds' => 12.5,
        'algorithm_version' => '1.0.0',
    ],
    [
        'scenario_id' => 'PUB-A',
        'run_id' => 'RUN-001',
        'period_start' => '2026-05-01 00:00:00',
        'period_end' => '2026-05-01 23:45:00',
        
        // Graph ki lines in dono columns se banengi:
        'baseline_energy_kwh' => 45.2,   // Red Line ke liye value
        'optimized_energy_kwh' => 32.8,  // Green Line ke liye value
        
        'energy_saving_kwh' => 22.4,
        'energy_saving_pct' => 237.43,
        'baseline_cost_pkr' => 2900.00,
        'optimized_cost_pkr' => 2375.50,
        'cost_saving_pkr' => 624.50,
        'cost_saving_pct' => 37.61,
        'baseline_emissions_kgco2e' => 30.79,
        'optimized_emissions_kgco2e' => 25.08,
        'emissions_avoided_kgco2e' => 15.71,
        'peak_grid_demand_kw' => 3.0,
        'peak_period_grid_energy_kwh' => 2.8,
        'solar_available_kwh' => 0.0,
        'solar_used_kwh' => 0.0,
        'solar_utilization_pct' => 0.0,
        'comfort_compliance_pct' => 99.5,
        'unsafe_occupied_intervals' => 0,
        'constraint_violations' => 0,
        'runtime_seconds' => 15.5,
        'algorithm_version' => '1.0.0',
    ]);
    }
}
