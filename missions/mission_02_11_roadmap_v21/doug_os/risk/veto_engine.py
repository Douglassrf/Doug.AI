from doug_os.risk.risk_core import RiskCore

class VetoEngine:
    def __init__(self):
        self.risk_core = RiskCore()

    def veto(self, market_event: dict) -> dict:
        return self.risk_core.evaluate(market_event)
