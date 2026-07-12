from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import uuid
import numpy as np


@dataclass
class ResearchQuestion:
    id: str = field(default_factory=lambda: f"q_{uuid.uuid4().hex[:12]}")
    text: str = ""
    priority: int = 5
    market_regime: str = ""
    category: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "pending"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "text": self.text, "priority": self.priority,
            "market_regime": self.market_regime, "category": self.category,
            "created_at": self.created_at.isoformat(), "status": self.status,
        }


class FutureQuestionsGenerator:
    """Gerador de perguntas de pesquisa futuras para o Discovery Layer."""

    _TEMPLATES = [
        "What is the relationship between {var1} and {var2} in {regime}?",
        "How does {var1} affect {var2} during {regime}?",
        "Does {var1} predict {var2} under {regime}?",
        "What are the drivers of {var1} in {regime}?",
        "Is {var1} a better indicator than {var2} for {regime}?",
    ]
    _REGIMES = ["trending_bull", "trending_bear", "ranging", "high_volatility", "crisis"]
    _VARIABLES = ["volatility", "momentum", "volume", "spread", "liquidity", "correlation"]
    _CATEGORIES = ["market_structure", "price_dynamics", "liquidity", "risk", "sentiment"]

    def __init__(self, seed: Optional[int] = None):
        self._rng = np.random.default_rng(seed)
        self._questions: Dict[str, ResearchQuestion] = {}

    def _choice(self, lst):
        return lst[int(self._rng.integers(0, len(lst)))]

    def generate_questions(
        self, market_regime: Optional[str] = None, n_questions: int = 5
    ) -> List[ResearchQuestion]:
        regime = market_regime or self._choice(self._REGIMES)
        questions = []
        for _ in range(n_questions):
            template = self._choice(self._TEMPLATES)
            var1 = self._choice(self._VARIABLES)
            remaining = [v for v in self._VARIABLES if v != var1]
            var2 = self._choice(remaining)
            text = template.format(var1=var1, var2=var2, regime=regime)
            q = ResearchQuestion(
                text=text,
                priority=int(self._rng.integers(1, 11)),
                market_regime=regime,
                category=self._choice(self._CATEGORIES),
            )
            questions.append(q)
            self._questions[q.id] = q
        return questions

    def identify_gaps(self, known: List[str], resolved: List[str]) -> List[ResearchQuestion]:
        return [
            q for q in self._questions.values()
            if q.text in known and q.text not in resolved
        ]

    def get_priority_queue(self, n: int = 10) -> List[ResearchQuestion]:
        pending = [q for q in self._questions.values() if q.status == "pending"]
        return sorted(pending, key=lambda x: x.priority, reverse=True)[:n]
