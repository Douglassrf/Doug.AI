# ============================================================
# MISSÃO 303 — SMALL CAPITAL READINESS GATE
# Fase Final — Final Trading Operating System
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class ReadinessCriteria:
    """Critério de prontidão."""

    id: str = field(default_factory=lambda: f"rc_{uuid.uuid4().hex[:12]}")
    name: str = ""
    category: str = ""
    threshold: float = 0.0
    current_value: float = 0.0
    status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "threshold": self.threshold,
            "current_value": self.current_value,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ReadinessReport:
    """Relatório de prontidão."""

    id: str = field(default_factory=lambda: f"rr_{uuid.uuid4().hex[:12]}")
    verdict: str = "PENDING"
    criteria: List[ReadinessCriteria] = field(default_factory=list)
    summary: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    human_review_required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "verdict": self.verdict,
            "criteria": [criterion.to_dict() for criterion in self.criteria],
            "summary": self.summary,
            "created_at": self.created_at.isoformat(),
            "human_review_required": self.human_review_required,
        }


class SmallCapitalReadinessGate:
    """
    Portão de prontidão para capital mínimo.

    Implementa:
    - Critérios mínimos
    - Drawdown máximo
    - Taxa de acerto
    - Expectativa matemática
    - Estabilidade
    - Veredito humano obrigatório
    """

    def __init__(self):
        self._criteria: List[ReadinessCriteria] = []
        self._reports: List[ReadinessReport] = []

    def add_criterion(self, name: str, category: str, threshold: float) -> ReadinessCriteria:
        """Adiciona critério de prontidão."""
        criterion = ReadinessCriteria(name=name, category=category, threshold=threshold)
        self._criteria.append(criterion)
        return criterion

    def evaluate_criterion(self, criterion_id: str, current_value: float) -> bool:
        """Avalia critério de prontidão."""
        for criterion in self._criteria:
            if criterion.id == criterion_id:
                criterion.current_value = current_value
                if criterion.category == "drawdown":
                    criterion.status = "met" if current_value <= criterion.threshold else "not_met"
                else:
                    criterion.status = "met" if current_value >= criterion.threshold else "not_met"
                return True
        return False

    def evaluate_readiness(self) -> ReadinessReport:
        """Avalia prontidão geral."""
        report = ReadinessReport()
        report.criteria = self._criteria.copy()

        met = sum(1 for criterion in self._criteria if criterion.status == "met")
        total = len(self._criteria)
        not_met = sum(1 for criterion in self._criteria if criterion.status == "not_met")
        pending = sum(1 for criterion in self._criteria if criterion.status == "pending")

        if not_met > 0:
            report.verdict = "NOT_READY"
            report.summary = f"System not ready. {not_met} criteria not met."
        elif pending > 0:
            report.verdict = "PENDING"
            report.summary = f"Evaluation pending. {pending} criteria not yet evaluated."
        elif met == total:
            report.verdict = "READY"
            report.summary = f"All {total} criteria met. System ready for small capital."
            report.human_review_required = True

        self._reports.append(report)
        return report

    def get_readiness_status(self) -> Dict[str, Any]:
        """Retorna status de prontidão."""
        total = len(self._criteria)
        met = sum(1 for criterion in self._criteria if criterion.status == "met")
        not_met = sum(1 for criterion in self._criteria if criterion.status == "not_met")
        pending = sum(1 for criterion in self._criteria if criterion.status == "pending")

        return {
            "total_criteria": total,
            "met": met,
            "not_met": not_met,
            "pending": pending,
            "completion": met / total if total > 0 else 0,
            "latest_report": self._reports[-1].to_dict() if self._reports else None,
            "human_review_required": self._reports[-1].human_review_required if self._reports else True,
        }
