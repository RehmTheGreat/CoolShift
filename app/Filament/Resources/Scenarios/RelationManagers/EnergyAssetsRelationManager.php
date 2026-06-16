<?php

namespace App\Filament\Resources\Scenarios\RelationManagers;

use Filament\Actions\BulkActionGroup;
use Filament\Actions\CreateAction;
use Filament\Actions\DeleteAction;
use Filament\Actions\DeleteBulkAction;
use Filament\Actions\EditAction;
use Filament\Forms\Components\TextInput;
use Filament\Resources\RelationManagers\RelationManager;
use Filament\Schemas\Schema;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Table;

class EnergyAssetsRelationManager extends RelationManager
{
    protected static string $relationship = 'energyAsset';

    public function form(Schema $schema): Schema
    {
        return $schema
            ->components([
                TextInput::make('solar_capacity_kw')
                    ->numeric()
                    ->default(0),
                TextInput::make('solar_conversion_efficiency')
                    ->numeric()
                    ->default(0),
                TextInput::make('battery_capacity_kwh')
                    ->numeric()
                    ->default(0),
                TextInput::make('initial_soc_kwh')
                    ->numeric()
                    ->default(0),
                TextInput::make('minimum_reserve_kwh')
                    ->numeric()
                    ->default(0),
                TextInput::make('max_charge_kw')
                    ->numeric()
                    ->default(0),
                TextInput::make('max_discharge_kw')
                    ->numeric()
                    ->default(0),
                TextInput::make('charge_efficiency')
                    ->numeric()
                    ->default(1),
                TextInput::make('discharge_efficiency')
                    ->numeric()
                    ->default(1),
            ]);
    }

    public function table(Table $table): Table
    {
        return $table
            ->recordTitleAttribute('id')
            ->columns([
                TextColumn::make('solar_capacity_kw')->label('Solar Cap (kW)'),
                TextColumn::make('battery_capacity_kwh')->label('Battery Cap (kWh)'),
                TextColumn::make('initial_soc_kwh')->label('Initial SOC'),
                TextColumn::make('minimum_reserve_kwh')->label('Min Reserve'),
            ])
            ->filters([
                //
            ])
            ->headerActions([
                CreateAction::make()->visible(fn (RelationManager $livewire) => $livewire->getRelationship()->count() === 0),
            ])
            ->recordActions([
                EditAction::make(),
                DeleteAction::make(),
            ])
            ->toolbarActions([
                BulkActionGroup::make([
                    DeleteBulkAction::make(),
                ]),
            ]);
    }
}
