# ============================================================
# MISSÃO 282 — PRECISION ENTRY ENGINE
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class EntryDecision:
    """Decisão de entrada."""
    id: str = field(default_factory=lambda: f"ed_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    entry_price: float = 0.0
    probability: float = 0.0
    precision_score: float = 0.0
    confirmations: List[Dict[str, Any]] = field(default_factory=list)
    final_decision: str = "NO_GO"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "entry_price": self.entry_price,
            "probability": self.probability,
            "precision_score": self.precision_score,
            "confirmations": self.confirmations,
            "final_decision": self.final_decision,
            "created_at": self.created_at.isoformat(),
        }


class PrecisionEntryEngine:
    """
    Motor de entrada de precisão.

    Implementa:
    - Entry Probability
    - Multi Confirmation
    - Liquidity Confirmation
    - Timing Confirmation
    - Institutional Confirmation
    - Regime Confirmation
    - Precision Score
    - Entry Simulator
    - Entry Analytics
    - Dashboard
    """

    def __init__(self):
        self._decisions: List[EntryDecision] = []
        self._precision_threshold = 0.7
        self._confirmation_weights = {
            "liquidity": 0.25,
            "timing": 0.20,
            "institutional": 0.25,
            "regime": 0.30,
        }

    def evaluate_entry(
        self,
        asset: str,
        entry_price: float,
        market_data: Dict[str, Any],
        confirmations: Dict[str, bool],
    ) -> EntryDecision:
        """Avalia entrada com multi-confirmação."""
        conf_list = self._build_confirmations(market_data, confirmations)
        probability = self._calculate_entry_probability(conf_list, market_data)
        precision_score = self._calculate_precision_score(conf_list, market_data)
        final_decision = "GO" if precision_score >= self._precision_threshold else "NO_GO"

        decision = EntryDecision(
            asset=asset,
            entry_price=entry_price,
            probability=probability,
            precision_score=precision_score,
            confirmations=conf_list,
            final_decision=final_decision,
        )
        self._decisions.append(decision)
        return decision

    def _build_confirmations(
        self,
        market_data: Dict[str, Any],
        confirmations: Dict[str, bool],
    ) -> List[Dict[str, Any]]:
        result = []

        liquidity_ok = confirmations.get("liquidity", False) or market_data.get("liquidity", 0) > 0.6
        result.append({
            "type": "liquidity",
            "passed": liquidity_ok,
            "score": market_data.get("liquidity", 0.5) if liquidity_ok else 0.3,
        })

        timing_ok = confirmations.get("timing", False) or market_data.get("timing_score", 0) > 0.5
        result.append({
            "type": "timing",
            "passed": timing_ok,
            "score": market_data.get("timing_score", 0.5) if timing_ok else 0.3,
        })

        institutional_ok = confirmations.get("institutional", False) or market_data.get("institutional_score", 0) > 0.5
        result.append({
            "type": "institutional",
            "passed": institutional_ok,
            "score": market_data.get("institutional_score", 0.5) if institutional_ok else 0.3,
        })

        regime_ok = confirmations.get("regime", False) or market_data.get("regime_favorable", False)
        result.append({
            "type": "regime",
            "passed": regime_ok,
            "score": market_data.get("regime_score", 0.5) if regime_ok else 0.3,
        })

        return result

    def _calculate_entry_probability(
        self,
        confirmations: List[Dict[str, Any]],
        market_data: Dict[str, Any],
    ) -> float:
        passed = sum(1 for c in confirmations if c.get("passed"))
        base_prob = passed / len(confirmations) if confirmations else 0.0
        momentum_boost = market_data.get("momentum", 0.0) * 0.2
        return min(base_prob + momentum_boost, 1.0)

    def _calculate_precision_score(
        self,
        confirmations: List[Dict[str, Any]],
        market_data: Dict[str, Any],
    ) -> float:
        weighted = 0.0
        for conf in confirmations:
            weight = self._confirmation_weights.get(conf.get("type", ""), 0.25)
            weighted += conf.get("score", 0.0) * weight

        volatility_penalty = abs(market_data.get("volatility", 0.3) - 0.3) * 0.2
        return min(max(weighted - volatility_penalty, 0.0), 1.0)

    def simulate_entry(
        self,
        asset: str,
        entry_price: float,
        market_data: Dict[str, Any],
        confirmations: Dict[str, bool],
    ) -> Dict[str, Any]:
        """Simula entrada sem registrar decisão final."""
        conf_list = self._build_confirmations(market_data, confirmations)
        precision_score = self._calculate_precision_score(conf_list, market_data)
        probability = self._calculate_entry_probability(conf_list, market_data)

        return {
            "asset": asset,
            "entry_price": entry_price,
            "simulated_probability": probability,
            "simulated_precision": precision_score,
            "would_go": precision_score >= self._precision_threshold,
            "confirmations": conf_list,
        }

    def get_entry_dashboard(self) -> Dict[str, Any]:
        go_count = sum(1 for d in self._decisions if d.final_decision == "GO")
        return {
            "total_decisions": len(self._decisions),
            "go_decisions": go_count,
            "no_go_decisions": len(self._decisions) - go_count,
            "avg_precision": np.mean([d.precision_score for d in self._decisions]) if self._decisions else 0,
            "avg_probability": np.mean([d.probability for d in self._decisions]) if self._decisions else 0,
            "recent_decisions": [d.to_dict() for d in self._decisions[-5:]],
        }
