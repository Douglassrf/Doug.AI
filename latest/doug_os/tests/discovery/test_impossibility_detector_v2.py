import pytest
from doug_os.discovery.impossibility_detector_v2 import ImpossibilityDetectorV2, ImpossibilityReport


def test_valid_hypothesis_not_impossible():
    det = ImpossibilityDetectorV2()
    report = det.check("momentum predicts returns", {"sample_size": 100, "p_value": 0.01, "probability": 0.6})
    assert report.is_impossible is False
    assert report.veto is False
    assert len(report.violations) == 0


def test_logical_violation_guaranteed_arbitrage():
    det = ImpossibilityDetectorV2()
    report = det.check("arbitrage guaranteed 100% return", {"sample_size": 100, "p_value": 0.01})
    assert any("Logical" in v for v in report.violations)


def test_contradiction_increase_decrease():
    det = ImpossibilityDetectorV2()
    report = det.check("price will increase and decrease simultaneously", {"sample_size": 100, "p_value": 0.01})
    assert any("Contradiction" in v for v in report.violations)


def test_statistical_violation_small_sample():
    det = ImpossibilityDetectorV2()
    report = det.check("momentum effect", {"sample_size": 10, "p_value": 0.01})
    assert any("Statistical" in v for v in report.violations)


def test_probabilistic_violation_too_high():
    det = ImpossibilityDetectorV2()
    report = det.check("signal fires", {"sample_size": 100, "p_value": 0.01, "probability": 0.9999})
    assert any("Probabilistic" in v for v in report.violations)


def test_veto_with_three_violations():
    det = ImpossibilityDetectorV2()
    # arbitrage 100% (logical) + increase/decrease (contradiction) + small sample (statistical)
    report = det.check(
        "arbitrage guaranteed 100% will increase and decrease",
        {"sample_size": 5, "p_value": 0.01}
    )
    assert len(report.violations) >= 3
    assert report.veto is True
    assert report.veto_reason != ""


def test_to_dict_serialization():
    det = ImpossibilityDetectorV2()
    report = det.check("test hypothesis", {"sample_size": 100, "p_value": 0.01})
    d = report.to_dict()
    assert "is_impossible" in d
    assert "violations" in d
    assert "suggestions" in d
    assert "veto" in d
    assert isinstance(d["violations"], list)
