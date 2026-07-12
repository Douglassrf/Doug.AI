from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import time

try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False


@dataclass
class BenchmarkSuite:
    id: str = field(default_factory=lambda: f"bs_{uuid.uuid4().hex[:12]}")
    name: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class BenchmarkRun:
    id: str = field(default_factory=lambda: f"br_{uuid.uuid4().hex[:12]}")
    suite_id: str = ""
    benchmark_name: str = ""
    iterations: int = 1
    avg_latency_ms: float = 0.0
    min_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    throughput: float = 0.0
    memory_mb: float = 0.0
    score: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "suite_id": self.suite_id,
            "benchmark_name": self.benchmark_name,
            "iterations": self.iterations,
            "avg_latency_ms": self.avg_latency_ms,
            "min_latency_ms": self.min_latency_ms,
            "max_latency_ms": self.max_latency_ms,
            "throughput": self.throughput,
            "memory_mb": self.memory_mb,
            "score": self.score,
            "timestamp": self.timestamp.isoformat(),
        }


class AutonomousBenchmarkFramework:
    """Framework autônomo de benchmarks — suítes, execução com timing, scoring e comparação."""

    def __init__(self) -> None:
        self._suites: Dict[str, BenchmarkSuite] = {}
        self._runs: List[BenchmarkRun] = []
        self._baselines: Dict[str, float] = {}

    def create_suite(self, name: str, description: str = "", tags: Optional[List[str]] = None) -> BenchmarkSuite:
        suite = BenchmarkSuite(name=name, description=description, tags=tags or [])
        self._suites[suite.id] = suite
        return suite

    def run_benchmark(
        self,
        suite_id: str,
        name: str,
        fn: Callable[[], Any],
        iterations: int = 10,
    ) -> BenchmarkRun:
        latencies: List[float] = []
        mem_before = self._get_memory_mb()

        for _ in range(iterations):
            t0 = time.perf_counter()
            fn()
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000.0)

        mem_after = self._get_memory_mb()
        avg_ms = sum(latencies) / len(latencies)
        throughput = 1000.0 / avg_ms if avg_ms > 0 else 0.0
        score = self._compute_score(avg_ms, throughput)

        run = BenchmarkRun(
            suite_id=suite_id,
            benchmark_name=name,
            iterations=iterations,
            avg_latency_ms=avg_ms,
            min_latency_ms=min(latencies),
            max_latency_ms=max(latencies),
            throughput=throughput,
            memory_mb=max(0.0, mem_after - mem_before),
            score=score,
        )
        self._runs.append(run)
        return run

    def _get_memory_mb(self) -> float:
        if _HAS_PSUTIL:
            try:
                return psutil.Process().memory_info().rss / 1024 / 1024
            except Exception:
                pass
        return 0.0

    def _compute_score(self, avg_latency_ms: float, throughput: float) -> float:
        latency_score = max(0.0, 1.0 - avg_latency_ms / 1000.0)
        throughput_score = min(1.0, throughput / 10000.0)
        return 0.5 * latency_score + 0.5 * throughput_score

    def set_baseline(self, benchmark_name: str, score: float) -> None:
        self._baselines[benchmark_name] = score

    def compare_to_baseline(self, run: BenchmarkRun) -> Dict[str, Any]:
        baseline = self._baselines.get(run.benchmark_name)
        if baseline is None:
            return {"status": "no_baseline"}
        delta = run.score - baseline
        return {
            "benchmark": run.benchmark_name,
            "baseline": baseline,
            "current": run.score,
            "delta": delta,
            "improved": delta > 0,
            "regression": delta < -0.05,
        }

    def get_framework_report(self) -> Dict[str, Any]:
        return {
            "suites": len(self._suites),
            "runs": len(self._runs),
            "baselines": len(self._baselines),
            "avg_score": sum(r.score for r in self._runs) / len(self._runs) if self._runs else 0.0,
            "recent_runs": [r.to_dict() for r in self._runs[-10:]],
        }
