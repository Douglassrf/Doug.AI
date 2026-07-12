import asyncio

from doug_os.core.intent_vector import IntentVector
from doug_os.brain.unified_intelligence_layer import UnifiedIntelligenceLayer


class BuyServo:
    name = "market"
    async def analyze(self, market_event):
        return IntentVector(
            servo="market",
            symbol="BTCUSDT",
            direction="BUY",
            confidence=60,
            risk=30,
            evidence_strength=60,
            manipulation_risk=10,
            entropy_score=20,
            reality_score=50,
            opportunity_score=60,
            reasons=("buy_signal",),
        )


class SellServo:
    name = "onchain"
    async def analyze(self, market_event):
        return IntentVector(
            servo="onchain",
            symbol="BTCUSDT",
            direction="SELL",
            confidence=60,
            risk=30,
            evidence_strength=60,
            manipulation_risk=10,
            entropy_score=20,
            reality_score=50,
            opportunity_score=60,
            reasons=("sell_signal",),
        )


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_unified_layer_detects_conflict():
    layer = UnifiedIntelligenceLayer([BuyServo(), SellServo()])
    result = run(layer.process_event({"cycle_id": "test"}))
    supervisor = result["supervisor"]
    # The supervisor should detect conflicting directions between buy and sell
    assert any("directions_conflict" in inc for inc in supervisor["inconsistencies"])
    # The council decision should be a HOLD due to low consensus (risk and weights equal)
    assert result["decision"]["decision"] in ("HOLD", "BLOCK")