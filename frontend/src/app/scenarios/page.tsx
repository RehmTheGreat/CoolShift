"use client";

import { useEffect, useState } from "react";
import { getScenarios, getAppliances, getAssets, updateScenario } from "@/lib/api";
import { ScenarioProfile, Appliance, EnergyAsset } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Building2, Save, Sparkles, ShieldCheck, Zap } from "lucide-react";

export default function ScenariosPage() {
  const [scenarios, setScenarios] = useState<ScenarioProfile[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  
  // Details state
  const [profile, setProfile] = useState<ScenarioProfile | null>(null);
  const [appliances, setAppliances] = useState<Appliance[]>([]);
  const [asset, setAsset] = useState<EnergyAsset | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  
  useEffect(() => {
    async function loadScenarios() {
      try {
        const list = await getScenarios();
        setScenarios(list);
        if (list.length > 0) {
          setSelectedId(list[0].scenario_id);
        }
      } catch (e) {
        console.error("Failed to load scenarios:", e);
      } finally {
        setLoading(false);
      }
    }
    loadScenarios();
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    
    async function loadDetails() {
      setDetailsLoading(true);
      try {
        const p = scenarios.find((s) => s.scenario_id === selectedId);
        if (p) setProfile({ ...p });
        
        const apps = await getAppliances(selectedId!);
        setAppliances(apps);
        
        try {
          const a = await getAssets(selectedId!);
          setAsset(a);
        } catch {
          setAsset(null); // No energy asset configuration
        }
      } catch (e) {
        console.error("Failed to load scenario details:", e);
      } finally {
        setDetailsLoading(false);
      }
    }
    loadDetails();
  }, [selectedId, scenarios]);

  const handleProfileChange = (key: keyof ScenarioProfile, val: any) => {
    if (!profile) return;
    setProfile({ ...profile, [key]: val });
  };

  const handleSave = async () => {
    if (!profile || !selectedId) return;
    setSaving(true);
    try {
      const updated = await updateScenario(selectedId, profile);
      // Update local state list
      setScenarios(scenarios.map((s) => (s.scenario_id === selectedId ? updated : s)));
      alert("Building profile updated successfully.");
    } catch (e) {
      console.error(e);
      alert("Failed to save changes: " + (e instanceof Error ? e.message : String(e)));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-8 h-8 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {scenarios.length === 0 ? (
        <div className="rounded-xl border border-dashed border-white/[0.08] p-12 text-center bg-white/[0.01]">
          <Building2 className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <p className="text-base text-slate-300 font-semibold">No Building Profiles Available</p>
          <p className="text-xs text-slate-500 mt-1">Please import the public dataset to manager profiles.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Left panel list */}
          <div className="md:col-span-1 space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Scenarios</h3>
            <div className="flex flex-col gap-2">
              {scenarios.map((s) => (
                <button
                  key={s.scenario_id}
                  onClick={() => setSelectedId(s.scenario_id)}
                  className={`w-full text-left p-4 rounded-xl transition-all duration-200 border ${
                    selectedId === s.scenario_id
                      ? "bg-white/[0.04] border-cyan-400/50 shadow-md shadow-cyan-500/5 text-cyan-400"
                      : "bg-[#070b16]/20 border-white/[0.05] text-slate-400 hover:text-white hover:bg-white/[0.02]"
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <Badge variant="outline" className={`font-mono text-[9px] ${
                      selectedId === s.scenario_id ? "border-cyan-400/20 text-cyan-400" : "border-white/[0.06] text-slate-500"
                    }`}>
                      {s.scenario_id}
                    </Badge>
                    <span className="text-[10px] text-slate-500">{s.building_type}</span>
                  </div>
                  <h4 className="font-bold text-sm text-white mt-2 group-hover:text-cyan-400">{s.name}</h4>
                </button>
              ))}
            </div>
          </div>

          {/* Right panel details */}
          <div className="md:col-span-3">
            {detailsLoading || !profile ? (
              <div className="flex items-center justify-center h-80 glass-card">
                <div className="w-6 h-6 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
              </div>
            ) : (
              <div className="space-y-6">
                <Tabs defaultValue="profile" className="w-full">
                  <TabsList className="bg-white/[0.02] border border-white/[0.05] rounded-lg p-1">
                    <TabsTrigger value="profile" className="rounded-md text-xs">Building Profile</TabsTrigger>
                    <TabsTrigger value="appliances" className="rounded-md text-xs">Cooling Appliances</TabsTrigger>
                    <TabsTrigger value="assets" className="rounded-md text-xs">Energy Assets</TabsTrigger>
                  </TabsList>

                  {/* TAB 1: Profile Editing */}
                  <TabsContent value="profile" className="mt-4">
                    <Card className="glass-card border-white/[0.06]">
                      <CardHeader className="border-b border-white/[0.04]">
                        <div className="flex justify-between items-center">
                          <div>
                            <CardTitle className="text-lg font-bold text-white">Scenario Profile Configuration</CardTitle>
                            <CardDescription className="text-xs">Adjust comfort constraints and baseline parameters.</CardDescription>
                          </div>
                          <Button
                            onClick={handleSave}
                            disabled={saving}
                            className="gradient-bg text-[#0a0e1a] font-semibold text-xs py-1.5 px-3 flex items-center gap-1.5"
                          >
                            <Save className="w-4 h-4" /> {saving ? "Saving..." : "Save Config"}
                          </Button>
                        </div>
                      </CardHeader>
                      <CardContent className="pt-6 grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
                        {/* Column 1 */}
                        <div className="space-y-4">
                          <div className="space-y-1.5">
                            <Label htmlFor="name" className="text-xs text-slate-400">Profile Name</Label>
                            <Input
                              id="name"
                              value={profile.name}
                              onChange={(e) => handleProfileChange("name", e.target.value)}
                              className="bg-white/[0.02] border-white/[0.08]"
                            />
                          </div>

                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-1.5">
                              <Label htmlFor="area" className="text-xs text-slate-400">Area (m²)</Label>
                              <Input
                                id="area"
                                type="number"
                                value={profile.area_m2}
                                onChange={(e) => handleProfileChange("area_m2", parseFloat(e.target.value))}
                                className="bg-white/[0.02] border-white/[0.08]"
                              />
                            </div>
                            <div className="space-y-1.5">
                              <Label htmlFor="rooms" className="text-xs text-slate-400">Room Count</Label>
                              <Input
                                id="rooms"
                                type="number"
                                value={profile.room_count}
                                onChange={(e) => handleProfileChange("room_count", parseInt(e.target.value))}
                                className="bg-white/[0.02] border-white/[0.08]"
                              />
                            </div>
                          </div>

                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-1.5">
                              <Label htmlFor="occupancy" className="text-xs text-slate-400">Max Occupancy</Label>
                              <Input
                                id="occupancy"
                                type="number"
                                value={profile.max_occupancy}
                                onChange={(e) => handleProfileChange("max_occupancy", parseInt(e.target.value))}
                                className="bg-white/[0.02] border-white/[0.08]"
                              />
                            </div>
                            <div className="space-y-1.5">
                              <Label htmlFor="vulnerable" className="text-xs text-slate-400">Vulnerable Occupants</Label>
                              <div className="flex items-center gap-2 mt-2">
                                <input
                                  type="checkbox"
                                  id="vulnerable"
                                  checked={profile.vulnerable_occupants}
                                  onChange={(e) => handleProfileChange("vulnerable_occupants", e.target.checked)}
                                  className="w-4 h-4 rounded border-white/[0.08] bg-white/[0.02] accent-cyan-500"
                                />
                                <span className="text-xs text-slate-300">Infants, Elderly or Sick</span>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Column 2 */}
                        <div className="space-y-4">
                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-1.5">
                              <Label htmlFor="comfort-min" className="text-xs text-slate-400">Comfort Min (°C)</Label>
                              <Input
                                id="comfort-min"
                                type="number"
                                value={profile.comfort_min_c}
                                onChange={(e) => handleProfileChange("comfort_min_c", parseFloat(e.target.value))}
                                className="bg-white/[0.02] border-white/[0.08] text-cyan-400"
                              />
                            </div>
                            <div className="space-y-1.5">
                              <Label htmlFor="comfort-max" className="text-xs text-slate-400">Comfort Max (°C)</Label>
                              <Input
                                id="comfort-max"
                                type="number"
                                value={profile.comfort_max_c}
                                onChange={(e) => handleProfileChange("comfort_max_c", parseFloat(e.target.value))}
                                className="bg-white/[0.02] border-white/[0.08] text-rose-400"
                              />
                            </div>
                          </div>

                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-1.5">
                              <Label htmlFor="insulation" className="text-xs text-slate-400">Insulation Level</Label>
                              <select
                                id="insulation"
                                value={profile.insulation_level}
                                onChange={(e) => handleProfileChange("insulation_level", e.target.value)}
                                className="w-full bg-[#070b16] border border-white/[0.08] rounded-md px-3 py-2 text-slate-300 text-sm focus:border-cyan-400"
                              >
                                <option value="Low">Low Insulation</option>
                                <option value="Medium">Medium Insulation</option>
                                <option value="High">High Insulation</option>
                              </select>
                            </div>
                            <div className="space-y-1.5">
                              <Label htmlFor="exposure" className="text-xs text-slate-400">Sun Exposure</Label>
                              <select
                                id="exposure"
                                value={profile.sun_exposure}
                                onChange={(e) => handleProfileChange("sun_exposure", e.target.value)}
                                className="w-full bg-[#070b16] border border-white/[0.08] rounded-md px-3 py-2 text-slate-300 text-sm focus:border-cyan-400"
                              >
                                <option value="Low">Low Solar Gain</option>
                                <option value="Medium">Medium Solar Gain</option>
                                <option value="High">High Solar Gain</option>
                              </select>
                            </div>
                          </div>

                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-1.5">
                              <Label htmlFor="budget" className="text-xs text-slate-400">Daily Budget (PKR)</Label>
                              <Input
                                id="budget"
                                type="number"
                                value={profile.budget_pkr_per_day}
                                onChange={(e) => handleProfileChange("budget_pkr_per_day", parseFloat(e.target.value))}
                                className="bg-white/[0.02] border-white/[0.08]"
                              />
                            </div>
                            <div className="space-y-1.5">
                              <Label htmlFor="demand" className="text-xs text-slate-400">Max Grid Demand (kW)</Label>
                              <Input
                                id="demand"
                                type="number"
                                value={profile.maximum_grid_demand_kw}
                                onChange={(e) => handleProfileChange("maximum_grid_demand_kw", parseFloat(e.target.value))}
                                className="bg-white/[0.02] border-white/[0.08]"
                              />
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  {/* TAB 2: Cooling Appliances List */}
                  <TabsContent value="appliances" className="mt-4">
                    <Card className="glass-card border-white/[0.06]">
                      <CardHeader className="border-b border-white/[0.04]">
                        <CardTitle className="text-lg font-bold text-white">Cooling Appliances ({appliances.length})</CardTitle>
                        <CardDescription className="text-xs">Physical cooling devices installed at this building.</CardDescription>
                      </CardHeader>
                      <CardContent className="pt-6">
                        <div className="overflow-x-auto">
                          <table className="w-full text-left text-xs border-collapse">
                            <thead>
                              <tr className="border-b border-white/[0.06] text-slate-400 bg-white/[0.01]">
                                <th className="p-3">Appliance ID</th>
                                <th className="p-3">Zone</th>
                                <th className="p-3">Type</th>
                                <th className="p-3">Quantity</th>
                                <th className="p-3">Rated Power</th>
                                <th className="p-3">Cooling Capacity</th>
                                <th className="p-3">Efficiency</th>
                                <th className="p-3 text-right">Setpoint range</th>
                              </tr>
                            </thead>
                            <tbody>
                              {appliances.map((app) => (
                                <tr key={app.appliance_id} className="border-b border-white/[0.04] text-slate-300 hover:bg-white/[0.01]">
                                  <td className="p-3 font-mono font-semibold text-cyan-400">{app.appliance_id}</td>
                                  <td className="p-3"><Badge variant="secondary" className="bg-white/[0.03] text-slate-400">{app.zone_id}</Badge></td>
                                  <td className="p-3">{app.appliance_type}</td>
                                  <td className="p-3 font-bold">{app.quantity}</td>
                                  <td className="p-3 font-mono">{app.rated_power_kw} kW</td>
                                  <td className="p-3 font-mono">{app.cooling_capacity_kw ? `${app.cooling_capacity_kw} kW` : "—"}</td>
                                  <td className="p-3"><Badge variant="outline" className="border-cyan-500/20 text-cyan-400 bg-cyan-500/5">{app.efficiency_label || "N/A"}</Badge></td>
                                  <td className="p-3 text-right font-mono text-slate-400">
                                    {app.min_setpoint_c && app.max_setpoint_c ? `${app.min_setpoint_c} - ${app.max_setpoint_c} °C` : "—"}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  {/* TAB 3: Solar + Battery configuration */}
                  <TabsContent value="assets" className="mt-4">
                    <Card className="glass-card border-white/[0.06]">
                      <CardHeader className="border-b border-white/[0.04]">
                        <CardTitle className="text-lg font-bold text-white">Distributed Energy Assets</CardTitle>
                        <CardDescription className="text-xs">Solar photovoltaic capacity and battery storage configuration.</CardDescription>
                      </CardHeader>
                      <CardContent className="pt-6">
                        {!asset || (asset.solar_capacity_kw === 0 && asset.battery_capacity_kwh === 0) ? (
                          <div className="p-6 text-center text-slate-500">
                            <Sparkles className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                            <p className="text-sm">No Energy Assets Configured</p>
                            <p className="text-xs mt-1">This scenario runs entirely on grid energy without solar generation or battery backup.</p>
                          </div>
                        ) : (
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
                            {/* Solar configuration */}
                            {asset.solar_capacity_kw > 0 && (
                              <div className="space-y-4 p-5 rounded-xl border border-white/[0.05] bg-white/[0.01]">
                                <h4 className="font-bold text-white flex items-center gap-2 border-b border-white/[0.04] pb-2">
                                  <Sparkles className="w-4 h-4 text-cyan-400" /> Solar Photovoltaic Generation
                                </h4>
                                <div className="grid grid-cols-2 gap-4">
                                  <div>
                                    <p className="text-xs text-slate-500">PV Solar Capacity</p>
                                    <p className="text-base font-semibold text-slate-300">{asset.solar_capacity_kw} kWp</p>
                                  </div>
                                  <div>
                                    <p className="text-xs text-slate-500">Conversion Efficiency</p>
                                    <p className="text-base font-semibold text-slate-300">{(asset.solar_conversion_efficiency * 100).toFixed(0)}%</p>
                                  </div>
                                </div>
                              </div>
                            )}

                            {/* Battery configuration */}
                            {asset.battery_capacity_kwh > 0 && (
                              <div className="space-y-4 p-5 rounded-xl border border-white/[0.05] bg-white/[0.01]">
                                <h4 className="font-bold text-white flex items-center gap-2 border-b border-white/[0.04] pb-2">
                                  <Zap className="w-4 h-4 text-emerald-400" /> Battery Storage System (BESS)
                                </h4>
                                <div className="grid grid-cols-2 gap-4">
                                  <div>
                                    <p className="text-xs text-slate-500">Battery Capacity</p>
                                    <p className="text-base font-semibold text-slate-300">{asset.battery_capacity_kwh} kWh</p>
                                  </div>
                                  <div>
                                    <p className="text-xs text-slate-500">Minimum Reserve SOC</p>
                                    <p className="text-base font-semibold text-emerald-400">{asset.minimum_reserve_kwh} kWh</p>
                                  </div>
                                </div>
                                <div className="grid grid-cols-2 gap-4 border-t border-white/[0.03] pt-3">
                                  <div>
                                    <p className="text-xs text-slate-500">Max Charge / Discharge</p>
                                    <p className="text-sm font-semibold text-slate-300">{asset.max_charge_kw} kW / {asset.max_discharge_kw} kW</p>
                                  </div>
                                  <div>
                                    <p className="text-xs text-slate-500">Charge / Discharge Eff.</p>
                                    <p className="text-sm font-semibold text-slate-300">{(asset.charge_efficiency*100).toFixed(0)}% / {(asset.discharge_efficiency*100).toFixed(0)}%</p>
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </TabsContent>
                </Tabs>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
