import pytest
from discovery.agent_reputation_engine import AgentReputationEngine, AgentPerformance, ReputationScore


def test_record_performance():
    engine = AgentReputationEngine()
    perf = engine.record_performance("agent1", accuracy=0.9, reliability=0.85, precision=0.88)
    assert perf.agent_id == "agent1"
    assert perf.accuracy == pytest.approx(0.9)


def test_reputation_computed():
    engine = AgentReputationEngine()
    engine.record_performance("agent1", accuracy=0.9, reliability=0.8, precision=0.85,
                               total_attempts=10, successful_attempts=9)
    rep = engine.get_reputation("agent1")
    assert rep is not None
    assert 0.0 < rep.overall_score <= 1.0


def test_reputation_improves_with_good_data():
    engine = AgentReputationEngine()
    for _ in range(5):
        engine.record_performance("agent1", accuracy=0.95, reliability=0.95, precision=0.95,
                                   total_attempts=1, successful_attempts=1)
    rep = engine.get_reputation("agent1")
    assert rep.overall_score > 0.7


def test_trend_improving():
    engine = AgentReputationEngine()
    for i, acc in enumerate([0.5, 0.6, 0.7, 0.8, 0.9]):
        engine.record_performance("a", accuracy=acc, reliability=acc, precision=acc)
    rep = engine.get_reputation("a")
    assert rep.trend == "improving"


def test_trend_declining():
    engine = AgentReputationEngine()
    for acc in [0.9, 0.8, 0.7, 0.6, 0.5]:
        engine.record_performance("a", accuracy=acc, reliability=acc, precision=acc)
    rep = engine.get_reputation("a")
    assert rep.trend == "declining"


def test_penalize():
    engine = AgentReputationEngine()
    engine.record_performance("a", accuracy=0.9, reliability=0.9, precision=0.9)
    rep = engine.get_reputation("a")
    original = rep.overall_score
    engine.penalize("a", 0.1)
    assert rep.overall_score < original


def test_ranking():
    engine = AgentReputationEngine()
    engine.record_performance("weak", accuracy=0.3, reliability=0.3, precision=0.3)
    engine.record_performance("strong", accuracy=0.95, reliability=0.95, precision=0.95)
    ranking = engine.get_reputation_ranking()
    assert ranking[0].agent_id == "strong"


def test_reputation_to_dict():
    r = ReputationScore(agent_id="a", overall_score=0.8, trend="stable")
    d = r.to_dict()
    assert d["agent_id"] == "a"
    assert d["trend"] == "stable"


def test_reputation_dashboard():
    engine = AgentReputationEngine()
    engine.record_performance("a", accuracy=0.8, reliability=0.8, precision=0.8)
    dash = engine.get_reputation_dashboard()
    assert "total_agents" in dash
    assert dash["total_agents"] == 1
