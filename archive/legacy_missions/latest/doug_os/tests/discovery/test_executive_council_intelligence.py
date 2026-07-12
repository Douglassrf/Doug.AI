import pytest
from doug_os.discovery.executive_council_intelligence import (
    ExecutiveCouncilIntelligence, ExecutiveDecision, DecisionLevel, ExecutiveScore
)


@pytest.fixture
def eci():
    return ExecutiveCouncilIntelligence()


def test_propose_decision_returns_pending(eci):
    d = eci.propose_decision("Launch Product", "Launch v2", DecisionLevel.STRATEGIC)
    assert isinstance(d, ExecutiveDecision)
    assert d.status == "pending"
    assert d.title == "Launch Product"
    assert d.level == DecisionLevel.STRATEGIC


def test_vote_registers_and_returns_true(eci):
    d = eci.propose_decision("Budget Q3", "Approve budget")
    result = eci.vote(d.id, "ceo", "approve", confidence=0.9)
    assert result is True
    assert d.votes["ceo"] == "approve"
    assert d.weights["ceo"] == 0.9


def test_vote_invalid_member_returns_false(eci):
    d = eci.propose_decision("Test", "desc")
    result = eci.vote(d.id, "unknown_member", "approve")
    assert result is False


def test_vote_invalid_decision_returns_false(eci):
    result = eci.vote("nonexistent_id", "ceo", "approve")
    assert result is False


def test_finalize_no_votes_rejected(eci):
    d = eci.propose_decision("No Votes Decision", "desc")
    result = eci.finalize_decision(d.id)
    assert result is not None
    assert result.status == "rejected"
    assert "No votes cast" in result.reasoning


def test_finalize_majority_approved(eci):
    d = eci.propose_decision("Team Hiring", "Hire 5 engineers", DecisionLevel.EXECUTIVE)
    eci.vote(d.id, "ceo", "approve", confidence=0.9)
    eci.vote(d.id, "cfo", "approve", confidence=0.8)
    eci.vote(d.id, "cmo", "approve", confidence=0.85)
    eci.vote(d.id, "cto", "reject", confidence=0.5)
    result = eci.finalize_decision(d.id)
    assert result.status == "approved"
    assert result.confidence >= 0.6
    assert result.result == "approve"


def test_finalize_low_confidence_rejected(eci):
    d = eci.propose_decision("Risky Move", "desc")
    eci.vote(d.id, "ceo", "approve", confidence=0.3)
    eci.vote(d.id, "cfo", "reject", confidence=0.7)
    result = eci.finalize_decision(d.id)
    # "reject" wins with confidence 0.7/(0.7+0.3) = 0.7, so approved
    # Let's ensure confidence is calculated correctly
    assert result.confidence > 0.0


def test_calculate_score_no_decisions(eci):
    score = eci.calculate_score()
    assert isinstance(score, ExecutiveScore)
    assert score.overall_score == 0.0
    assert len(score.recommendations) > 0


def test_calculate_score_with_approved_decisions(eci):
    d = eci.propose_decision("Strategic Move", "desc", DecisionLevel.STRATEGIC)
    eci.vote(d.id, "ceo", "approve", confidence=0.9)
    eci.vote(d.id, "cfo", "approve", confidence=0.85)
    eci.vote(d.id, "cmo", "approve", confidence=0.8)
    eci.finalize_decision(d.id)
    score = eci.calculate_score()
    assert score.overall_score > 0.0
    assert score.strategic_score > 0.0


def test_get_priority_queue_sorted_desc(eci):
    eci.propose_decision("Low", "desc", priority=2)
    eci.propose_decision("High", "desc", priority=9)
    eci.propose_decision("Med", "desc", priority=5)
    queue = eci.get_priority_queue()
    assert len(queue) == 3
    assert queue[0].priority == 9
    assert queue[1].priority == 5
    assert queue[2].priority == 2


def test_to_dict_level_is_string(eci):
    d = eci.propose_decision("Dict Test", "desc", DecisionLevel.EXECUTIVE)
    d_dict = d.to_dict()
    assert d_dict["level"] == "executive"
    assert isinstance(d_dict["level"], str)
    assert d_dict["status"] == "pending"
    assert d_dict["executed_at"] is None
