# AgriSmart AI — Crop Disease Detection (SIH 2026 Problem Statement 1)

**Internal Hackathon — L.J. Institute | `dev/malay` branch (strict SIH layout)**

Core: **Crop Disease Detection (CV)** — classify leaf image into 38 PlantVillage classes (28 shared with PlantDoc). Reports honest field metrics on PlantDoc TEST 236 images. Optional bonus modules are stubbed for future Android app; this branch focuses on reproducible core + judge tooling.

## 1) What we built
- **Core (mandatory):** `convnext_small.fb_in22k_ft_in1k` (timm), 2-phase PV→PV+PlantDoc field, 4-view TTA, restricted to 28 shared classes. Primary metric **Macro-F1 0.7412 / Acc 0.75** on held-out field TEST. See `report/model_report.md`.
- **Bonus:** stub APIs `/api/recommend-crop`, `/api/irrigation-advice`, etc. in `app/app.py` (lightweight, no keys). Full agentic/IoT will ship in Android later.
- **Tooling for judges (separate, uv-based):**
  - **CLI** `cli/app.py` (`agrismart predict --image/--dir --offline --json`) — `typer+rich`, ONNX Runtime → HF → heuristic
  - **Gradio** `gradio_app/app.py` — Core tab (upload → top-3 + confidence + advice) + Metrics tab (confusion matrix, per-class report, model report). Theme from your oklch tokens (primary #5B21B6, secondary #0E9F8A, accent #F59E0B, no JS).

## 2) Setup & Run (judge must reproduce in <10 min)

**Option A — uv (recommended):**
```bash
git clone https://github.com/yuvrajgitacc/agrismart -b dev/malay
cd agrismart
uv sync
uv run python model/predict.py --image model/sample_leaf.jpg
# → Potato___Late_blight
uv run agrismart predict --image model/sample_leaf.jpg --offline
uv run python gradio_app/app.py  # → http://localhost:7860
```

**Option B — pip:**
```bash
pip install -r requirements.txt
python model/predict.py --image model/sample_leaf.jpg
python gradio_app/app.py
```

Weights auto-download from HF Space `DakshBhavsar007/agrismart-crop-disease` (`repo_type="space"`) on first run (cached `~/.cache/huggingface/hub`). Use `--offline` to force local/heuristic. No manual steps — satisfies Section 4.1 `predict(image_path) -> label` + `python model/predict.py --image path` printing class.

**ONNX note:** Local `model.onnx` is stale (previous training export); heuristic fallback ensures reproducibility now. Replace `model/model.onnx` + `model/model.onnx.data` after retrain.

## 3) Dataset & Licence
- **PlantVillage** (lab, Mohanty et al. 2016) + **PlantDoc** TRAIN field split for training; **PlantDoc TEST 236** held-out never trained on (Section 4.1). 54k-scale, citation in `report/model_report.md`. Extra public data (Plant Pathology 2021 apple) optional. No leakage.

## 4) Reported metrics (every model)
- **Field TEST (restricted+TTA, 28 classes, 236 imgs):** Macro-F1 **0.7412**, Acc 0.75, Top-3 0.966, ECE 0.05 — `report/disease_metrics.json`, `report/confusion_matrix.png`, `report/per_class_report.txt` (`Corn Cercospora 0.167 weakest`, `Squash/Strawberry 1.0 strongest`).
- Lab val F1 0.9978 (optimistic), selection field-val 0.797.

## 5) Architecture & Limitations
- Backbone `convnext_small`, 2-phase oversample×3, AdamW+OneCycle, MixUp/CutMix+EMA, background replace 0.9 + field-photo sim 0.75, TTA 4 views, Temp 1.0, mask -1e4 for non-shared. Honest failure: lab→field drop, rare classes (n≤4) fragile, leaf gate 0.04 + low-conf 0.55 are heuristics, stale ONNX pending replacement — see Cell2 calibration/self-training/RL for next gains.

## 6) Demo & Deploy
- Video: **TBD** (3–5 min showing core on new field image)
- HF Space: https://huggingface.co/spaces/DakshBhavsar007/agrismart-crop-disease
- API: `uvicorn app.app:app --host 0.0.0.0 --port 8000` → `/docs`

## Repository structure (Section 7.1 strict)
```
/README.md
/app/          # FastAPI minimal
/model/        # predict.py + meta.json + advice.json + sample_leaf.jpg + weights/README
/report/       # model_report.md + disease_metrics.json + confusion_matrix.png + per_class_report.txt
/gradio_app/   # judge Gradio (separate)
/cli/          # judge CLI (separate, uv)
/requirements.txt / pyproject.toml / .python-version
```

**Originality:** Pretrained backbone + custom field augmentation; training code `cell1_train_agrismart (1).py` / `cell2_posttrain_rl_improve.py` gitignored locally (`D:\SIH\Agrismart\model\cell*.py`).

- GitHub may strip `*.pt/*.onnx` — weights live on HF Space (see `model/weights/README.md`).
