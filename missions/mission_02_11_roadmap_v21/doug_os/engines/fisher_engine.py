from statistics import variance

class FisherInformationEngine:
    def score(self, prices: list[float]) -> float:
        if len(prices) < 3:
            return 0.0
        diffs = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        v = variance(diffs) if len(diffs) > 1 else 0.0
        return round(min(100.0, 100.0 / (1.0 + v)), 2)
