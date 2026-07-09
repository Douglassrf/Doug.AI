"""Market scenario detection for strategy benchmarking."""
from __future__ import annotations

import statistics
from typing import Literal

Scenario = Literal["trending_up", "trending_down", "ranging", "high_volatility", "low_volatility"]


def detect_scenario(prices: list[float]) -> Scenario:
    if len(prices) < 10:
        return "ranging"

    returns = [(prices[i] - prices[i - 1]) / prices[i - 1] if prices[i - 1] else 0.0 for i in range(1, len(prices))]
    vol = statistics.pstdev(returns) if len(returns) > 1 else 0.0
    drift = (prices[-1] - prices[0]) / prices[0] if prices[0] else 0.0

    if vol > 0.002:
        return "high_volatility"
    if vol < 0.0003:
        return "low_volatility"
    if drift > 0.001:
        return "trending_up"
    if drift < -0.001:
        return "trending_down"
    return "ranging"
