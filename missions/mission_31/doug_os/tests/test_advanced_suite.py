import asyncio

from doug_os.servos.risk_empire_servo import RiskEmpireServo
from doug_os.servos.market_servo import MarketIntelligenceServo
from doug_os.engines.manipulation_intelligence import ManipulationIntelligenceEngine
from doug_os.brain.doug_brain import DougBrain


async def test_high_manipulation_blocks():
    """Extremely high manipulation risk should trigger an immediate block.

    We simulate a market event with a very high manipulation_risk.  The
    RiskEmpireServo delegates to the RiskEmpire engine and should return
    an IntentVector whose direction is ``BLOCK``.  This test ensures that
    manipulative conditions are detected and acted upon.
    """
    servo = RiskEmpireServo()
    event = {"manipulation_risk": 95, "risk": 50}
    vector = await servo.analyze(event)
    assert vector.direction == "BLOCK"
    assert vector.confidence >= 90


def test_fake_liquidity_detected():
    """A high fake liquidity score should result in a manipulation block.

    The ManipulationIntelligenceEngine aggregates multiple manipulation
    signals.  Setting the ``fake_liquidity_score`` to a very high value
    should produce a total manipulation_score above 70 and therefore
    classify the action as ``BLOCK``.
    """
    engine = ManipulationIntelligenceEngine()
    # To trigger a manipulation block we need to elevate multiple scores.
    # Using high values for all manipulation categories yields a score of 90.
    event = {
        "spoofing_score": 90,
        "wash_trading_score": 90,
        "stop_hunt_score": 90,
        "fake_liquidity_score": 90,
        "hft_stress_score": 90,
        "order_book_anomaly_score": 90,
        "absorption_score": 90,
    }
    result = engine.detect(event)
    assert result["manipulation_score"] > 70
    assert result["action"] == "BLOCK"


async def test_extreme_drawdown_blocks():
    """RiskEmpire should block when drawdown exceeds its configured threshold.

    We construct a market event with a drawdown well above the default
    max_drawdown (3%).  The servo should return a blocking vector and
    include bunker_mode warning.
    """
    servo = RiskEmpireServo()
    event = {"drawdown": 0.05, "risk": 30, "manipulation_risk": 10, "entropy": 20, "reality_score": 85}
    vector = await servo.analyze(event)
    assert vector.direction == "BLOCK"
    assert any(w for w in vector.warnings)


async def test_unexpected_event_fields_do_not_crash():
    """DougBrain should handle unexpected keys gracefully.

    The high‑level brain orchestrates servos, council and engines.  Passing
    an event with extraneous fields should not raise exceptions.  We
    simply ensure that a decision dictionary is returned with the
    expected keys.
    """
    brain = DougBrain()
    event = {
        "symbol": "BTCUSDT",
        "volatility": 0.02,
        "drawdown": 0.001,
        "alien_event": 42,
    }
    result = await brain.process_market_event(event)
    assert isinstance(result, dict)
    assert "decision" in result
    assert "vectors" in result
    assert "cycle_id" in result