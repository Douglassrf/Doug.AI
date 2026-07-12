from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class SafetyRule:
    id: str = field(default_factory=lambda: f"sr_{uuid.uuid4().hex[:12]}")
    name: str = ""
    description: str = ""
    severity: str = "medium"
    predicate: Optional[Callable[[Dict[str, Any]], bool]] = field(default=None, repr=False)
    violation_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "severity": self.severity,
            "violation_count": self.violation_count,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class SafetyVerificationResult:
    id: str = field(default_factory=lambda: f"svr_{uuid.uuid4().hex[:12]}")
    action: Dict[str, Any] = field(default_factory=dict)
    passed: bool = True
    violated_rules: List[str] = field(default_factory=list)
    severity: str = "none"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action": self.action,
            "passed": self.passed,
            "violated_rules": self.violated_rules,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
        }


class FormalSafetySpecification:
    """Especificação formal de segurança — regras verificáveis, invariantes e bloqueio de ações inseguras."""

    _SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}

    def __init__(self) -> None:
        self._rules: Dict[str, SafetyRule] = {}
        self._verifications: List[SafetyVerificationResult] = []
        self._block_on_critical = True

    def register_rule(
        self,
        name: str,
        predicate: Callable[[Dict[str, Any]], bool],
        description: str = "",
        severity: str = "medium",
    ) -> SafetyRule:
        rule = SafetyRule(name=name, description=description, severity=severity, predicate=predicate)
        self._rules[rule.id] = rule
        return rule

    def verify_action(self, action: Dict[str, Any]) -> SafetyVerificationResult:
        violated: List[str] = []
        max_severity = "none"

        for rule in self._rules.values():
            if rule.predicate is None:
                continue
            try:
                ok = rule.predicate(action)
            except Exception:
                ok = False

            if not ok:
                violated.append(rule.name)
                rule.violation_count += 1
                if self._SEVERITY_ORDER.get(rule.severity, 0) > self._SEVERITY_ORDER.get(max_severity, -1):
                    max_severity = rule.severity

        result = SafetyVerificationResult(
            action=action,
            passed=len(violated) == 0,
            violated_rules=violated,
            severity=max_severity,
        )
        self._verifications.append(result)
        return result

    def is_action_blocked(self, action: Dict[str, Any]) -> bool:
        result = self.verify_action(action)
        if not result.passed and self._block_on_critical:
            return result.severity == "critical"
        return not result.passed

    def get_safety_report(self) -> Dict[str, Any]:
        total = len(self._verifications)
        violations = [v for v in self._verifications if not v.passed]
        return {
            "total_verifications": total,
            "passed": total - len(violations),
            "failed": len(violations),
            "rules": {r.id: r.to_dict() for r in self._rules.values()},
            "recent_violations": [v.to_dict() for v in violations[-10:]],
        }
