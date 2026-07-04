import pytest
import time
from discovery.system_health_monitor import (
    SystemHealthMonitor, STATUS_HEALTHY, STATUS_DEGRADED,
    STATUS_CRITICAL, STATUS_OFFLINE,
)


def test_register_component():
    mon = SystemHealthMonitor()
    h = mon.register("MarketAgent", "agent")
    assert h.component_id == "MarketAgent"
    assert h.status == STATUS_HEALTHY


def test_heartbeat_healthy():
    mon = SystemHealthMonitor(latency_sla_ms=500.0, error_rate_sla=0.05)
    mon.register("agent1")
    h = mon.heartbeat("agent1", latency_ms=100.0, error_rate=0.01)
    assert h.status == STATUS_HEALTHY


def test_heartbeat_degraded_latency():
    mon = SystemHealthMonitor(latency_sla_ms=500.0)
    mon.register("agent1")
    h = mon.heartbeat("agent1", latency_ms=600.0)
    assert h.status == STATUS_DEGRADED


def test_heartbeat_critical_latency():
    mon = SystemHealthMonitor(latency_sla_ms=500.0)
    mon.register("agent1")
    h = mon.heartbeat("agent1", latency_ms=1600.0)
    assert h.status == STATUS_CRITICAL


def test_heartbeat_critical_error_rate():
    mon = SystemHealthMonitor(error_rate_sla=0.05)
    mon.register("agent1")
    h = mon.heartbeat("agent1", error_rate=0.35)
    assert h.status == STATUS_CRITICAL


def test_generate_report():
    mon = SystemHealthMonitor()
    mon.register("a1")
    mon.register("a2")
    mon.heartbeat("a1", latency_ms=100)
    mon.heartbeat("a2", latency_ms=200)
    report = mon.generate_report()
    assert report.overall_status == STATUS_HEALTHY
    assert report.healthy_count == 2


def test_critical_component_activates_degraded_mode():
    mon = SystemHealthMonitor(latency_sla_ms=500)
    mon.register("critical_agent", is_critical=True)
    mon.heartbeat("critical_agent", latency_ms=2000.0)
    report = mon.generate_report()
    assert report.degraded_mode_active is True
    assert mon.is_degraded_mode is True


def test_record_failure_consecutive():
    mon = SystemHealthMonitor()
    mon.register("flaky")
    mon.record_failure("flaky", "timeout")
    mon.record_failure("flaky", "timeout")
    mon.record_failure("flaky", "timeout")
    h = mon._components["flaky"]
    assert h.status == STATUS_CRITICAL


def test_get_active_alerts():
    mon = SystemHealthMonitor(latency_sla_ms=200)
    mon.register("slow_agent")
    mon.heartbeat("slow_agent", latency_ms=500)
    alerts = mon.get_active_alerts()
    assert len(alerts) >= 1


def test_get_stats():
    mon = SystemHealthMonitor()
    mon.register("a1")
    mon.register("a2")
    stats = mon.get_stats()
    assert stats["total_components"] == 2
    assert "by_status" in stats
