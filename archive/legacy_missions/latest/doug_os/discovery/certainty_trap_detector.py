from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid


@dataclass
class CertaintyTrapAlert:
    id: str = field(default_factory=lambda: f"ct_{uuid.uuid4().hex[:12]}")
    hypothesis_id: str = ""
    hypothesis_text: str = ""
    age_days: float = 0.0
    confidence_frozen: bool = False
    regime_changes: int = 0
    last_review: Optional[datetime] = None
    severity: str = "none"
    recommendation: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "hypothesis_id": self.hypothesis_id,
            "hypothesis_text": self.hypothesis_text, "age_days": self.age_days,
            "confidence_frozen": self.confidence_frozen, "regime_changes": self.regime_changes,
            "last_review": self.last_review.isoformat() if self.last_review else None,
            "severity": self.severity, "recommendation": self.recommendation,
            "created_at": self.created_at.isoformat(),
        }


class CertaintyTrapDetector:
    """Impede que hipóteses sejam tratadas como verdades absolutas pelo passar do tempo."""

    def __init__(self):
        self._alerts: Dict[str, CertaintyTrapAlert] = {}

    def check(
        self,
        hypothesis_id: str,
        hypothesis_text: str,
        created_at: datetime,
        last_review: Optional[datetime],
        current_regime: str,
        regime_history: List[str],
    ) -> CertaintyTrapAlert:
        age = (datetime.now(timezone.utc) - created_at).total_seconds() / 86400.0
        regime_changes = len(set(regime_history)) - 1
        frozen = last_review is None or (datetime.now(timezone.utc) - last_review).days > 30
        severity = self._determine_severity(age, regime_changes, frozen)
        rec = self._recommendation(severity, age, regime_changes)
        alert = CertaintyTrapAlert(
            hypothesis_id=hypothesis_id, hypothesis_text=hypothesis_text,
            age_days=age, confidence_frozen=frozen, regime_changes=regime_changes,
            last_review=last_review, severity=severity, recommendation=rec,
        )
        self._alerts[hypothesis_id] = alert
        return alert

    def _determine_severity(self, age: float, regime_changes: int, frozen: bool) -> str:
        if age > 365 and regime_changes > 3 and frozen: return "critical"
        if age > 180 and regime_changes > 2 and frozen: return "high"
        if age > 90 and regime_changes > 1: return "medium"
        if age > 30: return "low"
        return "none"

    def _recommendation(self, severity: str, age: float, regime_changes: int) -> str:
        if severity == "critical":
            return f"Hypothesis {age:.0f} days old with {regime_changes} regime changes. Mandatory review."
        if severity == "high": return f"Immediate review needed. Age: {age:.0f} days."
        if severity == "medium": return f"Schedule review. Age: {age:.0f} days."
        if severity == "low": return "Consider periodic review."
        return "No action needed."

    def get_stale_hypotheses(self, max_age_days: int = 90) -> List[str]:
        return [hid for hid, a in self._alerts.items() if a.age_days > max_age_days]
