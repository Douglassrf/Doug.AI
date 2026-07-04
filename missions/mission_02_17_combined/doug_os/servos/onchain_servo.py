from doug_os.core.intent_vector import IntentVector

class OnChainIntelligenceServo:
    name = "onchain"
    async def analyze(self, market_event: dict) -> IntentVector:
        exchange_inflow = float(market_event.get("exchange_inflow_score", 25))
        exchange_outflow = float(market_event.get("exchange_outflow_score", 55))
        whale = float(market_event.get("whale_accumulation_score", 50))
        dump_risk = exchange_inflow * 0.5 + (100 - whale) * 0.3
        direction = "BUY" if exchange_outflow > exchange_inflow and whale >= 50 else "HOLD"
        return IntentVector(
            cycle_id=market_event.get("cycle_id",""),
            servo="onchain",
            symbol=market_event.get("symbol","BTCUSDT"),
            direction=direction,
            confidence=max(45, min(85, whale)),
            risk=min(100, dump_risk),
            evidence_strength=65,
            manipulation_risk=float(market_event.get("manipulation_risk",30)),
            entropy_score=35,
            reality_score=78,
            opportunity_score=65 if direction == "BUY" else 40,
            reasons=("stablecoin_flow", "whale_movement", "exchange_flow"),
            warnings=("dump_risk" if dump_risk > 65 else "",),
        )
