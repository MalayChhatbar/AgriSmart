import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────────────────────────────────────
# MODEL ENGINE CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
# Options:
#   - "default"  : Active dual-model pipeline (EfficientNet-B0 calibrated engine)
#   - "teammate" : Custom model built by your teammate (ONNX or custom loader)
ACTIVE_ADAPTER = os.getenv("AGRI_ACTIVE_ADAPTER", "huggingface")

# Paths for Teammate Model (Drop files into model_engine/weights/ and set here)
TEAMMATE_MODEL_PATH = os.path.join(BASE_DIR, "weights", "teammate_model.onnx")
TEAMMATE_ONNX_PATH = TEAMMATE_MODEL_PATH
TEAMMATE_LABELS_PATH = os.path.join(BASE_DIR, "labels.json")

# Inference hardware priority: "cuda" -> "directml" -> "cpu"
PREFERRED_DEVICE = os.getenv("AGRI_INFERENCE_DEVICE", "auto")
