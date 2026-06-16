<?php

namespace App\Models;

use App\Models\ReasonCode;
use App\Models\Scenario;
use Illuminate\Database\Eloquent\Model;

class OutputSchedule extends Model
{
    protected $guarded = [];

    // Connection with Scenario
    public function scenario() {
        return $this->belongsTo(Scenario::class, 'scenario_id', 'scenario_id');
    }

    // Connection with ReasonCode using custom column
    public function reason() {
        return $this->belongsTo(ReasonCode::class, 'reason_code', 'reason_code');
    }
}
