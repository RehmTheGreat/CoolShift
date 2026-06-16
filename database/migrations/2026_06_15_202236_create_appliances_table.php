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
        Schema::create('appliances', function (Blueprint $table) {
            $table->id();
            $table->string('scenario_id'); // Foreign key to scenarios
            $table->string('appliance_id');
            $table->string('zone_id');
            $table->string('appliance_type');
            $table->integer('quantity');
            $table->decimal('rated_power_kw', 8, 3);
            $table->decimal('cooling_capacity_kw', 8, 3)->default(0);
            $table->string('efficiency_label')->nullable();
            $table->integer('min_runtime_minutes');
            $table->decimal('min_setpoint_c', 5, 2)->default(0);
            $table->decimal('max_setpoint_c', 5, 2)->default(0);
            $table->timestamps();

            $table->foreign('scenario_id')->references('scenario_id')->on('scenarios')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('appliances');
    }
};
