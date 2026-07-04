from doug_os.core.cycle_manager import DecisionCycleEngine
from doug_os.core.intelligence_council import IntelligenceCouncil
from doug_os.core.audit_log import AuditLog
from doug_os.execution.shadow_executor import ShadowExecutor
from doug_os.servos.market_servo import MarketServo
from doug_os.servos.onchain_servo_v1 import OnChainIntelligenceServoV1
from doug_os.servos.psychology_servo_v1 import NewsPsychologyServoV1
from doug_os.servos.risk_empire_servo import RiskEmpireServo
from doug_os.servos.evolution_research_servo import EvolutionResearchServo

class DougBrain:
    def __init__(self):
        self.cycle_engine = DecisionCycleEngine()
        self.council = IntelligenceCouncil()
        self.audit = AuditLog()
        self.executor = ShadowExecutor()

        self.servos = [
            MarketServo(),
            OnChainIntelligenceServoV1(),
            NewsPsychologyServoV1(),
            RiskEmpireServo(),
            EvolutionResearchServo(),
        ]

    async def process_market_event(self, market_event: dict) -> dict:
        cycle_id, vectors = await self.cycle_engine.run_cycle(self.servos, market_event)
        decision = self.council.decide(vectors, cycle_id=cycle_id)
        simulation = self.executor.simulate(decision, {**market_event, "cycle_id": cycle_id})

        payload = {
            "cycle_id": cycle_id,
            "market_event": market_event,
            "vectors": [v.to_dict() for v in vectors],
            "regime": decision.get("regime"),
            "weights": decision.get("weights"),
            "decision": decision,
            "simulation": simulation,
        }

        self.audit.record("market_cycle", payload)
        return payload
