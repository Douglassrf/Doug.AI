from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import time
import threading


@dataclass
class ChaosTest:
    id: str = field(default_factory=lambda: f"ct_{uuid.uuid4().hex[:12]}")
    name: str = ""
    type: str = ""
    duration_seconds: int = 0
    severity: str = "medium"
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "duration_seconds": self.duration_seconds,
            "severity": self.severity,
            "status": self.status,
            "result": self.result,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class ResilienceReport:
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    resilience_score: float = 0.0
    avg_recovery_time_seconds: float = 0.0
    critical_failures: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "resilience_score": self.resilience_score,
            "avg_recovery_time_seconds": self.avg_recovery_time_seconds,
            "critical_failures": self.critical_failures,
            "created_at": self.created_at.isoformat(),
        }


_RECOVERY_FACTOR = {
    "module_failure": 0.5,
    "memory_failure": 0.3,
    "latency": 0.2,
    "db_failure": 0.4,
    "data_feed": 0.25,
}


class ChaosTestingLaboratory:
    """Laboratório de testes de caos com simulação de falhas e relatório de resiliência."""

    def __init__(self) -> None:
        self._tests: Dict[str, ChaosTest] = {}
        self._reports: List[ResilienceReport] = []

    def schedule_chaos_test(
        self,
        name: str,
        test_type: str,
        duration_seconds: int = 30,
        severity: str = "medium",
    ) -> ChaosTest:
        test = ChaosTest(name=name, type=test_type, duration_seconds=duration_seconds, severity=severity)
        self._tests[test.id] = test
        return test

    def run_test(self, test_id: str) -> ChaosTest:
        test = self._tests.get(test_id)
        if not test:
            raise ValueError(f"Test {test_id} not found")

        test.started_at = datetime.now(timezone.utc)
        test.status = "running"

        try:
            result = self._simulate_failure(test.type, test.duration_seconds)
            test.result = result
            test.status = "completed"
        except Exception as exc:
            test.status = "failed"
            test.result = {"error": str(exc)}
        finally:
            test.completed_at = datetime.now(timezone.utc)

        return test

    def _simulate_failure(self, failure_type: str, duration_seconds: int) -> Dict[str, Any]:
        factor = _RECOVERY_FACTOR.get(failure_type, 0.1)
        recovery_time = duration_seconds * factor
        return {
            "type": failure_type,
            "recovered": True,
            "recovery_time_seconds": recovery_time,
        }

    def generate_resilience_report(self) -> ResilienceReport:
        total = len(self._tests)
        completed = [t for t in self._tests.values() if t.status == "completed"]
        failed = [t for t in self._tests.values() if t.status == "failed"]

        recovery_times = [
            t.result.get("recovery_time_seconds", 0)
            for t in completed
            if t.result
        ]
        avg_recovery = sum(recovery_times) / len(recovery_times) if recovery_times else 0.0

        report = ResilienceReport(
            total_tests=total,
            passed_tests=len(completed),
            failed_tests=len(failed),
            resilience_score=len(completed) / total if total else 0.0,
            avg_recovery_time_seconds=avg_recovery,
            critical_failures=sum(1 for t in failed if t.severity == "high"),
        )
        self._reports.append(report)
        return report

    def get_tests(self) -> List[ChaosTest]:
        return list(self._tests.values())

    def get_reports(self, limit: int = 10) -> List[ResilienceReport]:
        return self._reports[-limit:]
