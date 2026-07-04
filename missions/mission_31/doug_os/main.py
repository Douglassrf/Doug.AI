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
        "prices": [67800, 67900, 68000, 68100],
        "liquidity_distribution": [0.2, 0.3, 0.25, 0.25],
        "capital": 10000,
        "risk_amount": 50,
        "edge": 0.05,
        "win_prob": 0.56,
        "reward_risk": 1.5,
        "historical_edge": 58,
    }
    result = await brain.process_market_event(market_event)
    print("DOUG.OS — MARKET CYCLE")
    print("Cycle:", result["cycle_id"])
    print("Decision:", result["decision"]["decision"])
    print("Reason:", result["decision"]["reason"])
    print("Regime:", result["decision"].get("regime"))
    print("Confidence:", result["decision"].get("confidence"))
    print("Shadow:", result["simulation"]["note"])

if __name__ == "__main__":
    asyncio.run(main())
