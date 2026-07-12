"""Forex data connector for Doug.OS.

This connector provides read‑only access to a small set of foreign
exchange rates.  It implements the `BaseDataConnector` interface
defined in :mod:`doug_os.connectors.data_connector`.  The rates are
static and serve as placeholders; in a production environment, this
connector would query a Forex data provider via API.  Because this
environment is offline, we use hard‑coded values to simulate real
quotes.
"""

from __future__ import annotations

from typing import Iterable

from doug_os.connectors.data_connector import BaseDataConnector


class ForexConnector(BaseDataConnector):
    """Simple Forex connector returning static quotes for major pairs."""

    name = "forex"

    # Predefined exchange rates (USD base or quote depending on pair)
    _rates = {
        "EURUSD": 1.10,
        "USDJPY": 110.50,
        "GBPUSD": 1.30,
        "AUDUSD": 0.75,
        "USDCAD": 1.20,
        "USDCHF": 0.92,
    }

    def get_available_symbols(self) -> Iterable[str]:
        return self._rates.keys()

    def get_price(self, symbol: str) -> float:
        symbol = symbol.upper()
        if symbol not in self._rates:
            raise KeyError(symbol)
        return float(self._rates[symbol])
