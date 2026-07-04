import pytest
from doug_os.discovery.predictive_resource_manager import (
    PredictiveResourceManager, ResourcePrediction,
)


@pytest.fixture
def manager():
    m = PredictiveResourceManager()
    for i in range(20):
        m.record_usage("cpu", 0.3 + i * 0.01)
        m.record_usage("memory", 0.5 + i * 0.005)
    return m


def test_record_usage_stores_history(manager):
    assert len(manager._history["cpu"]) == 20


def test_record_unknown_resource_ignored():
    m = PredictiveResourceManager()
    m.record_usage("unknown_res", 0.5)  # Should not raise


def test_predict_resource_returns_prediction(manager):
    pred = manager.predict_resource("cpu")
    assert isinstance(pred, ResourcePrediction)


def test_predict_resource_confidence_in_range(manager):
    pred = manager.predict_resource("cpu")
    assert 0.0 <= pred.confidence <= 1.0


def test_predict_resource_predicted_value_positive(manager):
    pred = manager.predict_resource("memory")
    assert pred.predicted_value >= 0.0


def test_predict_resource_insufficient_history():
    m = PredictiveResourceManager()
    m.record_usage("cpu", 0.5)
    pred = m.predict_resource("cpu")
    assert pred.confidence == pytest.approx(0.3)


def test_predict_resource_no_history():
    m = PredictiveResourceManager()
    pred = m.predict_resource("cpu")
    assert pred.predicted_value == 0.0


def test_predict_stores_in_predictions(manager):
    manager.predict_resource("cpu")
    assert len(manager._predictions) >= 1


def test_get_auto_scaling_recommendation(manager):
    recs = manager.get_auto_scaling_recommendation()
    assert isinstance(recs, dict)


def test_get_resource_dashboard_structure(manager):
    dash = manager.get_resource_dashboard()
    assert "resource_types" in dash
    assert "predictions" in dash
    assert "cpu" in dash["resource_types"]


def test_dashboard_trend_values(manager):
    dash = manager.get_resource_dashboard()
    for rt, info in dash["resource_types"].items():
        assert info["trend"] in ("increasing", "decreasing", "stable")
