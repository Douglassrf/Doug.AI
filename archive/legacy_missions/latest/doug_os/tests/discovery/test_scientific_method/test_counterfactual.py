import pytest
from doug_os.discovery.scientific_method.counterfactual import CounterfactualEngine


@pytest.fixture
def engine():
    return CounterfactualEngine()


def test_counterfactual_basic(engine):
    result = engine.analyze(
        historical_data={"outcome": 100.0, "variance": 0.05},
        intervention={"description": "reduce fees by 50%", "effect_multiplier": 1.2},
    )
    assert result.expected_outcome == pytest.approx(120.0)
    assert result.confidence > 0.8


def test_counterfactual_high_variance_lowers_confidence(engine):
    low_var = engine.analyze(
        historical_data={"outcome": 100.0, "variance": 0.01},
        intervention={"effect_multiplier": 1.0},
    )
    high_var = engine.analyze(
        historical_data={"outcome": 100.0, "variance": 5.0},
        intervention={"effect_multiplier": 1.0},
    )
    assert low_var.confidence > high_var.confidence


def test_counterfactual_zero_multiplier(engine):
    result = engine.analyze(
        historical_data={"outcome": 50.0},
        intervention={"effect_multiplier": 0.0, "description": "halt trading"},
    )
    assert result.expected_outcome == pytest.approx(0.0)


def test_counterfactual_has_assumptions(engine):
    result = engine.analyze(
        historical_data={"outcome": 10.0},
        intervention={"effect_multiplier": 1.5},
    )
    assert len(result.assumptions) >= 3


def test_counterfactual_reasoning_contains_values(engine):
    result = engine.analyze(
        historical_data={"outcome": 200.0},
        intervention={"effect_multiplier": 0.5, "description": "cut position size"},
    )
    assert "200" in result.reasoning or "100" in result.reasoning
