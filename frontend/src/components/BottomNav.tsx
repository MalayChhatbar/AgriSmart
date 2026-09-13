import React from 'react';
import { Home, History, Settings, Camera } from 'lucide-react';

export type ActiveTab = 'home' | 'history' | 'settings';

interface BottomNavProps {
  activeTab: ActiveTab;
  onChangeTab: (tab: ActiveTab) => void;
  historyCount: number;
  onOpenScanner: () => void;
}

export const BottomNav: React.FC<BottomNavProps> = ({
  activeTab,
  onChangeTab,
  historyCount,
  onOpenScanner,
}) => {
  return (
    <div className="fixed bottom-0 left-0 right-0 z-40 pointer-events-none pb-safe">
      <div className="max-w-md mx-auto px-4 pb-3 pt-1">
        <nav className="pointer-events-auto bg-card/90 backdrop-blur-xl border border-border/80 rounded-2xl shadow-xl p-1.5 flex items-center justify-around relative">
          {/* Home Tab */}
          <button
            onClick={() => onChangeTab('home')}
            className={`flex flex-col items-center justify-center py-1 px-4 rounded-xl transition-all cursor-pointer ${
              activeTab === 'home'
                ? 'bg-primary/15 text-primary font-bold shadow-xs'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Home className="w-5 h-5 mb-0.5" />
            <span className="text-[11px]">Home</span>
          </button>

          {/* Quick Scan Center Button */}
          <button
            onClick={onOpenScanner}
            className="flex items-center justify-center -mt-6 w-14 h-14 rounded-full bg-gradient-to-tr from-primary to-emerald-400 text-primary-foreground shadow-lg shadow-primary/30 border-4 border-background hover:scale-105 active:scale-95 transition-all cursor-pointer group"
            title="Scan Crop Leaf"
          >
            <Camera className="w-6 h-6 group-hover:rotate-6 transition-transform" />
          </button>

          {/* History Tab */}
          <button
            onClick={() => onChangeTab('history')}
            className={`flex flex-col items-center justify-center py-1 px-4 rounded-xl transition-all relative cursor-pointer ${
              activeTab === 'history'
                ? 'bg-primary/15 text-primary font-bold shadow-xs'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <div className="relative">
              <History className="w-5 h-5 mb-0.5" />
              {historyCount > 0 && (
                <span className="absolute -top-1 -right-2 px-1.5 py-0.2 rounded-full text-[10px] font-extrabold bg-primary text-primary-foreground leading-tight">
                  {historyCount > 9 ? '9+' : historyCount}
                </span>
              )}
            </div>
            <span className="text-[11px]">History</span>
          </button>

          {/* Settings Tab */}
          <button
            onClick={() => onChangeTab('settings')}
            className={`flex flex-col items-center justify-center py-1 px-4 rounded-xl transition-all cursor-pointer ${
              activeTab === 'settings'
                ? 'bg-primary/15 text-primary font-bold shadow-xs'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Settings className="w-5 h-5 mb-0.5" />
            <span className="text-[11px]">Settings</span>
          </button>
        </nav>
      </div>
    </div>
  );
};
