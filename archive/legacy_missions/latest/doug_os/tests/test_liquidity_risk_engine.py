"""Tests for Liquidity Risk Engine (Missão 32)."""

from doug_os.engines import LiquidityRiskEngine


def test_liquidity_risk_collapse() -> None:
    engine = LiquidityRiskEngine(ideal_depth=1.0, ideal_volume=1.0)
    event = {"order_book_depth": 0.05, "daily_volume": 0.1}
    result = engine.evaluate(event)
    assert result["category"] == "collapse"
    assert result["liquidity_risk"] >= 0.8
    assert result["confidence_adjustment"] <= 0.2


def test_liquidity_risk_stress() -> None:
    engine = LiquidityRiskEngine()
    event = {"order_book_depth": 0.4, "daily_volume": 0.5}
    result = engine.evaluate(event)
    # risk around 0.6 → stress
    assert result["category"] == "stress"
    assert 0.5 <= result["liquidity_risk"] < 0.8


def test_liquidity_risk_vacuum() -> None:
    engine = LiquidityRiskEngine()
    event = {"order_book_depth": 0.7, "daily_volume": 0.6}
    result = engine.evaluate(event)
    # risk around 0.4 → vacuum
    assert result["category"] == "vacuum"
    assert 0.3 <= result["liquidity_risk"] < 0.5


def test_liquidity_risk_normal() -> None:
    engine = LiquidityRiskEngine()
    event = {"order_book_depth": 0.9, "daily_volume": 0.9}
    result = engine.evaluate(event)
    assert result["category"] == "normal"
    assert result["liquidity_risk"] < 0.3
    assert result["confidence_adjustment"] >= 0.7