class ManipulationEngine:
    def detect(self, market_event: dict) -> dict:
        signals = {
            "spoofing": float(market_event.get("spoofing_score", 0)),
            "wash_trading": float(market_event.get("wash_trading_score", 0)),
            "fake_liquidity": float(market_event.get("fake_liquidity_score", 0)),
            "stop_hunt": float(market_event.get("stop_hunt_score", 0)),
            "ghost_orders": float(market_event.get("ghost_orders_score", 0)),
        }
        score = round(
            signals["spoofing"] * 0.22
            + signals["wash_trading"] * 0.18
            + signals["fake_liquidity"] * 0.22
            + signals["stop_hunt"] * 0.20
            + signals["ghost_orders"] * 0.18,
            2,
        )

        if score > 70:
            action = "BLOCK"
        elif score >= 40:
            action = "REDUCE_CONFIDENCE"
        else:
            action = "ALLOW"

        return {"manipulation_score": score, "action": action, "signals": signals}
