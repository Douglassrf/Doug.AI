# ============================================================
# MISSÃO 315 — ECOSYSTEM INTELLIGENCE ORCHESTRATOR
# Fase XXI — Evolutionary Trading Intelligence
# ============================================================

from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class EcosystemReport:
    """Relatório unificado do ecossistema evolutivo."""

    id: str = field(default_factory=lambda: f"eco_{uuid.uuid4().hex[:12]}")
    evolution: Dict[str, Any] = field(default_factory=dict)
    lifecycle: Dict[str, Any] = field(default_factory=dict)
    patterns: Dict[str, Any] = field(default_factory=dict)
    memory: Dict[str, Any] = field(default_factory=dict)
    liquidity: Dict[str, Any] = field(default_factory=dict)
    alpha: Dict[str, Any] = field(default_factory=dict)
    mutations: Dict[str, Any] = field(default_factory=dict)
    ecosystem_health: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "evolution": self.evolution,
            "lifecycle": self.lifecycle,
            "patterns": self.patterns,
            "memory": self.memory,
            "liquidity": self.liquidity,
            "alpha": self.alpha,
            "mutations": self.mutations,
            "ecosystem_health": self.ecosystem_health,
            "created_at": self.created_at.isoformat(),
        }


class EcosystemIntelligenceOrchestrator:
    """
    Orquestrador de inteligência do ecossistema.

    Agrega missões 308-314 em relatório e dashboard unificados.
    """

    MODULE_KEYS = [
        "evolution",
        "lifecycle",
        "patterns",
        "memory",
        "liquidity",
        "alpha",
        "mutations",
    ]

    def __init__(self):
        self._reports: list[EcosystemReport] = []

    def aggregate(self, dashboards: Dict[str, Dict[str, Any]]) -> EcosystemReport:
        """Agrega dashboards das missões 308-314."""
        report = EcosystemReport(
            evolution=dashboards.get("evolution", {}),
            lifecycle=dashboards.get("lifecycle", {}),
            patterns=dashboards.get("patterns", {}),
            memory=dashboards.get("memory", {}),
            liquidity=dashboards.get("liquidity", {}),
            alpha=dashboards.get("alpha", {}),
            mutations=dashboards.get("mutations", {}),
        )
        report.ecosystem_health = self._calculate_ecosystem_health(report)
        self._reports.append(report)
        return report

    def _calculate_ecosystem_health(self, report: EcosystemReport) -> float:
        """Calcula saúde do ecossistema a partir dos módulos ativos."""
        active = 0
        scores: list[float] = []

        module_data = {
            "evolution": report.evolution,
            "lifecycle": report.lifecycle,
            "patterns": report.patterns,
            "memory": report.memory,
            "liquidity": report.liquidity,
            "alpha": report.alpha,
            "mutations": report.mutations,
        }

        for key, data in module_data.items():
            if data and data.get("status") != "no_data":
                active += 1
                if key == "evolution" and "evolution_score" in data:
                    scores.append(float(data["evolution_score"]))
                elif key == "alpha" and "avg_edge_score" in data:
                    scores.append(float(data["avg_edge_score"]))
                elif key == "mutations" and "avg_fitness" in data:
                    scores.append(float(data["avg_fitness"]))
                else:
                    scores.append(0.5)

        if active == 0:
            return 0.0

        base = sum(scores) / len(scores) if scores else 0.0
        coverage = active / len(self.MODULE_KEYS)
        return min(base * 0.7 + coverage * 0.3, 1.0)

    def get_ecosystem_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard do ecossistema."""
        latest = self._reports[-1].to_dict() if self._reports else {}
        return {
            "reports": len(self._reports),
            "latest": latest,
            "modules_active": sum(
                1 for key in self.MODULE_KEYS if latest.get(key) and latest[key].get("status") != "no_data"
            ),
            "ecosystem_health": latest.get("ecosystem_health", 0.0),
        }
