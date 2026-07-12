import pytest
from doug_os.discovery.regime_transition_intelligence import (
    RegimeTransitionIntelligence, RegimeTransition
)


def make_engine():
    return RegimeTransitionIntelligence()


INDICATORS_HIGH = {
    "volatility": 0.8,
    "momentum": 0.5,
    "volume_ratio": 3.0,
    "trend_change": 0.5,
    "anomaly": 0.8,
}

INDICATORS_LOW = {
    "volatility": 0.1,
    "momentum": 0.1,
    "volume_ratio": 1.0,
    "trend_change": 0.1,
    "anomaly": 0.1,
}


def test_analyze_returns_regime_transition():
    eng = make_engine()
    t = eng.analyze("bull", INDICATORS_HIGH)
    assert isinstance(t, RegimeTransition)
    assert t.current_regime == "bull"
    assert t.transition_score >= 0.0
    assert t.early_confidence >= 0.0
    assert t.transition_type in ("none", "soft", "hard")


def test_first_call_previous_equals_current():
    eng = make_engine()
    t = eng.analyze("bull", INDICATORS_LOW)
    assert t.previous_regime == "bull"


def test_second_call_different_regime():
    eng = make_engine()
    eng.analyze("bull", INDICATORS_LOW)
    t = eng.analyze("bear", INDICATORS_LOW)
    assert t.previous_regime == "bull"
    assert t.current_regime == "bear"


def test_high_indicators_transition_score_above_04():
    eng = make_engine()
    t = eng.analyze("bull", INDICATORS_HIGH)
    assert t.transition_score > 0.4


def test_hard_transition_type():
    eng = make_engine()
    # force score > 0.7 and confidence > 0.7
    indicators = {
        "volatility": 0.9,
        "momentum": 0.9,
        "volume_ratio": 3.0,
        "trend_change": 0.9,
        "anomaly": 0.9,
    }
    t = eng.analyze("crisis", indicators)
    assert t.transition_score > 0.7
    assert t.early_confidence > 0.7
    assert t.transition_type == "hard"


def test_none_transition_type_low_score():
    eng = make_engine()
    t = eng.analyze("bull", INDICATORS_LOW)
    # score should be 0 (no indicator breaches threshold)
    assert t.transition_score <= 0.4
    assert t.transition_type == "none"


def test_get_transition_alerts_filters_threshold():
    eng = make_engine()
    eng.analyze("bull", INDICATORS_LOW)   # low score
    eng.analyze("bear", INDICATORS_HIGH)  # high score
    alerts = eng.get_transition_alerts(threshold=0.4)
    assert len(alerts) >= 1
    assert all(a.transition_score > 0.4 for a in alerts)


def test_get_transition_alerts_empty_when_high_threshold():
    eng = make_engine()
    eng.analyze("bull", INDICATORS_LOW)
    alerts = eng.get_transition_alerts(threshold=0.99)
    assert alerts == []


def test_to_dict_all_fields():
    eng = make_engine()
    t = eng.analyze("bull", INDICATORS_HIGH)
    d = t.to_dict()
    for key in ["current_regime", "previous_regime", "transition_score",
                "early_confidence", "transition_type", "detected_at", "indicators"]:
        assert key in d
