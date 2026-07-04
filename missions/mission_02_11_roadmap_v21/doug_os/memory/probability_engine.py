class ProbabilityEngine:
    def estimate(self, experiences: list[dict]) -> dict:
        if not experiences:
            return {"win_probability": 0.0, "samples": 0, "confidence_adjustment": 0.0}

        wins = sum(1 for e in experiences if e.get("result") == "WIN")
        samples = len(experiences)
        win_probability = wins / samples

        return {
            "win_probability": round(win_probability, 4),
            "samples": samples,
            "confidence_adjustment": round((win_probability - 0.5) * 20, 4),
        }
