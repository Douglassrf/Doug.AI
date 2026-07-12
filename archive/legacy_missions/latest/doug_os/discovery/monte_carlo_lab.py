from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Callable
import numpy as np
import uuid


@dataclass
class MonteCarloResult:
    id: str = field(default_factory=lambda: f"mc_{uuid.uuid4().hex[:12]}")
    hypothesis_id: str = ""
    mean: float = 0.0
    median: float = 0.0
    std: float = 0.0
    min: float = 0.0
    max: float = 0.0
    robustness_score: float = 0.0
    variance_score: float = 0.0
    failure_probability: float = 0.0
    confidence_interval_90: Tuple[float, float] = (0.0, 0.0)
    confidence_interval_95: Tuple[float, float] = (0.0, 0.0)
    confidence_interval_99: Tuple[float, float] = (0.0, 0.0)
    bootstrap_estimates: List[float] = field(default_factory=list)
    stress_results: List[Dict[str, Any]] = field(default_factory=list)
    iterations: int = 1000
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "hypothesis_id": self.hypothesis_id,
            "mean": self.mean,
            "median": self.median,
            "std": self.std,
            "min": self.min,
            "max": self.max,
            "robustness_score": self.robustness_score,
            "variance_score": self.variance_score,
            "failure_probability": self.failure_probability,
            "confidence_interval_90": list(self.confidence_interval_90),
            "confidence_interval_95": list(self.confidence_interval_95),
            "confidence_interval_99": list(self.confidence_interval_99),
            "iterations": self.iterations,
            "created_at": self.created_at.isoformat(),
        }


class MonteCarloAdaptiveLab:
    """Laboratorio Monte Carlo adaptativo com convergencia, bootstrap e stress test."""

    _STRESS_SCENARIOS = [
        ("normal", 0.9, 1.1),
        ("high_volatility", 0.5, 2.0),
        ("extreme", 0.1, 5.0),
        ("low_liquidity", 0.7, 1.3),
        ("crash", 0.05, 1.5),
        ("recovery", 0.8, 2.5),
    ]

    def __init__(self, seed: Optional[int] = None):
        self._rng = np.random.default_rng(seed)
        self._results: Dict[str, MonteCarloResult] = {}

    def run_simulation(
        self,
        hypothesis_id: str,
        model: Callable[[Dict[str, Any]], float],
        parameters: Dict[str, Any],
        iterations: int = 10_000,
        convergence_threshold: float = 0.01,
    ) -> MonteCarloResult:
        results: List[float] = []
        actual_iterations = iterations

        for i in range(iterations):
            results.append(model(parameters))
            if i >= 200 and i % 100 == 0:
                prev_mean = float(np.mean(results[: i - 100]))
                curr_mean = float(np.mean(results))
                if prev_mean != 0.0 and abs(curr_mean - prev_mean) / abs(prev_mean) < convergence_threshold:
                    actual_iterations = i + 1
                    break

        arr = np.array(results, dtype=float)
        mean = float(np.mean(arr))
        median = float(np.median(arr))
        std = float(np.std(arr))
        min_val = float(np.min(arr))
        max_val = float(np.max(arr))

        ci_90 = (float(np.percentile(arr, 5)), float(np.percentile(arr, 95)))
        ci_95 = (float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5)))
        ci_99 = (float(np.percentile(arr, 0.5)), float(np.percentile(arr, 99.5)))

        robustness_score = min(1.0 / (1.0 + (std / abs(mean)) if mean != 0 else 1.0), 1.0)
        variance_score = max(0.0, 1.0 - min(std / (abs(mean) if mean != 0 else 1.0), 1.0))

        failure_threshold = float(parameters.get("failure_threshold", float("-inf")))
        failure_probability = float(np.mean(arr < failure_threshold))

        bootstrap_estimates = self._bootstrap(results, n_samples=500)
        stress_results = self._stress_test(model, parameters)

        mc_result = MonteCarloResult(
            hypothesis_id=hypothesis_id,
            mean=mean,
            median=median,
            std=std,
            min=min_val,
            max=max_val,
            robustness_score=robustness_score,
            variance_score=variance_score,
            failure_probability=failure_probability,
            confidence_interval_90=ci_90,
            confidence_interval_95=ci_95,
            confidence_interval_99=ci_99,
            bootstrap_estimates=bootstrap_estimates,
            stress_results=stress_results,
            iterations=actual_iterations,
        )
        self._results[mc_result.id] = mc_result
        return mc_result

    def _bootstrap(self, data: List[float], n_samples: int = 500) -> List[float]:
        arr = np.array(data, dtype=float)
        return [
            float(np.mean(self._rng.choice(arr, size=len(arr), replace=True)))
            for _ in range(n_samples)
        ]

    def _stress_test(
        self, model: Callable[[Dict[str, Any]], float], parameters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        results = []
        base = float(parameters.get("base", 1.0))
        for name, low_mult, high_mult in self._STRESS_SCENARIOS:
            test_params = {**parameters, "min": base * low_mult, "max": base * high_mult}
            try:
                val = model(test_params)
                results.append({"scenario": name, "result": val, "passed": True})
            except Exception as exc:
                results.append({"scenario": name, "error": str(exc), "passed": False})
        return results

    def get_result(self, result_id: str) -> Optional[MonteCarloResult]:
        return self._results.get(result_id)
