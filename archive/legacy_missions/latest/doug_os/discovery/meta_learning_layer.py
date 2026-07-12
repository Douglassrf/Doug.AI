from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import numpy as np


@dataclass
class ModelPerformance:
    model_id: str = ""
    model_name: str = ""
    regime: str = ""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    computational_cost_ms: float = 0.0
    samples: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id, "model_name": self.model_name,
            "regime": self.regime, "accuracy": self.accuracy,
            "precision": self.precision, "recall": self.recall,
            "f1_score": self.f1_score, "computational_cost_ms": self.computational_cost_ms,
            "samples": self.samples, "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class MetaLearningResult:
    best_model_by_regime: Dict[str, str] = field(default_factory=dict)
    strategy_ranking: List[Dict[str, Any]] = field(default_factory=list)
    meta_learning_score: float = 0.0
    recommendation: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "best_model_by_regime": self.best_model_by_regime,
            "strategy_ranking": self.strategy_ranking,
            "meta_learning_score": self.meta_learning_score,
            "recommendation": self.recommendation,
            "created_at": self.created_at.isoformat(),
        }


class MetaLearningLayer:
    _REGIMES = ["trending_bull", "trending_bear", "ranging", "high_volatility", "crisis"]

    def __init__(self):
        self._performances: List[ModelPerformance] = []

    def record_performance(self, performance: ModelPerformance) -> None:
        self._performances.append(performance)

    def learn(self) -> MetaLearningResult:
        if not self._performances:
            return MetaLearningResult(meta_learning_score=0.0, recommendation="Insufficient data for meta-learning")

        regime_perfs: Dict[str, List[ModelPerformance]] = {r: [] for r in self._REGIMES}
        for p in self._performances:
            if p.regime in regime_perfs:
                regime_perfs[p.regime].append(p)

        best_by_regime: Dict[str, str] = {}
        for regime, perfs in regime_perfs.items():
            if perfs:
                best_by_regime[regime] = max(perfs, key=lambda x: x.f1_score).model_id

        ranking = self._calculate_ranking()
        meta_score = self._calculate_meta_score(ranking)
        recommendation = self._generate_recommendation(best_by_regime, ranking)

        return MetaLearningResult(
            best_model_by_regime=best_by_regime,
            strategy_ranking=ranking,
            meta_learning_score=meta_score,
            recommendation=recommendation,
        )

    def _calculate_ranking(self) -> List[Dict[str, Any]]:
        model_perfs: Dict[str, List[ModelPerformance]] = {}
        for p in self._performances:
            model_perfs.setdefault(p.model_id, []).append(p)
        ranking = []
        for model_id, perfs in model_perfs.items():
            ranking.append({
                "model_id": model_id,
                "model_name": perfs[0].model_name,
                "average_f1": float(np.mean([p.f1_score for p in perfs])),
                "average_cost_ms": float(np.mean([p.computational_cost_ms for p in perfs])),
                "samples": len(perfs),
                "regimes_covered": len(set(p.regime for p in perfs)),
            })
        ranking.sort(key=lambda x: x["average_f1"], reverse=True)
        return ranking

    def _calculate_meta_score(self, ranking: List[Dict[str, Any]]) -> float:
        if not ranking: return 0.0
        best = ranking[0]["average_f1"]
        coverage = min(len(ranking) / 10, 1.0)
        return float(min((best + coverage) / 2, 1.0))

    def _generate_recommendation(self, best_by_regime, ranking) -> str:
        if not best_by_regime: return "Collect more data for recommendations"
        lines = ["Recommended models by regime:"]
        id_to_name = {p.model_id: p.model_name for p in self._performances}
        for regime, model_id in best_by_regime.items():
            lines.append(f"- {regime}: {id_to_name.get(model_id, model_id)}")
        return "\n".join(lines)
