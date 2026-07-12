import pytest
from discovery.agent_consensus_council import AgentConsensusCouncil, AgentVote, CouncilDecision


def test_vote_registered():
    council = AgentConsensusCouncil()
    vote = council.vote("topic1", "agent1", "buy", confidence=0.9)
    assert vote.option == "buy"
    assert "topic1" in council._votes


def test_expertise_applied():
    council = AgentConsensusCouncil()
    council.register_agent_expertise("expert_agent", 1.0)
    vote = council.vote("topic", "expert_agent", "sell", confidence=0.8)
    assert vote.expertise_weight == 1.0


def test_finalize_no_votes():
    council = AgentConsensusCouncil()
    decision = council.finalize_decision("empty_topic")
    assert decision.decision == "no_consensus"
    assert decision.confidence == 0.0


def test_finalize_single_option():
    council = AgentConsensusCouncil()
    council.vote("topic", "a1", "buy", confidence=0.8)
    council.vote("topic", "a2", "buy", confidence=0.9)
    decision = council.finalize_decision("topic")
    assert decision.decision == "buy"
    assert decision.confidence > 0.5


def test_finalize_weighted_choice():
    council = AgentConsensusCouncil()
    council.register_agent_expertise("senior", 1.0)
    council.register_agent_expertise("junior", 0.3)
    council.vote("t", "senior", "buy", confidence=1.0)
    council.vote("t", "junior", "sell", confidence=1.0)
    decision = council.finalize_decision("t")
    assert decision.decision == "buy"


def test_minority_report_generated():
    council = AgentConsensusCouncil()
    council.vote("t", "a1", "buy", confidence=0.8)
    council.vote("t", "a2", "sell", confidence=0.6)
    decision = council.finalize_decision("t")
    assert decision.minority_report is not None


def test_no_minority_when_unanimous():
    council = AgentConsensusCouncil()
    council.vote("t", "a1", "buy", confidence=0.9)
    decision = council.finalize_decision("t")
    assert decision.minority_report is None


def test_council_dashboard():
    council = AgentConsensusCouncil()
    council.vote("t", "a", "buy", confidence=0.9)
    council.finalize_decision("t")
    dash = council.get_council_dashboard()
    assert dash["total_decisions"] == 1
    assert "avg_confidence" in dash


def test_vote_to_dict():
    v = AgentVote(agent_id="a1", option="hold", confidence=0.7)
    d = v.to_dict()
    assert d["option"] == "hold"
    assert d["confidence"] == pytest.approx(0.7)
