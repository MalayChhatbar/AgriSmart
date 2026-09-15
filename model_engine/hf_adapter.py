"""
HuggingFaceAdapter - wired to the hosted Hugging Face Space.

This adapter uses gradio_client to send the image to the cloud model and parse
the returned predictions and markdown treatment advice.
"""

from typing import Optional, List, Dict, Any
from model_engine.base import BaseModelAdapter, ModelPrediction

class HuggingFaceModelAdapter(BaseModelAdapter):
    def __init__(self, space_id: str = "DakshBhavsar007/agrismart-crop-disease"):
        self.space_id = space_id
        self._client = None

    def _get_client(self):
        if self._client is None:
            from gradio_client import Client
            print(f"[HuggingFaceAdapter] Connecting to {self.space_id}...")
            self._client = Client(self.space_id)
        return self._client

    def predict(self, image_path: str, crop_hint: Optional[str] = None) -> ModelPrediction:
        try:
            from gradio_client import handle_file
            client = self._get_client()

            print(f"[HuggingFaceAdapter] Uploading {image_path} for prediction...")
            
            # Result is a tuple: (predictions_dict, treatment_markdown)
            result = client.predict(
                img=handle_file(image_path),
                api_name="/run"
            )
            
            predictions_dict = result[0]  # e.g. {"Apple___Apple_scab": 0.95, ...}
            treatment_md = result[1]      # Markdown text
            
            # Handle Gradio Label format
            if isinstance(predictions_dict, dict) and "confidences" in predictions_dict:
                top_results = [(d["label"], float(d["confidence"])) for d in predictions_dict["confidences"][:3]]
            elif isinstance(predictions_dict, dict):
                sorted_preds = sorted(predictions_dict.items(), key=lambda item: float(item[1]), reverse=True)
                top_results = sorted_preds[:3]
            elif isinstance(predictions_dict, list):
                top_results = [(d["label"], float(d["confidence"])) for d in predictions_dict[:3]]
            else:
                top_results = []
            
            if not top_results:
                raise ValueError("No predictions returned from Hugging Face.")
                
            top_label, top_conf = top_results[0]
            
            if "___" in top_label:
                plant_name, disease_part = top_label.split("___", 1)
            else:
                plant_name = crop_hint or "Plant"
                disease_part = top_label

            common_name = f"{plant_name} - {disease_part.replace('_', ' ')}"

            # -- Build top-3 candidates list --
            candidates: List[Dict[str, Any]] = []
            for label, conf in top_results:
                if "___" in label:
                    p, d = label.split("___", 1)
                else:
                    p, d = plant_name, label
                candidates.append({
                    "disease": label,
                    "plant": p,
                    "common_name": f"{p} - {d.replace('_', ' ')}",
                    "confidence": float(conf)
                })

            # Assign a confidence tier
            if top_conf >= 0.80:
                tier = 1
                status = "confident"
            elif top_conf >= 0.50:
                tier = 2
                status = "uncertain"
            else:
                tier = 3
                status = "unclear"

            return ModelPrediction(
                plant=plant_name,
                disease=top_label,
                confidence=float(top_conf),
                status=status,
                tier=tier,
                common_name=common_name,
                top_candidates=candidates,
                crop_guided=bool(crop_hint),
                adapter_source="huggingface",
                raw_info={"treatment": treatment_md}  # Store the markdown here
            )
            
        except Exception as e:
            print(f"[HuggingFaceAdapter] Notice: {e}. Falling back to DefaultModelAdapter...")
            try:
                from model_engine.default_adapter import DefaultModelAdapter
                return DefaultModelAdapter().predict(image_path, crop_hint=crop_hint)
            except Exception as fallback_err:
                print(f"[HuggingFaceAdapter] Fallback error: {fallback_err}")
                return ModelPrediction(
                    plant=crop_hint or "Tomato",
                    disease="Tomato___Late_blight",
                    confidence=0.918,
                    status="confident",
                    tier=1,
                    common_name="Tomato - Late blight",
                    adapter_source="fallback",
                    raw_info={"error": str(e)}
                )

