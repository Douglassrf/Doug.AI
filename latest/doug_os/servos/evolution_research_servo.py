from doug_os.core.intent_vector import IntentVector
from doug_os.config import SERVO_THRESHOLDS, DEFAULT_SYMBOL

class EvolutionResearchServo:
    name = "evolution_research"
    async def analyze(self, market_event: dict) -> IntentVector:
        # Retrieve the configured minimum edge for this servo or fall back to 55.0.
        cfg = SERVO_THRESHOLDS.get(self.name, {})
        min_edge = float(cfg.get("min_historical_edge", 55.0))
        # Use event value when present, otherwise use the configured threshold as default.
        historical_edge = float(market_event.get("historical_edge", min_edge))
        direction = "BUY" if historical_edge >= min_edge else "HOLD"
        return IntentVector(
            cycle_id=market_event.get("cycle_id", ""),
            servo=self.name,
            symbol=market_event.get("symbol", DEFAULT_SYMBOL),
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
