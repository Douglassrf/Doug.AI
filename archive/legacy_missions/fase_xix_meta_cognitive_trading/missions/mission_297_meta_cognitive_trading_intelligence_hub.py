# ============================================================
# MISSÃO 297 — META-COGNITIVE TRADING INTELLIGENCE HUB (stub mínimo)
# Fase XIX — Meta-Cognitive Trading Intelligence
# ============================================================

from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class MetaCognitiveTradingSnapshot:
    """Snapshot consolidado da fase Meta-Cognitive Trading Intelligence."""
    id: str = field(default_factory=lambda: f"mcts_{uuid.uuid4().hex[:12]}")
    meta_cognition: Dict[str, Any] = field(default_factory=dict)
    bias: Dict[str, Any] = field(default_factory=dict)
    uncertainty: Dict[str, Any] = field(default_factory=dict)
    regime: Dict[str, Any] = field(default_factory=dict)
    signal_reliability: Dict[str, Any] = field(default_factory=dict)
    opportunity: Dict[str, Any] = field(default_factory=dict)
    orchestrator: Dict[str, Any] = field(default_factory=dict)
    meta_learning: Dict[str, Any] = field(default_factory=dict)
    risk_balance: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "meta_cognition": self.meta_cognition,
            "bias": self.bias,
            "uncertainty": self.uncertainty,
            "regime": self.regime,
            "signal_reliability": self.signal_reliability,
            "opportunity": self.opportunity,
            "orchestrator": self.orchestrator,
            "meta_learning": self.meta_learning,
            "risk_balance": self.risk_balance,
            "created_at": self.created_at.isoformat(),
        }


class MetaCognitiveTradingIntelligenceHub:
    """Hub central que agrega dashboards das missões 288-296."""

    def __init__(self):
        self._snapshots: list[MetaCognitiveTradingSnapshot] = []

    def aggregate(self, dashboards: Dict[str, Dict[str, Any]]) -> MetaCognitiveTradingSnapshot:
        snapshot = MetaCognitiveTradingSnapshot(
            meta_cognition=dashboards.get("meta_cognition", {}),
            bias=dashboards.get("bias", {}),
            uncertainty=dashboards.get("uncertainty", {}),
            regime=dashboards.get("regime", {}),
            signal_reliability=dashboards.get("signal_reliability", {}),
            opportunity=dashboards.get("opportunity", {}),
            orchestrator=dashboards.get("orchestrator", {}),
            meta_learning=dashboards.get("meta_learning", {}),
            risk_balance=dashboards.get("risk_balance", {}),
        )
        self._snapshots.append(snapshot)
        return snapshot

    def get_hub_dashboard(self) -> Dict[str, Any]:
        latest = self._snapshots[-1].to_dict() if self._snapshots else {}
        module_keys = [
            "meta_cognition",
            "bias",
            "uncertainty",
            "regime",
            "signal_reliability",
            "opportunity",
            "orchestrator",
            "meta_learning",
            "risk_balance",
        ]
        return {
            "snapshots": len(self._snapshots),
            "latest": latest,
            "modules_active": sum(1 for key in module_keys if latest.get(key)),
        }
