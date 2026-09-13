# AgriSmart AI — Intelligent Agriculture Platform

[![SIH-2026](https://img.shields.io/badge/SIH--2026-Problem%20Statement%201-15803d?style=for-the-badge)](https://github.com/)
[![Macro-F1](https://img.shields.io/badge/Macro--F1-0.9904-brightgreen?style=for-the-badge)](report/model_report.md)
[![Model](https://img.shields.io/badge/Architecture-Dual--Model%20Cascade-blue?style=for-the-badge)](model/)

> **AgriSmart AI** is a dual-model, computer-vision driven precision agriculture platform designed for smallholder farmers and agricultural stakeholders. It solves the real-world domain gap in crop disease detection using **Confidence-Aware Masking**, **Temperature-Scaled Calibration**, **Test-Time Augmentation (TTA)**, and an end-to-end farm management suite covering smart irrigation, crop recommendation, weather risk intelligence, and bilingual farmer advisory.

---

## 1. Modules Built (Core + Bonus)

### Mandatory Core Task
* **Crop Disease Detection (Computer Vision):** Two-model cascade (Crop Validator + 38-class Disease Diagnostician) on EfficientNet-B0 backbones. Delivers 3-tier risk-calibrated responses (Confident, Differential Top-3, and Signs Unclear) with organic and chemical remedies.

### Optional Bonus Modules Implemented (All 7 Built & Functional)
* **Bonus Module A: Crop Recommendation Engine:** Multi-parameter tabular ML model (Random Forest, 99%+ accuracy) evaluating Nitrogen (N), Phosphorus (P), Potassium (K), Soil pH, Temperature, Humidity, and Rainfall to recommend optimal crops.
* **Bonus Module B: Smart Irrigation Advisory:** FAO-56 Penman-Monteith inspired soil moisture depletion model that calculates crop-stage specific water demand ($K_c$) and adjusts pumping schedules against 24-hour precipitation forecasts.
* **Bonus Module C: Weather-Based Disease Intelligence:** Microclimate fungal/bacterial spore germination risk index based on ambient temperature, relative humidity, and canopy leaf wetness duration.
* **Bonus Module D: Farm Sustainability Scorecard:** Reproducible 0–100 index quantifying water conservation, chemical pesticide reduction, and soil organic matter with estimated seasonal $CO_2$ emissions averted.
* **Bonus Module E: Bilingual Kisan AI Assistant:** Natural language farmer advisory interface providing grounded recommendations in English and Hindi for organic recipes (neem oil), fertilizer balance, and pest control.
* **Bonus Module F: Simulated IoT Sensor Telemetry:** Real-time physical parameter streaming (soil moisture, temperature, humidity, pH, NPK, battery status) simulating an ESP32 edge deployment.
* **Bonus Module G: Autonomous Agentic Decision Loop:** Multi-variable conflict resolver that autonomously arbitrates between sensor readings, forecasts, and disease alerts (e.g. overriding irrigation when rainfall is imminent to prevent root rot).

---

## 2. Setup & Reproduction Guide (< 10 Minutes)

Judges can reproduce a graded prediction in under 2 minutes using standard Python 3.10+:

### Step 1: Clone and Install Dependencies
```bash
git clone https://github.com/your-org/agrismart-ai.git
cd agrismart-ai
pip install -r requirements.txt
```

### Step 2: Run Graded Single Prediction CLI (Section 4.1 Compliance)
To run the official single-label prediction on any test image:
```bash
python model/predict.py --image data/val/Apple___Apple_scab/01a66316-0e98-4d3b-a56f-d78752cd043f___FREC_Scab\ 3003.JPG
```
**Output:**
```
Apple___Apple_scab
```

### Step 3: Run Full Evaluation on Held-Out Validation Split
To verify our reported Macro-F1 (0.9904) and confusion matrix from scratch:
```bash
python model/evaluate.py
```

### Step 4: Launch Web Dashboard & Interactive Platform
```bash
uvicorn app.app:app --host 0.0.0.0 --port 8000
```
Open your browser at: **[http://localhost:8000](http://localhost:8000)**.

---

## 3. Datasets Used & Sources / Licences

| Dataset | Role / Purpose | Source / Citation | License |
|---|---|---|---|
| **PlantVillage** | Core Training & Validation (~54,000 images, 38 classes) | [Mohanty et al., 2016](https://github.com/spMohanty/PlantVillage-Dataset) / Hugging Face `mohanty/PlantVillage` | CC BY-SA 4.0 |
| **Negative `no_leaf` Set** | Non-plant negative class (hands, soil, backgrounds) | Procedurally curated & synthesized (750 samples) | MIT |
| **PlantDoc & Field Samples** | Development robustness check for field domain gap | [Kayal et al., 2019](https://github.com/pratikkayal/PlantDoc-Dataset) | Academic Use |
| **Crop Recommendation Data** | Bonus A: Soil & climate tabular recommendation | [Ingle, 2020](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) | CC0: Public Domain |

*Note: In strict compliance with the hackathon rules, all development robustness checks are kept distinct from the organizers' official held-out field test set.*

---

## 4. Reported Metrics & Validation Results

### Primary Graded Core Metric (Model 2: 38 Disease Classes on Held-Out Validation Set)
Evaluated on **10,876 unseen validation images**:
* **Macro-Averaged F1:** **0.9904 (99.04%)** *(Primary ranking metric)*
* **Top-1 Accuracy:** **0.9938 (99.38%)**
* **Weighted F1:** **0.9939 (99.39%)**
* **Macro-Precision:** **0.9890 (98.90%)**
* **Macro-Recall:** **0.9923 (99.23%)**

### Model 1 Metric (Crop Classifier — 15 Classes: 14 Crops + `no_leaf`)
* **Validation Macro-F1:** **0.9858 (98.58%)**
* **Validation Accuracy:** **0.9851 (98.51%)**

Detailed per-class precision/recall and confusion matrix tables are documented in [`report/model_report.md`](report/model_report.md) and [`report/disease_metrics.json`](report/disease_metrics.json).

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
                                     • Tier 1: Confident Diagnosis
                                     • Tier 2: Differential Top-3
                                     • Tier 3: Signs Unclear
```

### Key Engineering Features
1. **Confidence-Aware Soft Masking:** Restricts Model 2 to the candidate diseases of the predicted crop, completely eliminating impossible cross-species errors (e.g. Apple scab on a Tomato leaf). Soft-masking widens the candidate pool if two crops share botanical similarity.
2. **Temperature Scaling ($T = 0.9761$):** Fitted on validation set using L-BFGS to eliminate overconfident predictions.
3. **Test-Time Augmentation (TTA):** Averages predictions over original, flipped, and zoom-cropped inputs to prevent sensitivity to lighting and camera angle.

### Known Limitations
* **Extreme Occlusion:** Leaves covered by more than 70% mud or severe camera blur will trigger Tier 3 ("Signs Unclear") prompting the farmer to take a clearer photo.
* **Closed-Set Crop Scope:** Identifies diseases on 14 supported agricultural crop families. Unsupported wild plants (e.g. houseplants) are cleanly rejected rather than guessed.

---

## 6. Demonstration Video & Live Links

* **3–5 Minute Walkthrough Video (Section 7.4):** [YouTube Unlisted Demo Link](https://youtu.be/example-agrismart-demo) *(Placeholder)*
* **Interactive Live API & Dashboard:** `http://localhost:8000` (Local deployment active)
* **API Documentation:** `http://localhost:8000/docs` (Interactive Swagger OpenAPI)

---

## Originality Declaration
We hereby declare that all core pipeline components, dual-model cascaded masking architecture, training workflows, calibration scripts, and advisory engines were authored for this challenge. Pretrained EfficientNet-B0 backbones and public datasets were sourced and cited as per Section 8 of the challenge guidelines.
