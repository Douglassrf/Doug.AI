import pytest
from discovery.multi_agent_orchestrator import MultiAgentOrchestrator, AgentInfo, AgentTask


def test_register_agent():
    orch = MultiAgentOrchestrator()
    agent = orch.register_agent("Analyst", {"market_analysis", "trend_detection"}, max_tasks=5)
    assert agent.name == "Analyst"
    assert "market_analysis" in agent.capabilities


def test_heartbeat_success():
    orch = MultiAgentOrchestrator()
    agent = orch.register_agent("Bot", {"processing"})
    assert orch.heartbeat(agent.id) is True


def test_heartbeat_unknown():
    orch = MultiAgentOrchestrator()
    assert orch.heartbeat("nonexistent") is False


def test_submit_task():
    orch = MultiAgentOrchestrator()
    task = orch.submit_task("scan", "market_analysis", {"symbol": "BTC"})
    assert task.name == "scan"
    assert task.status == "pending"


def test_dispatch_assigns_and_completes():
    orch = MultiAgentOrchestrator()
    orch.register_agent("Bot", {"analysis"})
    task = orch.submit_task("task1", "analysis", {})
    orch.dispatch_pending()
    assert task.status == "completed"


def test_dispatch_no_capable_agent():
    orch = MultiAgentOrchestrator()
    orch.register_agent("Bot", {"other_cap"})
    task = orch.submit_task("task", "missing_cap", {})
    orch.dispatch_pending()
    assert task.status == "failed"
    assert "No available agent" in (task.error or "")


def test_dispatch_with_fn():
    orch = MultiAgentOrchestrator()
    orch.register_agent("Bot", {"compute"})
    task = orch.submit_task("compute", "compute", {"x": 5}, fn=lambda p: {"result": p["x"] * 2})
    orch.dispatch_pending()
    assert task.result["result"] == 10


def test_capability_routing():
    orch = MultiAgentOrchestrator()
    orch.register_agent("MarketBot", {"market"})
    orch.register_agent("RiskBot", {"risk"})
    t1 = orch.submit_task("t1", "market", {})
    t2 = orch.submit_task("t2", "risk", {})
    orch.dispatch_pending()
    assert t1.assigned_to != t2.assigned_to


def test_get_agent_status():
    orch = MultiAgentOrchestrator()
    agent = orch.register_agent("Bot", {"cap"})
    status = orch.get_agent_status(agent.id)
    assert status["name"] == "Bot"


def test_orchestrator_dashboard():
    orch = MultiAgentOrchestrator()
    orch.register_agent("Bot", {"x"})
    orch.submit_task("t", "x", {})
    orch.dispatch_pending()
    dash = orch.get_orchestrator_dashboard()
    assert dash["total_agents"] == 1
    assert dash["completed_tasks"] >= 1
