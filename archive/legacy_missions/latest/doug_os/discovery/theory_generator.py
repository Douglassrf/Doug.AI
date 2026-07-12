from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import uuid
import hashlib
import random


@dataclass
class GeneratedTheory:
    id: str = field(default_factory=lambda: f"theory_{uuid.uuid4().hex[:12]}")
    hypothesis: str = ""
    target: str = ""
    predictors: List[str] = field(default_factory=list)
    mechanism: str = ""
    predictions: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    testability_score: float = 0.0
    novelty_score: float = 0.0
    plausibility_score: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "hypothesis": self.hypothesis,
            "target": self.target,
            "predictors": self.predictors,
            "mechanism": self.mechanism,
            "predictions": self.predictions,
            "assumptions": self.assumptions,
            "testability_score": self.testability_score,
            "novelty_score": self.novelty_score,
            "plausibility_score": self.plausibility_score,
            "created_at": self.created_at.isoformat(),
        }


_MECHANISMS = [
    "linear causal pathway",
    "feedback loop amplification",
    "threshold-based activation",
    "competitive inhibition",
    "synergistic reinforcement",
    "mediating variable chain",
    "moderating interaction effect",
    "non-linear dose-response",
]

_ASSUMPTION_TEMPLATES = [
    "Variables are independently measurable",
    "Temporal precedence is established",
    "No hidden confounders exist",
    "Effect is stable across contexts",
    "Measurement error is negligible",
    "Sample is representative of population",
]


class TheoryGenerator:
    """Gerador automatico de teorias cientificas baseadas em variaveis."""

    def __init__(self, seed: Optional[int] = None):
        self._rng = random.Random(seed)
        self._generated_theories: Dict[str, GeneratedTheory] = {}

    def generate_theories(
        self,
        target: str,
        predictors: List[str],
        n: int = 3,
    ) -> List[GeneratedTheory]:
        theories = []
        for _ in range(n):
            theory = self._generate_one(target, predictors)
            self._generated_theories[theory.id] = theory
            theories.append(theory)
        return theories

    def generate_single(self, target: str, predictors: List[str]) -> GeneratedTheory:
        theory = self._generate_one(target, predictors)
        self._generated_theories[theory.id] = theory
        return theory

    def _generate_one(self, target: str, predictors: List[str]) -> GeneratedTheory:
        selected = self._rng.sample(predictors, k=min(len(predictors), self._rng.randint(1, max(1, len(predictors)))))
        mechanism = self._rng.choice(_MECHANISMS)
        hypothesis = (
            f"The {', '.join(selected)} {'jointly ' if len(selected) > 1 else ''}influence(s) {target} "
            f"via {mechanism}."
        )
        predictions = [
            f"An increase in {p} leads to a measurable change in {target}" for p in selected
        ]
        assumptions = self._rng.sample(_ASSUMPTION_TEMPLATES, k=min(3, len(_ASSUMPTION_TEMPLATES)))
        testability_score = round(min(1.0, 0.4 + 0.1 * len(selected) + self._rng.uniform(0, 0.3)), 4)
        novelty_score = self._calculate_novelty(hypothesis)
        plausibility_score = round(self._rng.uniform(0.4, 0.95), 4)

        return GeneratedTheory(
            hypothesis=hypothesis,
            target=target,
            predictors=selected,
            mechanism=mechanism,
            predictions=predictions,
            assumptions=assumptions,
            testability_score=testability_score,
            novelty_score=novelty_score,
            plausibility_score=plausibility_score,
        )

    def _calculate_novelty(self, hypothesis: str) -> float:
        existing = list(self._generated_theories.values())
        if not existing:
            return 1.0
        h_words = set(hypothesis.lower().split())
        similarities = []
        for t in existing:
            t_words = set(t.hypothesis.lower().split())
            union = h_words | t_words
            intersection = h_words & t_words
            jaccard = len(intersection) / len(union) if union else 0.0
            similarities.append(jaccard)
        avg_similarity = sum(similarities) / len(similarities)
        return round(max(0.0, 1.0 - avg_similarity), 4)

    def get_theory(self, theory_id: str) -> Optional[GeneratedTheory]:
        return self._generated_theories.get(theory_id)

    def list_theories(self) -> List[GeneratedTheory]:
        return list(self._generated_theories.values())
