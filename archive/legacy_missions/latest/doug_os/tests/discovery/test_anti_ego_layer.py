import pytest
from doug_os.discovery.anti_ego_layer import AntiEgoLayer


@pytest.fixture
def layer():
    return AntiEgoLayer()


STRONG = {"quality": 0.9, "quantity": 15, "independence": True, "consistency": True, "novelty": True}
WEAK = {}


def test_self_score_calculated_correctly(layer):
    r = layer.evaluate("h1", STRONG, WEAK)
    assert r.self_score == pytest.approx(1.0)
    assert r.external_score == pytest.approx(0.0)


def test_humility_gap_equals_self_minus_external(layer):
    r = layer.evaluate("h2", STRONG, WEAK)
    assert r.humility_gap == pytest.approx(r.self_score - r.external_score)


def test_persistence_penalty_increases(layer):
    r1 = layer.evaluate("h3", STRONG, WEAK)
    assert r1.persistence_penalty == pytest.approx(0.0)
    r2 = layer.evaluate("h3", STRONG, WEAK)
    assert r2.persistence_penalty == pytest.approx(0.05)
    r3 = layer.evaluate("h3", STRONG, WEAK)
    assert r3.persistence_penalty == pytest.approx(0.10)


def test_large_gap_recommendation(layer):
    r = layer.evaluate("h4", STRONG, WEAK)
    assert "external validation" in r.recommendation.lower() or "overvaluing" in r.recommendation.lower()


def test_high_penalty_recommendation(layer):
    # call 7 times so penalty > 0.3 and gap is small (equal evidence)
    for _ in range(7):
        r = layer.evaluate("h5", STRONG, STRONG)
    assert "persistence" in r.recommendation.lower() or "alternatives" in r.recommendation.lower()


def test_to_dict_serializes_correctly(layer):
    r = layer.evaluate("h6", STRONG, WEAK)
    d = r.to_dict()
    for key in ["id", "hypothesis_id", "self_score", "external_score",
                "humility_gap", "persistence_penalty", "recommendation", "created_at"]:
        assert key in d
    assert d["hypothesis_id"] == "h6"
