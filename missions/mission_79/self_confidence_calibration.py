from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import numpy as np


@dataclass
class CalibrationData:
    predictions: List[float] = field(default_factory=list)
    outcomes: List[float] = field(default_factory=list)
    confidence_scores: List[float] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "predictions": self.predictions[-100:],
            "outcomes": self.outcomes[-100:],
            "confidence_scores": self.confidence_scores[-100:],
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class CalibrationResult:
    calibration_score: float = 0.0
    overconfidence_gap: float = 0.0
    underconfidence_gap: float = 0.0
    calibration_curve: List[Tuple[float, float]] = field(default_factory=list)
    alert_level: str = "green"
    recommendation: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "calibration_score": self.calibration_score,
            "overconfidence_gap": self.overconfidence_gap,
            "underconfidence_gap": self.underconfidence_gap,
            "alert_level": self.alert_level,
            "recommendation": self.recommendation,
            "created_at": self.created_at.isoformat(),
        }


class SelfConfidenceCalibration:
    def __init__(self, window_size: int = 100):
        self._predictions: List[float] = []
        self._outcomes: List[float] = []
        self._confidences: List[float] = []
        self._window_size = window_size

    def record_prediction(self, prediction: float, outcome: float, confidence: float) -> None:
        self._predictions.append(prediction)
        self._outcomes.append(outcome)
        self._confidences.append(confidence)
        if len(self._predictions) > self._window_size:
            self._predictions = self._predictions[-self._window_size:]
            self._outcomes = self._outcomes[-self._window_size:]
            self._confidences = self._confidences[-self._window_size:]

    def calibrate(self) -> CalibrationResult:
        if len(self._predictions) < 10:
            return CalibrationResult(
                calibration_score=0.5,
                recommendation="Need more data for calibration",
            )
        preds = np.array(self._predictions)
        outcomes = np.array(self._outcomes)
        confs = np.array(self._confidences)

        calibration_score = self._calculate_calibration_score(preds, outcomes)
        over_gap, under_gap = self._calculate_gaps(confs, outcomes)
        curve = self._generate_calibration_curve(preds, outcomes)
        alert = self._determine_alert(calibration_score, over_gap, under_gap)
        recommendation = self._generate_recommendation(calibration_score, over_gap, under_gap)

        return CalibrationResult(
            calibration_score=calibration_score,
            overconfidence_gap=over_gap,
            underconfidence_gap=under_gap,
            calibration_curve=curve,
            alert_level=alert,
            recommendation=recommendation,
        )

    def _calculate_calibration_score(self, preds: np.ndarray, outcomes: np.ndarray) -> float:
        brier = float(np.mean((preds - outcomes) ** 2))
        return float(min(max(1 - brier / 0.25, 0.0), 1.0))

    def _calculate_gaps(self, confs: np.ndarray, outcomes: np.ndarray) -> Tuple[float, float]:
        bins = np.linspace(0, 1, 11)
        over_gaps, under_gaps = [], []
        for i in range(len(bins) - 1):
            mask = (confs >= bins[i]) & (confs < bins[i + 1])
            if mask.sum() == 0:
                continue
            avg_conf = float(np.mean(confs[mask]))
            avg_acc = float(np.mean(outcomes[mask]))
            gap = avg_conf - avg_acc
            if gap > 0:
                over_gaps.append(gap)
            else:
                under_gaps.append(-gap)
        return (
            float(min(np.mean(over_gaps), 1.0)) if over_gaps else 0.0,
            float(min(np.mean(under_gaps), 1.0)) if under_gaps else 0.0,
        )

    def _generate_calibration_curve(self, preds: np.ndarray, outcomes: np.ndarray) -> List[Tuple[float, float]]:
        bins = np.linspace(0, 1, 11)
        curve = []
        for i in range(len(bins) - 1):
            mask = (preds >= bins[i]) & (preds < bins[i + 1])
            if mask.sum() == 0:
                continue
            prob_pred = float(np.mean(preds[mask]))
            prob_true = float(np.mean(outcomes[mask]))
            curve.append((prob_pred, prob_true))
        return curve

    def _determine_alert(self, calibration: float, over_gap: float, under_gap: float) -> str:
        if calibration < 0.3 or over_gap > 0.3: return "red"
        if calibration < 0.5 or over_gap > 0.2: return "yellow"
        return "green"

    def _generate_recommendation(self, calibration: float, over_gap: float, under_gap: float) -> str:
        if calibration < 0.3: return "Critical: Confidence is poorly calibrated"
        if over_gap > 0.3: return "High overconfidence detected. Apply correction factor."
        if under_gap > 0.3: return "High underconfidence detected. Increase confidence weighting."
        if calibration < 0.5: return "Moderate calibration issues. Review confidence scoring."
        return "Confidence is well calibrated"
