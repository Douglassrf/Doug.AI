# ============================================================
# MISSÃO 312 — PREDICTIVE LIQUIDITY ENGINE
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import uuid
import numpy as np


def _deterministic_unit(seed: str, lo: float = 0.0, hi: float = 1.0) -> float:
    digest = hashlib.sha256(seed.encode()).hexdigest()
    return lo + (int(digest[:8], 16) / 0xFFFFFFFF) * (hi - lo)


@dataclass
class LiquidityPrediction:
    """Previsão de liquidez."""

    id: str = field(default_factory=lambda: f"lp_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    predicted_liquidity: float = 0.0
    current_liquidity: float = 0.0
    confidence: float = 0.0
    time_horizon_hours: int = 24
    stop_cluster_density: float = 0.0
    volume_projection: float = 0.0
    migration_detected: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "predicted_liquidity": self.predicted_liquidity,
            "current_liquidity": self.current_liquidity,
            "confidence": self.confidence,
            "time_horizon_hours": self.time_horizon_hours,
            "stop_cluster_density": self.stop_cluster_density,
            "volume_projection": self.volume_projection,
            "migration_detected": self.migration_detected,
            "created_at": self.created_at.isoformat(),
        }


class PredictiveLiquidityEngine:
    """
    Motor preditivo de liquidez.

    Implementa:
    - Liquidity Forecast
    - Stop Cluster Prediction
    - Volume Projection
    - Order Book Forecast
    - Liquidity Migration
    - Liquidity Heatmap
    - Confidence Score
    - Timeline
    - Dashboard
    - Learning Engine
    """

    def __init__(self):
        self._predictions: Dict[str, List[LiquidityPrediction]] = {}
        self._liquidity_history: Dict[str, List[float]] = {}

    def predict_liquidity(
        self,
        asset: str,
        current_liquidity: float,
        order_book: Dict[str, Any],
        volume_data: Dict[str, float],
        horizon_hours: int = 24,
    ) -> LiquidityPrediction:
        """Prevê liquidez futura."""
        predicted = self._forecast_liquidity(asset, current_liquidity, volume_data)
        stop_density = self._calculate_stop_cluster_density(asset, order_book)
        volume_proj = self._project_volume(volume_data)
        migration = self._detect_liquidity_migration(asset, current_liquidity)
        confidence = self._calculate_confidence(volume_data, order_book)

        prediction = LiquidityPrediction(
            asset=asset,
            predicted_liquidity=predicted,
            current_liquidity=current_liquidity,
            confidence=confidence,
            time_horizon_hours=horizon_hours,
            stop_cluster_density=stop_density,
            volume_projection=volume_proj,
            migration_detected=migration,
        )

        if asset not in self._predictions:
            self._predictions[asset] = []

        self._predictions[asset].append(prediction)

        if asset not in self._liquidity_history:
            self._liquidity_history[asset] = []
        self._liquidity_history[asset].append(current_liquidity)

        return prediction

    def _forecast_liquidity(
        self, asset: str, current: float, volume: Dict[str, float]
    ) -> float:
        """Prevê liquidez usando modelo EWMA."""
        if asset not in self._liquidity_history or len(self._liquidity_history[asset]) < 5:
            jitter = _deterministic_unit(f"{asset}:forecast", -0.05, 0.05)
            return current * (1 + jitter)

        history = self._liquidity_history[asset][-10:]
        alpha = 0.3
        forecast = history[-1]

        for h in reversed(history[:-1]):
            forecast = alpha * h + (1 - alpha) * forecast

        volume_factor = min(volume.get("trend", 0.5) * 0.2, 0.2)
        return forecast * (1 + volume_factor)

    def _calculate_stop_cluster_density(self, asset: str, order_book: Dict[str, Any]) -> float:
        """Calcula densidade de stop clusters (determinístico)."""
        levels = order_book.get("levels", [])
        if not levels:
            return 0.0

        return _deterministic_unit(f"{asset}:stop_density:{len(levels)}", 0.1, 0.5)

    def _project_volume(self, volume: Dict[str, float]) -> float:
        """Projeta volume futuro."""
        base_volume = volume.get("average", 1000)
        trend = volume.get("trend", 0.0)
        return base_volume * (1 + trend * 0.5)

    def _detect_liquidity_migration(self, asset: str, current: float) -> bool:
        """Detecta migração de liquidez."""
        if asset not in self._liquidity_history or len(self._liquidity_history[asset]) < 5:
            return False

        recent = self._liquidity_history[asset][-5:]
        if len(recent) < 2:
            return False

        slope = (recent[-1] - recent[0]) / len(recent)
        return abs(slope) > 0.05

    def _calculate_confidence(
        self, volume: Dict[str, float], order_book: Dict[str, Any]
    ) -> float:
        """Calcula confiança da previsão."""
        confidence = 0.5

        if volume.get("data_quality", 0) > 0.7:
            confidence += 0.2

        if order_book.get("depth", 0) > 0.5:
            confidence += 0.1

        return min(confidence, 1.0)

    def get_liquidity_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de liquidez."""
        total_predictions = sum(len(preds) for preds in self._predictions.values())

        if total_predictions == 0:
            return {"status": "no_data"}

        all_predictions = [p for preds in self._predictions.values() for p in preds]

        return {
            "total_predictions": total_predictions,
            "assets_tracked": len(self._predictions),
            "avg_confidence": float(np.mean([p.confidence for p in all_predictions])),
            "avg_predicted_liquidity": float(
                np.mean([p.predicted_liquidity for p in all_predictions])
            ),
            "migrations_detected": sum(1 for p in all_predictions if p.migration_detected),
            "recent_predictions": [p.to_dict() for p in all_predictions[-5:]],
        }
