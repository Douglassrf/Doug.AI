from dataclasses import dataclass, field, asdict
from typing import Literal
from time import time_ns
from uuid import uuid4

Direction = Literal["BUY", "SELL", "HOLD", "BLOCK"]
ServoName = Literal["market","onchain","news_psychology","risk_empire","evolution_research"]
TimeHorizon = Literal["scalp","short","medium","long"]

def clamp_score(value: float) -> float:
    return max(0.0, min(100.0, float(value)))

@dataclass(frozen=True)
class IntentVector:
    id: str = field(default_factory=lambda: str(uuid4()))
    cycle_id: str = ""
    timestamp_ns: int = field(default_factory=time_ns)
    servo: ServoName = "market"
    symbol: str = "BTCUSDT"
    direction: Direction = "HOLD"
    confidence: float = 0.0
    risk: float = 100.0
    evidence_strength: float = 0.0
    manipulation_risk: float = 0.0
    entropy_score: float = 0.0
    reality_score: float = 0.0
    opportunity_score: float = 0.0
    time_horizon: TimeHorizon = "short"
    reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def __post_init__(self):
        for f in ["confidence","risk","evidence_strength","manipulation_risk","entropy_score","reality_score","opportunity_score"]:
            object.__setattr__(self, f, clamp_score(getattr(self, f)))

    def validate(self) -> bool:
        return (
            self.direction in ("BUY","SELL","HOLD","BLOCK")
            and self.time_horizon in ("scalp","short","medium","long")
            and all(0 <= getattr(self, f) <= 100 for f in [
                "confidence","risk","evidence_strength","manipulation_risk",
                "entropy_score","reality_score","opportunity_score"
            ])
        )

    def is_blocking(self) -> bool:
        """Return True if this vector should immediately block trading.

        The criteria for blocking are defined in
        :mod:`doug_os.config.INTENT_VECTOR_BLOCK_THRESHOLDS`.  A vector is
        considered blocking if its direction is ``BLOCK`` or any of
        risk, manipulation risk, reality score or entropy score exceed the
        configured limits.
        """
        from doug_os.config import INTENT_VECTOR_BLOCK_THRESHOLDS as BV

        return (
            self.direction == "BLOCK"
            or self.risk >= BV["risk"]
            or self.manipulation_risk >= BV["manipulation_risk"]
            or self.reality_score <= BV["reality_score"]
            or self.entropy_score >= BV["entropy_score"]
        )

    def to_dict(self) -> dict:
        return asdict(self)

def defensive_vector(servo: ServoName, symbol: str, reason: str, cycle_id: str = "") -> IntentVector:
    return IntentVector(
        cycle_id=cycle_id, servo=servo, symbol=symbol, direction="HOLD",
        confidence=0, risk=100, evidence_strength=0, manipulation_risk=100,
        entropy_score=100, reality_score=0, opportunity_score=0, warnings=(reason,)
    )

def block_vector(servo: ServoName, symbol: str, reason: str, cycle_id: str = "") -> IntentVector:
    return IntentVector(
        cycle_id=cycle_id, servo=servo, symbol=symbol, direction="BLOCK",
        confidence=100, risk=100, evidence_strength=100, manipulation_risk=100,
        entropy_score=100, reality_score=0, opportunity_score=0, warnings=(reason,)
    )
