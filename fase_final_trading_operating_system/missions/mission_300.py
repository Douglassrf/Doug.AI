# ============================================================
# MISSÃO 300 — DOUG.AI V1.0 CERTIFICATION GATE
# Fase Final — Final Trading Operating System
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class CertificationCriteria:
    """Critério de certificação."""

    id: str = field(default_factory=lambda: f"cc_{uuid.uuid4().hex[:12]}")
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
class CertificationReport:
    """Relatório de certificação."""

    id: str = field(default_factory=lambda: f"cr_{uuid.uuid4().hex[:12]}")
    version: str = "1.0.0"
    verdict: str = "PENDING"
    criteria: List[CertificationCriteria] = field(default_factory=list)
    summary: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    signed_by: str = "Intelligence Council"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "verdict": self.verdict,
            "criteria": [criterion.to_dict() for criterion in self.criteria],
            "summary": self.summary,
            "created_at": self.created_at.isoformat(),
            "signed_by": self.signed_by,
        }


class DougAICertificationGate:
    """
    Portão de certificação Doug.AI v1.0.

    Implementa:
    - GO/NO GO
    - Auditoria geral
    - Cobertura
    - Segurança
    - Governança
    - Prontidão operacional
    """

    def __init__(self):
        self._criteria: List[CertificationCriteria] = []
        self._reports: List[CertificationReport] = []

    def add_criterion(self, name: str, category: str, details: str) -> CertificationCriteria:
        """Adiciona critério de certificação."""
        criterion = CertificationCriteria(name=name, category=category, details=details)
        self._criteria.append(criterion)
        return criterion

    def evaluate_criterion(self, criterion_id: str, passed: bool) -> bool:
        """Avalia critério de certificação."""
        for criterion in self._criteria:
            if criterion.id == criterion_id:
                criterion.status = "passed" if passed else "failed"
                return True
        return False

    def certify(self) -> CertificationReport:
        """Executa certificação final."""
        report = CertificationReport()
        report.criteria = self._criteria.copy()

        passed = sum(1 for criterion in self._criteria if criterion.status == "passed")
        total = len(self._criteria)
        failed = sum(1 for criterion in self._criteria if criterion.status == "failed")
        pending = sum(1 for criterion in self._criteria if criterion.status == "pending")

        if failed > 0:
            report.verdict = "NO_GO"
            report.summary = f"Certification failed. {failed} criteria failed."
        elif pending > 0:
            report.verdict = "PENDING"
            report.summary = f"Certification pending. {pending} criteria not yet evaluated."
        elif passed == total:
            report.verdict = "GO"
            report.summary = f"All {total} criteria passed. Doug.AI v1.0 certified."

        self._reports.append(report)
        return report

    def get_certification_status(self) -> Dict[str, Any]:
        """Retorna status da certificação."""
        total = len(self._criteria)
        passed = sum(1 for criterion in self._criteria if criterion.status == "passed")
        failed = sum(1 for criterion in self._criteria if criterion.status == "failed")
        pending = sum(1 for criterion in self._criteria if criterion.status == "pending")

        return {
            "total_criteria": total,
            "passed": passed,
            "failed": failed,
            "pending": pending,
            "completion": passed / total if total > 0 else 0,
            "latest_report": self._reports[-1].to_dict() if self._reports else None,
        }
