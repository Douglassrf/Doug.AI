from doug_os.core.intent_vector import IntentVector

class OnChainIntelligenceServo:
    name = 'onchain'
    async def analyze(self, market_event: dict) -> IntentVector:
        return IntentVector(servo='onchain', symbol=market_event.get('symbol','BTCUSDT'), direction='HOLD', confidence=62, risk=38, evidence_strength=58, manipulation_risk=35, entropy_score=30, reality_score=75, opportunity_score=48, time_horizon='short', reasons=('neutral_whale_flow',))
