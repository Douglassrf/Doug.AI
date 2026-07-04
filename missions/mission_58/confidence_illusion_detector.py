from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List
import uuid


@dataclass
class ConfidenceIllusionReport:
    id: str = field(default_factory=lambda: f"ill_{uuid.uuid4().hex[:12]}")
    hypothesis_id: str = ""
    declared_confidence: float = 0.0
    evidence_confidence: float = 0.0
    illusion_gap: float = 0.0
    severity: str = "none"
    evidence_quality: float = 0.0
    recommendation: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "hypothesis_id": self.hypothesis_id,
            "declared_confidence": self.declared_confidence,
            "evidence_confidence": self.evidence_confidence,
            "illusion_gap": self.illusion_gap, "severity": self.severity,
            "evidence_quality": self.evidence_quality,
            "recommendation": self.recommendation,
            "created_at": self.created_at.isoformat(),
        }


class ConfidenceIllusionDetector:
    """Detecta quando o sistema está confiante demais sem evidência suficiente."""

    _SEVERITY_THRESHOLDS = {"low": 0.15, "medium": 0.30, "high": 0.45, "critical": 0.60}

    def __init__(self):
        self._reports: List[ConfidenceIllusionReport] = []

    def analyze(self, hypothesis_id: str, declared_confidence: float, evidence: Dict[str, Any]) -> ConfidenceIllusionReport:
        ev_conf = self._calculate_evidence_confidence(evidence)
        gap = declared_confidence - ev_conf
        ev_quality = self._calculate_evidence_quality(evidence)
        severity = self._determine_severity(gap)
        rec = self._recommendation(severity)
        r = ConfidenceIllusionReport(
            hypothesis_id=hypothesis_id,
            declared_confidence=declared_confidence,
            evidence_confidence=ev_conf,
            illusion_gap=gap,
            severity=severity,
            evidence_quality=ev_quality,
            recommendation=rec,
        )
        self._reports.append(r)
        return r

    def _calculate_evidence_confidence(self, evidence: Dict) -> float:
        score = 0.0
        n = evidence.get("sample_size", 0)
        if n > 1000: score += 0.3
        elif n > 100: score += 0.2
        elif n > 30: score += 0.1
        if evidence.get("reproducible", False): score += 0.3
        p = evidence.get("p_value", 1.0)
        if p < 0.01: score += 0.2
        elif p < 0.05: score += 0.1
        if evidence.get("consistent_effect", False): score += 0.2
        return min(score, 1.0)

    def _calculate_evidence_quality(self, evidence: Dict) -> float:
        q = 0.0
        if evidence.get("peer_reviewed", False): q += 0.2
        if evidence.get("raw_data_available", False): q += 0.2
        if evidence.get("methodology_documented", False): q += 0.2
        if evidence.get("independent_replication", False): q += 0.4
        return min(q, 1.0)

    def _determine_severity(self, gap: float) -> str:
        if gap >= self._SEVERITY_THRESHOLDS["critical"]: return "critical"
        if gap >= self._SEVERITY_THRESHOLDS["high"]: return "high"
        if gap >= self._SEVERITY_THRESHOLDS["medium"]: return "medium"
        if gap >= self._SEVERITY_THRESHOLDS["low"]: return "low"
        return "none"

    def _recommendation(self, severity: str) -> str:
        return {
            "none": "Confidence is well-aligned with evidence",
            "low": "Slight overconfidence. Review evidence.",
            "medium": "Moderate overconfidence. Require additional evidence.",
            "high": "Significant overconfidence. Postpone decision.",
            "critical": "Severe confidence illusion. Veto recommended.",
        }.get(severity, "Review confidence calibration")

    def get_critical_alerts(self) -> List[ConfidenceIllusionReport]:
        return [r for r in self._reports if r.severity in ("high", "critical")]
