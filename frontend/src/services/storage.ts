import { HistoryItem, AppSettings, EnvironmentalContext } from '../types';

const HISTORY_KEY = 'agrismart_scan_history_v2';
const SETTINGS_KEY = 'agrismart_app_settings_v2';
const ENV_KEY = 'agrismart_env_context_v2';

export const DEFAULT_SETTINGS: AppSettings = {
  geminiApiKey: '',
  openaiApiKey: '',
  weatherApiKey: '',
  nvidiaApiKey: '',
  aiModel: 'deepseek-ai/deepseek-v3',
  backendUrl: 'https://agrismart-62u5.onrender.com',
  farmerName: 'Ramesh Patel',
  farmLocation: 'Nashik District, Maharashtra',
  primaryCrop: 'Tomato',
  defaultSoil: 'Loamy',
  language: 'en',
  darkMode: false,
  voiceGuidance: true,
};

export const DEFAULT_ENV: EnvironmentalContext = {
  location: 'Nashik District, Maharashtra',
  latitude: 20.0059,
  longitude: 73.7898,
  temperature: 28.4,
  humidity: 78,
  rainfallProbability: 35,
  leafWetnessHours: 4.5,
  soilType: 'Loamy',
  cropStage: 'Flowering',
  irrigationType: 'Drip',
};

const INITIAL_SAMPLE_HISTORY: HistoryItem[] = [
  {
    id: 'scan-1726201001',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
    imageUrl: 'https://images.unsplash.com/photo-1592417817098-8f3d6ef23997?auto=format&fit=crop&w=400&q=80',
    plantName: 'Tomato',
    scientificName: 'Solanum lycopersicum',
    isHealthy: false,
    diseaseName: 'Early Blight (Alternaria solani)',
    confidence: 0.985,
    tier: 1,
    tierLabel: 'Confident Diagnosis',
    whyItHappens: {
      pathogen: 'Alternaria solani (Soil-borne fungus)',
      favorableConditions: 'High humidity (>75%), warm temperatures (24-29°C), and rain splash carrying spores from soil to lower foliage.',
      biology: 'Produces distinct dark brown to black spots with concentric rings ("bullseye" pattern), surrounded by chlorotic yellow halos on older leaves.',
    },
    remedies: {
      organic: [
        'Apply cold-pressed Neem Oil spray (5ml neem oil + 2ml liquid soap per 1 liter water) every 5 days.',
        'Incorporate bio-fungicide Trichoderma viride into the root zone to suppress fungal inoculum.'
      ],
      chemical: [
        'Spray Copper Oxychloride 50% WP @ 2.5g/L water during early infection stages.',
        'If severe, alternate with Mancozeb 75% WP @ 2g/L (wait period: 10 days before harvest).'
      ],
      cultural: [
        'Prune and destroy all lower leaves within 15 cm of the soil surface.',
        'Transition from sprinkler to drip irrigation to keep leaf canopies dry.',
        'Apply 5cm organic straw mulch to stop water splashing soil spores onto leaves.'
      ]
    },
    environmentalAdvice: 'High humidity (78%) in your field accelerates spore germination. Avoid overhead irrigation and apply preventive bio-spray within 24 hours.',
    environmentalSnapshot: {
      location: 'Nashik District, Maharashtra',
      temperature: 28.4,
      humidity: 78,
      soilType: 'Loamy'
    },
    notes: 'Noticed small circular brown spots on bottom row of 2nd tomato bed.'
  },
  {
    id: 'scan-1726101002',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 26).toISOString(), // Yesterday
    imageUrl: 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?auto=format&fit=crop&w=400&q=80',
    plantName: 'Corn (Maize)',
    scientificName: 'Zea mays',
    isHealthy: false,
    diseaseName: 'Common Rust (Puccinia sorghi)',
    confidence: 0.992,
    tier: 1,
    tierLabel: 'Confident Diagnosis',
    whyItHappens: {
      pathogen: 'Puccinia sorghi (Airborne rust fungus)',
      favorableConditions: 'Moderate temperatures (16-25°C) combined with high relative humidity and dew durations over 6 hours.',
      biology: 'Pustules erupt on both upper and lower leaf surfaces, releasing golden-brown powdery spores that disrupt photosynthesis.'
    },
    remedies: {
      organic: [
        'Foliar spray of 1% baking soda + horticultural oil solution to elevate leaf surface pH.',
        'Spray fermented butter-milk (Chaach) diluted 1:10 with water as a natural anti-fungal barrier.'
      ],
      chemical: [
        'Apply Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1ml/L water at first sign of rust pustules.',
        'Tilt (Propiconazole 25% EC) @ 1ml/L water if pustules cover >5% of upper leaf area.'
      ],
      cultural: [
        'Maintain optimal plant spacing (60cm × 20cm) to ensure wind penetration through rows.',
        'Plant certified rust-resistant corn hybrid seeds next cropping cycle.'
      ]
    },
    environmentalAdvice: 'Favorable rust temperature range (22-26°C). Morning dew is prolonging canopy wetness.',
    environmentalSnapshot: {
      location: 'Pune Rural, Maharashtra',
      temperature: 24.1,
      humidity: 84,
      soilType: 'Black Cotton'
    },
    notes: 'Checked North parcel corn crop. Pustules concentrated on mid-canopy leaves.'
  }
];

export const loadScanHistory = (): HistoryItem[] => {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(INITIAL_SAMPLE_HISTORY));
      return INITIAL_SAMPLE_HISTORY;
    }
    return JSON.parse(raw);
  } catch {
    return INITIAL_SAMPLE_HISTORY;
  }
};

export const saveScanToHistory = (item: HistoryItem): void => {
  try {
    const current = loadScanHistory();
    const updated = [item, ...current.filter((i) => i.id !== item.id)];
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
  } catch (e) {
    console.error('Error saving history item', e);
  }
};

export const deleteScanFromHistory = (id: string): HistoryItem[] => {
  try {
    const current = loadScanHistory();
    const updated = current.filter((item) => item.id !== id);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
    return updated;
  } catch {
    return [];
  }
};

export const clearAllHistory = (): void => {
  try {
    localStorage.removeItem(HISTORY_KEY);
  } catch (e) {
    console.error('Error clearing history', e);
  }
};

export const loadSettings = (): AppSettings => {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    const settings: AppSettings = raw ? { ...DEFAULT_SETTINGS, ...JSON.parse(raw) } : { ...DEFAULT_SETTINGS };
    if (typeof window !== 'undefined' && window.location.hostname && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
      if (settings.backendUrl.includes('127.0.0.1') || settings.backendUrl.includes('localhost')) {
        settings.backendUrl = `http://${window.location.hostname}:8000`;
      }
    }
    return settings;
  } catch {
    return DEFAULT_SETTINGS;
  }
};

export const saveSettings = (settings: AppSettings): void => {
  try {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
  } catch (e) {
    console.error('Error saving settings', e);
  }
};

export const loadEnvContext = (): EnvironmentalContext => {
  try {
    const raw = localStorage.getItem(ENV_KEY);
    if (!raw) return DEFAULT_ENV;
    return { ...DEFAULT_ENV, ...JSON.parse(raw) };
  } catch {
    return DEFAULT_ENV;
  }
};

export const saveEnvContext = (env: EnvironmentalContext): void => {
  try {
    localStorage.setItem(ENV_KEY, JSON.stringify(env));
  } catch (e) {
    console.error('Error saving env context', e);
  }
};
