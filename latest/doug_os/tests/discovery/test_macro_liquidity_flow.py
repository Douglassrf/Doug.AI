import pytest
from datetime import datetime, timezone
from doug_os.discovery.macro_liquidity_flow import (
    LiquidityData, LiquidityScore, MacroLiquidityFlowEngine
)


def make_data(global_liquidity=50.0, central_bank=25.0, market_cap=500.0,
              volume=50.0, stablecoin=25.0, reserves=50.0):
    return LiquidityData(
        timestamp=datetime.now(timezone.utc),
        global_liquidity=global_liquidity,
        central_bank_balance=central_bank,
        market_cap=market_cap,
        volume_24h=volume,
        stablecoin_supply=stablecoin,
        exchange_reserves=reserves,
    )


def test_update_returns_liquidity_score_with_score_between_0_and_1():
    engine = MacroLiquidityFlowEngine()
    data = make_data()
    result = engine.update(data)
    assert isinstance(result, LiquidityScore)
    assert 0.0 <= result.score <= 1.0


def test_alert_level_red_when_score_low():
    engine = MacroLiquidityFlowEngine()
    # Zero values → all components default low → score < 0.3
    data = LiquidityData(
        timestamp=datetime.now(timezone.utc),
        global_liquidity=0.0,
        central_bank_balance=0.0,
        market_cap=0.0,
        volume_24h=0.0,
        stablecoin_supply=0.0,
        exchange_reserves=0.0,
    )
    result = engine.update(data)
    assert result.alert_level == "red"


def test_alert_level_green_when_score_high_and_low_pressure():
    engine = MacroLiquidityFlowEngine()
    # High values → score >= 0.5; market_cap large, volume small, stablecoin small → low pressure
    data = make_data(global_liquidity=100.0, central_bank=50.0, market_cap=2000.0,
                     volume=50.0, stablecoin=25.0, reserves=100.0)
    result = engine.update(data)
    assert result.score >= 0.5
    assert result.alert_level == "green"


def test_detect_cycle_expansion_with_rising_data():
    engine = MacroLiquidityFlowEngine()
    # Feed 10 data points where recent values are much higher than earlier
    for i in range(10):
        # First 5: low, last 5: high (ma_short >> ma_long)
        val = 10.0 if i < 5 else 100.0
        engine.update(make_data(global_liquidity=val))
    assert engine._detect_cycle() == "expansion"


def test_calculate_trend_increasing_with_rising_data():
    engine = MacroLiquidityFlowEngine()
    for i in range(5):
        engine.update(make_data(global_liquidity=float(i * 10 + 10)))
    assert engine._calculate_trend() == "increasing"


def test_get_heatmap_returns_expected_keys():
    engine = MacroLiquidityFlowEngine()
    engine.update(make_data())
    heatmap = engine.get_heatmap()
    assert "global_liquidity" in heatmap
    assert "trend" in heatmap
    assert "pressure" in heatmap


def test_liquidity_score_to_dict_serializes_correctly():
    engine = MacroLiquidityFlowEngine()
    result = engine.update(make_data())
    d = result.to_dict()
    assert "score" in d
    assert "pressure_index" in d
    assert "cycle_phase" in d
    assert "trend" in d
    assert "alert_level" in d
    assert "components" in d
    assert "created_at" in d
    assert isinstance(d["score"], float)
    assert isinstance(d["components"], dict)
