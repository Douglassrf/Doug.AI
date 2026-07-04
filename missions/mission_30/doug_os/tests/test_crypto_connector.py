import pytest

from doug_os.connectors.data_connector import DataConnectorLayer
from doug_os.connectors.crypto_connector import CryptoConnector


def test_crypto_connector_prices():
    """Ensure the CryptoConnector returns expected static prices."""
    layer = DataConnectorLayer()
    layer.register_connector(CryptoConnector())
    # exact match for supported symbols
    assert layer.get_price("BTCUSD") == 50_000.0
    assert layer.get_price("ETHUSD") == 3_000.0
    assert layer.get_price("SOLUSD") == 100.0
    # case‑insensitive lookup
    assert layer.get_price("adausd") == 0.50


def test_crypto_connector_unknown_symbol():
    """Unknown symbols should raise KeyError."""
    layer = DataConnectorLayer()
    layer.register_connector(CryptoConnector())
    with pytest.raises(KeyError):
        layer.get_price("XYZUSD")


def test_connector_precedence():
    """When multiple connectors provide the same symbol, the first one wins."""

    class PartialCrypto(CryptoConnector):
        # override price table to simulate an alternative feed
        _prices = {"BTCUSD": 60_000.0}

    # Register a connector that only knows BTC first, then the full connector
    layer = DataConnectorLayer()
    # Register the connectors in specific order to enforce precedence
    layer.register_connector(PartialCrypto())
    layer.register_connector(CryptoConnector())
    # Should use PartialCrypto for BTC
    assert layer.get_price("BTCUSD") == 60_000.0
    # Should fall back to CryptoConnector for other symbols
    assert layer.get_price("ETHUSD") == 3_000.0