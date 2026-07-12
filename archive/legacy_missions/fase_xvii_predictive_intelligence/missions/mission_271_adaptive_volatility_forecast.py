# ============================================================
# MISSÃO 271 — ADAPTIVE VOLATILITY FORECAST
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class VolatilityForecast:
    """Previsão de volatilidade."""
    id: str = field(default_factory=lambda: f"vf_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    current_vol: float = 0.0
    predicted_vol: float = 0.0
    confidence: float = 0.0
    time_horizon_hours: int = 24
    shock_probability: float = 0.0
    compression_prob: float = 0.0
    expansion_prob: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "current_vol": self.current_vol,
            "predicted_vol": self.predicted_vol,
            "confidence": self.confidence,
            "time_horizon_hours": self.time_horizon_hours,
            "shock_probability": self.shock_probability,
            "compression_prob": self.compression_prob,
            "expansion_prob": self.expansion_prob,
            "created_at": self.created_at.isoformat(),
        }


class AdaptiveVolatilityForecast:
    """Previsão adaptativa de volatilidade."""

    def __init__(self):
        self._forecasts: Dict[str, List[VolatilityForecast]] = {}
        self._historical_vol: Dict[str, List[float]] = {}
        self._volatility_regimes = ["low", "normal", "high", "extreme"]

    def forecast_volatility(
        self,
        asset: str,
        historical_prices: List[float],
        implied_vol: float = 0.0,
        horizon_hours: int = 24,
    ) -> VolatilityForecast:
        current_vol = self._calculate_volatility(historical_prices)
        predicted_vol = self._predict_volatility(historical_prices, implied_vol)
        shock_prob = self._calculate_shock_probability(historical_prices, implied_vol)
        compression_prob = self._calculate_compression_probability(historical_prices)
        expansion_prob = self._calculate_expansion_probability(historical_prices)
        confidence = self._calculate_confidence(historical_prices, implied_vol)

        forecast = VolatilityForecast(
            asset=asset,
            current_vol=current_vol,
            predicted_vol=predicted_vol,
            confidence=confidence,
            time_horizon_hours=horizon_hours,
            shock_probability=shock_prob,
            compression_prob=compression_prob,
            expansion_prob=expansion_prob,
        )

        self._forecasts.setdefault(asset, []).append(forecast)
        self._historical_vol.setdefault(asset, []).append(current_vol)

        return forecast

    def _calculate_volatility(self, prices: List[float]) -> float:
        if len(prices) < 2:
            return 0.3

        returns = np.diff(np.log(prices))
        return float(np.std(returns) * np.sqrt(252))

    def _predict_volatility(self, prices: List[float], implied_vol: float) -> float:
        if len(prices) < 10:
            return 0.3

        current = self._calculate_volatility(prices)

        if implied_vol > 0:
            return current * 0.3 + implied_vol * 0.7

        returns = np.diff(np.log(prices))
        if len(returns) < 2:
            return current

        alpha = 0.94
        vol_sq = returns[-1] ** 2
        for r in reversed(returns[:-1]):
            vol_sq = alpha * vol_sq + (1 - alpha) * r ** 2

        return float(np.sqrt(vol_sq) * np.sqrt(252))

    def _calculate_shock_probability(self, prices: List[float], implied_vol: float) -> float:
        if len(prices) < 20:
            return 0.3

        returns = np.diff(np.log(prices))
        recent_vol = np.std(returns[-10:]) if len(returns) >= 10 else np.std(returns)
        historical_vol = np.std(returns) if len(returns) > 0 else 0.01

        if historical_vol > 0:
            ratio = recent_vol / historical_vol
            shock_prob = min(ratio / 2, 1.0)
        else:
            shock_prob = 0.3

        if implied_vol > 0 and implied_vol > historical_vol * 1.5:
            shock_prob = min(shock_prob + 0.2, 1.0)

        return float(shock_prob)

    def _calculate_compression_probability(self, prices: List[float]) -> float:
        if len(prices) < 10:
            return 0.3

        returns = np.diff(np.log(prices))
        recent_vol = np.std(returns[-5:]) if len(returns) >= 5 else np.std(returns)
        historical_vol = np.std(returns) if len(returns) > 0 else 0.01

        if historical_vol > 0:
            ratio = recent_vol / historical_vol
            if ratio < 0.5:
                return 0.6
            if ratio < 0.7:
                return 0.4

        return 0.2

    def _calculate_expansion_probability(self, prices: List[float]) -> float:
        return 1 - self._calculate_compression_probability(prices)

    def _calculate_confidence(self, prices: List[float], implied_vol: float) -> float:
        confidence = min(len(prices) / 100, 0.8) + 0.1
        if implied_vol > 0:
            confidence += 0.1
        return min(confidence, 1.0)

    def get_forecast_dashboard(self) -> Dict[str, Any]:
        total_forecasts = sum(len(fs) for fs in self._forecasts.values())

        return {
            "total_forecasts": total_forecasts,
            "assets_tracked": len(self._forecasts),
            "avg_confidence": np.mean([
                f.confidence for fs in self._forecasts.values() for f in fs
            ]) if total_forecasts > 0 else 0,
            "avg_predicted_vol": np.mean([
                f.predicted_vol for fs in self._forecasts.values() for f in fs
            ]) if total_forecasts > 0 else 0,
            "shock_probabilities": {
                "high": sum(1 for fs in self._forecasts.values() for f in fs if f.shock_probability > 0.5),
                "medium": sum(
                    1 for fs in self._forecasts.values() for f in fs if 0.3 <= f.shock_probability <= 0.5
                ),
                "low": sum(1 for fs in self._forecasts.values() for f in fs if f.shock_probability < 0.3),
            },
        }
