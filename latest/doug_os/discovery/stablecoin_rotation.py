from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import numpy as np


@dataclass
class StablecoinFlow:
    timestamp: datetime
    usdt_supply: float = 0.0
    usdc_supply: float = 0.0
    exchange_balance: float = 0.0
    net_flow: float = 0.0
    rotation_index: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "usdt_supply": self.usdt_supply,
            "usdc_supply": self.usdc_supply,
            "exchange_balance": self.exchange_balance,
            "net_flow": self.net_flow,
            "rotation_index": self.rotation_index,
        }


@dataclass
class StablecoinAnalysis:
    total_supply: float = 0.0
    usdt_share: float = 0.0
    usdc_share: float = 0.0
    exchange_ratio: float = 0.0
    pressure_index: float = 0.0
    trend: str = "neutral"
    alert: str = "green"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_supply": self.total_supply,
            "usdt_share": self.usdt_share,
            "usdc_share": self.usdc_share,
            "exchange_ratio": self.exchange_ratio,
            "pressure_index": self.pressure_index,
            "trend": self.trend,
            "alert": self.alert,
            "created_at": self.created_at.isoformat(),
        }


class StablecoinMacroRotation:
    def __init__(self, window_size: int = 30):
        self._flows: List[StablecoinFlow] = []
        self._window_size = window_size

    def update(self, flow: StablecoinFlow) -> StablecoinAnalysis:
        self._flows.append(flow)
        if len(self._flows) > self._window_size:
            self._flows = self._flows[-self._window_size:]
        total = flow.usdt_supply + flow.usdc_supply
        usdt_share = flow.usdt_supply / total if total > 0 else 0.5
        usdc_share = flow.usdc_supply / total if total > 0 else 0.5
        exchange_ratio = flow.exchange_balance / total if total > 0 else 0.0
        pressure = self._calculate_pressure(flow)
        trend = self._calculate_trend()
        alert = self._determine_alert(pressure)
        return StablecoinAnalysis(
            total_supply=total, usdt_share=usdt_share, usdc_share=usdc_share,
            exchange_ratio=exchange_ratio, pressure_index=pressure, trend=trend, alert=alert,
        )

    def _calculate_pressure(self, flow: StablecoinFlow) -> float:
        total = flow.usdt_supply + flow.usdc_supply
        if total == 0: return 0.0
        return min(max(flow.net_flow / total * 10, -1.0), 1.0)

    def _calculate_trend(self) -> str:
        if len(self._flows) < 5: return "neutral"
        avg = np.mean([f.net_flow for f in self._flows[-5:]])
        if avg > 0.1: return "increasing"
        if avg < -0.1: return "decreasing"
        return "neutral"

    def _determine_alert(self, pressure: float) -> str:
        if abs(pressure) > 0.8: return "red"
        if abs(pressure) > 0.5: return "yellow"
        return "green"
