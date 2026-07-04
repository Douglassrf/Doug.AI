class DynamicWeights:
    BASE = {
        "market": 0.25,
        "onchain": 0.25,
        "news_psychology": 0.15,
        "risk_empire": 0.25,
        "evolution_research": 0.10,
    }

    BY_REGIME = {
        "NORMAL": BASE,
        "TRENDING": {
            "market": 0.35,
            "onchain": 0.30,
            "news_psychology": 0.10,
            "risk_empire": 0.15,
            "evolution_research": 0.10,
        },
        "VOLATILE": {
            "market": 0.15,
            "onchain": 0.20,
            "news_psychology": 0.10,
            "risk_empire": 0.45,
            "evolution_research": 0.10,
        },
        "MANIPULATED": {
            "market": 0.10,
            "onchain": 0.35,
            "news_psychology": 0.05,
            "risk_empire": 0.40,
            "evolution_research": 0.10,
        },
        "CHAOTIC": {
            "market": 0.05,
            "onchain": 0.15,
            "news_psychology": 0.05,
            "risk_empire": 0.65,
            "evolution_research": 0.10,
        },
        "SYSTEMIC_RISK": {
            "market": 0.05,
            "onchain": 0.15,
            "news_psychology": 0.05,
            "risk_empire": 0.65,
            "evolution_research": 0.10,
        },
        "WHITE_NOISE": {
            "market": 0.05,
            "onchain": 0.05,
            "news_psychology": 0.05,
            "risk_empire": 0.75,
            "evolution_research": 0.10,
        },
    }

    def get(self, regime: str) -> dict[str, float]:
        return dict(self.BY_REGIME.get(regime, self.BASE))
