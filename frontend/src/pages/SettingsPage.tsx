import React, { useState } from 'react';
import { AppSettings } from '../types';
import {
  Settings,
  Key,
  Server,
  User,
  MapPin,
  Layers,
  Globe,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Save,
  Trash2,
  HelpCircle,
  ExternalLink,
  ArrowLeft,
  Sun,
  Moon,
} from 'lucide-react';
import { checkBackendConnection } from '../services/api';

interface SettingsPageProps {
  settings: AppSettings;
  onSaveSettings: (updated: AppSettings) => void;
  onClearHistory: () => void;
  onBack: () => void;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({
  settings,
  onSaveSettings,
  onClearHistory,
  onBack,
}) => {
  const [formData, setFormData] = useState<AppSettings>(settings);
  const [testStatus, setTestStatus] = useState<{
    tested: boolean;
    online: boolean;
    latencyMs: number;
    loading: boolean;
  }>({
    tested: false,
    online: false,
    latencyMs: 0,
    loading: false,
  });
  const [showSavedNotification, setShowSavedNotification] = useState(false);

  const handleTestBackend = async () => {
    setTestStatus((prev) => ({ ...prev, loading: true, tested: false }));
    const res = await checkBackendConnection(formData.backendUrl);
    setTestStatus({
      tested: true,
      online: res.online,
      latencyMs: res.latencyMs,
      loading: false,
    });
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    onSaveSettings(formData);
    try {
      await fetch(`${formData.backendUrl}/api/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nvidia_api_key: formData.nvidiaApiKey || '',
          deepseek_api_key: formData.openaiApiKey || '',
          gemini_api_key: formData.geminiApiKey || '',
          openweather_api_key: formData.weatherApiKey || '',
          ai_model: formData.aiModel || 'deepseek-ai/deepseek-v3',
          farmer_name: formData.farmerName,
          farm_location: formData.farmLocation,
          primary_crop: formData.primaryCrop,
          soil_type: formData.defaultSoil,
          language: formData.language,
          dark_mode: formData.darkMode,
        }),
      });
    } catch (err) {
      console.warn('Could not sync settings to backend SQLite:', err);
    }
    setShowSavedNotification(true);
    setTimeout(() => setShowSavedNotification(false), 3000);
    alert("Settings saved successfully!");
  };

  return (
    <div className="space-y-3.5 pb-24 animate-fadeIn">
      {/* Sleek Top Back Navigation Bar */}
      <div className="flex items-center justify-between pt-1 pb-1">
        <button
          onClick={onBack}
          className="flex items-center gap-2 py-2 px-3.5 rounded-xl bg-card hover:bg-secondary/70 border border-border text-xs font-bold text-foreground active:scale-95 transition-all cursor-pointer shadow-xs group"
          title="Back to Living World"
        >
          <ArrowLeft className="w-4 h-4 text-primary group-hover:-translate-x-0.5 transition-transform" />
          <span>Back to Living World</span>
        </button>
        <span className="text-[11px] font-black uppercase tracking-wider text-muted-foreground">
          Settings
        </span>
      </div>

      {/* Header */}
      <div className="bg-card rounded-2xl border border-border p-4 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-primary/20 flex items-center justify-center text-primary">
            <Settings className="w-4 h-4" />
          </div>
          <div>
            <h2 className="font-bold text-base text-foreground">Application Settings</h2>
            <p className="text-xs text-muted-foreground">API keys, server endpoints & farm profile</p>
          </div>
        </div>

        {showSavedNotification && (
          <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-primary text-primary-foreground flex items-center gap-1 shadow-xs animate-fadeIn">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Saved!
          </span>
        )}
      </div>

      <form onSubmit={handleSave} className="space-y-4">
        {/* 1. API Keys Section */}
        <div className="bg-card rounded-2xl border border-border p-4 shadow-sm space-y-3">
          <div className="flex items-center gap-2 pb-2 border-b border-border">
            <Key className="w-4 h-4 text-primary" />
            <h3 className="font-bold text-xs uppercase tracking-wider text-foreground">
              External AI & Weather API Keys
            </h3>
          </div>

          <div className="space-y-3">
            {/* NVIDIA NIM / DeepSeek API Key */}
            <div className="p-3 rounded-xl bg-primary/5 border border-primary/20 space-y-2">
              <label className="block text-xs font-semibold text-foreground flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-primary font-bold">
                  <span>NVIDIA NIM / DeepSeek API Key</span>
                </span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-primary/20 text-primary font-bold">Recommended</span>
              </label>
              <input
                type="password"
                value={formData.nvidiaApiKey || ''}
                onChange={(e) => setFormData({ ...formData, nvidiaApiKey: e.target.value })}
                placeholder="nvapi-... or sk-..."
                className="w-full bg-input/90 border border-primary/30 rounded-xl px-3 py-2 text-xs text-foreground placeholder:text-muted-foreground font-mono focus:ring-1 focus:ring-primary focus:outline-none"
              />
              <div className="flex items-center justify-between gap-2 pt-1">
                <label className="text-[11px] font-medium text-foreground">AI Model:</label>
                <select
                  value={formData.aiModel || 'deepseek-ai/deepseek-v3'}
                  onChange={(e) => setFormData({ ...formData, aiModel: e.target.value })}
                  className="bg-input border border-border rounded-lg px-2 py-1 text-xs text-foreground focus:ring-1 focus:ring-primary focus:outline-none"
                >
                  <option value="deepseek-ai/deepseek-v3">DeepSeek V3 (NVIDIA NIM)</option>
                  <option value="deepseek-ai/deepseek-r1">DeepSeek R1 (NVIDIA NIM)</option>
                  <option value="gpt-4o-mini">GPT-4o Mini (OpenAI)</option>
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo (OpenAI)</option>
                  <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                  <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                  <option value="moonshotai/kimi-k1.5">Kimi K1.5 (Moonshot)</option>
                  <option value="meta/llama-3.3-70b-instruct">Llama 3.3 70B Instruct</option>
                </select>
              </div>
              <p className="text-[10px] text-muted-foreground">
                Powers real-time dynamic remedies, biological causes, and tool-calling Kisan AI.
              </p>
            </div>

            {/* Gemini API Key */}
            <div>
              <label className="block text-xs font-semibold text-foreground mb-1 flex items-center justify-between">
                <span>Google Gemini API Key</span>
                <span className="text-[10px] text-muted-foreground font-normal">Optional</span>
              </label>
              <input
                type="password"
                value={formData.geminiApiKey}
                onChange={(e) => setFormData({ ...formData, geminiApiKey: e.target.value })}
                placeholder="AIzaSy..."
                className="w-full bg-input/70 border border-border rounded-xl px-3 py-2 text-xs text-foreground placeholder:text-muted-foreground font-mono focus:ring-1 focus:ring-primary focus:outline-none"
              />
              <p className="text-[10px] text-muted-foreground mt-1">
                Used for enhanced regional conversational advice and grounded Q&A.
              </p>
            </div>

            {/* OpenAI API Key */}
            <div>
              <label className="block text-xs font-semibold text-foreground mb-1 flex items-center justify-between">
                <span>OpenAI API Key</span>
                <span className="text-[10px] text-muted-foreground font-normal">Optional</span>
              </label>
              <input
                type="password"
                value={formData.openaiApiKey}
                onChange={(e) => setFormData({ ...formData, openaiApiKey: e.target.value })}
                placeholder="sk-..."
                className="w-full bg-input/70 border border-border rounded-xl px-3 py-2 text-xs text-foreground placeholder:text-muted-foreground font-mono focus:ring-1 focus:ring-primary focus:outline-none"
              />
            </div>

            {/* OpenWeatherMap Key */}
            <div>
              <label className="block text-xs font-semibold text-foreground mb-1 flex items-center justify-between">
                <span>OpenWeatherMap Key</span>
                <span className="text-[10px] text-muted-foreground font-normal">Optional</span>
              </label>
              <input
                type="password"
                value={formData.weatherApiKey}
                onChange={(e) => setFormData({ ...formData, weatherApiKey: e.target.value })}
                placeholder="32-character API key"
                className="w-full bg-input/70 border border-border rounded-xl px-3 py-2 text-xs text-foreground placeholder:text-muted-foreground font-mono focus:ring-1 focus:ring-primary focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* 2. Backend Server Endpoint */}
        <div className="bg-card rounded-2xl border border-border p-4 shadow-sm space-y-3">
          <div className="flex items-center gap-2 pb-2 border-b border-border">
            <Server className="w-4 h-4 text-primary" />
            <h3 className="font-bold text-xs uppercase tracking-wider text-foreground">
              AgriSmart AI Model Server
            </h3>
          </div>

          <div>
            <label className="block text-xs font-semibold text-foreground mb-1">
              FastAPI Inference URL
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={formData.backendUrl}
                onChange={(e) => setFormData({ ...formData, backendUrl: e.target.value })}
                placeholder="http://127.0.0.1:8000"
                className="flex-1 bg-input/70 border border-border rounded-xl px-3 py-2 text-xs text-foreground font-mono focus:ring-1 focus:ring-primary focus:outline-none"
              />
              <button
                type="button"
                onClick={handleTestBackend}
                disabled={testStatus.loading}
                className="px-3.5 py-2 rounded-xl bg-secondary text-secondary-foreground border border-border hover:border-primary/50 text-xs font-bold transition-all active:scale-95 cursor-pointer flex items-center gap-1.5 shadow-xs"
              >
                {testStatus.loading ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-primary" />
                ) : (
                  <span>Test</span>
                )}
              </button>
            </div>

            {testStatus.tested && (
              <div
                className={`mt-2 p-2 rounded-xl text-xs flex items-center gap-2 border ${
                  testStatus.online
                    ? 'bg-emerald-950/20 text-emerald-600 dark:text-emerald-400 border-emerald-500/30'
                    : 'bg-rose-950/20 text-rose-600 dark:text-rose-400 border-rose-500/30'
                }`}
              >
                {testStatus.online ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 shrink-0" />
                    <span>
                      Server Connected! Latency: <strong>{testStatus.latencyMs} ms</strong>
                    </span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>
                      Server unreachable at {formData.backendUrl}. The client will use high-fidelity offline mode.
                    </span>
                  </>
                )}
              </div>
            )}
          </div>
        </div>

        {/* 3. Farmer & Farm Profile */}
        <div className="bg-card rounded-2xl border border-border p-4 shadow-sm space-y-3">
          <div className="flex items-center gap-2 pb-2 border-b border-border">
            <User className="w-4 h-4 text-primary" />
            <h3 className="font-bold text-xs uppercase tracking-wider text-foreground">
              Farm Profile Defaults
            </h3>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-foreground mb-1">Farmer Name</label>
              <input
                type="text"
                value={formData.farmerName}
                onChange={(e) => setFormData({ ...formData, farmerName: e.target.value })}
                className="w-full bg-input/70 border border-border rounded-xl px-3 py-2 text-xs text-foreground focus:ring-1 focus:ring-primary focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-foreground mb-1">Primary Crop</label>
              <input
                type="text"
                value={formData.primaryCrop}
                onChange={(e) => setFormData({ ...formData, primaryCrop: e.target.value })}
                className="w-full bg-input/70 border border-border rounded-xl px-3 py-2 text-xs text-foreground focus:ring-1 focus:ring-primary focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-foreground mb-1">Default Location</label>
            <input
              type="text"
              value={formData.farmLocation}
              onChange={(e) => setFormData({ ...formData, farmLocation: e.target.value })}
              className="w-full bg-input/70 border border-border rounded-xl px-3 py-2 text-xs text-foreground focus:ring-1 focus:ring-primary focus:outline-none"
            />
          </div>
        </div>

        {/* 4. Appearance */}
        <div className="bg-card rounded-2xl border border-border p-4 shadow-sm space-y-3">
          <div className="flex items-center gap-2 pb-2 border-b border-border">
            <Sun className="w-4 h-4 text-primary" />
            <h3 className="font-bold text-xs uppercase tracking-wider text-foreground">
              Appearance
            </h3>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-foreground">Dark Mode</p>
              <p className="text-[10px] text-muted-foreground">Switch between light and dark theme</p>
            </div>
            <button
              type="button"
              onClick={() => {
                const updated = { ...formData, darkMode: !formData.darkMode };
                setFormData(updated);
                onSaveSettings(updated);
              }}
              className={`relative w-12 h-7 rounded-full transition-colors cursor-pointer ${
                formData.darkMode ? 'bg-primary' : 'bg-secondary border border-border'
              }`}
            >
              <span
                className={`absolute top-0.5 left-0.5 w-6 h-6 rounded-full bg-white shadow-md flex items-center justify-center transition-transform ${
                  formData.darkMode ? 'translate-x-5' : 'translate-x-0'
                }`}
              >
                {formData.darkMode ? (
                  <Moon className="w-3.5 h-3.5 text-primary" />
                ) : (
                  <Sun className="w-3.5 h-3.5 text-amber-500" />
                )}
              </span>
            </button>
          </div>
        </div>

        {/* Save Button */}
        <button
          type="submit"
          className="w-full py-3.5 px-4 rounded-xl bg-primary text-primary-foreground font-bold text-sm shadow-md hover:brightness-105 active:scale-98 transition-all cursor-pointer flex items-center justify-center gap-2"
        >
          <Save className="w-4 h-4" />
          <span>Save Preferences & Keys</span>
        </button>
      </form>

      {/* Danger Zone: Clear History */}
      <div className="pt-2">
        <button
          type="button"
          onClick={() => {
            if (window.confirm('Are you sure you want to clear all scan history?')) {
              onClearHistory();
            }
          }}
          className="w-full py-2.5 px-4 rounded-xl border border-destructive/30 text-destructive text-xs font-bold hover:bg-destructive/10 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Clear All Stored Scans</span>
        </button>
      </div>
    </div>
  );
};
