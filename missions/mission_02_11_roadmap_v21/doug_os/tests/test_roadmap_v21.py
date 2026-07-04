import asyncio
from doug_os.brain.doug_brain import DougBrain
from doug_os.engines.manipulation_engine import ManipulationEngine
from doug_os.engines.opportunity_ranker import OpportunityRanker
from doug_os.risk.risk_core import RiskCore
from doug_os.memory.experience_store import ExperienceStore
from doug_os.memory.probability_engine import ProbabilityEngine

async def test_cycle():
    brain = DougBrain()
    result = await brain.process_market_event({
        "symbol": "BTCUSDT",
        "price": 68000,
        "volume": 250000,
        "prices": [67800, 67900, 68000, 68100],
        "liquidity_distribution": [0.2, 0.3, 0.25, 0.25],
        "risk": 30,
        "entropy": 35,
        "manipulation_risk": 20,
        "reality_score": 82,
        "drawdown": 0.005,
    })
    assert result["cycle_id"]
    assert result["decision"]["decision"] in ("BUY", "SELL", "HOLD", "BLOCK")
    assert len(result["vectors"]) == 5

def test_risk_block():
    out = RiskCore().evaluate({"risk": 90})
    assert out["decision"] == "BLOCK"

def test_manipulation_block():
    out = ManipulationEngine().detect({
        "spoofing_score": 100,
        "wash_trading_score": 100,
        "fake_liquidity_score": 100,
        "stop_hunt_score": 100,
        "ghost_orders_score": 100,
    })
    assert out["action"] == "BLOCK"

def test_ranking():
    ranked = OpportunityRanker().rank([
        {"symbol": "BTC", "market_score": 80, "onchain_score": 75, "psychology_score": 70, "opportunity_score": 82, "risk_score": 30, "manipulation_score": 20},
        {"symbol": "XRP", "market_score": 40, "onchain_score": 35, "psychology_score": 45, "opportunity_score": 40, "risk_score": 70, "manipulation_score": 60},
    ])
    assert ranked[0]["symbol"] == "BTC"
    assert ranked[0]["approved"] is True

def test_experience():
    store = ExperienceStore(":memory:")
    context = {"symbol": "BTC", "regime": "NORMAL"}
    store.save(context, "NORMAL", "BUY", "WIN", 1.0)
    p = ProbabilityEngine().estimate(store.similar(context))
    assert p["samples"] == 1
    assert p["win_probability"] == 1.0

if __name__ == "__main__":
    asyncio.run(test_cycle())
    test_risk_block()
    test_manipulation_block()
    test_ranking()
    test_experience()
    print("roadmap v2.1 tests passed")
