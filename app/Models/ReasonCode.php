<?php

namespace App\Models;

use App\Models\OutputSchedule;
use Illuminate\Database\Eloquent\Model;

class ReasonCode extends Model
{
    protected $guarded = [];

    // Reverse connection to OutputSchedules using reason_code column
    public function outputSchedules() {
        return $this->hasMany(OutputSchedule::class, 'reason_code', 'reason_code');
    }
}
