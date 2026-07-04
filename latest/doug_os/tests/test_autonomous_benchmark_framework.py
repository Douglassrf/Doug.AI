import pytest
from discovery.autonomous_benchmark_framework import AutonomousBenchmarkFramework, BenchmarkSuite, BenchmarkRun


def test_create_suite():
    fw = AutonomousBenchmarkFramework()
    suite = fw.create_suite("Inference Bench", description="Test inference speed")
    assert suite.name == "Inference Bench"
    assert suite.id in fw._suites


def test_run_benchmark():
    fw = AutonomousBenchmarkFramework()
    suite = fw.create_suite("S1")
    run = fw.run_benchmark(suite.id, "noop", lambda: None, iterations=5)
    assert run.benchmark_name == "noop"
    assert run.iterations == 5
    assert run.avg_latency_ms >= 0.0


def test_run_benchmark_score_range():
    fw = AutonomousBenchmarkFramework()
    suite = fw.create_suite("S")
    run = fw.run_benchmark(suite.id, "test", lambda: sum(range(100)), iterations=10)
    assert 0.0 <= run.score <= 1.0


def test_set_and_compare_baseline():
    fw = AutonomousBenchmarkFramework()
    suite = fw.create_suite("S")
    run = fw.run_benchmark(suite.id, "bench", lambda: None, iterations=5)
    fw.set_baseline("bench", run.score * 0.5)
    comparison = fw.compare_to_baseline(run)
    assert comparison["improved"] is True


def test_compare_no_baseline():
    fw = AutonomousBenchmarkFramework()
    suite = fw.create_suite("S")
    run = fw.run_benchmark(suite.id, "bench", lambda: None, iterations=3)
    result = fw.compare_to_baseline(run)
    assert result["status"] == "no_baseline"


def test_regression_detected():
    fw = AutonomousBenchmarkFramework()
    suite = fw.create_suite("S")
    run = fw.run_benchmark(suite.id, "bench", lambda: None, iterations=3)
    fw.set_baseline("bench", run.score + 0.2)  # baseline much better
    comparison = fw.compare_to_baseline(run)
    assert comparison["regression"] is True


def test_get_framework_report_empty():
    fw = AutonomousBenchmarkFramework()
    report = fw.get_framework_report()
    assert report["runs"] == 0
    assert report["avg_score"] == 0.0


def test_get_framework_report():
    fw = AutonomousBenchmarkFramework()
    suite = fw.create_suite("S")
    fw.run_benchmark(suite.id, "b1", lambda: None, iterations=3)
    fw.run_benchmark(suite.id, "b2", lambda: None, iterations=3)
    report = fw.get_framework_report()
    assert report["runs"] == 2
    assert "recent_runs" in report


def test_run_to_dict():
    run = BenchmarkRun(suite_id="s", benchmark_name="b", iterations=5, score=0.8)
    d = run.to_dict()
    assert d["benchmark_name"] == "b"
    assert d["score"] == pytest.approx(0.8)
