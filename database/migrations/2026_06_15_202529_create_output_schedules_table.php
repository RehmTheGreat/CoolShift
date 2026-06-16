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
        Schema::create('output_schedules', function (Blueprint $table) {
            $table->id();
            $table->string('scenario_id');
            $table->string('run_id'); // optimization run ko track karne ke liye
            $table->dateTime('timestamp_local');
            $table->integer('recommended_ac_units_on')->nullable();
            $table->decimal('recommended_ac_setpoint_c', 5, 2)->nullable();
            $table->integer('recommended_fan_units_on')->nullable();
            $table->decimal('grid_energy_kwh', 8, 4)->nullable();
            $table->decimal('solar_energy_used_kwh', 8, 4)->nullable();
            $table->decimal('battery_charge_kwh', 8, 4)->nullable();
            $table->decimal('battery_discharge_kwh', 8, 4)->nullable();
            $table->decimal('battery_soc_kwh', 8, 4)->nullable();
            $table->decimal('cooling_energy_kwh', 8, 4)->nullable();
            $table->decimal('estimated_indoor_temp_c', 5, 2)->nullable();
            $table->string('comfort_status')->nullable();
            $table->decimal('interval_cost_pkr', 8, 2)->nullable();
            $table->decimal('interval_emissions_kgco2e', 8, 4)->nullable();
            $table->string('reason_code')->nullable(); // Foreign key to reason_codes
            $table->text('explanation')->nullable();
            $table->integer('constraint_violation_count')->default(0);
            $table->text('constraint_violation_details')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('output_schedules');
    }
};
