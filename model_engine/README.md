# Teammate Model Integration Guide (Plug-and-Play)

Welcome! This directory is designed so that you can drop in your trained computer vision model with **zero changes needed to the rest of the backend, database, or API**.

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Save your Model & Labels
1. Put your ONNX model file here:
   `model_engine/weights/teammate_model.onnx`
2. Put your class labels mapping JSON here:
   `model_engine/labels.json`
   *(Can be a list `["Apple___scab", ...]` or a dictionary `{"0": "Apple___scab", ...}`)*

### Step 2: Activate Your Model
Open [`model_engine/config.py`](file:///c:/Users/YUVRAJ/Downloads/agismart/model_engine/config.py) and change:
```python
ACTIVE_ADAPTER = "teammate"  # Changed from "default"
```

### Step 3: Test It!
Run this command from the project root:
```bash
python -c "from model_engine.engine import predict_crop_disease; print(predict_crop_disease('data/val/Apple___Apple_scab/00075aa8-d81a-4e84-a423-f3636c7463e1___FREC_Scabs 3335.JPG'))"
```

---

## 🛠️ Custom Preprocessing or PyTorch?
If your model requires custom preprocessing (e.g. 256x256, grayscale, or specific normalization) or you want to use PyTorch instead of ONNX:
- Open [`model_engine/teammate_adapter.py`](file:///c:/Users/YUVRAJ/Downloads/agismart/model_engine/teammate_adapter.py)
- Edit `preprocess_image()` or `predict()` directly.
- The output just needs to return a `ModelPrediction(plant=..., disease=..., confidence=...)`.

---

## 🌟 What Happens Next?
Once your model predicts `{ plant, disease, confidence }`:
1. The backend automatically fetches **Live Weather** (temperature, rainfall forecast) from OpenWeather.
2. The farmer's **NVIDIA / DeepSeek AI API Key** automatically generates:
   - Biological cause and pathogen overview
   - Desi / Organic natural remedies
   - Chemical remedies with exact mixing dilution (e.g. 2g per liter)
   - Preventive field management tips
3. The report is saved to the **SQLite database** (`agismart.db`) and delivered to the mobile app!
