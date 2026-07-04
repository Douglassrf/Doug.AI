from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
import uuid
import numpy as np


@dataclass
class CandidateIndicator:
    id: str = field(default_factory=lambda: f"ind_{uuid.uuid4().hex[:12]}")
    name: str = ""
    formula: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    baseline_score: float = 0.0
    current_score: float = 0.0
    improvement: float = 0.0
    parent_id: Optional[str] = None
    generation: int = 0
    mutation_history: List[Dict[str, Any]] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "name": self.name, "formula": self.formula,
            "parameters": self.parameters, "baseline_score": self.baseline_score,
            "current_score": self.current_score, "improvement": self.improvement,
            "parent_id": self.parent_id, "generation": self.generation,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }


class SelfInventionEngine:
    """Motor de auto-invenção de indicadores com mutação e seleção natural."""

    def __init__(self, seed: Optional[int] = None):
        self._rng = np.random.default_rng(seed)
        self._indicators: Dict[str, CandidateIndicator] = {}
        self._survival_rate: float = 0.3

    def generate_candidates(self, base_formulas: List[str], n_candidates: int = 10) -> List[CandidateIndicator]:
        candidates = []
        for i in range(n_candidates):
            base = base_formulas[int(self._rng.integers(0, len(base_formulas)))]
            formula, params = self._mutate(base)
            indicator = CandidateIndicator(
                name=f"IND_{len(self._indicators) + 1}",
                formula=formula,
                parameters=params,
                generation=0,
            )
            candidates.append(indicator)
            self._indicators[indicator.id] = indicator
        return candidates

    def _mutate(self, formula: str) -> Tuple[str, Dict[str, Any]]:
        choice = int(self._rng.integers(0, 4))
        mutations = [self._mutate_parameter, self._mutate_scale, self._mutate_lag, self._mutate_combination]
        return mutations[choice](formula)

    def _mutate_parameter(self, formula: str) -> Tuple[str, Dict[str, Any]]:
        period = int(self._rng.integers(5, 51))
        return formula, {"period": period}

    def _mutate_scale(self, formula: str) -> Tuple[str, Dict[str, Any]]:
        scale = float(self._rng.uniform(0.5, 2.0))
        return f"({formula}) * {scale:.3f}", {"scale": scale}

    def _mutate_lag(self, formula: str) -> Tuple[str, Dict[str, Any]]:
        lag = int(self._rng.integers(1, 11))
        return f"lag({formula}, {lag})", {"lag": lag}

    def _mutate_combination(self, formula: str) -> Tuple[str, Dict[str, Any]]:
        ops = ["+", "-", "*"]
        op = ops[int(self._rng.integers(0, len(ops)))]
        if self._indicators:
            keys = list(self._indicators.keys())
            other = self._indicators[keys[int(self._rng.integers(0, len(keys)))]]
            return f"({formula}) {op} ({other.formula})", {}
        return formula, {}

    def evaluate_candidates(
        self,
        indicators: List[CandidateIndicator],
        baseline_score: float,
        market_data: Dict[str, Any],
    ) -> List[CandidateIndicator]:
        for ind in indicators:
            perf = float(self._rng.uniform(0.3, 0.7)) + min(len(ind.formula) / 200, 0.15) - len(ind.parameters) * 0.02
            perf = min(max(perf, 0.0), 1.0)
            ind.baseline_score = baseline_score
            ind.current_score = perf
            ind.improvement = perf - baseline_score
            if ind.improvement < 0:
                ind.is_active = False
        indicators.sort(key=lambda x: x.improvement, reverse=True)
        return indicators

    def evolve_generation(self) -> List[CandidateIndicator]:
        active = sorted(
            [i for i in self._indicators.values() if i.is_active],
            key=lambda x: x.improvement, reverse=True,
        )
        survivors = active[: max(1, int(len(active) * self._survival_rate))]
        new_gen = []
        for survivor in survivors:
            for _ in range(3):
                formula, params = self._mutate(survivor.formula)
                child = CandidateIndicator(
                    name=f"{survivor.name}_V{survivor.generation + 1}",
                    formula=formula,
                    parameters={**survivor.parameters, **params},
                    parent_id=survivor.id,
                    generation=survivor.generation + 1,
                    mutation_history=[*survivor.mutation_history, {"type": "mutate"}],
                )
                new_gen.append(child)
                self._indicators[child.id] = child
        return new_gen

    def get_best_indicators(self, n: int = 5) -> List[CandidateIndicator]:
        active = sorted(
            [i for i in self._indicators.values() if i.is_active],
            key=lambda x: x.improvement, reverse=True,
        )
        return active[:n]
