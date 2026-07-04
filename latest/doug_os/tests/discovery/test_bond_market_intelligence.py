import pytest
from datetime import datetime, timezone
from doug_os.discovery.bond_market_intelligence import BondData, BondIntelligence, BondMarketIntelligence


def make_data(**kwargs):
    defaults = dict(
        timestamp=datetime.now(timezone.utc),
        yield_2y=2.0, yield_5y=2.5, yield_10y=3.0, yield_30y=3.5,
        credit_spread=0.5, corporate_yield=3.5, duration=5.0, volume=500.0,
    )
    defaults.update(kwargs)
    return BondData(**defaults)


def test_inverted_curve_status_and_inversion_score():
    engine = BondMarketIntelligence()
    data = make_data(yield_2y=4.0, yield_10y=3.5, yield_30y=3.8)
    result = engine.analyze(data)
    assert result.curve_status == "inverted"
    assert result.inversion_score > 0


def test_normal_curve_no_inversion():
    engine = BondMarketIntelligence()
    data = make_data(yield_2y=2.0, yield_10y=3.5, yield_30y=4.0)
    result = engine.analyze(data)
    assert result.curve_status == "normal"
    assert result.inversion_score == 0.0


def test_flat_curve_status():
    engine = BondMarketIntelligence()
    # spread_2_10 must be positive but < 0.25
    data = make_data(yield_2y=3.0, yield_10y=3.1, yield_30y=3.5)
    result = engine.analyze(data)
    assert result.curve_status == "flat"


def test_high_credit_spread_gives_high_credit_pressure():
    engine = BondMarketIntelligence()
    data = make_data(credit_spread=1.8)
    result = engine.analyze(data)
    assert result.credit_pressure >= 0.8


def test_high_duration_gives_high_duration_risk():
    engine = BondMarketIntelligence()
    data = make_data(duration=9.0)
    result = engine.analyze(data)
    assert result.duration_risk >= 0.8


def test_recession_probability_positive_when_inverted():
    engine = BondMarketIntelligence()
    data = make_data(yield_2y=4.5, yield_10y=3.5, yield_30y=3.8)
    result = engine.analyze(data)
    assert result.recession_probability > 0


def test_to_dict_serializes_all_fields():
    engine = BondMarketIntelligence()
    data = make_data()
    result = engine.analyze(data)
    d = result.to_dict()
    expected_keys = {
        "curve_status", "inversion_score", "credit_pressure",
        "duration_risk", "liquidity_score", "recession_probability", "created_at",
    }
    assert expected_keys == set(d.keys())
    assert isinstance(d["curve_status"], str)
    assert isinstance(d["inversion_score"], float)
    assert isinstance(d["created_at"], str)
