<?php

namespace App\Models;

use App\Models\Scenario;
use Illuminate\Database\Eloquent\Model;

class OutputSummary extends Model
{
    protected $guarded = [];

    // Connection with Scenario
    public function scenario() {
        return $this->belongsTo(Scenario::class, 'scenario_id', 'scenario_id');
    }
}
