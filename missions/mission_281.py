# ============================================================
# MISSÃO 281 — CAPITAL PRESERVATION AI
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class CapitalHealth:
    """Saúde do capital."""
    id: str = field(default_factory=lambda: f"ch_{uuid.uuid4().hex[:12]}")
    total_capital: float = 0.0
    exposed_capital: float = 0.0
    health_score: float = 0.0
    drawdown: float = 0.0
    max_drawdown_allowed: float = 0.0
    survival_probability: float = 0.0
    recovery_recommendation: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "total_capital": self.total_capital,
            "exposed_capital": self.exposed_capital,
            "health_score": self.health_score,
            "drawdown": self.drawdown,
            "max_drawdown_allowed": self.max_drawdown_allowed,
            "survival_probability": self.survival_probability,
            "recovery_recommendation": self.recovery_recommendation,
            "created_at": self.created_at.isoformat(),
        }


class CapitalPreservationAI:
    """
    IA de preservação de capital.

    Implementa:
    - Capital Health Score
    - Exposure Monitor
    - Equity Protection
    - Dynamic Risk Limit
    - Emergency Protection
    - Drawdown Shield
    - Capital Forecast
    - Survival Probability
    - Recovery Advisor
    - Dashboard
    """

    def __init__(self, max_drawdown: float = 0.2):
        self._max_drawdown_allowed = max_drawdown
        self._health_history: List[CapitalHealth] = []
        self._equity_history: List[float] = []
        self._drawdown_shield_active = False

    def monitor_capital(
        self,
        total_capital: float,
        exposed_capital: float,
        equity_curve: List[float],
    ) -> CapitalHealth:
        current_drawdown = self._calculate_drawdown(equity_curve)
        health_score = self._calculate_health_score(total_capital, exposed_capital, current_drawdown)
        survival_prob = self._calculate_survival_probability(total_capital, current_drawdown)
        recovery_rec = self._generate_recovery_recommendation(current_drawdown, health_score)

        if current_drawdown > self._max_drawdown_allowed * 0.8:
            self._drawdown_shield_active = True
        else:
            self._drawdown_shield_active = False

        health = CapitalHealth(
            total_capital=total_capital,
            exposed_capital=exposed_capital,
            health_score=health_score,
            drawdown=current_drawdown,
            max_drawdown_allowed=self._max_drawdown_allowed,
            survival_probability=survival_prob,
            recovery_recommendation=recovery_rec,
        )

        self._health_history.append(health)
        self._equity_history.extend(equity_curve[-10:])
        return health

    def _calculate_drawdown(self, equity: List[float]) -> float:
        if len(equity) < 2:
            return 0.0

        peak = max(equity)
        current = equity[-1]
        return (peak - current) / peak if peak > 0 else 0.0

    def _calculate_health_score(self, capital: float, exposed: float, drawdown: float) -> float:
        exposure_ratio = exposed / capital if capital > 0 else 0
        exposure_score = 1 - min(exposure_ratio, 1.0)
        dd_penalty = drawdown / self._max_drawdown_allowed
        health = exposure_score * 0.6 + (1 - min(dd_penalty, 1.0)) * 0.4
        return min(max(health, 0.0), 1.0)

    def _calculate_survival_probability(self, capital: float, drawdown: float) -> float:
        if drawdown == 0:
            return 1.0
        survival = 1 - (drawdown / self._max_drawdown_allowed)
        return min(max(survival, 0.0), 1.0)

    def _generate_recovery_recommendation(self, drawdown: float, health: float) -> str:
        if drawdown > self._max_drawdown_allowed * 0.9:
            return "EMERGENCY: Halt all trading. Immediate capital protection required."
        if drawdown > self._max_drawdown_allowed * 0.7:
            return "WARNING: Reduce position sizes by 50%. Monitor drawdown closely."
        if drawdown > self._max_drawdown_allowed * 0.5:
            return "CAUTION: Reduce position sizes by 30%. Consider profit taking."
        if health < 0.5:
            return "REVIEW: Capital health below threshold. Reassess risk parameters."
        return "NORMAL: Capital health acceptable. Continue with current risk parameters."

    def get_capital_dashboard(self) -> Dict[str, Any]:
        if not self._health_history:
            return {"status": "no_data"}

        latest = self._health_history[-1]

        return {
            "current_capital": latest.total_capital,
            "exposed_capital": latest.exposed_capital,
            "health_score": latest.health_score,
            "drawdown": latest.drawdown,
            "survival_probability": latest.survival_probability,
            "drawdown_shield_active": self._drawdown_shield_active,
            "recovery_recommendation": latest.recovery_recommendation,
            "health_history": [h.to_dict() for h in self._health_history[-10:]],
        }
