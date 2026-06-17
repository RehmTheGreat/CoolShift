<?php

namespace App\Filament\Pages;

use BackedEnum;
use Filament\Actions\Action;
use Filament\Forms\Components\FileUpload;
use Filament\Forms\Concerns\InteractsWithForms;
use Filament\Forms\Contracts\HasForms;
use Filament\Notifications\Notification;
use Filament\Pages\Page;
use Filament\Support\Icons\Heroicon;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Spatie\SimpleExcel\SimpleExcelReader;

class DataImportPage extends Page implements HasForms
{
    use InteractsWithForms;
    // protected string $view = 'filament.pages.data-import-page';
    protected static string|BackedEnum|null $navigationIcon = Heroicon::DocumentArrowUp;
    protected static ?string $navigationLabel = 'Data Import';
    protected static ?int $navigationSort = 5;
    protected static ?string $title = 'Import Application Data';

    // Default view ki zaroorat nahi agar hum sirf action use kar rahe hain
    protected  string $view = 'filament.pages.data-import-page';

    protected function getHeaderActions(): array
    {
        return [
            Action::make('import_data')
                ->label('Import Excel Data')
                ->icon('heroicon-o-arrow-up-tray')
                ->color('primary')
                ->form([
                    FileUpload::make('excel_file')
                        ->label('Upload Excel File (.xlsx, .csv)')
                        ->disk('local') // File temporary local storage mein aayegi
                        ->directory('imports')
                        ->acceptedFileTypes([
                            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            'text/csv'
                        ])
                        ->required(),
                ])
                ->action(function (array $data) {
                    $this->importExcelData($data['excel_file']);
                })
        ];
    }

