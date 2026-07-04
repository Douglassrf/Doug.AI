from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List
import numpy as np


@dataclass
class RealityTwinReport:
    prediction: Dict[str, Any] = field(default_factory=dict)
    actual: Dict[str, Any] = field(default_factory=dict)
    error: float = 0.0
    drift: float = 0.0
    divergence_alert: bool = False
    divergence_reason: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prediction": self.prediction, "actual": self.actual,
            "error": self.error, "drift": self.drift,
            "divergence_alert": self.divergence_alert,
            "divergence_reason": self.divergence_reason,
            "created_at": self.created_at.isoformat(),
        }


class RealityTwin:
    """Compara previsão vs mundo real e alerta sobre divergências."""

    ALERT_THRESHOLD = 0.3

    def __init__(self):
        self._history: List[RealityTwinReport] = []

    def compare(self, prediction: Dict[str, Any], actual: Dict[str, Any]) -> RealityTwinReport:
        error = self._calculate_error(prediction, actual)
        drift = self._calculate_drift(error)
        divergence = error > self.ALERT_THRESHOLD or drift > self.ALERT_THRESHOLD
        reason = self._explain_divergence(prediction, actual) if divergence else ""
        r = RealityTwinReport(
            prediction=prediction, actual=actual,
            error=error, drift=drift,
            divergence_alert=divergence, divergence_reason=reason,
        )
        self._history.append(r)
        return r

    def _calculate_error(self, prediction: Dict, actual: Dict) -> float:
        pred = prediction.get("value", 0)
        act = actual.get("value", 0)
        if pred == 0: return 0.0
        return abs(pred - act) / abs(pred)

    def _calculate_drift(self, current_error: float) -> float:
        if not self._history: return 0.0
        return max(0.0, current_error - self._history[-1].error)

    def _explain_divergence(self, prediction: Dict, actual: Dict) -> str:
        reasons = []
        for key in set(prediction) & set(actual):
            pv, av = prediction[key], actual[key]
            if isinstance(pv, (int, float)) and isinstance(av, (int, float)):
                if pv != 0 and abs(pv - av) / abs(pv) > 0.1:
                    reasons.append(f"{key} diverged by {abs(pv - av):.4f}")
        return "; ".join(reasons) if reasons else "Unknown divergence"

    def get_alerts(self) -> List[RealityTwinReport]:
        return [r for r in self._history if r.divergence_alert]
