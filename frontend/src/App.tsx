import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ActiveTab } from './components/BottomNav';
import { HomePage } from './pages/HomePage';
import { HistoryPage } from './pages/HistoryPage';
import { SettingsPage } from './pages/SettingsPage';
import { CropScannerModal } from './components/CropScannerModal';
import { KisanChatDrawer } from './components/KisanChatDrawer';
import {
  EnvironmentalContext,
  DiagnosisResult,
  HistoryItem,
  AppSettings,
} from './types';
import {
  loadScanHistory,
  saveScanToHistory,
  deleteScanFromHistory,
  clearAllHistory,
  loadSettings,
  saveSettings,
  loadEnvContext,
  saveEnvContext,
} from './services/storage';
import { checkBackendConnection, diagnoseCropImage } from './services/api';
import confetti from 'canvas-confetti';

export function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('home');
  const [settings, setSettings] = useState<AppSettings>(loadSettings);
  const [env, setEnv] = useState<EnvironmentalContext>(loadEnvContext);
  const [history, setHistory] = useState<HistoryItem[]>(loadScanHistory);
  const [latestDiagnosis, setLatestDiagnosis] = useState<DiagnosisResult | null>(() => {
    const hist = loadScanHistory();
    return hist.length > 0 ? hist[0] : null;
  });

  const [isScannerOpen, setIsScannerOpen] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInitialPrompt, setChatInitialPrompt] = useState<string | undefined>();
  const [backendOnline, setBackendOnline] = useState(false);

  // Track whether diagnosis was freshly scanned (to only auto-open sheet once)
  const [freshScanId, setFreshScanId] = useState<string | null>(null);

  // Ref to avoid stale closures in popstate
  const activeTabRef = useRef(activeTab);
  activeTabRef.current = activeTab;

  // Sync Dark Mode with document element
  useEffect(() => {
    if (settings.darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [settings.darkMode]);

  // Check Backend status on mount
  useEffect(() => {
    const ping = async () => {
      const res = await checkBackendConnection(settings.backendUrl);
      setBackendOnline(res.online);
    };
    ping();
    const interval = setInterval(ping, 15000);
    return () => clearInterval(interval);
  }, [settings.backendUrl]);

  const handleUpdateSettings = (newSettings: Partial<AppSettings>) => {
    const updated = { ...settings, ...newSettings };
    setSettings(updated);
    saveSettings(updated);
  };

  const handleUpdateEnv = (updatedFields: Partial<EnvironmentalContext>) => {
    const updated = { ...env, ...updatedFields };
    setEnv(updated);
    saveEnvContext(updated);
  };

  const handleScanComplete = async (
    fileOrBlob: File | Blob,
    previewUrl: string,
    presetKey?: string,
    cropHint?: string
  ) => {
    setIsScanning(true);
    try {
      const result = await diagnoseCropImage(
        fileOrBlob,
        previewUrl,
        env,
        settings.backendUrl,
        presetKey,
        cropHint
      );

      setLatestDiagnosis(result);
      setFreshScanId(result.id);

      // Save to history
      const historyEntry: HistoryItem = {
        ...result,
        environmentalSnapshot: {
          location: env.location,
          temperature: env.temperature,
          humidity: env.humidity,
          soilType: env.soilType,
        },
      };
      saveScanToHistory(historyEntry);
      setHistory(loadScanHistory());

      // If healthy, celebrate!
      if (result.isHealthy) {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 },
          colors: ['#10b981', '#34d399', '#6ee7b7', '#059669'],
        });
      }

      // Switch to Home tab to view the result
      setActiveTab('home');
    } catch (err) {
      console.error('Scan error', err);
    } finally {
      setIsScanning(false);
    }
  };

  const handleDeleteScan = (id: string) => {
    const updated = deleteScanFromHistory(id);
    setHistory(updated);
    if (latestDiagnosis?.id === id) {
      setLatestDiagnosis(updated.length > 0 ? updated[0] : null);
    }
  };

  const handleClearAllHistory = () => {
    clearAllHistory();
    setHistory([]);
    setLatestDiagnosis(null);
  };

  const handleOpenChat = useCallback((prompt?: string) => {
    setChatInitialPrompt(prompt);
    setIsChatOpen(true);
  }, []);

  const handleOpenScanner = useCallback(() => {
    setIsScannerOpen(true);
  }, []);

  // ── Simple, clean tab navigation ──
  // Only one pushState per tab change. No pushState for modals.
  const handleNavigateTab = useCallback((tab: ActiveTab) => {
    if (tab === activeTabRef.current) return;
    if (tab !== 'home') {
      // Push a state entry so hardware back returns to home
      window.history.pushState({ tab }, '', `#${tab}`);
    }
    setActiveTab(tab);
  }, []);

  // Back button from the UI "Back to Living World" header
  const handleBackToHome = useCallback(() => {
    // If we're on a non-home tab, the history has an entry for it.
    // Just go back to pop it, popstate handler will set tab to home.
    if (activeTabRef.current !== 'home') {
      window.history.back();
    }
  }, []);

  // ── Sync dock highlight in the 3D iframe ──
  useEffect(() => {
    const syncDock = () => {
      const iframe = document.querySelector('iframe');
      if (iframe?.contentWindow) {
        iframe.contentWindow.postMessage({ type: 'SYNC_TAB', tab: activeTab }, '*');
      }
    };
    // Small delay to ensure iframe is ready
    syncDock();
    const t = setTimeout(syncDock, 300);
    return () => clearTimeout(t);
  }, [activeTab]);

  // ── Global message listener for 3D iframe navigation ──
  // This is the ONLY listener. Removed duplicate in HomePage.
  useEffect(() => {
    const handleGlobalNav = (e: MessageEvent) => {
      if (e.data?.type === 'AGRI_NAV') {
        switch (e.data.action) {
          case 'scan':
            setIsScannerOpen(true);
            break;
          case 'chat':
            setIsChatOpen(true);
            break;
          case 'history':
            handleNavigateTab('history');
            break;
          case 'settings':
            handleNavigateTab('settings');
            break;
          case 'home':
            if (activeTabRef.current !== 'home') {
              window.history.back();
            }
            break;
        }
      }
    };
    window.addEventListener('message', handleGlobalNav);
    return () => window.removeEventListener('message', handleGlobalNav);
  }, [handleNavigateTab]);

  // ── Hardware / browser back button handling ──
  useEffect(() => {
    // Set initial state
    window.history.replaceState({ tab: 'home' }, '', '#home');

    const handlePopState = (event: PopStateEvent) => {
      const state = event.state;
      if (state?.tab) {
        setActiveTab(state.tab);
      } else {
        // Fallback: no state means we're at root => home
        setActiveTab('home');
      }
      // Always close modals on any back navigation
      setIsScannerOpen(false);
      setIsChatOpen(false);
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans">
      {/* Mobile Shell Wrapper with Smartphone Max-Width */}
      <div className="w-full max-w-md mx-auto flex-1 flex flex-col shadow-2xl bg-card border-x border-border/40 relative min-h-[100dvh]">
        {/* Main Tab View Content */}
        <main className={`flex-1 flex flex-col overflow-x-hidden ${activeTab === 'home' ? 'p-0 overflow-hidden' : 'p-3.5 sm:p-4 pb-10'}`}>
          {/* Home page is always mounted but hidden when not active to preserve the 3D scene */}
          <div style={{ display: activeTab === 'home' ? 'contents' : 'none' }}>
            <HomePage
              env={env}
              onUpdateEnv={handleUpdateEnv}
              latestDiagnosis={latestDiagnosis}
              freshScanId={freshScanId}
              onClearFreshScan={() => setFreshScanId(null)}
              onOpenScanner={handleOpenScanner}
              onOpenChat={handleOpenChat}
              onNavigateTab={handleNavigateTab}
              backendOnline={backendOnline}
            />
          </div>

          {activeTab === 'history' && (
            <HistoryPage
              history={history}
              onDeleteScan={handleDeleteScan}
              onClearAll={handleClearAllHistory}
              onOpenChat={handleOpenChat}
              onBack={handleBackToHome}
            />
          )}

          {activeTab === 'settings' && (
            <SettingsPage
              settings={settings}
              onSaveSettings={handleUpdateSettings}
              onClearHistory={handleClearAllHistory}
              onBack={handleBackToHome}
            />
          )}
        </main>
      </div>

      {/* Crop Scanner Modal */}
      <CropScannerModal
        isOpen={isScannerOpen}
        onClose={() => setIsScannerOpen(false)}
        onScanComplete={handleScanComplete}
        isScanning={isScanning}
      />

      {/* Kisan AI Doubt Clearance Chat Drawer */}
      <KisanChatDrawer
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
        currentCrop={latestDiagnosis?.plantName || 'Tomato'}
        detectedDisease={latestDiagnosis?.diseaseName || 'Early Blight'}
        language={settings.language}
        backendUrl={settings.backendUrl}
        initialPrompt={chatInitialPrompt}
      />
    </div>
  );
}

export default App;
