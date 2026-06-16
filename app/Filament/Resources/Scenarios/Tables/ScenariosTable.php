<?php

namespace App\Filament\Resources\Scenarios\Tables;

use Filament\Actions\BulkActionGroup;
use Filament\Actions\DeleteBulkAction;
use Filament\Actions\EditAction;
use Filament\Tables\Columns\IconColumn;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Table;

class ScenariosTable
{
    public static function configure(Table $table): Table
    {
        return $table
            ->columns([
                TextColumn::make('scenario_id')
                    ->label('ID')
                    ->badge()
                    ->color(fn (string $state): string => match ($state) {
                        'TEAM-CUSTOM' => 'warning',
                        default => 'info',
                    })
                    ->searchable()
                    ->sortable(),

                TextColumn::make('name')
                    ->searchable()
                    ->weight('bold'),

                TextColumn::make('building_type')
                    ->badge()
                    ->color('gray'),

                TextColumn::make('area_m2')
                    ->suffix(' m²')
                    ->sortable()
                    ->label('Area'),

                TextColumn::make('budget_pkr_per_day')
                    ->money('PKR')
                    ->sortable()
                    ->label('Daily Budget'),

                TextColumn::make('maximum_grid_demand_kw')
                    ->suffix(' kW')
                    ->label('Max Load'),

                IconColumn::make('vulnerable_occupants')
                    ->boolean()
                    ->label('Vulnerable')
                    ->trueIcon('heroicon-o-exclamation-triangle')
                    ->trueColor('danger'), // Agar vulnerable log hain toh red warning icon aayega
            ])
            ->filters([
                //
            ])
            ->recordActions([
                EditAction::make(),
            ])
            ->toolbarActions([
                BulkActionGroup::make([
                    DeleteBulkAction::make(),
                ]),
            ]);
    }
}
