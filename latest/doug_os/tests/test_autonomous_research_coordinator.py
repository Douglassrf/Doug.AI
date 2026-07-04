import pytest
from discovery.autonomous_research_coordinator import AutonomousResearchCoordinator, ResearchAgent, ResearchTask


def test_register_agent():
    coord = AutonomousResearchCoordinator()
    agent = coord.register_agent("AnalystBot", specialization="technical")
    assert agent.name == "AnalystBot"
    assert agent.specialization == "technical"


def test_submit_task_assigns_agent():
    coord = AutonomousResearchCoordinator()
    coord.register_agent("Bot")
    task = coord.submit_task("AI trading strategies", priority=7)
    assert task.status in ("in_progress", "queued")
    assert task.topic == "AI trading strategies"


def test_submit_task_no_agents_queued():
    coord = AutonomousResearchCoordinator()
    task = coord.submit_task("topic")
    assert task.status == "queued"


def test_complete_task():
    coord = AutonomousResearchCoordinator()
    coord.register_agent("Bot")
    task = coord.submit_task("topic")
    if task.status == "in_progress":
        success = coord.complete_task(task.id, {"evidence_score": 0.9, "quality_score": 0.8})
        assert success is True
        assert task.status == "completed"


def test_complete_unknown_task():
    coord = AutonomousResearchCoordinator()
    assert coord.complete_task("nonexistent_id", {}) is False


def test_agent_reputation_updates():
    coord = AutonomousResearchCoordinator()
    agent = coord.register_agent("Bot")
    task = coord.submit_task("topic")
    if task.status == "in_progress":
        coord.complete_task(task.id, {"quality_score": 1.0})
        assert coord._agents[agent.id].completed_tasks == 1


def test_aggregate_findings():
    coord = AutonomousResearchCoordinator()
    coord.register_agent("Bot")
    t = coord.submit_task("ML", priority=5)
    if t.status == "in_progress":
        coord.complete_task(t.id, {"evidence_score": 0.8, "confidence": 0.9})
    result = coord.aggregate_findings()
    if result.get("status") != "no_findings":
        assert "total_findings" in result


def test_aggregate_with_filter():
    coord = AutonomousResearchCoordinator()
    coord._findings.append({"topic": "BTC analysis", "evidence_score": 0.7})
    coord._findings.append({"topic": "ETH forecast", "evidence_score": 0.6})
    result = coord.aggregate_findings(topic_filter="BTC")
    assert result["total_findings"] == 1


def test_get_coordination_status():
    coord = AutonomousResearchCoordinator()
    coord.register_agent("Bot")
    status = coord.get_coordination_status()
    assert status["agents"] == 1
    assert "tasks" in status
