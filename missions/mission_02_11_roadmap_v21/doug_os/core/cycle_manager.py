import asyncio
from doug_os.core.cycle_registry import CycleRegistry
from doug_os.core.intent_vector import defensive_vector

class DecisionCycleEngine:
    def __init__(self, timeout_seconds: float = 1.5):
        self.registry = CycleRegistry()
        self.timeout_seconds = timeout_seconds

    async def run_cycle(self, servos, market_event: dict):
        cycle = self.registry.create(symbol=market_event.get("symbol", "BTCUSDT"))
        event = dict(market_event)
        event["cycle_id"] = cycle.cycle_id
        symbol = event["symbol"]

        async def call_servo(servo):
            try:
                return await asyncio.wait_for(servo.analyze(event), timeout=self.timeout_seconds)
            except Exception as exc:
                return defensive_vector(
                    servo=getattr(servo, "name", "market"),
                    symbol=symbol,
                    reason=f"servo_failure_or_timeout:{exc}",
                    cycle_id=cycle.cycle_id,
                )

        vectors = await asyncio.gather(*(call_servo(s) for s in servos))
        self.registry.close(cycle.cycle_id, status="COLLECTED")
        return cycle.cycle_id, vectors
