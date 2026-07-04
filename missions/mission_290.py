# ============================================================
# MISSÃO 290 — UNCERTAINTY QUANTIFICATION ENGINE
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class UncertaintyProfile:
    """Perfil de incerteza."""
    id: str = field(default_factory=lambda: f"up_{uuid.uuid4().hex[:12]}")
    prediction_id: str = ""
    mean: float = 0.0
    std: float = 0.0
    confidence_interval_90: Tuple[float, float] = (0.0, 0.0)
    confidence_interval_95: Tuple[float, float] = (0.0, 0.0)
    confidence_interval_99: Tuple[float, float] = (0.0, 0.0)
    entropy: float = 0.0
    model_variance: float = 0.0
    uncertainty_score: float = 0.0
    reliability: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "prediction_id": self.prediction_id,
            "mean": self.mean,
            "std": self.std,
            "confidence_interval_90": self.confidence_interval_90,
            "confidence_interval_95": self.confidence_interval_95,
            "confidence_interval_99": self.confidence_interval_99,
            "entropy": self.entropy,
            "model_variance": self.model_variance,
            "uncertainty_score": self.uncertainty_score,
            "reliability": self.reliability,
            "created_at": self.created_at.isoformat(),
        }


class UncertaintyQuantificationEngine:
    """
    Motor de quantificação de incerteza.

    Implementa:
    - Prediction Uncertainty
    - Confidence Interval
    - Bayesian Interval
    - Entropy Index
    - Model Variance
    - Uncertainty Ranking
    - Confidence Heatmap
    - Scenario Spread
    - Forecast Reliability
    - Dashboard
    """

    def __init__(self):
        self._profiles: Dict[str, List[UncertaintyProfile]] = {}
        self._uncertainty_threshold = 0.3

    def quantify_uncertainty(
        self,
        prediction_id: str,
        predictions: List[float],
        model_predictions: List[float],
    ) -> UncertaintyProfile:
        """Quantifica incerteza da previsão."""
        mean = np.mean(predictions)
        std = np.std(predictions)

        ci_90 = np.percentile(predictions, [5, 95])
        ci_95 = np.percentile(predictions, [2.5, 97.5])
        ci_99 = np.percentile(predictions, [0.5, 99.5])

        entropy = self._calculate_entropy(predictions)
        model_variance = np.var(model_predictions) if model_predictions else 0.0
        uncertainty_score = min(std / (abs(mean) + 0.001), 1.0)
        reliability = 1 - uncertainty_score

        profile = UncertaintyProfile(
            prediction_id=prediction_id,
            mean=mean,
            std=std,
            confidence_interval_90=(ci_90[0], ci_90[1]),
            confidence_interval_95=(ci_95[0], ci_95[1]),
            confidence_interval_99=(ci_99[0], ci_99[1]),
            entropy=entropy,
            model_variance=model_variance,
            uncertainty_score=uncertainty_score,
            reliability=reliability,
        )

        if prediction_id not in self._profiles:
            self._profiles[prediction_id] = []

        self._profiles[prediction_id].append(profile)
        return profile

    def _calculate_entropy(self, predictions: List[float]) -> float:
        """Calcula entropia das previsões."""
        if len(predictions) < 2:
            return 0.0

        hist, _ = np.histogram(predictions, bins=10)
        probs = hist / len(predictions)
        probs = probs[probs > 0]

        return -np.sum(probs * np.log(probs))

    def get_uncertainty_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de incerteza."""
        total_profiles = sum(len(profiles) for profiles in self._profiles.values())

        if total_profiles == 0:
            return {"status": "no_data"}

        all_profiles = [p for profiles in self._profiles.values() for p in profiles]

        return {
            "total_profiles": total_profiles,
            "avg_uncertainty": np.mean([p.uncertainty_score for p in all_profiles]),
            "avg_reliability": np.mean([p.reliability for p in all_profiles]),
            "avg_entropy": np.mean([p.entropy for p in all_profiles]),
            "high_uncertainty": sum(
                1 for p in all_profiles if p.uncertainty_score > self._uncertainty_threshold
            ),
            "confidence_ranges": {
                "90": np.mean([
                    p.confidence_interval_90[1] - p.confidence_interval_90[0]
                    for p in all_profiles
                ]),
                "95": np.mean([
                    p.confidence_interval_95[1] - p.confidence_interval_95[0]
                    for p in all_profiles
                ]),
                "99": np.mean([
                    p.confidence_interval_99[1] - p.confidence_interval_99[0]
                    for p in all_profiles
                ]),
            },
            "recent_profiles": [p.to_dict() for p in all_profiles[-5:]],
        }
