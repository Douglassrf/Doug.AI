import pytest

from doug_os.connectors.data_connector import DataConnectorLayer, MockPriceConnector


def test_mock_connector_returns_price():
    """Layer should return the price from a registered mock connector."""
    connector = MockPriceConnector({"BTCUSD": 10000.0, "ETHUSD": 2500.0})
    layer = DataConnectorLayer()
    layer.register_connector(connector)
    assert layer.get_price("BTCUSD") == 10000.0
    assert layer.get_price("ETHUSD") == 2500.0
    with pytest.raises(KeyError):
        layer.get_price("SOLUSD")


def test_layer_order_precedence():
    """When multiple connectors support the same symbol, the first one wins."""
    c1 = MockPriceConnector({"BTCUSD": 10000.0})
    c2 = MockPriceConnector({"BTCUSD": 20000.0})
    layer = DataConnectorLayer()
    layer.register_connector(c1)
    layer.register_connector(c2)
    # The layer returns the price from the first registered connector (c1)
    assert layer.get_price("BTCUSD") == 10000.0