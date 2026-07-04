import pytest
from doug_os.discovery.meta_learning_layer import MetaLearningLayer, ModelPerformance, MetaLearningResult


@pytest.fixture
def layer():
    return MetaLearningLayer()


def _make_perf(model_id, model_name, regime, f1, cost_ms=10.0):
    return ModelPerformance(
        model_id=model_id, model_name=model_name, regime=regime,
        f1_score=f1, computational_cost_ms=cost_ms, samples=100,
    )


def test_learn_no_data(layer):
    result = layer.learn()
    assert result.meta_learning_score == 0.0
    assert "insufficient" in result.recommendation.lower() or "data" in result.recommendation.lower()


def test_learn_fills_best_by_regime(layer):
    layer.record_performance(_make_perf("m1", "ModelA", "trending_bull", 0.8))
    layer.record_performance(_make_perf("m2", "ModelB", "trending_bear", 0.9))
    result = layer.learn()
    assert "trending_bull" in result.best_model_by_regime
    assert "trending_bear" in result.best_model_by_regime


def test_best_model_is_highest_f1(layer):
    layer.record_performance(_make_perf("m1", "ModelA", "ranging", 0.6))
    layer.record_performance(_make_perf("m2", "ModelB", "ranging", 0.85))
    result = layer.learn()
    assert result.best_model_by_regime["ranging"] == "m2"


def test_strategy_ranking_sorted_desc(layer):
    layer.record_performance(_make_perf("m1", "ModelA", "trending_bull", 0.5))
    layer.record_performance(_make_perf("m2", "ModelB", "trending_bear", 0.9))
    layer.record_performance(_make_perf("m3", "ModelC", "ranging", 0.7))
    result = layer.learn()
    f1s = [r["average_f1"] for r in result.strategy_ranking]
    assert f1s == sorted(f1s, reverse=True)


def test_meta_learning_score_range(layer):
    layer.record_performance(_make_perf("m1", "ModelA", "trending_bull", 0.75))
    result = layer.learn()
    assert 0.0 <= result.meta_learning_score <= 1.0


def test_recommendation_contains_model_names(layer):
    layer.record_performance(_make_perf("m1", "AlphaBot", "trending_bull", 0.8))
    layer.record_performance(_make_perf("m2", "BetaModel", "crisis", 0.9))
    result = layer.learn()
    assert "AlphaBot" in result.recommendation or "BetaModel" in result.recommendation


def test_to_dict_fields(layer):
    layer.record_performance(_make_perf("m1", "ModelA", "ranging", 0.7))
    result = layer.learn()
    d = result.to_dict()
    assert "best_model_by_regime" in d
    assert "strategy_ranking" in d
    assert "meta_learning_score" in d
    assert "recommendation" in d
    assert "created_at" in d
