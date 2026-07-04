# ============================================================
# MISSÃO 327 — OMEGA SECURITY FORTRESS
# Fase Ômega Final — Doug.AI v1.0
# ============================================================

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class SecurityThreat:
    """Ameaça detectada."""

    id: str = field(default_factory=lambda: f"st_{uuid.uuid4().hex[:12]}")
    threat_type: str = ""
    severity: str = "medium"
    source: str = ""
    description: str = ""
    mitigated: bool = False
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "threat_type": self.threat_type,
            "severity": self.severity,
            "source": self.source,
            "description": self.description,
            "mitigated": self.mitigated,
            "detected_at": self.detected_at.isoformat(),
        }


@dataclass
class SecurityReport:
    """Relatório de segurança."""

    id: str = field(default_factory=lambda: f"sr_{uuid.uuid4().hex[:12]}")
    audit_score: float = 0.0
    threats_detected: int = 0
    threats_mitigated: int = 0
    access_violations: int = 0
    verdict: str = "PENDING"
    findings: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "audit_score": self.audit_score,
            "threats_detected": self.threats_detected,
            "threats_mitigated": self.threats_mitigated,
            "access_violations": self.access_violations,
            "verdict": self.verdict,
            "findings": self.findings,
            "created_at": self.created_at.isoformat(),
        }


class OmegaSecurityFortress:
    """
    Fortaleza de segurança Doug.AI.

    Implementa auditoria, controle de acesso e detecção de ameaças.
    """

    def __init__(self):
        self._allowed_roles: Dict[str, Set[str]] = {
            "admin": {"read", "write", "execute", "audit"},
            "operator": {"read", "write", "execute"},
            "viewer": {"read"},
        }
        self._user_roles: Dict[str, str] = {}
        self._threats: List[SecurityThreat] = []
        self._access_log: List[Dict[str, Any]] = []
        self._reports: List[SecurityReport] = []

    def register_user(self, user_id: str, role: str) -> bool:
        """Registra usuário com role."""
        if role not in self._allowed_roles:
            return False
        self._user_roles[user_id] = role
        return True

    def check_access(self, user_id: str, action: str) -> bool:
        """Verifica permissão de acesso."""
        role = self._user_roles.get(user_id)
        allowed = role is not None and action in self._allowed_roles.get(role, set())

        self._access_log.append(
            {
                "user_id": user_id,
                "action": action,
                "allowed": allowed,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        if not allowed:
            self.detect_threat(
                "access_violation",
                "high",
                user_id,
                f"Unauthorized action: {action}",
            )

        return allowed

    def detect_threat(
        self,
        threat_type: str,
        severity: str,
        source: str,
        description: str,
    ) -> SecurityThreat:
        """Detecta e registra ameaça."""
        threat = SecurityThreat(
            threat_type=threat_type,
            severity=severity,
            source=source,
            description=description,
        )
        self._threats.append(threat)
        return threat

    def mitigate_threat(self, threat_id: str) -> bool:
        """Mitiga ameaça detectada."""
        for threat in self._threats:
            if threat.id == threat_id:
                threat.mitigated = True
                return True
        return False

    def run_security_audit(self) -> SecurityReport:
        """Executa auditoria de segurança."""
        report = SecurityReport()
        report.threats_detected = len(self._threats)
        report.threats_mitigated = sum(1 for threat in self._threats if threat.mitigated)
        report.access_violations = sum(
            1 for entry in self._access_log if not entry["allowed"]
        )

        critical = sum(
            1 for threat in self._threats if threat.severity == "critical" and not threat.mitigated
        )
        high = sum(
            1 for threat in self._threats if threat.severity == "high" and not threat.mitigated
        )

        score = 1.0
        score -= critical * 0.3
        score -= high * 0.15
        score -= report.access_violations * 0.05
        report.audit_score = max(0.0, min(1.0, score))

        if critical > 0 or report.audit_score < 0.5:
            report.verdict = "FAIL"
            report.findings.append("Critical security issues detected")
        elif high > 0 or report.audit_score < 0.8:
            report.verdict = "WARN"
            report.findings.append("Security warnings require attention")
        else:
            report.verdict = "PASS"
            report.findings.append("Security posture acceptable")

        self._reports.append(report)
        return report

    def get_security_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de segurança."""
        return {
            "registered_users": len(self._user_roles),
            "total_threats": len(self._threats),
            "active_threats": sum(1 for threat in self._threats if not threat.mitigated),
            "access_log_entries": len(self._access_log),
            "latest_report": self._reports[-1].to_dict() if self._reports else None,
        }
