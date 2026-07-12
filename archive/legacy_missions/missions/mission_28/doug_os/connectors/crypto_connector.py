"""Crypto data connector.

This module defines a read‑only connector for cryptocurrency price data.  It
implements the ``BaseDataConnector`` interface introduced in the Data
Connector Layer (Missão 21) and exposes a handful of common crypto
instruments.  All prices are static and denominated in USD, as real
connectors will be implemented in futuras missões.

The connector is intentionally simple and side‑effect free: it only
returns quotes and never places orders or mutates state.  Symbols are
case‑insensitive and unknown symbols raise ``KeyError``.
"""

from .data_connector import BaseDataConnector


class CryptoConnector(BaseDataConnector):
    """Read‑only connector returning static crypto quotes.

    The connector provides USD prices for several major crypto assets.  It
    inherits from ``BaseDataConnector`` to ensure a consistent API with
    other data sources (e.g., ForexConnector).  Developers can extend
    ``_prices`` to include additional assets as needed.
    """

    #: Human‑readable name used for registration within ``DataConnectorLayer``.
    name = "crypto"

    #: Static price table for supported crypto symbols (symbol → price in USD).
    _prices: dict[str, float] = {
        "BTCUSD": 50_000.0,
        "ETHUSD": 3_000.0,
        "SOLUSD": 100.0,
        "ADAUSD": 0.50,
        "DOGEUSD": 0.06,
    }

    def get_available_symbols(self) -> list[str]:
        """Return a list of supported symbols.

        Returns
        -------
        list[str]
            The available crypto pairs in uppercase form.
        """
        return list(self._prices.keys())

    def get_price(self, symbol: str) -> float:
        """Return the static price for a crypto asset.

        Parameters
        ----------
        symbol : str
            The symbol to quote, case‑insensitive (e.g., ``"btcusd"``).

        Returns
        -------
        float
            The current price of the requested crypto asset.

        Raises
        ------
        KeyError
            If the symbol is not supported by this connector.
        """
        normalized = symbol.upper()
        if normalized in self._prices:
            return self._prices[normalized]
        raise KeyError(f"Symbol {symbol} not supported by CryptoConnector")