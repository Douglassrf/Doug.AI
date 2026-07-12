from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import numpy as np


@dataclass
class BondData:
    timestamp: datetime
    yield_2y: float = 0.0
    yield_5y: float = 0.0
    yield_10y: float = 0.0
    yield_30y: float = 0.0
    credit_spread: float = 0.0
    corporate_yield: float = 0.0
    duration: float = 0.0
    volume: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "yield_2y": self.yield_2y, "yield_5y": self.yield_5y,
            "yield_10y": self.yield_10y, "yield_30y": self.yield_30y,
            "credit_spread": self.credit_spread, "corporate_yield": self.corporate_yield,
            "duration": self.duration, "volume": self.volume,
        }


@dataclass
class BondIntelligence:
    curve_status: str = "normal"
    inversion_score: float = 0.0
    credit_pressure: float = 0.0
    duration_risk: float = 0.0
    liquidity_score: float = 0.0
    recession_probability: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "curve_status": self.curve_status,
            "inversion_score": self.inversion_score,
            "credit_pressure": self.credit_pressure,
            "duration_risk": self.duration_risk,
            "liquidity_score": self.liquidity_score,
            "recession_probability": self.recession_probability,
            "created_at": self.created_at.isoformat(),
        }


class BondMarketIntelligence:
    def __init__(self):
        self._history: List[BondData] = []

    def analyze(self, data: BondData) -> BondIntelligence:
        self._history.append(data)
        inversion_score = self._detect_inversion(data)
        curve_status = self._determine_curve_status(data)
        credit_pressure = self._calculate_credit_pressure(data)
        duration_risk = self._calculate_duration_risk(data)
        liquidity_score = self._calculate_liquidity_score(data)
        recession_prob = self._calculate_recession_probability(data)
        return BondIntelligence(
            curve_status=curve_status, inversion_score=inversion_score,
            credit_pressure=credit_pressure, duration_risk=duration_risk,
            liquidity_score=liquidity_score, recession_probability=recession_prob,
        )

    def _detect_inversion(self, data: BondData) -> float:
        if data.yield_10y == 0 or data.yield_2y == 0:
            return 0.0
        spread = data.yield_10y - data.yield_2y
        return float(min(-spread * 10, 1.0)) if spread < 0 else 0.0

    def _determine_curve_status(self, data: BondData) -> str:
        if data.yield_2y == 0 or data.yield_10y == 0 or data.yield_30y == 0:
            return "normal"
        spread_2_10 = data.yield_10y - data.yield_2y
        spread_10_30 = data.yield_30y - data.yield_10y
        if spread_2_10 < 0:
            return "inverted"
        if abs(spread_2_10) < 0.25:
            return "flat"
        if spread_10_30 > spread_2_10 * 1.5:
            return "steep"
        return "normal"

    def _calculate_credit_pressure(self, data: BondData) -> float:
        if data.credit_spread == 0:
            return 0.0
        return float(min(data.credit_spread / 2.0, 1.0))

    def _calculate_duration_risk(self, data: BondData) -> float:
        if data.duration == 0:
            return 0.0
        return float(min(data.duration / 10.0, 1.0))

    def _calculate_liquidity_score(self, data: BondData) -> float:
        if data.volume == 0:
            return 0.0
        return float(min(data.volume / 1000, 1.0))

    def _calculate_recession_probability(self, data: BondData) -> float:
        prob = self._detect_inversion(data) * 0.3
        prob += self._calculate_credit_pressure(data) * 0.2
        if data.yield_10y - data.yield_2y < 0.5:
            prob += 0.1
        if len(self._history) > 5:
            recent_inv = sum(1 for d in self._history[-5:] if self._detect_inversion(d) > 0)
            prob += recent_inv / 5 * 0.2
        return float(min(prob, 1.0))
