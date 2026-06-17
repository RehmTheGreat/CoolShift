<?php

namespace App\Filament\Widgets;

use App\Models\OutputSummary;
use Filament\Widgets\ChartWidget;

class EnergyConsumptionChart extends ChartWidget
{
    protected ?string $heading = 'Base Line vs Optimize Energy';
    protected static ?int $sort=2;

   protected function getData(): array
    {
        // Fetch the latest record from the output_summaries table
        $data = OutputSummary::latest()->take(4)->get()->reverse();

        

        return [
           'datasets' => [
                [
                    'label' => 'Baseline Energy (kWh)',
                    'data' => $data->pluck('baseline_energy_kwh')->toArray(),
                    'backgroundColor' => '#f87171',
                ],
                [
                    'label' => 'Optimized Energy (kWh)',
                    'data' => $data->pluck('optimized_energy_kwh')->toArray(),
                    'backgroundColor' => '#34d399',
                ],
            ],
            // Use the run_id or ID as labels for the x-axis
            'labels' => $data->pluck('scenario_id')->toArray(),
        ];
    }

//     protected function getOptions(): array
// {
//     return [
//         'plugins' => [
//             'tooltip' => [
//                 'callbacks' => [
//                     'afterLabel' => 'function(context) {
//                         return "Algo: " + context.dataset.data[context.dataIndex]; // Yahan logic update ho sakti hai
//                     }'
//                 ]
//             ]
//         ],
//     ];
// }
    protected function getType(): string
    {
        return 'bar';
    }
}
