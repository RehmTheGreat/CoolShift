<?php

namespace App\Filament\Resources\IntervalInputs\Tables;

use App\Models\Scenario;
use Filament\Actions\BulkActionGroup;
use Filament\Actions\DeleteBulkAction;
use Filament\Actions\EditAction;
// use Filament\Forms\Components\Builder;
use Filament\Forms\Components\DatePicker;
use Filament\Tables\Columns\IconColumn;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Filters\Filter;
use Filament\Tables\Filters\SelectFilter;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;

class IntervalInputsTable
{
    public static function configure(Table $table): Table
    {
        return $table
            ->columns([
                TextColumn::make('scenario_id')
                    ->label('Scenario')
                    ->sortable()
                    ->searchable()
                    ->badge()
                    ->color('info'), // PUB-A, PUB-B ko blue badge mein dikhayega
                    
                TextColumn::make('timestamp_local')
                    ->dateTime('d M Y, h:i A') // Beautiful Date format
                    ->sortable()
                    ->label('Time'),

                TextColumn::make('temperature_c')
                    ->numeric()
                    ->sortable()
                    ->suffix(' °C')
                    ->label('Temp'),

                TextColumn::make('relative_humidity_pct')
                    ->numeric()
                    ->suffix(' %')
                    ->label('Humidity')
                    ->toggleable(isToggledHiddenByDefault: true), // By default hide, user can toggle

                IconColumn::make('grid_available')
                    ->boolean()
                    ->label('Grid')
                    ->trueIcon('heroicon-o-bolt')
                    ->falseIcon('heroicon-o-bolt-slash'),

                TextColumn::make('tariff_type')
                    ->badge()
                    ->color(fn (string $state): string => match ($state) {
                        'PEAK' => 'danger',     // Peak red color mein
                        'OFF_PEAK' => 'success', // Off-peak green color mein
                    })
                    ->label('Tariff'),

                TextColumn::make('tariff_pkr_per_kwh')
                    ->money('PKR')
                    ->sortable()
                    ->label('Price/kWh'),

                TextColumn::make('occupancy_count')
                    ->numeric()
                    ->sortable()
                    ->label('Occupants'),
            ])
            ->filters([
                SelectFilter::make('scenario_id')
                    ->label('Filter by Scenario')
                    ->options(fn () => Scenario::pluck('scenario_id', 'scenario_id')->toArray()) // Scenario table se exact list uthayega
                    ->searchable(), // Dropdown ke andar search bar query enable karega

                // 2. 🔥 DATE RANGE FILTER (From Date and Until Date)
                Filter::make('timestamp_local')
                    ->form([
                        DatePicker::make('from')
                            ->label('From Date'),
                        DatePicker::make('until')
                            ->label('Until Date'),
                    ])
                    ->query(function (Builder $query, array $data): Builder {
                        return $query
                            ->when(
                                $data['from'],
                                fn (Builder $query, $date): Builder => $query->whereDate('timestamp_local', '>=', $date),
                            )
                            ->when(
                                $data['until'],
                                fn (Builder $query, $date): Builder => $query->whereDate('timestamp_local', '<=', $date),
                            );
                    })
                    ->indicateUsing(function (array $data): array {
                        $indicators = [];
                        if ($data['from'] ?? null) {
                            $indicators[] = 'From: ' . \Carbon\Carbon::parse($data['from'])->toFormattedDateString();
                        }
                        if ($data['until'] ?? null) {
                            $indicators[] = 'Until: ' . \Carbon\Carbon::parse($data['until'])->toFormattedDateString();
                        }
                        return $indicators;
                    }),
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
