import pytest
from discovery.reputation_weighted_council import ReputationWeightedCouncil


def _votes(options=("BUY", "BUY", "HOLD")):
    agents = ["A", "B", "C"]
    return [{"agent_id": a, "option": o, "confidence": 0.75}
            for a, o in zip(agents, options)]


def test_basic_deliberation():
    c = ReputationWeightedCouncil()
    c.update_reputation("A", 0.80)
    c.update_reputation("B", 0.90)
    c.update_reputation("C", 0.70)
    d = c.deliberate("test", _votes(["BUY", "BUY", "HOLD"]))
    assert d.decision in ("BUY", "HOLD", "SELL")
    assert 0.0 <= d.confidence <= 1.0


def test_declining_agent_zeroed():
    c = ReputationWeightedCouncil(declining_zero_threshold=0.50)
    c.update_reputation("A", 0.80, trend="stable")
    c.update_reputation("B", 0.90, trend="stable")
    c.update_reputation("C", 0.30, trend="declining")
    d = c.deliberate("test", _votes())
    zeroed = [v for v in d.votes if v.zeroed]
    assert any(v.agent_id == "C" for v in zeroed)
    assert d.zeroed_agents >= 1


def test_declining_above_threshold_not_zeroed():
    c = ReputationWeightedCouncil(declining_zero_threshold=0.50)
    c.update_reputation("A", 0.70, trend="declining")  # above threshold
    d = c.deliberate("test", [{"agent_id": "A", "option": "BUY", "confidence": 0.8}])
    assert not d.votes[0].zeroed


def test_all_agents_zeroed_fallback_hold():
    c = ReputationWeightedCouncil(declining_zero_threshold=0.60, min_active_agents=1)
    c.update_reputation("A", 0.20, trend="declining")
    c.update_reputation("B", 0.15, trend="declining")
    votes = [{"agent_id": "A", "option": "BUY", "confidence": 0.8},
             {"agent_id": "B", "option": "SELL", "confidence": 0.9}]
    d = c.deliberate("test", votes)
    # Active < min_active_agents → HOLD
    assert d.decision == "HOLD"


def test_high_reputation_wins():
    c = ReputationWeightedCouncil()
    c.update_reputation("A", 0.95)
    c.update_reputation("B", 0.30)
    votes = [{"agent_id": "A", "option": "BUY", "confidence": 0.9},
             {"agent_id": "B", "option": "SELL", "confidence": 0.9}]
    d = c.deliberate("test", votes)
    assert d.decision == "BUY"


def test_get_agent_weights():
    c = ReputationWeightedCouncil()
    c.update_reputation("A", 0.85)
    c.update_reputation("B", 0.40, trend="declining")
    weights = c.get_agent_weights()
    assert weights["A"] == 0.85
    assert weights["B"] == 0.0   # declining + below threshold


def test_get_stats():
    c = ReputationWeightedCouncil()
    c.update_reputation("A", 0.80)
    c.deliberate("t1", _votes())
    c.deliberate("t2", _votes())
    stats = c.get_stats()
    assert stats["total"] == 2
    assert "agents_tracked" in stats


def test_conservative_tiebreak():
    c = ReputationWeightedCouncil()
    # Equal weights for BUY and SELL → SELL wins (more conservative)
    c.update_reputation("A", 1.0)
    c.update_reputation("B", 1.0)
    votes = [{"agent_id": "A", "option": "BUY", "confidence": 0.5},
             {"agent_id": "B", "option": "SELL", "confidence": 0.5}]
    d = c.deliberate("tie", votes)
    # Tie → most conservative option
    assert d.decision in ("HOLD", "SELL")


def test_decision_to_dict():
    c = ReputationWeightedCouncil()
    c.update_reputation("A", 0.80)
    d = c.deliberate("t", [{"agent_id": "A", "option": "BUY", "confidence": 0.8}])
    dd = d.to_dict()
    assert "tally" in dd
    assert "zeroed_agents" in dd
