from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class Experiment:
    id: str = field(default_factory=lambda: f"exp_{uuid.uuid4().hex[:12]}")
    name: str = ""
    hypothesis: str = ""
    variables: Dict[str, Any] = field(default_factory=dict)
    metrics: List[str] = field(default_factory=list)
    status: str = "planned"
    priority: float = 0.5
    results: Dict[str, Any] = field(default_factory=dict)
    iterations: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "hypothesis": self.hypothesis,
            "variables": self.variables,
            "metrics": self.metrics,
            "status": self.status,
            "priority": self.priority,
            "results": self.results,
            "iterations": self.iterations,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class AdaptiveExperimentPlanner:
    """Planejador adaptativo de experimentos — prioriza, adapta variáveis e detecta convergência."""

    def __init__(self, seed: int = 42) -> None:
        self._experiments: Dict[str, Experiment] = {}
        self._rng = np.random.default_rng(seed)
        self._active: Set[str] = set()
        self._completed: List[str] = []

    def create_experiment(
        self,
        name: str,
        hypothesis: str,
        variables: Dict[str, Any],
        metrics: Optional[List[str]] = None,
        priority: float = 0.5,
    ) -> Experiment:
        exp = Experiment(
            name=name,
            hypothesis=hypothesis,
            variables=variables,
            metrics=metrics or ["accuracy", "performance"],
            priority=priority,
        )
        self._experiments[exp.id] = exp
        return exp

    def start_experiment(self, exp_id: str) -> bool:
        exp = self._experiments.get(exp_id)
        if not exp or exp.status != "planned":
            return False
        exp.status = "running"
        self._active.add(exp_id)
        return True

    def record_iteration(self, exp_id: str, results: Dict[str, float]) -> Dict[str, Any]:
        exp = self._experiments.get(exp_id)
        if not exp or exp.status != "running":
            return {"error": "Experiment not running"}

        exp.iterations += 1
        for k, v in results.items():
            if k not in exp.results:
                exp.results[k] = []
            exp.results[k].append(v)

        converged = self._check_convergence(exp)
        if converged:
            exp.status = "converged"

        return {
            "iteration": exp.iterations,
            "results": results,
            "converged": converged,
        }

    def _check_convergence(self, exp: Experiment, window: int = 5, threshold: float = 0.01) -> bool:
        for metric, values in exp.results.items():
            if not isinstance(values, list) or len(values) < window:
                return False
            recent = np.array(values[-window:], dtype=float)
            if recent.std() > threshold:
                return False
        return exp.iterations >= window

    def complete_experiment(self, exp_id: str) -> bool:
        exp = self._experiments.get(exp_id)
        if not exp or exp.status not in ("running", "converged"):
            return False
        exp.status = "completed"
        exp.completed_at = datetime.now(timezone.utc)
        self._active.discard(exp_id)
        self._completed.append(exp_id)
        return True

    def adapt_variables(self, exp_id: str) -> Dict[str, Any]:
        exp = self._experiments.get(exp_id)
        if not exp:
            return {}
        adapted = {}
        for key, val in exp.variables.items():
            if isinstance(val, float):
                noise = float(self._rng.uniform(-0.1, 0.1))
                adapted[key] = val * (1.0 + noise)
            else:
                adapted[key] = val
        exp.variables = adapted
        return adapted

    def get_next_experiment(self) -> Optional[Experiment]:
        planned = [e for e in self._experiments.values() if e.status == "planned"]
        if not planned:
            return None
        return max(planned, key=lambda e: e.priority)

    def get_planner_report(self) -> Dict[str, Any]:
        exps = list(self._experiments.values())
        return {
            "total": len(exps),
            "planned": sum(1 for e in exps if e.status == "planned"),
            "running": sum(1 for e in exps if e.status == "running"),
            "completed": sum(1 for e in exps if e.status == "completed"),
            "converged": sum(1 for e in exps if e.status == "converged"),
            "active_ids": list(self._active),
        }
