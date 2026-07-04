import pytest
from discovery.scientific_evidence_ranking import ScientificEvidenceRanking, Evidence


def test_add_evidence():
    ser = ScientificEvidenceRanking()
    ev = ser.add_evidence("Study A", "Nature", p_value=0.01, effect_size=0.8, sample_size=500)
    assert ev.title == "Study A"
    assert ev.rank_score > 0.0


def test_high_quality_evidence_high_score():
    ser = ScientificEvidenceRanking()
    ev = ser.add_evidence("Top Study", "Science",
                          p_value=0.001, effect_size=1.2,
                          sample_size=5000, replication_count=5, peer_reviewed=True)
    assert ev.rank_score > 0.5


def test_low_quality_evidence_low_score():
    ser = ScientificEvidenceRanking()
    ev = ser.add_evidence("Weak Study", "Blog",
                          p_value=0.9, effect_size=0.0,
                          sample_size=10, peer_reviewed=False)
    assert ev.rank_score < 0.5


def test_rank_evidence_ordered():
    ser = ScientificEvidenceRanking()
    e1 = ser.add_evidence("Weak", "Blog", p_value=0.9, effect_size=0.0, sample_size=5)
    e2 = ser.add_evidence("Strong", "Journal", p_value=0.001, effect_size=0.9, sample_size=1000, peer_reviewed=True)
    ranked = ser.rank_evidence()
    assert ranked[0].title == "Strong"


def test_get_top_evidence():
    ser = ScientificEvidenceRanking()
    for i in range(10):
        ser.add_evidence(f"Study {i}", "src", p_value=0.05 - i*0.005, effect_size=0.5)
    top = ser.get_top_evidence(n=3)
    assert len(top) == 3


def test_tag_filter():
    ser = ScientificEvidenceRanking()
    ser.add_evidence("BTC", "src", p_value=0.01, tags=["crypto"])
    ser.add_evidence("SPY", "src", p_value=0.01, tags=["equity"])
    crypto = ser.rank_evidence(tag_filter="crypto")
    assert len(crypto) == 1
    assert crypto[0].title == "BTC"


def test_compare_evidence():
    ser = ScientificEvidenceRanking()
    e1 = ser.add_evidence("Strong", "src", p_value=0.001, effect_size=0.9, sample_size=1000)
    e2 = ser.add_evidence("Weak", "src", p_value=0.9, effect_size=0.01, sample_size=10)
    result = ser.compare_evidence(e1.id, e2.id)
    assert result["winner_id"] == e1.id


def test_compare_missing_evidence():
    ser = ScientificEvidenceRanking()
    e = ser.add_evidence("E1", "src")
    result = ser.compare_evidence(e.id, "nonexistent")
    assert "error" in result


def test_get_ranking_summary():
    ser = ScientificEvidenceRanking()
    ser.add_evidence("E1", "src", p_value=0.01, peer_reviewed=True)
    ser.add_evidence("E2", "src", p_value=0.05)
    summary = ser.get_ranking_summary()
    assert summary["total"] == 2
    assert summary["peer_reviewed_count"] == 1


def test_empty_ranking_summary():
    ser = ScientificEvidenceRanking()
    assert ser.get_ranking_summary() == {"status": "empty"}
