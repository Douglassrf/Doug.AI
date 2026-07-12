# ============================================================
# MISSÃO 317 — FASE XXI CERTIFICATION GATE
# Fase XXI — Evolutionary Trading Intelligence
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class CertificationReport:
    """Relatório de certificação GO/NO-GO."""

    id: str = field(default_factory=lambda: f"cert_{uuid.uuid4().hex[:12]}")
    verdict: str = "NO-GO"
    criteria: Dict[str, bool] = field(default_factory=dict)
    score: float = 0.0
    blockers: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "verdict": self.verdict,
            "criteria": self.criteria,
            "score": self.score,
            "blockers": self.blockers,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat(),
        }


class FaseXXICertificationGate:
    """
    Portão de certificação GO/NO-GO da Fase XXI.

    Implementa:
    - Criteria Evaluation
    - Report Generation
    - Status Dashboard
    """

    CRITERIA_THRESHOLDS = {
        "evolution_engine_active": lambda d: d.get("evolution", {}).get("total_reports", 0) >= 1,
        "lifecycle_tracking_active": lambda d: d.get("lifecycle", {}).get("total_strategies", 0) >= 1,
        "pattern_intelligence_active": lambda d: d.get("patterns", {}).get("total_patterns", 0) >= 1,
        "memory_network_active": lambda d: d.get("memory", {}).get("total_memories", 0) >= 1,
        "liquidity_engine_active": lambda d: (
            d.get("liquidity", {}).get("total_predictions", 0) >= 1
            or d.get("liquidity", {}).get("status") != "no_data"
        ),
        "alpha_analyzer_active": lambda d: d.get("alpha", {}).get("total_analyses", 0) >= 1,
        "mutation_engine_active": lambda d: d.get("mutations", {}).get("total_candidates", 0) >= 1,
        "ecosystem_health_ok": lambda d: d.get("ecosystem_health", 0.0) >= 0.4,
        "learning_loop_active": lambda d: d.get("learning", {}).get("total_cycles", 0) >= 1,
    }

    def __init__(self):
        self._reports: List[CertificationReport] = []

    def evaluate(self, ecosystem_data: Dict[str, Any]) -> CertificationReport:
        """Avalia critérios e gera veredito GO/NO-GO."""
        criteria: Dict[str, bool] = {}
        blockers: List[str] = []

        for name, evaluator in self.CRITERIA_THRESHOLDS.items():
            passed = bool(evaluator(ecosystem_data))
            criteria[name] = passed
            if not passed:
                blockers.append(name)

        passed_count = sum(1 for v in criteria.values() if v)
        score = passed_count / len(criteria) if criteria else 0.0
        verdict = "GO" if score >= 0.75 and len(blockers) <= 2 else "NO-GO"
        recommendations = self._generate_recommendations(criteria, ecosystem_data)

        report = CertificationReport(
            verdict=verdict,
            criteria=criteria,
            score=score,
            blockers=blockers,
            recommendations=recommendations,
        )
        self._reports.append(report)
        return report

    def _generate_recommendations(
        self, criteria: Dict[str, bool], data: Dict[str, Any]
    ) -> List[str]:
        """Gera recomendações para critérios falhos."""
        recommendations: List[str] = []

        if not criteria.get("evolution_engine_active"):
            recommendations.append("Execute market evolution analysis before certification.")
        if not criteria.get("ecosystem_health_ok"):
            recommendations.append(
                f"Improve ecosystem health (current: {data.get('ecosystem_health', 0.0):.2f})."
            )
        if not criteria.get("learning_loop_active"):
            recommendations.append("Run at least one evolutionary learning cycle.")

        if not recommendations and all(criteria.values()):
            recommendations.append("All criteria met — phase ready for operational deployment.")

        return recommendations

    def get_certification_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de certificação."""
        latest = self._reports[-1].to_dict() if self._reports else {}
        return {
            "total_evaluations": len(self._reports),
            "latest_verdict": latest.get("verdict", "PENDING"),
            "latest_score": latest.get("score", 0.0),
            "latest_blockers": latest.get("blockers", []),
            "latest_report": latest,
        }
