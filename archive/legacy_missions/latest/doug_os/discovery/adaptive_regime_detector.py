from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class RegimeData:
    timestamp: datetime
    volatility: float = 0.0
    momentum: float = 0.0
    volume: float = 0.0
    spread: float = 0.0
    correlation: float = 0.0
    trend_strength: float = 0.0

    def to_feature_array(self) -> List[float]:
        return [
            self.volatility, self.momentum, self.volume,
            self.spread, self.correlation, self.trend_strength,
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "volatility": self.volatility,
            "momentum": self.momentum,
            "volume": self.volume,
            "spread": self.spread,
            "correlation": self.correlation,
            "trend_strength": self.trend_strength,
        }


@dataclass
class RegimeDetectionResult:
    id: str = field(default_factory=lambda: f"reg_{uuid.uuid4().hex[:12]}")
    regime: str = ""
    confidence: float = 0.0
    transition_score: float = 0.0
    features: Dict[str, float] = field(default_factory=dict)
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "regime": self.regime,
            "confidence": self.confidence,
            "transition_score": self.transition_score,
            "features": self.features,
            "alternatives": self.alternatives,
            "created_at": self.created_at.isoformat(),
        }


class _NumpyKMeans:
    """Minimal K-Means using numpy only."""

    def __init__(self, n_clusters: int = 4, max_iter: int = 100, seed: int = 42):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self._rng = np.random.default_rng(seed)
        self.centers_: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray) -> None:
        idx = self._rng.choice(len(X), self.n_clusters, replace=False)
        self.centers_ = X[idx].copy().astype(float)
        for _ in range(self.max_iter):
            labels = self._assign(X)
            new_centers = np.array(
                [
                    X[labels == k].mean(axis=0) if (labels == k).any() else self.centers_[k]
                    for k in range(self.n_clusters)
                ]
            )
            if np.allclose(new_centers, self.centers_):
                break
            self.centers_ = new_centers

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self._assign(X)

    def transform(self, X: np.ndarray) -> np.ndarray:
        return np.linalg.norm(X[:, None, :] - self.centers_[None, :, :], axis=2)

    def _assign(self, X: np.ndarray) -> np.ndarray:
        return np.argmin(self.transform(X), axis=1)


class AdaptiveRegimeDetector:
    def __init__(self, window_size: int = 50):
        self._history: List[RegimeData] = []
        self._regime_history: List[str] = []
        self._detections: List[RegimeDetectionResult] = []
        self._window_size = window_size
        self._model: Optional[_NumpyKMeans] = None
        self._mean: Optional[np.ndarray] = None
        self._std: Optional[np.ndarray] = None
        self._is_trained = False

    def add_data(self, data: RegimeData) -> None:
        self._history.append(data)
        if len(self._history) > self._window_size * 2:
            self._history = self._history[-self._window_size * 2:]

    def train(self) -> None:
        if len(self._history) < self._window_size:
            return
        X = np.array([d.to_feature_array() for d in self._history[-self._window_size:]], dtype=float)
        self._mean = X.mean(axis=0)
        self._std = X.std(axis=0) + 1e-8
        X_scaled = (X - self._mean) / self._std
        n_clusters = min(5, len(X) // 3)
        if n_clusters < 2:
            return
        self._model = _NumpyKMeans(n_clusters=n_clusters)
        self._model.fit(X_scaled)
        self._is_trained = True

    def detect_regime(self) -> RegimeDetectionResult:
        result = RegimeDetectionResult()
        if not self._history or not self._is_trained:
            result.regime = "unknown"
            return result
        latest = self._history[-1]
        x = np.array([latest.to_feature_array()], dtype=float)
        x_scaled = (x - self._mean) / self._std
        cluster = int(self._model.predict(x_scaled)[0])
        distances = self._model.transform(x_scaled)[0]
        result.regime = self._cluster_to_regime(cluster)
        total_dist = distances.sum() + 1e-6
        result.confidence = float(np.clip(1.0 - distances[cluster] / total_dist, 0.0, 1.0))
        result.features = {
            "volatility": latest.volatility, "momentum": latest.momentum,
            "volume": latest.volume, "spread": latest.spread,
            "correlation": latest.correlation, "trend_strength": latest.trend_strength,
        }
        result.transition_score = self._transition_score(result.regime)
        sorted_idx = np.argsort(distances)
        result.alternatives = [
            {
                "regime": self._cluster_to_regime(int(i)),
                "confidence": float(np.clip(1.0 - distances[i] / total_dist, 0.0, 1.0)),
            }
            for i in sorted_idx[1:3]
        ]
        self._regime_history.append(result.regime)
        self._detections.append(result)
        return result

    def _cluster_to_regime(self, cluster: int) -> str:
        if self._model is None or self._mean is None or self._std is None:
            return "unknown"
        center_scaled = self._model.centers_[cluster]
        center_real = center_scaled * self._std + self._mean
        vol, mom, trend = center_real[0], center_real[1], center_real[5]
        if vol > 0.7:
            return "crisis"
        if vol > 0.5:
            return "high_volatility"
        if abs(mom) > 0.5 and trend > 0.3:
            return "trending_bull" if mom > 0 else "trending_bear"
        if abs(mom) < 0.2:
            return "ranging"
        return "low_volatility"

    def _transition_score(self, current: str) -> float:
        if len(self._regime_history) < 5:
            return 0.0
        recent = self._regime_history[-10:]
        changes = sum(1 for i in range(1, len(recent)) if recent[i] != recent[i - 1])
        return changes / len(recent)

    def get_regime_history(self, limit: int = 20) -> List[str]:
        return self._regime_history[-limit:]

    def get_detection_stats(self) -> Dict[str, Any]:
        if not self._detections:
            return {"status": "no_data"}
        regimes = [d.regime for d in self._detections]
        counts: Dict[str, int] = {}
        for r in regimes:
            counts[r] = counts.get(r, 0) + 1
        return {
            "total_detections": len(self._detections),
            "regime_counts": counts,
            "avg_confidence": float(np.mean([d.confidence for d in self._detections])),
            "avg_transition_score": float(np.mean([d.transition_score for d in self._detections])),
            "current_regime": regimes[-1] if regimes else "unknown",
        }
