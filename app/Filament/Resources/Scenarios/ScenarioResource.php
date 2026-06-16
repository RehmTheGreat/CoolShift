<?php

namespace App\Filament\Resources\Scenarios;

use App\Filament\Resources\Scenarios\Pages\CreateScenario;
use App\Filament\Resources\Scenarios\Pages\EditScenario;
use App\Filament\Resources\Scenarios\Pages\ListScenarios;
use App\Filament\Resources\Scenarios\RelationManagers\AppliancesRelationManager;
use App\Filament\Resources\Scenarios\RelationManagers\EnergyAssetsRelationManager;
use App\Filament\Resources\Scenarios\Schemas\ScenarioForm;
use App\Filament\Resources\Scenarios\Tables\ScenariosTable;
use App\Models\Scenario;
use BackedEnum;
use Filament\Resources\Resource;
use Filament\Schemas\Schema;
use Filament\Support\Icons\Heroicon;
use Filament\Tables\Table;

class ScenarioResource extends Resource
{
    protected static ?string $model = Scenario::class;

    protected static string|BackedEnum|null $navigationIcon = Heroicon::OutlinedBuildingLibrary;

    protected static ?int $navigationSort = 1;
    protected static ?string $recordTitleAttribute = 'Scenario';

    public static function form(Schema $schema): Schema
    {
        return ScenarioForm::configure($schema);
    }

    public static function table(Table $table): Table
    {
        return ScenariosTable::configure($table);
    }

    public static function getRelations(): array
    {
        return [
            AppliancesRelationManager::class,
            EnergyAssetsRelationManager::class
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => ListScenarios::route('/'),
            'create' => CreateScenario::route('/create'),
            'edit' => EditScenario::route('/{record}/edit'),
        ];
    }
}
