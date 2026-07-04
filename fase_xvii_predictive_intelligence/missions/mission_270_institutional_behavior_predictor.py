# ============================================================
# MISSÃO 270 — INSTITUTIONAL BEHAVIOR PREDICTOR
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class InstitutionalPrediction:
    """Previsão de comportamento institucional."""
    id: str = field(default_factory=lambda: f"ip_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    predicted_action: str = ""
    confidence: float = 0.0
    time_horizon_hours: int = 24
    accumulation_prob: float = 0.0
    distribution_prob: float = 0.0
    hold_prob: float = 0.0
    historical_accuracy: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "predicted_action": self.predicted_action,
            "confidence": self.confidence,
            "time_horizon_hours": self.time_horizon_hours,
            "accumulation_prob": self.accumulation_prob,
            "distribution_prob": self.distribution_prob,
            "hold_prob": self.hold_prob,
            "historical_accuracy": self.historical_accuracy,
            "created_at": self.created_at.isoformat(),
        }


class InstitutionalBehaviorPredictor:
    """Preditor de comportamento institucional."""

    def __init__(self):
        self._predictions: Dict[str, List[InstitutionalPrediction]] = {}
        self._historical_accuracy: Dict[str, List[float]] = {}
        self._cycle_phases = ["accumulation", "distribution", "holding"]

    def predict_behavior(
        self,
        asset: str,
        footprint_data: Dict[str, Any],
        market_data: Dict[str, Any],
    ) -> InstitutionalPrediction:
        acc_prob = self._calculate_accumulation_prob(footprint_data, market_data)
        dist_prob = self._calculate_distribution_prob(footprint_data, market_data)
        hold_prob = max(0.0, 1 - acc_prob - dist_prob)

        probs = {
            "accumulate": acc_prob,
            "distribute": dist_prob,
            "hold": hold_prob,
        }
        predicted_action = max(probs, key=probs.get)
        confidence = self._calculate_confidence(probs, footprint_data)
        hist_accuracy = self._get_historical_accuracy(asset)

        prediction = InstitutionalPrediction(
            asset=asset,
            predicted_action=predicted_action,
            confidence=confidence,
            accumulation_prob=acc_prob,
            distribution_prob=dist_prob,
            hold_prob=hold_prob,
            historical_accuracy=hist_accuracy,
        )

        self._predictions.setdefault(asset, []).append(prediction)
        return prediction

    def _detect_cycle(self, footprint: Dict[str, Any]) -> str:
        acc_score = footprint.get("accumulation_score", 0)
        dist_score = footprint.get("distribution_score", 0)

        if acc_score > dist_score + 0.2:
            return "accumulation"
        if dist_score > acc_score + 0.2:
            return "distribution"
        return "holding"

    def _calculate_accumulation_prob(self, footprint: Dict[str, Any], market: Dict[str, Any]) -> float:
        base_prob = footprint.get("accumulation_score", 0.3)

        if market.get("volatility", 0.3) < 0.3:
            base_prob += 0.1
        if market.get("trend", "neutral") == "bullish":
            base_prob += 0.1

        return min(base_prob, 1.0)

    def _calculate_distribution_prob(self, footprint: Dict[str, Any], market: Dict[str, Any]) -> float:
        base_prob = footprint.get("distribution_score", 0.3)

        if market.get("volatility", 0.3) > 0.4:
            base_prob += 0.1
        if market.get("trend", "neutral") == "bearish":
            base_prob += 0.1

        return min(base_prob, 1.0)

    def _calculate_confidence(self, probs: Dict[str, float], footprint: Dict[str, Any]) -> float:
        max_prob = max(probs.values())
        quality = footprint.get("data_quality", 0.5)
        return min(max_prob * quality, 1.0)

    def _get_historical_accuracy(self, asset: str) -> float:
        if asset in self._historical_accuracy and self._historical_accuracy[asset]:
            return float(np.mean(self._historical_accuracy[asset]))
        return 0.5

    def update_accuracy(self, asset: str, correct: bool) -> None:
        self._historical_accuracy.setdefault(asset, []).append(1.0 if correct else 0.0)
        if len(self._historical_accuracy[asset]) > 100:
            self._historical_accuracy[asset] = self._historical_accuracy[asset][-100:]

    def get_forecast_dashboard(self) -> Dict[str, Any]:
        total_predictions = sum(len(preds) for preds in self._predictions.values())

        return {
            "total_predictions": total_predictions,
            "assets_tracked": len(self._predictions),
            "avg_confidence": np.mean([
                p.confidence for preds in self._predictions.values() for p in preds
            ]) if total_predictions > 0 else 0,
            "predicted_actions": {
                "accumulate": sum(
                    1 for preds in self._predictions.values() for p in preds if p.predicted_action == "accumulate"
                ),
                "distribute": sum(
                    1 for preds in self._predictions.values() for p in preds if p.predicted_action == "distribute"
                ),
                "hold": sum(
                    1 for preds in self._predictions.values() for p in preds if p.predicted_action == "hold"
                ),
            },
            "avg_historical_accuracy": np.mean([
                p.historical_accuracy for preds in self._predictions.values() for p in preds
            ]) if total_predictions > 0 else 0,
        }
