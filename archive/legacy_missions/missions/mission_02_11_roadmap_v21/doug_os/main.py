import asyncio
from doug_os.brain.doug_brain import DougBrain
from doug_os.brian.brian_supreme import BrianSupreme
from doug_os.memory.experience_store import ExperienceStore
from doug_os.memory.probability_engine import ProbabilityEngine
from doug_os.engines.opportunity_ranker import OpportunityRanker

async def main():
    brain = DougBrain()

    market_event = {
        "symbol": "BTCUSDT",
        "price": 68000,
        "volume": 250000,
        "prices": [67800, 67900, 68000, 68100],
        "liquidity_distribution": [0.2, 0.3, 0.25, 0.25],
        "volatility": 0.025,
        "drawdown": 0.005,
        "daily_loss": 0.0,
        "weekly_loss": 0.0,
        "entropy": 35,
        "risk": 30,
        "manipulation_risk": 20,
        "reality_score": 82,
        "exchange_inflow_score": 20,
        "exchange_outflow_score": 65,
        "whale_accumulation_score": 60,
        "stablecoin_flow_score": 62,
        "sentiment_score": 64,
        "panic_score": 20,
        "greed_score": 55,
        "narrative_strength": 60,
        "historical_edge": 60,
    }

    result = await brain.process_market_event(market_event)

    store = ExperienceStore()
    context = {"symbol": market_event["symbol"], "regime": result["regime"], "decision": result["decision"]["decision"]}
    store.save(context=context, regime=result["regime"], decision=result["decision"]["decision"], result="SIMULATED", pnl=0.0)
    probability = ProbabilityEngine().estimate(store.similar(context))

    ranking = OpportunityRanker().rank([
        {"symbol": "BTC", "market_score": 78, "onchain_score": 72, "psychology_score": 65, "opportunity_score": 80, "risk_score": 35, "manipulation_score": 20},
        {"symbol": "ETH", "market_score": 72, "onchain_score": 70, "psychology_score": 60, "opportunity_score": 74, "risk_score": 38, "manipulation_score": 25},
        {"symbol": "SOL", "market_score": 66, "onchain_score": 58, "psychology_score": 64, "opportunity_score": 70, "risk_score": 55, "manipulation_score": 30},
    ])

    brian = BrianSupreme().learn()

    print("DOUG.OS — ROADMAP PRODUÇÃO v2.1")
    print("Cycle:", result["cycle_id"])
    print("Decision:", result["decision"]["decision"])
    print("Reason:", result["decision"]["reason"])
    print("Regime:", result["regime"])
    print("Confidence:", result["decision"]["confidence"])
    print("Top opportunity:", ranking[0])
    print("Experience:", probability)
    print("Brian:", brian)

if __name__ == "__main__":
    asyncio.run(main())
