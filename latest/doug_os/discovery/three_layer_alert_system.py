"""Mission 336 — Three-Layer Alert System: valida cada sinal em 3 camadas antes de liberar."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class LayerResult:
    layer: int = 0
    name: str = ""
    passed: bool = False
    score: float = 0.0
    threshold: float = 0.0
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer": self.layer,
            "name": self.name,
            "passed": self.passed,
            "score": round(self.score, 4),
            "threshold": self.threshold,
            "reason": self.reason,
        }


@dataclass
class AlertDecision:
    id: str = field(default_factory=lambda: f"ad_{uuid.uuid4().hex[:12]}")
    signal: Dict[str, Any] = field(default_factory=dict)
    approved: bool = False
    blocked_at_layer: int = 0          # 0 = não bloqueado
    layers: List[LayerResult] = field(default_factory=list)
    final_reason: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "signal": self.signal,
            "approved": self.approved,
            "blocked_at_layer": self.blocked_at_layer,
            "layers": [l.to_dict() for l in self.layers],
            "final_reason": self.final_reason,
            "created_at": self.created_at.isoformat(),
        }


class ThreeLayerAlertSystem:
    """
    Valida qualquer sinal de trading em 3 camadas sequenciais:

    Camada 1 — ScientificEvidenceRanking: evidence_score ≥ evidence_threshold
    Camada 2 — MultiModelConsensusEngine: agreement_score ≥ consensus_threshold
    Camada 3 — FormalDecisionVerification: risk_pct ≤ max_risk_pct

    Qualquer falha bloqueia imediatamente. Zero exceções.
    """

    def __init__(
        self,
        evidence_threshold: float = 0.75,
        consensus_threshold: float = 0.70,
        max_risk_pct: float = 2.0,
    ) -> None:
        self._evidence_threshold = evidence_threshold
        self._consensus_threshold = consensus_threshold
        self._max_risk_pct = max_risk_pct
        self._decisions: List[AlertDecision] = []

    # ------------------------------------------------------------------ #
    #  Evaluate                                                            #
    # ------------------------------------------------------------------ #

    def evaluate(self, signal: Dict[str, Any]) -> AlertDecision:
        """
        signal deve conter:
            evidence_score   (float 0–1)
            agreement_score  (float 0–1)
            risk_pct         (float, % do capital em risco)
        """
        decision = AlertDecision(signal=signal)
        layers: List[LayerResult] = []

        # ── Camada 1: Evidência Científica ───────────────────────────────
        ev_score = float(signal.get("evidence_score", 0.0))
        l1 = LayerResult(
            layer=1,
            name="ScientificEvidence",
            score=ev_score,
            threshold=self._evidence_threshold,
            passed=ev_score >= self._evidence_threshold,
            reason="" if ev_score >= self._evidence_threshold
                    else f"evidence_score {ev_score:.3f} < {self._evidence_threshold}",
        )
        layers.append(l1)

        if not l1.passed:
            decision.approved = False
            decision.blocked_at_layer = 1
            decision.layers = layers
            decision.final_reason = l1.reason
            self._decisions.append(decision)
            return decision

        # ── Camada 2: Consenso Multi-Modelo ─────────────────────────────
        ag_score = float(signal.get("agreement_score", 0.0))
        l2 = LayerResult(
            layer=2,
            name="MultiModelConsensus",
            score=ag_score,
            threshold=self._consensus_threshold,
            passed=ag_score >= self._consensus_threshold,
            reason="" if ag_score >= self._consensus_threshold
                    else f"agreement_score {ag_score:.3f} < {self._consensus_threshold}",
        )
        layers.append(l2)

        if not l2.passed:
            decision.approved = False
            decision.blocked_at_layer = 2
            decision.layers = layers
            decision.final_reason = l2.reason
            self._decisions.append(decision)
            return decision

        # ── Camada 3: Verificação Formal de Risco ───────────────────────
        risk_pct = float(signal.get("risk_pct", 0.0))
        l3 = LayerResult(
            layer=3,
            name="FormalRiskVerification",
            score=risk_pct,
            threshold=self._max_risk_pct,
            passed=risk_pct <= self._max_risk_pct,
            reason="" if risk_pct <= self._max_risk_pct
                    else f"risk_pct {risk_pct:.2f}% > max {self._max_risk_pct}%",
        )
        layers.append(l3)

        if not l3.passed:
            decision.approved = False
            decision.blocked_at_layer = 3
            decision.layers = layers
            decision.final_reason = l3.reason
            self._decisions.append(decision)
            return decision

        # Todas as camadas passaram
        decision.approved = True
        decision.blocked_at_layer = 0
        decision.layers = layers
        decision.final_reason = "Aprovado em todas as 3 camadas"
        self._decisions.append(decision)
        return decision

    # ------------------------------------------------------------------ #
    #  Introspection                                                       #
    # ------------------------------------------------------------------ #

    def get_stats(self) -> Dict[str, Any]:
        total = len(self._decisions)
        if total == 0:
            return {"total": 0, "approved": 0, "blocked": 0, "approval_rate": 0.0,
                    "blocked_at": {1: 0, 2: 0, 3: 0}}
        approved = sum(1 for d in self._decisions if d.approved)
        blocked_at = {1: 0, 2: 0, 3: 0}
        for d in self._decisions:
            if d.blocked_at_layer > 0:
                blocked_at[d.blocked_at_layer] = blocked_at.get(d.blocked_at_layer, 0) + 1
        return {
            "total": total,
            "approved": approved,
            "blocked": total - approved,
            "approval_rate": round(approved / total, 4),
            "blocked_at": blocked_at,
        }

    def get_history(self, approved_only: bool = False, limit: int = 100) -> List[Dict[str, Any]]:
        decisions = self._decisions
        if approved_only:
            decisions = [d for d in decisions if d.approved]
        return [d.to_dict() for d in decisions[-limit:]]
