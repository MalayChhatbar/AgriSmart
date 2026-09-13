import React, { useState } from 'react';
import {
  MapPin,
  Navigation,
  Thermometer,
  Droplets,
  CloudRain,
  Clock,
  Layers,
  Sparkles,
  ChevronDown,
  ChevronUp,
  RefreshCw,
} from 'lucide-react';
import { EnvironmentalContext } from '../types';

interface EnvironmentCardProps {
  env: EnvironmentalContext;
  onUpdateEnv: (updated: Partial<EnvironmentalContext>) => void;
}

export const EnvironmentCard: React.FC<EnvironmentCardProps> = ({ env, onUpdateEnv }) => {
  const [isLocating, setIsLocating] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [locationText, setLocationText] = useState(env.location);

  const handleAutoLocate = () => {
    setIsLocating(true);
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setIsLocating(false);
          const detectedLoc = `Field GPS (${pos.coords.latitude.toFixed(2)}°N, ${pos.coords.longitude.toFixed(2)}°E)`;
          setLocationText(detectedLoc);
          onUpdateEnv({
            location: detectedLoc,
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
            temperature: 29.2,
            humidity: 76,
            rainfallProbability: 30,
          });
        },
        () => {
          setIsLocating(false);
          const fallbackLoc = 'Nashik Agri Hub, Maharashtra';
          setLocationText(fallbackLoc);
          onUpdateEnv({ location: fallbackLoc });
        },
        { timeout: 5000 }
      );
    } else {
      setIsLocating(false);
    }
  };

  const soilOptions: EnvironmentalContext['soilType'][] = [
    'Loamy',
    'Black Cotton',
    'Red Laterite',
    'Clayey',
    'Sandy',
    'Alluvial',
  ];

  const stageOptions: EnvironmentalContext['cropStage'][] = [
    'Seedling',
    'Vegetative',
    'Flowering',
    'Fruiting',
    'Harvest',
  ];

  const irrigationOptions: EnvironmentalContext['irrigationType'][] = [
    'Drip',
    'Sprinkler',
    'Furrow',
    'Rainfed',
  ];

  return (
    <div className="bg-card rounded-2xl border border-border p-4 shadow-sm transition-colors">
      {/* Header & Location */}
      <div className="flex items-center justify-between pb-3 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-primary/15 text-primary">
            <MapPin className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Farm Environmental Context
            </h3>
            <div className="flex items-center gap-1 mt-0.5">
              <input
                type="text"
                value={locationText}
                onChange={(e) => {
                  setLocationText(e.target.value);
                  onUpdateEnv({ location: e.target.value });
                }}
                className="text-sm font-semibold text-foreground bg-transparent border-none p-0 focus:outline-none focus:ring-0 w-48 truncate"
                placeholder="Enter village or district..."
              />
            </div>
          </div>
        </div>

        <button
          onClick={handleAutoLocate}
          disabled={isLocating}
          className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-secondary text-secondary-foreground text-xs font-bold border border-border hover:border-primary/40 active:scale-95 transition-all cursor-pointer shadow-xs disabled:opacity-50"
          title="Auto-Detect GPS Location"
        >
          {isLocating ? (
            <RefreshCw className="w-3.5 h-3.5 animate-spin text-primary" />
          ) : (
            <Navigation className="w-3.5 h-3.5 text-primary" />
          )}
          <span>{isLocating ? 'Locating...' : 'GPS Auto'}</span>
        </button>
      </div>

      {/* Auto-detected Weather Grid */}
      <div className="grid grid-cols-4 gap-2 my-3">
        {/* Temperature */}
        <div className="bg-secondary/70 rounded-xl p-2.5 border border-border/60 text-center">
          <div className="flex items-center justify-center text-amber-500 mb-1">
            <Thermometer className="w-4 h-4" />
          </div>
          <span className="block text-[10px] text-muted-foreground font-medium">Temp</span>
          <span className="text-sm font-bold text-foreground">{env.temperature}°C</span>
        </div>

        {/* Humidity */}
        <div className="bg-secondary/70 rounded-xl p-2.5 border border-border/60 text-center">
          <div className="flex items-center justify-center text-blue-500 mb-1">
            <Droplets className="w-4 h-4" />
          </div>
          <span className="block text-[10px] text-muted-foreground font-medium">Humidity</span>
          <span className="text-sm font-bold text-foreground">{env.humidity}%</span>
        </div>

        {/* Rain Probability */}
        <div className="bg-secondary/70 rounded-xl p-2.5 border border-border/60 text-center">
          <div className="flex items-center justify-center text-indigo-500 mb-1">
            <CloudRain className="w-4 h-4" />
          </div>
          <span className="block text-[10px] text-muted-foreground font-medium">Rain 24h</span>
          <span className="text-sm font-bold text-foreground">{env.rainfallProbability}%</span>
        </div>

        {/* Leaf Wetness Duration */}
        <div className="bg-secondary/70 rounded-xl p-2.5 border border-border/60 text-center">
          <div className="flex items-center justify-center text-emerald-500 mb-1">
            <Clock className="w-4 h-4" />
          </div>
          <span className="block text-[10px] text-muted-foreground font-medium">Leaf Wet</span>
          <span className="text-sm font-bold text-foreground">{env.leafWetnessHours}h</span>
        </div>
      </div>

      {/* Primary Farmer Inputs (Soil & Crop Stage) */}
      <div className="space-y-2.5 pt-1">
        <div className="grid grid-cols-2 gap-2.5">
          {/* Soil Type Select */}
          <div>
            <label className="block text-[11px] font-bold text-muted-foreground uppercase tracking-wider mb-1 flex items-center gap-1">
              <Layers className="w-3 h-3 text-primary" />
              Soil Type
            </label>
            <select
              value={env.soilType}
              onChange={(e) => onUpdateEnv({ soilType: e.target.value as EnvironmentalContext['soilType'] })}
              className="w-full bg-input/70 border border-border text-foreground text-xs font-semibold rounded-xl px-2.5 py-2 focus:ring-1 focus:ring-primary focus:outline-none cursor-pointer"
            >
              {soilOptions.map((soil) => (
                <option key={soil} value={soil}>
                  {soil} Soil
                </option>
              ))}
            </select>
          </div>

          {/* Growth Stage Select */}
          <div>
            <label className="block text-[11px] font-bold text-muted-foreground uppercase tracking-wider mb-1 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-primary" />
              Growth Stage
            </label>
            <select
              value={env.cropStage}
              onChange={(e) => onUpdateEnv({ cropStage: e.target.value as EnvironmentalContext['cropStage'] })}
              className="w-full bg-input/70 border border-border text-foreground text-xs font-semibold rounded-xl px-2.5 py-2 focus:ring-1 focus:ring-primary focus:outline-none cursor-pointer"
            >
              {stageOptions.map((stg) => (
                <option key={stg} value={stg}>
                  {stg} Stage
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Collapsible Irrigation & Advanced Settings */}
        {showAdvanced && (
          <div className="pt-2 border-t border-border/60 animate-fadeIn">
            <label className="block text-[11px] font-bold text-muted-foreground uppercase tracking-wider mb-1">
              Irrigation Delivery Mode
            </label>
            <div className="grid grid-cols-4 gap-1.5">
              {irrigationOptions.map((mode) => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => onUpdateEnv({ irrigationType: mode })}
                  className={`py-1.5 px-2 rounded-lg text-xs font-semibold border transition-all cursor-pointer ${
                    env.irrigationType === mode
                      ? 'bg-primary text-primary-foreground border-primary shadow-xs'
                      : 'bg-secondary text-secondary-foreground border-border hover:border-primary/40'
                  }`}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Toggle Advanced */}
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="w-full flex items-center justify-center gap-1 pt-1 text-xs font-semibold text-muted-foreground hover:text-primary transition-colors cursor-pointer"
        >
          <span>{showAdvanced ? 'Hide Irrigation Options' : 'Customize Irrigation & Parameters'}</span>
          {showAdvanced ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>
    </div>
  );
};
