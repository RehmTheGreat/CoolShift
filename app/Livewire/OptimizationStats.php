<?php

namespace App\Livewire;

use Filament\Widgets\StatsOverviewWidget;
use Filament\Widgets\StatsOverviewWidget\Stat;

class OptimizationStats extends StatsOverviewWidget
{
  
        // 1. Parent Blade file se data receive karne k liye variables define karein
    public $totalCostSaved = 0;
    public $totalEnergySaved = 0;
    public $carbonEmissionsAvoided = 0;
    public $averageComfortCompliance = 0;

    public static function canView(): bool
    {
        // Yahan aap check karein ke kya result aa chuka hai
        // Aap session ya koi state check kar sakte hain
        return request()->has('isOptimized') || session()->has('show_results');
    }
    protected function getStats(): array
    {
        return [
            // Cost Saved Card
            Stat::make('Total Cost Saved (PKR)', 'Rs ' . number_format($this->totalCostSaved, 2))
                ->description('Smart savings generated')
                ->descriptionIcon('heroicon-m-arrow-trending-down')
                ->color('success'),

            // Energy Saved Card
            Stat::make('Total Energy Saved', number_format($this->totalEnergySaved, 2) . ' kWh')
                ->description('Power consumption cut')
                ->descriptionIcon('heroicon-m-bolt')
                ->color('warning'),

            // Carbon Emissions Card
            Stat::make('Carbon Emissions Avoided', number_format($this->carbonEmissionsAvoided, 2) . ' kgCO2e')
                ->description('Environmental impact')
                ->descriptionIcon('heroicon-m-globe-americas')
                ->color('success'),

            // Comfort Compliance Card
            Stat::make('Average Comfort Compliance', number_format($this->averageComfortCompliance, 1) . '%')
                ->description('Indoor climate stability')
                ->descriptionIcon('heroicon-m-academic-cap') // Aap apni pasand ka icon laga sakte hain
                ->color('info'),
        ];
    }
}
