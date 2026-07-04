class ManipulationIntelligenceEngine:
    def detect(self, market_event: dict) -> dict:
        spoofing = float(market_event.get("spoofing_score", 0))
        wash = float(market_event.get("wash_trading_score", 0))
        stop_hunt = float(market_event.get("stop_hunt_score", 0))
        fake_liquidity = float(market_event.get("fake_liquidity_score", 0))
        hft_stress = float(market_event.get("hft_stress_score", 0))
        order_book_anomaly = float(market_event.get("order_book_anomaly_score", 0))
        absorption = float(market_event.get("absorption_score", 0))

        score = round(
            spoofing * 0.18 + wash * 0.14 + stop_hunt * 0.16 + fake_liquidity * 0.18
            + hft_stress * 0.12 + order_book_anomaly * 0.14 + absorption * 0.08,
            2,
        )

        if score > 70:
            action = "BLOCK"
        elif score >= 40:
            action = "REDUCE_CONFIDENCE"
        else:
            action = "ALLOW"

        return {
            "manipulation_score": score,
            "action": action,
            "signals": {
                "spoofing": spoofing,
                "wash_trading": wash,
                "stop_hunt": stop_hunt,
                "fake_liquidity": fake_liquidity,
                "hft_stress": hft_stress,
                "order_book_anomaly": order_book_anomaly,
                "absorption": absorption,
            },
        }
