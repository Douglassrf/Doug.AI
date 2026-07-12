from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class DecisionVerification:
    id: str = field(default_factory=lambda: f"dv_{uuid.uuid4().hex[:12]}")
    decision_id: str = ""
    verified: bool = False
    invariants_passed: List[str] = field(default_factory=list)
    invariants_failed: List[str] = field(default_factory=list)
    safety_violations: List[str] = field(default_factory=list)
    capital_check_passed: bool = False
    risk_veto_triggered: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "decision_id": self.decision_id,
            "verified": self.verified,
            "invariants_passed": self.invariants_passed,
            "invariants_failed": self.invariants_failed,
            "safety_violations": self.safety_violations,
            "capital_check_passed": self.capital_check_passed,
            "risk_veto_triggered": self.risk_veto_triggered,
            "created_at": self.created_at.isoformat(),
        }


class FormalDecisionVerification:
    """Verificação formal de decisões: invariantes, preservação de capital e veto de risco."""

    def __init__(self) -> None:
        self._verifications: Dict[str, DecisionVerification] = {}
        self._invariants: Dict[str, Callable] = {}
        self._safety_rules: List[Callable] = []

    def register_invariant(self, name: str, check_func: Callable) -> None:
        self._invariants[name] = check_func

    def register_safety_rule(self, check_func: Callable) -> None:
        self._safety_rules.append(check_func)

    def verify_decision(self, decision: Dict[str, Any]) -> DecisionVerification:
        verification = DecisionVerification(decision_id=decision.get("id", ""))

        passed: List[str] = []
        failed: List[str] = []

        for name, func in self._invariants.items():
            try:
                if func(decision):
                    passed.append(name)
                else:
                    failed.append(name)
            except Exception:
                failed.append(name)

        verification.invariants_passed = passed
        verification.invariants_failed = failed

        violations: List[str] = []
        for rule in self._safety_rules:
            try:
                if not rule(decision):
                    violations.append(getattr(rule, "__name__", "anonymous_rule"))
            except Exception:
                violations.append("rule_exception")
        verification.safety_violations = violations

        verification.capital_check_passed = self._check_capital_preservation(decision)
        verification.risk_veto_triggered = self._check_risk_veto(decision)

        verification.verified = (
            len(failed) == 0
            and len(violations) == 0
            and verification.capital_check_passed
            and not verification.risk_veto_triggered
        )

        self._verifications[verification.id] = verification
        return verification

    def _check_capital_preservation(self, decision: Dict[str, Any]) -> bool:
        risk_amount = decision.get("risk_amount", 0)
        capital = decision.get("capital", 100)
        return risk_amount <= capital * 0.02

    def _check_risk_veto(self, decision: Dict[str, Any]) -> bool:
        return decision.get("risk_score", 0) > 0.8

    def get_verification(self, verification_id: str) -> Optional[DecisionVerification]:
        return self._verifications.get(verification_id)

    def get_all_verifications(self) -> List[DecisionVerification]:
        return list(self._verifications.values())
