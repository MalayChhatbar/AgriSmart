import React, { useState } from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  Leaf,
  Sparkles,
  ShieldCheck,
  FlaskConical,
  Sprout,
  MessageSquare,
  Share2,
  Info,
  Layers,
  Thermometer,
} from 'lucide-react';
import { DiagnosisResult } from '../types';

interface DiagnosisCardProps {
  result: DiagnosisResult;
  onOpenChat: (initialPrompt?: string) => void;
}

export const DiagnosisCard: React.FC<DiagnosisCardProps> = ({ result, onOpenChat }) => {
  const [activeTab, setActiveTab] = useState<'organic' | 'chemical' | 'cultural'>('organic');

  return (
    <div className="bg-card rounded-3xl border border-border shadow-md overflow-hidden transition-all animate-fadeIn">
      {/* Top Media & Identification Hero */}
      <div className="relative h-48 sm:h-56 w-full overflow-hidden bg-black">
        <img
          src={result.imageUrl}
          alt={result.plantName}
          className="w-full h-full object-cover opacity-90"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />

        {/* Badges on Image */}
        <div className="absolute top-3 left-3 right-3 flex items-center justify-between">
          <span className="px-3 py-1 rounded-full bg-black/60 backdrop-blur-md text-white text-xs font-bold border border-white/20 flex items-center gap-1.5 shadow-sm">
            <Leaf className="w-3.5 h-3.5 text-primary" />
            {result.plantName}
          </span>

          <span
            className={`px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider backdrop-blur-md border shadow-sm flex items-center gap-1.5 ${
              result.isHealthy
                ? 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40'
                : 'bg-rose-950/80 text-rose-300 border-rose-500/40'
            }`}
          >
            {result.isHealthy ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                Healthy Foliage
              </>
            ) : (
              <>
                <AlertTriangle className="w-3.5 h-3.5 text-rose-400 animate-pulse" />
                Disease Detected
              </>
            )}
          </span>
        </div>

        {/* Disease Title & Confidence on Image Bottom */}
        <div className="absolute bottom-3 left-4 right-4 text-white">
          <h2 className="text-xl sm:text-2xl font-black tracking-tight leading-tight">
            {result.diseaseName}
          </h2>
          {result.scientificName && (
            <p className="text-xs text-white/70 italic font-mono mt-0.5">
              {result.scientificName}
            </p>
          )}

          {/* Calibrated Confidence Bar */}
          <div className="flex items-center gap-3 mt-2">
            <div className="flex-1 bg-white/20 rounded-full h-2 overflow-hidden backdrop-blur-sm">
              <div
                className="bg-primary h-full rounded-full transition-all duration-1000 shadow-sm"
                style={{ width: `${Math.round(result.confidence * 100)}%` }}
              />
            </div>
            <span className="text-xs font-extrabold text-primary-foreground bg-primary px-2 py-0.5 rounded-md leading-none shadow-xs">
              {(result.confidence * 100).toFixed(1)}% Match
            </span>
            <span className="text-[10px] text-white/75 font-semibold px-2 py-0.5 rounded bg-white/10">
              {result.tierLabel}
            </span>
          </div>
        </div>
      </div>

      {/* Main Content Body */}
      <div className="p-4 space-y-4">
        {/* Why This Happens Section */}
        <div className="bg-secondary/60 rounded-2xl p-3.5 border border-border/70 space-y-2">
          <div className="flex items-center gap-2 text-foreground font-bold text-xs uppercase tracking-wider">
            <HelpCircle className="w-4 h-4 text-primary" />
            <span>Why This Happens (Pathogen & Cause)</span>
          </div>

          <p className="text-xs text-foreground leading-relaxed">
            {result.whyItHappens.biology}
          </p>

          <div className="pt-2 border-t border-border/50 grid grid-cols-2 gap-2 text-[11px]">
            <div>
              <span className="font-bold text-muted-foreground block">Causal Agent:</span>
              <span className="text-foreground font-semibold">{result.whyItHappens.pathogen}</span>
            </div>
            <div>
              <span className="font-bold text-muted-foreground block">Trigger Conditions:</span>
              <span className="text-foreground font-semibold">
                {result.whyItHappens.favorableConditions}
              </span>
            </div>
          </div>
        </div>

        {/* Environmental Synthesis (Farmer's Weather & Soil Sync) */}
        {result.environmentalAdvice && (
          <div className="bg-primary/10 rounded-2xl p-3 border border-primary/25 flex items-start gap-2.5">
            <div className="p-1.5 rounded-lg bg-primary/20 text-primary mt-0.5">
              <Thermometer className="w-4 h-4" />
            </div>
            <div>
              <span className="text-xs font-bold text-primary block">
                Field Microclimate Advisory
              </span>
              <p className="text-xs text-foreground mt-0.5 leading-relaxed">
                {result.environmentalAdvice}
              </p>
            </div>
          </div>
        )}

        {/* Remedies & Prescriptions Tabs */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-primary" />
              Prescription & Treatment Guide
            </h3>
          </div>

          {/* Sub-tabs */}
          <div className="grid grid-cols-3 gap-1.5 p-1 bg-secondary/80 rounded-xl border border-border">
            <button
              onClick={() => setActiveTab('organic')}
              className={`py-1.5 text-xs font-bold rounded-lg transition-all cursor-pointer flex items-center justify-center gap-1 ${
                activeTab === 'organic'
                  ? 'bg-card text-foreground shadow-xs'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Sprout className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
              <span>Organic</span>
            </button>

            <button
              onClick={() => setActiveTab('chemical')}
              className={`py-1.5 text-xs font-bold rounded-lg transition-all cursor-pointer flex items-center justify-center gap-1 ${
                activeTab === 'chemical'
                  ? 'bg-card text-foreground shadow-xs'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <FlaskConical className="w-3.5 h-3.5 text-blue-500" />
              <span>Chemical</span>
            </button>

            <button
              onClick={() => setActiveTab('cultural')}
              className={`py-1.5 text-xs font-bold rounded-lg transition-all cursor-pointer flex items-center justify-center gap-1 ${
                activeTab === 'cultural'
                  ? 'bg-card text-foreground shadow-xs'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Layers className="w-3.5 h-3.5 text-amber-500" />
              <span>Hygiene</span>
            </button>
          </div>

          {/* Active Tab Content */}
          <div className="mt-2.5 p-3 rounded-2xl bg-card border border-border space-y-2">
            {activeTab === 'organic' && (
              <ul className="space-y-1.5 text-xs text-foreground">
                {result.remedies.organic.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            )}

            {activeTab === 'chemical' && (
              <ul className="space-y-1.5 text-xs text-foreground">
                {result.remedies.chemical.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5 shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            )}

            {activeTab === 'cultural' && (
              <ul className="space-y-1.5 text-xs text-foreground">
                {result.remedies.cultural.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Top-3 Candidates (Differential Diagnosis) */}
        {result.top3Candidates && result.top3Candidates.length > 1 && (
          <div className="pt-2 border-t border-border">
            <span className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider mb-2 block">
              Differential Diagnosis (Top Probability Alternatives)
            </span>
            <div className="space-y-1.5">
              {result.top3Candidates.map((c, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between text-xs p-2 rounded-xl bg-secondary/50 border border-border/50"
                >
                  <span className="font-semibold text-foreground truncate max-w-[240px]">
                    {c.commonName || c.disease}
                  </span>
                  <span className="font-mono font-bold text-primary">
                    {c.confidence.toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Interactive Doubt Clearance Action */}
        <div className="pt-2">
          <button
            onClick={() => onOpenChat(`I just scanned my ${result.plantName} with ${result.diseaseName}. What is the best organic spray schedule for my field?`)}
            className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-primary to-emerald-500 text-primary-foreground font-bold text-xs shadow-md hover:brightness-105 active:scale-98 transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            <MessageSquare className="w-4 h-4" />
            <span>Ask Kisan AI Doubts about this Diagnosis</span>
          </button>
        </div>
      </div>
    </div>
  );
};
