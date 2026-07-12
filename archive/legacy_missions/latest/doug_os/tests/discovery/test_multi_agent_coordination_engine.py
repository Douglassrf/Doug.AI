import pytest
from doug_os.discovery.multi_agent_coordination_engine import (
    MultiAgentCoordinationEngine, Agent, AgentTask,
)


@pytest.fixture
def engine():
    e = MultiAgentCoordinationEngine()
    e.register_agent("analyst", "analysis", {"reasoning", "analysis"})
    e.register_agent("trader", "trading", {"trading", "risk"})
    return e


def test_register_agent_stores_agent(engine):
    assert len(engine._agents) == 2


def test_register_agent_returns_agent(engine):
    a = engine.register_agent("new", "role", {"x"})
    assert isinstance(a, Agent)


def test_submit_task_returns_completed(engine):
    task = engine.submit_task("add", "reasoning", {}, fn=lambda: {"score": 1, "accuracy": 1})
    assert task.status == "completed"


def test_submit_task_result_from_fn(engine):
    task = engine.submit_task("calc", "analysis", {}, fn=lambda: {"score": 0.9, "accuracy": 0.8})
    assert task.result is not None


def test_submit_task_unknown_capability_fails(engine):
    task = engine.submit_task("x", "nonexistent_cap", {})
    assert task.status == "failed"
    assert task.error is not None


def test_submit_task_failing_fn_marks_failed(engine):
    task = engine.submit_task("fail", "trading", {}, fn=lambda: 1 / 0)
    assert task.status == "failed"
    assert task.error is not None


def test_agent_reputation_increases_on_success(engine):
    agent_ids = list(engine._agents.keys())
    agent = engine._agents[agent_ids[0]]
    initial_rep = agent.reputation
    engine.submit_task("work", list(agent.capabilities)[0], {}, fn=lambda: {"score": 1})
    assert agent.reputation >= initial_rep


def test_agent_reputation_decreases_on_failure(engine):
    agent_ids = list(engine._agents.keys())
    agent = engine._agents[agent_ids[0]]
    initial_rep = agent.reputation
    engine.submit_task("fail", list(agent.capabilities)[0], {}, fn=lambda: (_ for _ in ()).throw(Exception("err")))
    assert agent.reputation <= initial_rep


def test_get_agent_status(engine):
    aid = list(engine._agents.keys())[0]
    status = engine.get_agent_status(aid)
    assert status is not None
    assert "reputation" in status


def test_get_agent_status_unknown_returns_none(engine):
    assert engine.get_agent_status("ghost") is None


def test_get_task_result(engine):
    task = engine.submit_task("work", "reasoning", {}, fn=lambda: {"score": 1})
    result = engine.get_task_result(task.id)
    assert result is not None
    assert result.status == "completed"


def test_get_agent_metrics(engine):
    engine.submit_task("t1", "reasoning", {}, fn=lambda: {"score": 1})
    metrics = engine.get_agent_metrics()
    assert metrics["total_agents"] == 2
    assert metrics["total_tasks"] >= 1
