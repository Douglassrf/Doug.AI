import asyncio
from doug_os.core.intent_vector import defensive_vector

class DougBus:
    def __init__(self, timeout_seconds: float = 1.5):
        self.timeout_seconds = timeout_seconds
    async def collect(self, servos, market_event: dict):
        symbol = market_event.get('symbol','BTCUSDT')
        async def run_servo(servo):
            try:
                return await asyncio.wait_for(servo.analyze(market_event), timeout=self.timeout_seconds)
            except Exception as exc:
                return defensive_vector(servo=getattr(servo, 'name', 'market'), symbol=symbol, reason=f'servo_failure: {exc}')
        return await asyncio.gather(*(run_servo(servo) for servo in servos))
