export interface DiagnosisResult {
  id: string;
  timestamp: string;
  imageUrl: string;
  plantName: string;
  scientificName?: string;
  isHealthy: boolean;
  diseaseName: string;
  confidence: number;
  tier: 1 | 2 | 3;
  tierLabel: string;
  whyItHappens: {
    pathogen: string;
    favorableConditions: string;
    biology: string;
  };
  remedies: {
    organic: string[];
    chemical: string[];
    cultural: string[];
  };
  environmentalAdvice?: string;
  top3Candidates?: Array<{
    disease: string;
    commonName: string;
    confidence: number;
  }>;
}

export interface EnvironmentalContext {
  location: string;
  latitude?: number;
  longitude?: number;
  temperature: number;
  humidity: number;
  rainfallProbability: number;
  leafWetnessHours: number;
  soilType: 'Loamy' | 'Clayey' | 'Sandy' | 'Black Cotton' | 'Red Laterite' | 'Alluvial';
  cropStage: 'Seedling' | 'Vegetative' | 'Flowering' | 'Fruiting' | 'Harvest';
  irrigationType: 'Drip' | 'Sprinkler' | 'Furrow' | 'Rainfed';
}

export interface HistoryItem extends DiagnosisResult {
  environmentalSnapshot?: {
    location: string;
    temperature: number;
    humidity: number;
    soilType: string;
  };
  notes?: string;
}

export interface AppSettings {
  geminiApiKey: string;
  openaiApiKey: string;
  weatherApiKey: string;
  nvidiaApiKey?: string;
  aiModel?: string;
  backendUrl: string;
  farmerName: string;
  farmLocation: string;
  primaryCrop: string;
  defaultSoil: string;
  language: 'en' | 'hi' | 'gu' | 'mr' | 'pa';
  darkMode: boolean;
  voiceGuidance: boolean;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  textHi?: string;
  timestamp: string;
  category?: 'remedy' | 'fertilizer' | 'weather' | 'general';
}
