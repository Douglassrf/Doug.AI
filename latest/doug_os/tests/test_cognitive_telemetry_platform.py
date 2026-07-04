import pytest
from discovery.cognitive_telemetry_platform import CognitiveTelemetryPlatform, TelemetryPoint


def test_record_metric():
    platform = CognitiveTelemetryPlatform()
    pt = platform.record_metric("cpu_usage", 45.0, source="monitor")
    assert pt.name == "cpu_usage"
    assert pt.value == 45.0
    assert pt.metric_type == "metric"


def test_record_log():
    platform = CognitiveTelemetryPlatform()
    pt = platform.record_log("system started", severity="info")
    assert pt.metric_type == "log"
    assert pt.value == "system started"


def test_get_metric():
    platform = CognitiveTelemetryPlatform()
    platform.record_metric("latency", 10.0)
    platform.record_metric("latency", 20.0)
    vals = platform.get_metric("latency")
    assert vals == [10.0, 20.0]


def test_get_metrics_summary():
    platform = CognitiveTelemetryPlatform()
    platform.record_metric("score", 0.8)
    platform.record_metric("score", 0.9)
    summary = platform.get_metrics_summary()
    assert "score" in summary
    assert summary["score"]["count"] == 2
    assert summary["score"]["min"] == pytest.approx(0.8)
    assert summary["score"]["max"] == pytest.approx(0.9)


def test_get_logs():
    platform = CognitiveTelemetryPlatform()
    platform.record_log("error occurred", severity="error")
    platform.record_log("info message", severity="info")
    errors = platform.get_logs(severity="error")
    assert len(errors) == 1


def test_collect_manual():
    platform = CognitiveTelemetryPlatform()
    pt = TelemetryPoint(source="test", metric_type="metric", name="x", value=5.0)
    platform.collect(pt)
    assert len(platform._points) == 1


def test_max_points_trimmed():
    platform = CognitiveTelemetryPlatform(max_points=5)
    for i in range(10):
        platform.record_metric("x", float(i))
    assert len(platform._points) <= 5


def test_get_dashboard():
    platform = CognitiveTelemetryPlatform()
    platform.record_metric("m", 1.0)
    platform.record_log("log msg")
    dash = platform.get_dashboard()
    assert "total_points" in dash
    assert dash["total_points"] >= 2


def test_telemetry_point_to_dict():
    pt = TelemetryPoint(source="s", metric_type="metric", name="n", value=3.14)
    d = pt.to_dict()
    assert d["name"] == "n"
    assert d["value"] == pytest.approx(3.14)
