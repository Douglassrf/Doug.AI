# ============================================================
# MISSÃO 298 — FINAL ARCHITECTURE CONSOLIDATION
# Fase Final — Final Trading Operating System
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class ArchitectureModule:
    """Módulo arquitetural."""

    id: str = field(default_factory=lambda: f"am_{uuid.uuid4().hex[:12]}")
    name: str = ""
    layer: str = ""
    dependencies: List[str] = field(default_factory=list)
    contracts: List[str] = field(default_factory=list)
    status: str = "active"
    description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "layer": self.layer,
            "dependencies": self.dependencies,
            "contracts": self.contracts,
            "status": self.status,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ArchitectureReport:
    """Relatório arquitetural."""

    id: str = field(default_factory=lambda: f"ar_{uuid.uuid4().hex[:12]}")
    total_modules: int = 0
    layers: Dict[str, int] = field(default_factory=dict)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    risks: List[Dict[str, Any]] = field(default_factory=list)
    flows: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "total_modules": self.total_modules,
            "layers": self.layers,
            "dependencies": self.dependencies,
            "risks": self.risks,
            "flows": self.flows,
            "created_at": self.created_at.isoformat(),
        }


class ArchitectureConsolidator:
    """
    Consolidador de arquitetura final.

    Implementa:
    - Mapa final de módulos
    - Dependências
    - Camadas
    - Contratos
    - Fluxos
    - Riscos
    - Relatório arquitetural
    """

    def __init__(self):
        self._modules: Dict[str, ArchitectureModule] = {}
        self._layers = [
            "foundation",
            "intelligence",
            "risk",
            "discovery",
            "evolution",
            "governance",
            "distributed",
            "executive",
        ]

    def register_module(self, module: ArchitectureModule) -> None:
        """Registra módulo arquitetural."""
        self._modules[module.id] = module

    def consolidate(self) -> ArchitectureReport:
        """Consolida arquitetura."""
        report = ArchitectureReport()
        report.total_modules = len(self._modules)

        for layer in self._layers:
            report.layers[layer] = sum(
                1 for module in self._modules.values() if module.layer == layer
            )

        for module in self._modules.values():
            report.dependencies[module.id] = module.dependencies

        report.risks = self._identify_risks()
        report.flows = self._map_flows()
        return report

    def _identify_risks(self) -> List[Dict[str, Any]]:
        """Identifica riscos arquiteturais."""
        risks: List[Dict[str, Any]] = []
        dependency_map = {
            module.id: module.dependencies for module in self._modules.values()
        }

        seen_cycles: set[tuple[str, str]] = set()
        for module_id, deps in dependency_map.items():
            for dep in deps:
                if dep in dependency_map and module_id in dependency_map.get(dep, []):
                    cycle_key = tuple(sorted((module_id, dep)))
                    if cycle_key in seen_cycles:
                        continue
                    seen_cycles.add(cycle_key)
                    risks.append(
                        {
                            "type": "circular_dependency",
                            "modules": list(cycle_key),
                            "severity": "high",
                        }
                    )

        for module in self._modules.values():
            if not module.dependencies and module.layer != "foundation":
                risks.append(
                    {
                        "type": "orphan_module",
                        "module": module.id,
                        "severity": "medium",
                    }
                )

        return risks

    def _map_flows(self) -> List[Dict[str, Any]]:
        """Mapeia fluxos de dados."""
        return [
            {
                "name": "Market Data Flow",
                "source": "market_data",
                "target": "intelligence",
                "type": "data",
            },
            {
                "name": "Decision Flow",
                "source": "intelligence",
                "target": "governance",
                "type": "decision",
            },
            {
                "name": "Risk Flow",
                "source": "risk",
                "target": "executive",
                "type": "risk",
            },
        ]

    def get_architecture_report(self) -> ArchitectureReport:
        """Retorna relatório arquitetural."""
        return self.consolidate()
