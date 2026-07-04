# ============================================================
# MISSÃO 305 — CONTROLLED CAPITAL SCALING
# Fase Final — Final Trading Operating System
# ============================================================

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class ScalingTier:
    """Nível de capital controlado."""

    id: str = field(default_factory=lambda: f"st_{uuid.uuid4().hex[:12]}")
    name: str = ""
    min_capital: float = 0.0
    max_capital: float = 0.0
    min_win_rate: float = 0.0
    min_sharpe: float = 0.0
    approval_required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "min_capital": self.min_capital,
            "max_capital": self.max_capital,
            "min_win_rate": self.min_win_rate,
            "min_sharpe": self.min_sharpe,
            "approval_required": self.approval_required,
        }


@dataclass
class ScalingDecision:
    """Decisão de escalonamento de capital."""

    id: str = field(default_factory=lambda: f"sd_{uuid.uuid4().hex[:12]}")
    current_tier: str = ""
    proposed_tier: str = ""
    approved: bool = False
    rollback_triggered: bool = False
    reason: str = ""
    metrics: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "current_tier": self.current_tier,
            "proposed_tier": self.proposed_tier,
            "approved": self.approved,
            "rollback_triggered": self.rollback_triggered,
            "reason": self.reason,
            "metrics": self.metrics,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ScalingReport:
    """Relatório de escalonamento."""

    id: str = field(default_factory=lambda: f"sr_{uuid.uuid4().hex[:12]}")
    current_capital: float = 0.0
    current_tier: str = ""
    drawdown: float = 0.0
    status: str = "stable"
    decisions: List[ScalingDecision] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "current_capital": self.current_capital,
            "current_tier": self.current_tier,
            "drawdown": self.drawdown,
            "status": self.status,
            "decisions": [decision.to_dict() for decision in self.decisions],
            "created_at": self.created_at.isoformat(),
        }


class ControlledCapitalScaling:
    """
    Escalonamento controlado de capital.

    Implementa:
    - Tiers de capital
    - Gates de aprovação
    - Rollback por drawdown
    - Métricas de performance
    """

    def __init__(self, max_drawdown: float = 0.15):
        self._max_drawdown = max_drawdown
        self._current_capital = 1000.0
        self._current_tier_index = 0
        self._decisions: List[ScalingDecision] = []
        self._reports: List[ScalingReport] = []
        self._tiers: List[ScalingTier] = [
            ScalingTier(name="micro", min_capital=500, max_capital=2000, min_win_rate=0.45, min_sharpe=0.5),
            ScalingTier(name="small", min_capital=2000, max_capital=10000, min_win_rate=0.50, min_sharpe=0.8),
            ScalingTier(name="medium", min_capital=10000, max_capital=50000, min_win_rate=0.52, min_sharpe=1.0),
        ]

    def evaluate_performance(self, metrics: Dict[str, float]) -> ScalingDecision:
        """Avalia se o capital pode escalar ou deve regredir."""
        drawdown = metrics.get("drawdown", 0.0)
        win_rate = metrics.get("win_rate", 0.0)
        sharpe = metrics.get("sharpe", 0.0)

        current_tier = self._tiers[self._current_tier_index]
        decision = ScalingDecision(
            current_tier=current_tier.name,
            metrics={"drawdown": drawdown, "win_rate": win_rate, "sharpe": sharpe},
        )

        if drawdown >= self._max_drawdown:
            decision.rollback_triggered = True
            decision.reason = f"Drawdown {drawdown:.2%} exceeded limit {self._max_drawdown:.2%}"
            if self._current_tier_index > 0:
                self._current_tier_index -= 1
                decision.proposed_tier = self._tiers[self._current_tier_index].name
                self._current_capital = self._tiers[self._current_tier_index].max_capital
        elif (
            self._current_tier_index < len(self._tiers) - 1
            and win_rate >= current_tier.min_win_rate
            and sharpe >= current_tier.min_sharpe
        ):
            next_tier = self._tiers[self._current_tier_index + 1]
            decision.proposed_tier = next_tier.name
            decision.reason = "Performance metrics meet next tier requirements"
        else:
            decision.proposed_tier = current_tier.name
            decision.reason = "Performance stable at current tier"

        self._decisions.append(decision)
        return decision

    def approve_scaling(self, decision_id: str, approver_id: str) -> bool:
        """Aprova escalonamento proposto."""
        if not approver_id:
            return False

        for decision in self._decisions:
            if decision.id != decision_id or decision.rollback_triggered:
                continue
            if decision.proposed_tier == decision.current_tier:
                return False

            for index, tier in enumerate(self._tiers):
                if tier.name == decision.proposed_tier and index == self._current_tier_index + 1:
                    decision.approved = True
                    self._current_tier_index = index
                    self._current_capital = tier.max_capital
                    return True
        return False

    def rollback(self, reason: str) -> ScalingDecision:
        """Executa rollback imediato de tier."""
        current_tier = self._tiers[self._current_tier_index]
        decision = ScalingDecision(
            current_tier=current_tier.name,
            proposed_tier=self._tiers[max(self._current_tier_index - 1, 0)].name,
            rollback_triggered=True,
            approved=True,
            reason=reason,
        )
        if self._current_tier_index > 0:
            self._current_tier_index -= 1
            self._current_capital = self._tiers[self._current_tier_index].max_capital
        self._decisions.append(decision)
        return decision

    def generate_scaling_report(self) -> ScalingReport:
        """Gera relatório de escalonamento."""
        latest_metrics = self._decisions[-1].metrics if self._decisions else {}
        report = ScalingReport(
            current_capital=self._current_capital,
            current_tier=self._tiers[self._current_tier_index].name,
            drawdown=latest_metrics.get("drawdown", 0.0),
            status="rollback" if any(d.rollback_triggered for d in self._decisions[-3:]) else "stable",
            decisions=self._decisions[-5:],
        )
        self._reports.append(report)
        return report

    def get_scaling_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de escalonamento."""
        return {
            "current_capital": self._current_capital,
            "current_tier": self._tiers[self._current_tier_index].name,
            "tiers": [tier.to_dict() for tier in self._tiers],
            "total_decisions": len(self._decisions),
            "latest_decision": self._decisions[-1].to_dict() if self._decisions else None,
            "latest_report": self._reports[-1].to_dict() if self._reports else None,
        }
