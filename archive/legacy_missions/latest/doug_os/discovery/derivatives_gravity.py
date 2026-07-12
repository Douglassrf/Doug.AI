from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import numpy as np


@dataclass
class DerivativeData:
    timestamp: datetime
    open_interest: float = 0.0
    gamma_exposure: float = 0.0
    delta_exposure: float = 0.0
    dealer_delta: float = 0.0
    options_volume: float = 0.0
    puts_calls_ratio: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "open_interest": self.open_interest,
            "gamma_exposure": self.gamma_exposure,
            "delta_exposure": self.delta_exposure,
            "dealer_delta": self.dealer_delta,
            "options_volume": self.options_volume,
            "puts_calls_ratio": self.puts_calls_ratio,
        }


@dataclass
class GravityIndex:
    index: float = 0.0
    gravity_score: float = 0.0
    pressure_score: float = 0.0
    risk_level: str = "low"
    components: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "gravity_score": self.gravity_score,
            "pressure_score": self.pressure_score,
            "risk_level": self.risk_level,
            "components": self.components,
            "created_at": self.created_at.isoformat(),
        }


class DerivativesGravityEngine:
    def __init__(self):
        self._history: List[DerivativeData] = []
        self._gravity_history: List[GravityIndex] = []

    def analyze(self, data: DerivativeData) -> GravityIndex:
        self._history.append(data)
        components = self._calculate_components(data)
        gravity_score = self._calculate_gravity(components)
        pressure_score = self._calculate_pressure(data)
        index = (gravity_score + pressure_score) / 2
        risk_level = self._determine_risk_level(index)
        result = GravityIndex(
            index=index, gravity_score=gravity_score,
            pressure_score=pressure_score, risk_level=risk_level, components=components,
        )
        self._gravity_history.append(result)
        return result

    def _calculate_components(self, data: DerivativeData) -> Dict[str, float]:
        return {
            "open_interest": min(data.open_interest / 1000, 1.0) if data.open_interest > 0 else 0.3,
            "gamma": min(data.gamma_exposure / 100, 1.0) if data.gamma_exposure > 0 else 0.3,
            "delta": min(abs(data.delta_exposure) / 100, 1.0) if data.delta_exposure != 0 else 0.3,
            "dealer_delta": min(abs(data.dealer_delta) / 100, 1.0) if data.dealer_delta != 0 else 0.3,
            "volume": min(data.options_volume / 100, 1.0) if data.options_volume > 0 else 0.2,
            "put_call": min(data.puts_calls_ratio / 2, 1.0) if data.puts_calls_ratio > 0 else 0.5,
        }

    def _calculate_gravity(self, components: Dict[str, float]) -> float:
        return min(
            components["open_interest"] * 0.30
            + components["gamma"] * 0.25
            + components["delta"] * 0.25
            + components["dealer_delta"] * 0.10
            + components["volume"] * 0.10,
            1.0,
        )

    def _calculate_pressure(self, data: DerivativeData) -> float:
        pc = min(data.puts_calls_ratio / 2, 1.0) if data.puts_calls_ratio > 0 else 0.5
        gp = min(data.gamma_exposure / 50, 1.0) if data.gamma_exposure > 0 else 0.5
        return min((pc + gp) / 2, 1.0)

    def _determine_risk_level(self, index: float) -> str:
        if index > 0.8: return "extreme"
        if index > 0.6: return "high"
        if index > 0.4: return "medium"
        return "low"
