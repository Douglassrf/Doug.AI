import pytest
from doug_os.discovery.confidence_illusion_detector import ConfidenceIllusionDetector, ConfidenceIllusionReport


@pytest.fixture
def detector():
    return ConfidenceIllusionDetector()


def test_small_gap_severity_none_or_low(detector):
    evidence = {"sample_size": 500, "reproducible": True, "p_value": 0.01, "consistent_effect": True}
    # declared ~= evidence_confidence (0.3+0.3+0.2+0.2=1.0), so gap near 0
    r = detector.analyze("h1", 1.0, evidence)
    assert r.severity in ("none", "low")


def test_large_gap_severity_critical(detector):
    # weak evidence → ev_conf = 0; declared = 0.9 → gap = 0.9 → critical
    r = detector.analyze("h2", 0.9, {})
    assert r.severity == "critical"
    assert r.illusion_gap >= 0.6


def test_strong_evidence_high_confidence(detector):
    evidence = {"sample_size": 2000, "reproducible": True, "p_value": 0.005, "consistent_effect": True}
    r = detector.analyze("h3", 0.5, evidence)
    assert r.evidence_confidence >= 0.8


def test_get_critical_alerts_filters_correctly(detector):
    detector.analyze("h4", 0.9, {})   # critical
    detector.analyze("h5", 0.6, {})   # high (gap=0.6)
    detector.analyze("h6", 1.0, {"sample_size": 2000, "reproducible": True, "p_value": 0.001, "consistent_effect": True})  # none/low
    alerts = detector.get_critical_alerts()
    assert all(a.severity in ("high", "critical") for a in alerts)
    assert len(alerts) >= 1


def test_evidence_quality_calculated_correctly(detector):
    evidence = {
        "peer_reviewed": True,
        "raw_data_available": True,
        "methodology_documented": True,
        "independent_replication": True,
    }
    r = detector.analyze("h7", 0.5, evidence)
    assert r.evidence_quality == pytest.approx(1.0)


def test_to_dict_serializes_all_fields(detector):
    r = detector.analyze("h8", 0.7, {"sample_size": 50})
    d = r.to_dict()
    for key in ["id", "hypothesis_id", "declared_confidence", "evidence_confidence",
                "illusion_gap", "severity", "evidence_quality", "recommendation", "created_at"]:
        assert key in d
    assert d["hypothesis_id"] == "h8"
    assert d["declared_confidence"] == 0.7
