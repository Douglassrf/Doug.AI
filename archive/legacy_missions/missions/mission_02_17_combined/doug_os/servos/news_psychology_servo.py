from doug_os.core.intent_vector import IntentVector

class NewsPsychologyServo:
    name = "news_psychology"
    async def analyze(self, market_event: dict) -> IntentVector:
        sentiment = float(market_event.get("sentiment_score", 60))
        panic = float(market_event.get("panic_score", 20))
        greed = float(market_event.get("greed_score", 50))
        cognitive_entropy = float(market_event.get("cognitive_entropy", 35))
        direction = "BUY" if sentiment > 60 and panic < 50 else "HOLD"
        return IntentVector(
            cycle_id=market_event.get("cycle_id",""),
            servo="news_psychology",
            symbol=market_event.get("symbol","BTCUSDT"),
            direction=direction,
            confidence=sentiment,
            risk=max(panic, greed if greed > 85 else 35),
            evidence_strength=float(market_event.get("news_impact_score", 60)),
            manipulation_risk=float(market_event.get("narrative_manipulation_score", 25)),
            entropy_score=cognitive_entropy,
            reality_score=70,
            opportunity_score=sentiment if direction == "BUY" else 35,
            reasons=("sentiment", "panic_greed", "news_impact"),
        )
