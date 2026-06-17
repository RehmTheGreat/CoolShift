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
            Stat::make("Total Cost Savings", 4)
                ->description('32% increase')
                ->descriptionIcon('heroicon-m-arrow-trending-up')
                ->color('success'),
            Stat::make("Carbon Offset", 4),
            Stat::make("Avg. Comfort Compliance", 4),
            Stat::make("Peak Load Reduction", 4)

//             Total Cost Savings	Sum(baseline_cost - optimized_cost)
// Environmental	Carbon Offset	Sum(baseline_emissions - optimized_emissions)
// Performance	Avg. Comfort Compliance	Average(comfort_compliance_pct)
// Efficiency	Peak Load Reduction	Sum(baseline_peak_kw - optimized_peak_kw)
        ];
    }
}
