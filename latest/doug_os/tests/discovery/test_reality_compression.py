import pytest
from doug_os.discovery.reality_compression import RealityCompressionEngine, CompressionMetrics


def test_normal_data_green():
    engine = RealityCompressionEngine()
    m = engine.analyze({"original_dim": 10, "reduced_dim": 9, "variance_explained": 0.95})
    assert m.alert_level == "green"
    assert m.warning == ""


def test_high_info_loss_red():
    engine = RealityCompressionEngine()
    m = engine.analyze({"original_dim": 10, "reduced_dim": 5, "variance_explained": 0.50})
    assert m.alert_level == "red"
    assert "critical" in m.warning


def test_high_compression_ratio_yellow():
    engine = RealityCompressionEngine()
    # compression_ratio = 1 - (reduced/original) = 1 - (5/10) = 0.5 > 0.3
    # but information_loss = 1 - 0.85 = 0.15 < 0.4
    m = engine.analyze({"original_dim": 10, "reduced_dim": 5, "variance_explained": 0.85})
    assert m.alert_level == "yellow"
    assert "threshold" in m.warning


def test_detect_dangerous_simplification_filters():
    engine = RealityCompressionEngine()
    engine.analyze({"original_dim": 10, "reduced_dim": 9, "variance_explained": 0.99})  # green
    engine.analyze({"original_dim": 10, "reduced_dim": 5, "variance_explained": 0.85})  # yellow
    engine.analyze({"original_dim": 10, "reduced_dim": 3, "variance_explained": 0.50})  # red
    dangerous = engine.detect_dangerous_simplification()
    assert len(dangerous) == 2
    levels = {d["level"] for d in dangerous}
    assert "yellow" in levels
    assert "red" in levels
    assert "green" not in levels


def test_history_accumulates():
    engine = RealityCompressionEngine()
    for i in range(5):
        engine.analyze({"original_dim": 10, "reduced_dim": 8, "variance_explained": 0.9})
    assert len(engine._history) == 5


def test_to_dict_serialization():
    engine = RealityCompressionEngine()
    m = engine.analyze({"original_dim": 10, "reduced_dim": 7, "variance_explained": 0.8})
    d = m.to_dict()
    assert "compression_ratio" in d
    assert "information_loss" in d
    assert "alert_level" in d
    assert "created_at" in d
    assert isinstance(d["alert_level"], str)
