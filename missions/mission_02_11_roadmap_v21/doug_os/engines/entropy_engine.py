import math

class ShannonEntropyEngine:
    def score(self, probabilities: list[float]) -> float:
        total = sum(probabilities) or 1.0
        probs = [p / total for p in probabilities if p > 0]
        if len(probs) <= 1:
            return 0.0
        entropy = -sum(p * math.log2(p) for p in probs)
        max_entropy = math.log2(len(probs))
        return round((entropy / max_entropy) * 100, 2)
