# ============================================================
# MISSÃO 293 — STRATEGIC OPPORTUNITY OPTIMIZER
# Fase XIX — Meta-Cognitive Trading Intelligence
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class StrategicOpportunity:
    """Oportunidade estratégica otimizada."""
    id: str = field(default_factory=lambda: f"so_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    direction: str = "neutral"
    expected_return: float = 0.0
    risk_adjusted_score: float = 0.0
    confidence: float = 0.0
    priority_rank: int = 0
    allocation_pct: float = 0.0
    rationale: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "direction": self.direction,
            "expected_return": self.expected_return,
            "risk_adjusted_score": self.risk_adjusted_score,
            "confidence": self.confidence,
            "priority_rank": self.priority_rank,
            "allocation_pct": self.allocation_pct,
            "rationale": self.rationale,
            "created_at": self.created_at.isoformat(),
        }


class StrategicOpportunityOptimizer:
    """
    Otimizador de oportunidades estratégicas.

    Implementa:
    - Opportunity Scoring
    - Risk-Adjusted Ranking
    - Capital Allocation
    - Multi-Asset Prioritization
    - Confidence Weighting
    - Opportunity Dashboard
    """

    def __init__(self):
        self._opportunities: List[StrategicOpportunity] = []
        self._min_score = 0.4

    def optimize(
        self,
        candidates: List[Dict[str, Any]],
        total_capital: float = 100000.0,
        max_allocation_pct: float = 0.25,
    ) -> List[StrategicOpportunity]:
        """Ranqueia e aloca capital entre oportunidades candidatas."""
        scored: List[StrategicOpportunity] = []

        for candidate in candidates:
            asset = candidate.get("asset", "")
            direction = candidate.get("direction", "neutral")
            expected_return = candidate.get("expected_return", 0.0)
            risk = max(candidate.get("risk", 0.3), 0.01)
            confidence = min(max(candidate.get("confidence", 0.5), 0.0), 1.0)

            risk_adjusted = (expected_return / risk) * confidence
            rationale = self._build_rationale(direction, expected_return, risk, confidence)

            scored.append(
                StrategicOpportunity(
                    asset=asset,
                    direction=direction,
                    expected_return=expected_return,
                    risk_adjusted_score=risk_adjusted,
                    confidence=confidence,
                    rationale=rationale,
                )
            )

        scored.sort(key=lambda o: o.risk_adjusted_score, reverse=True)

        for rank, opportunity in enumerate(scored, start=1):
            opportunity.priority_rank = rank

        eligible = [o for o in scored if o.risk_adjusted_score >= self._min_score]
        allocation_targets = eligible if eligible else scored

        weights = np.array([max(o.risk_adjusted_score, 0.01) for o in allocation_targets])
        weights = weights / weights.sum()
        capped = np.minimum(weights, max_allocation_pct)
        capped = capped / capped.sum()

        for opportunity, allocation in zip(allocation_targets, capped):
            opportunity.allocation_pct = float(allocation)
            opportunity.rationale += (
                f" | rank={opportunity.priority_rank} alloc={allocation:.2%}"
            )

        self._opportunities.extend(scored)
        return scored

    def _build_rationale(
        self, direction: str, expected_return: float, risk: float, confidence: float
    ) -> str:
        if expected_return <= 0:
            return f"Low return profile for {direction}"
        if risk > 0.6:
            return f"High risk {direction} setup — reduce size"
        if confidence > 0.7:
            return f"Strong {direction} opportunity with calibrated confidence"
        return f"Moderate {direction} opportunity — monitor confirmation"

    def get_top_opportunities(self, limit: int = 5) -> List[StrategicOpportunity]:
        """Retorna top oportunidades por score ajustado ao risco."""
        ranked = sorted(
            self._opportunities,
            key=lambda o: o.risk_adjusted_score,
            reverse=True,
        )
        return ranked[:limit]

    def get_optimizer_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard do otimizador."""
        if not self._opportunities:
            return {"status": "no_opportunities"}

        return {
            "total_opportunities": len(self._opportunities),
            "eligible_opportunities": sum(
                1 for o in self._opportunities if o.risk_adjusted_score >= self._min_score
            ),
            "avg_risk_adjusted_score": np.mean([o.risk_adjusted_score for o in self._opportunities]),
            "avg_confidence": np.mean([o.confidence for o in self._opportunities]),
            "total_allocation_pct": sum(o.allocation_pct for o in self._opportunities),
            "top_opportunities": [o.to_dict() for o in self.get_top_opportunities()],
        }
