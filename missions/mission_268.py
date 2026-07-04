# ============================================================
# MISSÃO 268 — PREDICTIVE MARKET STATE ENGINE
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class MarketStatePrediction:
    """Previsão de estado de mercado."""
    id: str = field(default_factory=lambda: f"msp_{uuid.uuid4().hex[:12]}")
    current_regime: str = ""
    predicted_regime: str = ""
    transition_probability: float = 0.0
    confidence: float = 0.0
    time_horizon_hours: int = 24
    persistence_score: float = 0.0
    early_warning_level: str = "green"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "current_regime": self.current_regime,
            "predicted_regime": self.predicted_regime,
            "transition_probability": self.transition_probability,
            "confidence": self.confidence,
            "time_horizon_hours": self.time_horizon_hours,
            "persistence_score": self.persistence_score,
            "early_warning_level": self.early_warning_level,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class StateTransitionMatrix:
    """Matriz de transição de estados."""
    id: str = field(default_factory=lambda: f"stm_{uuid.uuid4().hex[:12]}")
    matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sample_size: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "matrix": self.matrix,
            "last_updated": self.last_updated.isoformat(),
            "sample_size": self.sample_size,
        }


class PredictiveMarketStateEngine:
    """Motor preditivo de estado de mercado."""

    def __init__(self):
        self._predictions: List[MarketStatePrediction] = []
        self._transition_matrices: List[StateTransitionMatrix] = []
        self._regime_history: List[str] = []
        self._regimes = ["trending_bull", "trending_bear", "ranging", "high_volatility", "crisis"]

    def predict_next_state(
        self,
        current_regime: str,
        market_data: Dict[str, Any],
        horizon_hours: int = 24,
    ) -> MarketStatePrediction:
        matrix = self._build_transition_matrix()

        if current_regime in matrix:
            transition_probs = matrix[current_regime]
            predicted_regime = max(transition_probs, key=transition_probs.get)
            transition_prob = transition_probs[predicted_regime]
        else:
            predicted_regime = current_regime
            transition_prob = 0.5

        persistence = self._calculate_persistence(current_regime)
        confidence = self._calculate_confidence(current_regime, transition_prob, market_data)
        early_warning = self._determine_early_warning(transition_prob, confidence)

        prediction = MarketStatePrediction(
            current_regime=current_regime,
            predicted_regime=predicted_regime,
            transition_probability=transition_prob,
            confidence=confidence,
            time_horizon_hours=horizon_hours,
            persistence_score=persistence,
            early_warning_level=early_warning,
        )

        self._predictions.append(prediction)
        return prediction

    def _build_transition_matrix(self) -> Dict[str, Dict[str, float]]:
        if len(self._regime_history) < 2:
            return {r: {r2: 1.0 / len(self._regimes) for r2 in self._regimes} for r in self._regimes}

        matrix = {r: {r2: 0.0 for r2 in self._regimes} for r in self._regimes}

        for i in range(len(self._regime_history) - 1):
            current = self._regime_history[i]
            next_state = self._regime_history[i + 1]
            matrix[current][next_state] += 1

        for current in self._regimes:
            total = sum(matrix[current].values())
            if total > 0:
                matrix[current] = {k: v / total for k, v in matrix[current].items()}

        return matrix

    def _calculate_persistence(self, regime: str) -> float:
        if len(self._regime_history) < 10:
            return 0.5

        recent = self._regime_history[-20:]
        same_regime = sum(1 for r in recent if r == regime)
        return same_regime / len(recent)

    def _calculate_confidence(
        self,
        regime: str,
        trans_prob: float,
        market_data: Dict[str, Any],
    ) -> float:
        base_conf = trans_prob
        volatility = market_data.get("volatility", 0.3)
        vol_penalty = min(volatility * 0.3, 0.3)
        liquidity = market_data.get("liquidity", 0.5)
        liq_boost = liquidity * 0.1
        final_conf = base_conf - vol_penalty + liq_boost
        return min(max(final_conf, 0.1), 1.0)

    def _determine_early_warning(self, trans_prob: float, confidence: float) -> str:
        combined = trans_prob * confidence
        if combined > 0.6:
            return "red"
        if combined > 0.35:
            return "yellow"
        return "green"

    def update_regime_history(self, regime: str) -> None:
        self._regime_history.append(regime)
        if len(self._regime_history) > 1000:
            self._regime_history = self._regime_history[-1000:]

    def get_predictive_dashboard(self) -> Dict[str, Any]:
        if not self._predictions:
            return {"status": "no_data"}

        recent = self._predictions[-20:]
        accuracy = (
            sum(1 for p in recent if p.predicted_regime == p.current_regime) / len(recent)
            if recent
            else 0
        )

        return {
            "total_predictions": len(self._predictions),
            "recent_accuracy": accuracy,
            "avg_confidence": np.mean([p.confidence for p in recent]) if recent else 0,
            "regime_distribution": {
                r: self._regime_history.count(r) / len(self._regime_history) if self._regime_history else 0
                for r in self._regimes
            },
            "last_prediction": self._predictions[-1].to_dict() if self._predictions else None,
            "early_warnings": {
                "red": sum(1 for p in recent if p.early_warning_level == "red"),
                "yellow": sum(1 for p in recent if p.early_warning_level == "yellow"),
                "green": sum(1 for p in recent if p.early_warning_level == "green"),
            },
        }
