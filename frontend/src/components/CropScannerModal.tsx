import React, { useState, useRef } from 'react';
import {
  X,
  Upload,
  Camera,
  CheckCircle2,
  Sparkles,
  RefreshCw,
  Image as ImageIcon,
} from 'lucide-react';
import { samplePresetImages } from '../services/api';

interface CropScannerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onScanComplete: (fileOrBlob: File | Blob, previewUrl: string, presetKey?: string, cropHint?: string) => Promise<void>;
  isScanning: boolean;
}

export const CropScannerModal: React.FC<CropScannerModalProps> = ({
  isOpen,
  onClose,
  onScanComplete,
  isScanning,
}) => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | Blob | null>(null);
  const [selectedPresetKey, setSelectedPresetKey] = useState<string | undefined>(undefined);
  const [selectedCropHint, setSelectedCropHint] = useState<string>('auto');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const galleryInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setSelectedPresetKey(undefined);
      const url = URL.createObjectURL(file);
      setSelectedImage(url);
    }
  };

  const handleSelectPreset = async (preset: (typeof samplePresetImages)[0]) => {
    setSelectedPresetKey(preset.key);
    setSelectedImage(preset.url);

    // Create a mock blob from sample
    try {
      const response = await fetch(preset.url);
      const blob = await response.blob();
      setSelectedFile(blob);
    } catch {
      setSelectedFile(new Blob(['mock-leaf'], { type: 'image/jpeg' }));
    }
  };

  const handleStartScan = async () => {
    if (!selectedImage || !selectedFile) return;
    await onScanComplete(selectedFile, selectedImage, selectedPresetKey, selectedCropHint);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-card w-full max-w-md rounded-3xl border border-border overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-4 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-primary/20 flex items-center justify-center text-primary">
              <Camera className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-base text-foreground">Crop Disease Scanner</h3>
              <p className="text-xs text-muted-foreground">Upload or choose sample leaf</p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={isScanning}
            className="p-1.5 rounded-full hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-4 overflow-y-auto space-y-4">
          {/* Crop Family Selector (AI Auto-Detect or Manual Guidance) */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-foreground flex items-center justify-between">
              <span>Target Crop Family</span>
              <span className="text-[11px] text-muted-foreground font-normal">Optional Guidance</span>
            </label>
            <select
              value={selectedCropHint}
              onChange={(e) => setSelectedCropHint(e.target.value)}
              disabled={isScanning}
              className="w-full text-xs bg-secondary/80 border border-border rounded-xl px-3 py-2.5 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 cursor-pointer transition-all"
            >
              <option value="auto">🌱 Auto-Detect Crop (AI Neural Network)</option>
              <option value="Potato">🥔 Potato (आलू)</option>
              <option value="Tomato">🍅 Tomato (टमाटर)</option>
              <option value="Apple">🍎 Apple (सेब)</option>
              <option value="Corn">🌽 Corn / Maize (मक्का)</option>
              <option value="Grape">🍇 Grape (अंगूर)</option>
              <option value="Pepper_bell">🫑 Bell Pepper / Shimla Mirch (शिमला मिर्च)</option>
              <option value="Peach">🍑 Peach (आड़ू)</option>
              <option value="Cherry">🍒 Cherry (चेरी)</option>
              <option value="Strawberry">🍓 Strawberry (स्ट्रॉबेरी)</option>
              <option value="Squash">🎃 Squash / Kaddu (कद्दू)</option>
              <option value="Soybean">🌱 Soybean (सोयाबीन)</option>
              <option value="Orange">🍊 Orange / Citrus (संतरा)</option>
              <option value="Blueberry">🫐 Blueberry</option>
              <option value="Raspberry">🍇 Raspberry</option>
            </select>
          </div>

          {/* Main Preview / Upload Box */}
          <div className="relative rounded-2xl overflow-hidden border-2 border-dashed border-border bg-secondary/40 min-h-[200px] flex flex-col items-center justify-center text-center p-4 transition-all">
            {selectedImage ? (
              <div className="relative w-full h-56 rounded-xl overflow-hidden group">
                <img
                  src={selectedImage}
                  alt="Selected Leaf"
                  className="w-full h-full object-cover rounded-xl"
                />

                {/* Laser Scanning Animation Overlay */}
                {isScanning && (
                  <div className="absolute inset-0 bg-primary/10 flex flex-col justify-between p-4 pointer-events-none">
                    {/* Bounding box corners */}
                    <div className="w-full h-full border-2 border-primary rounded-lg relative overflow-hidden">
                      {/* Laser scanning line */}
                      <div className="w-full h-1 bg-gradient-to-r from-transparent via-primary to-transparent shadow-[0_0_15px_#10b981] animate-bounce" />
                    </div>
                  </div>
                )}

                {/* Change photo button */}
                {!isScanning && (
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="absolute bottom-2 right-2 px-3 py-1.5 bg-black/60 hover:bg-black/80 backdrop-blur-md text-white rounded-xl text-xs font-semibold border border-white/20 transition-all cursor-pointer flex items-center gap-1"
                  >
                    <Upload className="w-3 h-3" />
                    Change
                  </button>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center p-6 w-full h-full gap-3">
                <div className="w-14 h-14 rounded-2xl bg-primary/15 text-primary flex items-center justify-center mb-1 shadow-inner">
                  <Upload className="w-7 h-7" />
                </div>
                <h4 className="font-bold text-sm text-foreground">Scan a Leaf</h4>
                <p className="text-xs text-muted-foreground max-w-[240px]">
                  Take a clear photo or choose from your gallery
                </p>
                <div className="flex gap-3 mt-1 w-full">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="flex-1 flex flex-col items-center gap-1.5 py-3 px-3 rounded-xl border-2 border-primary/30 bg-primary/10 hover:bg-primary/20 text-primary font-semibold text-xs transition-all cursor-pointer"
                  >
                    <Camera className="w-5 h-5" />
                    <span>Take Photo</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => galleryInputRef.current?.click()}
                    className="flex-1 flex flex-col items-center gap-1.5 py-3 px-3 rounded-xl border-2 border-border bg-secondary/60 hover:bg-secondary text-foreground font-semibold text-xs transition-all cursor-pointer"
                  >
                    <Upload className="w-5 h-5" />
                    <span>Browse Gallery</span>
                  </button>
                </div>
              </div>
            )}

            {/* Camera input (opens camera directly on mobile) */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleFileChange}
              className="hidden"
            />
            {/* Gallery input (opens file picker / photo gallery) */}
            <input
              ref={galleryInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />
          </div>


        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-border bg-card flex gap-2.5">
          <button
            type="button"
            onClick={onClose}
            disabled={isScanning}
            className="flex-1 py-3 px-4 rounded-xl border border-border text-foreground font-semibold text-xs hover:bg-secondary transition-all cursor-pointer disabled:opacity-50"
          >
            Cancel
          </button>

          <button
            type="button"
            onClick={handleStartScan}
            disabled={!selectedImage || isScanning}
            className="flex-2 py-3 px-4 rounded-xl bg-primary text-primary-foreground font-bold text-xs shadow-md hover:brightness-105 active:scale-98 transition-all cursor-pointer flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isScanning ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Analyzing Disease Features...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Diagnose Plant Now</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
