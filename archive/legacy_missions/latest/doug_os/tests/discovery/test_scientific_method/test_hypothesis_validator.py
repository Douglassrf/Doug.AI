import pytest
from doug_os.discovery.scientific_method.hypothesis_validator import HypothesisValidator


@pytest.fixture
def validator():
    return HypothesisValidator()


def test_good_hypothesis(validator):
    result = validator.validate(
        "If market volatility increases, then trading volume will increase significantly"
    )
    assert result.valid is True
    assert result.score > 0.7
    assert result.errors == []


def test_bad_hypothesis_not_falsifiable(validator):
    result = validator.validate("Market is volatile")
    assert result.valid is False
    assert any("falsifiable" in e for e in result.errors)


def test_short_hypothesis_gives_warning(validator):
    result = validator.validate("If X then Y will change")
    assert any("short" in w for w in result.warnings)


def test_score_bounded_0_to_1(validator):
    result = validator.validate(
        "If market volatility increases between sessions, trading data will be observed "
        "and statistically measured as significantly different within asset classes"
    )
    assert 0.0 <= result.score <= 1.0
