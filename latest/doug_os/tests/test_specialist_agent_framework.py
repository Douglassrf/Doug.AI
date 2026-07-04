import pytest
from discovery.specialist_agent_framework import (
    BaseSpecialistAgent, MarketAgent, RiskAgent,
    DiscoveryAgent, LearningAgent, AuditAgent, ResearchAgent, AgentExecution,
)


def test_base_agent_execute():
    agent = BaseSpecialistAgent("Base", "base")
    result = agent.execute({"key": "value"})
    assert result.status == "completed"
    assert result.agent_type == "base"


def test_base_agent_duration_set():
    agent = BaseSpecialistAgent("Base", "base")
    result = agent.execute({})
    assert result.duration_ms >= 0.0


def test_base_agent_history():
    agent = BaseSpecialistAgent("Base", "base")
    agent.execute({})
    agent.execute({})
    assert len(agent.get_history()) == 2


def test_market_agent():
    agent = MarketAgent()
    result = agent.execute({"symbol": "BTC"})
    assert result.status == "completed"
    assert "trend" in result.output_data


def test_risk_agent():
    agent = RiskAgent()
    result = agent.execute({"symbol": "ETH"})
    assert result.status == "completed"
    assert "risk_score" in result.output_data
    assert result.output_data["risk_score"] <= 1.0


def test_discovery_agent():
    agent = DiscoveryAgent()
    result = agent.execute({"data": [1, 2, 3]})
    assert result.status == "completed"
    assert "discoveries" in result.output_data


def test_learning_agent():
    agent = LearningAgent()
    result = agent.execute({})
    assert result.status == "completed"
    assert result.output_data.get("model_updated") is True


def test_audit_agent():
    agent = AuditAgent()
    result = agent.execute({})
    assert result.status == "completed"
    assert result.output_data.get("audit_passed") is True


def test_research_agent():
    agent = ResearchAgent()
    result = agent.execute({"topic": "ML"})
    assert result.status == "completed"
    assert "evidence_score" in result.output_data


def test_capabilities_registered():
    m = MarketAgent()
    caps = m.get_capabilities()
    assert "market_analysis" in caps


def test_execution_to_dict():
    agent = MarketAgent()
    ex = agent.execute({})
    d = ex.to_dict()
    assert d["status"] == "completed"
    assert d["agent_type"] == "market"
