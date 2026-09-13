import React from 'react';
import { Sprout, Sun, Moon, Globe, Radio } from 'lucide-react';
import { AppSettings } from '../types';

interface NavbarProps {
  settings: AppSettings;
  onUpdateSettings: (newSettings: Partial<AppSettings>) => void;
  backendOnline: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ settings, onUpdateSettings, backendOnline }) => {
  return (
    <header className="sticky top-0 z-40 bg-card/85 backdrop-blur-md border-b border-border transition-colors">
      <div className="max-w-md mx-auto px-4 h-15 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-primary/20 border border-primary/40 flex items-center justify-center text-primary shadow-xs">
            <Sprout className="w-5 h-5 text-primary animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <h1 className="font-extrabold text-base tracking-tight leading-none text-foreground">
                AgriSmart<span className="text-primary font-black">AI</span>
              </h1>
              <span className="text-[10px] uppercase font-bold tracking-widest px-1.5 py-0.5 rounded-full bg-primary/15 text-primary border border-primary/25">
                v2.0
              </span>
            </div>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span
                className={`w-2 h-2 rounded-full ${
                  backendOnline ? 'bg-emerald-500 animate-ping' : 'bg-amber-500'
                }`}
              />
              <span className="text-[11px] font-medium text-muted-foreground">
                {backendOnline ? 'AI Model Online' : 'Smart Offline Client'}
              </span>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2">
          {/* Language Toggle */}
          <button
            onClick={() => onUpdateSettings({ language: settings.language === 'en' ? 'hi' : 'en' })}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-secondary text-secondary-foreground text-xs font-semibold border border-border hover:border-primary/40 transition-all active:scale-95 cursor-pointer shadow-xs"
            title="Switch Language (English / हिन्दी)"
          >
            <Globe className="w-3.5 h-3.5 text-primary" />
            <span>{settings.language === 'en' ? 'हिन्दी' : 'English'}</span>
          </button>

          {/* Theme Toggle */}
          <button
            onClick={() => onUpdateSettings({ darkMode: !settings.darkMode })}
            className="p-2 rounded-lg bg-secondary text-secondary-foreground border border-border hover:border-primary/40 transition-all active:scale-95 cursor-pointer shadow-xs"
            aria-label="Toggle Dark Mode"
          >
            {settings.darkMode ? (
              <Sun className="w-4 h-4 text-amber-400" />
            ) : (
              <Moon className="w-4 h-4 text-slate-700" />
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
