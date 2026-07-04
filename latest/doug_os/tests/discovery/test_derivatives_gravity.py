import pytest
from datetime import datetime, timezone
from doug_os.discovery.derivatives_gravity import (
    DerivativeData, GravityIndex, DerivativesGravityEngine
)


def make_data(oi=500.0, gamma=50.0, delta=50.0, dealer=50.0, vol=50.0, pc=1.0):
    return DerivativeData(
        timestamp=datetime.now(timezone.utc),
        open_interest=oi,
        gamma_exposure=gamma,
        delta_exposure=delta,
        dealer_delta=dealer,
        options_volume=vol,
        puts_calls_ratio=pc,
    )


def test_analyze_returns_gravity_index_between_0_and_1():
    engine = DerivativesGravityEngine()
    result = engine.analyze(make_data())
    assert isinstance(result, GravityIndex)
    assert 0.0 <= result.index <= 1.0


def test_risk_level_extreme_when_index_above_0_8():
    engine = DerivativesGravityEngine()
    # Max all values to push index above 0.8
    result = engine.analyze(make_data(oi=1000.0, gamma=100.0, delta=100.0,
                                       dealer=100.0, vol=100.0, pc=2.0))
    assert result.index > 0.8
    assert result.risk_level == "extreme"


def test_risk_level_low_when_index_at_or_below_0_4():
    engine = DerivativesGravityEngine()
    # Zero values → defaults give low components
    data = DerivativeData(
        timestamp=datetime.now(timezone.utc),
        open_interest=0.0, gamma_exposure=0.0, delta_exposure=0.0,
        dealer_delta=0.0, options_volume=0.0, puts_calls_ratio=0.0,
    )
    result = engine.analyze(data)
    assert result.index <= 0.4
    assert result.risk_level == "low"


def test_components_calculated_correctly_with_open_interest():
    engine = DerivativesGravityEngine()
    data = make_data(oi=500.0)
    result = engine.analyze(data)
    assert "open_interest" in result.components
    assert result.components["open_interest"] == pytest.approx(0.5, abs=0.01)


def test_gravity_score_and_pressure_score_compose_index():
    engine = DerivativesGravityEngine()
    result = engine.analyze(make_data())
    assert result.index == pytest.approx((result.gravity_score + result.pressure_score) / 2, abs=1e-9)


def test_to_dict_serializes_all_fields():
    engine = DerivativesGravityEngine()
    result = engine.analyze(make_data())
    d = result.to_dict()
    for key in ["index", "gravity_score", "pressure_score", "risk_level", "components", "created_at"]:
        assert key in d
    assert isinstance(d["components"], dict)
    assert isinstance(d["created_at"], str)
