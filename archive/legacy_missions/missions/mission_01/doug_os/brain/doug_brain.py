from doug_os.core.doug_bus import DougBus
from doug_os.core.intelligence_council import IntelligenceCouncil
from doug_os.core.audit_log import AuditLog
from doug_os.execution.shadow_executor import ShadowExecutor
from doug_os.servos.market_servo import MarketIntelligenceServo
from doug_os.servos.onchain_servo import OnChainIntelligenceServo
from doug_os.servos.news_psychology_servo import NewsPsychologyServo
from doug_os.servos.risk_empire_servo import RiskEmpireServo
from doug_os.servos.evolution_research_servo import EvolutionResearchServo

class DougBrain:
    def __init__(self):
        self.bus = DougBus(); self.council = IntelligenceCouncil(); self.executor = ShadowExecutor(); self.audit = AuditLog()
        self.servos = [MarketIntelligenceServo(), OnChainIntelligenceServo(), NewsPsychologyServo(), RiskEmpireServo(), EvolutionResearchServo()]
    async def process_market_event(self, market_event: dict) -> dict:
        vectors = await self.bus.collect(self.servos, market_event)
        decision = self.council.decide(vectors)
        simulation = self.executor.simulate(decision, market_event)
        audit_payload = {'market_event':market_event,'vectors':[v.to_dict() for v in vectors],'decision':decision,'simulation':simulation}
        self.audit.record('market_cycle', audit_payload)
        return audit_payload
