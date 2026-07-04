import pytest
from datetime import datetime, timezone
from doug_os.discovery.predictive_macro_engine import MacroData, MacroPrediction, PredictiveMacroEngine


def make_data(**kwargs):
    defaults = dict(
        timestamp=datetime.now(timezone.utc),
        gdp_growth=2.0, inflation=2.5, unemployment=4.5,
        interest_rate=2.0, pmi_manufacturing=52.0, pmi_services=53.0,
        consumer_confidence=80.0,
    )
    defaults.update(kwargs)
    return MacroData(**defaults)


def test_expansion_regime():
    engine = PredictiveMacroEngine()
    data = make_data(gdp_growth=3.0, inflation=2.0)
    result = engine.predict(data)
    assert result.predicted_regime == "expansion"


def test_recession_regime():
    engine = PredictiveMacroEngine()
    data = make_data(gdp_growth=-1.0)
    result = engine.predict(data)
    assert result.predicted_regime == "recession"


def test_inflationary_regime():
    engine = PredictiveMacroEngine()
    data = make_data(gdp_growth=1.0, inflation=5.0)
    result = engine.predict(data)
    assert result.predicted_regime == "inflationary"


def test_forecast_rates_increases_when_inflation_above_rate():
    engine = PredictiveMacroEngine()
    data = make_data(interest_rate=2.0, inflation=4.0, gdp_growth=1.0)
    result = engine.predict(data)
    assert result.rate_forecast > data.interest_rate


def test_forecast_gdp_uses_mean_of_last_three():
    engine = PredictiveMacroEngine()
    for gdp in [1.0, 2.0, 3.0]:
        engine.predict(make_data(gdp_growth=gdp))
    # Now history has 3, so 4th call uses mean
    data = make_data(gdp_growth=4.0, pmi_manufacturing=50.0, pmi_services=50.0)
    result = engine.predict(data)
    # mean of [1,2,3,4] last 3 = mean([2,3,4]) = 3.0, pmi_avg=50 so no bonus
    assert abs(result.gdp_forecast - 3.0) < 0.01


def test_confidence_index_positive_with_high_consumer_confidence():
    engine = PredictiveMacroEngine()
    data = make_data(consumer_confidence=90.0)
    result = engine.predict(data)
    assert result.confidence_index > 0


def test_to_dict_serializes_all_fields():
    engine = PredictiveMacroEngine()
    data = make_data()
    result = engine.predict(data)
    d = result.to_dict()
    expected_keys = {
        "gdp_forecast", "inflation_forecast", "rate_forecast",
        "confidence_index", "regime_transition_score", "predicted_regime", "created_at",
    }
    assert expected_keys == set(d.keys())
    assert isinstance(d["predicted_regime"], str)
    assert isinstance(d["created_at"], str)
