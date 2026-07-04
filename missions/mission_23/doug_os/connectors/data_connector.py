"""Unified data connector layer for Doug.OS.

This module introduces a base class for read‑only data connectors and a
registry (``DataConnectorLayer``) that aggregates multiple connectors.  The
intent is to standardise how market data (prices, order books, historical
bars) is accessed without coupling the core logic to any particular
exchange API.  All connectors operate in **read‑only** mode: nenhuma
função para enviar ordens ou movimentar dinheiro é exposta.

Example usage::

    layer = DataConnectorLayer()
    layer.register_connector(MockConnector())
    price = layer.get_price("BTCUSD")

Future missions (22 e 23) irão adicionar conectores concretos para Forex
e criptomoedas, implementando os métodos definidos aqui.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Iterable, List


class BaseDataConnector(ABC):
    """Abstract base class for data connectors.

    Concrete connectors should inherit from this class and implement
    ``get_available_symbols`` and ``get_price``.  Methods for order
    execution are intentionally omitted to enforce read‑only behaviour.
    """

    #: Human‑readable name for the connector (e.g., "binance", "forex")
    name: str = "base"

    @abstractmethod
    def get_available_symbols(self) -> Iterable[str]:
        """Return a collection of symbols supported by this connector."""

    @abstractmethod
    def get_price(self, symbol: str) -> float:
        """Return the latest price for the given symbol.

        Should raise ``KeyError`` if the symbol is not supported.
        """


class DataConnectorLayer:
    """Aggregate multiple read‑only data connectors.

    The layer allows the Doug.OS to query prices across different asset
    classes without worrying about the underlying source.  Connectors are
    registered with the ``register_connector`` method and looked up by
    symbol.  If multiple connectors provide the same symbol, the first
    registered connector wins.
    """

    def __init__(self) -> None:
        self._connectors: List[BaseDataConnector] = []

    def register_connector(self, connector: BaseDataConnector) -> None:
        """Register a new data connector.

        Connectors are consulted in registration order when looking up
        symbols.  Duplicate registrations of the same connector are
        permitted but have no effect.
        """
        self._connectors.append(connector)

    def get_price(self, symbol: str) -> float:
        """Return the latest price for ``symbol`` by consulting registered connectors.

        This method iterates through registered connectors in order of
        registration and delegates the price lookup to each connector.
        Connectors may perform their own symbol normalisation (e.g., case
        folding).  If a connector raises ``KeyError`` for an unknown
        symbol, the layer proceeds to the next connector.  Other
        exceptions are ignored to avoid leaking connector‑specific
        failures to the caller.  If no connector can provide a price, a
        ``KeyError`` is raised.
        """
        last_error: Exception | None = None
        for connector in self._connectors:
            try:
                return connector.get_price(symbol)
            except KeyError as e:
                # Symbol not supported by this connector; try next
                last_error = e
                continue
            except Exception as e:
                # Other errors are ignored but stored for debugging
                last_error = e
                continue
        # If none of the connectors returned a price, raise an error
        raise KeyError(f"No connector available for symbol {symbol}") from last_error


class MockPriceConnector(BaseDataConnector):
    """A simple connector for testing that returns fixed prices.

    This mock connector can be used in unit tests to simulate price
    retrieval without relying on external APIs.  It is deliberately
    deterministic so that tests remain reproducible.
    """

    name = "mock"

    def __init__(self, prices: Dict[str, float]) -> None:
        self._prices = {s.upper(): float(p) for s, p in prices.items()}

    def get_available_symbols(self) -> Iterable[str]:
        return self._prices.keys()

    def get_price(self, symbol: str) -> float:
        symbol = symbol.upper()
        if symbol not in self._prices:
            raise KeyError(symbol)
        return self._prices[symbol]
