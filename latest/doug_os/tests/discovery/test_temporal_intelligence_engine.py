import pytest
from datetime import datetime, timezone
from doug_os.discovery.temporal_intelligence_engine import (
    TemporalIntelligenceEngine, TemporalData, TimeHorizon, TemporalIntelligence
)


def make_data(value=1.0, horizon=TimeHorizon.SHORT, confidence=0.8):
    return TemporalData(timestamp=datetime.now(timezone.utc), value=value, horizon=horizon, confidence=confidence)


def test_analyze_short_term_populated():
    eng = TemporalIntelligenceEngine()
    result = eng.analyze(make_data(5.0, TimeHorizon.SHORT))
    st = result.short_term
    assert "mean" in st
    assert "std" in st
    assert "trend" in st
    assert st["mean"] == pytest.approx(5.0)


def test_horizon_without_data_no_data():
    eng = TemporalIntelligenceEngine()
    eng.analyze(make_data(1.0, TimeHorizon.SHORT))
    result = eng.analyze(make_data(2.0, TimeHorizon.SHORT))
    assert result.medium_term == {"status": "no_data"}


def test_trend_increasing():
    eng = TemporalIntelligenceEngine()
    for i in range(5):
        eng.analyze(make_data(float(i * 10), TimeHorizon.SHORT))
    result = eng.analyze(make_data(50.0, TimeHorizon.SHORT))
    assert result.short_term["trend"] == "increasing"


def test_trend_decreasing():
    eng = TemporalIntelligenceEngine()
    for i in range(5):
        eng.analyze(make_data(float(50 - i * 10), TimeHorizon.SHORT))
    result = eng.analyze(make_data(0.0, TimeHorizon.SHORT))
    assert result.short_term["trend"] == "decreasing"


def test_trend_stable_few_values():
    eng = TemporalIntelligenceEngine()
    # with < 3 values trend is "stable"
    result = eng.analyze(make_data(1.0, TimeHorizon.MEDIUM))
    assert result.medium_term["trend"] == "stable"


def test_persistence_with_10_plus_data():
    eng = TemporalIntelligenceEngine()
    for i in range(12):
        eng.analyze(make_data(float(i), TimeHorizon.SHORT))
    result = eng.analyze(make_data(12.0, TimeHorizon.SHORT))
    assert 0.0 <= result.persistence_score <= 1.0


def test_persistence_less_than_10_is_zero():
    eng = TemporalIntelligenceEngine()
    for i in range(5):
        eng.analyze(make_data(float(i), TimeHorizon.SHORT))
    result = eng.analyze(make_data(5.0, TimeHorizon.SHORT))
    assert result.persistence_score == 0.0


def test_detect_cycle_with_20_plus_data():
    eng = TemporalIntelligenceEngine()
    for i in range(22):
        eng.analyze(make_data(float(i % 5), TimeHorizon.SHORT))
    result = eng.analyze(make_data(0.0, TimeHorizon.SHORT))
    assert result.cycle_detected is not None
    assert isinstance(result.cycle_detected, str)


def test_detect_cycle_none_with_few_data():
    eng = TemporalIntelligenceEngine()
    for i in range(5):
        eng.analyze(make_data(float(i), TimeHorizon.SHORT))
    result = eng.analyze(make_data(5.0, TimeHorizon.SHORT))
    assert result.cycle_detected is None


def test_change_score_positive_when_differs():
    eng = TemporalIntelligenceEngine()
    # older group: values around 0
    for _ in range(5):
        eng.analyze(make_data(0.0, TimeHorizon.SHORT))
    # recent group: values around 100
    for _ in range(5):
        eng.analyze(make_data(100.0, TimeHorizon.SHORT))
    result = eng.analyze(make_data(100.0, TimeHorizon.SHORT))
    assert result.change_score > 0.0


def test_to_dict_all_fields():
    eng = TemporalIntelligenceEngine()
    result = eng.analyze(make_data(1.0))
    d = result.to_dict()
    for key in ["short_term", "medium_term", "long_term", "very_long_term",
                "persistence_score", "cycle_detected", "change_score", "created_at"]:
        assert key in d
