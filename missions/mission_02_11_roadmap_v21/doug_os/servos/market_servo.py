from doug_os.core.intent_vector import IntentVector
from doug_os.engines.integrity_engine import MarketIntegrityCore

class MarketServo:
    name = "market"

    async def analyze(self, market_event: dict) -> IntentVector:
        integrity = MarketIntegrityCore().evaluate(market_event)
        direction = "BUY" if integrity["approved"] else "HOLD"
        return IntentVector(
            cycle_id=market_event.get("cycle_id", ""),
            servo="market",
            symbol=market_event.get("symbol", "BTCUSDT"),
            direction=direction,
            confidence=76 if integrity["approved"] else 35,
            risk=38 if integrity["approved"] else 75,
            evidence_strength=72,
            manipulation_risk=float(market_event.get("manipulation_risk", 20)),
            entropy_score=integrity["entropy_score"],
            reality_score=integrity["reality_score"],
            opportunity_score=74 if integrity["approved"] else 25,
            reasons=("market_integrity", integrity["reason"]),
        )
