from doug_os.core.intent_vector import IntentVector

class OnChainIntelligenceServoV1:
    name = "onchain"

    async def analyze(self, market_event: dict) -> IntentVector:
        exchange_inflow = float(market_event.get("exchange_inflow_score", 20))
        exchange_outflow = float(market_event.get("exchange_outflow_score", 60))
        whale = float(market_event.get("whale_accumulation_score", 55))
        stablecoin = float(market_event.get("stablecoin_flow_score", 55))
        mempool = float(market_event.get("mempool_pressure_score", 35))
        wallet = float(market_event.get("large_wallet_intent_score", 55))

        dump_risk = min(100, exchange_inflow * 0.45 + (100 - whale) * 0.25 + mempool * 0.20)
        opportunity = round((exchange_outflow + whale + stablecoin + wallet) / 4, 2)

        direction = "BUY" if opportunity >= 60 and dump_risk < 60 else "HOLD"

        return IntentVector(
            cycle_id=market_event.get("cycle_id", ""),
            servo="onchain",
            symbol=market_event.get("symbol", "BTCUSDT"),
            direction=direction,
            confidence=opportunity,
            risk=dump_risk,
            evidence_strength=68,
            manipulation_risk=float(market_event.get("manipulation_risk", 25)),
            entropy_score=35,
            reality_score=78,
            opportunity_score=opportunity,
            reasons=("whale_mirror", "stablecoin_flow", "exchange_flow", "wallet_radar"),
        )
