from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid


@dataclass
class Belief:
    id: str = field(default_factory=lambda: f"bel_{uuid.uuid4().hex[:12]}")
    hypothesis_id: str = ""
    probability: float = 0.5
    prior: float = 0.5
    posterior: float = 0.5
    confidence: float = 0.5
    liquidity: float = 1.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "hypothesis_id": self.hypothesis_id,
            "probability": self.probability, "prior": self.prior,
            "posterior": self.posterior, "confidence": self.confidence,
            "liquidity": self.liquidity,
            "last_updated": self.last_updated.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


class BeliefMarket:
    """Mercado de crenças — hipóteses são transformadas em crenças quantificadas e negociáveis."""

    def __init__(self):
        self._beliefs: Dict[str, Belief] = {}
        self._trade_history: List[Dict[str, Any]] = []

    def create_belief(self, hypothesis_id: str, prior: float = 0.5) -> Belief:
        b = Belief(hypothesis_id=hypothesis_id, prior=prior, probability=prior, posterior=prior)
        self._beliefs[hypothesis_id] = b
        return b

    def update_belief(self, hypothesis_id: str, evidence: Dict[str, Any]) -> Optional[Belief]:
        b = self._beliefs.get(hypothesis_id)
        if not b: return None
        likelihood = float(evidence.get("likelihood", 0.5))
        prior = b.probability
        denom = likelihood * prior + (1.0 - likelihood) * (1.0 - prior)
        posterior = (likelihood * prior) / denom if denom > 0 else prior
        b.prior = prior
        b.posterior = posterior
        b.probability = posterior
        b.confidence = min(1.0, b.confidence + 0.1 * abs(posterior - prior))
        b.last_updated = datetime.now(timezone.utc)
        return b

    def compete(self, hypothesis_ids: List[str]) -> Dict[str, float]:
        raw: Dict[str, float] = {}
        for hid in hypothesis_ids:
            b = self._beliefs.get(hid)
            if b:
                raw[hid] = b.probability * b.confidence * b.liquidity
        total = sum(raw.values())
        if total <= 0: return {hid: 0.0 for hid in hypothesis_ids}
        return {hid: v / total for hid, v in raw.items()}

    def get_belief_value(self, hypothesis_id: str) -> float:
        b = self._beliefs.get(hypothesis_id)
        return b.probability if b else 0.5
