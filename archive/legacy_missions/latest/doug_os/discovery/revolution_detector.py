from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import uuid


@dataclass
class ParadigmShift:
    id: str = field(default_factory=lambda: f"ps_{uuid.uuid4().hex[:12]}")
    old_theory: str = ""
    new_theory: str = ""
    shift_score: float = 0.0          # 0-1: how large the paradigm shift is
    evidence: List[str] = field(default_factory=list)
    is_revolution: bool = False
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "old_theory": self.old_theory,
            "new_theory": self.new_theory,
            "shift_score": self.shift_score,
            "evidence": self.evidence,
            "is_revolution": self.is_revolution,
            "detected_at": self.detected_at.isoformat(),
        }


class ScientificRevolutionDetector:
    """Detecta quando uma nova teoria representa uma revolução científica (Kuhn)."""

    REVOLUTION_THRESHOLD = 0.7

    def __init__(self):
        self._history: List[ParadigmShift] = []

    def compare_theories(
        self,
        old_theory: Dict[str, Any],
        new_theory: Dict[str, Any],
    ) -> ParadigmShift:
        """Compara duas teorias e calcula o shift_score (quão disruptiva é a nova teoria)."""
        old_score = float(old_theory.get("predictive_power", 0.5))
        new_score = float(new_theory.get("predictive_power", 0.5))
        old_complexity = float(old_theory.get("complexity", 1.0))
        new_complexity = float(new_theory.get("complexity", 1.0))
        old_assumptions = set(old_theory.get("assumptions", []))
        new_assumptions = set(new_theory.get("assumptions", []))

        # Performance gain component (0-1)
        perf_gain = max(0.0, new_score - old_score)

        # Assumption divergence component (0-1)
        union = old_assumptions | new_assumptions
        intersection = old_assumptions & new_assumptions
        assumption_divergence = 1.0 - (len(intersection) / len(union)) if union else 0.0

        # Complexity change component — simpler new theory scores higher
        complexity_ratio = old_complexity / max(new_complexity, 0.01)
        complexity_bonus = min(max(complexity_ratio - 1.0, 0.0), 0.5)

        # Combine: performance gain, assumption divergence, complexity improvement
        # Scale perf_gain: a gain of 0.35 (0.5->0.85) should contribute strongly
        perf_component = min(perf_gain * 2.0, 0.7)  # cap at 0.7, 0.35 gain -> 0.70
        shift_score = min(1.0, perf_component * 0.5 + assumption_divergence * 0.4 + complexity_bonus * 0.1)

        evidence: List[str] = []
        if new_score > old_score:
            evidence.append(f"New theory improves predictive power: {old_score:.2f} -> {new_score:.2f}")
        if assumption_divergence > 0.5:
            evidence.append(f"Major assumption divergence: {assumption_divergence:.2%} of assumptions differ")
        if complexity_ratio > 1.2:
            evidence.append(f"New theory is simpler: complexity reduced by {(1 - 1/complexity_ratio):.1%}")

        shift = ParadigmShift(
            old_theory=old_theory.get("name", "OldTheory"),
            new_theory=new_theory.get("name", "NewTheory"),
            shift_score=shift_score,
            evidence=evidence,
            is_revolution=shift_score >= self.REVOLUTION_THRESHOLD,
        )
        self._history.append(shift)
        return shift

    def get_revolution_alerts(self, threshold: Optional[float] = None) -> List[ParadigmShift]:
        """Retorna paradigm shifts acima do threshold (padrão: REVOLUTION_THRESHOLD)."""
        t = threshold if threshold is not None else self.REVOLUTION_THRESHOLD
        return [s for s in self._history if s.shift_score >= t]

    def get_history(self) -> List[ParadigmShift]:
        return list(self._history)
