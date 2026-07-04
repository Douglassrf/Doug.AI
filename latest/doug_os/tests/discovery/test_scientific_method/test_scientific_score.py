import pytest
from doug_os.discovery.scientific_method.scientific_score import (
    ScientificScore, ScientificScoreCalculator
)


@pytest.fixture
def calculator():
    return ScientificScoreCalculator()


def test_score_all_zeros():
    s = ScientificScore()
    s.calculate_overall()
    assert s.overall_score == pytest.approx(0.0)


def test_score_calculation_high_quality(calculator):
    protocol_data = {
        "question": "Does X affect Y?",
        "hypothesis_formulation": "If X increases, Y increases",
        "independent_variables": ["X"],
        "dependent_variables": ["Y"],
        "success_criteria": {"effect_size": 0.2},
        "novel_combination": True,
        "contribution": "New insight",
    }
    results = {
        "effect_size": 0.5,
        "p_value": 0.01,
        "confidence_level": 0.95,
        "sample_size": 200,
        "repetitions": 5,
        "consistency": 0.9,
        "variance": 0.1,
        "stress_tests_passed": 5,
        "sensitivity": 0.8,
        "conditions_tested": 4,
    }
    score = calculator.calculate(protocol_data, results)
    assert score.overall_score > 0.7


def test_recommendations_generated_for_low_scores(calculator):
    score = calculator.calculate({}, {})
    assert len(score.recommendations) > 0


def test_score_to_dict(calculator):
    score = calculator.calculate({}, {})
    d = score.to_dict()
    assert "overall_score" in d
    assert "recommendations" in d
    assert isinstance(d["recommendations"], list)
