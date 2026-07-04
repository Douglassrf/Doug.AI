class ShadowExecutor:
    def simulate(self, decision: dict, market_event: dict) -> dict:
        return {
            "mode": "shadow",
            "executed": False,
            "real_money": False,
            "symbol": market_event.get("symbol"),
            "decision": decision.get("decision"),
            "confidence": decision.get("confidence"),
            "note": "paper simulation only; no real order sent",
        }
