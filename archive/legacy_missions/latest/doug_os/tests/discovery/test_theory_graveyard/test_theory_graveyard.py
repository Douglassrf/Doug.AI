import pytest
from doug_os.discovery.theory_graveyard import TheoryGraveyard, BuriedTheory


@pytest.fixture
def graveyard():
    return TheoryGraveyard()


def test_bury_theory_returns_buried_theory(graveyard):
    buried = graveyard.bury_theory(
        hypothesis="Higher interest rates cause lower inflation",
        failure_reason="p_value was not significant",
    )
    assert isinstance(buried, BuriedTheory)
    assert buried.hypothesis == "Higher interest rates cause lower inflation"
    assert buried.failure_reason == "p_value was not significant"
    assert buried.id.startswith("buried_")


def test_similarity_hash_is_generated(graveyard):
    buried = graveyard.bury_theory(
        hypothesis="More data leads to better models",
        failure_reason="No statistical evidence",
    )
    assert buried.similarity_hash != ""
    assert len(buried.similarity_hash) == 16


def test_similarity_hash_is_deterministic(graveyard):
    h = "Prices increase with demand"
    b1 = graveyard.bury_theory(hypothesis=h, failure_reason="reason A")
    g2 = TheoryGraveyard()
    b2 = g2.bury_theory(hypothesis=h, failure_reason="reason B")
    assert b1.similarity_hash == b2.similarity_hash


def test_search_similar_finds_similar_theory(graveyard):
    graveyard.bury_theory(
        hypothesis="High volume leads to low prices",
        failure_reason="correlation spurious",
    )
    results = graveyard.search_similar("High volume leads to low prices", threshold=0.3)
    assert len(results) >= 1


def test_search_similar_returns_empty_for_unrelated(graveyard):
    graveyard.bury_theory(
        hypothesis="Quantum entanglement affects cognition",
        failure_reason="no mechanism",
    )
    results = graveyard.search_similar("Revenue increases with marketing spend", threshold=0.8)
    assert len(results) == 0


def test_check_duplicate_returns_true_for_identical(graveyard):
    h = "Unemployment causes inflation via wage pressure"
    graveyard.bury_theory(hypothesis=h, failure_reason="not significant")
    assert graveyard.check_duplicate(h) is True


def test_check_duplicate_returns_false_for_different(graveyard):
    graveyard.bury_theory(
        hypothesis="Bears hibernate in winter",
        failure_reason="empirical data inconsistent",
    )
    assert graveyard.check_duplicate("Fish fly in summer") is False


def test_get_failure_patterns_returns_dict(graveyard):
    graveyard.bury_theory("High p_value hypothesis", "significance not met")
    graveyard.bury_theory("Contradictory hypothesis", "logical fallacy detected")
    graveyard.bury_theory("Bad data hypothesis", "empirical evidence missing")
    patterns = graveyard.get_failure_patterns()
    assert isinstance(patterns, dict)
    assert len(patterns) > 0
    assert all(isinstance(v, int) for v in patterns.values())


def test_to_dict_serializes_correctly(graveyard):
    buried = graveyard.bury_theory(
        hypothesis="Sample hypothesis for serialization",
        failure_reason="correlation does not imply causation",
        metadata={"source": "test"},
    )
    d = buried.to_dict()
    assert d["hypothesis"] == "Sample hypothesis for serialization"
    assert d["similarity_hash"] != ""
    assert isinstance(d["lessons_learned"], list)
    assert "buried_at" in d
    assert d["metadata"]["source"] == "test"


def test_exhume_recovers_buried_theory(graveyard):
    buried = graveyard.bury_theory(
        hypothesis="Gravity is a myth",
        failure_reason="contradicted by experiment",
    )
    recovered = graveyard.exhume(buried.id)
    assert recovered is buried


def test_exhume_returns_none_for_missing(graveyard):
    assert graveyard.exhume("nonexistent_id") is None


def test_burial_depth_increases_for_duplicates(graveyard):
    h = "Same hypothesis submitted twice"
    b1 = graveyard.bury_theory(hypothesis=h, failure_reason="first attempt")
    b2 = graveyard.bury_theory(hypothesis=h, failure_reason="second attempt")
    assert b2.burial_depth > b1.burial_depth
