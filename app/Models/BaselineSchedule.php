<?php

namespace App\Models;

use App\Models\Scenario;
use Illuminate\Database\Eloquent\Model;

class BaselineSchedule extends Model
{
    protected $guarded = [];

    public function scenario() {
        return $this->belongsTo(Scenario::class, 'scenario_id', 'scenario_id');
    }
}
