import asyncio
import random

class BinanceTestnetDataConnector:
    async def stream_mock(self, symbol="BTCUSDT", ticks=3):
        for _ in range(ticks):
            await asyncio.sleep(0.01)
            yield {
                "symbol": symbol,
                "price": round(68000 + random.uniform(-100, 100), 2),
                "volume": random.randint(100000, 300000),
                "volatility": 0.025,
                "drawdown": 0.005,
                "entropy": 35,
                "manipulation_risk": 20,
                "reality_score": 82,
            }
