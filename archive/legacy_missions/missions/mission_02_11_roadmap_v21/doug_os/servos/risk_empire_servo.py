from doug_os.core.intent_vector import IntentVector
from doug_os.risk.veto_engine import VetoEngine
from doug_os.engines.manipulation_engine import ManipulationEngine

class RiskEmpireServo:
    name = "risk_empire"

    async def analyze(self, market_event: dict) -> IntentVector:
        manipulation = ManipulationEngine().detect(market_event)
        enriched = dict(market_event)
        enriched["manipulation_risk"] = max(float(enriched.get("manipulation_risk", 0)), manipulation["manipulation_score"])

        veto = VetoEngine().veto(enriched)
        direction = "BLOCK" if veto["decision"] == "BLOCK" else "HOLD"

        return IntentVector(
            cycle_id=market_event.get("cycle_id", ""),
            servo="risk_empire",
            symbol=market_event.get("symbol", "BTCUSDT"),
            direction=direction,
            confidence=96 if direction == "BLOCK" else 72,
            risk=96 if direction == "BLOCK" else 44,
            evidence_strength=92,
            manipulation_risk=manipulation["manipulation_score"],
            entropy_score=float(market_event.get("entropy", 35)),
            reality_score=float(market_event.get("reality_score", 80)),
            opportunity_score=0 if direction == "BLOCK" else 35,
            reasons=(veto["reason"], manipulation["action"]),
            warnings=("bunker_mode",) if veto.get("bunker_mode") else (),
        )
