class OpportunityRankingEngine:
    def score(self, item: dict) -> float:
        opportunity = float(item.get("opportunity_score", 0))
        technical = float(item.get("technical_score", 0))
        onchain = float(item.get("onchain_score", 0))
        psychology = float(item.get("psychology_score", 0))
        risk = float(item.get("risk_score", 100))
        manipulation = float(item.get("manipulation_score", 100))
        score = (
            opportunity * 0.30 + technical * 0.20 + onchain * 0.20 + psychology * 0.10
            + (100-risk) * 0.10 + (100-manipulation) * 0.10
        )
        return round(max(0, min(100, score)), 2)

    def rank(self, opportunities: list[dict]) -> list[dict]:
        ranked = []
        for item in opportunities:
            enriched = dict(item)
            enriched["final_score"] = self.score(item)
            enriched["approved"] = enriched["final_score"] >= 70 and item.get("risk_score", 100) < 70 and item.get("manipulation_score", 100) < 70
            ranked.append(enriched)
        return sorted(ranked, key=lambda x: x["final_score"], reverse=True)
