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
        Schema::create('energy_assets', function (Blueprint $table) {
            $table->id();
            $table->string('scenario_id'); // Foreign key
            $table->decimal('solar_capacity_kw', 8, 2)->default(0);
            $table->decimal('solar_conversion_efficiency', 5, 2)->default(0);
            $table->decimal('battery_capacity_kwh', 8, 2)->default(0);
            $table->decimal('initial_soc_kwh', 8, 2)->default(0);
            $table->decimal('minimum_reserve_kwh', 8, 2)->default(0);
            $table->decimal('max_charge_kw', 8, 2)->default(0);
            $table->decimal('max_discharge_kw', 8, 2)->default(0);
            $table->decimal('charge_efficiency', 5, 2)->default(1);
            $table->decimal('discharge_efficiency', 5, 2)->default(1);
            $table->timestamps();

            $table->foreign('scenario_id')->references('scenario_id')->on('scenarios')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('energy_assets');
    }
};
