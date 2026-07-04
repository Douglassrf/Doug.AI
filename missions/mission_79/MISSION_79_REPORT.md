# Mission 79 — Self Confidence Calibration

## Status: COMPLETED

## Module
`doug_os/discovery/self_confidence_calibration.py`

## Classes
- `CalibrationData`: Dataclass storing predictions, outcomes, confidence scores.
- `CalibrationResult`: Dataclass with calibration_score, overconfidence_gap, underconfidence_gap, calibration_curve, alert_level, recommendation.
- `SelfConfidenceCalibration`: Main class implementing numpy-only calibration (no sklearn). Brier score-based calibration score, bin-based gap analysis, calibration curve generation, alert level and recommendation logic.

## Key behaviors
- `record_prediction(pred, outcome, conf)`: stores and trims to window_size
- `calibrate()`: returns CalibrationResult; needs >= 10 samples; calibration_score = 1 - brier/0.25
- `_generate_calibration_curve()`: pure numpy binning, returns List[Tuple[float, float]]
- Alert "red" if calibration < 0.3 or over_gap > 0.3

## Tests (7 passing)
- < 10 records → calibration_score=0.5, recommendation about insufficient data
- perfect predictions → calibration_score > 0.9
- pred=0.9, outcome=0 → over_gap > 0.3, alert "red"
- calibration_curve returns list of (float, float) tuples
- window_size=5 after 6 records → 5 stored
- alert "green" with perfect calibration
- to_dict serializes all required fields

## Commit
`f0ef48b` — Missao 79 - Self Confidence Calibration
