from doug_os.core.intent_vector import IntentVector
from doug_os.config import SERVO_THRESHOLDS, DEFAULT_SYMBOL

class OnChainIntelligenceServo:
    name = "onchain"
    async def analyze(self, market_event: dict) -> IntentVector:
        exchange_inflow = float(market_event.get("exchange_inflow_score", 25))
        exchange_outflow = float(market_event.get("exchange_outflow_score", 55))
        whale = float(market_event.get("whale_accumulation_score", 50))
        dump_risk = exchange_inflow * 0.5 + (100 - whale) * 0.3
        # Use configured thresholds for whale accumulation and dump risk warnings
        cfg = SERVO_THRESHOLDS.get(self.name, {})
        min_whale = float(cfg.get("min_whale_accumulation", 50.0))
        warning_threshold = float(cfg.get("max_dump_risk_warning", 65.0))
        direction = "BUY" if exchange_outflow > exchange_inflow and whale >= min_whale else "HOLD"
        return IntentVector(
            cycle_id=market_event.get("cycle_id", ""),
            servo=self.name,
            symbol=market_event.get("symbol", DEFAULT_SYMBOL),
            direction=direction,
            confidence=max(45.0, min(85.0, whale)),
            risk=min(100.0, dump_risk),
            evidence_strength=65,
            manipulation_risk=float(market_event.get("manipulation_risk", 30)),
            entropy_score=35,
            reality_score=78,
            opportunity_score=65 if direction == "BUY" else 40,
            reasons=("stablecoin_flow", "whale_movement", "exchange_flow"),
            # Only include the dump_risk warning when the calculated risk exceeds the configured threshold
            warnings=("dump_risk",) if dump_risk > warning_threshold else (),
        )
