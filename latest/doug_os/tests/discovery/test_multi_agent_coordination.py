import pytest
from doug_os.discovery.multi_agent_coordination import (
    MultiAgentCoordinationEngine, Agent, CoordinationMessage
)


@pytest.fixture
def engine():
    return MultiAgentCoordinationEngine()


def test_register_agent_idle(engine):
    agent = engine.register_agent("Alpha", "planner", ["planning", "analysis"])
    assert isinstance(agent, Agent)
    assert agent.status == "idle"
    assert agent.name == "Alpha"
    assert agent.role == "planner"


def test_get_agents_by_role(engine):
    engine.register_agent("A1", "worker", ["compute"])
    engine.register_agent("A2", "worker", ["memory"])
    engine.register_agent("A3", "manager", ["oversight"])
    workers = engine.get_agents_by_role("worker")
    assert len(workers) == 2
    managers = engine.get_agents_by_role("manager")
    assert len(managers) == 1


def test_get_agents_by_role_empty(engine):
    result = engine.get_agents_by_role("nonexistent_role")
    assert result == []


def test_send_message_creates_and_increments(engine):
    a1 = engine.register_agent("Sender", "worker", [])
    a2 = engine.register_agent("Receiver", "worker", [])
    msg = engine.send_message(a1.id, a2.id, "task_assign", {"task": "do_work"})
    assert isinstance(msg, CoordinationMessage)
    assert msg.from_agent == a1.id
    assert msg.to_agent == a2.id
    assert msg.type == "task_assign"
    summary = engine.get_coordination_summary()
    assert summary["total_messages"] == 1


def test_broadcast_sends_to_all_except_sender(engine):
    a1 = engine.register_agent("Broadcaster", "lead", [])
    a2 = engine.register_agent("R1", "worker", [])
    a3 = engine.register_agent("R2", "worker", [])
    msgs = engine.broadcast(a1.id, "announcement", {"msg": "hello"})
    assert len(msgs) == 2
    recipients = {m.to_agent for m in msgs}
    assert a1.id not in recipients
    assert a2.id in recipients
    assert a3.id in recipients


def test_update_agent_status(engine):
    agent = engine.register_agent("Worker", "worker", [])
    result = engine.update_agent_status(agent.id, "busy")
    assert result is True
    assert agent.status == "busy"


def test_update_agent_status_invalid(engine):
    result = engine.update_agent_status("nonexistent", "busy")
    assert result is False


def test_get_coordination_summary(engine):
    a1 = engine.register_agent("A1", "planner", [])
    a2 = engine.register_agent("A2", "worker", [])
    a3 = engine.register_agent("A3", "worker", [])
    engine.update_agent_status(a2.id, "busy")
    engine.send_message(a1.id, a2.id, "command", {})
    engine.send_message(a1.id, a3.id, "command", {})
    engine.send_message(a2.id, a1.id, "report", {})
    summary = engine.get_coordination_summary()
    assert summary["total_agents"] == 3
    assert summary["total_messages"] == 3
    assert summary["active_agents"] == 1
    assert summary["messages_by_type"]["command"] == 2
    assert summary["messages_by_type"]["report"] == 1
    assert "worker" in summary["agents_by_role"]


def test_to_dict_all_fields(engine):
    agent = engine.register_agent("TestAgent", "analyst", ["data", "ml"])
    d = agent.to_dict()
    for key in ["id", "name", "role", "capabilities", "status", "current_task", "last_active", "created_at"]:
        assert key in d
    assert d["status"] == "idle"
    assert d["current_task"] is None

    a2 = engine.register_agent("Sender", "worker", [])
    msg = engine.send_message(agent.id, a2.id, "ping", {"data": 1}, priority=8)
    md = msg.to_dict()
    for key in ["id", "from_agent", "to_agent", "type", "content", "priority", "created_at"]:
        assert key in md
    assert md["priority"] == 8
