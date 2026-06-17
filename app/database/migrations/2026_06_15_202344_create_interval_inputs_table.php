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
        Schema::create('interval_inputs', function (Blueprint $table) {
            $table->id();
            $table->string('scenario_id'); // Foreign key
            $table->dateTime('timestamp_local');
            $table->integer('interval_minutes')->default(15);
            $table->decimal('temperature_c', 5, 2);
            $table->decimal('relative_humidity_pct', 5, 2);
            $table->decimal('heat_index_c', 5, 2)->nullable();
            $table->decimal('solar_irradiance_w_m2', 8, 2);
            $table->decimal('solar_available_kw', 8, 2)->nullable();
            $table->integer('occupancy_count');
            $table->boolean('grid_available');
            $table->string('tariff_type'); // PEAK / OFF_PEAK
            $table->decimal('tariff_pkr_per_kwh', 8, 2);
            $table->decimal('grid_carbon_kgco2_per_kwh', 8, 4);
            $table->decimal('non_cooling_load_kw', 8, 2);
            $table->boolean('source_missing_flag')->default(0);
            $table->timestamps();

            $table->foreign('scenario_id')->references('scenario_id')->on('scenarios')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('interval_inputs');
    }
};
