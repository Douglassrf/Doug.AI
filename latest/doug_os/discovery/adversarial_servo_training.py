from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np
import random


@dataclass
class AdversarialScenario:
    id: str = field(default_factory=lambda: f"adv_{uuid.uuid4().hex[:12]}")
    name: str = ""
    description: str = ""
    scenario_type: str = ""
    severity: float = 0.0
    duration_hours: float = 0.0
    parameters: Dict[str, Any] = field(default_factory=dict)
    expected_impact: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "name": self.name, "description": self.description,
            "scenario_type": self.scenario_type, "severity": self.severity,
            "duration_hours": self.duration_hours, "parameters": self.parameters,
            "expected_impact": self.expected_impact, "created_at": self.created_at.isoformat(),
        }


@dataclass
class AdversarialResult:
    scenario_id: str = ""
    model_resilience: float = 0.0
    panic_level: float = 0.0
    recovery_time_ms: float = 0.0
    decision_quality: float = 0.0
    weaknesses: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id, "model_resilience": self.model_resilience,
            "panic_level": self.panic_level, "recovery_time_ms": self.recovery_time_ms,
            "decision_quality": self.decision_quality, "weaknesses": self.weaknesses,
            "strengths": self.strengths, "created_at": self.created_at.isoformat(),
        }


class AdversarialServoTraining:
    _SCENARIO_TYPES = [
        "liquidity_crisis", "market_manipulation", "extreme_noise",
        "flash_crash", "regime_change", "data_manipulation", "latency_attack",
    ]

    def __init__(self):
        self._scenarios: List[AdversarialScenario] = []
        self._results: List[AdversarialResult] = []

    def generate_scenarios(self, n_scenarios: int = 10, seed: int = 42) -> List[AdversarialScenario]:
        rng = np.random.default_rng(seed)
        scenarios = []
        for _ in range(n_scenarios):
            stype = self._SCENARIO_TYPES[int(rng.integers(0, len(self._SCENARIO_TYPES)))]
            severity = float(rng.uniform(0.3, 0.9))
            duration = float(rng.uniform(1, 48))
            scenario = AdversarialScenario(
                name=f"{stype.replace('_', ' ').title()} Scenario",
                description=f"Adversarial scenario: {stype}",
                scenario_type=stype, severity=severity, duration_hours=duration,
                parameters=self._generate_parameters(stype, severity, rng),
                expected_impact=float(severity * rng.uniform(0.5, 1.5)),
            )
            scenarios.append(scenario)
            self._scenarios.append(scenario)
        return scenarios

    def _generate_parameters(self, stype: str, severity: float, rng) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "intensity": severity,
            "volatility_multiplier": float(1 + severity * rng.uniform(0.5, 2.0)),
            "noise_level": float(severity * rng.uniform(0.3, 1.0)),
        }
        if stype == "liquidity_crisis":
            params["spread_multiplier"] = float(1 + severity * rng.uniform(1, 5))
            params["depth_reduction"] = float(severity * rng.uniform(0.3, 0.8))
        elif stype == "market_manipulation":
            params["price_deviation"] = float(severity * rng.uniform(0.1, 0.3))
            params["volume_anomaly"] = float(severity * rng.uniform(2, 5))
        elif stype == "flash_crash":
            params["drop_percentage"] = float(severity * rng.uniform(0.05, 0.20))
            params["recovery_speed"] = float(rng.uniform(0.1, 0.5))
        return params

    def run_scenario(self, scenario: AdversarialScenario, model_response: Dict[str, Any]) -> AdversarialResult:
        resilience = self._calculate_resilience(scenario, model_response)
        panic = self._calculate_panic(model_response)
        recovery = float(model_response.get("recovery_time_ms", 0.0))
        decision_quality = float(model_response.get("decision_quality", 0.5))
        weaknesses = self._identify_weaknesses(scenario, model_response, resilience, panic)
        strengths = self._identify_strengths(resilience, panic, decision_quality)
        result = AdversarialResult(
            scenario_id=scenario.id, model_resilience=resilience, panic_level=panic,
            recovery_time_ms=recovery, decision_quality=decision_quality,
            weaknesses=weaknesses, strengths=strengths,
        )
        self._results.append(result)
        return result

    def _calculate_resilience(self, scenario: AdversarialScenario, response: Dict) -> float:
        baseline = response.get("baseline_performance", 0.5)
        stressed = response.get("stressed_performance", 0.0)
        if baseline == 0: return 0.0
        return min(max(stressed / baseline, 0.0), 1.0)

    def _calculate_panic(self, response: Dict) -> float:
        vol = response.get("volatility_increase", 0.0)
        instability = response.get("decision_instability", 0.0)
        return min((vol + instability) / 2, 1.0)

    def _identify_weaknesses(self, scenario, response, resilience, panic) -> List[str]:
        w = []
        if resilience < 0.5: w.append("Low resilience under stress")
        if panic > 0.7: w.append("Panic response to volatility")
        if response.get("latency_increase", 0) > 100: w.append("Slow response under pressure")
        return w

    def _identify_strengths(self, resilience, panic, decision_quality) -> List[str]:
        s = []
        if resilience > 0.8: s.append("High resilience under stress")
        if panic < 0.3: s.append("Stable under volatility")
        if decision_quality > 0.8: s.append("Good decision quality under pressure")
        return s

    def get_resistance_report(self) -> Dict[str, Any]:
        if not self._results: return {"status": "no_data"}
        avg_resilience = float(np.mean([r.model_resilience for r in self._results]))
        avg_panic = float(np.mean([r.panic_level for r in self._results]))
        avg_quality = float(np.mean([r.decision_quality for r in self._results]))
        return {
            "average_resilience": avg_resilience,
            "average_panic": avg_panic,
            "average_decision_quality": avg_quality,
            "total_scenarios": len(self._results),
            "overall_score": (avg_resilience + (1 - avg_panic) + avg_quality) / 3,
        }
