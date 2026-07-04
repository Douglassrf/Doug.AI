from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import numpy as np


@dataclass
class MiningMetrics:
    timestamp: datetime
    hash_rate: float = 0.0
    difficulty: float = 0.0
    block_time: float = 0.0
    electricity_cost: float = 0.0
    miner_revenue: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "hash_rate": self.hash_rate,
            "difficulty": self.difficulty,
            "block_time": self.block_time,
            "electricity_cost": self.electricity_cost,
            "miner_revenue": self.miner_revenue,
        }


@dataclass
class EnergyCostResult:
    production_cost: float = 0.0
    market_price: float = 0.0
    cost_gap: float = 0.0
    miner_capitulation_index: float = 0.0
    hash_rate_trend: str = "stable"
    difficulty_phase: str = "normal"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "production_cost": self.production_cost,
            "market_price": self.market_price,
            "cost_gap": self.cost_gap,
            "miner_capitulation_index": self.miner_capitulation_index,
            "hash_rate_trend": self.hash_rate_trend,
            "difficulty_phase": self.difficulty_phase,
            "created_at": self.created_at.isoformat(),
        }


class EnergyCostModelBTC:
    def __init__(self):
        self._metrics: List[MiningMetrics] = []

    def analyze(self, metrics: MiningMetrics, market_price: float) -> EnergyCostResult:
        self._metrics.append(metrics)
        production_cost = self._estimate_production_cost(metrics)
        cost_gap = market_price - production_cost
        capitulation = self._calculate_capitulation(metrics, market_price, production_cost)
        hr_trend = self._calculate_hashrate_trend()
        diff_phase = self._calculate_difficulty_phase()
        return EnergyCostResult(
            production_cost=production_cost, market_price=market_price,
            cost_gap=cost_gap, miner_capitulation_index=capitulation,
            hash_rate_trend=hr_trend, difficulty_phase=diff_phase,
        )

    def _estimate_production_cost(self, metrics: MiningMetrics) -> float:
        if metrics.hash_rate == 0 or metrics.electricity_cost == 0:
            return 0.0
        efficiency = 30  # J/TH
        energy_per_hash = efficiency / 1e12
        hashes_per_sec = metrics.hash_rate * 1e12
        energy_per_sec = hashes_per_sec * energy_per_hash  # W
        cost_per_sec = energy_per_sec * metrics.electricity_cost / 1000
        btc_per_sec = 1 / (metrics.difficulty * 2**32) if metrics.difficulty > 0 else 0
        if btc_per_sec > 0:
            return cost_per_sec / btc_per_sec
        return 0.0

    def _calculate_capitulation(self, metrics: MiningMetrics, market_price: float, production_cost: float) -> float:
        if production_cost == 0: return 0.0
        profit_margin = (market_price - production_cost) / production_cost
        return min(max(-profit_margin / 2, 0.0), 1.0)

    def _calculate_hashrate_trend(self) -> str:
        if len(self._metrics) < 5: return "stable"
        recent = [m.hash_rate for m in self._metrics[-5:]]
        slope = (recent[-1] - recent[0]) / recent[0] if recent[0] > 0 else 0
        if slope > 0.1: return "increasing"
        if slope < -0.1: return "decreasing"
        return "stable"

    def _calculate_difficulty_phase(self) -> str:
        if len(self._metrics) < 3: return "normal"
        recent = [m.difficulty for m in self._metrics[-3:]]
        changes = [(recent[i] - recent[i-1]) / recent[i-1] if recent[i-1] > 0 else 0
                   for i in range(1, len(recent))]
        avg = np.mean(changes) if changes else 0
        if avg > 0.05: return "increasing"
        if avg < -0.05: return "decreasing"
        return "normal"
