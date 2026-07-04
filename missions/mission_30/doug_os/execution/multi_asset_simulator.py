"""Multi‑asset price simulator (Missão 26).

This module provides a simple simulator for multiple asset classes.  It
generates synthetic price series for a configurable set of instruments,
including Forex pairs, precious metals (gold, silver) and cryptocurrencies.
The simulator is intended for offline testing and does **not** place
orders or interface with external APIs.  Prices evolve via a random
walk with configurable volatility.
"""

from __future__ import annotations

import random
from typing import Dict, Iterable


class MultiAssetSimulator:
    """Simulate price movements for multiple assets.

    Parameters
    ----------
    initial_prices : dict
        A mapping from symbol to starting price.
    volatility : float, optional
        Controls the maximum percentage change per tick (default 0.01 = ±1%).
    seed : int, optional
        If provided, seeds the RNG for deterministic simulations (useful for tests).
    """

    def __init__(self, initial_prices: Dict[str, float], volatility: float = 0.01, seed: int | None = None) -> None:
        self.prices = {symbol.upper(): float(price) for symbol, price in initial_prices.items()}
        self.volatility = float(volatility)
        self._rng = random.Random(seed)

    def get_available_symbols(self) -> Iterable[str]:
        """Return the list of symbols being simulated."""
        return list(self.prices.keys())

    def get_price(self, symbol: str) -> float:
        """Return the current simulated price for the given symbol."""
        symbol = symbol.upper()
        if symbol not in self.prices:
            raise KeyError(symbol)
        return self.prices[symbol]

    def tick(self) -> None:
        """Advance the simulation by one time step.

        Each symbol's price is updated by a random percentage drawn
        uniformly from ``[-volatility, +volatility]`` of its current value.
        Prices are floored at 0.01 to avoid non‑positive values.
        """
        for symbol, price in self.prices.items():
            # percentage change
            pct_change = self._rng.uniform(-self.volatility, self.volatility)
            new_price = price * (1 + pct_change)
            # ensure price doesn't go negative or zero
            self.prices[symbol] = max(0.01, new_price)