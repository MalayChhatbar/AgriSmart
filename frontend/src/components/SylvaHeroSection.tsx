import React, { useState } from 'react';
import { SylvaHero } from '../shaders/landing-pages/LandingPages';
import { Sparkles, Maximize2, Minimize2, Scan, MessageSquare, CloudRain } from 'lucide-react';

interface SylvaHeroSectionProps {
  onScanClick: () => void;
  onChatClick: () => void;
  onScrollToWeather: () => void;
}

export const SylvaHeroSection: React.FC<SylvaHeroSectionProps> = ({
  onScanClick,
  onChatClick,
  onScrollToWeather,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="relative rounded-3xl overflow-hidden border border-border/80 shadow-md bg-card transition-all duration-300">
      {/* 3D Living World Canvas Container */}
      <div
        className={`w-full relative transition-all duration-500 ease-out flex items-center justify-center ${
          isExpanded ? 'h-[300px]' : 'h-[200px]'
        }`}
        style={{
          background: 'linear-gradient(135deg, #0f172a 0%, #064e3b 100%)'
        }}
      >
        {/* Subtle pattern overlay */}
        <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.15) 1px, transparent 0)', backgroundSize: '24px 24px' }}></div>

        {/* Ambient Top Vignette */}
        <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-black/40 via-transparent to-card/95" />

        {/* Expand / Minimize Living World Control */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="absolute top-3 right-3 z-20 p-2 rounded-xl bg-black/40 hover:bg-black/60 backdrop-blur-md text-white border border-white/15 transition-all active:scale-95 cursor-pointer shadow-sm flex items-center gap-1.5 text-xs font-semibold"
          title={isExpanded ? 'Minimize 3D View' : 'Expand 3D Living World'}
        >
          {isExpanded ? (
            <>
              <Minimize2 className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-[11px]">Compact</span>
            </>
          ) : (
            <>
              <Maximize2 className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-[11px]">3D View</span>
            </>
          )}
        </button>

        {/* Nature Tag Pill */}
        <div className="absolute top-3 left-3 z-20 px-2.5 py-1 rounded-full bg-black/40 backdrop-blur-md text-emerald-300 border border-emerald-500/20 text-[11px] font-medium flex items-center gap-1.5 shadow-sm">
          <Sparkles className="w-3 h-3 text-emerald-400 animate-spin" />
          <span>Sylva Living Biosphere</span>
        </div>

        {/* Floating Hero Copy */}
        <div className="absolute bottom-3 left-4 right-4 z-20 text-foreground">
          <div className="flex items-end justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-primary">
                Precision Agriculture
              </p>
              <h2 className="text-xl font-extrabold tracking-tight text-white drop-shadow-sm">
                Smart Plant Doctor
              </h2>
            </div>
          </div>
        </div>
      </div>

      {/* Action Bar Below 3D View */}
      <div className="p-3.5 bg-card border-t border-border/60">
        <div className="grid grid-cols-3 gap-2">
          {/* Scan Button */}
          <button
            onClick={onScanClick}
            className="flex flex-col items-center justify-center gap-1.5 py-2.5 px-2 rounded-xl bg-primary text-primary-foreground font-semibold text-xs shadow-sm hover:brightness-105 active:scale-98 transition-all cursor-pointer"
          >
            <Scan className="w-4 h-4" />
            <span>Scan Leaf</span>
          </button>

          {/* Chat AI Button */}
          <button
            onClick={onChatClick}
            className="flex flex-col items-center justify-center gap-1.5 py-2.5 px-2 rounded-xl bg-secondary text-secondary-foreground font-semibold text-xs border border-border hover:border-primary/40 active:scale-98 transition-all cursor-pointer"
          >
            <MessageSquare className="w-4 h-4 text-primary" />
            <span>Ask AI</span>
          </button>

          {/* Microclimate Button */}
          <button
            onClick={onScrollToWeather}
            className="flex flex-col items-center justify-center gap-1.5 py-2.5 px-2 rounded-xl bg-secondary text-secondary-foreground font-semibold text-xs border border-border hover:border-primary/40 active:scale-98 transition-all cursor-pointer"
          >
            <CloudRain className="w-4 h-4 text-sky-500" />
            <span>Weather</span>
          </button>
        </div>
      </div>
    </div>
  );
};
