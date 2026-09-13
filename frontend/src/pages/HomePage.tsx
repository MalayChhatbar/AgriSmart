import React, { useState, useEffect, useRef } from 'react';
import { SylvaHero } from '../shaders/landing-pages/LandingPages';
import { DiagnosisCard } from '../components/DiagnosisCard';
import { EnvironmentalContext, DiagnosisResult } from '../types';
import { ActiveTab } from '../components/BottomNav';
import { Sparkles, X, ChevronUp, CloudRain, ShieldCheck, Camera, MessageSquare } from 'lucide-react';

interface HomePageProps {
  env: EnvironmentalContext;
  onUpdateEnv: (updated: Partial<EnvironmentalContext>) => void;
  latestDiagnosis: DiagnosisResult | null;
  freshScanId: string | null;
  onClearFreshScan: () => void;
  onOpenScanner: () => void;
  onOpenChat: (initialPrompt?: string) => void;
  onNavigateTab: (tab: ActiveTab) => void;
  backendOnline: boolean;
}

export const HomePage: React.FC<HomePageProps> = ({
  env,
  latestDiagnosis,
  freshScanId,
  onClearFreshScan,
  onOpenScanner,
  onOpenChat,
  onNavigateTab,
  backendOnline,
}) => {
  const [isDiagnosisSheetOpen, setIsDiagnosisSheetOpen] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);

  // Only auto-open the diagnosis sheet when a FRESH scan comes in (not on re-mount)
  useEffect(() => {
    if (freshScanId && latestDiagnosis && latestDiagnosis.id === freshScanId) {
      setIsDiagnosisSheetOpen(true);
      setIsDismissed(false);
      onClearFreshScan();
    }
  }, [freshScanId, latestDiagnosis, onClearFreshScan]);

  // NOTE: Navigation events from the 3D iframe are handled ONLY in App.tsx.
  // No duplicate listener here.

  return (
    <div className="relative w-full h-full min-h-[100dvh] flex flex-col bg-[#383b34] overflow-hidden select-none">
      {/* 1. Full-Screen ThreeUI 3D Living World Frame */}
      <div className="absolute inset-0 w-full h-full z-0">
        <SylvaHero
          variant="living-green"
          style={{
            width: '100%',
            height: '100%',
            minHeight: '100dvh',
            border: 0,
          }}
        />
      </div>

      {/* 2. Floating Quick Action Bar (Bottom Overlay for high accessibility) */}
      <div className="absolute bottom-5 left-4 right-4 z-20 pointer-events-none flex flex-col items-center gap-2.5">
        {/* Floating Active Diagnosis Pill (If diagnosis exists) */}
        {latestDiagnosis && !isDismissed && (
          <div
            onClick={() => setIsDiagnosisSheetOpen(true)}
            className="pointer-events-auto w-full max-w-sm bg-black/75 hover:bg-black/85 backdrop-blur-xl border border-emerald-500/30 text-white rounded-2xl p-3 shadow-2xl cursor-pointer transition-all active:scale-98 flex items-center justify-between group"
          >
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-400/30 flex items-center justify-center text-emerald-400">
                <Sparkles className="w-4 h-4 animate-spin" />
              </div>
              <div className="text-left">
                <div className="flex items-center gap-1.5">
                  <span className="text-[10px] uppercase font-black tracking-wider text-emerald-400">
                    Latest Report
                  </span>
                  <span className="text-[10px] text-white/50">•</span>
                  <span className="text-[10px] text-white/70">
                    {(latestDiagnosis.confidence * 100).toFixed(1)}% Match
                  </span>
                </div>
                <h4 className="text-xs font-bold text-white truncate max-w-[190px]">
                  {latestDiagnosis.plantName}: {latestDiagnosis.diseaseName}
                </h4>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <span className="text-[11px] font-semibold text-emerald-300 flex items-center gap-0.5 group-hover:translate-y-[-1px] transition-transform">
                View <ChevronUp className="w-3.5 h-3.5" />
              </span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setIsDismissed(true);
                }}
                className="p-1 text-white/40 hover:text-white rounded-lg transition-colors cursor-pointer"
                title="Dismiss pill"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 4. Slide-Over Diagnosis Sheet Modal */}
      {isDiagnosisSheetOpen && latestDiagnosis && (
        <div className="fixed inset-0 z-50 flex flex-col justify-end bg-black/60 backdrop-blur-sm animate-fadeIn">
          {/* Backdrop dismiss */}
          <div
            className="flex-1 w-full"
            onClick={() => setIsDiagnosisSheetOpen(false)}
          />

          {/* Sheet container */}
          <div className="relative w-full max-w-md mx-auto bg-card border-t border-border rounded-t-3xl shadow-2xl max-h-[88vh] flex flex-col animate-slideUp overflow-hidden">
            {/* Sheet Handle & Header */}
            <div className="p-4 pb-2 border-b border-border/50 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-primary/15 text-primary flex items-center justify-center">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-black text-foreground">
                    Plant Health Diagnostics
                  </h3>
                  <p className="text-[10px] text-muted-foreground">
                    Analyzed with organizers' Dual-Model CV Pipeline
                  </p>
                </div>
              </div>

              <button
                onClick={() => setIsDiagnosisSheetOpen(false)}
                className="w-8 h-8 rounded-full bg-secondary text-secondary-foreground hover:bg-secondary/80 flex items-center justify-center cursor-pointer transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Scrollable Report Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <DiagnosisCard
                result={latestDiagnosis}
                onOpenChat={onOpenChat}
              />
            </div>

            {/* Bottom Actions inside Sheet */}
            <div className="p-3 bg-secondary/30 border-t border-border/60 flex items-center gap-2">
              <button
                onClick={() => {
                  setIsDiagnosisSheetOpen(false);
                  onOpenScanner();
                }}
                className="flex-1 py-2.5 px-3 rounded-xl bg-primary text-primary-foreground font-bold text-xs shadow-sm hover:brightness-105 active:scale-98 transition-all flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <Camera className="w-3.5 h-3.5" />
                <span>Scan Another Leaf</span>
              </button>
              <button
                onClick={() => {
                  setIsDiagnosisSheetOpen(false);
                  onOpenChat(`Tell me how to cure ${latestDiagnosis.diseaseName} in my ${latestDiagnosis.plantName} step by step.`);
                }}
                className="py-2.5 px-3 rounded-xl bg-secondary text-secondary-foreground border border-border font-bold text-xs hover:border-primary/40 active:scale-98 transition-all flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <MessageSquare className="w-3.5 h-3.5 text-primary" />
                <span>Ask AI</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
