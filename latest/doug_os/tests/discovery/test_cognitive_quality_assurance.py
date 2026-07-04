import pytest
from doug_os.discovery.cognitive_quality_assurance import (
    CognitiveQualityAssurance, QAReport, QAMetrics,
)


@pytest.fixture
def qa():
    return CognitiveQualityAssurance()


ALL_PASS = {
    "check_inputs": {"passed": True},
    "check_outputs": {"passed": True},
    "check_latency": {"passed": True},
    "check_confidence": {"passed": True},
}

HALF_PASS = {
    "check_inputs": {"passed": True},
    "check_outputs": {"passed": False, "issue": "null output", "recommendation": "add fallback"},
}

ALL_FAIL = {
    "check_a": {"passed": False, "issue": "failed A"},
    "check_b": {"passed": False, "issue": "failed B"},
}


def test_check_component_returns_qa_report(qa):
    report = qa.check_component("decision", ALL_PASS)
    assert isinstance(report, QAReport)


def test_all_pass_score_is_1(qa):
    report = qa.check_component("decision", ALL_PASS)
    assert report.quality_score == 1.0
    assert report.passed is True


def test_half_pass_score_correct(qa):
    report = qa.check_component("risk", HALF_PASS)
    assert report.quality_score == 0.5
    assert report.passed is False


def test_all_fail_score_is_0(qa):
    report = qa.check_component("memory", ALL_FAIL)
    assert report.quality_score == 0.0
    assert report.passed is False


def test_issues_populated_on_failure(qa):
    report = qa.check_component("prediction", HALF_PASS)
    assert len(report.issues) > 0


def test_recommendations_populated(qa):
    report = qa.check_component("learning", HALF_PASS)
    assert len(report.recommendations) > 0


def test_unknown_component_raises(qa):
    with pytest.raises(ValueError):
        qa.check_component("nonexistent", ALL_PASS)


def test_register_new_component(qa):
    qa.register_component("custom_module")
    report = qa.check_component("custom_module", ALL_PASS)
    assert report.quality_score == 1.0


def test_get_component_metrics_accumulate(qa):
    qa.check_component("decision", ALL_PASS)
    qa.check_component("decision", HALF_PASS)
    m = qa.get_component_metrics("decision")
    assert m.total_checks == 6  # 4 + 2


def test_get_latest_report(qa):
    qa.check_component("risk", ALL_PASS)
    qa.check_component("risk", HALF_PASS)
    latest = qa.get_latest_report("risk")
    assert latest.quality_score == 0.5


def test_get_latest_report_unknown_returns_none(qa):
    assert qa.get_latest_report("ghost") is None


def test_get_qa_dashboard(qa):
    qa.check_component("decision", ALL_PASS)
    dash = qa.get_qa_dashboard()
    assert "total_reports" in dash
    assert "overall_quality" in dash
    assert "components" in dash
