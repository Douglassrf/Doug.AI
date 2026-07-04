import pytest
from doug_os.discovery.cognitive_benchmark_laboratory import (
    CognitiveBenchmarkLaboratory, BenchmarkResult,
)


@pytest.fixture
def lab():
    return CognitiveBenchmarkLaboratory()


def good_fn():
    return {"score": 0.9, "accuracy": 0.85}


def bad_fn():
    raise RuntimeError("fail")


def test_run_benchmark_returns_result(lab):
    result = lab.run_benchmark("algo_test", "algorithm", good_fn, iterations=3)
    assert isinstance(result, BenchmarkResult)


def test_run_benchmark_score_positive(lab):
    result = lab.run_benchmark("algo_test", "algorithm", good_fn, iterations=3)
    assert result.score > 0.0


def test_run_benchmark_latency_positive(lab):
    result = lab.run_benchmark("lat_test", "latency", good_fn, iterations=3)
    assert result.latency_ms >= 0.0


def test_run_benchmark_confidence_in_range(lab):
    result = lab.run_benchmark("conf_test", "confidence", good_fn, iterations=5)
    assert 0.1 <= result.confidence <= 1.0


def test_run_benchmark_failing_fn_score_zero(lab):
    result = lab.run_benchmark("fail_test", "strategy", bad_fn, iterations=3)
    assert result.score == 0.0


def test_run_benchmark_unknown_category_raises(lab):
    with pytest.raises(ValueError):
        lab.run_benchmark("x", "unknown_cat", good_fn)


def test_get_best_in_category_empty_returns_none(lab):
    assert lab.get_best_in_category("algorithm") is None


def test_get_best_in_category_returns_best(lab):
    lab.run_benchmark("a", "algorithm", good_fn, iterations=3)
    lab.run_benchmark("b", "algorithm", good_fn, iterations=3)
    best = lab.get_best_in_category("algorithm", "score")
    assert best is not None


def test_get_category_ranking_sorted(lab):
    lab.run_benchmark("r1", "risk", good_fn, iterations=2)
    lab.run_benchmark("r2", "risk", good_fn, iterations=2)
    ranking = lab.get_category_ranking("risk", "score")
    scores = [r.score for r in ranking]
    assert scores == sorted(scores, reverse=True)


def test_get_benchmark_dashboard(lab):
    lab.run_benchmark("d1", "accuracy", good_fn, iterations=2)
    dash = lab.get_benchmark_dashboard()
    assert "categories" in dash
    assert dash["categories"]["accuracy"]["total_results"] == 1
