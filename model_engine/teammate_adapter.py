"""
================================================================================
  TEAMMATE MODEL ADAPTER (PLUG & PLAY)
================================================================================
  How to use:
  1. Save your trained ONNX model to: `model_engine/weights/teammate_model.onnx`
     (Or PyTorch model, TorchScript, etc.)
  2. Put your class label mapping in: `model_engine/labels.json`
  3. In `model_engine/config.py`, change:
        ACTIVE_ADAPTER = "teammate"
  4. Done! The entire AgriSmart backend, SQLite database, OpenWeather context,
     and NVIDIA AI agent will automatically use your model!
================================================================================
"""

import os
import json
import numpy as np
from PIL import Image
from typing import Optional, Dict, Any, List
from model_engine.base import BaseModelAdapter, ModelPrediction
from model_engine.config import TEAMMATE_MODEL_PATH, TEAMMATE_LABELS_PATH

try:
    import onnxruntime as ort
except ImportError:
    ort = None

class TeammateModelAdapter(BaseModelAdapter):
    def __init__(self, model_path: str = TEAMMATE_MODEL_PATH, labels_path: str = TEAMMATE_LABELS_PATH):
        self.model_path = model_path
        self.labels_path = labels_path
        self.session = None
        self.labels = {}
        self._load_labels()
        self._init_session()

    def _load_labels(self):
        if os.path.exists(self.labels_path):
            with open(self.labels_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Supports either list ["Apple___scab", ...] or dict {"0": "Apple___scab"}
                if isinstance(data, list):
                    self.labels = {str(i): name for i, name in enumerate(data)}
                else:
                    self.labels = {str(k): v for k, v in data.items()}
        else:
            # Fallback placeholder labels
            self.labels = {
                "0": "Potato___Late_blight",
                "1": "Tomato___Early_blight",
                "2": "Apple___Apple_scab",
            }

    def _init_session(self):
        if not os.path.exists(self.model_path):
            print(f"[TeammateModelAdapter] Notice: Model file not yet found at '{self.model_path}'.")
            print("[TeammateModelAdapter] Please drop your model file there. Fallback mock will be used until then.")
            return

        if ort is None:
            print("[TeammateModelAdapter] Warning: onnxruntime not installed.")
            return

        try:
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
            self.session = ort.InferenceSession(self.model_path, providers=providers)
            print(f"[TeammateModelAdapter] ONNX session loaded successfully from {self.model_path}")
        except Exception as e:
            print(f"[TeammateModelAdapter] Error initializing ONNX session: {e}")
            self.session = None

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Standard image preprocessing for computer vision models.
        Modify this method if your model expects a different size or normalization!
        Default: 224x224, Normalized with ImageNet mean/std, (1, 3, 224, 224) float32.
        """
        img = Image.open(image_path).convert("RGB")
        img = img.resize((224, 224), Image.Resampling.BILINEAR)
        img_np = np.array(img).astype(np.float32) / 255.0

        # Standard ImageNet normalization: (x - mean) / std
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        img_np = (img_np - mean) / std

        # Transpose HWC -> CHW and add batch dim -> NCHW: (1, 3, 224, 224)
        tensor = np.transpose(img_np, (2, 0, 1))
        tensor = np.expand_dims(tensor, axis=0)
        return tensor

    def predict(self, image_path: str, crop_hint: Optional[str] = None) -> ModelPrediction:
        """
        Execute prediction on the provided image path.
        """
        # If your ONNX model is loaded, run real inference:
        if self.session is not None:
            try:
                input_name = self.session.get_inputs()[0].name
                tensor = self.preprocess_image(image_path)
                outputs = self.session.run(None, {input_name: tensor})
                logits = outputs[0][0]

                # Softmax
                exp_logits = np.exp(logits - np.max(logits))
                probs = exp_logits / np.sum(exp_logits)

                top_idx = int(np.argmax(probs))
                top_prob = float(probs[top_idx])
                raw_label = self.labels.get(str(top_idx), f"Class_{top_idx}")

                # Extract plant name and disease name from label (e.g. 'Potato___Late_blight')
                if "___" in raw_label:
                    plant_name, disease_name = raw_label.split("___", 1)
                else:
                    plant_name = crop_hint or "Plant"
                    disease_name = raw_label

                # Top 3 candidates
                sorted_indices = np.argsort(probs)[::-1][:3]
                candidates = []
                for idx in sorted_indices:
                    label_str = self.labels.get(str(idx), f"Class_{idx}")
                    p_name = label_str.split("___")[0] if "___" in label_str else plant_name
                    d_name = label_str.split("___")[1] if "___" in label_str else label_str
                    candidates.append({
                        "plant": p_name,
                        "disease": label_str,
                        "common_name": f"{p_name} - {d_name.replace('_', ' ')}",
                        "confidence": round(float(probs[idx]) * 100, 2)
                    })

                tier = 1 if top_prob >= 0.50 else 2
                status = "confident" if tier == 1 else "uncertain"

                return ModelPrediction(
                    plant=crop_hint if crop_hint else plant_name,
                    disease=raw_label,
                    confidence=top_prob,
                    status=status,
                    tier=tier,
                    common_name=f"{plant_name} - {disease_name.replace('_', ' ')}",
                    top_candidates=candidates,
                    crop_guided=crop_hint is not None,
                )
            except Exception as e:
                print(f"[TeammateModelAdapter] Inference failed: {e}. Falling back to sample.")

        # Fallback simulation if model file is not yet dropped in:
        return ModelPrediction(
            plant=crop_hint or "Potato",
            disease="Potato___Late_blight",
            confidence=0.942,
            status="confident",
            tier=1,
            common_name="Potato - Late Blight",
            top_candidates=[
                {"disease": "Potato___Late_blight", "common_name": "Potato - Late Blight", "confidence": 94.2},
                {"disease": "Potato___Early_blight", "common_name": "Potato - Early Blight", "confidence": 4.1},
                {"disease": "Potato___healthy", "common_name": "Potato - Healthy", "confidence": 1.7},
            ],
            crop_guided=crop_hint is not None,
            adapter_source="teammate"
        )

    def is_ready(self) -> bool:
        return self.session is not None

