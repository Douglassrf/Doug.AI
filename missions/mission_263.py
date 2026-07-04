# ============================================================
# MISSÃO 263 — ALPHA PORTFOLIO COMPOSER (stub mínimo)
# Fase XVI — Alpha Generation Intelligence
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class AlphaAllocation:
    """Alocação de alpha no portfólio."""
    id: str = field(default_factory=lambda: f"aa_{uuid.uuid4().hex[:12]}")
    alpha_id: str = ""
    weight: float = 0.0
    expected_return: float = 0.0
    risk_contribution: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "alpha_id": self.alpha_id,
            "weight": self.weight,
            "expected_return": self.expected_return,
            "risk_contribution": self.risk_contribution,
            "created_at": self.created_at.isoformat(),
        }


class AlphaPortfolioComposer:
    """Compõe portfólio a partir de alphas descobertos."""

    def __init__(self):
        self._allocations: List[AlphaAllocation] = []

    def compose(
        self,
        alphas: List[Dict[str, Any]],
        max_weight: float = 0.25,
    ) -> List[AlphaAllocation]:
        if not alphas:
            return []

        scores = [max(a.get("score", 0.0), 0.0) for a in alphas]
        total = sum(scores) or 1.0
        allocations: List[AlphaAllocation] = []

        for alpha, score in zip(alphas, scores):
            weight = min(max_weight, score / total)
            allocations.append(
                AlphaAllocation(
                    alpha_id=alpha.get("id", ""),
                    weight=weight,
                    expected_return=alpha.get("score", 0.0) * 0.1,
                    risk_contribution=weight * alpha.get("correlation_to_market", 0.0),
                )
            )

        self._allocations = allocations
        return allocations

    def get_portfolio_dashboard(self) -> Dict[str, Any]:
        weights = [a.weight for a in self._allocations]
        return {
            "allocations": len(self._allocations),
            "total_weight": sum(weights),
            "avg_expected_return": np.mean([a.expected_return for a in self._allocations]) if self._allocations else 0,
        }
