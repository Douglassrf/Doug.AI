# ============================================================
# MISSÃO 309 — STRATEGY LIFECYCLE MANAGER
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


class LifecycleStage:
    """Estágios do ciclo de vida."""

    BIRTH = "birth"
    GROWTH = "growth"
    MATURITY = "maturity"
    DECLINE = "decline"
    RETIRED = "retired"


@dataclass
class StrategyLifecycle:
    """Ciclo de vida da estratégia."""

    id: str = field(default_factory=lambda: f"sl_{uuid.uuid4().hex[:12]}")
    strategy_id: str = ""
    stage: str = LifecycleStage.BIRTH
    performance_history: List[float] = field(default_factory=list)
    version: int = 1
    lifecycle_score: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    retired_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "strategy_id": self.strategy_id,
            "stage": self.stage,
            "performance_history": self.performance_history[-20:],
            "version": self.version,
            "lifecycle_score": self.lifecycle_score,
            "created_at": self.created_at.isoformat(),
            "retired_at": self.retired_at.isoformat() if self.retired_at else None,
        }


class StrategyLifecycleManager:
    """
    Gerenciador de ciclo de vida de estratégias.

    Implementa:
    - Strategy Birth
    - Growth
    - Maturity
    - Decline
    - Retirement
    - Version Manager
    - Performance History
    - Lifecycle Score
    - Strategy Registry
    - Dashboard
    """

    def __init__(self):
        self._strategies: Dict[str, StrategyLifecycle] = {}
        self._strategy_registry: Dict[str, Dict[str, Any]] = {}

    def register_strategy(self, strategy_id: str) -> StrategyLifecycle:
        """Registra nova estratégia (Birth)."""
        lifecycle = StrategyLifecycle(
            strategy_id=strategy_id,
            stage=LifecycleStage.BIRTH,
            lifecycle_score=0.1,
        )

        self._strategies[strategy_id] = lifecycle
        self._strategy_registry[strategy_id] = {
            "birth_date": datetime.now(timezone.utc).isoformat(),
            "versions": 1,
        }

        return lifecycle

    def update_performance(self, strategy_id: str, performance: float) -> None:
        """Atualiza performance da estratégia."""
        if strategy_id not in self._strategies:
            return

        lifecycle = self._strategies[strategy_id]
        lifecycle.performance_history.append(performance)
        self._update_stage(strategy_id)

    def _update_stage(self, strategy_id: str) -> None:
        """Atualiza estágio da estratégia."""
        lifecycle = self._strategies.get(strategy_id)
        if not lifecycle or len(lifecycle.performance_history) < 10:
            return

        recent = lifecycle.performance_history[-20:]
        if len(recent) < 10:
            return

        x = np.arange(len(recent))
        slope, _ = np.polyfit(x, recent, 1)

        if lifecycle.stage == LifecycleStage.BIRTH:
            if slope > 0.01 and len(lifecycle.performance_history) >= 20:
                lifecycle.stage = LifecycleStage.GROWTH

        elif lifecycle.stage == LifecycleStage.GROWTH:
            if slope < 0.005:
                lifecycle.stage = LifecycleStage.MATURITY

        elif lifecycle.stage == LifecycleStage.MATURITY:
            if slope < -0.01:
                lifecycle.stage = LifecycleStage.DECLINE

        elif lifecycle.stage == LifecycleStage.DECLINE:
            if slope < -0.02:
                lifecycle.retired_at = datetime.now(timezone.utc)
                lifecycle.stage = LifecycleStage.RETIRED

        lifecycle.lifecycle_score = self._calculate_lifecycle_score(lifecycle)

    def _calculate_lifecycle_score(self, lifecycle: StrategyLifecycle) -> float:
        """Calcula score do ciclo de vida."""
        if not lifecycle.performance_history:
            return 0.0

        recent = lifecycle.performance_history[-20:]
        avg_perf = float(np.mean(recent)) if recent else 0.0

        stage_multipliers = {
            LifecycleStage.BIRTH: 0.3,
            LifecycleStage.GROWTH: 0.7,
            LifecycleStage.MATURITY: 1.0,
            LifecycleStage.DECLINE: 0.5,
            LifecycleStage.RETIRED: 0.0,
        }

        return avg_perf * stage_multipliers.get(lifecycle.stage, 0.3)

    def get_lifecycle_status(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Retorna status do ciclo de vida."""
        lifecycle = self._strategies.get(strategy_id)
        if not lifecycle:
            return None

        return {
            "strategy_id": strategy_id,
            "stage": lifecycle.stage,
            "version": lifecycle.version,
            "lifecycle_score": lifecycle.lifecycle_score,
            "performance_count": len(lifecycle.performance_history),
            "age_days": (datetime.now(timezone.utc) - lifecycle.created_at).days,
        }

    def get_lifecycle_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard do ciclo de vida."""
        total = len(self._strategies)

        stages = {
            LifecycleStage.BIRTH: 0,
            LifecycleStage.GROWTH: 0,
            LifecycleStage.MATURITY: 0,
            LifecycleStage.DECLINE: 0,
            LifecycleStage.RETIRED: 0,
        }

        for lifecycle in self._strategies.values():
            stages[lifecycle.stage] += 1

        return {
            "total_strategies": total,
            "stage_distribution": stages,
            "avg_lifecycle_score": (
                float(np.mean([s.lifecycle_score for s in self._strategies.values()]))
                if total > 0
                else 0.0
            ),
            "recent_retirements": sum(
                1 for s in self._strategies.values() if s.stage == LifecycleStage.RETIRED
            ),
            "strategy_registry": self._strategy_registry,
        }
