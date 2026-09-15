import React from 'react';


const HomeIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M4 10L12 3L20 10V20C20 20.5523 19.5523 21 19 21H5C4.44772 21 4 20.5523 4 20V10Z" />
    <path d="M9 21V12H15V21" />
  </svg>
);

const HistoryIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M3 12C3 13.78 3.52784 15.5201 4.51677 17.0001C5.50571 18.4802 6.91131 19.6337 8.55585 20.3149C10.2004 20.9961 12.01 21.1743 13.7558 20.8271C15.5016 20.4798 17.1053 19.6226 18.364 18.364C19.6226 17.1053 20.4798 15.5016 20.8271 13.7558C21.1743 12.01 20.9961 10.2004 20.3149 8.55585C19.6337 6.91131 18.4802 5.50571 17.0001 4.51677C15.5201 3.52784 13.78 3 12 3C9.48395 3.00947 7.06897 3.99122 5.26 5.74L3 8M8 8H3V3M12 7V12L16 14" />
  </svg>
);

const SettingsIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M9.67106 4.13615C9.72616 3.55649 9.99539 3.0182 10.4262 2.62643C10.8569 2.23467 11.4183 2.01758 12.0006 2.01758C12.5828 2.01758 13.1442 2.23467 13.575 2.62643C14.0057 3.0182 14.275 3.55649 14.3301 4.13615C14.3632 4.51061 14.486 4.87157 14.6882 5.18849C14.8904 5.50541 15.1659 5.76896 15.4915 5.95683C15.8171 6.1447 16.1832 6.25135 16.5588 6.26777C16.9343 6.28419 17.3083 6.20989 17.6491 6.05115C18.1782 5.81093 18.7777 5.77617 19.3311 5.95364C19.8844 6.1311 20.3519 6.5081 20.6426 7.01126C20.9333 7.51441 21.0263 8.10772 20.9037 8.67572C20.7811 9.24372 20.4515 9.74577 19.9791 10.0842C19.6714 10.3 19.4203 10.5868 19.247 10.9202C19.0736 11.2536 18.9831 11.6239 18.9831 11.9997C18.9831 12.3754 19.0736 12.7457 19.247 13.0791C19.4203 13.4125 19.6714 13.6993 19.9791 13.9152C20.4515 14.2535 20.7811 14.7556 20.9037 15.3236C21.0263 15.8916 20.9333 16.4849 20.6426 16.988C20.3519 17.4912 19.8844 17.8682 19.3311 18.0457C18.7777 18.2231 18.1782 18.1884 17.6491 17.9482C17.3083 17.7894 16.9343 17.7151 16.5588 17.7315C16.1832 17.7479 15.8171 17.8546 15.4915 18.0425C15.1659 18.2303 14.8904 18.4939 14.6882 18.8108C14.486 19.1277 14.3632 19.4887 14.3301 19.8632C14.275 20.4428 14.0057 20.9811 13.575 21.3729C13.1442 21.7646 12.5828 21.9817 12.0006 21.9817C11.4183 21.9817 10.8569 21.7646 10.4262 21.3729C9.99539 20.9811 9.72616 20.4428 9.67106 19.8632C9.638 19.4886 9.51516 19.1275 9.31293 18.8104C9.11069 18.4934 8.83503 18.2298 8.50929 18.0419C8.18355 17.854 7.81733 17.7474 7.44164 17.7311C7.06595 17.7147 6.69186 17.7892 6.35106 17.9482C5.82195 18.1884 5.22239 18.2231 4.66906 18.0457C4.11573 17.8682 3.64823 17.4912 3.35754 16.988C3.06685 16.4849 2.97377 15.8916 3.09642 15.3236C3.21907 14.7556 3.54866 14.2535 4.02106 13.9152C4.32868 13.6993 4.57979 13.4125 4.75315 13.0791C4.92651 12.7457 5.01701 12.3754 5.01701 11.9997C5.01701 11.6239 4.92651 11.2536 4.75315 10.9202C4.57979 10.5868 4.32868 10.3 4.02106 10.0842C3.54932 9.7456 3.22031 9.24375 3.09796 8.67613C2.97561 8.10852 3.06867 7.51569 3.35904 7.01286C3.64942 6.51004 4.11637 6.13313 4.66915 5.95539C5.22193 5.77766 5.82104 5.81179 6.35006 6.05115C6.69082 6.20989 7.0648 6.28419 7.44036 6.26777C7.81592 6.25135 8.18199 6.1447 8.5076 5.95683C8.8332 5.76896 9.10875 5.50541 9.31093 5.18849C9.5131 4.87157 9.63594 4.51061 9.66906 4.13615M15 12C15 13.6569 13.6569 15 12 15C10.3431 15 9 13.6569 9 12C9 10.3431 10.3431 9 12 9C13.6569 9 15 10.3431 15 12Z" />
  </svg>
);

const CameraIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M23 19C23 20.1046 22.1046 21 21 21H3C1.89543 21 1 20.1046 1 19V8C1 6.89543 1.89543 6 3 6H7L9 3H15L17 6H21C22.1046 6 23 6.89543 23 8V19Z" />
    <path d="M12 17C14.7614 17 17 14.7614 17 12C17 9.23858 14.7614 7 12 7C9.23858 7 7 9.23858 7 12C7 14.7614 9.23858 17 12 17Z" />
  </svg>
);

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
    <div className="fixed bottom-0 left-0 right-0 z-40 pointer-events-none style={{ paddingBottom: 'max(env(safe-area-inset-bottom), 12px)' }}">
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
            <HomeIcon className="w-5 h-5 mb-0.5" />
            <span className="text-[11px]">Home</span>
          </button>

          {/* Quick Scan Center Button */}
          <button
            onClick={onOpenScanner}
            className="flex items-center justify-center -mt-6 w-14 h-14 rounded-full bg-gradient-to-tr from-primary to-emerald-400 text-primary-foreground shadow-lg shadow-primary/30 border-4 border-background hover:scale-105 active:scale-95 transition-all cursor-pointer group"
            title="Scan Crop Leaf"
          >
            <CameraIcon className="w-6 h-6 group-hover:rotate-6 transition-transform" />
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
              <HistoryIcon className="w-5 h-5 mb-0.5" />
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
            <SettingsIcon className="w-5 h-5 mb-0.5" />
            <span className="text-[11px]">Settings</span>
          </button>
        </nav>
      </div>
    </div>
  );
};
