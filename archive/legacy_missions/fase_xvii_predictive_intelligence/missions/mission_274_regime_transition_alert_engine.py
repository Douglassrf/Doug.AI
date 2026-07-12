# ============================================================
# MISSÃO 274 — REGIME TRANSITION ALERT ENGINE (stub mínimo)
# Fase XVII — Predictive Intelligence Architecture
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class RegimeAlert:
    """Alerta de transição de regime."""
    id: str = field(default_factory=lambda: f"ra_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    from_regime: str = ""
    to_regime: str = ""
    severity: str = "info"
    probability: float = 0.0
    message: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "from_regime": self.from_regime,
            "to_regime": self.to_regime,
            "severity": self.severity,
            "probability": self.probability,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
        }


class RegimeTransitionAlertEngine:
    """Emite alertas quando transições de regime são detectadas."""

    def __init__(self):
        self._alerts: List[RegimeAlert] = []

    def evaluate(
        self,
        asset: str,
        current_regime: str,
        predicted_regime: str,
        transition_probability: float,
    ) -> RegimeAlert:
        if current_regime == predicted_regime:
            severity = "info"
            message = f"Regime stable: {current_regime}"
        elif transition_probability > 0.6:
            severity = "critical"
            message = f"High probability transition {current_regime} -> {predicted_regime}"
        elif transition_probability > 0.35:
            severity = "warning"
            message = f"Possible transition {current_regime} -> {predicted_regime}"
        else:
            severity = "info"
            message = f"Low probability transition to {predicted_regime}"

        alert = RegimeAlert(
            asset=asset,
            from_regime=current_regime,
            to_regime=predicted_regime,
            severity=severity,
            probability=transition_probability,
            message=message,
        )
        self._alerts.append(alert)
        return alert

    def get_alert_dashboard(self) -> Dict[str, Any]:
        return {
            "total_alerts": len(self._alerts),
            "critical": sum(1 for a in self._alerts if a.severity == "critical"),
            "warning": sum(1 for a in self._alerts if a.severity == "warning"),
            "recent_alerts": [a.to_dict() for a in self._alerts[-5:]],
        }
