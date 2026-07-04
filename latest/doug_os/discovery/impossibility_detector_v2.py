from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
import re


@dataclass
class ImpossibilityReport:
    is_impossible: bool = False
    confidence: float = 1.0
    violations: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    veto: bool = False
    veto_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_impossible": self.is_impossible,
            "confidence": self.confidence,
            "violations": self.violations,
            "suggestions": self.suggestions,
            "veto": self.veto,
            "veto_reason": self.veto_reason,
        }


class ImpossibilityDetectorV2:
    """Detector de impossibilidades científicas e lógicas — versão completa."""

    _LOGICAL_RULES = [
        ("perpetual_motion", r"(profit|return|gain).{0,20}(100%|infinite|unlimited|always)"),
        ("negative_risk", r"risk.{0,10}(negative|< ?0|below zero)"),
        ("guaranteed_arbitrage", r"(arbitrage|risk.free).{0,15}(guaranteed|100%)"),
        ("perfect_prediction", r"(predict|forecast).{0,15}(100%|perfect|exact|always)"),
        ("zero_variance", r"(variance|volatility).{0,10}(zero|= ?0)"),
    ]

    _CONTRADICTION_PAIRS = [
        ("increase", "decrease"),
        ("buy", "sell"),
        ("certain", "uncertain"),
        ("risk_free", "risky"),
    ]

    def __init__(self):
        self._stat_thresholds = {
            "min_sample": 30,
            "max_correlation": 0.95,
            "max_p_value": 0.05,
        }
        self._prob_thresholds = {"max": 0.999, "min": 0.001}

    def check(self, hypothesis: str, variables: Dict[str, Any]) -> ImpossibilityReport:
        violations: List[str] = []
        suggestions: List[str] = []
        confidence = 1.0

        ok, msg, sug = self._logical_check(hypothesis)
        if not ok:
            violations.append(f"Logical: {msg}")
            suggestions.append(sug)
            confidence *= 0.7

        ok, msg, sug = self._contradiction_check(hypothesis)
        if not ok:
            violations.append(f"Contradiction: {msg}")
            suggestions.append(sug)
            confidence *= 0.8

        ok, msg, sug = self._statistical_check(variables)
        if not ok:
            violations.append(f"Statistical: {msg}")
            suggestions.append(sug)
            confidence *= 0.7

        ok, msg, sug = self._probabilistic_check(variables)
        if not ok:
            violations.append(f"Probabilistic: {msg}")
            suggestions.append(sug)
            confidence *= 0.7

        is_impossible = len(violations) >= 2
        veto = len(violations) >= 3
        return ImpossibilityReport(
            is_impossible=is_impossible,
            confidence=confidence,
            violations=violations,
            suggestions=suggestions,
            veto=veto,
            veto_reason="Multiple impossibility violations" if veto else "",
        )

    def _logical_check(self, hypothesis: str) -> Tuple[bool, str, str]:
        h = hypothesis.lower()
        for rule_name, pattern in self._LOGICAL_RULES:
            if re.search(pattern, h):
                return False, f"{rule_name} detected", f"Remove '{rule_name}' concept from hypothesis"
        return True, "", ""

    def _contradiction_check(self, hypothesis: str) -> Tuple[bool, str, str]:
        h = hypothesis.lower()
        for a, b in self._CONTRADICTION_PAIRS:
            if a in h and b in h:
                return False, f"'{a}' and '{b}' coexist", f"Remove one of: {a}, {b}"
        return True, "", ""

    def _statistical_check(self, variables: Dict[str, Any]) -> Tuple[bool, str, str]:
        sample = variables.get("sample_size", self._stat_thresholds["min_sample"])
        if sample < self._stat_thresholds["min_sample"]:
            return False, f"Sample size {sample} < {self._stat_thresholds['min_sample']}", "Increase sample size"
        corr = variables.get("correlation", 0.0)
        if abs(corr) > self._stat_thresholds["max_correlation"]:
            return False, f"Correlation {corr:.2f} > {self._stat_thresholds['max_correlation']}", "Check multicollinearity"
        p = variables.get("p_value", 0.01)
        if p > self._stat_thresholds["max_p_value"]:
            return False, f"p-value {p:.3f} > {self._stat_thresholds['max_p_value']}", "Not significant"
        return True, "", ""

    def _probabilistic_check(self, variables: Dict[str, Any]) -> Tuple[bool, str, str]:
        prob = variables.get("probability", 0.5)
        if prob > self._prob_thresholds["max"]:
            return False, f"Probability {prob} > {self._prob_thresholds['max']}", "Probability unrealistically high"
        if prob < self._prob_thresholds["min"]:
            return False, f"Probability {prob} < {self._prob_thresholds['min']}", "Probability unrealistically low"
        probs = [v for k, v in variables.items() if k.startswith("prob_")]
        if probs and sum(probs) > 1.0 + 1e-9:
            return False, f"Exclusive probs sum={sum(probs):.4f} > 1", "Probabilities must sum <= 1"
        return True, "", ""
