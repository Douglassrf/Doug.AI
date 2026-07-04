from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import inspect
import ast


@dataclass
class ArchitectureViolation:
    id: str = field(default_factory=lambda: f"viol_{uuid.uuid4().hex[:12]}")
    module: str = ""
    violation_type: str = ""
    description: str = ""
    severity: str = "high"
    recommendation: str = ""
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    fixed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "module": self.module, "violation_type": self.violation_type,
            "description": self.description, "severity": self.severity,
            "recommendation": self.recommendation,
            "detected_at": self.detected_at.isoformat(), "fixed": self.fixed,
        }


@dataclass
class ArchitectureReport:
    total_modules: int = 0
    violations: List[ArchitectureViolation] = field(default_factory=list)
    critical_violations: int = 0
    high_violations: int = 0
    medium_violations: int = 0
    low_violations: int = 0
    soli_score: float = 0.0
    clean_arch_score: float = 0.0
    overall_score: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_modules": self.total_modules,
            "violations": [v.to_dict() for v in self.violations],
            "critical_violations": self.critical_violations,
            "high_violations": self.high_violations,
            "medium_violations": self.medium_violations,
            "low_violations": self.low_violations,
            "soli_score": self.soli_score,
            "clean_arch_score": self.clean_arch_score,
            "overall_score": self.overall_score,
            "created_at": self.created_at.isoformat(),
        }


class AutonomousArchitectureGuardian:
    def __init__(self):
        self._violations: List[ArchitectureViolation] = []
        self._modules: Dict[str, Any] = {}
        self._dependency_graph: Dict[str, Set[str]] = {}

    def register_module(self, module_name: str, module_object: Any) -> None:
        self._modules[module_name] = module_object
        self._dependency_graph[module_name] = set()

    def scan(self) -> ArchitectureReport:
        report = ArchitectureReport()
        report.total_modules = len(self._modules)
        self._scan_dependencies()
        circular = self._detect_circular_dependencies()
        for cycle in circular:
            v = ArchitectureViolation(
                module=" -> ".join(cycle), violation_type="circular",
                description=f"Circular dependency: {' -> '.join(cycle)}", severity="critical",
                recommendation="Break circular dependency using interfaces or dependency injection",
            )
            report.violations.append(v)
            report.critical_violations += 1
        solid_violations = self._check_solid()
        clean_violations = self._check_clean_architecture()
        for v in solid_violations + clean_violations:
            report.violations.append(v)
            if v.severity == "critical": report.critical_violations += 1
            elif v.severity == "high": report.high_violations += 1
            elif v.severity == "medium": report.medium_violations += 1
            else: report.low_violations += 1
        max_v = max(report.total_modules * 3, 1)
        report.soli_score = max(0.0, 1.0 - len(solid_violations) / max_v)
        report.clean_arch_score = max(0.0, 1.0 - len(clean_violations) / max_v)
        report.overall_score = (report.soli_score + report.clean_arch_score) / 2
        self._violations = report.violations
        return report

    def _scan_dependencies(self) -> None:
        for module_name, module_obj in self._modules.items():
            try:
                source = inspect.getsource(module_obj)
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            dep = alias.name.split('.')[0]
                            if dep in self._modules:
                                self._dependency_graph[module_name].add(dep)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            dep = node.module.split('.')[0]
                            if dep in self._modules:
                                self._dependency_graph[module_name].add(dep)
            except Exception:
                pass

    def _detect_circular_dependencies(self) -> List[List[str]]:
        cycles: List[List[str]] = []
        visited: Set[str] = set()
        path: List[str] = []

        def dfs(node: str) -> None:
            if node in path:
                cycles.append(path[path.index(node):] + [node])
                return
            if node in visited:
                return
            visited.add(node)
            path.append(node)
            for dep in self._dependency_graph.get(node, []):
                dfs(dep)
            path.pop()

        for m in self._modules:
            dfs(m)
        return cycles

    def _check_solid(self) -> List[ArchitectureViolation]:
        violations = []
        for name, obj in self._modules.items():
            try:
                methods = [m for m in dir(obj) if not m.startswith('_') and callable(getattr(obj, m))]
                if len(methods) > 20:
                    violations.append(ArchitectureViolation(
                        module=name, violation_type="solid_s",
                        description=f"Module has {len(methods)} methods — may violate Single Responsibility",
                        severity="medium", recommendation="Consider splitting into smaller modules",
                    ))
            except Exception:
                pass
            try:
                if hasattr(obj, '__abstractmethods__') and len(obj.__abstractmethods__) > 5:
                    violations.append(ArchitectureViolation(
                        module=name, violation_type="solid_i",
                        description=f"Interface has {len(obj.__abstractmethods__)} abstract methods",
                        severity="medium", recommendation="Split interface into smaller, focused interfaces",
                    ))
            except Exception:
                pass
        return violations

    def _check_clean_architecture(self) -> List[ArchitectureViolation]:
        violations = []
        for name in self._modules:
            nl = name.lower()
            if 'presentation' in nl and 'domain' in nl:
                violations.append(ArchitectureViolation(
                    module=name, violation_type="clean_arch",
                    description="Module mixes presentation and domain layers",
                    severity="high", recommendation="Separate presentation and domain layers",
                ))
            if 'infrastructure' in nl and 'domain' in nl:
                violations.append(ArchitectureViolation(
                    module=name, violation_type="clean_arch",
                    description="Module mixes infrastructure and domain layers",
                    severity="high", recommendation="Separate infrastructure and domain layers",
                ))
        return violations

    def get_report(self) -> ArchitectureReport:
        if not self._violations:
            return self.scan()
        return ArchitectureReport(
            total_modules=len(self._modules), violations=self._violations,
            critical_violations=sum(1 for v in self._violations if v.severity == "critical"),
            high_violations=sum(1 for v in self._violations if v.severity == "high"),
            medium_violations=sum(1 for v in self._violations if v.severity == "medium"),
            low_violations=sum(1 for v in self._violations if v.severity == "low"),
        )

    def fix_violation(self, violation_id: str) -> bool:
        for v in self._violations:
            if v.id == violation_id:
                v.fixed = True
                return True
        return False
