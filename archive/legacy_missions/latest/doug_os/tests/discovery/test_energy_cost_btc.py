import pytest
from datetime import datetime, timezone
from doug_os.discovery.energy_cost_btc import (
    MiningMetrics, EnergyCostResult, EnergyCostModelBTC
)


def make_metrics(hash_rate=100.0, difficulty=1e13, block_time=600.0,
                 electricity_cost=0.05, miner_revenue=300000.0):
    return MiningMetrics(
        timestamp=datetime.now(timezone.utc),
        hash_rate=hash_rate,
        difficulty=difficulty,
        block_time=block_time,
        electricity_cost=electricity_cost,
        miner_revenue=miner_revenue,
    )


def test_analyze_returns_energy_cost_result():
    engine = EnergyCostModelBTC()
    result = engine.analyze(make_metrics(), market_price=50000.0)
    assert isinstance(result, EnergyCostResult)


def test_hash_rate_zero_gives_production_cost_zero():
    engine = EnergyCostModelBTC()
    result = engine.analyze(make_metrics(hash_rate=0.0), market_price=50000.0)
    assert result.production_cost == 0.0


def test_electricity_cost_zero_gives_production_cost_zero():
    engine = EnergyCostModelBTC()
    result = engine.analyze(make_metrics(electricity_cost=0.0), market_price=50000.0)
    assert result.production_cost == 0.0


def test_market_price_above_production_cost_gives_zero_capitulation():
    engine = EnergyCostModelBTC()
    # hash_rate=1, electricity=0.0001, difficulty=4 → production_cost ≈ 51540
    # market_price=100000 > production_cost → profit_margin > 0 → capitulation = 0
    result = engine.analyze(make_metrics(hash_rate=1.0, electricity_cost=0.0001,
                                          difficulty=4.0), market_price=100000.0)
    assert result.miner_capitulation_index == 0.0


def test_market_price_below_production_cost_gives_positive_capitulation():
    engine = EnergyCostModelBTC()
    # Force production cost to be large: high hash_rate + high electricity + low difficulty
    metrics = make_metrics(hash_rate=1000.0, electricity_cost=1.0, difficulty=1.0)
    result = engine.analyze(metrics, market_price=0.01)
    assert result.miner_capitulation_index > 0.0


def test_hash_rate_trend_increasing_with_5_rising_entries():
    engine = EnergyCostModelBTC()
    for i in range(5):
        engine.analyze(make_metrics(hash_rate=100.0 + i * 50.0), market_price=50000.0)
    # After 5 entries with last=300, first=100 → slope = (300-100)/100 = 2.0 > 0.1
    result = engine.analyze(make_metrics(hash_rate=350.0), market_price=50000.0)
    assert result.hash_rate_trend == "increasing"


def test_difficulty_phase_increasing_with_3_rising_entries():
    engine = EnergyCostModelBTC()
    engine.analyze(make_metrics(difficulty=1e13), market_price=50000.0)
    engine.analyze(make_metrics(difficulty=1.1e13), market_price=50000.0)
    result = engine.analyze(make_metrics(difficulty=1.21e13), market_price=50000.0)
    assert result.difficulty_phase == "increasing"


def test_to_dict_serializes_correctly():
    engine = EnergyCostModelBTC()
    result = engine.analyze(make_metrics(), market_price=50000.0)
    d = result.to_dict()
    for key in ["production_cost", "market_price", "cost_gap",
                "miner_capitulation_index", "hash_rate_trend", "difficulty_phase", "created_at"]:
        assert key in d
    assert isinstance(d["created_at"], str)
