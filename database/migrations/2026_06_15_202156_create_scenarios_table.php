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
        Schema::create('scenarios', function (Blueprint $table) {
            $table->string('scenario_id')->primary(); // PK: jaise PUB-A, PUB-B
            $table->string('name');
            $table->string('timezone');
            $table->string('building_type');
            $table->integer('area_m2');
            $table->integer('room_count');
            $table->integer('max_occupancy');
            $table->string('insulation_level');
            $table->string('sun_exposure');
            $table->decimal('comfort_min_c', 5, 2);
            $table->decimal('comfort_max_c', 5, 2);
            $table->boolean('vulnerable_occupants');
            $table->decimal('budget_pkr_per_day', 10, 2);
            $table->decimal('maximum_grid_demand_kw', 8, 2);
            $table->string('evaluation_focus')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('scenarios');
    }
};
