# ============================================================
# MISSÃO 329 — OMEGA CERTIFICATION GATE (v1.0)
# Fase Ômega Final — Doug.AI v1.0
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class CertificationCriteria:
    """Critério de certificação Omega."""

    id: str = field(default_factory=lambda: f"occ_{uuid.uuid4().hex[:12]}")
    name: str = ""
    category: str = ""
    phase: str = ""
    status: str = "pending"
    details: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "phase": self.phase,
            "status": self.status,
            "details": self.details,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class OmegaCertificationReport:
    """Relatório de certificação final Doug.AI v1.0."""

    id: str = field(default_factory=lambda: f"ocr_{uuid.uuid4().hex[:12]}")
    version: str = "1.0.0"
    verdict: str = "PENDING"
    criteria: List[CertificationCriteria] = field(default_factory=list)
    summary: str = ""
    signed_by: str = "Omega Intelligence Council"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "verdict": self.verdict,
            "criteria": [criterion.to_dict() for criterion in self.criteria],
            "summary": self.summary,
            "signed_by": self.signed_by,
            "created_at": self.created_at.isoformat(),
        }


class OmegaCertificationGate:
    """
    Portão final GO/NO-GO para Doug.AI v1.0.

    Agrega critérios de todas as fases anteriores.
    """

    REQUIRED_CATEGORIES = (
        "architecture",
        "security",
        "governance",
        "performance",
        "memory",
        "integration",
    )

    def __init__(self):
        self._criteria: List[CertificationCriteria] = []
        self._reports: List[OmegaCertificationReport] = []

    def add_criterion(
        self,
        name: str,
        category: str,
        phase: str,
        details: str,
    ) -> CertificationCriteria:
        """Adiciona critério de certificação."""
        criterion = CertificationCriteria(
            name=name,
            category=category,
            phase=phase,
            details=details,
        )
        self._criteria.append(criterion)
        return criterion

    def evaluate_criterion(self, criterion_id: str, passed: bool) -> bool:
        """Avalia critério."""
        for criterion in self._criteria:
            if criterion.id == criterion_id:
                criterion.status = "passed" if passed else "failed"
                return True
        return False

    def register_phase_verdict(self, phase: str, verdict: str) -> None:
        """Registra veredicto de fase como critério automático."""
        passed = verdict.upper() in {"GO", "PASS", "READY", "LAUNCHED", "STABLE"}
        criterion = self.add_criterion(
            name=f"{phase} phase verdict",
            category="integration",
            phase=phase,
            details=f"Phase verdict: {verdict}",
        )
        self.evaluate_criterion(criterion.id, passed)

    def certify(self) -> OmegaCertificationReport:
        """Executa certificação final."""
        report = OmegaCertificationReport(criteria=self._criteria.copy())

        passed = sum(1 for criterion in self._criteria if criterion.status == "passed")
        failed = sum(1 for criterion in self._criteria if criterion.status == "failed")
        pending = sum(1 for criterion in self._criteria if criterion.status == "pending")
        total = len(self._criteria)

        categories_covered = {criterion.category for criterion in self._criteria}
        missing_categories = [
            category
            for category in self.REQUIRED_CATEGORIES
            if category not in categories_covered
        ]

        if failed > 0:
            report.verdict = "NO_GO"
            report.summary = f"Certification failed. {failed} criteria failed."
        elif pending > 0 or missing_categories:
            report.verdict = "PENDING"
            parts = []
            if pending > 0:
                parts.append(f"{pending} criteria pending")
            if missing_categories:
                parts.append(f"missing categories: {', '.join(missing_categories)}")
            report.summary = "Certification pending. " + "; ".join(parts) + "."
        elif passed == total and total > 0:
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
            "version": "1.0.0",
            "total_criteria": total,
            "passed": passed,
            "failed": failed,
            "pending": pending,
            "completion": passed / total if total > 0 else 0,
            "latest_report": self._reports[-1].to_dict() if self._reports else None,
        }
