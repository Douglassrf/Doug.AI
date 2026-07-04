import pytest
from doug_os.discovery.belief_market import BeliefMarket


@pytest.fixture
def market():
    return BeliefMarket()


def test_create_belief_probability_equals_prior(market):
    b = market.create_belief("h1", prior=0.7)
    assert b.probability == pytest.approx(0.7)
    assert b.prior == pytest.approx(0.7)


def test_update_belief_high_likelihood_increases_probability(market):
    market.create_belief("h2", prior=0.5)
    b = market.update_belief("h2", {"likelihood": 0.9})
    assert b.probability > 0.5


def test_update_belief_low_likelihood_decreases_probability(market):
    market.create_belief("h3", prior=0.5)
    b = market.update_belief("h3", {"likelihood": 0.1})
    assert b.probability < 0.5


def test_compete_normalizes_to_one(market):
    market.create_belief("h4", prior=0.6)
    market.create_belief("h5", prior=0.4)
    result = market.compete(["h4", "h5"])
    assert sum(result.values()) == pytest.approx(1.0)


def test_get_belief_value_unknown_returns_default(market):
    val = market.get_belief_value("unknown_hyp")
    assert val == pytest.approx(0.5)


def test_update_belief_missing_hypothesis_returns_none(market):
    result = market.update_belief("nonexistent", {"likelihood": 0.8})
    assert result is None


def test_to_dict_serializes_all_fields(market):
    b = market.create_belief("h6", prior=0.6)
    d = b.to_dict()
    for key in ["id", "hypothesis_id", "probability", "prior", "posterior",
                "confidence", "liquidity", "last_updated", "created_at"]:
        assert key in d
    assert d["hypothesis_id"] == "h6"
