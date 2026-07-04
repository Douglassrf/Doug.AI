import asyncio
from doug_os.brain.doug_brain import DougBrain


async def main():
    brain = DougBrain()

    market_event = {
        "symbol": "BTCUSDT",
        "price": 68000,
        "volume": 250000,
        "volatility": 0.025,
        "drawdown": 0.005,
        "entropy": 35,
        "manipulation_risk": 20,
        "reality_score": 82,
    }

    result = await brain.process_market_event(market_event)

    print("DOUG.OS — DECISION CYCLE")
    print("Cycle ID:", result["cycle_id"])
    print("Decision:", result["decision"]["decision"])
    print("Reason:", result["decision"]["reason"])
    print("Regime:", result["decision"].get("regime"))
    print("Confidence:", result["decision"].get("confidence"))
    print("Shadow:", result["simulation"])


if __name__ == "__main__":
    asyncio.run(main())
