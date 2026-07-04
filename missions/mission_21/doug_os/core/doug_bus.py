import asyncio
from uuid import uuid4
from doug_os.core.intent_vector import defensive_vector

class DougBus:
    def __init__(self, timeout_seconds: float = 1.5):
        self.timeout_seconds = timeout_seconds

    async def collect(self, servos, market_event: dict):
        cycle_id = market_event.get("cycle_id") or str(uuid4())
        market_event = dict(market_event)
        market_event["cycle_id"] = cycle_id
        symbol = market_event.get("symbol", "BTCUSDT")

        async def run_servo(servo):
            try:
                return await asyncio.wait_for(servo.analyze(market_event), timeout=self.timeout_seconds)
            except Exception as exc:
                return defensive_vector(getattr(servo, "name", "market"), symbol, f"servo_failure: {exc}", cycle_id=cycle_id)

        vectors = await asyncio.gather(*(run_servo(servo) for servo in servos))
        return cycle_id, vectors
