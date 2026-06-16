<?php

namespace App\Filament\Resources\IntervalInputs\Pages;

use App\Filament\Resources\IntervalInputs\IntervalInputResource;
use App\Models\IntervalInput;
use Filament\Actions\Action;
use Filament\Actions\CreateAction;
use Filament\Forms\Components\FileUpload;
use Filament\Resources\Pages\ListRecords;
// use Illuminate\Notifications\Notification;
use Filament\Notifications\Notification;

use Illuminate\Support\Facades\Storage;
use Spatie\SimpleExcel\SimpleExcelReader;

class ListIntervalInputs extends ListRecords
{
    protected static string $resource = IntervalInputResource::class;

    // protected function getHeaderActions(): array
    // {
    //     return [
    //         CreateAction::make(),
    //     ];
    // }

    protected function getHeaderActions(): array
    {
        return [
            CreateAction::make(),

            // 🔥 UNIVERSAL CSV & XLSX IMPORT BUTTON
            Action::make('importDataset')
                ->label('Import Dataset (CSV/XLSX)')
                ->icon('heroicon-o-document-arrow-up')
                ->color('success')
                ->form([
                    FileUpload::make('import_file')
                        ->label('Select Interval_Inputs File')
                        ->disk('local')
                        ->directory('temp-imports')
                        ->acceptedFileTypes([
                            'text/csv',
                            'application/csv',
                            'text/plain',
                            'application/vnd.ms-excel',
                            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        ])
                        ->required(),
                ])
                ->action(function (array $data) {
                    $filePath = Storage::disk('local')->path($data['import_file']);

                    try {
                        $reader = SimpleExcelReader::create($filePath);

                        // 1. 🔥 FIX: Agar Excel (.xlsx) file hai to sahi sheet select karna
                        // Kyonke workbook mein pehli sheet README hoti hai jisme data nahi hota.
                        $extension = strtolower(pathinfo($filePath, PATHINFO_EXTENSION));
                        if (in_array($extension, ['xlsx', 'xls'])) {
                            // Yahan apni sheet ka exact naam likhein (e.g., 'Interval_Inputs')
                            $reader->fromSheetName('Interval_Inputs');
                        }

                        $insertData = [];
                        $chunkSize = 500;
                        $rowCount = 0;
                        $skippedCount = 0;

                        foreach ($reader->getRows() as $row) {
                            // 2. 🔥 FIX: Column headers ko lowercase karna taake Spaces/Case ka masla na aaye
                            $row = array_change_key_case($row, CASE_LOWER);

                            // Trim karke check karna
                            $scenarioId = isset($row['scenario_id']) ? trim($row['scenario_id']) : null;

                            if (empty($scenarioId)) {
                                $skippedCount++;
                                continue; // Agar scenario_id nahi hai to skip karein
                            }

                            // Excel mein dates kabhi DateTime object ban jati hain, unhe format karna:
                            $timestamp = $row['timestamp_local'] ?? null;
                            if ($timestamp instanceof \DateTime) {
                                $formattedDate = $timestamp->format('Y-m-d H:i:s');
                            } elseif (is_string($timestamp)) {
                                $formattedDate = date('Y-m-d H:i:s', strtotime($timestamp));
                            } else {
                                $formattedDate = null;
                            }

                            // Columns Map karna
                            $insertData[] = [
                                'scenario_id'               => $scenarioId,
                                'timestamp_local'           => $formattedDate,
                                'interval_minutes'          => (int)($row['interval_minutes'] ?? 15),
                                'temperature_c'             => (float)($row['temperature_c'] ?? 0),
                                'relative_humidity_pct'     => (float)($row['relative_humidity_pct'] ?? 0),
                                'heat_index_c'              => (float)($row['heat_index_c'] ?? 0),
                                'solar_irradiance_w_m2'     => (float)($row['solar_irradiance_w_m2'] ?? 0),
                                'solar_available_kw'        => (float)($row['solar_available_kw'] ?? 0),
                                'occupancy_count'           => (int)($row['occupancy_count'] ?? 0),
                                'grid_available'            => (int)($row['grid_available'] ?? 1),
                                'tariff_type'               => $row['tariff_type'] ?? 'OFF_PEAK',
                                'tariff_pkr_per_kwh'        => (float)($row['tariff_pkr_per_kwh'] ?? 0),
                                'grid_carbon_kgco2_per_kwh' => (float)($row['grid_carbon_kgco2_per_kwh'] ?? 0),
                                'non_cooling_load_kw'       => (float)($row['non_cooling_load_kw'] ?? 0),
                                'source_missing_flag'       => (int)($row['source_missing_flag'] ?? 0),
                                'created_at'                => now(),
                                'updated_at'                => now(),
                            ];

                            $rowCount++;

                            // Bulk insert chunking
                            if (count($insertData) >= $chunkSize) {
                                IntervalInput::insert($insertData);
                                $insertData = [];
                            }
                        }

                        // Bachi hui rows ko insert karna
                        if (count($insertData) > 0) {
                            IntervalInput::insert($insertData);
                        }

                        // Temporary file delete karna
                        Storage::disk('local')->delete($data['import_file']);

                        // 🎉 Success Notification
                        Notification::make()
                            ->title('Import Completed Successfully!')
                            ->body("Processed and imported total $rowCount rows from the file.")
                            ->success()
                            ->send();
                    } catch (\Exception $e) {
                        Notification::make()
                            ->title('Import Failed!')
                            ->body('Error processing file: ' . $e->getMessage())
                            ->danger()
                            ->send();
                    }
                }),
        ];
    }
}
