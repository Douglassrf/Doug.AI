from doug_os.core.intent_vector import IntentVector
from doug_os.core.intelligence_council import IntelligenceCouncil

def test_council_buy_consensus():
    vectors = [
        IntentVector(servo='market', direction='BUY', confidence=80, risk=25, evidence_strength=75, manipulation_risk=20, entropy_score=25, reality_score=85, opportunity_score=80),
        IntentVector(servo='onchain', direction='BUY', confidence=75, risk=30, evidence_strength=70, manipulation_risk=25, entropy_score=30, reality_score=80, opportunity_score=75),
        IntentVector(servo='news_psychology', direction='BUY', confidence=70, risk=35, evidence_strength=68, manipulation_risk=20, entropy_score=35, reality_score=78, opportunity_score=70),
        IntentVector(servo='risk_empire', direction='HOLD', confidence=70, risk=45, evidence_strength=70, manipulation_risk=25, entropy_score=30, reality_score=80, opportunity_score=30),
        IntentVector(servo='evolution_research', direction='BUY', confidence=62, risk=35, evidence_strength=55, manipulation_risk=20, entropy_score=30, reality_score=78, opportunity_score=60),
    ]
    decision = IntelligenceCouncil().decide(vectors)
    assert decision['decision'] in ('BUY','HOLD')

def test_risk_empire_blocks():
    vectors = [IntentVector(servo='market', direction='BUY', confidence=90, risk=20, evidence_strength=90, manipulation_risk=20, entropy_score=20, reality_score=90, opportunity_score=90), IntentVector(servo='risk_empire', direction='BLOCK', confidence=95, risk=95, evidence_strength=90, manipulation_risk=80, entropy_score=90, reality_score=20, opportunity_score=0)]
    decision = IntelligenceCouncil().decide(vectors)
    assert decision['decision'] == 'BLOCK'

if __name__ == '__main__':
    test_council_buy_consensus(); test_risk_empire_blocks(); print('tests passed')
