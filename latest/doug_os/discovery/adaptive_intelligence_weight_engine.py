from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class AdaptiveWeights:
    id: str = field(default_factory=lambda: f"aw_{uuid.uuid4().hex[:12]}")
    regime: str = ""
    weights: Dict[str, float] = field(default_factory=dict)
    confidence: float = 0.5
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    performance_history: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "regime": self.regime, "weights": self.weights,
            "confidence": self.confidence, "last_updated": self.last_updated.isoformat(),
            "performance_history": self.performance_history[-10:],
        }


@dataclass
class WeightOptimizationResult:
    regime: str = ""
    old_weights: Dict[str, float] = field(default_factory=dict)
    new_weights: Dict[str, float] = field(default_factory=dict)
    improvement: float = 0.0
    confidence: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "regime": self.regime, "old_weights": self.old_weights,
            "new_weights": self.new_weights, "improvement": self.improvement,
            "confidence": self.confidence, "created_at": self.created_at.isoformat(),
        }


class AdaptiveIntelligenceWeightEngine:
    _FACTORS = ["momentum", "volatility", "volume", "sentiment", "macro", "liquidity"]
    _REGIMES = ["trending_bull", "trending_bear", "ranging", "high_volatility", "crisis"]

    def __init__(self):
        self._weights: Dict[str, AdaptiveWeights] = {}
        self._optimization_history: List[WeightOptimizationResult] = []

    def initialize_weights(self, regime: str) -> AdaptiveWeights:
        uniform = 1.0 / len(self._FACTORS)
        aw = AdaptiveWeights(regime=regime, weights={f: uniform for f in self._FACTORS}, confidence=0.5)
        self._weights[regime] = aw
        return aw

    def update_weights(self, regime: str, performance: Dict[str, float]) -> WeightOptimizationResult:
        if regime not in self._weights:
            self.initialize_weights(regime)
        current = self._weights[regime]
        old_weights = current.weights.copy()
        total_perf = sum(performance.values()) if performance else 1.0
        if total_perf > 0:
            target = {f: performance.get(f, 0.0) / total_perf for f in self._FACTORS}
        else:
            target = {f: 1.0 / len(self._FACTORS) for f in self._FACTORS}
        lr = 0.3
        new_weights = {f: (1 - lr) * current.weights.get(f, 0.0) + lr * target.get(f, 0.0)
                       for f in self._FACTORS}
        total = sum(new_weights.values())
        if total > 0:
            new_weights = {k: v / total for k, v in new_weights.items()}
        old_perf = self._weighted_performance(old_weights, performance)
        new_perf = self._weighted_performance(new_weights, performance)
        improvement = new_perf - old_perf
        current.weights = new_weights
        current.performance_history.append(improvement)
        current.confidence = min(current.confidence + abs(improvement) * 0.1, 1.0)
        current.last_updated = datetime.now(timezone.utc)
        result = WeightOptimizationResult(regime=regime, old_weights=old_weights,
                                          new_weights=new_weights, improvement=improvement,
                                          confidence=current.confidence)
        self._optimization_history.append(result)
        return result

    def _weighted_performance(self, weights: Dict[str, float], perf: Dict[str, float]) -> float:
        return sum(weights.get(f, 0.0) * perf.get(f, 0.0) for f in self._FACTORS)

    def get_weights(self, regime: str) -> Dict[str, float]:
        if regime not in self._weights:
            self.initialize_weights(regime)
        return self._weights[regime].weights.copy()

    def get_best_regime_weights(self) -> Dict[str, float]:
        best = None
        best_score = -float('inf')
        for regime, aw in self._weights.items():
            if aw.performance_history:
                score = float(np.mean(aw.performance_history[-5:]))
                if score > best_score:
                    best_score = score
                    best = regime
        if best:
            return self.get_weights(best)
        return {f: 1.0 / len(self._FACTORS) for f in self._FACTORS}

    def get_optimization_summary(self) -> Dict[str, Any]:
        return {
            "regimes_covered": len(self._weights),
            "total_optimizations": len(self._optimization_history),
            "avg_improvement": float(np.mean([r.improvement for r in self._optimization_history]))
                               if self._optimization_history else 0.0,
            "best_regime": max(self._weights, key=lambda x: self._weights[x].confidence)
                           if self._weights else None,
        }
