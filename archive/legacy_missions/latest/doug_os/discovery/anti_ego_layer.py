from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List
import uuid


@dataclass
class CognitiveHumilityReport:
    id: str = field(default_factory=lambda: f"hum_{uuid.uuid4().hex[:12]}")
    hypothesis_id: str = ""
    self_score: float = 0.0
    external_score: float = 0.0
    humility_gap: float = 0.0
    persistence_penalty: float = 0.0
    recommendation: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "hypothesis_id": self.hypothesis_id,
            "self_score": self.self_score, "external_score": self.external_score,
            "humility_gap": self.humility_gap, "persistence_penalty": self.persistence_penalty,
            "recommendation": self.recommendation, "created_at": self.created_at.isoformat(),
        }


class AntiEgoLayer:
    """Impede o sistema de defender ideias ruins só por tê-las criado."""

    def __init__(self):
        self._reports: Dict[str, CognitiveHumilityReport] = {}
        self._persistence: Dict[str, int] = {}

    def evaluate(self, hypothesis_id: str, self_evidence: Dict[str, Any], external_evidence: Dict[str, Any]) -> CognitiveHumilityReport:
        ss = self._calculate_score(self_evidence)
        es = self._calculate_score(external_evidence)
        gap = ss - es
        count = self._persistence.get(hypothesis_id, 0)
        penalty = min(count * 0.05, 0.5)
        if gap > 0.3:
            rec = "Overvaluing own evidence. Seek external validation."
        elif penalty > 0.3:
            rec = "Excessive persistence without new evidence. Consider alternatives."
        else:
            rec = "Balanced evaluation. Proceed with caution."
        self._persistence[hypothesis_id] = count + 1
        r = CognitiveHumilityReport(
            hypothesis_id=hypothesis_id, self_score=ss, external_score=es,
            humility_gap=gap, persistence_penalty=penalty, recommendation=rec,
        )
        self._reports[hypothesis_id] = r
        return r

    def _calculate_score(self, evidence: Dict) -> float:
        s = 0.0
        if evidence.get("quality", 0) > 0.7: s += 0.3
        if evidence.get("quantity", 0) > 10: s += 0.2
        if evidence.get("independence", False): s += 0.2
        if evidence.get("consistency", False): s += 0.2
        if evidence.get("novelty", False): s += 0.1
        return min(s, 1.0)

    def get_recommendations(self) -> List[str]:
        return [r.recommendation for r in self._reports.values() if r.humility_gap > 0.2]
