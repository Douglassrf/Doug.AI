from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import numpy as np


@dataclass
class Position:
    asset_id: str = ""
    asset_name: str = ""
    asset_class: str = ""
    quantity: float = 0.0
    price: float = 0.0
    value: float = 0.0
    weight: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id, "asset_name": self.asset_name,
            "asset_class": self.asset_class, "quantity": self.quantity,
            "price": self.price, "value": self.value, "weight": self.weight,
        }


@dataclass
class PortfolioIntelligence:
    total_value: float = 0.0
    diversification_score: float = 0.0
    concentration_risk: float = 0.0
    entropy: float = 0.0
    correlation_risk: float = 0.0
    stress_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_value": self.total_value,
            "diversification_score": self.diversification_score,
            "concentration_risk": self.concentration_risk,
            "entropy": self.entropy,
            "correlation_risk": self.correlation_risk,
            "stress_score": self.stress_score,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat(),
        }


class PortfolioIntelligenceLayer:
    def __init__(self):
        self._portfolios: List[Dict[str, Any]] = []

    def analyze(self, positions: List[Position]) -> PortfolioIntelligence:
        if not positions:
            return PortfolioIntelligence(
                diversification_score=0.0, concentration_risk=1.0,
                recommendations=["Add positions to portfolio"],
            )
        total_value = sum(p.value for p in positions)
        if total_value > 0:
            for p in positions:
                p.weight = p.value / total_value
        weights = [p.weight for p in positions]
        n = len(weights)
        hhi = sum(w**2 for w in weights)
        diversification = float(min(max(1 - (hhi - 1/n) / (1 - 1/n), 0.0), 1.0)) if n > 1 else 0.0
        concentration_risk = float(min(max(weights) * 2, 1.0)) if weights else 1.0
        entropy = self._calculate_entropy(weights)
        correlation_risk = self._calculate_correlation_risk(positions)
        stress_score = self._stress_test(positions)
        recommendations = self._generate_recommendations(diversification, concentration_risk, entropy)
        return PortfolioIntelligence(
            total_value=total_value, diversification_score=diversification,
            concentration_risk=concentration_risk, entropy=entropy,
            correlation_risk=correlation_risk, stress_score=stress_score,
            recommendations=recommendations,
        )

    def _calculate_entropy(self, weights: List[float]) -> float:
        if not weights: return 0.0
        entropy = -sum(w * np.log(w) for w in weights if w > 0)
        max_entropy = np.log(len(weights))
        if max_entropy == 0: return 0.0
        return float(min(entropy / max_entropy, 1.0))

    def _calculate_correlation_risk(self, positions: List[Position]) -> float:
        # Determinístico: usa 0.3 como proxy de correlação média
        if len(positions) < 2: return 0.0
        return 0.3

    def _stress_test(self, positions: List[Position]) -> float:
        if not positions: return 1.0
        loss_multipliers = {"crypto": 0.4, "equity": 0.25, "bond": 0.1, "commodity": 0.2, "forex": 0.15}
        stress_loss = sum(p.value * loss_multipliers.get(p.asset_class, 0.2) for p in positions)
        total = sum(p.value for p in positions)
        return float(min(stress_loss / total, 1.0)) if total > 0 else 0.0

    def _generate_recommendations(self, diversification, concentration, entropy) -> List[str]:
        recs = []
        if diversification < 0.3: recs.append("Portfolio is under-diversified. Consider adding uncorrelated assets.")
        if concentration > 0.5: recs.append("High concentration risk. Reduce largest positions.")
        if entropy < 0.3: recs.append("Low portfolio entropy. Consider rebalancing.")
        if diversification > 0.7 and concentration < 0.3: recs.append("Portfolio is well-diversified. Maintain current allocation.")
        return recs
