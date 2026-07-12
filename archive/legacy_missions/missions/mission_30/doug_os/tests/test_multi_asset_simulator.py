import pytest

from doug_os.execution.multi_asset_simulator import MultiAssetSimulator


def test_multi_asset_simulator_tick_changes_prices():
    """After a tick, prices should change within the volatility bounds."""
    initial = {
        "EURUSD": 1.2,
        "XAUUSD": 1800.0,  # gold
        "XAGUSD": 25.0,   # silver
        "BTCUSD": 50_000.0,
        "ETHUSD": 3_000.0,
        "SOLUSD": 100.0,
    }
    volatility = 0.05  # 5% max change per tick
    sim = MultiAssetSimulator(initial, volatility=volatility, seed=123)
    before = {s: sim.get_price(s) for s in sim.get_available_symbols()}
    sim.tick()
    after = {s: sim.get_price(s) for s in sim.get_available_symbols()}
    for symbol in initial:
        old_price = before[symbol]
        new_price = after[symbol]
        assert new_price != pytest.approx(old_price)
        # price should be within ±volatility of the old price
        assert old_price * (1 - volatility) <= new_price <= old_price * (1 + volatility)


def test_multi_asset_simulator_unknown_symbol():
    sim = MultiAssetSimulator({"EURUSD": 1.1})
    with pytest.raises(KeyError):
        sim.get_price("ABCXYZ")