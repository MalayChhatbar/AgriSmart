"""
Gemini Vision Adapter
Uses Google's Generative AI API (Gemini) to perform crop disease prediction visually.
"""
import os
import json
from typing import Optional
from model_engine.base import BaseModelAdapter, ModelPrediction

class GeminiVisionAdapter(BaseModelAdapter):
    def predict(self, image_path: str, crop_hint: Optional[str] = None) -> ModelPrediction:
        try:
            import google.generativeai as genai
        except ImportError:
            return self._fallback_error("google-generativeai package not installed")

        # Try to read settings from db.database manually or via env
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            import sqlite3
            db_path = "data/agrismart.db"
            try:
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    c = conn.cursor()
                    c.execute("SELECT value FROM settings WHERE key='gemini_api_key' OR key='nvidia_api_key' AND value LIKE 'AIza%'")
                    row = c.fetchone()
                    if row and row[0] and row[0].startswith("AIza"):
                        api_key = row[0]
                    conn.close()
            except Exception:
                pass
                
        if not api_key:
            return self._fallback_error("No Gemini API key found. Add it in Settings.")

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            with open(image_path, "rb") as img_file:
                image_data = img_file.read()
            
            image_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": image_data
                }
            ]
            
            prompt = (
                "You are an expert plant pathologist. Analyze this leaf image. "
                "Output ONLY a valid JSON object with EXACTLY these fields (no markdown, no backticks):\n"
                '{"plant": "Name of the crop (e.g. Tomato, Apple, Corn)", "disease": "Name of the disease (or healthy)", "confidence": 0.95}'
            )
            
            response = model.generate_content([prompt, image_parts[0]])
            text = response.text.strip()
            
            # Remove markdown JSON fences if present
            if text.startswith("```"):
                text = text.split('\n', 1)[1]
            if text.endswith("```"):
                text = text.rsplit('\n', 1)[0]
            if text.startswith("json"):
                text = text[4:]
                
            data = json.loads(text.strip())
            
            plant = data.get("plant", crop_hint or "Unknown")
            disease = data.get("disease", "Unknown")
            conf = float(data.get("confidence", 0.9))
            
            is_healthy = "health" in disease.lower() or "normal" in disease.lower()
            tier = 1 if conf > 0.6 else 2
            
            formatted_disease = disease.replace(" ", "_")
            if "___" not in formatted_disease and not is_healthy:
                formatted_disease = f"{plant}___{formatted_disease}"
            
            return ModelPrediction(
                plant=plant,
                disease=formatted_disease if not is_healthy else f"{plant}___healthy",
                confidence=conf,
                status="confident" if conf > 0.6 else "uncertain",
                tier=tier,
                common_name=f"{plant} - {disease}",
                top_candidates=[{"disease": formatted_disease, "plant": plant, "common_name": disease, "confidence": conf}],
                crop_guided=bool(crop_hint),
                adapter_source="gemini_vision"
            )
            
        except Exception as e:
            return self._fallback_error(f"Gemini API Error: {str(e)}")

    def _fallback_error(self, msg: str):
        print(f"[GeminiVisionAdapter] {msg}")
        return ModelPrediction(
            plant="Unknown",
            disease="Unknown",
            confidence=0.0,
            status="unclear",
            tier=3,
            common_name=msg,
            adapter_source="gemini_vision",
            raw_info={"error": msg}
        )
