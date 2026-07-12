from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import uuid
import hashlib


@dataclass
class BuriedTheory:
    id: str = field(default_factory=lambda: f"buried_{uuid.uuid4().hex[:12]}")
    hypothesis: str = ""
    failure_reason: str = ""
    failure_category: str = ""
    similarity_hash: str = ""
    burial_depth: int = 1
    lessons_learned: List[str] = field(default_factory=list)
    related_theories: List[str] = field(default_factory=list)
    buried_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "hypothesis": self.hypothesis,
            "failure_reason": self.failure_reason,
            "failure_category": self.failure_category,
            "similarity_hash": self.similarity_hash,
            "burial_depth": self.burial_depth,
            "lessons_learned": self.lessons_learned,
            "related_theories": self.related_theories,
            "buried_at": self.buried_at.isoformat(),
            "metadata": self.metadata,
        }


_FAILURE_CATEGORIES = {
    "statistical": ["p_value", "significance", "correlation", "variance", "sample"],
    "logical": ["contradiction", "circular", "tautology", "fallacy", "invalid"],
    "empirical": ["data", "evidence", "observation", "experiment", "result"],
    "causal": ["confound", "spurious", "reverse", "causal", "mechanism"],
    "theoretical": ["assumption", "axiom", "framework", "model", "theory"],
}

_LESSONS_TEMPLATES = {
    "statistical": [
        "Ensure sufficient statistical power before testing",
        "Account for multiple comparison corrections",
        "Validate distributional assumptions",
    ],
    "logical": [
        "Check for internal consistency before proceeding",
        "Define terms precisely to avoid circular reasoning",
        "Map the argument structure explicitly",
    ],
    "empirical": [
        "Collect more representative data",
        "Pre-register hypotheses to avoid HARKing",
        "Use holdout sets for validation",
    ],
    "causal": [
        "Use randomization or natural experiments",
        "Control for known confounders",
        "Establish temporal precedence",
    ],
    "theoretical": [
        "Review foundational assumptions carefully",
        "Seek convergent evidence from multiple frameworks",
        "Explicitly state boundary conditions",
    ],
}


def _compute_similarity_hash(hypothesis: str) -> str:
    normalized = " ".join(sorted(hypothesis.lower().split()))
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def _classify_failure(failure_reason: str) -> str:
    reason_lower = failure_reason.lower()
    for category, keywords in _FAILURE_CATEGORIES.items():
        if any(kw in reason_lower for kw in keywords):
            return category
    return "theoretical"


class TheoryGraveyard:
    """Repositorio de teorias falhas com analise de padroes e deteccao de duplicatas."""

    def __init__(self):
        self._buried: Dict[str, BuriedTheory] = {}

    def bury_theory(
        self,
        hypothesis: str,
        failure_reason: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> BuriedTheory:
        category = _classify_failure(failure_reason)
        sim_hash = _compute_similarity_hash(hypothesis)
        lessons = _LESSONS_TEMPLATES.get(category, _LESSONS_TEMPLATES["theoretical"])
        burial_depth = self._compute_burial_depth(sim_hash)
        related = self._find_related(sim_hash)

        buried = BuriedTheory(
            hypothesis=hypothesis,
            failure_reason=failure_reason,
            failure_category=category,
            similarity_hash=sim_hash,
            burial_depth=burial_depth,
            lessons_learned=list(lessons),
            related_theories=related,
            metadata=metadata or {},
        )
        self._buried[buried.id] = buried
        return buried

    def _compute_burial_depth(self, sim_hash: str) -> int:
        count = sum(1 for t in self._buried.values() if t.similarity_hash == sim_hash)
        return count + 1

    def _find_related(self, sim_hash: str) -> List[str]:
        return [t.id for t in self._buried.values() if t.similarity_hash == sim_hash]

    def search_similar(self, hypothesis: str, threshold: float = 0.5) -> List[BuriedTheory]:
        query_words = set(hypothesis.lower().split())
        results = []
        for t in self._buried.values():
            t_words = set(t.hypothesis.lower().split())
            union = query_words | t_words
            intersection = query_words & t_words
            if not union:
                continue
            jaccard = len(intersection) / len(union)
            if jaccard >= threshold:
                results.append(t)
        return results

    def check_duplicate(self, hypothesis: str) -> bool:
        target_hash = _compute_similarity_hash(hypothesis)
        return any(t.similarity_hash == target_hash for t in self._buried.values())

    def get_failure_patterns(self) -> Dict[str, int]:
        patterns: Dict[str, int] = {}
        for t in self._buried.values():
            patterns[t.failure_category] = patterns.get(t.failure_category, 0) + 1
        return patterns

    def exhume(self, buried_id: str) -> Optional[BuriedTheory]:
        return self._buried.get(buried_id)

    def list_buried(self) -> List[BuriedTheory]:
        return list(self._buried.values())
