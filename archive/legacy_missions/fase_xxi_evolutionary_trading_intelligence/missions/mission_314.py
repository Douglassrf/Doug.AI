# ============================================================
# MISSÃO 314 — ADAPTIVE STRATEGY MUTATION ENGINE
# Fase XXI — Evolutionary Trading Intelligence
# ============================================================

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import uuid
import numpy as np


def _deterministic_unit(seed: str, lo: float = 0.0, hi: float = 1.0) -> float:
    digest = hashlib.sha256(seed.encode()).hexdigest()
    return lo + (int(digest[:8], 16) / 0xFFFFFFFF) * (hi - lo)


def _deterministic_choice(seed: str, options: List[str]) -> str:
    idx = int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) % len(options)
    return options[idx]


@dataclass
class MutationCandidate:
    """Candidato a mutação de estratégia."""

    id: str = field(default_factory=lambda: f"mc_{uuid.uuid4().hex[:12]}")
    parent_strategy_id: str = ""
    mutation_type: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    fitness_score: float = 0.0
    evolution_signal: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "parent_strategy_id": self.parent_strategy_id,
            "mutation_type": self.mutation_type,
            "parameters": self.parameters,
            "fitness_score": self.fitness_score,
            "evolution_signal": self.evolution_signal,
            "created_at": self.created_at.isoformat(),
        }


class AdaptiveStrategyMutationEngine:
    """
    Motor de mutação adaptativa de estratégias.

    Implementa:
    - Mutation Candidates
    - Fitness Scoring
    - Selection
    - Rollback
    - Evolution Signal Integration
    - Mutation Dashboard
    """

    MUTATION_TYPES = ["parameter_shift", "regime_adaptation", "risk_rebalance", "signal_blend"]

    def __init__(self):
        self._candidates: Dict[str, MutationCandidate] = {}
        self._selected: Dict[str, str] = {}
        self._rollback_stack: List[Dict[str, Any]] = []

    def generate_mutations(
        self,
        strategy_id: str,
        evolution_signals: Dict[str, Any],
        count: int = 3,
    ) -> List[MutationCandidate]:
        """Gera candidatos de mutação baseados em sinais de evolução."""
        candidates: List[MutationCandidate] = []

        for i in range(count):
            mutation_type = _deterministic_choice(
                f"{strategy_id}:mut:{i}:{evolution_signals.get('regime', '')}",
                self.MUTATION_TYPES,
            )
            parameters = self._build_parameters(strategy_id, mutation_type, evolution_signals, i)
            fitness = self._score_fitness(parameters, evolution_signals)

            candidate = MutationCandidate(
                parent_strategy_id=strategy_id,
                mutation_type=mutation_type,
                parameters=parameters,
                fitness_score=fitness,
                evolution_signal=evolution_signals,
            )
            self._candidates[candidate.id] = candidate
            candidates.append(candidate)

        return sorted(candidates, key=lambda c: c.fitness_score, reverse=True)

    def _build_parameters(
        self,
        strategy_id: str,
        mutation_type: str,
        signals: Dict[str, Any],
        index: int,
    ) -> Dict[str, Any]:
        """Constrói parâmetros da mutação."""
        base_risk = signals.get("risk_tolerance", 0.5)
        drift = _deterministic_unit(f"{strategy_id}:{mutation_type}:{index}", -0.1, 0.1)

        return {
            "mutation_type": mutation_type,
            "risk_adjustment": min(max(base_risk + drift, 0.0), 1.0),
            "evolution_score": signals.get("evolution_score", 0.0),
            "regime": signals.get("regime", "unknown"),
            "lookback": int(10 + _deterministic_unit(f"{strategy_id}:lb:{index}", 0, 20)),
        }

    def _score_fitness(
        self, parameters: Dict[str, Any], signals: Dict[str, Any]
    ) -> float:
        """Calcula fitness da mutação."""
        evolution = signals.get("evolution_score", 0.0)
        risk_fit = 1.0 - abs(parameters.get("risk_adjustment", 0.5) - signals.get("risk_tolerance", 0.5))
        return min(max(evolution * 0.6 + risk_fit * 0.4, 0.0), 1.0)

    def select_best(self, strategy_id: str, candidates: List[MutationCandidate]) -> Optional[MutationCandidate]:
        """Seleciona melhor candidato e registra para rollback."""
        if not candidates:
            return None

        best = max(candidates, key=lambda c: c.fitness_score)
        previous = self._selected.get(strategy_id)
        self._rollback_stack.append(
            {
                "strategy_id": strategy_id,
                "previous_candidate_id": previous,
                "selected_candidate_id": best.id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        self._selected[strategy_id] = best.id
        return best

    def rollback(self, strategy_id: str) -> Optional[str]:
        """Reverte última seleção de mutação."""
        for entry in reversed(self._rollback_stack):
            if entry["strategy_id"] == strategy_id:
                self._rollback_stack.remove(entry)
                previous = entry.get("previous_candidate_id")
                if previous:
                    self._selected[strategy_id] = previous
                elif strategy_id in self._selected:
                    del self._selected[strategy_id]
                return previous
        return None

    def get_mutation_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de mutações."""
        candidates = list(self._candidates.values())
        return {
            "total_candidates": len(candidates),
            "selected_strategies": len(self._selected),
            "avg_fitness": (
                float(np.mean([c.fitness_score for c in candidates])) if candidates else 0.0
            ),
            "mutation_types": {
                mt: sum(1 for c in candidates if c.mutation_type == mt)
                for mt in self.MUTATION_TYPES
            },
            "rollback_stack_size": len(self._rollback_stack),
            "recent_candidates": [c.to_dict() for c in candidates[-5:]],
        }
