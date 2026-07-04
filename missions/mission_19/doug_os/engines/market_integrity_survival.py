import math
from statistics import variance

class MarketIntegritySurvivalCore:
    def shannon_entropy(self, probabilities: list[float]) -> float:
        total = sum(probabilities) or 1.0
        probs = [p/total for p in probabilities if p > 0]
        entropy = -sum(p * math.log2(p) for p in probs)
        max_entropy = math.log2(len(probs)) if len(probs) > 1 else 1
        return round((entropy / max_entropy) * 100, 2) if max_entropy else 0

    def fisher_information(self, prices: list[float]) -> float:
        if len(prices) < 3:
            return 0
        diffs = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        v = variance(diffs) if len(diffs) > 1 else 0
        return round(min(100, 100 / (1 + v)), 2)

    def gamblers_ruin_probability(self, capital: float, risk_per_trade: float, edge: float) -> float:
        if capital <= 0 or risk_per_trade <= 0:
            return 100
        if edge <= 0:
            return 100
        risk_units = capital / risk_per_trade
        ruin = (1 - edge) ** risk_units
        return round(max(0, min(100, ruin * 100)), 4)

    def dynamic_kelly(self, win_prob: float, reward_risk: float) -> float:
        if reward_risk <= 0:
            return 0
        kelly = win_prob - ((1 - win_prob) / reward_risk)
        return round(max(0, min(0.25, kelly)), 4)

    def ergodicity_risk(self, drawdown: float, volatility: float) -> float:
        return round(max(0, min(100, (drawdown * 1200) + (volatility * 800))), 2)

    def evaluate(self, market_event: dict) -> dict:
        prices = market_event.get("prices", [1, 1.01, 1.02, 1.01])
        liquidity_probs = market_event.get("liquidity_distribution", [0.25,0.25,0.25,0.25])
        entropy = self.shannon_entropy(liquidity_probs)
        fisher = self.fisher_information(prices)
        ruin = self.gamblers_ruin_probability(
            capital=float(market_event.get("capital", 1000)),
            risk_per_trade=float(market_event.get("risk_amount", 10)),
            edge=float(market_event.get("edge", 0.05)),
        )
        kelly = self.dynamic_kelly(
            win_prob=float(market_event.get("win_prob", 0.55)),
            reward_risk=float(market_event.get("reward_risk", 1.5)),
        )
        ergodicity = self.ergodicity_risk(
            drawdown=float(market_event.get("drawdown", 0)),
            volatility=float(market_event.get("volatility", 0.02)),
        )

        tradeable = entropy < 85 and fisher > 20 and ruin < 70 and ergodicity < 80
        return {
            "tradeable": tradeable,
            "entropy_score": entropy,
            "fisher_information": fisher,
            "ruin_probability": ruin,
            "dynamic_kelly": kelly,
            "ergodicity_risk": ergodicity,
            "reason": "market_integrity_approved" if tradeable else "market_integrity_rejected",
        }
