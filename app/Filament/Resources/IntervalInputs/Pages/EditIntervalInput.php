<?php

namespace App\Filament\Resources\IntervalInputs\Pages;

use App\Filament\Resources\IntervalInputs\IntervalInputResource;
use Filament\Actions\DeleteAction;
use Filament\Resources\Pages\EditRecord;

class EditIntervalInput extends EditRecord
{
    protected static string $resource = IntervalInputResource::class;

    protected function getHeaderActions(): array
    {
        return [
            DeleteAction::make(),
        ];
    }
}
