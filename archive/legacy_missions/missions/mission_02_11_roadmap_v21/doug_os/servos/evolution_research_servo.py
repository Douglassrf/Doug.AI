from doug_os.core.intent_vector import IntentVector

class EvolutionResearchServo:
    name = "evolution_research"

    async def analyze(self, market_event: dict) -> IntentVector:
        edge = float(market_event.get("historical_edge", 55))
        direction = "BUY" if edge >= 58 else "HOLD"

        return IntentVector(
            cycle_id=market_event.get("cycle_id", ""),
            servo="evolution_research",
            symbol=market_event.get("symbol", "BTCUSDT"),
            direction=direction,
            confidence=edge,
            risk=35,
            evidence_strength=55,
            manipulation_risk=20,
            entropy_score=35,
            reality_score=76,
            opportunity_score=edge,
            reasons=("experience_probability", "strategy_decay_check"),
        )
