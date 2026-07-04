from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any


@dataclass
class DiscoveryMetrics:
    total_hypotheses: int = 0
    useful_hypotheses: int = 0
    useless_hypotheses: int = 0
    false_positives: int = 0
    computational_cost_ms: float = 0.0
    average_time_per_hypothesis: float = 0.0
    repeated_hypotheses: int = 0
    unique_hypotheses: int = 0
    efficiency_by_regime: Dict[str, float] = field(default_factory=dict)
    success_rate: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_hypotheses": self.total_hypotheses,
            "useful_hypotheses": self.useful_hypotheses,
            "useless_hypotheses": self.useless_hypotheses,
            "false_positives": self.false_positives,
            "computational_cost_ms": self.computational_cost_ms,
            "average_time_per_hypothesis": self.average_time_per_hypothesis,
            "repeated_hypotheses": self.repeated_hypotheses,
            "unique_hypotheses": self.unique_hypotheses,
            "efficiency_by_regime": self.efficiency_by_regime,
            "success_rate": self.success_rate,
            "created_at": self.created_at.isoformat(),
        }


class DiscoveryOfDiscoveryEngine:
    """Avalia a qualidade e eficiência do próprio Discovery Layer."""

    def __init__(self):
        self._metrics_history: List[DiscoveryMetrics] = []
        self._hypothesis_cache: Dict[str, int] = {}
        self._regime_performance: Dict[str, List[float]] = {}

    def analyze_discoveries(
        self,
        hypotheses: List[Dict[str, Any]],
        results: List[Dict[str, Any]],
    ) -> DiscoveryMetrics:
        metrics = DiscoveryMetrics()
        metrics.total_hypotheses = len(hypotheses)
        metrics.useful_hypotheses = sum(1 for h in hypotheses if h.get("is_useful", False))
        metrics.useless_hypotheses = metrics.total_hypotheses - metrics.useful_hypotheses
        metrics.false_positives = sum(1 for r in results if r.get("is_false_positive", False))

        total_cost = sum(float(h.get("computational_cost", 0)) for h in hypotheses)
        metrics.computational_cost_ms = total_cost
        metrics.average_time_per_hypothesis = total_cost / len(hypotheses) if hypotheses else 0.0

        for h in hypotheses:
            h_hash = h.get("hash", "")
            if h_hash:
                self._hypothesis_cache[h_hash] = self._hypothesis_cache.get(h_hash, 0) + 1
                if self._hypothesis_cache[h_hash] > 1:
                    metrics.repeated_hypotheses += 1

        metrics.unique_hypotheses = len({h.get("hash", "") for h in hypotheses if h.get("hash")})

        for h in hypotheses:
            regime = h.get("market_regime", "unknown")
            self._regime_performance.setdefault(regime, []).append(1 if h.get("is_useful") else 0)

        metrics.efficiency_by_regime = {
            r: sum(s) / len(s) for r, s in self._regime_performance.items() if s
        }
        metrics.success_rate = (
            metrics.useful_hypotheses / metrics.total_hypotheses if metrics.total_hypotheses else 0.0
        )
        self._metrics_history.append(metrics)
        return metrics

    def check_alerts(self, metrics: DiscoveryMetrics) -> List[str]:
        alerts = []
        if metrics.success_rate < 0.3:
            alerts.append("Low success rate — Discovery may need recalibration")
        if metrics.total_hypotheses > 0 and metrics.repeated_hypotheses > metrics.total_hypotheses * 0.5:
            alerts.append("High repetition rate — Discovery stuck in local optimum")
        if metrics.total_hypotheses > 0 and metrics.false_positives > metrics.total_hypotheses * 0.4:
            alerts.append("High false positive rate — Validation may be too weak")
        if metrics.average_time_per_hypothesis > 1000:
            alerts.append("High computational cost — Optimization needed")
        return alerts

    def get_performance_trend(self) -> Dict[str, Any]:
        if len(self._metrics_history) < 2:
            return {"trend": "insufficient_data"}
        recent = self._metrics_history[-1]
        previous = self._metrics_history[-2]
        return {
            "trend": "improving" if recent.success_rate > previous.success_rate else "declining",
            "success_rate_delta": recent.success_rate - previous.success_rate,
            "cost_delta": recent.computational_cost_ms - previous.computational_cost_ms,
        }
