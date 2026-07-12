from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class Scenario:
    id: str = field(default_factory=lambda: f"sc_{uuid.uuid4().hex[:12]}")
    name: str = ""
    description: str = ""
    probability: float = 0.0
    outcome: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    branch_path: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "name": self.name, "description": self.description,
            "probability": self.probability, "outcome": self.outcome,
            "confidence": self.confidence, "branch_path": self.branch_path,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ScenarioTree:
    id: str = field(default_factory=lambda: f"st_{uuid.uuid4().hex[:12]}")
    root_scenario: Scenario = field(default_factory=Scenario)
    branches: List[Scenario] = field(default_factory=list)
    probabilities: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "root_scenario": self.root_scenario.to_dict(),
            "branches": [b.to_dict() for b in self.branches],
            "probabilities": self.probabilities,
            "created_at": self.created_at.isoformat(),
        }


class ProbabilisticScenarioEngine:
    def __init__(self, seed: int = 42):
        self._scenarios: Dict[str, Scenario] = {}
        self._trees: List[ScenarioTree] = []
        self._rng = np.random.default_rng(seed)

    def generate_scenarios(
        self,
        base_conditions: Dict[str, Any],
        n_scenarios: int = 5,
        time_horizon: str = "short",
    ) -> List[Scenario]:
        vol_mult = {"short": 1.0, "medium": 1.5, "long": 2.0}.get(time_horizon, 1.0)
        scenarios = []
        for i in range(n_scenarios):
            variation = float(self._rng.normal(0, 0.1 * vol_mult))
            prob = float(np.clip(1.0 / n_scenarios + variation * 0.1, 0.01, 0.99))
            conf = float(np.clip(1.0 - abs(variation) / (0.3 * vol_mult), 0.1, 0.95))
            scenario = Scenario(
                name=f"Scenario_{i + 1}",
                description=f"Scenario with {variation:.2f} variation",
                probability=prob,
                outcome=self._generate_outcome(base_conditions, variation),
                confidence=conf,
            )
            scenarios.append(scenario)
            self._scenarios[scenario.id] = scenario
        total_prob = sum(s.probability for s in scenarios)
        if total_prob > 0:
            for s in scenarios:
                s.probability /= total_prob
        return scenarios

    def _generate_outcome(self, base: Dict[str, Any], variation: float) -> Dict[str, Any]:
        outcome: Dict[str, Any] = {}
        for key, value in base.items():
            if isinstance(value, (int, float)):
                scale = float(self._rng.uniform(0.5, 1.5))
                outcome[key] = value * (1.0 + variation * scale)
            elif isinstance(value, list):
                outcome[key] = [
                    v * (1.0 + variation * float(self._rng.uniform(0.5, 1.5)))
                    if isinstance(v, (int, float)) else v
                    for v in value
                ]
            else:
                outcome[key] = value
        return outcome

    def build_scenario_tree(
        self,
        root_conditions: Dict[str, Any],
        depth: int = 3,
        branching_factor: int = 3,
    ) -> ScenarioTree:
        root = Scenario(name="Root", description="Current state",
                        probability=1.0, outcome=root_conditions, confidence=1.0)
        tree = ScenarioTree(root_scenario=root, probabilities={"root": 1.0})
        self._build_branches(tree, root, depth, branching_factor, 1.0)
        self._trees.append(tree)
        return tree

    def _build_branches(
        self,
        tree: ScenarioTree,
        parent: Scenario,
        remaining_depth: int,
        branching_factor: int,
        probability: float,
    ) -> None:
        if remaining_depth == 0:
            return
        for i in range(branching_factor):
            variation = float(self._rng.normal(0, 0.1 * remaining_depth))
            branch_prob = probability / branching_factor
            branch = Scenario(
                name=f"{parent.name}_{i + 1}",
                description=f"Branch {i + 1} at depth {remaining_depth}",
                probability=branch_prob,
                outcome=self._generate_outcome(parent.outcome, variation),
                confidence=float(np.clip(1.0 - abs(variation) * 2, 0.1, 0.95)),
                branch_path=parent.branch_path + [parent.id],
            )
            tree.branches.append(branch)
            tree.probabilities[branch.id] = branch_prob
            self._scenarios[branch.id] = branch
            self._build_branches(tree, branch, remaining_depth - 1, branching_factor, branch_prob)

    def rank_scenarios(
        self, scenarios: List[Scenario], criteria: Dict[str, float]
    ) -> List[Scenario]:
        scored = []
        for s in scenarios:
            score = (s.probability * criteria.get("probability", 0.3)
                     + s.confidence * criteria.get("confidence", 0.3)
                     + self._evaluate_outcome(s.outcome, criteria) * criteria.get("outcome", 0.4))
            scored.append((s, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [x[0] for x in scored]

    def _evaluate_outcome(self, outcome: Dict[str, Any], criteria: Dict[str, float]) -> float:
        score = 0.0
        for key, weight in criteria.items():
            if key in outcome and isinstance(outcome[key], (int, float)):
                score += float(np.clip(outcome[key] / 100, 0.0, 1.0)) * weight
        return min(score, 1.0)

    def get_best_scenario(self, scenarios: List[Scenario]) -> Optional[Scenario]:
        if not scenarios:
            return None
        return max(scenarios, key=lambda s: s.probability * s.confidence)

    def compare_scenarios(
        self, scenario1: Scenario, scenario2: Scenario
    ) -> Dict[str, Any]:
        diff: Dict[str, Any] = {}
        for key in set(scenario1.outcome) | set(scenario2.outcome):
            v1 = scenario1.outcome.get(key)
            v2 = scenario2.outcome.get(key)
            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                diff[key] = {
                    "scenario1": v1, "scenario2": v2,
                    "difference": v1 - v2,
                    "percent_change": (v1 - v2) / v2 * 100 if v2 != 0 else 0,
                }
            else:
                diff[key] = {"scenario1": v1, "scenario2": v2, "difference": "Non-numeric"}
        return {
            "scenario1_id": scenario1.id, "scenario2_id": scenario2.id,
            "differences": diff,
            "confidence_gap": scenario1.confidence - scenario2.confidence,
            "probability_gap": scenario1.probability - scenario2.probability,
        }
