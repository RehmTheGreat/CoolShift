<x-filament-panels::page>
    <x-filament::section>
        <form wire:submit="runAlgorithm">
            {{ $this->form }}

            <div class="mt-6 flex justify-end">
                <x-filament::button type="submit" wire:loading.attr="disabled">
                    <span wire:loading.remove wire:target="runAlgorithm">
                        Run Algorithm
                    </span>
                    <span wire:loading wire:target="runAlgorithm">
                        <x-filament::loading-indicator class="h-5 w-5 inline-block mr-2" />
                        Running Thermodynamic Model...
                    </span>
                </x-filament::button>
            </div>
        </form>
    </x-filament::section>

    {{-- RESULTS SECTION (Hidden until algorithm runs) --}}
    @if ($isOptimized)
        <div 
            x-data="{ show: false }" 
            x-init="setTimeout(() => show = true, 50)" 
            x-show="show" 
            x-transition:enter="transition ease-out duration-500"
            x-transition:enter-start="opacity-0 translate-y-4"
            x-transition:enter-end="opacity-100 translate-y-0"
            class="space-y-6"
        >
            {{-- KPI WIDGETS --}}
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                {{-- <x-filament::section>
                    <div class="text-sm text-gray-500">Total Cost Saved (PKR)</div>
                    <div class="text-2xl font-bold text-success-600">Rs {{ number_format($totalCostSaved, 2) }}</div>
                </x-filament::section> --}}
                @livewire(OptimizationStats::class, [
            'totalCostSaved' => $totalCostSaved,
            'totalEnergySaved' => $totalEnergySaved,
            'carbonEmissionsAvoided' => $carbonEmissionsAvoided,
            'averageComfortCompliance' => $averageComfortCompliance
        ])

            </div>

            {{-- CHARTS AREA --}}
            {{-- <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="h-96">
                    @livewire(\App\Filament\Widgets\BaselineVsOptimizedChart::class, ['scenario_id' => $data['scenario_id']])
                </div>

                <div class="h-96">
                    @livewire(\App\Filament\Widgets\TemperatureVsComfortChart::class, ['scenario_id' => $data['scenario_id']])
                </div>
            </div> --}}

            {{-- EXPLANATION TABLE (Interval Outputs) --}}
            {{-- <x-filament::section heading="Action Explanation & Schedule (15-Min)">
                @livewire(\App\Filament\Widgets\OutputScheduleTableWidget::class, ['scenario_id' => $data['scenario_id']])
            </x-filament::section> --}}
        </div>
    @endif
</x-filament-panels::page>