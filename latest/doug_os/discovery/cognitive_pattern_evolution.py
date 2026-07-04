from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class CognitivePattern:
    id: str = field(default_factory=lambda: f"cp_{uuid.uuid4().hex[:12]}")
    name: str = ""
    description: str = ""
    pattern_data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.5
    fitness: float = 0.0
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    mutation_history: List[str] = field(default_factory=list)
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "pattern_data": self.pattern_data,
            "confidence": self.confidence,
            "fitness": self.fitness,
            "generation": self.generation,
            "parent_ids": self.parent_ids,
            "mutation_history": self.mutation_history,
            "active": self.active,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }


class CognitivePatternEvolution:
    """Evolução genética de padrões cognitivos — sem sklearn, sem random stdlib."""

    def __init__(self, population_size: int = 50, seed: int = 42) -> None:
        self._rng = np.random.default_rng(seed)
        self._patterns: Dict[str, CognitivePattern] = {}
        self._population_size = population_size
        self._generation = 0
        self._fitness_history: List[float] = []

    # ------------------------------------------------------------------
    def create_pattern(
        self,
        name: str,
        description: str,
        pattern_data: Dict[str, Any],
        confidence: float = 0.5,
    ) -> CognitivePattern:
        pattern = CognitivePattern(
            name=name,
            description=description,
            pattern_data=pattern_data,
            confidence=confidence,
            generation=self._generation,
        )
        self._patterns[pattern.id] = pattern
        return pattern

    def evolve_generation(self) -> List[CognitivePattern]:
        self._generation += 1

        for pattern in self._patterns.values():
            pattern.fitness = self._calculate_fitness(pattern)

        active = [p for p in self._patterns.values() if p.active]
        sorted_active = sorted(active, key=lambda x: x.fitness, reverse=True)
        survivors = sorted_active[: max(1, int(len(sorted_active) * 0.3))]

        new_patterns: List[CognitivePattern] = []
        attempts = 0
        while len(survivors) + len(new_patterns) < self._population_size and attempts < 200:
            attempts += 1
            if self._rng.random() < 0.6:
                if survivors:
                    idx = int(self._rng.integers(0, len(survivors)))
                    child = self._mutate_pattern(survivors[idx])
                    new_patterns.append(child)
            else:
                if len(survivors) >= 2:
                    idxs = self._rng.choice(len(survivors), 2, replace=False)
                    child = self._fuse_patterns(survivors[idxs[0]], survivors[idxs[1]])
                    new_patterns.append(child)

        for p in new_patterns:
            self._patterns[p.id] = p

        avg_fitness = float(np.mean([p.fitness for p in self._patterns.values()]))
        self._fitness_history.append(avg_fitness)
        return new_patterns

    def _calculate_fitness(self, pattern: CognitivePattern) -> float:
        confidence_score = pattern.confidence * 0.6
        complexity = len(str(pattern.pattern_data))
        complexity_score = max(0.0, 1 - complexity / 1000) * 0.2
        novelty = (pattern.generation / max(1, self._generation)) * 0.2
        return confidence_score + complexity_score + novelty

    def _mutate_pattern(self, parent: CognitivePattern) -> CognitivePattern:
        new_data = dict(parent.pattern_data)
        mutation_type = int(self._rng.integers(0, 3))

        if mutation_type == 0 and new_data:
            keys = list(new_data.keys())
            key = keys[int(self._rng.integers(0, len(keys)))]
            if isinstance(new_data[key], (int, float)):
                new_data[key] = float(new_data[key]) * float(self._rng.uniform(0.8, 1.2))
        elif mutation_type == 1:
            new_data[f"param_{len(new_data)}"] = float(self._rng.uniform(0, 1))
        elif mutation_type == 2 and len(new_data) > 1:
            keys = list(new_data.keys())
            key = keys[int(self._rng.integers(0, len(keys)))]
            del new_data[key]

        new_conf = float(parent.confidence * self._rng.uniform(0.9, 1.1))
        new_conf = min(1.0, max(0.1, new_conf))

        return CognitivePattern(
            name=f"{parent.name}_M{len(parent.mutation_history)}",
            description=f"Mutation of {parent.name}",
            pattern_data=new_data,
            confidence=new_conf,
            generation=self._generation,
            parent_ids=[parent.id],
            mutation_history=parent.mutation_history + ["mutate"],
        )

    def _fuse_patterns(
        self, parent1: CognitivePattern, parent2: CognitivePattern
    ) -> CognitivePattern:
        fused: Dict[str, Any] = {}
        common = set(parent1.pattern_data) & set(parent2.pattern_data)
        for key in common:
            v1, v2 = parent1.pattern_data[key], parent2.pattern_data[key]
            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                fused[key] = (float(v1) + float(v2)) / 2
            else:
                fused[key] = v1 if self._rng.random() < 0.5 else v2

        for key in set(parent1.pattern_data) ^ set(parent2.pattern_data):
            src = parent1 if key in parent1.pattern_data else parent2
            fused[key] = src.pattern_data[key]

        return CognitivePattern(
            name=f"{parent1.name}_{parent2.name}_F",
            description=f"Fusion of {parent1.name} and {parent2.name}",
            pattern_data=fused,
            confidence=(parent1.confidence + parent2.confidence) / 2,
            generation=self._generation,
            parent_ids=[parent1.id, parent2.id],
            mutation_history=["fusion"],
        )

    def retire_pattern(self, pattern_id: str) -> bool:
        p = self._patterns.get(pattern_id)
        if not p:
            return False
        p.active = False
        return True

    def get_top_patterns(self, n: int = 10) -> List[CognitivePattern]:
        active = [p for p in self._patterns.values() if p.active]
        return sorted(active, key=lambda x: x.fitness, reverse=True)[:n]

    def get_pattern_dashboard(self) -> Dict[str, Any]:
        active = [p for p in self._patterns.values() if p.active]
        retired = [p for p in self._patterns.values() if not p.active]
        return {
            "total_patterns": len(self._patterns),
            "active_patterns": len(active),
            "retired_patterns": len(retired),
            "current_generation": self._generation,
            "avg_fitness": float(np.mean([p.fitness for p in active])) if active else 0.0,
            "fitness_history": self._fitness_history[-10:],
            "top_patterns": [p.to_dict() for p in self.get_top_patterns(5)],
        }
