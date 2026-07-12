import pytest
from doug_os.discovery.revolution_detector import ScientificRevolutionDetector, ParadigmShift


OLD = {
    "name": "OldEMH",
    "predictive_power": 0.5,
    "complexity": 2.0,
    "assumptions": ["markets_efficient", "random_walk", "rational_agents"],
}

NEW_BETTER = {
    "name": "BehavioralFinance",
    "predictive_power": 0.85,
    "complexity": 1.5,
    "assumptions": ["cognitive_biases", "momentum", "sentiment"],
}

NEW_EQUIVALENT = {
    "name": "AltEMH",
    "predictive_power": 0.52,
    "complexity": 2.1,
    "assumptions": ["markets_efficient", "random_walk", "rational_agents"],
}


def test_compare_theories_returns_paradigm_shift():
    det = ScientificRevolutionDetector()
    shift = det.compare_theories(OLD, NEW_BETTER)
    assert isinstance(shift, ParadigmShift)
    assert shift.shift_score >= 0.0
    assert shift.shift_score <= 1.0


def test_new_theory_much_better_shift_score_high():
    det = ScientificRevolutionDetector()
    shift = det.compare_theories(OLD, NEW_BETTER)
    assert shift.shift_score > 0.7, f"Expected shift_score > 0.7, got {shift.shift_score}"
    assert shift.is_revolution is True


def test_equivalent_theories_moderate_shift():
    det = ScientificRevolutionDetector()
    shift = det.compare_theories(OLD, NEW_EQUIVALENT)
    assert shift.shift_score < 0.7, f"Expected shift_score < 0.7, got {shift.shift_score}"
    assert shift.is_revolution is False


def test_get_revolution_alerts_filters_by_threshold():
    det = ScientificRevolutionDetector()
    det.compare_theories(OLD, NEW_BETTER)     # high shift
    det.compare_theories(OLD, NEW_EQUIVALENT) # low shift
    alerts = det.get_revolution_alerts()
    assert len(alerts) == 1
    assert alerts[0].shift_score > det.REVOLUTION_THRESHOLD


def test_to_dict_serialization():
    det = ScientificRevolutionDetector()
    shift = det.compare_theories(OLD, NEW_BETTER)
    d = shift.to_dict()
    assert "shift_score" in d
    assert "old_theory" in d
    assert "new_theory" in d
    assert "is_revolution" in d
    assert "detected_at" in d


def test_evidence_filled_when_new_better():
    det = ScientificRevolutionDetector()
    shift = det.compare_theories(OLD, NEW_BETTER)
    assert len(shift.evidence) > 0
    assert any("predictive power" in e.lower() or "assumption" in e.lower() for e in shift.evidence)
