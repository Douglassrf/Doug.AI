from doug_os.engines.entropy_engine import ShannonEntropyEngine
from doug_os.engines.fisher_engine import FisherInformationEngine

class MarketIntegrityCore:
    def __init__(self):
        self.entropy = ShannonEntropyEngine()
        self.fisher = FisherInformationEngine()

    def evaluate(self, market_event: dict) -> dict:
        entropy_score = self.entropy.score(market_event.get("liquidity_distribution", [0.25, 0.25, 0.25, 0.25]))
        fisher_score = self.fisher.score(market_event.get("prices", [1.0, 1.01, 1.02, 1.01]))
        reality_score = float(market_event.get("reality_score", 80))

        white_noise = entropy_score >= 85 or fisher_score <= 20
        approved = not white_noise and reality_score > 40

        return {
            "approved": approved,
            "entropy_score": entropy_score,
            "fisher_score": fisher_score,
            "reality_score": reality_score,
            "reason": "market_integrity_approved" if approved else "market_quality_bad_hold",
        }
