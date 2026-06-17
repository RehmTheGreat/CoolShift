<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('output_summaries', function (Blueprint $table) {
            $table->id();
            // $table->string('scenario_id');
            $table->string('scenario_id');
            // $table->foreignId('scenario_id')->constrained()->onDelete('cascade');

            $table->string('run_id');
            $table->dateTime('period_start');
            $table->dateTime('period_end');
            $table->decimal('baseline_energy_kwh', 10, 2)->nullable();
            $table->decimal('optimized_energy_kwh', 10, 2)->nullable();
            $table->decimal('energy_saving_kwh', 10, 2)->nullable();
            $table->decimal('energy_saving_pct', 5, 2)->nullable();
            $table->decimal('baseline_cost_pkr', 10, 2)->nullable();
            $table->decimal('optimized_cost_pkr', 10, 2)->nullable();
            $table->decimal('cost_saving_pkr', 10, 2)->nullable();
            $table->decimal('cost_saving_pct', 5, 2)->nullable();
            $table->decimal('baseline_emissions_kgco2e', 10, 4)->nullable();
            $table->decimal('optimized_emissions_kgco2e', 10, 4)->nullable();
            $table->decimal('emissions_avoided_kgco2e', 10, 4)->nullable();
            $table->decimal('peak_grid_demand_kw', 8, 2)->nullable();
            $table->decimal('peak_period_grid_energy_kwh', 10, 2)->nullable();
            $table->decimal('solar_available_kwh', 10, 2)->nullable();
            $table->decimal('solar_used_kwh', 10, 2)->nullable();
            $table->decimal('solar_utilization_pct', 5, 2)->nullable();
            $table->decimal('comfort_compliance_pct', 5, 2)->nullable();
            $table->integer('unsafe_occupied_intervals')->nullable();
            $table->integer('constraint_violations')->nullable();
            $table->integer('runtime_seconds')->nullable();
            $table->string('algorithm_version')->nullable();
            $table->timestamps();
            $table->foreign('scenario_id')
                ->references('scenario_id')
                ->on('scenarios')
                ->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('output_summaries');
    }
};
