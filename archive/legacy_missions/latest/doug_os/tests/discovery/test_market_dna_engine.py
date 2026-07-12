import pytest
from doug_os.discovery.market_dna_engine import MarketDNAEngine, MarketDNA, DNADriftResult


@pytest.fixture
def engine():
    return MarketDNAEngine()


FULL_DATA = {
    "momentum": 0.7, "mean_reversion": 0.3, "trend_following": 0.6, "volatility_clustering": 0.5,
    "historical_vol": 0.4, "implied_vol": 0.45, "volatility_skew": 0.1, "volatility_term": 0.05,
    "spread": 0.02, "depth": 0.8, "volume": 0.9, "turnover": 0.7,
    "institutional_presence": 0.6, "flow_pattern": 0.5, "execution_style": 0.6, "positioning": 0.5,
    "price_reaction": 0.7, "volume_reaction": 0.8, "speed_of_absorption": 0.6, "sentiment_dependency": 0.5,
    "rate_sensitivity": 0.4, "inflation_sensitivity": 0.3, "growth_sensitivity": 0.5, "liquidity_sensitivity": 0.6,
    "whale_presence": 0.4, "concentration": 0.5, "distribution_pattern": 0.6, "accumulation_behavior": 0.7,
    "cycle_amplitude": 0.5, "cycle_frequency": 0.4, "cycle_phase": 0.6, "cycle_stability": 0.8,
}


def test_build_dna_returns_market_dna(engine):
    dna = engine.build_dna("BTC", FULL_DATA)
    assert isinstance(dna, MarketDNA)
    assert dna.asset == "BTC"


def test_build_dna_confidence_high_with_full_data(engine):
    dna = engine.build_dna("BTC", FULL_DATA)
    assert dna.confidence > 0.9


def test_build_dna_confidence_lower_with_sparse_data(engine):
    dna = engine.build_dna("ETH", {"momentum": 0.5})
    assert dna.confidence < 0.8


def test_build_dna_extracts_all_components(engine):
    dna = engine.build_dna("BTC", FULL_DATA)
    assert len(dna.behavioral_signature) > 0
    assert len(dna.volatility_dna) > 0
    assert len(dna.liquidity_dna) > 0
    assert len(dna.whale_dna) > 0


def test_get_dna_returns_stored(engine):
    engine.build_dna("BTC", FULL_DATA)
    dna = engine.get_dna("BTC")
    assert dna is not None
    assert dna.asset == "BTC"


def test_get_dna_missing_returns_none(engine):
    assert engine.get_dna("UNKNOWN") is None


def test_detect_drift_no_baseline(engine):
    result = engine.detect_drift("BTC", FULL_DATA)
    assert result.alert_level == "green"
    assert "No baseline" in result.recommendation


def test_detect_drift_stable(engine):
    engine.build_dna("BTC", FULL_DATA)
    result = engine.detect_drift("BTC", FULL_DATA)
    assert result.alert_level == "green"
    assert result.drift_score < 0.3


def test_detect_drift_significant_change(engine):
    engine.build_dna("BTC", FULL_DATA)
    changed = {k: v * 5 for k, v in FULL_DATA.items()}
    result = engine.detect_drift("BTC", changed)
    assert result.drift_score > 0.0


def test_get_drift_history(engine):
    engine.build_dna("BTC", FULL_DATA)
    engine.detect_drift("BTC", FULL_DATA)
    engine.detect_drift("BTC", FULL_DATA)
    history = engine.get_drift_history("BTC")
    assert len(history) == 2


def test_to_dict_serializes(engine):
    dna = engine.build_dna("BTC", FULL_DATA)
    d = dna.to_dict()
    assert all(k in d for k in ("id", "asset", "behavioral_signature", "confidence",
                                 "created_at", "updated_at"))
