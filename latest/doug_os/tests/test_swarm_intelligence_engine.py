import pytest
import numpy as np
from discovery.swarm_intelligence_engine import SwarmIntelligenceEngine, SwarmAgent


def sphere(pos):
    return -sum(x ** 2 for x in pos)  # maximize (minimizing sphere = finding 0)


def test_initialize_agents():
    engine = SwarmIntelligenceEngine(n_agents=10, dimensions=2, seed=42)
    bounds = [(-5.0, 5.0), (-5.0, 5.0)]
    engine.initialize(bounds)
    assert len(engine._agents) == 10
    for agent in engine._agents:
        assert len(agent.position) == 2


def test_positions_within_bounds():
    engine = SwarmIntelligenceEngine(n_agents=5, dimensions=2, seed=42)
    bounds = [(-3.0, 3.0), (-3.0, 3.0)]
    engine.initialize(bounds)
    for agent in engine._agents:
        for i, (lo, hi) in enumerate(bounds):
            assert lo <= agent.position[i] <= hi


def test_evaluate_updates_scores():
    engine = SwarmIntelligenceEngine(n_agents=5, dimensions=2, seed=42)
    bounds = [(-5.0, 5.0), (-5.0, 5.0)]
    engine.initialize(bounds)
    best = engine.evaluate(sphere)
    assert best <= 0.0
    assert engine._global_best_score > float("-inf")


def test_step_moves_agents():
    engine = SwarmIntelligenceEngine(n_agents=5, dimensions=2, seed=42)
    bounds = [(-5.0, 5.0), (-5.0, 5.0)]
    engine.initialize(bounds)
    engine.evaluate(sphere)
    positions_before = [agent.position[:] for agent in engine._agents]
    engine.step(bounds)
    positions_after = [agent.position for agent in engine._agents]
    changed = any(b != a for b, a in zip(positions_before, positions_after))
    assert changed


def test_run_finds_optimum():
    engine = SwarmIntelligenceEngine(n_agents=20, dimensions=2, seed=42)
    bounds = [(-5.0, 5.0), (-5.0, 5.0)]
    result = engine.run(sphere, bounds, iterations=50)
    assert result["best_score"] > -1.0  # near 0 = good


def test_run_returns_structure():
    engine = SwarmIntelligenceEngine(n_agents=10, dimensions=2, seed=99)
    bounds = [(-2.0, 2.0), (-2.0, 2.0)]
    result = engine.run(sphere, bounds, iterations=10)
    assert "best_position" in result
    assert "best_score" in result
    assert "iterations" in result


def test_convergence_improves():
    engine = SwarmIntelligenceEngine(n_agents=15, dimensions=2, seed=42)
    bounds = [(-5.0, 5.0), (-5.0, 5.0)]
    result = engine.run(sphere, bounds, iterations=30)
    history = result["convergence"]
    assert len(history) > 0


def test_swarm_dashboard():
    engine = SwarmIntelligenceEngine(n_agents=5, dimensions=2, seed=42)
    bounds = [(-2.0, 2.0), (-2.0, 2.0)]
    engine.run(sphere, bounds, iterations=5)
    dash = engine.get_swarm_dashboard()
    assert "n_agents" in dash
    assert dash["n_agents"] == 5
    assert dash["iterations_run"] > 0


def test_agent_to_dict():
    agent = SwarmAgent(position=[1.0, 2.0], velocity=[0.1, 0.2])
    d = agent.to_dict()
    assert d["position"] == [1.0, 2.0]
