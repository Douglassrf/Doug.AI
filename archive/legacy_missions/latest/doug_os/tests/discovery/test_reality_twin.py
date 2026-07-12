import pytest
from doug_os.discovery.reality_twin import RealityTwin


@pytest.fixture
def twin():
    return RealityTwin()


def test_perfect_prediction_no_divergence(twin):
    r = twin.compare({"value": 100}, {"value": 100})
    assert r.error == pytest.approx(0.0)
    assert r.divergence_alert is False


def test_large_error_triggers_divergence_alert(twin):
    r = twin.compare({"value": 100}, {"value": 160})
    assert r.error == pytest.approx(0.6)
    assert r.divergence_alert is True


def test_drift_calculated_correctly(twin):
    twin.compare({"value": 100}, {"value": 110})  # error = 0.1
    r2 = twin.compare({"value": 100}, {"value": 150})  # error = 0.5, drift = 0.4
    assert r2.drift == pytest.approx(0.4)


def test_drift_is_zero_on_first_call(twin):
    r = twin.compare({"value": 100}, {"value": 150})
    assert r.drift == pytest.approx(0.0)


def test_get_alerts_returns_only_divergent(twin):
    twin.compare({"value": 100}, {"value": 100})  # no alert
    twin.compare({"value": 100}, {"value": 200})  # alert
    alerts = twin.get_alerts()
    assert len(alerts) == 1
    assert alerts[0].divergence_alert is True


def test_to_dict_serializes_correctly(twin):
    r = twin.compare({"value": 100}, {"value": 150})
    d = r.to_dict()
    for key in ["prediction", "actual", "error", "drift",
                "divergence_alert", "divergence_reason", "created_at"]:
        assert key in d


def test_explain_divergence_identifies_fields(twin):
    r = twin.compare({"value": 100, "price": 50}, {"value": 200, "price": 100})
    assert r.divergence_alert is True
    assert r.divergence_reason != ""
