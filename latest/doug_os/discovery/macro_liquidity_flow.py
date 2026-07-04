from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import numpy as np
from collections import deque


@dataclass
class LiquidityData:
    timestamp: datetime
    global_liquidity: float = 0.0
    central_bank_balance: float = 0.0
    market_cap: float = 0.0
    volume_24h: float = 0.0
    stablecoin_supply: float = 0.0
    exchange_reserves: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "global_liquidity": self.global_liquidity,
            "central_bank_balance": self.central_bank_balance,
            "market_cap": self.market_cap,
            "volume_24h": self.volume_24h,
            "stablecoin_supply": self.stablecoin_supply,
            "exchange_reserves": self.exchange_reserves,
        }


@dataclass
class LiquidityScore:
    score: float = 0.0
    pressure_index: float = 0.0
    cycle_phase: str = "expansion"
    trend: str = "stable"
    alert_level: str = "green"
    components: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "pressure_index": self.pressure_index,
            "cycle_phase": self.cycle_phase,
            "trend": self.trend,
            "alert_level": self.alert_level,
            "components": self.components,
            "created_at": self.created_at.isoformat(),
        }


class MacroLiquidityFlowEngine:
    def __init__(self, window_size: int = 30):
        self._history: deque = deque(maxlen=window_size)
        self._liquidity_scores: List[LiquidityScore] = []

    def update(self, data: LiquidityData) -> LiquidityScore:
        self._history.append(data)
        components = self._calculate_components(data)
        score = self._calculate_liquidity_score(components)
        pressure = self._calculate_pressure_index(data)
        cycle_phase = self._detect_cycle()
        trend = self._calculate_trend()
        alert_level = self._determine_alert(score, pressure)
        result = LiquidityScore(
            score=score, pressure_index=pressure, cycle_phase=cycle_phase,
            trend=trend, alert_level=alert_level, components=components,
        )
        self._liquidity_scores.append(result)
        return result

    def _calculate_components(self, data: LiquidityData) -> Dict[str, float]:
        return {
            "global_liquidity": min(data.global_liquidity / 100, 1.0) if data.global_liquidity > 0 else 0.5,
            "central_bank": min(data.central_bank_balance / 50, 1.0) if data.central_bank_balance > 0 else 0.5,
            "market_cap": min(data.market_cap / 1000, 1.0) if data.market_cap > 0 else 0.5,
            "volume": min(data.volume_24h / 100, 1.0) if data.volume_24h > 0 else 0.3,
            "stablecoins": min(data.stablecoin_supply / 50, 1.0) if data.stablecoin_supply > 0 else 0.3,
            "reserves": min(data.exchange_reserves / 100, 1.0) if data.exchange_reserves > 0 else 0.5,
        }

    def _calculate_liquidity_score(self, components: Dict[str, float]) -> float:
        weights = {"global_liquidity": 0.30, "central_bank": 0.20, "market_cap": 0.15,
                   "volume": 0.15, "stablecoins": 0.10, "reserves": 0.10}
        return min(max(sum(components.get(k, 0.5) * w for k, w in weights.items()), 0.0), 1.0)

    def _calculate_pressure_index(self, data: LiquidityData) -> float:
        if data.market_cap > 0:
            volume_ratio = data.volume_24h / data.market_cap
            pressure = volume_ratio * 10
        else:
            pressure = 0.0
        stable_pressure = data.stablecoin_supply / 50 if data.stablecoin_supply > 0 else 0
        pressure = (pressure + stable_pressure) / 2
        return min(max((pressure - 0.5) * 2, -1.0), 1.0)

    def _detect_cycle(self) -> str:
        if len(self._history) < 10:
            return "neutral"
        values = [d.global_liquidity for d in self._history]
        ma_short = np.mean(values[-5:])
        ma_long = np.mean(values[-10:])
        if ma_short > ma_long * 1.02:
            return "expansion"
        elif ma_short < ma_long * 0.98:
            return "contraction"
        return "neutral"

    def _calculate_trend(self) -> str:
        if len(self._history) < 5:
            return "stable"
        recent = [d.global_liquidity for d in list(self._history)[-5:]]
        if len(recent) < 2:
            return "stable"
        slope = (recent[-1] - recent[0]) / len(recent)
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        return "stable"

    def _determine_alert(self, score: float, pressure: float) -> str:
        if score < 0.3 or abs(pressure) > 0.8:
            return "red"
        elif score < 0.5 or abs(pressure) > 0.5:
            return "yellow"
        return "green"

    def get_heatmap(self) -> Dict[str, Any]:
        return {
            "global_liquidity": self._history[-1].global_liquidity if self._history else 0,
            "trend": self._calculate_trend(),
            "pressure": self._liquidity_scores[-1].pressure_index if self._liquidity_scores else 0,
        }
