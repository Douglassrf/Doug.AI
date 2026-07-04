import pytest
from doug_os.discovery.autonomous_consensus_protocol import (
    AutonomousConsensusProtocol, ConsensusVote, ConsensusResult,
)


@pytest.fixture
def protocol():
    p = AutonomousConsensusProtocol()
    p.register_voter("agent_alpha", weight=2.0)
    p.register_voter("agent_beta", weight=1.0)
    p.register_voter("agent_gamma", weight=1.5)
    p.propose("prop_001", ["buy", "sell", "hold"], {"asset": "BTC"})
    return p


def test_register_voter(protocol):
    assert "agent_alpha" in protocol._voters
    assert protocol._voters["agent_alpha"] == 2.0


def test_vote_returns_consensus_vote(protocol):
    v = protocol.vote("prop_001", "agent_alpha", "buy", confidence=0.9, risk_score=0.1)
    assert isinstance(v, ConsensusVote)
    assert v.option == "buy"


def test_vote_unregistered_voter_raises(protocol):
    with pytest.raises(ValueError):
        protocol.vote("prop_001", "unknown", "buy")


def test_vote_unknown_proposal_raises(protocol):
    with pytest.raises(ValueError):
        protocol.vote("unknown_prop", "agent_alpha", "buy")


def test_finalize_no_votes_returns_no_consensus(protocol):
    protocol.propose("empty_prop", ["a", "b"], {})
    result = protocol.finalize("empty_prop")
    assert result.winner == "no_consensus"


def test_finalize_with_majority(protocol):
    protocol.vote("prop_001", "agent_alpha", "buy", 0.9, 0.1)
    protocol.vote("prop_001", "agent_beta", "buy", 0.8, 0.2)
    protocol.vote("prop_001", "agent_gamma", "sell", 0.7, 0.3)
    result = protocol.finalize("prop_001")
    assert result.winner == "buy"
    assert result.total_votes == 3


def test_finalize_confidence_in_range(protocol):
    protocol.vote("prop_001", "agent_alpha", "buy", 0.9, 0.1)
    result = protocol.finalize("prop_001")
    assert 0.0 <= result.confidence <= 1.0


def test_get_consensus_history(protocol):
    protocol.vote("prop_001", "agent_alpha", "hold", 0.6, 0.3)
    protocol.finalize("prop_001")
    history = protocol.get_consensus_history(limit=5)
    assert len(history) == 1


def test_get_consensus_metrics_no_data():
    p = AutonomousConsensusProtocol()
    assert p.get_consensus_metrics() == {"status": "no_data"}


def test_get_consensus_metrics_after_finalize(protocol):
    protocol.vote("prop_001", "agent_alpha", "buy", 0.9, 0.1)
    protocol.finalize("prop_001")
    metrics = protocol.get_consensus_metrics()
    assert metrics["total_consensos"] == 1
    assert 0.0 <= metrics["avg_confidence"] <= 1.0


def test_votes_distribution_correct(protocol):
    protocol.vote("prop_001", "agent_alpha", "buy", 0.9, 0.1)
    protocol.vote("prop_001", "agent_beta", "sell", 0.7, 0.2)
    protocol.vote("prop_001", "agent_gamma", "buy", 0.8, 0.15)
    result = protocol.finalize("prop_001")
    assert result.votes_distribution.get("buy", 0) == 2
    assert result.votes_distribution.get("sell", 0) == 1
