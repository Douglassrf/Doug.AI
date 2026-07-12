# ============================================================
# MISSÃO 296 — COGNITIVE RISK BALANCER (stub mínimo)
# Fase XIX — Meta-Cognitive Trading Intelligence
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class CognitiveRiskBalance:
    """Balanceamento de risco com camada meta-cognitiva."""
    id: str = field(default_factory=lambda: f"crb_{uuid.uuid4().hex[:12]}")
    portfolio_id: str = ""
    base_risk: float = 0.0
    cognitive_adjustment: float = 0.0
    adjusted_risk: float = 0.0
    exposure_limit: float = 0.0
    recommendation: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "portfolio_id": self.portfolio_id,
            "base_risk": self.base_risk,
            "cognitive_adjustment": self.cognitive_adjustment,
            "adjusted_risk": self.adjusted_risk,
            "exposure_limit": self.exposure_limit,
            "recommendation": self.recommendation,
            "created_at": self.created_at.isoformat(),
        }


class CognitiveRiskBalancer:
    """Ajusta risco com base em viés, incerteza e confiabilidade."""

    def __init__(self):
        self._balances: List[CognitiveRiskBalance] = []
        self._max_exposure = 1.0

    def balance(
        self,
        portfolio_id: str,
        base_risk: float,
        cognitive_factors: Dict[str, float],
    ) -> CognitiveRiskBalance:
        bias_penalty = cognitive_factors.get("bias_score", 0.0) * 0.2
        uncertainty_penalty = cognitive_factors.get("uncertainty_score", 0.0) * 0.3
        reliability_bonus = cognitive_factors.get("reliability_score", 0.5) * 0.1

        cognitive_adjustment = reliability_bonus - bias_penalty - uncertainty_penalty
        adjusted_risk = min(max(base_risk + cognitive_adjustment, 0.0), self._max_exposure)
        exposure_limit = max(0.1, self._max_exposure - adjusted_risk)

        recommendation = (
            "Reduce exposure — elevated cognitive risk"
            if adjusted_risk > 0.7
            else "Risk within cognitive tolerance"
        )

        balance = CognitiveRiskBalance(
            portfolio_id=portfolio_id,
            base_risk=base_risk,
            cognitive_adjustment=cognitive_adjustment,
            adjusted_risk=adjusted_risk,
            exposure_limit=exposure_limit,
            recommendation=recommendation,
        )
        self._balances.append(balance)
        return balance

    def get_risk_dashboard(self) -> Dict[str, Any]:
        if not self._balances:
            return {"status": "no_balances"}

        return {
            "balances": len(self._balances),
            "avg_adjusted_risk": np.mean([b.adjusted_risk for b in self._balances]),
            "avg_exposure_limit": np.mean([b.exposure_limit for b in self._balances]),
            "recent_balances": [b.to_dict() for b in self._balances[-5:]],
        }
