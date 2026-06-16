<?php

namespace App\Filament\Widgets;

use Filament\Widgets\StatsOverviewWidget;
use Filament\Widgets\StatsOverviewWidget\Stat;

class StatsWidget extends StatsOverviewWidget
{
    protected function getStats(): array
    {
        return [
            //
            Stat::make("Total Senarios", 4)
                ->description('32% increase')
                ->descriptionIcon('heroicon-m-arrow-trending-up')
                ->color('success'),
            Stat::make("Total Electricity Cost Saved", 4),
            Stat::make("Total Carbon Emissions Reduced", 4),
            // Stat::make("Average Solar Utilization Rate", 4)

        ];
    }
}
