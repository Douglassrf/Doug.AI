import asyncio
from doug_os.brain.doug_brain import DougBrain
from doug_os.engines.manipulation_intelligence import ManipulationIntelligenceEngine
from doug_os.engines.opportunity_ranking import OpportunityRankingEngine
from doug_os.execution.digital_twin import DigitalTwin
from doug_os.execution.microcapital_guard import MicrocapitalGuard

async def test_brain_cycle():
    brain = DougBrain()
    result = await brain.process_market_event({"symbol":"BTCUSDT","price":68000,"volume":250000,"volatility":0.02,"drawdown":0.005,"entropy":30,"manipulation_risk":20,"reality_score":82})
    assert result["cycle_id"]
    assert result["decision"]["decision"] in ("BUY","SELL","HOLD","BLOCK")

def test_manipulation_block():
    out = ManipulationIntelligenceEngine().detect({"spoofing_score":100,"wash_trading_score":100,"stop_hunt_score":100,"fake_liquidity_score":100,"hft_stress_score":100,"order_book_anomaly_score":100,"absorption_score":100})
    assert out["action"] == "BLOCK"

def test_opportunity_ranking():
    ranked = OpportunityRankingEngine().rank([
        {"symbol":"BTC","opportunity_score":82,"technical_score":80,"onchain_score":75,"psychology_score":70,"risk_score":30,"manipulation_score":20},
        {"symbol":"XRP","opportunity_score":40,"technical_score":50,"onchain_score":45,"psychology_score":55,"risk_score":60,"manipulation_score":55},
    ])
    assert ranked[0]["symbol"] == "BTC"

def test_digital_twin():
    result = DigitalTwin().simulate({"decision":"BUY"}, {"drawdown":0.01,"max_drawdown":0.03})
    assert result["approved"] is True

def test_microcapital_guard():
    assert MicrocapitalGuard().validate({"risk":0.001,"daily_loss":0,"leverage":1})["approved"] is True

if __name__ == "__main__":
    asyncio.run(test_brain_cycle())
    test_manipulation_block()
    test_opportunity_ranking()
    test_digital_twin()
    test_microcapital_guard()
    print("defensive core tests passed")
