import pytest
from doug_os.discovery.adversarial_servo_training import (
    AdversarialServoTraining, AdversarialScenario, AdversarialResult
)


@pytest.fixture
def trainer():
    return AdversarialServoTraining()


@pytest.fixture
def scenarios(trainer):
    return trainer.generate_scenarios(n_scenarios=5, seed=42)


def test_generate_scenarios_count(trainer):
    scenarios = trainer.generate_scenarios(n_scenarios=7, seed=0)
    assert len(scenarios) == 7


def test_scenario_type_valid(trainer):
    scenarios = trainer.generate_scenarios(n_scenarios=20, seed=1)
    for s in scenarios:
        assert s.scenario_type in AdversarialServoTraining._SCENARIO_TYPES


def test_severity_range(trainer):
    scenarios = trainer.generate_scenarios(n_scenarios=20, seed=2)
    for s in scenarios:
        assert 0.3 <= s.severity <= 0.9


def test_run_scenario_resilience(trainer, scenarios):
    scenario = scenarios[0]
    response = {
        "baseline_performance": 0.8,
        "stressed_performance": 0.6,
        "volatility_increase": 0.1,
        "decision_instability": 0.1,
        "decision_quality": 0.7,
        "recovery_time_ms": 50.0,
    }
    result = trainer.run_scenario(scenario, response)
    assert abs(result.model_resilience - 0.75) < 1e-9


def test_panic_calculation(trainer, scenarios):
    scenario = scenarios[0]
    response = {
        "baseline_performance": 0.8,
        "stressed_performance": 0.6,
        "volatility_increase": 0.6,
        "decision_instability": 0.4,
        "decision_quality": 0.5,
    }
    result = trainer.run_scenario(scenario, response)
    assert abs(result.panic_level - 0.5) < 1e-9


def test_weakness_low_resilience(trainer, scenarios):
    scenario = scenarios[0]
    response = {
        "baseline_performance": 1.0,
        "stressed_performance": 0.3,  # resilience = 0.3 < 0.5
        "volatility_increase": 0.1,
        "decision_instability": 0.1,
        "decision_quality": 0.5,
    }
    result = trainer.run_scenario(scenario, response)
    assert "Low resilience under stress" in result.weaknesses


def test_strength_high_resilience(trainer, scenarios):
    scenario = scenarios[0]
    response = {
        "baseline_performance": 1.0,
        "stressed_performance": 0.9,  # resilience = 0.9 > 0.8
        "volatility_increase": 0.1,
        "decision_instability": 0.1,
        "decision_quality": 0.5,
    }
    result = trainer.run_scenario(scenario, response)
    assert "High resilience under stress" in result.strengths


def test_get_resistance_report(trainer, scenarios):
    for s in scenarios:
        trainer.run_scenario(s, {
            "baseline_performance": 0.8,
            "stressed_performance": 0.7,
            "volatility_increase": 0.2,
            "decision_instability": 0.1,
            "decision_quality": 0.8,
        })
    report = trainer.get_resistance_report()
    assert "overall_score" in report
    assert 0.0 <= report["overall_score"] <= 1.0


def test_get_resistance_report_no_data(trainer):
    report = trainer.get_resistance_report()
    assert report == {"status": "no_data"}
