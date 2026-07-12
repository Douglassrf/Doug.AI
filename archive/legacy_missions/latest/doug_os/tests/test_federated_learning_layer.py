import pytest
from discovery.federated_learning_layer import FederatedLearningLayer, FederatedModel, ModelUpdate


def test_create_model():
    fl = FederatedLearningLayer()
    model = fl.create_model("price_predictor", {"w1": 0.5, "w2": 0.3})
    assert model.name == "price_predictor"
    assert "w1" in model.global_weights


def test_submit_update_valid_privacy():
    fl = FederatedLearningLayer(privacy_threshold=0.7)
    model = fl.create_model("m", {"w": 1.0})
    update = fl.submit_update(model.id, "node1", {"w": 1.1}, {"accuracy": 0.9}, privacy_score=0.8)
    assert update.node_id == "node1"
    assert update.privacy_score == 0.8


def test_submit_update_low_privacy_rejected():
    fl = FederatedLearningLayer(privacy_threshold=0.7)
    model = fl.create_model("m", {"w": 1.0})
    with pytest.raises(ValueError, match="Privacy score"):
        fl.submit_update(model.id, "node1", {"w": 1.1}, {}, privacy_score=0.5)


def test_submit_update_unknown_model():
    fl = FederatedLearningLayer()
    with pytest.raises(ValueError, match="not found"):
        fl.submit_update("bad_id", "node1", {}, {}, privacy_score=0.9)


def test_aggregate_averages_weights():
    fl = FederatedLearningLayer(privacy_threshold=0.0)
    model = fl.create_model("m", {"w": 0.0})
    fl.submit_update(model.id, "n1", {"w": 1.0}, {}, privacy_score=0.5)
    fl.submit_update(model.id, "n2", {"w": 3.0}, {}, privacy_score=0.5)
    result = fl.aggregate(model.id)
    assert result["status"] == "success"
    assert result["aggregated_weights"]["w"] == pytest.approx(2.0)


def test_aggregate_clears_updates():
    fl = FederatedLearningLayer(privacy_threshold=0.0)
    model = fl.create_model("m", {"w": 0.0})
    fl.submit_update(model.id, "n1", {"w": 1.0}, {}, privacy_score=0.5)
    fl.aggregate(model.id)
    assert len(model.local_updates) == 0


def test_aggregate_no_updates():
    fl = FederatedLearningLayer()
    model = fl.create_model("empty", {})
    result = fl.aggregate(model.id)
    assert result["status"] == "no_updates"


def test_aggregate_increments_count():
    fl = FederatedLearningLayer(privacy_threshold=0.0)
    model = fl.create_model("m", {"w": 1.0})
    fl.submit_update(model.id, "n1", {"w": 2.0}, {}, privacy_score=0.5)
    fl.aggregate(model.id)
    assert model.aggregation_count == 1


def test_get_model_metrics():
    fl = FederatedLearningLayer(privacy_threshold=0.0)
    model = fl.create_model("m", {"w": 1.0})
    fl.submit_update(model.id, "n1", {"w": 2.0}, {"accuracy": 0.9}, privacy_score=0.5)
    metrics = fl.get_model_metrics(model.id)
    assert "version" in metrics
