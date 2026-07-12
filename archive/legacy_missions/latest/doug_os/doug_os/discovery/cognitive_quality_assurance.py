from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class QAReport:
    id: str = field(default_factory=lambda: f"qa_{uuid.uuid4().hex[:12]}")
    component: str = ""
    quality_score: float = 0.0
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    passed: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "component": self.component,
            "quality_score": self.quality_score,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "passed": self.passed,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class QAMetrics:
    component: str = ""
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    quality_trend: List[float] = field(default_factory=list)
    last_check: Optional[datetime] = None
    overall_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component": self.component,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "quality_trend": self.quality_trend[-10:],
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "overall_score": self.overall_score,
        }


class CognitiveQualityAssurance:
    """Garantia de qualidade cognitiva para módulos Doug.AI."""

    _COMPONENTS = (
        "decision", "prediction", "learning", "memory",
        "risk", "discovery", "architecture", "regression",
    )

    def __init__(self) -> None:
        self._reports: List[QAReport] = []
        self._metrics: Dict[str, QAMetrics] = {c: QAMetrics(component=c) for c in self._COMPONENTS}

    def register_component(self, component: str) -> None:
        if component not in self._metrics:
            self._metrics[component] = QAMetrics(component=component)

    def check_component(
        self,
        component: str,
        checks: Dict[str, Dict[str, Any]],
    ) -> QAReport:
        if component not in self._metrics:
            raise ValueError(f"Unknown component: {component}")

        issues: List[str] = []
        recs: List[str] = []
        passed_cnt = 0
        total = len(checks)

        for name, result in checks.items():
            if result.get("passed", False):
                passed_cnt += 1
            else:
                issues.append(f"{name}: {result.get('issue', 'unknown issue')}")
                if "recommendation" in result:
                    recs.append(result["recommendation"])

        score = passed_cnt / total if total else 0.0
        passed = score >= 0.8

        report = QAReport(
            component=component,
            quality_score=score,
            issues=issues,
            recommendations=recs,
            passed=passed,
        )
        self._reports.append(report)

        m = self._metrics[component]
        m.total_checks += total
        m.passed_checks += passed_cnt
        m.failed_checks += total - passed_cnt
        m.quality_trend.append(score)
        m.last_check = datetime.now(timezone.utc)
        m.overall_score = m.passed_checks / m.total_checks if m.total_checks else 0.0

        return report

    def get_component_metrics(self, component: str) -> Optional[QAMetrics]:
        return self._metrics.get(component)

    def get_latest_report(self, component: str) -> Optional[QAReport]:
        for report in reversed(self._reports):
            if report.component == component:
                return report
        return None

    def get_qa_dashboard(self) -> Dict[str, Any]:
        overall = (
            sum(m.overall_score for m in self._metrics.values()) / len(self._metrics)
            if self._metrics else 0.0
        )
        return {
            "total_reports": len(self._reports),
            "components": {c: m.to_dict() for c, m in self._metrics.items()},
            "overall_quality": overall,
            "critical_issues": sum(1 for r in self._reports if r.quality_score < 0.5),
        }
