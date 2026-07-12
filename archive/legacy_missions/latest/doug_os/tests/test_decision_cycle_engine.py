import asyncio
from doug_os.brain.doug_brain import DougBrain
from doug_os.core.intent_vector import IntentVector
from doug_os.core.intelligence_council import IntelligenceCouncil


async def test_cycle_id_is_preserved():
    brain = DougBrain()
    result = await brain.process_market_event({"symbol": "BTCUSDT", "volatility": 0.02, "drawdown": 0.001})
    cycle_id = result["cycle_id"]
    assert cycle_id
    assert all(v["cycle_id"] == cycle_id for v in result["vectors"])
    assert result["decision"]["cycle_id"] == cycle_id


def test_council_rejects_wrong_cycle():
    council = IntelligenceCouncil()
    good_cycle = "cycle-A"
    vectors = [
        IntentVector(cycle_id=good_cycle, servo="market", direction="BUY", confidence=80, risk=20, evidence_strength=80, manipulation_risk=20, entropy_score=20, reality_score=80, opportunity_score=80),
        IntentVector(cycle_id="cycle-B", servo="onchain", direction="BUY", confidence=80, risk=20, evidence_strength=80, manipulation_risk=20, entropy_score=20, reality_score=80, opportunity_score=80),
    ]
    decision = council.decide(vectors, cycle_id=good_cycle)
    assert len(decision["accepted"]) == 1
    assert len(decision["rejected"]) == 1
    assert decision["rejected"][0]["reason"] == "wrong_cycle_id"


def test_risk_empire_veto_by_cycle():
    council = IntelligenceCouncil()
    cycle = "risk-cycle"
    vectors = [
        IntentVector(cycle_id=cycle, servo="market", direction="BUY", confidence=90, risk=20, evidence_strength=90, manipulation_risk=20, entropy_score=20, reality_score=90, opportunity_score=90),
        IntentVector(cycle_id=cycle, servo="risk_empire", direction="BLOCK", confidence=95, risk=95, evidence_strength=90, manipulation_risk=80, entropy_score=90, reality_score=20, opportunity_score=0),
    ]
    decision = council.decide(vectors, cycle_id=cycle)
    assert decision["decision"] == "BLOCK"
    assert decision["reason"] == "critical_servo_block"


if __name__ == "__main__":
    asyncio.run(test_cycle_id_is_preserved())
    test_council_rejects_wrong_cycle()
    test_risk_empire_veto_by_cycle()
    print("decision cycle tests passed")
