# ============================================================
# MISSÃO 283 — PRECISION EXIT ENGINE (stub mínimo)
# Fase XVIII — Quantum Trading Intelligence
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class ExitDecision:
    """Decisão de saída."""
    id: str = field(default_factory=lambda: f"xd_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    exit_price: float = 0.0
    probability: float = 0.0
    precision_score: float = 0.0
    reason: str = ""
    final_decision: str = "HOLD"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "exit_price": self.exit_price,
            "probability": self.probability,
            "precision_score": self.precision_score,
            "reason": self.reason,
            "final_decision": self.final_decision,
            "created_at": self.created_at.isoformat(),
        }


class PrecisionExitEngine:
    """Motor de saída de precisão — par complementar ao Precision Entry."""

    def __init__(self):
        self._decisions: List[ExitDecision] = []
        self._exit_threshold = 0.65

    def evaluate_exit(
        self,
        asset: str,
        exit_price: float,
        position_data: Dict[str, Any],
    ) -> ExitDecision:
        profit = position_data.get("profit_pct", 0.0)
        duration = position_data.get("duration_minutes", 0)
        score = min(0.5 + profit * 2 + (0.1 if duration > 60 else 0), 1.0)
        probability = min(max(profit + 0.5, 0.0), 1.0)
        final_decision = "EXIT" if score >= self._exit_threshold else "HOLD"
        reason = "take_profit" if profit > 0.02 else "monitor"

        decision = ExitDecision(
            asset=asset,
            exit_price=exit_price,
            probability=probability,
            precision_score=score,
            reason=reason,
            final_decision=final_decision,
        )
        self._decisions.append(decision)
        return decision

    def get_exit_dashboard(self) -> Dict[str, Any]:
        return {
            "total_decisions": len(self._decisions),
            "exit_decisions": sum(1 for d in self._decisions if d.final_decision == "EXIT"),
            "avg_precision": np.mean([d.precision_score for d in self._decisions]) if self._decisions else 0,
        }
