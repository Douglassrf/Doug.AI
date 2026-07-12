class DigitalTwin:
    def simulate(self, decision: dict, portfolio: dict) -> dict:
        drawdown_after = float(portfolio.get("drawdown", 0)) + (0.005 if decision.get("decision") in ("BUY","SELL") else 0)
        approved = drawdown_after < float(portfolio.get("max_drawdown", 0.03)) and decision.get("decision") != "BLOCK"
        return {"approved": approved, "drawdown_after": drawdown_after, "reason": "digital_twin_approved" if approved else "digital_twin_rejected"}
