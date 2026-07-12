import pytest
from discovery.multi_model_consensus_engine import MultiModelConsensusEngine, ModelPrediction, ConsensusResult


def test_register_model():
    engine = MultiModelConsensusEngine()
    model_id = engine.register_model("LSTM", weight=1.5)
    assert model_id.startswith("model_")
    assert engine._models[model_id]["name"] == "LSTM"


def test_submit_prediction():
    engine = MultiModelConsensusEngine()
    mid = engine.register_model("LSTM")
    pred = engine.submit_prediction(mid, 0.7, confidence=0.9)
    assert pred.model_id == mid
    assert pred.confidence == 0.9


def test_submit_unknown_model_raises():
    engine = MultiModelConsensusEngine()
    with pytest.raises(ValueError, match="not registered"):
        engine.submit_prediction("bad_id", 0.5, confidence=0.8)


def test_compute_consensus_numeric():
    engine = MultiModelConsensusEngine(min_models=2, confidence_threshold=0.0)
    m1 = engine.register_model("M1", weight=1.0)
    m2 = engine.register_model("M2", weight=1.0)
    p1 = engine.submit_prediction(m1, 1.0, confidence=1.0)
    p2 = engine.submit_prediction(m2, 3.0, confidence=1.0)
    result = engine.compute_consensus([p1, p2])
    assert result.consensus_value == pytest.approx(2.0)


def test_compute_consensus_below_min_models():
    engine = MultiModelConsensusEngine(min_models=3, confidence_threshold=0.0)
    mid = engine.register_model("M1")
    p = engine.submit_prediction(mid, 1.0, confidence=1.0)
    result = engine.compute_consensus([p])
    assert result.consensus_value is None


def test_compute_consensus_confidence_filter():
    engine = MultiModelConsensusEngine(min_models=1, confidence_threshold=0.8)
    mid = engine.register_model("M1")
    p = engine.submit_prediction(mid, 1.0, confidence=0.3)
    result = engine.compute_consensus([p])
    assert result.consensus_value is None


def test_agreement_score_range():
    engine = MultiModelConsensusEngine(min_models=2, confidence_threshold=0.0)
    m1 = engine.register_model("M1")
    m2 = engine.register_model("M2")
    p1 = engine.submit_prediction(m1, 1.0, confidence=1.0)
    p2 = engine.submit_prediction(m2, 1.0, confidence=1.0)
    result = engine.compute_consensus([p1, p2])
    assert 0.0 <= result.agreement_score <= 1.0


def test_categorical_consensus():
    engine = MultiModelConsensusEngine(min_models=2, confidence_threshold=0.0)
    m1 = engine.register_model("M1", weight=2.0)
    m2 = engine.register_model("M2", weight=1.0)
    p1 = engine.submit_prediction(m1, "buy", confidence=1.0)
    p2 = engine.submit_prediction(m2, "sell", confidence=1.0)
    result = engine.compute_consensus([p1, p2])
    assert result.consensus_value == "buy"  # M1 has higher weight


def test_get_consensus_metrics_empty():
    engine = MultiModelConsensusEngine()
    m = engine.get_consensus_metrics()
    assert m["status"] == "no_results"


def test_get_consensus_metrics():
    engine = MultiModelConsensusEngine(min_models=1, confidence_threshold=0.0)
    mid = engine.register_model("M")
    p = engine.submit_prediction(mid, 1.0, confidence=0.9)
    engine.compute_consensus([p])
    m = engine.get_consensus_metrics()
    assert m["total_rounds"] == 1
