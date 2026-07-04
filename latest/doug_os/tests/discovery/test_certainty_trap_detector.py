import pytest
from datetime import datetime, timezone, timedelta
from doug_os.discovery.certainty_trap_detector import CertaintyTrapDetector


@pytest.fixture
def detector():
    return CertaintyTrapDetector()


def _now():
    return datetime.now(timezone.utc)


def test_new_hypothesis_severity_none(detector):
    alert = detector.check(
        "h1", "new hyp", _now(), _now(), "bull", ["bull"]
    )
    assert alert.severity == "none"


def test_hypothesis_over_30_days_severity_low(detector):
    created = _now() - timedelta(days=40)
    alert = detector.check("h2", "old hyp", created, _now(), "bull", ["bull"])
    assert alert.severity == "low"


def test_hypothesis_over_90_days_medium(detector):
    created = _now() - timedelta(days=100)
    alert = detector.check("h3", "older", created, _now(), "bull", ["bull", "bear", "sideways"])
    assert alert.severity == "medium"


def test_hypothesis_critical(detector):
    created = _now() - timedelta(days=400)
    last_review = _now() - timedelta(days=60)  # frozen
    alert = detector.check("h4", "ancient", created, last_review, "bull",
                           ["bull", "bear", "sideways", "volatile", "crash"])
    assert alert.severity == "critical"


def test_get_stale_hypotheses(detector):
    created_old = _now() - timedelta(days=120)
    created_new = _now() - timedelta(days=10)
    detector.check("old_h", "old", created_old, _now(), "bull", ["bull"])
    detector.check("new_h", "new", created_new, _now(), "bull", ["bull"])
    stale = detector.get_stale_hypotheses(max_age_days=90)
    assert "old_h" in stale
    assert "new_h" not in stale


def test_to_dict_serializes_correctly(detector):
    created = _now() - timedelta(days=5)
    alert = detector.check("h5", "test hyp", created, _now(), "bull", ["bull"])
    d = alert.to_dict()
    for key in ["id", "hypothesis_id", "hypothesis_text", "age_days",
                "confidence_frozen", "regime_changes", "severity", "recommendation", "created_at"]:
        assert key in d
    assert d["hypothesis_id"] == "h5"
    assert d["hypothesis_text"] == "test hyp"
