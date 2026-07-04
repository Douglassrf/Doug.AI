import pytest
from datetime import datetime, timezone
from doug_os.discovery.stablecoin_rotation import (
    StablecoinFlow, StablecoinAnalysis, StablecoinMacroRotation
)


def make_flow(usdt=60.0, usdc=40.0, exchange=20.0, net_flow=0.0, rotation=0.0):
    return StablecoinFlow(
        timestamp=datetime.now(timezone.utc),
        usdt_supply=usdt,
        usdc_supply=usdc,
        exchange_balance=exchange,
        net_flow=net_flow,
        rotation_index=rotation,
    )


def test_update_returns_stablecoin_analysis():
    engine = StablecoinMacroRotation()
    result = engine.update(make_flow())
    assert isinstance(result, StablecoinAnalysis)


def test_usdt_share_plus_usdc_share_approximately_1():
    engine = StablecoinMacroRotation()
    result = engine.update(make_flow(usdt=60.0, usdc=40.0))
    assert result.usdt_share + result.usdc_share == pytest.approx(1.0, abs=1e-9)


def test_pressure_index_between_minus_1_and_1():
    engine = StablecoinMacroRotation()
    # Large net flow to test clamping
    result = engine.update(make_flow(usdt=50.0, usdc=50.0, net_flow=1000.0))
    assert -1.0 <= result.pressure_index <= 1.0


def test_alert_red_when_pressure_above_0_8():
    engine = StablecoinMacroRotation()
    # net_flow = 10.0, total = 10.0 → pressure = 10/10*10 = 10 → clamped to 1.0 > 0.8
    result = engine.update(make_flow(usdt=5.0, usdc=5.0, net_flow=10.0))
    assert result.alert == "red"


def test_trend_increasing_with_positive_net_flows():
    engine = StablecoinMacroRotation()
    for _ in range(5):
        engine.update(make_flow(usdt=50.0, usdc=50.0, net_flow=5.0))
    result = engine.update(make_flow(usdt=50.0, usdc=50.0, net_flow=5.0))
    assert result.trend == "increasing"


def test_to_dict_serializes_correctly():
    engine = StablecoinMacroRotation()
    result = engine.update(make_flow())
    d = result.to_dict()
    for key in ["total_supply", "usdt_share", "usdc_share", "exchange_ratio",
                "pressure_index", "trend", "alert", "created_at"]:
        assert key in d
    assert isinstance(d["created_at"], str)
