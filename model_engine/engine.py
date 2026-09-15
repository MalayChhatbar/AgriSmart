import os
from typing import Optional
from model_engine.base import BaseModelAdapter, ModelPrediction
from model_engine.config import ACTIVE_ADAPTER

_cached_adapter: Optional[BaseModelAdapter] = None

def get_model_engine() -> BaseModelAdapter:
    """
    Factory function returning the active model adapter.
    Configure in model_engine/config.py (ACTIVE_ADAPTER = 'default' or 'teammate')
    """
    global _cached_adapter
    if _cached_adapter is not None:
        return _cached_adapter

    adapter_name = ACTIVE_ADAPTER.lower().strip()
    if adapter_name == "huggingface":
        try:
            import gradio_client
            print("[ModelEngine] Loading HuggingFaceModelAdapter...")
            from model_engine.hf_adapter import HuggingFaceModelAdapter
            _cached_adapter = HuggingFaceModelAdapter()
        except ImportError:
            print("[ModelEngine] gradio_client not installed; using DefaultModelAdapter (/model)...")
            from model_engine.default_adapter import DefaultModelAdapter
            _cached_adapter = DefaultModelAdapter()
    elif adapter_name == "teammate":
        print("[ModelEngine] Loading TeammateModelAdapter...")
        from model_engine.teammate_adapter import TeammateModelAdapter
        _cached_adapter = TeammateModelAdapter()
    else:
        print("[ModelEngine] Loading DefaultModelAdapter (Calibrated Dual-Model)...")
        from model_engine.default_adapter import DefaultModelAdapter
        _cached_adapter = DefaultModelAdapter()

    return _cached_adapter


def predict_crop_disease(image_path: str, crop_hint: Optional[str] = None) -> ModelPrediction:
    """
    Unified entry point for disease prediction across the entire backend.
    """
    engine = get_model_engine()
    return engine.predict(image_path, crop_hint=crop_hint)
