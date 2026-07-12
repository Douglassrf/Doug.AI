class OpportunityRanker:
    def score(self, item: dict) -> float:
        score = (
            float(item.get("market_score", 0)) * 0.25
            + float(item.get("onchain_score", 0)) * 0.20
            + float(item.get("psychology_score", 0)) * 0.15
            + float(item.get("opportunity_score", 0)) * 0.20
            + (100 - float(item.get("risk_score", 100))) * 0.10
            + (100 - float(item.get("manipulation_score", 100))) * 0.10
        )
        return round(max(0, min(100, score)), 2)

    def rank(self, opportunities: list[dict]) -> list[dict]:
        ranked = []
        for item in opportunities:
            enriched = dict(item)
            enriched["final_score"] = self.score(item)
            enriched["approved"] = (
                enriched["final_score"] >= 70
                and float(item.get("risk_score", 100)) < 70
                and float(item.get("manipulation_score", 100)) < 70
            )
            ranked.append(enriched)
        return sorted(ranked, key=lambda x: x["final_score"], reverse=True)
