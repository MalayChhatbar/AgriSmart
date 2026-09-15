"""
HuggingFaceAdapter - wired to the hosted Hugging Face Space.
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
            self._client = Client(self.space_id, token="")
        return self._client

    def predict(self, image_path: str, crop_hint: Optional[str] = None) -> ModelPrediction:
        from gradio_client import handle_file
        
        try:
            client = self._get_client()
            print(f"[HuggingFaceAdapter] Uploading {image_path} for prediction...")
            
            result = client.predict(
                img=handle_file(image_path),
                api_name="/run"
            )
            
            raw_predictions = result[0]
            treatment_md = result[1]
            
            # --- Parse the response ---
            # Format: {'label': 'X___Y', 'confidences': [{'label': '...', 'confidence': 0.xx}, ...]}
            if isinstance(raw_predictions, dict) and 'confidences' in raw_predictions:
                confidences_list = raw_predictions['confidences']
                top_results = [(c['label'], c['confidence']) for c in confidences_list[:3]]
            elif isinstance(raw_predictions, dict):
                # Old format: {disease_name: confidence_float, ...}
                sorted_preds = sorted(raw_predictions.items(), key=lambda item: item[1], reverse=True)
                top_results = sorted_preds[:3]
            else:
                raise ValueError(f"Unexpected predictions format: {type(raw_predictions)}")
            
            if not top_results:
                raise ValueError("No predictions returned from Hugging Face.")
                
            top_label, top_conf = top_results[0]
            
            if "___" in top_label:
                plant_name, disease_part = top_label.split("___", 1)
            else:
                plant_name = crop_hint or "Plant"
                disease_part = top_label

            common_name = f"{plant_name} - {disease_part.replace('_', ' ')}"
            
            print(f"[HuggingFaceAdapter] Detected: {common_name} ({top_conf:.1%})")

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
                raw_info={"treatment": treatment_md}
            )
            
        except Exception as e:
            print(f"[HuggingFaceAdapter] Prediction failed: {e}")
            self._client = None  # Reset client for next retry
            return ModelPrediction(
                plant=crop_hint or "Unknown",
                disease="Unknown",
                confidence=0.0,
                status="unclear",
                tier=3,
                common_name="Error reaching prediction API",
                adapter_source="huggingface",
                raw_info={"error": str(e)}
            )
