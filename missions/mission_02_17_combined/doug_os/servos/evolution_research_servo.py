from doug_os.core.intent_vector import IntentVector

class EvolutionResearchServo:
    name = "evolution_research"
    async def analyze(self, market_event: dict) -> IntentVector:
        historical_edge = float(market_event.get("historical_edge", 55))
        direction = "BUY" if historical_edge >= 55 else "HOLD"
        return IntentVector(
            cycle_id=market_event.get("cycle_id",""),
            servo="evolution_research",
            symbol=market_event.get("symbol","BTCUSDT"),
            direction=direction,
            confidence=historical_edge,
            risk=35,
            evidence_strength=55,
            manipulation_risk=20,
            entropy_score=35,
            reality_score=78,
            opportunity_score=historical_edge,
            reasons=("experience_probability_mock", "strategy_decay_checked"),
        )
