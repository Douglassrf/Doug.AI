# ============================================================
# MISSÃO 280 — ADAPTIVE ALPHA LABORATORY
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import hashlib
import re
import numpy as np


def _deterministic_unit(seed: str, lo: float = 0.0, hi: float = 1.0) -> float:
    digest = hashlib.sha256(seed.encode()).hexdigest()
    return lo + (int(digest[:8], 16) / 0xFFFFFFFF) * (hi - lo)


def _deterministic_choice(seed: str, options: List[Any]) -> Any:
    idx = int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) % len(options)
    return options[idx]


def _deterministic_int(seed: str, lo: int, hi: int) -> int:
    return lo + int(_deterministic_unit(seed, 0.0, 1.0) * (hi - lo + 1))


@dataclass
class AlphaCandidate:
    """Candidato a Alpha."""
    id: str = field(default_factory=lambda: f"ac_{uuid.uuid4().hex[:12]}")
    name: str = ""
    description: str = ""
    formula: str = ""
    fitness: float = 0.0
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    validation_status: str = "pending"
    performance: List[float] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "formula": self.formula,
            "fitness": self.fitness,
            "generation": self.generation,
            "parent_ids": self.parent_ids,
            "validation_status": self.validation_status,
            "performance": self.performance[-20:],
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }


class AdaptiveAlphaLaboratory:
    """
    Laboratório adaptativo de Alpha.

    Implementa:
    - Alpha Discovery Queue
    - Alpha Validation
    - Alpha Mutation
    - Alpha Fitness
    - Alpha Ranking
    - Alpha Retirement
    - Alpha Versioning
    - Alpha Certification
    - Alpha Repository
    - Dashboard
    """

    def __init__(self):
        self._alphas: Dict[str, AlphaCandidate] = {}
        self._certified_alphas: List[str] = []
        self._retired_alphas: List[str] = []
        self._generation = 0

    def submit_alpha(
        self,
        name: str,
        description: str,
        formula: str,
        performance: List[float],
    ) -> AlphaCandidate:
        alpha = AlphaCandidate(
            name=name,
            description=description,
            formula=formula,
            performance=performance,
            generation=self._generation,
        )
        alpha.fitness = self._calculate_fitness(performance)
        self._alphas[alpha.id] = alpha
        return alpha

    def _calculate_fitness(self, performance: List[float]) -> float:
        if len(performance) < 2:
            return 0.0

        returns = np.array(performance)
        win_rate = sum(1 for r in returns if r > 0) / len(returns)
        sharpe = np.mean(returns) / (np.std(returns) + 0.001)
        return win_rate * 0.5 + min(sharpe / 2, 0.5)

    def mutate_alpha(self, alpha_id: str) -> AlphaCandidate:
        parent = self._alphas.get(alpha_id)
        if not parent:
            raise ValueError(f"Alpha {alpha_id} not found")

        mutation_types = ["modify_parameter", "add_term", "remove_term", "combine"]
        mutation_type = _deterministic_choice(f"{alpha_id}:mut_type", mutation_types)
        new_formula = self._apply_mutation(parent.formula, mutation_type, parent.id)

        new_performance = [
            p * _deterministic_unit(f"{alpha_id}:perf:{i}", 0.9, 1.1)
            for i, p in enumerate(parent.performance[-10:])
        ]

        mutation_count = len([a for a in self._alphas.values() if parent.id in a.parent_ids])
        child = AlphaCandidate(
            name=f"{parent.name}_M{mutation_count + 1}",
            description=f"Mutation of {parent.name}",
            formula=new_formula,
            generation=self._generation,
            parent_ids=[parent.id],
            performance=new_performance,
        )

        child.fitness = self._calculate_fitness(new_performance)
        self._alphas[child.id] = child
        return child

    def _apply_mutation(self, formula: str, mutation_type: str, parent_id: str) -> str:
        if mutation_type == "modify_parameter":
            replacement = str(_deterministic_int(f"{parent_id}:param", 1, 100))
            return re.sub(r"\d+", replacement, formula, count=1)
        if mutation_type == "add_term":
            terms = ["MA", "RSI", "MACD", "BB", "ATR"]
            term = _deterministic_choice(f"{parent_id}:term", terms)
            period = _deterministic_int(f"{parent_id}:period", 5, 20)
            return f"{formula} + {term}({period})"
        if mutation_type == "remove_term":
            return formula.split("+")[0].strip() if "+" in formula else formula
        if mutation_type == "combine":
            others = [a for a in self._alphas.values() if a.id != parent_id]
            if not others:
                return formula
            other = _deterministic_choice(f"{parent_id}:combine", others)
            return f"({formula}) + ({other.formula})"
        return formula

    def validate_alpha(self, alpha_id: str) -> bool:
        alpha = self._alphas.get(alpha_id)
        if not alpha:
            return False

        if alpha.fitness > 0.4 and len(alpha.performance) > 20:
            alpha.validation_status = "validated"
            return True

        alpha.validation_status = "rejected"
        return False

    def certify_alpha(self, alpha_id: str) -> bool:
        alpha = self._alphas.get(alpha_id)
        if not alpha or alpha.validation_status != "validated":
            return False

        if alpha.fitness > 0.6:
            alpha.validation_status = "certified"
            self._certified_alphas.append(alpha_id)
            return True

        return False

    def retire_alpha(self, alpha_id: str) -> bool:
        alpha = self._alphas.get(alpha_id)
        if not alpha:
            return False

        alpha.validation_status = "rejected"
        self._retired_alphas.append(alpha_id)
        return True

    def get_alpha_ranking(self) -> List[AlphaCandidate]:
        valid = [a for a in self._alphas.values() if a.validation_status in ["validated", "certified"]]
        return sorted(valid, key=lambda x: x.fitness, reverse=True)

    def get_alpha_dashboard(self) -> Dict[str, Any]:
        total = len(self._alphas)
        certified = len(self._certified_alphas)
        retired = len(self._retired_alphas)

        return {
            "total_alphas": total,
            "certified_alphas": certified,
            "retired_alphas": retired,
            "pending_validation": sum(1 for a in self._alphas.values() if a.validation_status == "pending"),
            "avg_fitness": np.mean([a.fitness for a in self._alphas.values()]) if total > 0 else 0,
            "top_alphas": [a.to_dict() for a in self.get_alpha_ranking()[:5]],
        }
