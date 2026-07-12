import pytest
from doug_os.discovery.probabilistic_scenario_engine import (
    ProbabilisticScenarioEngine, Scenario, ScenarioTree,
)


@pytest.fixture
def engine():
    return ProbabilisticScenarioEngine(seed=42)


BASE = {"price": 100.0, "volume": 1000.0, "sentiment": 0.5}


def test_generate_scenarios_count(engine):
    scenarios = engine.generate_scenarios(BASE, n_scenarios=5)
    assert len(scenarios) == 5


def test_generate_scenarios_probabilities_sum_to_1(engine):
    scenarios = engine.generate_scenarios(BASE, n_scenarios=4)
    total = sum(s.probability for s in scenarios)
    assert abs(total - 1.0) < 1e-6


def test_generate_scenarios_confidence_in_range(engine):
    scenarios = engine.generate_scenarios(BASE, n_scenarios=3)
    for s in scenarios:
        assert 0.0 <= s.confidence <= 1.0


def test_build_scenario_tree_has_root(engine):
    tree = engine.build_scenario_tree(BASE, depth=2, branching_factor=2)
    assert tree.root_scenario.name == "Root"
    assert len(tree.branches) > 0


def test_build_scenario_tree_probabilities(engine):
    tree = engine.build_scenario_tree(BASE, depth=1, branching_factor=3)
    assert "root" in tree.probabilities


def test_rank_scenarios(engine):
    scenarios = engine.generate_scenarios(BASE, n_scenarios=5)
    criteria = {"probability": 0.4, "confidence": 0.3, "outcome": 0.3}
    ranked = engine.rank_scenarios(scenarios, criteria)
    assert len(ranked) == 5


def test_get_best_scenario(engine):
    scenarios = engine.generate_scenarios(BASE, n_scenarios=3)
    best = engine.get_best_scenario(scenarios)
    assert best is not None
    assert isinstance(best, Scenario)


def test_get_best_scenario_empty(engine):
    assert engine.get_best_scenario([]) is None


def test_compare_scenarios(engine):
    scenarios = engine.generate_scenarios(BASE, n_scenarios=2)
    comparison = engine.compare_scenarios(scenarios[0], scenarios[1])
    assert "differences" in comparison
    assert "probability_gap" in comparison


def test_to_dict_scenario(engine):
    scenarios = engine.generate_scenarios(BASE, n_scenarios=1)
    d = scenarios[0].to_dict()
    assert all(k in d for k in ("id", "name", "probability", "confidence", "outcome"))


def test_to_dict_tree(engine):
    tree = engine.build_scenario_tree(BASE, depth=1, branching_factor=2)
    d = tree.to_dict()
    assert "root_scenario" in d and "branches" in d
