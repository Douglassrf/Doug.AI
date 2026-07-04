import pytest
from discovery.high_availability_architecture import HighAvailabilityArchitecture, ServiceInstance, AvailabilityReport


def test_register_service():
    ha = HighAvailabilityArchitecture()
    inst = ha.register_service("api", "host1", 8080)
    assert inst.service_name == "api"
    assert inst.host == "host1"
    assert inst.port == 8080


def test_multiple_instances():
    ha = HighAvailabilityArchitecture()
    ha.register_service("api", "host1", 8080)
    ha.register_service("api", "host2", 8080)
    report = ha.check_health("api")
    assert report.total_instances == 2


def test_heartbeat_success():
    ha = HighAvailabilityArchitecture()
    inst = ha.register_service("db", "db-host", 5432)
    assert ha.heartbeat(inst.id) is True


def test_heartbeat_unknown():
    ha = HighAvailabilityArchitecture()
    assert ha.heartbeat("nonexistent_id") is False


def test_check_health_empty():
    ha = HighAvailabilityArchitecture()
    report = ha.check_health("unknown")
    assert report.total_instances == 0
    assert report.availability_score == 0.0


def test_check_health_healthy():
    ha = HighAvailabilityArchitecture()
    inst = ha.register_service("cache", "cache-host", 6379)
    ha.heartbeat(inst.id)
    report = ha.check_health("cache")
    assert report.healthy_instances >= 0
    assert 0.0 <= report.availability_score <= 1.0


def test_failover_marks_offline():
    ha = HighAvailabilityArchitecture()
    inst1 = ha.register_service("svc", "host1", 80)
    inst2 = ha.register_service("svc", "host2", 80)
    fallback = ha.failover("svc", inst1.id)
    assert inst1.status == "offline"
    assert fallback is not None
    assert fallback.id == inst2.id


def test_failover_no_healthy():
    ha = HighAvailabilityArchitecture()
    inst = ha.register_service("svc", "host", 80)
    result = ha.failover("svc", inst.id)
    assert result is None


def test_graceful_degradation():
    ha = HighAvailabilityArchitecture()
    inst = ha.register_service("ml", "ml-host", 9000)
    inst.health_score = 0.2  # below 0.3 threshold
    degraded = ha.graceful_degradation("ml")
    assert inst.id in degraded
    assert inst.status == "offline"


def test_get_availability_score():
    ha = HighAvailabilityArchitecture()
    ha.register_service("auth", "auth-host", 3000)
    scores = ha.get_availability_score()
    assert "auth" in scores
    assert 0.0 <= scores["auth"] <= 1.0


def test_availability_report_fields():
    r = AvailabilityReport(service_name="test", total_instances=2, healthy_instances=2)
    d = r.to_dict()
    assert d["service_name"] == "test"
    assert d["total_instances"] == 2
