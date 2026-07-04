import pytest
from doug_os.discovery.distributed_intelligence_fabric import (
    DistributedIntelligenceFabric, CognitiveNode,
)


@pytest.fixture
def fabric():
    f = DistributedIntelligenceFabric()
    f.register_node("node_a", {"reasoning", "analysis"}, max_tasks=5)
    f.register_node("node_b", {"trading", "risk"}, max_tasks=3)
    return f


def test_register_node(fabric):
    assert len(fabric._nodes) == 2


def test_register_node_status_active(fabric):
    for node in fabric._nodes.values():
        assert node.status == "active"


def test_submit_task_completes(fabric):
    task = fabric.submit_task("add", lambda: 1 + 1)
    assert task.status == "completed"
    assert task.result == 2


def test_submit_task_with_capability(fabric):
    task = fabric.submit_task("trade", lambda: "executed", required_capability="trading")
    assert task.status == "completed"
    assert task.node_id in fabric._nodes


def test_submit_task_wrong_capability_raises(fabric):
    with pytest.raises(ValueError):
        fabric.submit_task("x", lambda: None, required_capability="nonexistent_cap")


def test_submit_task_no_nodes_raises():
    f = DistributedIntelligenceFabric()
    with pytest.raises(ValueError):
        f.submit_task("x", lambda: None)


def test_submit_task_failing_function(fabric):
    task = fabric.submit_task("fail", lambda: 1 / 0)
    assert task.status == "failed"
    assert task.error is not None


def test_get_task_status(fabric):
    task = fabric.submit_task("work", lambda: 42)
    status = fabric.get_task_status(task.id)
    assert status is not None
    assert status["status"] == "completed"


def test_get_task_status_missing(fabric):
    assert fabric.get_task_status("nonexistent") is None


def test_get_fabric_metrics(fabric):
    fabric.submit_task("t1", lambda: 1)
    fabric.submit_task("t2", lambda: 2)
    metrics = fabric.get_fabric_metrics()
    assert metrics["total_tasks"] == 2
    assert metrics["completed_tasks"] == 2
    assert metrics["success_rate"] == 1.0


def test_update_node_health(fabric):
    node_id = list(fabric._nodes.keys())[0]
    result = fabric.update_node_health(node_id)
    assert result is True


def test_update_node_health_invalid(fabric):
    assert fabric.update_node_health("nonexistent") is False
