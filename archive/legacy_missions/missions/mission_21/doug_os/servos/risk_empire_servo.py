from doug_os.core.intent_vector import IntentVector
from doug_os.engines.risk_empire import RiskEmpire
from doug_os.engines.manipulation_intelligence import ManipulationIntelligenceEngine
from doug_os.config import DEFAULT_SYMBOL

class RiskEmpireServo:
    name = "risk_empire"
    async def analyze(self, market_event: dict) -> IntentVector:
        manipulation = ManipulationIntelligenceEngine().detect(market_event)
        enriched = dict(market_event)
        enriched["manipulation_risk"] = max(float(enriched.get("manipulation_risk", 0)), manipulation["manipulation_score"])
        risk = RiskEmpire().evaluate_market(enriched)
        direction = "BLOCK" if risk["decision"] == "BLOCK" else "HOLD"
        return IntentVector(
            cycle_id=market_event.get("cycle_id", ""),
            servo=self.name,
            symbol=market_event.get("symbol", DEFAULT_SYMBOL),
            direction=direction,
            confidence=95 if direction == "BLOCK" else 72,
            risk=95 if direction == "BLOCK" else 45,
            evidence_strength=90,
            manipulation_risk=manipulation["manipulation_score"],
            entropy_score=float(market_event.get("entropy", 35)),
            reality_score=float(market_event.get("reality_score", 80)),
            opportunity_score=0 if direction == "BLOCK" else 35,
                reasons=(risk["reason"], manipulation["action"]),
                # Only include the bunker_mode warning when it is active; avoid empty strings in the warnings tuple
                warnings=("bunker_mode",) if risk.get("bunker_mode") else (),
            )
