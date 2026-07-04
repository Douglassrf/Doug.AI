# ============================================================
# MISSÃO 316 — EVOLUTIONARY LEARNING LOOP
# Fase XXI — Evolutionary Trading Intelligence
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class LearningCycle:
    """Ciclo de aprendizado evolutivo."""

    id: str = field(default_factory=lambda: f"lc_{uuid.uuid4().hex[:12]}")
    evolution_score: float = 0.0
    feedback_score: float = 0.0
    model_version: int = 1
    performance_delta: float = 0.0
    updates_applied: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "evolution_score": self.evolution_score,
            "feedback_score": self.feedback_score,
            "model_version": self.model_version,
            "performance_delta": self.performance_delta,
            "updates_applied": self.updates_applied,
            "created_at": self.created_at.isoformat(),
        }


class EvolutionaryLearningLoop:
    """
    Loop contínuo de aprendizado evolutivo.

    Implementa:
    - Feedback Integration
    - Model Updates
    - Performance Tracking
    - Learning Dashboard
    """

    def __init__(self):
        self._cycles: List[LearningCycle] = []
        self._model_version: int = 1
        self._performance_history: List[float] = []
        self._feedback_log: List[Dict[str, Any]] = []

    def integrate_feedback(
        self,
        evolution_data: Dict[str, Any],
        performance_metrics: Dict[str, Any],
    ) -> LearningCycle:
        """Integra feedback de evolução e atualiza modelo."""
        evolution_score = float(evolution_data.get("evolution_score", 0.0))
        feedback_score = self._calculate_feedback_score(performance_metrics)
        performance_delta = self._calculate_performance_delta(performance_metrics)
        updates = self._determine_updates(evolution_score, feedback_score, performance_delta)

        if updates:
            self._model_version += 1

        cycle = LearningCycle(
            evolution_score=evolution_score,
            feedback_score=feedback_score,
            model_version=self._model_version,
            performance_delta=performance_delta,
            updates_applied=updates,
        )

        self._cycles.append(cycle)
        self._performance_history.append(feedback_score)
        self._feedback_log.append(
            {
                "cycle_id": cycle.id,
                "evolution_score": evolution_score,
                "feedback_score": feedback_score,
                "timestamp": cycle.created_at.isoformat(),
            }
        )

        return cycle

    def _calculate_feedback_score(self, metrics: Dict[str, Any]) -> float:
        """Calcula score de feedback a partir de métricas."""
        accuracy = float(metrics.get("accuracy", 0.5))
        stability = float(metrics.get("stability", 0.5))
        return min(max(accuracy * 0.6 + stability * 0.4, 0.0), 1.0)

    def _calculate_performance_delta(self, metrics: Dict[str, Any]) -> float:
        """Calcula delta de performance vs ciclo anterior."""
        current = float(metrics.get("performance", 0.5))
        if not self._performance_history:
            return 0.0
        return current - self._performance_history[-1]

    def _determine_updates(
        self,
        evolution_score: float,
        feedback_score: float,
        performance_delta: float,
    ) -> List[str]:
        """Determina atualizações de modelo necessárias."""
        updates: List[str] = []

        if evolution_score > 0.5:
            updates.append("regime_adapter_refresh")
        if feedback_score < 0.4:
            updates.append("risk_model_recalibration")
        if performance_delta < -0.1:
            updates.append("strategy_weight_rebalance")
        if not updates and evolution_score > 0.3:
            updates.append("incremental_parameter_tune")

        return updates

    def get_learning_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de aprendizado."""
        return {
            "total_cycles": len(self._cycles),
            "model_version": self._model_version,
            "avg_feedback_score": (
                float(np.mean([c.feedback_score for c in self._cycles]))
                if self._cycles
                else 0.0
            ),
            "avg_performance_delta": (
                float(np.mean([c.performance_delta for c in self._cycles]))
                if self._cycles
                else 0.0
            ),
            "feedback_events": len(self._feedback_log),
            "recent_cycles": [c.to_dict() for c in self._cycles[-5:]],
        }
