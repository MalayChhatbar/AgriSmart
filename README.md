# AgriSmart AI

### Intelligent crop-disease detection — built for the field, not just the lab

[![SIH 2026](https://img.shields.io/badge/SIH-2026%20Internal%20Hackathon-blue)](https://github.com/yuvrajgitacc/agrismart)
[![Branch](https://img.shields.io/badge/branch-dev%2Fmalay-5B21B6)](https://github.com/yuvrajgitacc/agrismart/tree/dev/malay)
[![Python](https://img.shields.io/badge/python-3.11+-3776AB)](https://www.python.org)
[![ONNX Runtime](https://img.shields.io/badge/inference-ONNX%20Runtime-0E9F8A)](https://onnxruntime.ai)
[![HF Space](https://img.shields.io/badge/HF%20Space-agrismart--crop--disease-F59E0B)](https://huggingface.co/spaces/DakshBhavsar007/agrismart-crop-disease)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Farmers don't photograph leaves in a lab. They photograph them in dust, glare, shadow and wind. AgriSmart is a crop-disease detector designed for that reality — trained on clean lab images, tested on real field photos, and honest about where it still fails.

> **SIH 2026 — Problem Statement 1 · LJ Institute (C-433)** · Core task is mandatory, bonus modules are optional. This branch (`dev/malay`) is a **strict, reproducible core** plus two standalone tools for judges to test — a `uv`-based CLI and a themed Gradio app. The full Android app ships next.

---

## What it does

**Core — Crop Disease Detection**
- 38 PlantVillage classes (28 shared with PlantDoc field data) — e.g. `Tomato___Early_blight`, `Potato___Late_blight`, plus healthy.
- Backbone `convnext_small.fb_in22k_ft_in1k` (timm), 2-phase training: PlantVillage pre-train → PlantVillage + PlantDoc field fine-tune (field oversampled ×3).
- Field-photography augmentation at 75%: shadow, blur, noise, JPEG, white-balance, low-res — so the model survives phone photos.
- 4-view TTA + shared-class restriction. Reported on **held-out PlantDoc TEST (236 images, 27 classes)** — never trained on, never used for checkpoint selection.

**Honest numbers, not lab numbers**

| Split | Macro-F1 | Accuracy | Notes |
|---|---:|---:|---|
| **Field TEST** (restricted+TTA) | **0.7412** | 0.7500 | Primary ranking metric · `report/confusion_matrix.png` |
| Field TEST top-3 / ECE | 0.9661 / 0.05 | — | `report/per_class_report.txt` |
| Lab val | 0.9978 | — | Optimistic lab gap — see limitations |
| Selection (field-val) | 0.7975 | — | `model/meta.json` |

Weakest: `Corn Cercospora 0.167 (n=4)`, `Tomato Bacterial Spot 0.308` · Strongest: `Squash Powdery Mildew 1.0`, `Strawberry healthy 1.0`. Full per-class table in `report/per_class_report.txt` and `report/disease_metrics.json`.

**Bonus stubs** — lightweight FastAPI endpoints (`/api/recommend-crop`, `/api/irrigation-advice`, `/api/weather-risk`, `/api/sustainability-score`, `/api/iot-telemetry`, `/api/agentic-cycle`, `/api/chat`) backed by `app/services/` heuristics. No API keys required. The real agentic/IoT loop lands in the Android build.

---

## How it runs

```mermaid
flowchart LR
    A[Leaf Photo] --> B[Preprocess\n224· Resize + CenterCrop\nNormalize]
    B --> C{Engine}
    C -->|ONNX local| D[model.onnx\n+ model.onnx.data]
    C -->|miss| E[HF Space\nDakshBhavsar007/agrismart-crop-disease]
    C -->|offline/torch| F[model_weights.pt\ntimm]
    C -->|fallback| G[Heuristic\nsample_leaf guard]
    D & E & F & G --> H[Logits / T=1.0\nmask -1e4 non-shared]
    H --> I[Softmax avg 4 views]
    I --> J[Top-3 + Advice\nadvice.json]
    J --> K[CLI / Gradio / FastAPI]
```

```mermaid
graph TD
    subgraph Training
        PV[PlantVillage 54k lab] --> P1[Phase 1: PV only 6 epochs]
        PD[PlantDoc TRAIN field] --> P2[Phase 2: PV+field 10 epochs\noversample x3]
        P1 --> P2 --> TTA[TTA-4 + Restriction]
        TTA --> EVAL[PlantDoc TEST 236 held-out]
    end
    subgraph Inference
        EVAL -.-> META[meta.json\n38 classes, 28 allowed]
        META --> ONNX
    end
```

Weights are **not** committed to GitHub (100 MB limit). They live on HF Space and are fetched once via `huggingface_hub` (cached at `~/.cache/huggingface/hub`). Current `model.onnx` is a stale export from the previous run — the code warns and falls back cleanly; replace both `model.onnx` + `model.onnx.data` after retraining.

---

## Quick start — under 10 minutes

### `uv` (recommended)

```bash
git clone https://github.com/yuvrajgitacc/agrismart -b dev/malay
cd agrismart
uv sync

# core — SIH §4.1 interface, prints bare label
uv run python model/predict.py --image model/sample_leaf.jpg
# → Potato___Late_blight

# more detail
uv run python model/predict.py --image model/sample_leaf.jpg --verbose
uv run python model/predict.py --image model/sample_leaf.jpg --json

# judge CLI (single + batch + offline)
uv run agrismart predict --image model/sample_leaf.jpg --offline
uv run agrismart predict --dir ./images --out predictions.csv

# Gradio — Core + Metrics
uv run python gradio_app/app.py
# → http://localhost:7860

# FastAPI
uv run uvicorn app.app:app --host 0.0.0.0 --port 8000
# → http://localhost:8000/docs
```

### `pip`

```bash
pip install -r requirements.txt
python model/predict.py --image model/sample_leaf.jpg
python gradio_app/app.py
```

> `python -c "from model.predict import predict; print(predict('model/sample_leaf.jpg'))"` also works — same label, same engine.

---

## Using the tools

**CLI**

```bash
# single image, restricted to 28 shared classes (default)
agrismart predict --image leaf.jpg --topk 3

# all 38 classes, no HF download
agrismart predict --image leaf.jpg --all-classes --offline --json

# batch a folder, write CSV for judges
agrismart predict --dir data/field_photos --topk 3 --out report.csv
agrismart info  # model, classes, HF id, metrics
```

**Gradio**

- **Detect** — upload a leaf, pick `Top-K` and `restrict`, hit Diagnose → top-3 label/confidence bars + precaution (`advice.json`) + raw JSON. Try the seeded example `model/sample_leaf.jpg → Potato___Late_blight`.
- **Metrics & Report** — field macro-F1, accuracy, top-3, ECE, confusion matrix, per-class table and the one-page `report/model_report.md`. Styled from your oklch palette (`primary #5B21B6`, `secondary #0E9F8A`, `accent #F59E0B`, no JS).

**API**

`POST /api/predict` with `file` (image) and optional `crop_hint`. Returns `{plant, disease, confidence, tier, isHealthy, top3, advice}`. Other bonus routes return sensible stubs without keys — see `app/app.py`.

---

## Project structure

This branch follows SIH §7.1 strictly — only what judges need to reproduce the core.

```
.
├── app/                # FastAPI minimal — /api/predict + bonus stubs, no DB
│   ├── services/       # advisory + crop recommendation heuristics
│   └── static/index.html
├── model/              # SIH §4.1 predict interface + artifacts
│   ├── predict.py      # ONNX → HF Space → torch → heuristic, TTA-4, predict()
│   ├── classes.py      # synced to meta.json (spaces in labels preserved)
│   ├── meta.json       # 38 classes, 28 allowed, metrics, temp, thresholds
│   ├── advice.json     # 38 precautions (farmer-facing)
│   ├── sample_leaf.jpg # test fixture → Potato___Late_blight
│   └── weights/README.md  # HF download instructions
├── report/             # §7.3 one-page + metrics
│   ├── model_report.md
│   ├── disease_metrics.json
│   ├── confusion_matrix.png
│   ├── confusion_matrix_plain.png
│   └── per_class_report.txt
├── cli/                # judge CLI — typer + rich, standalone
├── gradio_app/         # judge Gradio — Detect + Metrics, themed
├── requirements.txt    # ONNX Runtime minimal (torch optional)
├── pyproject.toml      # uv + `agrismart` console script
└── test_sih_compliance.py  # 5 checks — structure, predict, metrics, bonus, FastAPI
```

Training code (`cell1_train_agrismart (1).py`, `cell2_posttrain_rl_improve.py`) is gitignored and lives locally at `D:\SIH\Agrismart\model\` — not needed to reproduce inference.

---

## Dataset & training notes

- **Sources:** PlantVillage (lab) + PlantDoc TRAIN (field). **PlantDoc TEST 236** is held-out, never trained on. ~54k scale. Citations in `report/model_report.md`.
- **Model:** `convnext_small.fb_in22k_ft_in1k`, AdamW + OneCycle, MixUp/CutMix + EMA, label smooth 0.1, background replacement 0.9.
- **Limitations (honest):** lab→field gap persists (0.997→0.741), rare classes (n≤4) fragile, leaf-fraction gate 0.04 and low-conf 0.55 are heuristics, stale ONNX pending replacement. Cell 2 adds calibration, self-training and RL-tuned CLIP ensemble that further close the gap.

---

## Hosting & reproducibility

- **HF Space:** https://huggingface.co/spaces/DakshBhavsar007/agrismart-crop-disease — `model_weights.pt` (198 MB) today; add `model.onnx` + `model.onnx.data` together next export (`*.onnx` is already LFS-tracked in `.gitattributes`).
- **Manual fetch:** `huggingface-cli download DakshBhavsar007/agrismart-crop-disease --repo-type space --local-dir model model.onnx model.onnx.data meta.json advice.json`
- **Compliance:** `python test_sih_compliance.py` must pass structure, `predict()` vs CLI label equality, field F1 gate 0.70, bonus stubs and FastAPI. Full verification in one command.

---

## Roadmap

- Replace stale ONNX + add JIT for Android TorchScript
- Full agentic advisor (weather + soil + stage) + IoT ESP32 stream + regional-language GenAI — in the Android app (separate milestone, not this branch)

---

## License & originality

MIT — see `LICENSE`. Pretrained backbone + custom field augmentation; no wholesale notebook copy. Commit history is the proof of work (Sept 10–15 window per §8).

*Built with care for farmers who photograph leaves in the real world.*
