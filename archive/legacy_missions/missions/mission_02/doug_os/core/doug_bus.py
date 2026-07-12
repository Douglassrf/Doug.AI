import asyncio
from doug_os.core.intent_vector import defensive_vector, new_cycle_id


class DougBus:
    def __init__(self, timeout_seconds: float = 1.5):
        self.timeout_seconds = timeout_seconds

    async def collect(self, servos, market_event: dict):
        cycle_id = market_event.get("cycle_id") or new_cycle_id()
        symbol = market_event.get("symbol", "BTCUSDT")
        event = dict(market_event)
        event["cycle_id"] = cycle_id

        async def run_servo(servo):
            servo_name = getattr(servo, "name", "market")
            try:
                vector = await asyncio.wait_for(
                    servo.analyze(event),
                    timeout=self.timeout_seconds,
                )

                if vector.cycle_id != cycle_id:
                    return defensive_vector(
                        servo=servo_name,
                        symbol=symbol,
                        cycle_id=cycle_id,
                        reason="cycle_id_mismatch",
                    )

                return vector

            except asyncio.TimeoutError:
                return defensive_vector(
                    servo=servo_name,
                    symbol=symbol,
                    cycle_id=cycle_id,
                    reason="servo_timeout",
                )
            except Exception as exc:
                return defensive_vector(
                    servo=servo_name,
                    symbol=symbol,
                    cycle_id=cycle_id,
                    reason=f"servo_failure: {exc}",
                )

        vectors = await asyncio.gather(*(run_servo(servo) for servo in servos))

        return {
            "cycle_id": cycle_id,
            "market_event": event,
            "vectors": vectors,
        }
