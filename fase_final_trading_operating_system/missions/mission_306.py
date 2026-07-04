# ============================================================
# MISSÃO 306 — FULL AUTONOMOUS OPERATIONS GATE
# Fase Final — Final Trading Operating System
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class OperationalCriterion:
    """Critério operacional para autonomia total."""

    id: str = field(default_factory=lambda: f"oc_{uuid.uuid4().hex[:12]}")
    name: str = ""
    category: str = ""
    status: str = "pending"
    details: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "status": self.status,
            "details": self.details,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class AutonomousOperationsReport:
    """Relatório final GO/NO-GO para operações autônomas."""

    id: str = field(default_factory=lambda: f"aor_{uuid.uuid4().hex[:12]}")
    verdict: str = "PENDING"
    gates_status: Dict[str, bool] = field(default_factory=dict)
    criteria: List[OperationalCriterion] = field(default_factory=list)
    summary: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "verdict": self.verdict,
            "gates_status": self.gates_status,
            "criteria": [criterion.to_dict() for criterion in self.criteria],
            "summary": self.summary,
            "created_at": self.created_at.isoformat(),
        }


class FullAutonomousOperationsGate:
    """
    Portão final para operações autônomas.

    Implementa:
    - Verificação de todos os gates anteriores
    - Critérios operacionais
    - GO/NO-GO final
    """

    REQUIRED_GATES = (
        "certification",
        "readiness",
        "micro_live",
        "paper_trading",
        "shadow_mode",
    )

    def __init__(self):
        self._gate_status: Dict[str, bool] = {gate: False for gate in self.REQUIRED_GATES}
        self._criteria: List[OperationalCriterion] = []
        self._reports: List[AutonomousOperationsReport] = []

    def register_gate_status(self, gate_name: str, passed: bool) -> bool:
        """Registra status de gate anterior."""
        if gate_name not in self._gate_status:
            return False
        self._gate_status[gate_name] = passed
        return True

    def add_criterion(self, name: str, category: str, details: str) -> OperationalCriterion:
        """Adiciona critério operacional."""
        criterion = OperationalCriterion(name=name, category=category, details=details)
        self._criteria.append(criterion)
        return criterion

    def evaluate_criterion(self, criterion_id: str, passed: bool) -> bool:
        """Avalia critério operacional."""
        for criterion in self._criteria:
            if criterion.id == criterion_id:
                criterion.status = "passed" if passed else "failed"
                return True
        return False

    def evaluate_autonomous_readiness(self) -> AutonomousOperationsReport:
        """Avalia prontidão para operações autônomas."""
        report = AutonomousOperationsReport(gates_status=self._gate_status.copy())
        report.criteria = self._criteria.copy()

        gates_passed = all(self._gate_status.values())
        failed_criteria = sum(1 for criterion in self._criteria if criterion.status == "failed")
        pending_criteria = sum(1 for criterion in self._criteria if criterion.status == "pending")
        passed_criteria = sum(1 for criterion in self._criteria if criterion.status == "passed")

        if not gates_passed:
            report.verdict = "NO_GO"
            missing = [gate for gate, ok in self._gate_status.items() if not ok]
            report.summary = f"Required gates not passed: {', '.join(missing)}"
        elif failed_criteria > 0:
            report.verdict = "NO_GO"
            report.summary = f"{failed_criteria} operational criteria failed."
        elif pending_criteria > 0:
            report.verdict = "PENDING"
            report.summary = f"{pending_criteria} operational criteria pending."
        elif passed_criteria == len(self._criteria) and gates_passed:
            report.verdict = "GO"
            report.summary = "All gates and criteria passed. Autonomous operations authorized."

        self._reports.append(report)
        return report

    def get_operations_status(self) -> Dict[str, Any]:
        """Retorna status operacional."""
        return {
            "gates_status": self._gate_status.copy(),
            "gates_passed": sum(1 for passed in self._gate_status.values() if passed),
            "total_gates": len(self._gate_status),
            "criteria_total": len(self._criteria),
            "criteria_passed": sum(1 for criterion in self._criteria if criterion.status == "passed"),
            "criteria_failed": sum(1 for criterion in self._criteria if criterion.status == "failed"),
            "criteria_pending": sum(1 for criterion in self._criteria if criterion.status == "pending"),
            "latest_report": self._reports[-1].to_dict() if self._reports else None,
        }
