from doug_os.core.intent_vector import IntentVector
from doug_os.engines.market_integrity_survival import MarketIntegritySurvivalCore
from doug_os.config import DEFAULT_SYMBOL

class MarketIntelligenceServo:
    name = "market"
    async def analyze(self, market_event: dict) -> IntentVector:
            integrity = MarketIntegritySurvivalCore().evaluate(market_event)
            direction = "BUY" if integrity["tradeable"] else "HOLD"
            return IntentVector(
                cycle_id=market_event.get("cycle_id", ""),
                servo=self.name,
                symbol=market_event.get("symbol", DEFAULT_SYMBOL),
                direction=direction,
                confidence=78 if integrity["tradeable"] else 40,
                risk=40 if integrity["tradeable"] else 75,
                evidence_strength=72,
                manipulation_risk=float(market_event.get("manipulation_risk", 20)),
                entropy_score=integrity["entropy_score"],
                reality_score=float(market_event.get("reality_score", 80)),
                opportunity_score=76 if integrity["tradeable"] else 25,
                reasons=("market_integrity", integrity["reason"]),
            )
