import pytest
from discovery.hybrid_local_cloud_orchestrator import HybridLocalCloudOrchestrator, ExecutionDecision


def test_route_to_local_when_resources_available():
    orch = HybridLocalCloudOrchestrator()
    orch.update_local_resources(cpu_percent=10.0, memory_percent=10.0)
    decision = orch.route_task("inference", cpu_required=5.0, memory_required=5.0)
    assert decision.target == "local"
    assert decision.estimated_cost == 0.0


def test_route_to_cloud_when_saturated():
    orch = HybridLocalCloudOrchestrator(local_cpu_threshold=50.0)
    orch.update_local_resources(cpu_percent=60.0, memory_percent=20.0)
    decision = orch.route_task("training", cpu_required=20.0, memory_required=5.0)
    assert decision.target == "cloud"
    assert decision.estimated_cost > 0.0


def test_latency_sensitive_prefers_local():
    orch = HybridLocalCloudOrchestrator()
    orch.update_local_resources(cpu_percent=10.0, memory_percent=10.0)
    decision = orch.route_task("realtime", latency_sensitive=True)
    assert decision.target == "local"
    assert decision.estimated_latency_ms < 10.0


def test_cloud_higher_latency():
    orch = HybridLocalCloudOrchestrator(local_cpu_threshold=10.0)
    orch.update_local_resources(cpu_percent=50.0, memory_percent=20.0)
    decision = orch.route_task("batch")
    assert decision.target == "cloud"
    assert decision.estimated_latency_ms > 50.0


def test_get_routing_metrics_empty():
    orch = HybridLocalCloudOrchestrator()
    m = orch.get_routing_metrics()
    assert m["total_tasks"] == 0


def test_routing_metrics_after_tasks():
    orch = HybridLocalCloudOrchestrator()
    orch.update_local_resources(10.0, 10.0)
    orch.route_task("a")
    orch.route_task("b")
    m = orch.get_routing_metrics()
    assert m["total_tasks"] == 2


def test_decision_fields():
    orch = HybridLocalCloudOrchestrator()
    orch.update_local_resources(5.0, 5.0)
    d = orch.route_task("test")
    assert d.task_type == "test"
    assert d.reason != ""


def test_dashboard_contains_metrics():
    orch = HybridLocalCloudOrchestrator()
    orch.update_local_resources(30.0, 20.0)
    orch.route_task("x")
    dash = orch.get_orchestration_dashboard()
    assert "routing_metrics" in dash
    assert "local_resources" in dash


def test_decision_to_dict():
    d = ExecutionDecision(task_type="ml", target="local", reason="ok")
    data = d.to_dict()
    assert data["target"] == "local"
    assert data["task_type"] == "ml"
