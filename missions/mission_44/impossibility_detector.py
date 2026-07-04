from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional


@dataclass
class ImpossibilityCheck:
    is_impossible: bool = False
    reason: str = ""
    confidence: float = 0.0
    violations: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    veto: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_impossible": self.is_impossible,
            "reason": self.reason,
            "confidence": self.confidence,
            "violations": self.violations,
            "suggestions": self.suggestions,
            "veto": self.veto,
        }


class ImpossibilityDetector:
    """
    Detector de impossibilidades cientificas e logicas.
    Firewall que bloqueia hipoteses que violam principios fundamentais.
    """

    _KNOWN_IMPOSSIBILITIES = [
        "perpetual_motion",
        "negative_risk_free_rate",
        "guaranteed_arbitrage",
        "perfect_prediction",
        "zero_variance_portfolio",
    ]

    _CONTRADICTION_PAIRS = [
        ("increase", "decrease"),
        ("buy", "sell"),
        ("high", "low"),
        ("certain", "uncertain"),
        ("risk_free", "risky"),
    ]

    def check(self, hypothesis: str, variables: Dict[str, Any]) -> ImpossibilityCheck:
        violations: List[str] = []
        suggestions: List[str] = []

        # 1. Logica — contradicoes internas
        logic_ok, logic_msg = self._logical_check(hypothesis)
        if not logic_ok:
            violations.append(f"Logical: {logic_msg}")
            suggestions.append(f"Remove contradiction: {logic_msg}")

        # 2. Estatistica — valores impossiveis
        stat_ok, stat_msg = self._statistical_check(variables)
        if not stat_ok:
            violations.append(f"Statistical: {stat_msg}")
            suggestions.append(f"Adjust: {stat_msg}")

        # 3. Probabilistica — probabilidades invalidas
        prob_ok, prob_msg = self._probabilistic_check(variables)
        if not prob_ok:
            violations.append(f"Probabilistic: {prob_msg}")
            suggestions.append(f"Fix probability: {prob_msg}")

        # 4. Impossibilidades conhecidas
        known_impossible, known_msg = self._known_impossibility_check(hypothesis)
        if known_impossible:
            violations.append(f"Known impossibility: {known_msg}")
            suggestions.append("This violates fundamental principles — discard hypothesis")

        is_impossible = len(violations) >= 2
        veto = len(violations) >= 3
        confidence = 1.0 - len(violations) / max(len(violations) + 1, 1)

        return ImpossibilityCheck(
            is_impossible=is_impossible,
            reason="; ".join(violations) if violations else "No issues detected",
            confidence=confidence,
            violations=violations,
            suggestions=suggestions,
            veto=veto,
        )

    def _logical_check(self, hypothesis: str) -> Tuple[bool, str]:
        h = hypothesis.lower()
        for a, b in self._CONTRADICTION_PAIRS:
            if a in h and b in h:
                return False, f"Contradiction: '{a}' and '{b}' cannot coexist"
        return True, ""

    def _statistical_check(self, variables: Dict[str, Any]) -> Tuple[bool, str]:
        # Variancia negativa e impossivel
        if variables.get("variance", 0) < 0:
            return False, "Variance cannot be negative"
        # Correlacao fora de [-1, 1]
        corr = variables.get("correlation", 0)
        if abs(corr) > 1.0:
            return False, f"Correlation {corr} out of [-1, 1]"
        # Probabilidade fora de [0, 1]
        prob = variables.get("probability", 0.5)
        if not (0.0 <= prob <= 1.0):
            return False, f"Probability {prob} out of [0, 1]"
        return True, ""

    def _probabilistic_check(self, variables: Dict[str, Any]) -> Tuple[bool, str]:
        # Soma de probabilidades exclusivas > 1
        probs = [v for k, v in variables.items() if k.startswith("prob_")]
        if probs and sum(probs) > 1.0 + 1e-9:
            return False, f"Sum of exclusive probabilities {sum(probs):.4f} > 1"
        # Expected return impossivel (> 100% garantido)
        if variables.get("guaranteed_return", 0) > 1.0:
            return False, "Guaranteed return > 100% is impossible"
        return True, ""

    def _known_impossibility_check(self, hypothesis: str) -> Tuple[bool, str]:
        h = hypothesis.lower().replace(" ", "_")
        for impossibility in self._KNOWN_IMPOSSIBILITIES:
            if impossibility in h:
                return True, impossibility
        return False, ""
