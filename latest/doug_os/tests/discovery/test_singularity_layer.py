import pytest
from doug_os.discovery.singularity_layer import IntelligenceSingularityLayer, SingularityAlert


def test_monitor_clean_state_no_alerts():
    layer = IntelligenceSingularityLayer()
    alerts = layer.monitor({
        "latest_hypothesis": "momentum predicts returns",
        "instability_score": 0.1,
        "confidence": 0.7,
        "plausibility": 0.9,
        "complexity_level": 3,
    })
    assert alerts == []


def test_loop_detection_after_five_identical():
    layer = IntelligenceSingularityLayer()
    state = {
        "latest_hypothesis": "same_hyp",
        "instability_score": 0.0,
        "confidence": 0.5,
        "plausibility": 0.8,
        "complexity_level": 2,
    }
    for _ in range(5):
        layer.monitor(state)
    loop_alerts = [a for a in layer._alerts if a.alert_type == "loop"]
    assert len(loop_alerts) >= 1
    assert loop_alerts[-1].severity == 8


def test_instability_alert():
    layer = IntelligenceSingularityLayer()
    alerts = layer.monitor({
        "latest_hypothesis": "x",
        "instability_score": 0.95,
        "confidence": 0.5,
        "plausibility": 0.8,
        "complexity_level": 2,
    })
    inst_alerts = [a for a in alerts if a.alert_type == "instability"]
    assert len(inst_alerts) == 1
    assert inst_alerts[0].severity == 7


def test_hallucination_alert():
    layer = IntelligenceSingularityLayer()
    alerts = layer.monitor({
        "latest_hypothesis": "weird claim",
        "instability_score": 0.0,
        "confidence": 0.99,
        "plausibility": 0.01,
        "complexity_level": 2,
    })
    hall_alerts = [a for a in alerts if a.alert_type == "hallucination"]
    assert len(hall_alerts) == 1
    assert hall_alerts[0].severity == 9


def test_overcomplexity_alert():
    layer = IntelligenceSingularityLayer()
    alerts = layer.monitor({
        "latest_hypothesis": "complex",
        "instability_score": 0.0,
        "confidence": 0.5,
        "plausibility": 0.8,
        "complexity_level": 15,
    })
    comp_alerts = [a for a in alerts if a.alert_type == "overcomplexity"]
    assert len(comp_alerts) == 1
    assert comp_alerts[0].severity == 6


def test_get_active_alerts_filters_by_severity():
    layer = IntelligenceSingularityLayer()
    layer.monitor({"latest_hypothesis": "x", "instability_score": 0.9,
                   "confidence": 0.5, "plausibility": 0.8, "complexity_level": 2})
    all_active = layer.get_active_alerts(min_severity=1)
    high_only = layer.get_active_alerts(min_severity=8)
    assert len(all_active) >= len(high_only)
    for a in high_only:
        assert a.severity >= 8


def test_mitigate_marks_alert():
    layer = IntelligenceSingularityLayer()
    layer.monitor({"latest_hypothesis": "x", "instability_score": 0.95,
                   "confidence": 0.5, "plausibility": 0.8, "complexity_level": 2})
    alert = layer._alerts[0]
    result = layer.mitigate(alert.id, "Reset discovery engine")
    assert result is True
    assert alert.mitigated is True
    assert alert.mitigation_action == "Reset discovery engine"
    # should no longer appear in active
    active = layer.get_active_alerts()
    assert alert not in active
