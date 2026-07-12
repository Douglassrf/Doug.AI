from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import hashlib


@dataclass
class DecisionDNA:
    id: str = field(default_factory=lambda: f"dna_{uuid.uuid4().hex[:12]}")
    decision_id: str = ""
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    hypotheses: List[Dict[str, Any]] = field(default_factory=list)
    modules: List[str] = field(default_factory=list)
    market_regime: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    score: float = 0.0
    confidence: float = 0.0
    risk_score: float = 0.0
    weights: Dict[str, float] = field(default_factory=dict)
    explanation: str = ""
    reasoning_chain: List[str] = field(default_factory=list)
    audit_hash: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    outcome: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.audit_hash:
            self.audit_hash = self._generate_hash()

    def _generate_hash(self) -> str:
        content = f"{self.decision_id}{self.explanation}{self.confidence}{self.timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "decision_id": self.decision_id,
            "evidence": self.evidence, "hypotheses": self.hypotheses,
            "modules": self.modules, "market_regime": self.market_regime,
            "timestamp": self.timestamp.isoformat(), "score": self.score,
            "confidence": self.confidence, "risk_score": self.risk_score,
            "weights": self.weights, "explanation": self.explanation,
            "reasoning_chain": self.reasoning_chain, "audit_hash": self.audit_hash,
            "created_at": self.created_at.isoformat(), "outcome": self.outcome,
        }


class DecisionDNAEngine:
    def __init__(self):
        self._dnas: Dict[str, DecisionDNA] = {}

    def create_dna(self, decision_id: str, evidence: List[Dict], hypotheses: List[Dict],
                   modules: List[str], market_regime: str, score: float, confidence: float,
                   risk_score: float, weights: Dict[str, float], explanation: str,
                   reasoning_chain: List[str]) -> DecisionDNA:
        dna = DecisionDNA(
            decision_id=decision_id, evidence=evidence, hypotheses=hypotheses,
            modules=modules, market_regime=market_regime, score=score,
            confidence=confidence, risk_score=risk_score, weights=weights,
            explanation=explanation, reasoning_chain=reasoning_chain,
        )
        self._dnas[dna.id] = dna
        return dna

    def get_dna(self, dna_id: str) -> Optional[DecisionDNA]:
        return self._dnas.get(dna_id)

    def get_dna_by_decision(self, decision_id: str) -> Optional[DecisionDNA]:
        return next((d for d in self._dnas.values() if d.decision_id == decision_id), None)

    def update_outcome(self, dna_id: str, outcome: Dict[str, Any]) -> None:
        dna = self._dnas.get(dna_id)
        if dna:
            dna.outcome = outcome

    def search_dna(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        q = query.lower()
        results = []
        for dna in self._dnas.values():
            score = 0.0
            if q in dna.explanation.lower(): score += 0.5
            for ev in dna.evidence:
                if any(isinstance(v, str) and q in v.lower() for v in ev.values()):
                    score += 0.2; break
            for hyp in dna.hypotheses:
                if any(isinstance(v, str) and q in v.lower() for v in hyp.values()):
                    score += 0.2; break
            if score > 0:
                results.append({"dna": dna.to_dict(), "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]
