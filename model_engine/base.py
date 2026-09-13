from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class DiagnosisCandidate:
    disease: str
    common_name: str
    confidence: float

@dataclass
class ModelPrediction:
    plant: str
    disease: str
    confidence: float
    status: str = "confident"  # "confident" | "uncertain" | "unclear" | "no_leaf" | "unsupported_plant"
    tier: int = 1              # 1 = Confident, 2 = Differential, 3 = Unclear
    common_name: str = ""
    top_candidates: List[Dict[str, Any]] = field(default_factory=list)
    crop_guided: bool = False
    adapter_source: str = "default"
    raw_info: Optional[Dict[str, Any]] = None

    @property
    def is_healthy(self) -> bool:
        return "healthy" in self.disease.lower() or "normal" in self.disease.lower()

    @property
    def tier_label(self) -> str:
        if self.tier == 1:
            return "Confident Diagnosis"
        elif self.tier == 2:
            return "Differential Top-3 Triage"
        return "Signs Unclear"

    @property
    def top3(self) -> List[Dict[str, Any]]:
        return self.top_candidates

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "tier": self.tier,
            "tier_label": self.tier_label,
            "is_healthy": self.is_healthy,
            "plant": self.plant,
            "disease": self.disease,
            "confidence": round(self.confidence, 4),
            "common_name": self.common_name or f"{self.plant} - {self.disease.split('___')[-1].replace('_', ' ')}",
            "crop_guided": self.crop_guided,
            "adapter_source": self.adapter_source,
            "top3": self.top_candidates,
            "likely_candidates": self.top_candidates if self.tier > 1 else None,
        }

class BaseModelAdapter(ABC):
    """
    Abstract Base Class for Crop Disease Detection Models.
    Any model built by any team member only needs to inherit from this
    and implement the `predict` method returning a `ModelPrediction`.
    """
    @abstractmethod
    def predict(self, image_path: str, crop_hint: Optional[str] = None) -> ModelPrediction:
        """
        Execute inference on an image file path.
        :param image_path: Absolute or relative path to the image.
        :param crop_hint: Optional crop name (e.g. 'Potato', 'Apple') if provided by farmer.
        :return: ModelPrediction object with plant, disease, confidence, and candidates.
        """
        pass

    def is_ready(self) -> bool:
        """Returns True if model weights are loaded and ready for inference."""
        return True
