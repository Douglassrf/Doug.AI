import pytest
from discovery.agent_performance_monitor import AgentPerformanceMonitor, PerformanceSnapshot


def test_record_task_success():
    monitor = AgentPerformanceMonitor()
    monitor.record_task("agent1", latency_ms=50.0, success=True)
    assert "agent1" in monitor._latencies
    assert len(monitor._latencies["agent1"]) == 1


def test_latency_sla_breach_generates_alert():
    monitor = AgentPerformanceMonitor(latency_sla_ms=100.0)
    monitor.record_task("agent1", latency_ms=500.0)
    alerts = monitor.get_alerts("agent1")
    assert len(alerts) == 1
    assert alerts[0]["type"] == "latency_sla_breach"


def test_no_alert_within_sla():
    monitor = AgentPerformanceMonitor(latency_sla_ms=500.0)
    monitor.record_task("agent1", latency_ms=100.0)
    assert len(monitor.get_alerts("agent1")) == 0


def test_snapshot_created():
    monitor = AgentPerformanceMonitor()
    monitor.record_task("a", latency_ms=10.0)
    snap = monitor.snapshot("a", tasks_completed=9, tasks_failed=1)
    assert snap.agent_id == "a"
    assert snap.error_rate == pytest.approx(0.1)


def test_error_rate_sla_breach():
    monitor = AgentPerformanceMonitor(error_rate_sla=0.05)
    monitor.snapshot("a", tasks_completed=1, tasks_failed=9)
    alerts = monitor.get_alerts("a")
    breach = [al for al in alerts if al["type"] == "error_rate_sla_breach"]
    assert len(breach) > 0


def test_get_snapshots():
    monitor = AgentPerformanceMonitor()
    monitor.record_task("a", latency_ms=10.0)
    monitor.snapshot("a", tasks_completed=5, tasks_failed=0)
    snaps = monitor.get_snapshots("a")
    assert len(snaps) == 1


def test_is_sla_met_within():
    monitor = AgentPerformanceMonitor(latency_sla_ms=200.0)
    monitor.record_task("a", latency_ms=50.0)
    assert monitor.is_sla_met("a") is True


def test_is_sla_met_breach():
    monitor = AgentPerformanceMonitor(latency_sla_ms=50.0)
    for _ in range(5):
        monitor.record_task("a", latency_ms=200.0)
    assert monitor.is_sla_met("a") is False


def test_get_monitor_dashboard():
    monitor = AgentPerformanceMonitor()
    monitor.record_task("a", latency_ms=10.0)
    monitor.snapshot("a", 10, 0)
    dash = monitor.get_monitor_dashboard()
    assert "monitored_agents" in dash
    assert dash["monitored_agents"] == 1


def test_p99_latency_computed():
    monitor = AgentPerformanceMonitor()
    for i in range(100):
        monitor.record_task("a", latency_ms=float(i))
    snap = monitor.snapshot("a", tasks_completed=100, tasks_failed=0)
    assert snap.p99_latency_ms >= 90.0
