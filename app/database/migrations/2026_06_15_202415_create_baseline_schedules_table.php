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
        Schema::create('baseline_schedules', function (Blueprint $table) {
            $table->id();
            $table->string('scenario_id'); // Foreign key
            $table->dateTime('timestamp_local');
            $table->integer('baseline_ac_units_on');
            $table->decimal('baseline_ac_setpoint_c', 5, 2)->nullable();
            $table->integer('baseline_fan_units_on');
            $table->decimal('baseline_other_cooling_kw', 8, 2)->default(0);
            $table->string('baseline_rule')->nullable();
            $table->timestamps();

            $table->foreign('scenario_id')->references('scenario_id')->on('scenarios')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('baseline_schedules');
    }
};
