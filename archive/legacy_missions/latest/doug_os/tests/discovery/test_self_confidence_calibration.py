import pytest
from doug_os.discovery.self_confidence_calibration import SelfConfidenceCalibration, CalibrationResult


@pytest.fixture
def calib():
    return SelfConfidenceCalibration(window_size=100)


def test_calibrate_insufficient_data(calib):
    for _ in range(5):
        calib.record_prediction(0.7, 1.0, 0.7)
    result = calib.calibrate()
    assert result.calibration_score == 0.5
    assert "data" in result.recommendation.lower() or "more" in result.recommendation.lower()


def test_calibrate_perfect_predictions(calib):
    for v in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        calib.record_prediction(v, v, v)
    result = calib.calibrate()
    assert result.calibration_score > 0.9


def test_calibrate_bad_predictions_over_gap(calib):
    # Confidence always 0.9 but outcome always 0 → big overconfidence
    for _ in range(20):
        calib.record_prediction(0.9, 0.0, 0.9)
    result = calib.calibrate()
    assert result.overconfidence_gap > 0.3
    assert result.alert_level == "red"


def test_calibration_curve_returns_tuples(calib):
    import numpy as np
    rng = np.random.default_rng(42)
    for _ in range(30):
        p = float(rng.uniform(0, 1))
        o = float(rng.uniform(0, 1))
        calib.record_prediction(p, o, p)
    result = calib.calibrate()
    assert isinstance(result.calibration_curve, list)
    assert len(result.calibration_curve) > 0
    for item in result.calibration_curve:
        assert isinstance(item, tuple)
        assert len(item) == 2


def test_window_size_limit():
    calib = SelfConfidenceCalibration(window_size=5)
    for i in range(6):
        calib.record_prediction(float(i) / 10, float(i) / 10, float(i) / 10)
    assert len(calib._predictions) == 5


def test_alert_green_good_calibration(calib):
    # Perfect predictions → calibration_score high, gaps low
    for v in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        calib.record_prediction(v, v, v)
    result = calib.calibrate()
    assert result.alert_level == "green"


def test_to_dict_fields(calib):
    for v in [0.5] * 10:
        calib.record_prediction(v, v, v)
    result = calib.calibrate()
    d = result.to_dict()
    assert "calibration_score" in d
    assert "overconfidence_gap" in d
    assert "underconfidence_gap" in d
    assert "alert_level" in d
    assert "recommendation" in d
    assert "created_at" in d
