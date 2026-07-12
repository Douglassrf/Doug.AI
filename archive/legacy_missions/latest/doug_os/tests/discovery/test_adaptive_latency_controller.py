import pytest
import numpy as np
from doug_os.discovery.adaptive_latency_controller import AdaptiveLatencyController, LatencyReport


def test_record_and_analyze_returns_latency_report():
    ctrl = AdaptiveLatencyController(max_latency_ms=100.0)
    for v in [10.0, 20.0, 30.0, 40.0, 50.0]:
        ctrl.record_latency("module_a", v)
    reports = ctrl.analyze()
    assert len(reports) == 1
    r = reports[0]
    assert isinstance(r, LatencyReport)
    assert r.module_name == "module_a"
    assert abs(r.avg_latency_ms - 30.0) < 0.01
    assert r.max_latency_ms == 50.0
    assert r.min_latency_ms == 10.0
    assert r.sample_count == 5


def test_latency_above_max_sets_threshold_breached():
    ctrl = AdaptiveLatencyController(max_latency_ms=50.0)
    ctrl.record_latency("mod", 200.0)
    reports = ctrl.analyze()
    assert reports[0].threshold_breached is True


def test_six_consecutive_violations_activates_throttle():
    ctrl = AdaptiveLatencyController(max_latency_ms=100.0)
    for _ in range(6):
        ctrl.record_latency("slow_mod", 200.0)
    assert ctrl.should_throttle("slow_mod") is True


def test_ok_value_after_violations_deactivates_throttle():
    ctrl = AdaptiveLatencyController(max_latency_ms=100.0)
    for _ in range(6):
        ctrl.record_latency("mod", 200.0)
    ctrl.record_latency("mod", 10.0)  # within threshold
    assert ctrl.should_throttle("mod") is False


def test_get_slow_modules_returns_modules_above_threshold():
    ctrl = AdaptiveLatencyController(max_latency_ms=100.0)
    for _ in range(5):
        ctrl.record_latency("slow", 200.0)
    for _ in range(5):
        ctrl.record_latency("fast", 10.0)
    slow = ctrl.get_slow_modules()
    assert "slow" in slow
    assert "fast" not in slow


def test_predict_latency_returns_float_gte_zero():
    ctrl = AdaptiveLatencyController()
    for v in [10, 20, 30, 40, 50, 60]:
        ctrl.record_latency("trend", float(v))
    pred = ctrl.predict_latency("trend")
    assert isinstance(pred, float)
    assert pred >= 0.0


def test_get_recommendation_critical_when_avg_gt_2x_max():
    ctrl = AdaptiveLatencyController(max_latency_ms=100.0)
    for _ in range(5):
        ctrl.record_latency("bad_mod", 250.0)
    rec = ctrl.get_recommendation("bad_mod")
    assert "CRITICAL" in rec


def test_to_dict_serializes_latency_report():
    ctrl = AdaptiveLatencyController()
    ctrl.record_latency("m", 50.0)
    reports = ctrl.analyze()
    d = reports[0].to_dict()
    assert "module_name" in d
    assert "avg_latency_ms" in d
    assert "p95_latency_ms" in d
    assert "threshold_breached" in d
    assert isinstance(d["created_at"], str)
