"""Tests for servo hardening and configuration use.

These tests ensure that servos do not emit empty warning strings and
that they respect the centralized configuration for thresholds and
default symbols.
"""

import asyncio

import pytest

from doug_os.config import DEFAULT_SYMBOL, SERVO_THRESHOLDS
from doug_os.servos.evolution_research_servo import EvolutionResearchServo
from doug_os.servos.news_psychology_servo import NewsPsychologyServo
from doug_os.servos.onchain_servo import OnChainIntelligenceServo
from doug_os.servos.risk_empire_servo import RiskEmpireServo


def run_async(coro):
    """Helper to run an asynchronous coroutine in a synchronous context."""
    return asyncio.get_event_loop().run_until_complete(coro)


def test_risk_empire_no_warning_when_not_bunker():
    servo = RiskEmpireServo()
    # Event with moderate metrics should not trigger bunker_mode or any warnings
    market_event = {
        "manipulation_risk": 10,
        "risk": 30,
        "reality_score": 80,
        "drawdown": 0.01,
        "daily_loss": 0.0,
        "entropy": 30,
    }
    vector = run_async(servo.analyze(market_event))
    assert vector.warnings == (), "RiskEmpireServo should not include empty warning strings"


def test_onchain_warning_threshold():
    servo = OnChainIntelligenceServo()
    cfg = SERVO_THRESHOLDS.get("onchain", {})
    warning_threshold = float(cfg.get("max_dump_risk_warning", 65.0))
    # Create event with dump_risk above threshold to trigger warning
    # dump_risk = inflow*0.5 + (100 - whale)*0.3
    market_event = {
        "exchange_inflow_score": 200,  # high inflow
        "exchange_outflow_score": 0,
        "whale_accumulation_score": 10,  # low whale => high dump risk
    }
    vector = run_async(servo.analyze(market_event))
    assert vector.warnings == ("dump_risk",), "OnChain servo should warn when dump_risk exceeds threshold"
    # Event below threshold should yield no warnings
    market_event_low = {
        "exchange_inflow_score": 5,
        "exchange_outflow_score": 10,
        "whale_accumulation_score": 80,
    }
    vector_low = run_async(servo.analyze(market_event_low))
    assert vector_low.warnings == (), "OnChain servo should not warn when dump_risk is below threshold"


def test_default_symbol_usage():
    # If no symbol is provided, servos should use DEFAULT_SYMBOL
    for servo_cls in [EvolutionResearchServo, NewsPsychologyServo, OnChainIntelligenceServo, RiskEmpireServo]:
        servo = servo_cls()
        vector = run_async(servo.analyze({}))
        assert vector.symbol == DEFAULT_SYMBOL, f"{servo_cls.__name__} should default symbol to {DEFAULT_SYMBOL}"


def test_evolution_research_threshold_configurable():
    servo = EvolutionResearchServo()
    cfg = SERVO_THRESHOLDS.get("evolution_research", {})
    min_edge = float(cfg.get("min_historical_edge", 55.0))
    # Event with edge just below threshold should result in HOLD
    event_hold = {"historical_edge": min_edge - 1}
    vector_hold = run_async(servo.analyze(event_hold))
    assert vector_hold.direction == "HOLD"
    # Event with edge equal or above threshold should result in BUY
    event_buy = {"historical_edge": min_edge}
    vector_buy = run_async(servo.analyze(event_buy))
    assert vector_buy.direction == "BUY"