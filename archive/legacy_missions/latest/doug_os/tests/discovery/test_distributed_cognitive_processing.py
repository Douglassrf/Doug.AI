import pytest
from doug_os.discovery.distributed_cognitive_processing import (
    DistributedCognitiveProcessing, CognitiveNode, DistributedTask
)


@pytest.fixture
def dcp():
    return DistributedCognitiveProcessing()


def test_register_node_active(dcp):
    node = dcp.register_node("node-alpha", ["reasoning", "memory"])
    assert isinstance(node, CognitiveNode)
    assert node.status == "active"
    assert node.name == "node-alpha"
    assert "reasoning" in node.capabilities


def test_submit_task_completed(dcp):
    dcp.register_node("worker", ["compute"])
    task = dcp.submit_task("add", lambda x, y: x + y, 5, None, 3, 4)
    assert task.status == "completed"
    assert task.result == 7
    assert task.started_at is not None
    assert task.completed_at is not None


def test_submit_task_exception_failed(dcp):
    dcp.register_node("worker", ["compute"])
    def bad_func():
        raise RuntimeError("deliberate error")
    task = dcp.submit_task("bad", bad_func)
    assert task.status == "failed"
    assert "deliberate error" in task.error


def test_submit_task_no_nodes_raises(dcp):
    with pytest.raises(ValueError, match="No available node found"):
        dcp.submit_task("orphan", lambda: None)


def test_node_capability_filters(dcp):
    dcp.register_node("general", ["compute"])
    dcp.register_node("specialist", ["vision", "compute"])
    # Submit task requiring "vision" capability
    task = dcp.submit_task("vision-task", lambda: "ok", 5, "vision")
    assert task.status == "completed"
    # The node selected must have "vision"
    node = dcp._nodes[task.node_id]
    assert "vision" in node.capabilities


def test_node_capability_not_found_raises(dcp):
    dcp.register_node("general", ["compute"])
    with pytest.raises(ValueError):
        dcp.submit_task("task", lambda: None, 5, "nonexistent_cap")


def test_update_node_health(dcp):
    node = dcp.register_node("healthy", ["ping"])
    old_heartbeat = node.last_heartbeat
    import time; time.sleep(0.01)
    result = dcp.update_node_health(node.id)
    assert result is True
    assert node.last_heartbeat >= old_heartbeat


def test_update_node_health_invalid(dcp):
    result = dcp.update_node_health("nonexistent_node")
    assert result is False


def test_get_task_status_dict(dcp):
    dcp.register_node("worker", ["compute"])
    task = dcp.submit_task("status-test", lambda: 42)
    status = dcp.get_task_status(task.id)
    assert isinstance(status, dict)
    assert status["status"] == "completed"
    assert status["result"] == 42
    assert "id" in status
    assert "node_id" in status
    assert "created_at" in status


def test_get_task_status_not_found(dcp):
    result = dcp.get_task_status("fake_task_id")
    assert result is None


def test_get_node_status_returns_dict(dcp):
    dcp.register_node("n1", ["a"])
    dcp.register_node("n2", ["b"])
    status = dcp.get_node_status()
    assert len(status) == 2
    for nid, ndict in status.items():
        assert "id" in ndict
        assert "status" in ndict
