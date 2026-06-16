<?php

namespace App\Filament\Resources\Scenarios\RelationManagers;

use Filament\Actions\AssociateAction;
use Filament\Actions\BulkActionGroup;
use Filament\Actions\CreateAction;
use Filament\Actions\DeleteAction;
use Filament\Actions\DeleteBulkAction;
use Filament\Actions\DissociateAction;
use Filament\Actions\DissociateBulkAction;
use Filament\Actions\EditAction;
use Filament\Forms\Components\TextInput;
use Filament\Resources\RelationManagers\RelationManager;
use Filament\Schemas\Schema;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Table;

class AppliancesRelationManager extends RelationManager
{
    protected static string $relationship = 'appliances';

    public function form(Schema $schema): Schema
    {
        return $schema
            ->components([
             TextInput::make('appliance_id')
                    ->required()
                    ->maxLength(255),
               TextInput::make('zone_id')
                    ->required()
                    ->maxLength(255),
               TextInput::make('appliance_type')
                    ->required()
                    ->maxLength(255),
               TextInput::make('quantity')
                    ->numeric()
                    ->required(),
               TextInput::make('rated_power_kw')
                    ->numeric()
                    ->required(),
               TextInput::make('cooling_capacity_kw')
                    ->numeric()
                    ->default(0),
               TextInput::make('efficiency_label')
                    ->maxLength(255),
               TextInput::make('min_runtime_minutes')
                    ->numeric()
                    ->required(),
               TextInput::make('min_setpoint_c')
                    ->numeric()
                    ->default(0),
               TextInput::make('max_setpoint_c')
                    ->numeric()
                    ->default(0),
            ]);
    }

    public function table(Table $table): Table
    {
        return $table
            ->recordTitleAttribute('appliance_type')
            ->columns([
                TextColumn::make('appliance_id')->sortable()->searchable(),
                TextColumn::make('zone_id')->sortable(),
                TextColumn::make('appliance_type'),
                TextColumn::make('quantity'),
                TextColumn::make('rated_power_kw')->label('Power (kW)'),
                TextColumn::make('cooling_capacity_kw')->label('Cooling (kW)'),
            ])
            ->filters([
                //
            ])
            ->headerActions([
                CreateAction::make()->visible(fn (RelationManager $livewire) => $livewire->getRelationship()->count() === 0),
                AssociateAction::make(),
            ])
            ->recordActions([
                EditAction::make(),
                DissociateAction::make(),
                DeleteAction::make(),
            ])
            ->toolbarActions([
                BulkActionGroup::make([
                    DissociateBulkAction::make(),
                    DeleteBulkAction::make(),
                ]),
            ]);
    }
}
