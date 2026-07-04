import pytest
from doug_os.discovery.cognitive_observability_engine import (
    CognitiveObservabilityEngine, Trace, ObservableEvent,
)


@pytest.fixture
def engine():
    return CognitiveObservabilityEngine()


def test_start_trace_returns_trace(engine):
    t = engine.start_trace("buy_signal", "decision_engine")
    assert isinstance(t, Trace)
    assert t.status == "started"


def test_end_trace_sets_completed(engine):
    t = engine.start_trace("op", "mod")
    engine.end_trace(t.id)
    assert engine._traces[t.id].status == "completed"


def test_end_trace_calculates_duration(engine):
    t = engine.start_trace("op", "mod")
    ended = engine.end_trace(t.id)
    assert ended.duration_ms >= 0.0


def test_end_trace_with_error(engine):
    t = engine.start_trace("op", "mod")
    engine.end_trace(t.id, status="failed", error="timeout")
    assert engine._traces[t.id].status == "failed"
    assert engine._traces[t.id].error == "timeout"


def test_end_trace_unknown_returns_none(engine):
    assert engine.end_trace("nonexistent") is None


def test_log_event_returns_event(engine):
    ev = engine.log_event("decision", "risk_module", {"action": "hold"}, severity="info")
    assert isinstance(ev, ObservableEvent)


def test_get_events_filters_by_type(engine):
    engine.log_event("decision", "mod", {})
    engine.log_event("risk", "mod", {})
    decisions = engine.get_events(event_type="decision")
    assert all(e.type == "decision" for e in decisions)


def test_get_events_filters_by_severity(engine):
    engine.log_event("x", "mod", {}, severity="warning")
    engine.log_event("y", "mod", {}, severity="info")
    warnings = engine.get_events(severity="warning")
    assert all(e.severity == "warning" for e in warnings)


def test_get_timeline(engine):
    engine.log_event("a", "mod", {})
    timeline = engine.get_timeline()
    assert len(timeline) >= 1
    assert "timestamp" in timeline[0]


def test_get_trace_tree(engine):
    root = engine.start_trace("root_op", "engine_a")
    child = engine.start_trace("child_op", "engine_b", parent_id=root.id)
    tree = engine.get_trace_tree(root.id)
    ids = [t.id for t in tree]
    assert root.id in ids
    assert child.id in ids


def test_get_observability_dashboard(engine):
    t = engine.start_trace("op", "mod")
    engine.end_trace(t.id)
    engine.log_event("ev", "mod", {}, severity="warning")
    dash = engine.get_observability_dashboard()
    assert dash["total_traces"] >= 1
    assert dash["completed_traces"] >= 1
    assert dash["events_by_severity"]["warning"] >= 1
