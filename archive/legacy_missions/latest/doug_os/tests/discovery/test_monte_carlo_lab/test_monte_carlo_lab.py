import pytest
from doug_os.discovery.monte_carlo_lab import MonteCarloAdaptiveLab, MonteCarloResult


def constant_model(params):
    return 1.0


def normal_model(params):
    import numpy as np
    rng = np.random.default_rng()
    return float(rng.normal(loc=params.get("mean", 1.0), scale=params.get("std", 0.1)))


def negative_model(params):
    return -5.0


@pytest.fixture
def lab():
    return MonteCarloAdaptiveLab(seed=42)


def test_result_has_correct_fields(lab):
    result = lab.run_simulation(
        hypothesis_id="h_001",
        model=normal_model,
        parameters={"mean": 2.0, "std": 0.2},
        iterations=500,
    )
    assert isinstance(result, MonteCarloResult)
    assert result.hypothesis_id == "h_001"
    assert result.mean != 0.0
    assert result.std >= 0.0
    assert result.min <= result.mean <= result.max
    assert len(result.confidence_interval_95) == 2
    assert result.confidence_interval_95[0] <= result.confidence_interval_95[1]


def test_bootstrap_estimates_count(lab):
    result = lab.run_simulation(
        hypothesis_id="h_002",
        model=normal_model,
        parameters={"mean": 1.0, "std": 0.1},
        iterations=300,
    )
    assert len(result.bootstrap_estimates) == 500


def test_stress_results_has_six_scenarios(lab):
    result = lab.run_simulation(
        hypothesis_id="h_003",
        model=normal_model,
        parameters={"mean": 1.0, "std": 0.1, "base": 1.0},
        iterations=200,
    )
    assert len(result.stress_results) == 6
    scenario_names = {s["scenario"] for s in result.stress_results}
    assert "normal" in scenario_names
    assert "extreme" in scenario_names
    assert "crash" in scenario_names


def test_convergence_stops_early(lab):
    result = lab.run_simulation(
        hypothesis_id="h_004",
        model=constant_model,
        parameters={},
        iterations=10_000,
        convergence_threshold=0.001,
    )
    # Constant model should converge well before 10000
    assert result.iterations < 10_000


def test_failure_probability_zero_above_threshold(lab):
    result = lab.run_simulation(
        hypothesis_id="h_005",
        model=constant_model,
        parameters={"failure_threshold": 0.5},
        iterations=500,
    )
    # All values are 1.0, threshold is 0.5 — no failures
    assert result.failure_probability == 0.0


def test_failure_probability_positive(lab):
    result = lab.run_simulation(
        hypothesis_id="h_006",
        model=negative_model,
        parameters={"failure_threshold": 0.0},
        iterations=200,
    )
    # All values are -5.0, threshold is 0.0 — all fail
    assert result.failure_probability == 1.0


def test_robustness_score_between_0_and_1(lab):
    result = lab.run_simulation(
        hypothesis_id="h_007",
        model=normal_model,
        parameters={"mean": 5.0, "std": 0.5},
        iterations=300,
    )
    assert 0.0 <= result.robustness_score <= 1.0


def test_to_dict_serializes_correctly(lab):
    result = lab.run_simulation(
        hypothesis_id="h_008",
        model=constant_model,
        parameters={},
        iterations=200,
    )
    d = result.to_dict()
    assert d["hypothesis_id"] == "h_008"
    assert isinstance(d["mean"], float)
    assert isinstance(d["confidence_interval_95"], list)
    assert len(d["confidence_interval_95"]) == 2
    assert "created_at" in d


def test_get_result_by_id(lab):
    result = lab.run_simulation(
        hypothesis_id="h_009",
        model=constant_model,
        parameters={},
        iterations=100,
    )
    fetched = lab.get_result(result.id)
    assert fetched is result


def test_get_result_missing_returns_none(lab):
    assert lab.get_result("nonexistent") is None
