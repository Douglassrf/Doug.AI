from dataclasses import dataclass, field, asdict
from typing import Literal
from time import time_ns
from uuid import uuid4

Direction = Literal['BUY', 'SELL', 'HOLD', 'BLOCK']
ServoName = Literal['market','onchain','news_psychology','risk_empire','evolution_research']
TimeHorizon = Literal['scalp','short','medium','long']

def clamp_score(value: float) -> float:
    return max(0.0, min(100.0, float(value)))

@dataclass(frozen=True)
class IntentVector:
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp_ns: int = field(default_factory=time_ns)
    servo: ServoName = 'market'
    symbol: str = 'BTCUSDT'
    direction: Direction = 'HOLD'
    confidence: float = 0.0
    risk: float = 100.0
    evidence_strength: float = 0.0
    manipulation_risk: float = 0.0
    entropy_score: float = 0.0
    reality_score: float = 0.0
    opportunity_score: float = 0.0
    time_horizon: TimeHorizon = 'short'
    reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def __post_init__(self):
        for field_name in ['confidence','risk','evidence_strength','manipulation_risk','entropy_score','reality_score','opportunity_score']:
            object.__setattr__(self, field_name, clamp_score(getattr(self, field_name)))

    def validate(self) -> bool:
        if self.direction not in ('BUY','SELL','HOLD','BLOCK'):
            return False
        if self.time_horizon not in ('scalp','short','medium','long'):
            return False
        return all(0 <= getattr(self, f) <= 100 for f in ['confidence','risk','evidence_strength','manipulation_risk','entropy_score','reality_score','opportunity_score'])

    def is_blocking(self) -> bool:
        return self.direction == 'BLOCK' or self.risk >= 80 or self.manipulation_risk >= 70 or self.reality_score <= 40 or self.entropy_score >= 85

    def to_dict(self) -> dict:
        return asdict(self)

def defensive_vector(servo: ServoName, symbol: str, reason: str) -> IntentVector:
    return IntentVector(servo=servo, symbol=symbol, direction='HOLD', confidence=0, risk=100, evidence_strength=0, manipulation_risk=100, entropy_score=100, reality_score=0, opportunity_score=0, warnings=(reason,))

def block_vector(servo: ServoName, symbol: str, reason: str) -> IntentVector:
    return IntentVector(servo=servo, symbol=symbol, direction='BLOCK', confidence=100, risk=100, evidence_strength=100, manipulation_risk=100, entropy_score=100, reality_score=0, opportunity_score=0, warnings=(reason,))
