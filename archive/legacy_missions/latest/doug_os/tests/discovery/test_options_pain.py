import pytest
from datetime import datetime, timezone
from doug_os.discovery.options_pain import (
    OptionCluster, OptionsPainResult, OptionsPainEngine
)


def test_calculate_pain_returns_options_pain_result():
    engine = OptionsPainEngine()
    calls = [{"strike": 100.0, "open_interest": 500.0, "gamma": 0.3, "delta": 0.5}]
    puts = [{"strike": 95.0, "open_interest": 300.0, "gamma": 0.2, "delta": -0.4}]
    result = engine.calculate_pain(calls, puts, current_price=98.0)
    assert isinstance(result, OptionsPainResult)


def test_max_pain_is_strike_with_highest_total_oi():
    engine = OptionsPainEngine()
    calls = [
        {"strike": 100.0, "open_interest": 1000.0, "gamma": 0.1, "delta": 0.5},
        {"strike": 105.0, "open_interest": 200.0, "gamma": 0.1, "delta": 0.3},
    ]
    puts = [
        {"strike": 100.0, "open_interest": 800.0, "gamma": 0.1, "delta": -0.4},
    ]
    result = engine.calculate_pain(calls, puts, current_price=102.0)
    # Strike 100 has OI 1000+800=1800, strike 105 has OI 200
    assert result.max_pain_price == 100.0


def test_pain_gap_equals_abs_diff_current_and_max_pain():
    engine = OptionsPainEngine()
    calls = [{"strike": 90.0, "open_interest": 1000.0, "gamma": 0.1, "delta": 0.5}]
    puts = []
    result = engine.calculate_pain(calls, puts, current_price=100.0)
    assert result.pain_gap == pytest.approx(abs(100.0 - result.max_pain_price), abs=1e-9)


def test_gamma_walls_detects_up_to_5_strikes():
    engine = OptionsPainEngine()
    calls = [{"strike": float(s), "open_interest": 100.0, "gamma": float(s), "delta": 0.5}
             for s in range(10, 70, 10)]
    puts = []
    result = engine.calculate_pain(calls, puts, current_price=40.0)
    assert len(result.gamma_walls) <= 5
    # Highest gamma strike (60) should be first
    assert result.gamma_walls[0] == 60.0


def test_expiration_pressure_is_proportion_atm_oi():
    engine = OptionsPainEngine()
    # ATM: strikes between 0.95 and 1.05
    calls = [
        {"strike": 1.0, "open_interest": 500.0, "gamma": 0.1, "delta": 0.5},
        {"strike": 2.0, "open_interest": 500.0, "gamma": 0.1, "delta": 0.5},
    ]
    puts = []
    result = engine.calculate_pain(calls, puts, current_price=1.0)
    # Only strike 1.0 is in [0.95, 1.05]; total OI = 1000
    assert result.expiration_pressure == pytest.approx(0.5, abs=0.01)


def test_to_dict_serializes_correctly():
    engine = OptionsPainEngine()
    calls = [{"strike": 100.0, "open_interest": 200.0, "gamma": 0.2, "delta": 0.5}]
    puts = [{"strike": 95.0, "open_interest": 100.0, "gamma": 0.1, "delta": -0.3}]
    result = engine.calculate_pain(calls, puts, current_price=98.0)
    d = result.to_dict()
    for key in ["max_pain_price", "current_price", "pain_gap", "gamma_walls",
                "expiration_pressure", "created_at"]:
        assert key in d
    assert isinstance(d["gamma_walls"], list)
    assert isinstance(d["created_at"], str)
