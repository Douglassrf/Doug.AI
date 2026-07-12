from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class AgentPerformance:
    id: str = field(default_factory=lambda: f"ap_{uuid.uuid4().hex[:12]}")
    agent_id: str = ""
    accuracy: float = 0.0
    reliability: float = 0.0
    precision: float = 0.0
    false_positives: int = 0
    false_negatives: int = 0
    total_attempts: int = 0
    successful_attempts: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "accuracy": self.accuracy,
            "reliability": self.reliability,
            "precision": self.precision,
            "false_positives": self.false_positives,
            "false_negatives": self.false_negatives,
            "total_attempts": self.total_attempts,
            "successful_attempts": self.successful_attempts,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ReputationScore:
    agent_id: str = ""
    overall_score: float = 0.0
    accuracy_score: float = 0.0
    reliability_score: float = 0.0
    precision_score: float = 0.0
    trend: str = "stable"
    history: List[float] = field(default_factory=list)
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "overall_score": self.overall_score,
            "accuracy_score": self.accuracy_score,
            "reliability_score": self.reliability_score,
            "precision_score": self.precision_score,
            "trend": self.trend,
            "history": self.history[-10:],
            "updated_at": self.updated_at.isoformat(),
        }


class AgentReputationEngine:
    """Motor de reputação de agentes — scoring, ranking, trend analysis."""

    def __init__(self) -> None:
        self._performances: Dict[str, List[AgentPerformance]] = {}
        self._reputations: Dict[str, ReputationScore] = {}
        self._weights = {"accuracy": 0.35, "reliability": 0.30, "precision": 0.20, "success_rate": 0.15}

    def record_performance(
        self,
        agent_id: str,
        accuracy: float,
        reliability: float,
        precision: float,
        false_positives: int = 0,
        false_negatives: int = 0,
        total_attempts: int = 1,
        successful_attempts: int = 1,
    ) -> AgentPerformance:
        perf = AgentPerformance(
            agent_id=agent_id,
            accuracy=min(max(accuracy, 0.0), 1.0),
            reliability=min(max(reliability, 0.0), 1.0),
            precision=min(max(precision, 0.0), 1.0),
            false_positives=false_positives,
            false_negatives=false_negatives,
            total_attempts=total_attempts,
            successful_attempts=successful_attempts,
        )
        self._performances.setdefault(agent_id, []).append(perf)
        self._update_reputation(agent_id)
        return perf

    def _update_reputation(self, agent_id: str) -> None:
        performances = self._performances.get(agent_id, [])
        if not performances:
            return
        recent = performances[-10:]
        avg_accuracy = float(np.mean([p.accuracy for p in recent]))
        avg_reliability = float(np.mean([p.reliability for p in recent]))
        avg_precision = float(np.mean([p.precision for p in recent]))
        total_attempts = sum(p.total_attempts for p in recent)
        success_rate = sum(p.successful_attempts for p in recent) / total_attempts if total_attempts > 0 else 0.0

        overall = (
            avg_accuracy * self._weights["accuracy"]
            + avg_reliability * self._weights["reliability"]
            + avg_precision * self._weights["precision"]
            + success_rate * self._weights["success_rate"]
        )

        trend = "stable"
        if len(performances) >= 5:
            scores = [p.accuracy * p.reliability for p in performances[-5:]]
            slope = (scores[-1] - scores[0]) / 5
            if slope > 0.02:
                trend = "improving"
            elif slope < -0.02:
                trend = "declining"

        self._reputations[agent_id] = ReputationScore(
            agent_id=agent_id,
            overall_score=overall,
            accuracy_score=avg_accuracy,
            reliability_score=avg_reliability,
            precision_score=avg_precision,
            trend=trend,
            history=[p.accuracy for p in performances[-20:]],
        )

    def get_reputation(self, agent_id: str) -> Optional[ReputationScore]:
        return self._reputations.get(agent_id)

    def get_reputation_ranking(self) -> List[ReputationScore]:
        return sorted(self._reputations.values(), key=lambda r: r.overall_score, reverse=True)

    def penalize(self, agent_id: str, penalty: float = 0.1) -> bool:
        rep = self._reputations.get(agent_id)
        if not rep:
            return False
        rep.overall_score = max(0.0, rep.overall_score - penalty)
        return True

    def get_reputation_dashboard(self) -> Dict[str, Any]:
        total = len(self._reputations)
        return {
            "total_agents": total,
            "avg_score": float(np.mean([r.overall_score for r in self._reputations.values()])) if total else 0.0,
            "improving": sum(1 for r in self._reputations.values() if r.trend == "improving"),
            "declining": sum(1 for r in self._reputations.values() if r.trend == "declining"),
            "ranking": [r.to_dict() for r in self.get_reputation_ranking()[:5]],
        }
