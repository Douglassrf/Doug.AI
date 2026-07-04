import pytest
from doug_os.discovery.cognitive_performance_optimizer import (
    CognitivePerformanceOptimizer,
    PerformanceMetric,
    OptimizationRecommendation,
)


def make_optimizer():
    return CognitivePerformanceOptimizer()


def test_record_metric_creates_performance_metric_with_correct_alert_level():
    opt = make_optimizer()
    m = opt.record_metric("mod_a", "cpu", 50.0, threshold=80.0)
    assert isinstance(m, PerformanceMetric)
    assert m.module == "mod_a"
    assert m.metric_type == "cpu"
    assert m.value == 50.0
    assert m.alert_level == "green"


def test_record_metric_above_threshold_alert_red():
    opt = make_optimizer()
    m = opt.record_metric("mod_b", "memory", 90.0, threshold=80.0)
    assert m.alert_level == "red"


def test_record_metric_yellow_zone():
    opt = make_optimizer()
    # threshold*0.75 = 60, value=65 -> yellow
    m = opt.record_metric("mod_c", "cpu", 65.0, threshold=80.0)
    assert m.alert_level == "yellow"


def test_get_metrics_filters_by_module():
    opt = make_optimizer()
    opt.record_metric("alpha", "cpu", 10.0)
    opt.record_metric("beta", "cpu", 20.0)
    opt.record_metric("alpha", "memory", 30.0)
    result = opt.get_metrics(module="alpha")
    assert all(m.module == "alpha" for m in result)
    assert len(result) == 2


def test_get_metrics_filters_by_metric_type():
    opt = make_optimizer()
    opt.record_metric("alpha", "cpu", 10.0)
    opt.record_metric("alpha", "memory", 20.0)
    result = opt.get_metrics(metric_type="cpu")
    assert all(m.metric_type == "cpu" for m in result)
    assert len(result) == 1


def test_get_recommendations_filters_by_priority_threshold():
    opt = make_optimizer()
    opt._recommendations.append(OptimizationRecommendation(priority=3, implemented=False))
    opt._recommendations.append(OptimizationRecommendation(priority=8, implemented=False))
    result = opt.get_recommendations(priority_threshold=5)
    assert all(r.priority >= 5 for r in result)
    assert len(result) == 1


def test_implement_recommendation_valid_id():
    opt = make_optimizer()
    rec = OptimizationRecommendation(priority=5)
    opt._recommendations.append(rec)
    result = opt.implement_recommendation(rec.id)
    assert result is True
    assert rec.implemented is True


def test_implement_recommendation_invalid_id_returns_false():
    opt = make_optimizer()
    result = opt.implement_recommendation("does_not_exist")
    assert result is False


def test_get_performance_summary_with_metrics_has_avg_cpu():
    opt = make_optimizer()
    opt.record_metric("system", "cpu", 40.0)
    opt.record_metric("system", "cpu", 60.0)
    opt.record_metric("system", "memory", 50.0)
    summary = opt.get_performance_summary()
    assert "avg_cpu" in summary
    assert abs(summary["avg_cpu"] - 50.0) < 1e-6


def test_get_performance_summary_no_metrics_returns_no_data():
    opt = make_optimizer()
    summary = opt.get_performance_summary()
    assert summary == {"status": "no_data"}
