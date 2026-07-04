from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class SwarmAgent:
    id: str = field(default_factory=lambda: f"sa_{uuid.uuid4().hex[:12]}")
    position: List[float] = field(default_factory=lambda: [0.0, 0.0])
    velocity: List[float] = field(default_factory=lambda: [0.0, 0.0])
    best_position: List[float] = field(default_factory=lambda: [0.0, 0.0])
    best_score: float = float("-inf")
    current_score: float = float("-inf")
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "position": self.position,
            "velocity": self.velocity,
            "best_score": self.best_score,
            "current_score": self.current_score,
            "created_at": self.created_at.isoformat(),
        }


class SwarmIntelligenceEngine:
    """Motor de inteligência de enxame (PSO) para otimização distribuída."""

    def __init__(
        self,
        n_agents: int = 20,
        dimensions: int = 2,
        inertia: float = 0.7,
        cognitive: float = 1.5,
        social: float = 1.5,
        seed: int = 42,
    ) -> None:
        self._rng = np.random.default_rng(seed)
        self._n_agents = n_agents
        self._dimensions = dimensions
        self._inertia = inertia
        self._cognitive = cognitive
        self._social = social
        self._agents: List[SwarmAgent] = []
        self._global_best_position: List[float] = [0.0] * dimensions
        self._global_best_score: float = float("-inf")
        self._iteration = 0
        self._history: List[float] = []

    def initialize(self, bounds: List[tuple]) -> None:
        """Inicializa agentes dentro dos limites fornecidos."""
        self._agents = []
        for _ in range(self._n_agents):
            pos = [float(self._rng.uniform(b[0], b[1])) for b in bounds]
            vel = [float(self._rng.uniform(-1.0, 1.0)) for _ in bounds]
            agent = SwarmAgent(position=pos, velocity=vel, best_position=pos[:])
            self._agents.append(agent)

    def evaluate(self, objective_fn) -> float:
        """Avalia todos os agentes com a função objetivo."""
        for agent in self._agents:
            score = float(objective_fn(agent.position))
            agent.current_score = score
            if score > agent.best_score:
                agent.best_score = score
                agent.best_position = agent.position[:]
            if score > self._global_best_score:
                self._global_best_score = score
                self._global_best_position = agent.position[:]
        self._history.append(self._global_best_score)
        return self._global_best_score

    def step(self, bounds: List[tuple]) -> None:
        """Executa um passo PSO."""
        for agent in self._agents:
            for d in range(self._dimensions):
                r1 = float(self._rng.uniform(0, 1))
                r2 = float(self._rng.uniform(0, 1))
                cognitive_v = self._cognitive * r1 * (agent.best_position[d] - agent.position[d])
                social_v = self._social * r2 * (self._global_best_position[d] - agent.position[d])
                agent.velocity[d] = self._inertia * agent.velocity[d] + cognitive_v + social_v
                new_pos = agent.position[d] + agent.velocity[d]
                agent.position[d] = max(bounds[d][0], min(bounds[d][1], new_pos))
        self._iteration += 1

    def run(self, objective_fn, bounds: List[tuple], iterations: int = 50) -> Dict[str, Any]:
        self.initialize(bounds)
        for _ in range(iterations):
            self.evaluate(objective_fn)
            self.step(bounds)
        return {
            "best_position": self._global_best_position,
            "best_score": self._global_best_score,
            "iterations": self._iteration,
            "convergence": self._history[-10:],
        }

    def get_swarm_dashboard(self) -> Dict[str, Any]:
        return {
            "n_agents": self._n_agents,
            "dimensions": self._dimensions,
            "iterations_run": self._iteration,
            "global_best_score": self._global_best_score,
            "global_best_position": self._global_best_position,
            "convergence_history": self._history[-20:],
        }
