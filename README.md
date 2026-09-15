# AgriSmart AI — Intelligent Agriculture Platform

[![SIH-2026](https://img.shields.io/badge/SIH--2026-Problem%20Statement%201-15803d?style=for-the-badge)](https://github.com/)
[![Macro-F1](https://img.shields.io/badge/Macro--F1-0.9904-brightgreen?style=for-the-badge)](report/model_report.md)
[![Model](https://img.shields.io/badge/Architecture-Dual--Model%20Cascade-blue?style=for-the-badge)](model/)
[![License](https://img.shields.io/badge/License-MIT-orange?style=for-the-badge)](LICENSE)

> **AgriSmart AI** is an AI-powered crop-disease detection and smart-agriculture advisory platform built for the **Smart India Hackathon (SIH 2026 Internal Hackathon — Problem Statement 1)**. It classifies plant diseases from leaf photographs, reports its accuracy on held-out test data, presents results with organic and chemical remedies, and provides an end-to-end advisory suite covering crop recommendation, smart irrigation, weather risk, sustainability scoring, IoT sensor telemetry, and bilingual farmer chat.

---

## 1. Modules Built (Core Task + All 7 Bonus Modules)

### Mandatory Core Task (Section 3.1)
* **Crop Disease Detection (Computer Vision):** Classifies foliage photographs across 38 crop-disease classes (and "healthy" states) covering 14 crops. Surfaces predicted disease, confidence percentage, confidence tier (Confident, Differential Top-3, Signs Unclear), pathogen cause, organic remedies (e.g. cold-pressed neem oil), chemical remedy dilution ratios, and weather-aware spray advisories.

### Optional Bonus Modules Built (Section 3.2 — All 7 Built & Functional)
* **Bonus Module A — Crop Recommendation:** Multi-parameter Random Forest model (`app/services/crop_recommendation.py`) evaluating soil Nitrogen, Phosphorus, Potassium, pH, Temperature, Humidity, and Rainfall to recommend optimal crops (`POST /api/recommend-crop`).
* **Bonus Module B — Smart Irrigation Advisory:** FAO-56 Penman-Monteith inspired soil moisture depletion engine (`app/services/advisory.py`) calculating crop-stage evapotranspiration ($K_c$) and adjusting watering advice against 24-hour rainfall forecasts (`POST /api/irrigation-advice`).
* **Bonus Module C — Weather-Based Disease Intelligence:** Computes fungal and bacterial spore germination risk score from ambient temperature, humidity, and rainfall duration (`app/services/advisory.py`, `services/weather.py`), paired with real-time weather data (`GET /api/weather`, `POST /api/weather-risk`).
* **Bonus Module D — Sustainability Scorecard:** Transparent, reproducible $0\text{--}100$ scoring formula ($0.35W + 0.30C + 0.20S + 0.15M$) quantifying water efficiency, chemical pesticide reduction, soil organic matter, and estimated seasonal $\text{CO}_2$ emissions saved (`POST /api/sustainability-score`).
* **Bonus Module E — Farmer Assistant (GenAI):** Conversational advisory assistant (`services/agent.py`) with tool-calling capabilities and grounded bilingual (English + Hindi) fallback guidance (`POST /api/chat`).
* **Bonus Module F — IoT Sensor Integration:** Real-time physical parameter streaming (`app/services/advisory.py`) simulating an ESP32 edge node reporting soil moisture, temperature, humidity, pH, N-P-K, and battery voltage (`GET /api/iot-telemetry`).
* **Bonus Module G — Autonomous Agentic Advisor:** Autonomous decision cycle (`app/services/advisory.py`) resolving multi-variable conflicts (e.g. holding automated irrigation when rain is imminent to prevent root rot) (`POST /api/agentic-cycle`).

---

## 2. Setup & Run Instructions (< 10 Minutes Reproduction)

Judges can reproduce predictions and verify all requirements in under 2 minutes:

### Step 1: Clone Repository & Install Dependencies
```bash
git clone https://github.com/yuvrajgitacc/agrismart.git
cd agrismart
pip install -r requirements.txt
```

### Step 2: Run Graded Prediction CLI (Section 4.1 Compliance)
Run the prediction CLI on the bundled sample test leaf (`model/sample_leaf.jpg`):
```bash
python model/predict.py --image model/sample_leaf.jpg
```
**Terminal Output:**
```
Potato___Late_blight
```

*For detailed diagnostics including confidence and differential top-3 candidates:*
```bash
python model/predict.py --image model/sample_leaf.jpg --verbose
```

*Python API Interface:*
```python
from model.predict import predict
result = predict("model/sample_leaf.jpg")
print(result)  # "Potato___Late_blight"
```

### Step 3: Run Full Evaluation on Held-Out Test Set (Section 4.2)
Compute Macro-Averaged F1, Top-1 Accuracy, and per-class metrics:
```bash
python model/evaluate.py
```
*(Prints classification metrics table and exports [`report/disease_metrics.json`](report/disease_metrics.json)).*

### Step 4: Run Training Pipeline Demo (Section 3.1)
Run a quick transfer learning dry-run with data augmentations:
```bash
python model/train.py --demo
```

### Step 5: Launch Web Platform & Backend
```bash
uvicorn app.app:app --host 0.0.0.0 --port 8000
```
* **Main Web App:** Open [http://localhost:8000](http://localhost:8000) (Serves the compiled React app from `frontend/dist`).
* **Standalone Dashboard:** Open [http://localhost:8000/dashboard](http://localhost:8000/dashboard) (Single-file HTML dashboard).
* **Interactive API Docs:** Open [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger OpenAPI schema).

### Step 6: Run Full Automated Verification Suite
Verify all Section 7.1 structure requirements, Section 4.1 CLI, metrics, and all 7 bonus modules in one command:
```bash
python test_sih_compliance.py
```

---

## 3. Datasets Used & Sources / Licences

| Dataset | Role / Purpose | Scale / Split | Source / Citation | License |
|---|---|---|---|---|
| **PlantVillage** | Core Training & Validation | 54,306 images across 38 classes (70/15/15 split) | [Mohanty et al., 2016](https://github.com/spMohanty/PlantVillage-Dataset) | CC BY-SA 4.0 |
| **PlantDoc** | Development Field Robustness Reference | 2,598 field photos with natural lighting & clutter | [Kayal et al., 2019](https://github.com/pratikkayal/PlantDoc-Dataset) | Academic Use |
| **Crop Recommendation** | Bonus Module A Training | 2,200 multi-parameter soil & climate records | [Ingle, 2020](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) | CC0: Public Domain |

*Data Compliance: As mandated by Section 4.1 and Section 8, the organizers' held-out field test set was never trained on.*

---

## 4. Reported Metrics (Core Task)

Evaluated across **38 classes** on **10,761 unseen held-out validation images**:

| Metric | Score | Percentage | Notes |
|---|---|---|---|
| **Macro-Averaged F1** | **0.9904** | **99.04%** | **Primary Ranking Metric (Section 4.2)** |
| **Top-1 Accuracy** | **0.9925** | **99.25%** | Overall correct diagnoses |
| **Weighted F1** | **0.9907** | **99.07%** | Frequency-weighted F1 |
| **Macro-Precision** | **0.9888** | **98.88%** | Precision averaged across 38 classes |
| **Macro-Recall** | **0.9924** | **99.24%** | Sensitivity averaged across 38 classes |

### Comparison Against Standard Baseline
| Model Pipeline | Backbone | Macro-F1 | Top-1 Accuracy | Real-Field Behavior |
|---|---|---|---|---|
| **Standard Baseline** | ResNet-50 (Vanilla Softmax) | 0.8920 | 0.9015 | Prone to cross-species misclassifications |
| **AgriSmart AI (Ours)** | **Dual EfficientNet-B0 + Masking** | **0.9904** | **0.9925** | **Eliminates cross-species errors (+0.0984 Macro-F1)** |

Full 38-class metrics table, per-class precision/recall, and confusion matrix are in [`report/model_report.md`](report/model_report.md) and [`report/disease_metrics.json`](report/disease_metrics.json).

---

## 5. Architecture Overview & Known Limitations

```
                      [Input Leaf Image]
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
        [Model 1: Crop Class]         [Model 2: Disease Class]
       (EfficientNet-B0, 15 cls)     (EfficientNet-B0, 38 cls)
                │                             │
    ┌───────────┴───────────┐                 │
    ▼                       ▼                 │
[no_leaf?]          [Conf < 0.35?]            │
(Reject non-plant)  (Reject unsupported)      │
    │                       │                 │
    └───────────┬───────────┘                 │
                │ Valid crop                  │
                ▼                             ▼
        [Candidate Masking] ──────────► [Apply Mask & Softmax]
        (Soft-mask if top-2                     │
         crops within 15%)                      ▼
                                      [Calibrated 3-Tier Output]
                                      • Tier 1: Confident Diagnosis (>75%)
                                      • Tier 2: Differential Top-3 (50-75%)
                                      • Tier 3: Signs Unclear (<50%)
```

### Key Engineering Features
1. **Candidate Masking:** Constrains disease predictions to biologically plausible candidates for the detected crop family.
2. **Temperature Scaling ($T = 0.9761$):** Calibrated using L-BFGS to prevent overconfident probabilities.
3. **Multi-Engine Fallback:** Dynamically loads ONNX runtime (`teammate_model.onnx`), cloud Hugging Face Space (`DakshBhavsar007/agrismart-crop-disease`), or local calibrated feature engine so predictions never crash.
4. **Offline Agronomic Knowledge Base:** Built-in biological, organic, and chemical remedy guidelines available even without external AI API keys.

### Known Limitations
* **Severe Leaf Occlusion:** If over 70% of the leaf surface is covered in mud, soil, or physical tears, confidence drops below 50% and triggers Tier 3 ("Signs Unclear"), advising the farmer to photograph a cleaner leaf.
* **Crop Family Scope:** Calibrated for 14 primary agricultural crops. Non-agricultural plants and weeds are rejected by the validator.

---

## 6. Demonstration Video & Deployed Links

* **Walkthrough Video (Section 7.4):** [YouTube Unlisted Demo](https://youtu.be/agrismart-demo-sih2026) *(3–5 minute demonstration)*
* **Local Web Application:** `http://localhost:8000`
* **Standalone Dashboard:** `http://localhost:8000/dashboard`
* **API Documentation:** `http://localhost:8000/docs`
* **Hosted Hugging Face Model:** [DakshBhavsar007/agrismart-crop-disease](https://huggingface.co/spaces/DakshBhavsar007/agrismart-crop-disease)

---

## 7. Submission Repository Structure (Section 7.1 Contract)

```
agrismart/
├── README.md                  # Entry point & reproduction guide (Section 7.2)
├── requirements.txt           # Unified dependency specifications
├── pyproject.toml             # Project metadata & build settings
├── LICENSE                    # MIT License
├── SECURITY.md                # Security policy & reporting guidelines
├── CONTRIBUTING.md            # Contribution guidelines & workflow
├── test_sih_compliance.py     # Automated compliance test suite
│
├── model/                     # Mandatory Model Directory (Section 7.1)
│   ├── predict.py             # predict() function & CLI (Section 4.1)
│   ├── predict_rich.py        # Diagnostic rich prediction bridge
│   ├── evaluate.py            # Evaluation & metrics generation (Section 4.2)
│   ├── train.py               # Transfer learning training pipeline (Section 3.1)
│   ├── classes.py             # 38-class labels & botanical parsers
│   ├── labels.json            # Machine-readable class definitions
│   ├── sample_leaf.jpg        # Bundled sample leaf image (Potato___Late_blight)
│   └── weights/               # Local checkpoint directory (.gitkeep)
│
├── report/                    # Mandatory Report Directory (Section 7.1)
│   ├── model_report.md        # One-page model report (Section 7.3)
│   └── disease_metrics.json   # Per-class metrics & 38x38 confusion matrix
│
├── app/                       # Application Backend (Section 7.1)
│   ├── app.py                 # FastAPI backend server
│   ├── static/index.html      # Standalone single-file dashboard
│   └── services/
│       ├── crop_recommendation.py  # Bonus A: Random Forest (99.3%)
│       └── advisory.py             # Bonus B, C, D, E, F, G logic
│
├── model_engine/              # Model Adapter Layer
│   ├── engine.py              # Dynamic adapter resolver
│   ├── default_adapter.py     # Local /model bridge
│   ├── hf_adapter.py          # Hugging Face Space cloud adapter
│   └── teammate_adapter.py    # ONNX runtime custom model adapter
│
├── services/                  # External Service Integrations
│   ├── agent.py               # Tool-calling AI agent & remedy database
│   └── weather.py             # OpenWeatherMap & Open-Meteo live weather
│
├── db/                        # SQLite Persistence
│   └── database.py            # Async SQLite storage for profile, scans, & chat
│
└── frontend/                  # React + Vite + Capacitor Web & Mobile App
    └── dist/                  # Pre-built production bundle (zero-node setup)
```

---

## 8. Originality & Timeframe Declaration (Section 8)

* **Hackathon Timeframe:** All substantive development, model integration, adapter engineering, and platform features were authored during the **10 – 15 September** hackathon window.
* **Original Work Declaration:** The dual-model cascaded masking architecture, multi-tier confidence calibration, FAO-56 irrigation logic, weather risk scoring, sustainability index, and autonomous decision loop were designed and authored for this challenge.
* **Third-Party Open-Source Attribution:**
  * EfficientNet-B0 backbone weights initialized from ImageNet via PyTorch / torchvision.
  * PlantVillage dataset ([Mohanty et al., 2016](https://github.com/spMohanty/PlantVillage-Dataset)) used under CC BY-SA 4.0.
  * PlantDoc dataset ([Kayal et al., 2019](https://github.com/pratikkayal/PlantDoc-Dataset)) used for field domain gap reference.
  * Crop recommendation dataset ([Ingle, 2020](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset)) used under CC0: Public Domain.
  * Open-Meteo API used for zero-key geocoding and live meteorological data.
