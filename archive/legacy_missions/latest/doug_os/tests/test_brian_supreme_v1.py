from doug_os.brian.brian_supreme_v1 import BrianSupremeV1
from doug_os.core.intent_vector import IntentVector


def test_detects_direction_conflict_and_suggests_hold():
    bs = BrianSupremeV1()
    v1 = IntentVector(servo="market", direction="BUY", symbol="BTCUSDT", confidence=60, risk=30,
                       evidence_strength=70, manipulation_risk=10, entropy_score=20, reality_score=50,
                       opportunity_score=60, reasons=("trend",))
    v2 = IntentVector(servo="onchain", direction="SELL", symbol="BTCUSDT", confidence=55, risk=25,
                       evidence_strength=65, manipulation_risk=5, entropy_score=15, reality_score=50,
                       opportunity_score=55, reasons=("whales",))
    result = bs.review([v1, v2])
    # Should detect conflict
    assert any("directions_conflict" in inc for inc in result["inconsistencies"])
    # Should suggest hold or weight adjustments
    assert result["suggestions"]
    # Should produce two explanations
    assert len(result["explanations"]) == 2


def test_detects_high_risk_action():
    bs = BrianSupremeV1()
    v = IntentVector(servo="risk_empire", direction="BUY", symbol="BTCUSDT", confidence=70, risk=85,
                     evidence_strength=50, manipulation_risk=20, entropy_score=30, reality_score=50,
                     opportunity_score=70, reasons=("oversold",))
    result = bs.review([v])
    # Should flag high risk action
    assert any("high_risk_action" in inc for inc in result["inconsistencies"])
    # Should suggest to review decision
    assert any("Reveja" in s for s in result["suggestions"])