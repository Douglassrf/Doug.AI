import pytest
from doug_os.discovery.doubt_engine import DoubtEngine


@pytest.fixture
def engine():
    return DoubtEngine()


WEAK_EVIDENCE = {"sample_size": 10, "reproducible": False, "independent_validation": False, "peer_reviewed": False, "quality": 0.3}
STRONG_EVIDENCE = {"sample_size": 1000, "reproducible": True, "independent_validation": True, "peer_reviewed": True, "quality": 0.9}


def test_weak_evidence_populates_gaps(engine):
    hyp = {"id": "h1"}
    a = engine.analyze(hyp, WEAK_EVIDENCE)
    assert len(a.evidence_gaps) >= 3


def test_high_confidence_hypothesis_generates_adversarial(engine):
    hyp = {"id": "h2", "confidence": 0.9}
    a = engine.analyze(hyp, STRONG_EVIDENCE)
    assert len(a.adversarial_arguments) >= 1
    assert any("confidence" in arg.lower() for arg in a.adversarial_arguments)


def test_doubt_score_increases_with_gaps(engine):
    hyp_weak = {"id": "h3"}
    hyp_strong = {"id": "h4"}
    a_weak = engine.analyze(hyp_weak, WEAK_EVIDENCE)
    a_strong = engine.analyze(hyp_strong, STRONG_EVIDENCE)
    assert a_weak.doubt_score > a_strong.doubt_score


def test_high_doubt_recommendation(engine):
    # many gaps + poor quality
    hyp = {"id": "h5", "confidence": 0.9, "complexity": 6, "expected_effect": 0.5}
    a = engine.analyze(hyp, WEAK_EVIDENCE)
    assert "High doubt" in a.recommendation or a.doubt_score > 0.7


def test_get_high_doubt_recommendations_filters(engine):
    engine.analyze({"id": "h6"}, WEAK_EVIDENCE)
    engine.analyze({"id": "h7"}, STRONG_EVIDENCE)
    high = engine.get_high_doubt_recommendations(threshold=0.4)
    ids = [a.hypothesis_id for a in high]
    # h6 with weak evidence should be in high doubt
    assert "h6" in ids


def test_to_dict_serializes_correctly(engine):
    a = engine.analyze({"id": "h8"}, WEAK_EVIDENCE)
    d = a.to_dict()
    for key in ["id", "hypothesis_id", "critical_questions", "doubt_score",
                "evidence_gaps", "adversarial_arguments", "recommendation", "created_at"]:
        assert key in d
    assert d["hypothesis_id"] == "h8"
    assert isinstance(d["critical_questions"], list)
