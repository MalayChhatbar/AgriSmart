import React, { useState } from 'react';
import {
  HistoryItem,
} from '../types';
import {
  History,
  Search,
  Trash2,
  Download,
  Calendar,
  MapPin,
  Leaf,
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  Sparkles,
  ArrowUpDown,
  ArrowLeft,
} from 'lucide-react';
import { DiagnosisCard } from '../components/DiagnosisCard';

interface HistoryPageProps {
  history: HistoryItem[];
  onDeleteScan: (id: string) => void;
  onClearAll: () => void;
  onOpenChat: (prompt?: string) => void;
  onBack: () => void;
}

export const HistoryPage: React.FC<HistoryPageProps> = ({
  history,
  onDeleteScan,
  onClearAll,
  onOpenChat,
  onBack,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'diseased' | 'healthy'>('all');
  const [selectedScan, setSelectedScan] = useState<HistoryItem | null>(null);

  const filteredHistory = history.filter((item) => {
    const matchesSearch =
      item.plantName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.diseaseName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.environmentalSnapshot?.location || '').toLowerCase().includes(searchTerm.toLowerCase());

    if (filterType === 'diseased') return matchesSearch && !item.isHealthy;
    if (filterType === 'healthy') return matchesSearch && item.isHealthy;
    return matchesSearch;
  });

  const handleExportJSON = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(history, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `agrismart_history_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
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
          Records
        </span>
      </div>

      {/* Header & Controls */}
      <div className="bg-card rounded-2xl border border-border p-4 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-primary/20 flex items-center justify-center text-primary">
              <History className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-bold text-base text-foreground">Scanned Crop History</h2>
              <p className="text-xs text-muted-foreground">
                {history.length} field {history.length === 1 ? 'diagnosis' : 'diagnoses'} recorded
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            {history.length > 0 && (
              <>
                <button
                  onClick={handleExportJSON}
                  className="p-2 rounded-xl bg-secondary text-secondary-foreground border border-border hover:border-primary/40 text-xs font-semibold active:scale-95 transition-all cursor-pointer shadow-2xs"
                  title="Export History JSON"
                >
                  <Download className="w-4 h-4" />
                </button>
                <button
                  onClick={onClearAll}
                  className="p-2 rounded-xl bg-destructive/10 text-destructive border border-destructive/20 hover:bg-destructive/20 text-xs font-semibold active:scale-95 transition-all cursor-pointer shadow-2xs"
                  title="Clear All History"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </>
            )}
          </div>
        </div>

        {/* Search Input */}
        <div className="relative">
          <Search className="w-4 h-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search crop, disease, or field location..."
            className="w-full bg-input/70 border border-border rounded-xl pl-9 pr-3 py-2 text-xs text-foreground placeholder:text-muted-foreground focus:ring-1 focus:ring-primary focus:outline-none"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5 pt-1">
          <button
            onClick={() => setFilterType('all')}
            className={`px-3 py-1 rounded-full text-xs font-bold transition-all cursor-pointer ${
              filterType === 'all'
                ? 'bg-primary text-primary-foreground shadow-xs'
                : 'bg-secondary text-muted-foreground hover:text-foreground'
            }`}
          >
            All ({history.length})
          </button>
          <button
            onClick={() => setFilterType('diseased')}
            className={`px-3 py-1 rounded-full text-xs font-bold transition-all cursor-pointer ${
              filterType === 'diseased'
                ? 'bg-rose-500 text-white shadow-xs'
                : 'bg-secondary text-muted-foreground hover:text-foreground'
            }`}
          >
            Diseased ({history.filter((h) => !h.isHealthy).length})
          </button>
          <button
            onClick={() => setFilterType('healthy')}
            className={`px-3 py-1 rounded-full text-xs font-bold transition-all cursor-pointer ${
              filterType === 'healthy'
                ? 'bg-emerald-600 text-white shadow-xs'
                : 'bg-secondary text-muted-foreground hover:text-foreground'
            }`}
          >
            Healthy ({history.filter((h) => h.isHealthy).length})
          </button>
        </div>
      </div>

      {/* History List */}
      {filteredHistory.length === 0 ? (
        <div className="bg-card rounded-2xl border border-border p-8 text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-secondary mx-auto flex items-center justify-center text-muted-foreground">
            <Search className="w-6 h-6" />
          </div>
          <h4 className="font-bold text-sm text-foreground">No matching scan records</h4>
          <p className="text-xs text-muted-foreground max-w-xs mx-auto">
            {searchTerm ? 'Try adjusting your search query' : 'Your scanned plant records will appear here.'}
          </p>
        </div>
      ) : (
        <div className="space-y-2.5">
          {filteredHistory.map((item) => {
            const dateStr = new Date(item.timestamp).toLocaleDateString([], {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            });

            return (
              <div
                key={item.id}
                onClick={() => setSelectedScan(item)}
                className="bg-card rounded-2xl border border-border p-3 shadow-xs hover:border-primary/50 transition-all cursor-pointer flex items-center gap-3 active:scale-99 group"
              >
                {/* Thumbnail */}
                <div className="w-16 h-16 rounded-xl overflow-hidden bg-black shrink-0 relative">
                  <img
                    src={item.imageUrl}
                    alt={item.plantName}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                  />
                  <div className="absolute top-1 right-1">
                    {item.isHealthy ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 drop-shadow" />
                    ) : (
                      <AlertTriangle className="w-3.5 h-3.5 text-rose-400 drop-shadow" />
                    )}
                  </div>
                </div>

                {/* Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className="text-[10px] uppercase font-bold text-primary tracking-wider">
                      {item.plantName}
                    </span>
                    <span className="text-[10px] text-muted-foreground">• {dateStr}</span>
                  </div>

                  <h3 className="font-bold text-sm text-foreground truncate mt-0.5">
                    {item.diseaseName}
                  </h3>

                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-primary/15 text-primary">
                      {(item.confidence * 100).toFixed(0)}% Confident
                    </span>

                    {item.environmentalSnapshot && (
                      <span className="text-[10px] text-muted-foreground flex items-center gap-0.5 truncate max-w-[140px]">
                        <MapPin className="w-2.5 h-2.5 shrink-0" />
                        {item.environmentalSnapshot.location.split(',')[0]}
                      </span>
                    )}
                  </div>
                </div>

                {/* Arrow */}
                <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-primary group-hover:translate-x-0.5 transition-all" />
              </div>
            );
          })}
        </div>
      )}

      {/* Selected Scan Full View Modal */}
      {selectedScan && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div className="bg-card w-full max-w-md rounded-3xl border border-border max-h-[90vh] overflow-y-auto shadow-2xl p-4 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-border">
              <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                Historical Diagnosis Record
              </span>
              <button
                onClick={() => setSelectedScan(null)}
                className="p-1.5 rounded-full hover:bg-secondary text-muted-foreground hover:text-foreground cursor-pointer"
              >
                ✕
              </button>
            </div>

            <DiagnosisCard
              result={selectedScan}
              onOpenChat={(prompt) => {
                setSelectedScan(null);
                onOpenChat(prompt);
              }}
            />

            <div className="flex gap-2 pt-2">
              <button
                onClick={() => {
                  onDeleteScan(selectedScan.id);
                  setSelectedScan(null);
                }}
                className="flex-1 py-2.5 rounded-xl border border-destructive/30 text-destructive text-xs font-bold hover:bg-destructive/10 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <Trash2 className="w-4 h-4" />
                <span>Delete Record</span>
              </button>
              <button
                onClick={() => setSelectedScan(null)}
                className="flex-1 py-2.5 rounded-xl bg-secondary text-foreground text-xs font-bold hover:bg-secondary/80 transition-colors cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
