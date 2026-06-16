<?php

namespace App\Filament\Resources\Scenarios\Schemas;

use Filament\Forms\Components\Select;
use Filament\Forms\Components\Textarea;
use Filament\Forms\Components\TextInput;
use Filament\Forms\Components\Toggle;
use Filament\Schemas\Components\Grid;
use Filament\Schemas\Components\Section;
use Filament\Schemas\Schema;

class ScenarioForm
{
    public static function configure(Schema $schema): Schema
    {
        return $schema
            ->components([
                Section::make('Scenario Identity')
                    ->description('Basic information about the building or case study.')
                    ->schema([
                        Grid::make(3)->schema([
                            TextInput::make('scenario_id')
                                ->required()
                                ->unique(ignoreRecord: true)
                                ->label('Scenario ID')
                                ->placeholder('e.g. PUB-A or TEAM-CUSTOM'),
                                
                            TextInput::make('name')
                                ->required()
                                ->label('Building Name/Title'),
                                
                            Select::make('building_type')
                                ->options([
                                    'Household' => 'Household',
                                    'School' => 'School',
                                    'Office' => 'Office',
                                    'Commercial' => 'Commercial',
                                ])
                                ->required(),
                        ]),
                    ]),

                // SECTION 2: Physical Properties
                Section::make('Building Physical Properties')
                    ->schema([
                        Grid::make(4)->schema([
                            TextInput::make('area_m2')
                                ->numeric()
                                ->required()
                                ->suffix('m²')
                                ->label('Floor Area'),

                            TextInput::make('room_count')
                                ->numeric()
                                ->required()
                                ->label('Total Rooms'),

                            Select::make('insulation_level')
                                ->options([
                                    'Low' => 'Low Insulation',
                                    'Medium' => 'Medium Insulation',
                                    'High' => 'High Insulation',
                                ])
                                ->required(),

                            Select::make('sun_exposure')
                                ->options([
                                    'Low' => 'Low Exposure',
                                    'Medium' => 'Medium Exposure',
                                    'High' => 'High Exposure',
                                ])
                                ->required(),
                        ]),
                    ]),

                // SECTION 3: Comfort & Constraints (The Core Logic Params)
                Section::make('Comfort & Constraints')
                    ->description('Rules that the AI optimization algorithm must follow.')
                    ->schema([
                        Grid::make(3)->schema([
                            TextInput::make('comfort_min_c')
                                ->numeric()
                                ->required()
                                ->suffix('°C')
                                ->label('Min Comfort Temp'),

                            TextInput::make('comfort_max_c')
                                ->numeric()
                                ->required()
                                ->suffix('°C')
                                ->label('Max Comfort Temp'),

                            TextInput::make('budget_pkr_per_day')
                                ->numeric()
                                ->required()
                                ->prefix('PKR')
                                ->label('Daily Budget Limit'),

                            TextInput::make('maximum_grid_demand_kw')
                                ->numeric()
                                ->required()
                                ->suffix('kW')
                                ->label('Max Grid Demand'),

                            TextInput::make('max_occupancy')
                                ->numeric()
                                ->required()
                                ->label('Max Occupancy'),

                            Toggle::make('vulnerable_occupants')
                                ->label('Vulnerable Occupants Present?')
                                ->inline(false),
                        ]),
                    ]),

                // SECTION 4: Hackathon Specific Info
                Section::make('Evaluation Focus')
                    ->schema([
                        Textarea::make('evaluation_focus')
                            ->label('What does this scenario test?')
                            ->placeholder('e.g. Tests solar utilization, battery reserve, and comfort trade-offs.')
                            ->columnSpanFull(),
                    ])->collapsed(), // Isko by default band rakha hai taake space bache
            ]);
    }
}
