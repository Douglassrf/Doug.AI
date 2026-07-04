"""Tests for Market Integrity V2 Engine (Missão 31)."""

from doug_os.engines import MarketIntegrityV2Engine


def test_market_integrity_v2_high_risk() -> None:
    engine = MarketIntegrityV2Engine()
    event = {
        "spoofing_score": 0.8,
        "liquidity_trap_score": 0.9,
        "fake_breakout_score": 0.7,
        "wash_trading_score": 0.85,
    }
    result = engine.detect(event)
    # weighted average of scores should be high (>0.6) → dangerous
    assert result["classification"] == "dangerous"
    assert result["score"] > 60


def test_market_integrity_v2_warning() -> None:
    engine = MarketIntegrityV2Engine()
    event = {
        "spoofing_score": 0.5,
        "liquidity_trap_score": 0.5,
        "fake_breakout_score": 0.4,
        "wash_trading_score": 0.4,
    }
    result = engine.detect(event)
    # average around 0.45 → warning
    assert result["classification"] == "warning"
    assert 40 <= result["score"] <= 60


def test_market_integrity_v2_ok() -> None:
    engine = MarketIntegrityV2Engine()
    event = {
        "spoofing_score": 0.1,
        "liquidity_trap_score": 0.2,
        "fake_breakout_score": 0.1,
        "wash_trading_score": 0.1,
    }
    result = engine.detect(event)
    # average below 0.4 → ok
    assert result["classification"] == "ok"
    assert result["score"] < 40


def test_market_integrity_v2_custom_thresholds_and_weights() -> None:
    # Use custom weights and thresholds to verify customization
    engine = MarketIntegrityV2Engine(
        weights={"spoofing": 0.4, "liquidity_trap": 0.3, "fake_breakout": 0.2, "wash_trading": 0.1},
        threshold_high=0.7,
        threshold_warning=0.3,
    )
    event = {
        "spoofing_score": 0.6,
        "liquidity_trap_score": 0.5,
        "fake_breakout_score": 0.4,
        "wash_trading_score": 0.3,
    }
    result = engine.detect(event)
    # Weighted average: 0.6*0.4 + 0.5*0.3 + 0.4*0.2 + 0.3*0.1 = 0.24+0.15+0.08+0.03 = 0.5
    # With high threshold 0.7 and warning threshold 0.3, should be 'warning'
    assert result["classification"] == "warning"
    assert 30 <= result["score"] < 70