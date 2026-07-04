import pytest
from discovery.adaptive_experiment_planner import AdaptiveExperimentPlanner, Experiment


def test_create_experiment():
    planner = AdaptiveExperimentPlanner()
    exp = planner.create_experiment("LR Test", "LR improves accuracy", {"lr": 0.01})
    assert exp.name == "LR Test"
    assert exp.status == "planned"


def test_start_experiment():
    planner = AdaptiveExperimentPlanner()
    exp = planner.create_experiment("E1", "H1", {"x": 1.0})
    ok = planner.start_experiment(exp.id)
    assert ok is True
    assert exp.status == "running"


def test_start_unknown_experiment():
    planner = AdaptiveExperimentPlanner()
    assert planner.start_experiment("bad_id") is False


def test_record_iteration():
    planner = AdaptiveExperimentPlanner()
    exp = planner.create_experiment("E", "H", {"lr": 0.01})
    planner.start_experiment(exp.id)
    result = planner.record_iteration(exp.id, {"accuracy": 0.8, "performance": 0.9})
    assert result["iteration"] == 1
    assert result["results"]["accuracy"] == 0.8


def test_convergence_detection():
    planner = AdaptiveExperimentPlanner()
    exp = planner.create_experiment("E", "H", {"lr": 0.01}, metrics=["accuracy"])
    planner.start_experiment(exp.id)
    for _ in range(6):
        planner.record_iteration(exp.id, {"accuracy": 0.9})
    assert exp.status == "converged"


def test_complete_experiment():
    planner = AdaptiveExperimentPlanner()
    exp = planner.create_experiment("E", "H", {})
    planner.start_experiment(exp.id)
    ok = planner.complete_experiment(exp.id)
    assert ok is True
    assert exp.status == "completed"


def test_adapt_variables():
    planner = AdaptiveExperimentPlanner(seed=42)
    exp = planner.create_experiment("E", "H", {"lr": 0.01, "batch": 32})
    planner.start_experiment(exp.id)
    adapted = planner.adapt_variables(exp.id)
    assert "lr" in adapted
    assert adapted["lr"] != 0.01  # should be mutated


def test_get_next_experiment():
    planner = AdaptiveExperimentPlanner()
    planner.create_experiment("low", "H", {}, priority=0.2)
    planner.create_experiment("high", "H", {}, priority=0.9)
    next_exp = planner.get_next_experiment()
    assert next_exp is not None
    assert next_exp.name == "high"


def test_planner_report():
    planner = AdaptiveExperimentPlanner()
    planner.create_experiment("E1", "H", {})
    planner.create_experiment("E2", "H", {})
    report = planner.get_planner_report()
    assert report["total"] == 2
    assert report["planned"] == 2
