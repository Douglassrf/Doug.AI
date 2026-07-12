import pytest
from datetime import datetime, timezone
import numpy as np
from doug_os.discovery.adaptive_regime_detector import AdaptiveRegimeDetector, RegimeData


def _make_data(vol: float = 0.3, mom: float = 0.1, trend: float = 0.2) -> RegimeData:
    return RegimeData(
        timestamp=datetime.now(timezone.utc),
        volatility=vol, momentum=mom, volume=0.5,
        spread=0.02, correlation=0.4, trend_strength=trend,
    )


@pytest.fixture
def trained_detector():
    det = AdaptiveRegimeDetector(window_size=20)
    rng = np.random.default_rng(42)
    for _ in range(25):
        det.add_data(_make_data(
            vol=float(rng.uniform(0.1, 0.9)),
            mom=float(rng.uniform(-0.8, 0.8)),
            trend=float(rng.uniform(0.0, 0.8)),
        ))
    det.train()
    return det


def test_add_data_stores(trained_detector):
    assert len(trained_detector._history) > 0


def test_train_insufficient_data():
    det = AdaptiveRegimeDetector(window_size=50)
    for _ in range(10):
        det.add_data(_make_data())
    det.train()
    assert not det._is_trained


def test_train_sufficient_data(trained_detector):
    assert trained_detector._is_trained


def test_detect_regime_untrained_returns_unknown():
    det = AdaptiveRegimeDetector(window_size=50)
    det.add_data(_make_data())
    result = det.detect_regime()
    assert result.regime == "unknown"


def test_detect_regime_returns_nonempty_string(trained_detector):
    trained_detector.add_data(_make_data())
    result = trained_detector.detect_regime()
    assert isinstance(result.regime, str) and len(result.regime) > 0


def test_confidence_in_range(trained_detector):
    trained_detector.add_data(_make_data())
    result = trained_detector.detect_regime()
    assert 0.0 <= result.confidence <= 1.0


def test_regime_history_grows(trained_detector):
    trained_detector.add_data(_make_data())
    trained_detector.detect_regime()
    trained_detector.add_data(_make_data())
    trained_detector.detect_regime()
    assert len(trained_detector.get_regime_history()) == 2


def test_get_detection_stats_no_data():
    det = AdaptiveRegimeDetector()
    assert det.get_detection_stats() == {"status": "no_data"}


def test_get_detection_stats_after_detection(trained_detector):
    trained_detector.add_data(_make_data())
    trained_detector.detect_regime()
    stats = trained_detector.get_detection_stats()
    assert stats["total_detections"] >= 1
    assert "regime_counts" in stats
    assert 0.0 <= stats["avg_confidence"] <= 1.0


def test_alternatives_at_most_two(trained_detector):
    trained_detector.add_data(_make_data())
    result = trained_detector.detect_regime()
    assert len(result.alternatives) <= 2


def test_high_volatility_data_gets_volatile_regime(trained_detector):
    trained_detector.add_data(_make_data(vol=0.95, mom=0.0, trend=0.0))
    result = trained_detector.detect_regime()
    assert result.regime in ("crisis", "high_volatility", "ranging", "low_volatility",
                             "trending_bull", "trending_bear")


def test_to_dict_serializes(trained_detector):
    trained_detector.add_data(_make_data())
    result = trained_detector.detect_regime()
    d = result.to_dict()
    assert "regime" in d and "confidence" in d and "features" in d
