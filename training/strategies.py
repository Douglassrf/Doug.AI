"""Paper-trading strategies for DogEye continuous training.

Each strategy maps to Doug.AI mission themes (331 missions ecosystem).
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Callable, Literal

Direction = Literal["buy", "sell", "hold"]


@dataclass(frozen=True)
class StrategySpec:
    id: str
    name: str
    mission_ref: str
    description: str


STRATEGIES: tuple[StrategySpec, ...] = (
    StrategySpec("S01", "Momentum Pulse", "M261", "Adaptive market timing — follow short drift"),
    StrategySpec("S02", "Mean Reversion", "M275", "Fade extremes back to mean"),
    StrategySpec("S03", "Breakout Hunter", "M259", "Opportunity radar — break recent range"),
    StrategySpec("S04", "Trend Rider", "M284", "Orchestrator — ride established trend"),
    StrategySpec("S05", "Scalp Tick", "M301", "Paper launch — quick tick direction"),
    StrategySpec("S06", "Volatility Guard", "M271", "Vol forecast — trade only when vol justifies"),
    StrategySpec("S07", "RSI Proxy", "M280", "Alpha lab — oversold/overbought proxy"),
    StrategySpec("S08", "Range Bound", "M269", "Liquidity matrix — range edges"),
    StrategySpec("S09", "Capital Shield", "M281", "Preservation — conservative, skip noise"),
    StrategySpec("S10", "Meta Blend", "M288", "Meta-cognition — ensemble of simple signals"),
)


def _sma(prices: list[float], n: int) -> float:
    chunk = prices[-n:]
    return sum(chunk) / len(chunk) if chunk else 0.0


def signal_momentum(prices: list[float]) -> Direction:
    if len(prices) < 5:
        return "hold"
    if prices[-1] > prices[-3] > prices[-5]:
        return "buy"
    if prices[-1] < prices[-3] < prices[-5]:
        return "sell"
    return "hold"


def signal_mean_reversion(prices: list[float]) -> Direction:
    if len(prices) < 10:
        return "hold"
    mean = statistics.mean(prices[-10:])
    last = prices[-1]
    if last < mean * 0.999:
        return "buy"
    if last > mean * 1.001:
        return "sell"
    return "hold"


def signal_breakout(prices: list[float]) -> Direction:
    if len(prices) < 15:
        return "hold"
    window = prices[-15:-1]
    hi, lo = max(window), min(window)
    if prices[-1] > hi:
        return "buy"
    if prices[-1] < lo:
        return "sell"
    return "hold"


def signal_trend(prices: list[float]) -> Direction:
    if len(prices) < 20:
        return "hold"
    fast = _sma(prices, 5)
    slow = _sma(prices, 15)
    if fast > slow * 1.0005:
        return "buy"
    if fast < slow * 0.9995:
        return "sell"
    return "hold"


def signal_scalp(prices: list[float]) -> Direction:
    if len(prices) < 3:
        return "hold"
    if prices[-1] > prices[-2]:
        return "buy"
    if prices[-1] < prices[-2]:
        return "sell"
    return "hold"


def signal_volatility(prices: list[float]) -> Direction:
    if len(prices) < 12:
        return "hold"
    rets = [abs(prices[i] - prices[i - 1]) for i in range(-10, 0)]
    if statistics.mean(rets) < statistics.mean([abs(prices[i] - prices[i - 1]) for i in range(1, len(prices))]) * 0.5:
        return "hold"
    return signal_momentum(prices)


def signal_rsi_proxy(prices: list[float]) -> Direction:
    if len(prices) < 14:
        return "hold"
    gains, losses = [], []
    for i in range(-13, 0):
        d = prices[i] - prices[i - 1]
        gains.append(max(d, 0))
        losses.append(abs(min(d, 0)))
    avg_g = sum(gains) / 13 or 1e-9
    avg_l = sum(losses) / 13 or 1e-9
    rsi = 100 - (100 / (1 + avg_g / avg_l))
    if rsi < 35:
        return "buy"
    if rsi > 65:
        return "sell"
    return "hold"


def signal_range(prices: list[float]) -> Direction:
    if len(prices) < 12:
        return "hold"
    window = prices[-12:]
    hi, lo = max(window), min(window)
    mid = (hi + lo) / 2
    last = prices[-1]
    if last <= lo + (mid - lo) * 0.2:
        return "buy"
    if last >= hi - (hi - mid) * 0.2:
        return "sell"
    return "hold"


def signal_capital_shield(prices: list[float]) -> Direction:
    if len(prices) < 8:
        return "hold"
    vol = statistics.pstdev(prices[-8:])
    mean = statistics.mean(prices[-8:])
    if mean and vol / mean > 0.002:
        return "hold"
    return signal_trend(prices)


def signal_meta_blend(prices: list[float]) -> Direction:
    votes: dict[str, int] = {"buy": 0, "sell": 0, "hold": 0}
    for fn in (signal_momentum, signal_mean_reversion, signal_trend, signal_rsi_proxy):
        votes[fn(prices)] += 1
    if votes["buy"] >= 2 and votes["buy"] > votes["sell"]:
        return "buy"
    if votes["sell"] >= 2 and votes["sell"] > votes["buy"]:
        return "sell"
    return "hold"


SIGNAL_FNS: dict[str, Callable[[list[float]], Direction]] = {
    "S01": signal_momentum,
    "S02": signal_mean_reversion,
    "S03": signal_breakout,
    "S04": signal_trend,
    "S05": signal_scalp,
    "S06": signal_volatility,
    "S07": signal_rsi_proxy,
    "S08": signal_range,
    "S09": signal_capital_shield,
    "S10": signal_meta_blend,
}


def evaluate_signal(direction: Direction, entry: float, exit_price: float) -> bool | None:
    """True=win, False=loss, None=hold/skipped."""
    if direction == "hold":
        return None
    move = exit_price - entry
    if direction == "buy":
        return move > 0
    return move < 0
