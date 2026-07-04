import pytest
from doug_os.discovery.cognitive_resource_scheduler import (
    CognitiveResourceScheduler, ScheduledTask, TaskPriority
)


def test_schedule_returns_task_with_pending_status():
    sched = CognitiveResourceScheduler()
    task = sched.schedule("task1", lambda: 42, TaskPriority.NORMAL)
    assert isinstance(task, ScheduledTask)
    assert task.status == "pending"
    assert task.name == "task1"


def test_run_next_executes_function_and_returns_completed():
    sched = CognitiveResourceScheduler()
    sched.schedule("task1", lambda: 99, TaskPriority.NORMAL)
    result = sched.run_next()
    assert result is not None
    assert result.status == "completed"
    assert result.result == 99


def test_run_next_failing_function_sets_failed_status():
    sched = CognitiveResourceScheduler()

    def boom():
        raise ValueError("oops")

    sched.schedule("bad_task", boom, TaskPriority.NORMAL)
    result = sched.run_next()
    assert result.status == "failed"
    assert "oops" in result.error


def test_real_time_priority_executed_before_normal():
    sched = CognitiveResourceScheduler()
    order = []
    sched.schedule("normal_task", lambda: order.append("normal"), TaskPriority.NORMAL)
    sched.schedule("realtime_task", lambda: order.append("realtime"), TaskPriority.REAL_TIME)
    sched.run_all()
    assert order[0] == "realtime"
    assert order[1] == "normal"


def test_run_all_executes_all_pending_tasks():
    sched = CognitiveResourceScheduler()
    for i in range(5):
        sched.schedule(f"task_{i}", lambda i=i: i, TaskPriority.NORMAL)
    results = sched.run_all()
    assert len(results) == 5
    assert all(t.status == "completed" for t in results)


def test_get_task_returns_task_by_id():
    sched = CognitiveResourceScheduler()
    task = sched.schedule("find_me", lambda: "found", TaskPriority.LOW)
    found = sched.get_task(task.id)
    assert found is task


def test_to_dict_serializes_fields():
    sched = CognitiveResourceScheduler()
    task = sched.schedule("dict_task", lambda: 1, TaskPriority.HIGH)
    sched.run_next()
    d = task.to_dict()
    assert d["name"] == "dict_task"
    assert d["priority"] == TaskPriority.HIGH
    assert d["status"] == "completed"
    assert d["result"] == 1
    assert "scheduled_at" in d
    assert "completed_at" in d


def test_run_next_on_empty_queue_returns_none():
    sched = CognitiveResourceScheduler()
    assert sched.run_next() is None
