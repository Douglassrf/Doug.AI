import pytest
from doug_os.discovery.autonomous_research_sandbox import AutonomousResearchSandbox, ResearchTask


@pytest.fixture
def sandbox():
    return AutonomousResearchSandbox(timeout_seconds=5)


def test_submit_task_completed(sandbox):
    task = sandbox.submit_task("test", "desc", lambda: 42)
    assert task.status == "completed"


def test_submit_task_result_data(sandbox):
    task = sandbox.submit_task("test", "desc", lambda: {"value": 99})
    assert task.result["data"] == {"value": 99}


def test_submit_task_exception_fails(sandbox):
    def bad_func():
        raise ValueError("boom")
    task = sandbox.submit_task("bad", "desc", bad_func)
    assert task.status == "failed"
    assert "boom" in task.error


def test_get_task_returns_correct(sandbox):
    task = sandbox.submit_task("find_me", "desc", lambda: 1)
    fetched = sandbox.get_task(task.id)
    assert fetched is task


def test_get_completed_tasks(sandbox):
    t1 = sandbox.submit_task("ok", "desc", lambda: 1)
    t2 = sandbox.submit_task("bad", "desc", lambda: 1 / 0)
    completed = sandbox.get_completed_tasks()
    assert t1 in completed
    assert t2 not in completed


def test_get_report_success_rate(sandbox):
    sandbox.submit_task("ok", "desc", lambda: 1)
    sandbox.submit_task("bad", "desc", lambda: 1 / 0)
    report = sandbox.get_report()
    assert report["total_tasks"] == 2
    assert report["completed"] == 1
    assert report["failed"] == 1
    assert abs(report["success_rate"] - 0.5) < 1e-9


def test_to_dict_fields(sandbox):
    task = sandbox.submit_task("t", "d", lambda: "x")
    d = task.to_dict()
    assert d["status"] == "completed"
    assert d["started_at"] is not None
    assert d["completed_at"] is not None
    assert "id" in d
    assert "name" in d
