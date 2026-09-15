"""
AgriSmart AI - predict_rich wrapper
Provides backward-compatible export for model_engine/default_adapter.py
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from model.predict import predict_rich, predict
except ImportError:
    from predict import predict_rich, predict

__all__ = ["predict_rich", "predict"]
