# ============================================================
# MISSÃO 322 — INTELLIGENCE COMPILER
# Fase Ômega Final — Doug.AI v1.0
# ============================================================

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import time
import networkx as nx


@dataclass
class CompiledIntelligence:
    """Inteligência compilada."""

    id: str = field(default_factory=lambda: f"ci_{uuid.uuid4().hex[:12]}")
    modules: List[Dict[str, Any]] = field(default_factory=list)
    weights: Dict[str, float] = field(default_factory=dict)
    dependencies: List[Tuple[str, str]] = field(default_factory=list)
    rules: List[str] = field(default_factory=list)
    compiled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "modules": self.modules,
            "weights": self.weights,
            "dependencies": self.dependencies,
            "rules": self.rules[:10],
            "compiled_at": self.compiled_at.isoformat(),
            "version": self.version,
        }


@dataclass
class CompilerReport:
    """Relatório do compilador."""

    id: str = field(default_factory=lambda: f"cr_{uuid.uuid4().hex[:12]}")
    total_modules: int = 0
    total_dependencies: int = 0
    conflicts: int = 0
    redundancies: int = 0
    consistency_score: float = 0.0
    compilation_time_ms: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "total_modules": self.total_modules,
            "total_dependencies": self.total_dependencies,
            "conflicts": self.conflicts,
            "redundancies": self.redundancies,
            "consistency_score": self.consistency_score,
            "compilation_time_ms": self.compilation_time_ms,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat(),
        }


class IntelligenceCompiler:
    """
    Compilador de inteligência.

    Implementa dependency graph, conflict/redundancy detection e compiled output.
    """

    def __init__(self):
        self._graph = nx.DiGraph()
        self._reports: List[CompilerReport] = []
        self._modules: Dict[str, Dict[str, Any]] = {}
        self._compiled: List[CompiledIntelligence] = []

    def register_module(
        self,
        module_id: str,
        module_data: Dict[str, Any],
        dependencies: List[str],
        rules: List[str],
        weights: Dict[str, float],
    ) -> None:
        """Registra módulo para compilação."""
        self._modules[module_id] = {
            "data": module_data,
            "dependencies": dependencies,
            "rules": rules,
            "weights": weights,
        }

        self._graph.add_node(module_id)
        for dep in dependencies:
            self._graph.add_edge(module_id, dep)

    def compile(self) -> CompilerReport:
        """Compila inteligência."""
        start = time.perf_counter()
        report = CompilerReport()
        report.total_modules = len(self._modules)
        report.total_dependencies = sum(
            len(module["dependencies"]) for module in self._modules.values()
        )
        report.conflicts = self._detect_conflicts()
        report.redundancies = self._detect_redundancies()
        report.consistency_score = self._check_consistency()
        report.recommendations = self._generate_recommendations(report)
        report.compilation_time_ms = (time.perf_counter() - start) * 1000

        compiled = CompiledIntelligence(
            modules=[
                {"id": module_id, **module["data"]}
                for module_id, module in self._modules.items()
            ],
            weights={
                key: value
                for module in self._modules.values()
                for key, value in module["weights"].items()
            },
            dependencies=list(self._graph.edges()),
            rules=[
                rule
                for module in self._modules.values()
                for rule in module["rules"]
            ],
        )
        self._compiled.append(compiled)
        self._reports.append(report)
        return report

    def get_latest_compiled(self) -> Optional[CompiledIntelligence]:
        """Retorna última inteligência compilada."""
        return self._compiled[-1] if self._compiled else None

    def _detect_conflicts(self) -> int:
        """Detecta conflitos entre módulos."""
        conflicts = 0
        module_ids = list(self._modules.keys())

        for index in range(len(module_ids)):
            for other in range(index + 1, len(module_ids)):
                first = module_ids[index]
                second = module_ids[other]

                if nx.has_path(self._graph, first, second) and nx.has_path(
                    self._graph, second, first
                ):
                    conflicts += 1

        return conflicts

    def _detect_redundancies(self) -> int:
        """Detecta redundâncias."""
        redundancies = 0
        rules_seen: set[str] = set()

        for module in self._modules.values():
            for rule in module["rules"]:
                if rule in rules_seen:
                    redundancies += 1
                rules_seen.add(rule)

        return redundancies

    def _check_consistency(self) -> float:
        """Verifica consistência geral."""
        if not self._modules:
            return 1.0

        score = 1.0
        score -= self._detect_conflicts() * 0.1
        score -= self._detect_redundancies() * 0.05
        return max(score, 0.0)

    def _generate_recommendations(self, report: CompilerReport) -> List[str]:
        """Gera recomendações."""
        recommendations: List[str] = []

        if report.conflicts > 0:
            recommendations.append(
                f"Resolve {report.conflicts} conflicts between modules"
            )

        if report.redundancies > 0:
            recommendations.append(f"Remove {report.redundancies} redundant rules")

        if report.consistency_score < 0.8:
            recommendations.append("Improve overall consistency")

        if report.total_dependencies > report.total_modules * 2:
            recommendations.append("Reduce coupling between modules")

        return recommendations

    def get_compiler_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard do compilador."""
        return {
            "total_reports": len(self._reports),
            "latest_report": self._reports[-1].to_dict() if self._reports else None,
            "total_modules": len(self._modules),
            "total_dependencies": sum(
                len(module["dependencies"]) for module in self._modules.values()
            ),
            "avg_dependencies": (
                sum(len(module["dependencies"]) for module in self._modules.values())
                / len(self._modules)
                if self._modules
                else 0
            ),
            "compiled_count": len(self._compiled),
        }
