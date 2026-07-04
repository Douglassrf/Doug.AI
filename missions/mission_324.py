# ============================================================
# MISSÃO 324 — GLOBAL SYSTEM ORCHESTRATOR
# Fase Ômega Final — Doug.AI v1.0
# ============================================================

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

_missions_dir = Path(__file__).resolve().parent
if str(_missions_dir) not in sys.path:
    sys.path.insert(0, str(_missions_dir))

from mission_318 import DougOperatingSystem
from mission_319 import UniversalEventBus
from mission_320 import UniversalTimeMachine
from mission_321 import AIDigitalGenome
from mission_322 import IntelligenceCompiler
from mission_323 import AutonomousArchitectureOptimizer


@dataclass
class BootStep:
    """Passo da sequência de boot."""

    id: str = field(default_factory=lambda: f"bs_{uuid.uuid4().hex[:12]}")
    component: str = ""
    status: str = "pending"
    message: str = ""
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "component": self.component,
            "status": self.status,
            "message": self.message,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class SystemStatusReport:
    """Relatório unificado de status."""

    id: str = field(default_factory=lambda: f"ssr_{uuid.uuid4().hex[:12]}")
    boot_complete: bool = False
    components: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    boot_steps: List[BootStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "boot_complete": self.boot_complete,
            "components": self.components,
            "boot_steps": [step.to_dict() for step in self.boot_steps],
            "created_at": self.created_at.isoformat(),
        }


class GlobalSystemOrchestrator:
    """
    Orquestrador global do Doug.AI.

    Coordena DougOS, EventBus, TimeMachine, Genome, Compiler e Optimizer.
    """

    BOOT_SEQUENCE = (
        "doug_os",
        "event_bus",
        "time_machine",
        "genome",
        "compiler",
        "optimizer",
    )

    def __init__(self):
        self.doug_os = DougOperatingSystem()
        self.event_bus = UniversalEventBus()
        self.time_machine = UniversalTimeMachine()
        self.genome = AIDigitalGenome()
        self.compiler = IntelligenceCompiler()
        self.optimizer = AutonomousArchitectureOptimizer()
        self._boot_steps: List[BootStep] = []
        self._boot_complete = False
        self._reports: List[SystemStatusReport] = []

    async def boot_sequence(self) -> SystemStatusReport:
        """Executa sequência de boot unificada."""
        self._boot_steps.clear()
        self._boot_complete = False

        for component in self.BOOT_SEQUENCE:
            step = BootStep(component=component, status="running")
            self._boot_steps.append(step)

            try:
                if component == "doug_os":
                    self.doug_os.set_config("orchestrator", "omega_final")
                    self.doug_os.register_module(
                        "event_bus",
                        "core",
                        self.event_bus,
                        start_priority=1,
                    )
                    step.status = "completed"
                    step.message = "DougOS configured"
                elif component == "event_bus":
                    await self.event_bus.start(workers=2)
                    step.status = "completed"
                    step.message = "Event bus started"
                elif component == "time_machine":
                    self.time_machine.create_snapshot("boot", {"phase": "omega_final"})
                    step.status = "completed"
                    step.message = "Initial snapshot created"
                elif component == "genome":
                    self.genome.create_genome(
                        "doug_ai_root",
                        "architecture",
                        {"version": "1.0.0"},
                    )
                    step.status = "completed"
                    step.message = "Root genome created"
                elif component == "compiler":
                    self.compiler.register_module(
                        "core",
                        {"role": "orchestrator"},
                        [],
                        ["boot_complete"],
                        {"core": 1.0},
                    )
                    self.compiler.compile()
                    step.status = "completed"
                    step.message = "Intelligence compiled"
                elif component == "optimizer":
                    self.optimizer.register_module("core", [], complexity=0.3, cohesion=0.9)
                    self.optimizer.analyze_architecture()
                    step.status = "completed"
                    step.message = "Architecture analyzed"

                step.completed_at = datetime.now(timezone.utc)

            except Exception as exc:
                step.status = "failed"
                step.message = str(exc)
                break

        self._boot_complete = all(step.status == "completed" for step in self._boot_steps)
        report = SystemStatusReport(
            boot_complete=self._boot_complete,
            components=self.get_unified_status()["components"],
            boot_steps=self._boot_steps.copy(),
        )
        self._reports.append(report)
        return report

    def get_unified_status(self) -> Dict[str, Any]:
        """Retorna status unificado de todos os componentes."""
        return {
            "boot_complete": self._boot_complete,
            "components": {
                "doug_os": self.doug_os.get_dashboard(),
                "event_bus": self.event_bus.get_metrics(),
                "time_machine": self.time_machine.get_time_machine_dashboard(),
                "genome": self.genome.get_genome_dashboard(),
                "compiler": self.compiler.get_compiler_dashboard(),
                "optimizer": self.optimizer.get_architecture_dashboard(),
            },
            "boot_steps": [step.to_dict() for step in self._boot_steps],
            "latest_report": self._reports[-1].to_dict() if self._reports else None,
        }

    async def shutdown(self) -> None:
        """Encerra componentes do sistema."""
        await self.event_bus.stop()
        await self.doug_os.stop()
