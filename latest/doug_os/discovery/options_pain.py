from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import numpy as np


@dataclass
class OptionCluster:
    strike: float = 0.0
    open_interest: float = 0.0
    gamma: float = 0.0
    delta: float = 0.0
    type: str = "call"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strike": self.strike, "open_interest": self.open_interest,
            "gamma": self.gamma, "delta": self.delta, "type": self.type,
        }


@dataclass
class OptionsPainResult:
    max_pain_price: float = 0.0
    current_price: float = 0.0
    pain_gap: float = 0.0
    gamma_walls: List[float] = field(default_factory=list)
    clusters: List[OptionCluster] = field(default_factory=list)
    expiration_pressure: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_pain_price": self.max_pain_price,
            "current_price": self.current_price,
            "pain_gap": self.pain_gap,
            "gamma_walls": self.gamma_walls,
            "expiration_pressure": self.expiration_pressure,
            "created_at": self.created_at.isoformat(),
        }


class OptionsPainEngine:
    def __init__(self):
        self._models: List[OptionsPainResult] = []

    def calculate_pain(
        self,
        calls: List[Dict[str, float]],
        puts: List[Dict[str, float]],
        current_price: float,
    ) -> OptionsPainResult:
        clusters = self._create_clusters(calls, puts)
        max_pain = self._find_max_pain(clusters, current_price)
        gamma_walls = self._detect_gamma_walls(clusters)
        expiration_pressure = self._calculate_expiration_pressure(clusters)
        result = OptionsPainResult(
            max_pain_price=max_pain, current_price=current_price,
            pain_gap=abs(current_price - max_pain),
            gamma_walls=gamma_walls, clusters=clusters,
            expiration_pressure=expiration_pressure,
        )
        self._models.append(result)
        return result

    def _create_clusters(self, calls, puts) -> List[OptionCluster]:
        clusters = [
            OptionCluster(strike=c.get("strike", 0), open_interest=c.get("open_interest", 0),
                          gamma=c.get("gamma", 0), delta=c.get("delta", 0), type="call")
            for c in calls
        ] + [
            OptionCluster(strike=p.get("strike", 0), open_interest=p.get("open_interest", 0),
                          gamma=p.get("gamma", 0), delta=p.get("delta", 0), type="put")
            for p in puts
        ]
        return sorted(clusters, key=lambda x: x.strike)

    def _find_max_pain(self, clusters: List[OptionCluster], current_price: float) -> float:
        if not clusters: return current_price
        strike_oi: Dict[float, float] = {}
        for c in clusters:
            strike_oi[c.strike] = strike_oi.get(c.strike, 0) + c.open_interest
        return max(strike_oi, key=strike_oi.get) if strike_oi else current_price

    def _detect_gamma_walls(self, clusters: List[OptionCluster]) -> List[float]:
        gamma_by_strike: Dict[float, float] = {}
        for c in clusters:
            if c.gamma > 0:
                gamma_by_strike[c.strike] = gamma_by_strike.get(c.strike, 0) + c.gamma
        sorted_walls = sorted(gamma_by_strike.items(), key=lambda x: x[1], reverse=True)
        return [s for s, _ in sorted_walls[:5]]

    def _calculate_expiration_pressure(self, clusters: List[OptionCluster]) -> float:
        total_oi = sum(c.open_interest for c in clusters)
        if total_oi == 0: return 0.0
        atm_oi = sum(c.open_interest for c in clusters if 0.95 <= c.strike <= 1.05)
        return atm_oi / total_oi
