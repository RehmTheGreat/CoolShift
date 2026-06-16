<?php

namespace App\Filament\Resources\IntervalInputs\Schemas;

use Filament\Forms\Components\DateTimePicker;
use Filament\Forms\Components\Select;
use Filament\Forms\Components\TextInput;
use Filament\Forms\Components\Toggle;
use Filament\Schemas\Components\Grid;
use Filament\Schemas\Components\Section;
use Filament\Schemas\Schema;
// use Filament\TextInput;

class IntervalInputForm
{
    public static function configure(Schema $schema): Schema
    {
        return $schema
            ->components([
                Section::make('Timing & Scenario')
                    ->description('Select scenario and time interval')
                    ->schema([
                        Select::make('scenario_id')
                            ->relationship('scenario', 'scenario_id') // Dropdown se PUB-A, PUB-B select karega
                            ->required()
                            ->searchable(),
                        
                        DateTimePicker::make('timestamp_local')
                            ->required()
                            ->label('Local Time'),

                        TextInput::make('interval_minutes')
                            ->numeric()
                            ->default(15)
                            ->required()
                            ->label('Interval (Mins)'),
                            
                        Toggle::make('source_missing_flag')
                            ->label('Is Data Missing/Substituted?')
                            ->default(false),
                    ])->columnSpan(1),

                // Right Side: Environment & Weather Data
                Section::make('Weather Conditions')
                    ->schema([
                        Grid::make(2)->schema([
                            TextInput::make('temperature_c')
                                ->numeric()
                                ->required()
                                ->suffix('°C')
                                ->label('Temperature'),
                                
                            TextInput::make('relative_humidity_pct')
                                ->numeric()
                                ->required()
                                ->suffix('%')
                                ->label('Humidity'),
                                
                            TextInput::make('heat_index_c')
                                ->numeric()
                                ->suffix('°C')
                                ->label('Heat Index (Optional)'),
                                
                            TextInput::make('solar_irradiance_w_m2')
                                ->numeric()
                                ->required()
                                ->suffix('W/m²')
                                ->label('Solar Irradiance'),
                        ]),
                    ])->columnSpan(1),

                // Bottom Side: Grid & Tariff Data
                Section::make('Grid, Occupancy & Electricity')
                    ->schema([
                        Grid::make(3)->schema([
                            TextInput::make('occupancy_count')
                                ->numeric()
                                ->required()
                                ->label('People Present'),
                                
                            Toggle::make('grid_available')
                                ->label('Grid Power Available')
                                ->default(true)
                                ->inline(false),
                                
                            Select::make('tariff_type')
                                ->options([
                                    'PEAK' => 'Peak Hours',
                                    'OFF_PEAK' => 'Off-Peak Hours',
                                ])
                                ->required()
                                ->label('Tariff Type'),
                                
                            TextInput::make('tariff_pkr_per_kwh')
                                ->numeric()
                                ->required()
                                ->prefix('PKR')
                                ->label('Electricity Cost'),
                                
                            TextInput::make('grid_carbon_kgco2_per_kwh')
                                ->numeric()
                                ->required()
                                ->label('Grid Carbon Factor'),
                                
                            TextInput::make('non_cooling_load_kw')
                                ->numeric()
                                ->required()
                                ->suffix('kW')
                                ->label('Other Appliances Load'),
                        ]),
                    ])->columnSpanFull(),
            ])->columns(2);
            // ]);
    }
}
