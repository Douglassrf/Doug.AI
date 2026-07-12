from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import time
import numpy as np

try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False


@dataclass
class BenchmarkResult:
    id: str = field(default_factory=lambda: f"bm_{uuid.uuid4().hex[:12]}")
    name: str = ""
    category: str = ""
    score: float = 0.0
    latency_ms: float = 0.0
    memory_usage_mb: float = 0.0
    accuracy: float = 0.0
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "score": self.score,
            "latency_ms": self.latency_ms,
            "memory_usage_mb": self.memory_usage_mb,
            "accuracy": self.accuracy,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class CognitiveBenchmarkLaboratory:
    """Laboratório de benchmark cognitivo para módulos Doug.AI."""

    _CATEGORIES = ("algorithm", "strategy", "latency", "memory", "risk", "accuracy", "confidence", "discovery")

    def __init__(self) -> None:
        self._results: Dict[str, List[BenchmarkResult]] = {c: [] for c in self._CATEGORIES}

    def run_benchmark(
        self,
        name: str,
        category: str,
        test_function: Callable,
        iterations: int = 10,
    ) -> BenchmarkResult:
        if category not in self._results:
            raise ValueError(f"Unknown category: {category}")

        scores: List[float] = []
        latencies: List[float] = []
        memories: List[float] = []
        accuracies: List[float] = []

        for _ in range(iterations):
            t0 = time.perf_counter()
            m0 = self._memory_mb()
            try:
                out = test_function()
                scores.append(float(out.get("score", 0.5)) if isinstance(out, dict) else 0.5)
                accuracies.append(float(out.get("accuracy", 0.5)) if isinstance(out, dict) else 0.5)
            except Exception:
                scores.append(0.0)
                accuracies.append(0.0)
            latencies.append((time.perf_counter() - t0) * 1000)
            memories.append(max(0.0, self._memory_mb() - m0))

        avg_score = float(np.mean(scores))
        avg_lat = float(np.mean(latencies))
        avg_mem = float(np.mean(memories))
        avg_acc = float(np.mean(accuracies))
        std_score = float(np.std(scores))
        confidence = min(1.0, max(0.1, 1.0 - std_score / (avg_score + 1e-9)))

        result = BenchmarkResult(
            name=name,
            category=category,
            score=avg_score,
            latency_ms=avg_lat,
            memory_usage_mb=avg_mem,
            accuracy=avg_acc,
            confidence=confidence,
            metadata={"iterations": iterations, "scores": scores, "latencies": latencies},
        )
        self._results[category].append(result)
        return result

    def _memory_mb(self) -> float:
        if _HAS_PSUTIL:
            try:
                return psutil.Process().memory_info().rss / (1024 * 1024)
            except Exception:
                pass
        return 0.0

    def get_best_in_category(self, category: str, metric: str = "score") -> Optional[BenchmarkResult]:
        results = self._results.get(category, [])
        return max(results, key=lambda x: getattr(x, metric, 0.0)) if results else None

    def get_category_ranking(self, category: str, metric: str = "score") -> List[BenchmarkResult]:
        results = self._results.get(category, [])
        return sorted(results, key=lambda x: getattr(x, metric, 0.0), reverse=True)

    def get_benchmark_dashboard(self) -> Dict[str, Any]:
        return {
            "categories": {
                cat: {
                    "total_results": len(rs),
                    "best_score": max((r.score for r in rs), default=0.0),
                    "best_latency_ms": min((r.latency_ms for r in rs), default=0.0),
                    "avg_score": float(np.mean([r.score for r in rs])) if rs else 0.0,
                }
                for cat, rs in self._results.items()
            }
        }
