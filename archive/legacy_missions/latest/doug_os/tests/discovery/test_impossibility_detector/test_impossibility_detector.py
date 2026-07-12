import pytest
from doug_os.discovery.impossibility_detector import ImpossibilityDetector, ImpossibilityCheck


@pytest.fixture
def detector():
    return ImpossibilityDetector()


def test_valid_hypothesis_not_impossible(detector):
    result = detector.check(
        hypothesis="Higher marketing spend increases brand awareness",
        variables={"probability": 0.7, "variance": 0.5, "correlation": 0.6},
    )
    assert isinstance(result, ImpossibilityCheck)
    assert result.is_impossible is False
    assert result.veto is False
    assert len(result.violations) == 0


def test_logical_contradiction_generates_violation(detector):
    result = detector.check(
        hypothesis="Prices will increase and decrease simultaneously",
        variables={},
    )
    assert any("Logical" in v for v in result.violations)


def test_negative_variance_generates_statistical_violation(detector):
    result = detector.check(
        hypothesis="Returns are normally distributed",
        variables={"variance": -1.0},
    )
    assert any("Statistical" in v for v in result.violations)
    assert any("Variance cannot be negative" in v for v in result.violations)


def test_correlation_out_of_range_generates_violation(detector):
    result = detector.check(
        hypothesis="X and Y are correlated",
        variables={"correlation": 1.5},
    )
    assert any("Statistical" in v for v in result.violations)


def test_probability_out_of_range_generates_violation(detector):
    result = detector.check(
        hypothesis="Event probability is known",
        variables={"probability": 1.5},
    )
    assert any("Statistical" in v for v in result.violations)


def test_sum_of_probabilities_exceeds_one(detector):
    result = detector.check(
        hypothesis="Mutually exclusive outcomes",
        variables={"prob_A": 0.6, "prob_B": 0.5},
    )
    assert any("Probabilistic" in v for v in result.violations)


def test_guaranteed_return_above_one_impossible(detector):
    result = detector.check(
        hypothesis="This asset guarantees returns",
        variables={"guaranteed_return": 1.5},
    )
    assert any("Probabilistic" in v for v in result.violations)


def test_known_impossibility_guaranteed_arbitrage(detector):
    result = detector.check(
        hypothesis="This strategy provides guaranteed_arbitrage in all markets",
        variables={},
    )
    assert any("Known impossibility" in v for v in result.violations)


def test_veto_true_when_three_or_more_violations(detector):
    # 3 violations: logical contradiction + negative variance + prob sum > 1
    result = detector.check(
        hypothesis="Prices will increase and decrease",  # logical
        variables={
            "variance": -1.0,  # statistical
            "prob_A": 0.7, "prob_B": 0.6,  # probabilistic
        },
    )
    assert len(result.violations) >= 3
    assert result.veto is True
    assert result.is_impossible is True


def test_is_impossible_when_two_violations(detector):
    # 2 violations: negative variance + prob sum > 1
    result = detector.check(
        hypothesis="A neutral hypothesis",
        variables={
            "variance": -1.0,
            "prob_A": 0.7, "prob_B": 0.6,
        },
    )
    assert len(result.violations) >= 2
    assert result.is_impossible is True


def test_to_dict_serializes_correctly(detector):
    result = detector.check(
        hypothesis="Something valid",
        variables={"probability": 0.5},
    )
    d = result.to_dict()
    assert "is_impossible" in d
    assert "violations" in d
    assert "suggestions" in d
    assert "veto" in d
    assert "confidence" in d
    assert "reason" in d
    assert isinstance(d["violations"], list)


def test_suggestions_provided_for_violations(detector):
    result = detector.check(
        hypothesis="Returns will buy and sell simultaneously",
        variables={"variance": -0.5},
    )
    assert len(result.suggestions) > 0


def test_confidence_between_0_and_1(detector):
    result = detector.check(
        hypothesis="Some hypothesis",
        variables={"probability": 0.5},
    )
    assert 0.0 <= result.confidence <= 1.0
