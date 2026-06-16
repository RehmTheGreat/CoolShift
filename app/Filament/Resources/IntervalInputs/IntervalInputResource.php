<?php

namespace App\Filament\Resources\IntervalInputs;

use App\Filament\Resources\IntervalInputs\Pages\CreateIntervalInput;
use App\Filament\Resources\IntervalInputs\Pages\EditIntervalInput;
use App\Filament\Resources\IntervalInputs\Pages\ListIntervalInputs;
use App\Filament\Resources\IntervalInputs\Schemas\IntervalInputForm;
use App\Filament\Resources\IntervalInputs\Tables\IntervalInputsTable;
use App\Models\IntervalInput;
use BackedEnum;
use Filament\Actions\Action;
use Filament\Actions\CreateAction;
use Filament\Forms\Components\FileUpload;
use Filament\Resources\Resource;
use Filament\Schemas\Schema;
use Filament\Support\Icons\Heroicon;
use Filament\Tables\Table;
use Illuminate\Support\Facades\Notification;
use Illuminate\Support\Facades\Storage;

class IntervalInputResource extends Resource
{
    protected static ?string $model = IntervalInput::class;

    protected static string|BackedEnum|null $navigationIcon = Heroicon::ArrowDownOnSquareStack;

    protected static ?int $navigationSort = 2;

    protected static ?string $recordTitleAttribute = 'Weather & Grid Data';
    protected static ?string $navigationLabel = 'Weather & Grid Data';
protected static ?string $pluralModelLabel = 'Weather & Grid Data';
    protected static ?string $modelLabel = 'Weather & Grid Data';

    public static function form(Schema $schema): Schema
    {
        return IntervalInputForm::configure($schema);
    }

    public static function table(Table $table): Table
    {
        return IntervalInputsTable::configure($table);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => ListIntervalInputs::route('/'),
            'create' => CreateIntervalInput::route('/create'),
            'edit' => EditIntervalInput::route('/{record}/edit'),
        ];
    }

}
