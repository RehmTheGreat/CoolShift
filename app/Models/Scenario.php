<?php

namespace App\Models;

use App\Models\Appliance;
use App\Models\BaselineSchedule;
use App\Models\EnergyAsset;
use App\Models\IntervalInput;
use App\Models\OutputSchedule;
use App\Models\OutputSummary;
use Illuminate\Database\Eloquent\Model;

class Scenario extends Model
{
    protected $guarded = [];
    
    // Custom Primary Key
    protected $primaryKey = 'scenario_id';
    public $incrementing = false;
    protected $keyType = 'string';

    // Connections (Relationships)
    public function appliances() {
        return $this->hasMany(Appliance::class, 'scenario_id', 'scenario_id');
    }

    public function energyAsset() {
        return $this->hasOne(EnergyAsset::class, 'scenario_id', 'scenario_id');
    }

    public function intervalInputs() {
        return $this->hasMany(IntervalInput::class, 'scenario_id', 'scenario_id');
    }

    public function baselineSchedules() {
        return $this->hasMany(BaselineSchedule::class, 'scenario_id', 'scenario_id');
    }

    public function outputSchedules() {
        return $this->hasMany(OutputSchedule::class, 'scenario_id', 'scenario_id');
    }

    public function outputSummaries() {
        return $this->hasMany(OutputSummary::class, 'scenario_id', 'scenario_id');
    }
}
