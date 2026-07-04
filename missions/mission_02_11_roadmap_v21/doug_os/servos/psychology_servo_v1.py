from doug_os.core.intent_vector import IntentVector

class NewsPsychologyServoV1:
    name = "news_psychology"

    async def analyze(self, market_event: dict) -> IntentVector:
        sentiment = float(market_event.get("sentiment_score", 60))
        panic = float(market_event.get("panic_score", 25))
        greed = float(market_event.get("greed_score", 55))
        cognitive_entropy = float(market_event.get("cognitive_entropy", 35))
        narrative = float(market_event.get("narrative_strength", 60))

        risk = max(panic, greed - 20 if greed > 80 else 30)
        direction = "BUY" if sentiment >= 62 and panic < 50 and cognitive_entropy < 65 else "HOLD"

        return IntentVector(
            cycle_id=market_event.get("cycle_id", ""),
            servo="news_psychology",
            symbol=market_event.get("symbol", "BTCUSDT"),
            direction=direction,
            confidence=sentiment,
            risk=risk,
            evidence_strength=narrative,
            manipulation_risk=float(market_event.get("narrative_manipulation_score", 20)),
            entropy_score=cognitive_entropy,
            reality_score=70,
            opportunity_score=(sentiment + narrative) / 2,
            reasons=("sentiment", "panic", "greed", "narrative_strength"),
        )
