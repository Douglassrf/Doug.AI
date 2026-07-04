import pytest
from doug_os.discovery.cognitive_fault_tolerance import (
    CognitiveFaultTolerance, FaultRecord, HealthStatus,
)


@pytest.fixture
def cft():
    c = CognitiveFaultTolerance()
    c.register_component("decision_engine")
    c.register_component("risk_manager")
    return c


def test_register_component_stores_health(cft):
    assert "decision_engine" in cft._health
    assert cft._health["decision_engine"].status == "healthy"


def test_detect_failure_creates_record(cft):
    fault = cft.detect_failure("decision_engine", "crash", "Process crashed unexpectedly")
    assert isinstance(fault, FaultRecord)
    assert fault.fault_type == "crash"
    assert fault.severity == "critical"


def test_detect_failure_updates_health(cft):
    cft.detect_failure("decision_engine", "crash", "crashed")
    assert cft._health["decision_engine"].status == "failed"


def test_detect_failure_isolates_high_severity(cft):
    cft.detect_failure("decision_engine", "crash", "crashed")
    assert cft.is_component_isolated("decision_engine")


def test_detect_failure_low_severity_not_isolated(cft):
    cft.detect_failure("risk_manager", "network", "network blip")
    assert not cft.is_component_isolated("risk_manager")


def test_recover_component_success(cft):
    cft.detect_failure("decision_engine", "crash", "crashed")
    result = cft.recover_component("decision_engine")
    assert result is True
    assert cft._health["decision_engine"].status == "healthy"
    assert not cft.is_component_isolated("decision_engine")


def test_recover_unregistered_component(cft):
    assert cft.recover_component("nonexistent") is False


def test_get_stability_score_decreases_after_fault(cft):
    initial = cft.get_stability_score("decision_engine")
    cft.detect_failure("decision_engine", "timeout", "timed out")
    assert cft.get_stability_score("decision_engine") < initial


def test_get_stability_score_unknown_component(cft):
    assert cft.get_stability_score("nonexistent") == 1.0


def test_get_failure_analytics_no_faults():
    c = CognitiveFaultTolerance()
    assert c.get_failure_analytics() == {"status": "no_faults"}


def test_get_failure_analytics_with_faults(cft):
    cft.detect_failure("decision_engine", "crash", "crashed")
    cft.detect_failure("risk_manager", "timeout", "timed out")
    analytics = cft.get_failure_analytics()
    assert analytics["total_faults"] == 2
    assert analytics["by_type"]["crash"] == 1
    assert analytics["by_type"]["timeout"] == 1


def test_recovery_action_set_correctly(cft):
    fault = cft.detect_failure("risk_manager", "memory", "OOM")
    assert fault.recovery_action == "clear_cache_and_restart"
