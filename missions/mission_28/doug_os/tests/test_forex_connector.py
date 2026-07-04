import pytest

from doug_os.connectors.forex_connector import ForexConnector
from doug_os.connectors.data_connector import DataConnectorLayer


def test_forex_returns_rates():
    """ForexConnector should return predefined rates via the layer."""
    connector = ForexConnector()
    layer = DataConnectorLayer()
    layer.register_connector(connector)
    assert pytest.approx(layer.get_price("EURUSD"), 0.001) == 1.10
    assert pytest.approx(layer.get_price("USDJPY"), 0.001) == 110.50
    assert pytest.approx(layer.get_price("GBPUSD"), 0.001) == 1.30


def test_forex_unknown_pair():
    """Requesting an unknown currency pair should raise KeyError."""
    connector = ForexConnector()
    layer = DataConnectorLayer()
    layer.register_connector(connector)
    with pytest.raises(KeyError):
        layer.get_price("XYZABC")