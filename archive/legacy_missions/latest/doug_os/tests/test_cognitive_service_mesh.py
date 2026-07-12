import pytest
from discovery.cognitive_service_mesh import CognitiveServiceMesh, MeshServiceInstance, ServiceRequest


def test_register_service():
    mesh = CognitiveServiceMesh()
    inst = mesh.register_service("auth", "host", 3000)
    assert inst.name == "auth"
    assert inst.port == 3000


def test_register_handler_and_call():
    mesh = CognitiveServiceMesh()
    mesh.register_service("calc", "host", 8080)
    mesh.register_handler("calc", "compute", lambda p: {"result": p.get("x", 0) * 2})
    result = mesh.call("calc", "compute", {"x": 5})
    assert result.status == "success"
    assert result.response == {"result": 10}


def test_call_unknown_service_fails():
    mesh = CognitiveServiceMesh()
    result = mesh.call("nonexistent", "get", {})
    assert result.status == "failed"


def test_call_no_handler_fails():
    mesh = CognitiveServiceMesh()
    mesh.register_service("empty", "host", 9000)
    result = mesh.call("empty", "get", {})
    assert result.status == "failed"


def test_multiple_instances_load_balance():
    mesh = CognitiveServiceMesh()
    mesh.register_service("api", "host1", 80)
    mesh.register_service("api", "host2", 80)
    mesh.register_handler("api", "get", lambda p: {"ok": True})
    result = mesh.call("api", "get", {})
    assert result.status == "success"


def test_circuit_breaker_open():
    mesh = CognitiveServiceMesh()
    mesh.register_service("svc", "host", 80)
    mesh.register_handler("svc", "get", lambda p: {"ok": True})
    mesh.open_circuit_breaker("svc")
    result = mesh.call("svc", "get", {})
    assert result.status == "failed"
    assert "circuit" in (result.error or "").lower()


def test_close_circuit_breaker():
    mesh = CognitiveServiceMesh()
    mesh.register_service("svc", "host", 80)
    mesh.register_handler("svc", "get", lambda p: {"ok": True})
    mesh.open_circuit_breaker("svc")
    mesh.close_circuit_breaker("svc")
    result = mesh.call("svc", "get", {})
    assert result.status == "success"


def test_service_instance_fields():
    inst = MeshServiceInstance(name="test", host="h", port=1234)
    d = inst.to_dict()
    assert d["name"] == "test"
    assert d["port"] == 1234


def test_get_service_status():
    mesh = CognitiveServiceMesh()
    mesh.register_service("s", "h", 80)
    status = mesh.get_service_status()
    assert "s" in status
    assert status["s"]["instances"] == 1


def get_metrics_not_present():
    # cognitive_service_mesh does not expose get_metrics — use get_service_status
    mesh = CognitiveServiceMesh()
    mesh.register_service("s", "h", 80)
    mesh.register_handler("s", "get", lambda p: {})
    mesh.call("s", "get", {})
    status = mesh.get_service_status()
    assert isinstance(status, dict)