    private function importExcelData($filePath)
    {
        // File ka absolute path get karein
        $absolutePath = Storage::disk('local')->path($filePath);

        try {
            // Database transaction start karein (Taqay agar error aaye toh half data save na ho)
            DB::beginTransaction();

            // Spatie Simple Excel Reader Initialize Karein
            // Note: Agar aapki Excel file mein multiple sheets hain, toh aap fromSheetName() use kar sakte hain

            // --- 1. IMPORT SCENARIOS ---
            // Example: $reader = SimpleExcelReader::create($absolutePath)->fromSheetName('scenarios');
            // 1. Scenarios (Sheet Name: Scenario_Profiles)
            SimpleExcelReader::create($absolutePath)
                ->fromSheetName('Scenario_Profiles')
                ->getRows()
                ->each(function (array $row) {
                    if (!isset($row['scenario_id']) || empty($row['scenario_id'])) return;

                    DB::table('scenarios')->updateOrInsert(
                        ['scenario_id' => $row['scenario_id']],
                        [
                            'name'                   => $row['name'],
                            'timezone'               => $row['timezone'] ?? null,
                            'building_type'          => $row['building_type'],
                            'area_m2'                => (int) $row['area_m2'],
                            'room_count'             => (int) $row['room_count'],
                            'max_occupancy'          => (int) $row['max_occupancy'],
                            'insulation_level'       => $row['insulation_level'],
                            'sun_exposure'           => $row['sun_exposure'],
                            'comfort_min_c'          => (float) $row['comfort_min_c'],
                            'comfort_max_c'          => (float) $row['comfort_max_c'],
                            'vulnerable_occupants'   => (bool) $row['vulnerable_occupants'],
                            'budget_pkr_per_day'     => (float) $row['budget_pkr_per_day'],
                            'maximum_grid_demand_kw' => (float) $row['maximum_grid_demand_kw'],
                            'evaluation_focus'       => $row['evaluation_focus'] ?? null,
                            'created_at'             => now(),
                            'updated_at'             => now(),
                        ]
                    );
                });

            // 2. Appliances (Sheet Name: Appliances)
            SimpleExcelReader::create($absolutePath)
                ->fromSheetName('Appliances')
                ->getRows()
                ->each(function (array $row) {
                    if (!isset($row['scenario_id']) || empty($row['scenario_id'])) return;

                    DB::table('appliances')->insert([
                        'scenario_id'         => $row['scenario_id'],
                        'appliance_id'        => $row['appliance_id'],
                        'zone_id'             => $row['zone_id'],
                        'appliance_type'      => $row['appliance_type'],
                        'quantity'            => (int) $row['quantity'],
                        'rated_power_kw'      => (float) $row['rated_power_kw'],
                        'cooling_capacity_kw' => (float) ($row['cooling_capacity_kw'] ?? 0),
                        'efficiency_label'    => $row['efficiency_label'] ?? null,
                        'min_runtime_minutes' => (int) $row['min_runtime_minutes'],
                        'min_setpoint_c'      => (float) ($row['min_setpoint_c'] ?? 0),
                        'max_setpoint_c'      => (float) ($row['max_setpoint_c'] ?? 0),
                        'created_at'          => now(),
                        'updated_at'          => now(),
                    ]);
                });

            // 3. Energy Assets (Sheet Name: Energy_Assets)
            SimpleExcelReader::create($absolutePath)
                ->fromSheetName('Energy_Assets')
                ->getRows()
                ->each(function (array $row) {
                    if (!isset($row['scenario_id']) || empty($row['scenario_id'])) return;

                    DB::table('energy_assets')->insert([
                        'scenario_id'                 => $row['scenario_id'],
                        'solar_capacity_kw'           => (float) ($row['solar_capacity_kw'] ?? 0),
                        'solar_conversion_efficiency' => (float) ($row['solar_conversion_efficiency'] ?? 0),
                        'battery_capacity_kwh'        => (float) ($row['battery_capacity_kwh'] ?? 0),
                        'initial_soc_kwh'             => (float) ($row['initial_soc_kwh'] ?? 0),
                        'minimum_reserve_kwh'         => (float) ($row['minimum_reserve_kwh'] ?? 0),
                        'max_charge_kw'               => (float) ($row['max_charge_kw'] ?? 0),
                        'max_discharge_kw'            => (float) ($row['max_discharge_kw'] ?? 0),
                        'charge_efficiency'           => (float) ($row['charge_efficiency'] ?? 1),
                        'discharge_efficiency'        => (float) ($row['discharge_efficiency'] ?? 1),
                        'created_at'                  => now(),
                        'updated_at'                  => now(),
                    ]);
                });

            // 4. Interval Inputs (Sheet Name: Interval_Inputs)
            SimpleExcelReader::create($absolutePath)
                ->fromSheetName('Interval_Inputs')
                ->getRows()
                ->each(function (array $row) {
                    if (!isset($row['scenario_id']) || empty($row['scenario_id'])) return;

                    DB::table('interval_inputs')->insert([
                        'scenario_id'               => $row['scenario_id'],
                        'timestamp_local'           => \Carbon\Carbon::parse($row['timestamp_local']),
                        'interval_minutes'          => (int) ($row['interval_minutes'] ?? 15),
                        'temperature_c'             => (float) $row['temperature_c'],
                        'relative_humidity_pct'     => (float) $row['relative_humidity_pct'],
                        'heat_index_c'              => isset($row['heat_index_c']) ? (float) $row['heat_index_c'] : null,
                        'solar_irradiance_w_m2'     => (float) $row['solar_irradiance_w_m2'],
                        'solar_available_kw'        => isset($row['solar_available_kw']) ? (float) $row['solar_available_kw'] : null,
                        'occupancy_count'           => (int) $row['occupancy_count'],
                        'grid_available'            => (bool) $row['grid_available'],
                        'tariff_type'               => $row['tariff_type'],
                        'tariff_pkr_per_kwh'        => (float) $row['tariff_pkr_per_kwh'],
                        'grid_carbon_kgco2_per_kwh' => (float) $row['grid_carbon_kgco2_per_kwh'],
                        'non_cooling_load_kw'       => (float) $row['non_cooling_load_kw'],
                        'source_missing_flag'       => (bool) ($row['source_missing_flag'] ?? 0),
                        'created_at'                => now(),
                        'updated_at'                => now(),
                    ]);
                });

            // 5. Baseline Schedules (Sheet Name: Baseline_Schedule)
            SimpleExcelReader::create($absolutePath)
                ->fromSheetName('Baseline_Schedule')
                ->getRows()
                ->each(function (array $row) {
                    if (!isset($row['scenario_id']) || empty($row['scenario_id'])) return;

                    DB::table('baseline_schedules')->insert([
                        'scenario_id'               => $row['scenario_id'],
                        'timestamp_local'           => \Carbon\Carbon::parse($row['timestamp_local']),
                        'baseline_ac_units_on'      => (int) $row['baseline_ac_units_on'],
                        'baseline_ac_setpoint_c'    => isset($row['baseline_ac_setpoint_c']) ? (float) $row['baseline_ac_setpoint_c'] : null,
                        'baseline_fan_units_on'     => (int) $row['baseline_fan_units_on'],
                        'baseline_other_cooling_kw' => (float) ($row['baseline_other_cooling_kw'] ?? 0),
                        'baseline_rule'             => $row['baseline_rule'] ?? null,
                        'created_at'                => now(),
                        'updated_at'                => now(),
                    ]);
                });

            // 6. Reason Codes (Sheet Name: Reason_Codes)
            SimpleExcelReader::create($absolutePath)
                ->fromSheetName('Reason_Codes')
                ->getRows()
                ->each(function (array $row) {
                    if (!isset($row['reason_code']) || empty($row['reason_code'])) return;

                    DB::table('reason_codes')->updateOrInsert(
                        ['reason_code' => $row['reason_code']],
                        [
                            'meaning'    => $row['meaning'],
                            'created_at' => now(),
                            'updated_at' => now(),
                        ]
                    );
                });

            // Note: Aapki excel file mein Output Tables "Templates" hain isliye unko abhi mein yahan se hatwa raha hun taqay error na aaye, 
            // Agar aap unko bhi import karna chahte hain toh 'Output_Schedule_Template' aur 'Output_Summary_Template' names use honge.
            DB::commit();

            // Import ke baad file delete kar dein (Optional)
            Storage::disk('local')->delete($filePath);

            Notification::make()
                ->title('Data Imported Successfully!')
                ->success()
                ->send();
        } catch (\Exception $e) {
            DB::rollBack();

            Notification::make()
                ->title('Import Failed!')
                ->body('Error: ' . $e->getMessage())
                ->danger()
                ->send();
        }
    }
}
