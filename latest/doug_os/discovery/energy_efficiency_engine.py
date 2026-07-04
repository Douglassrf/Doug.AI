from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False


@dataclass
class EnergyProfile:
    id: str = field(default_factory=lambda: f"ep_{uuid.uuid4().hex[:12]}")
    component: str = ""
    cpu_energy: float = 0.0
    memory_energy: float = 0.0
    total_energy: float = 0.0
    efficiency_score: float = 0.0
    workload_pattern: str = "normal"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "component": self.component,
            "cpu_energy": self.cpu_energy,
            "memory_energy": self.memory_energy,
            "total_energy": self.total_energy,
            "efficiency_score": self.efficiency_score,
            "workload_pattern": self.workload_pattern,
            "timestamp": self.timestamp.isoformat(),
        }


class EnergyEfficiencyEngine:
    """Motor de eficiência energética com perfis, agendamento e modo idle."""

    def __init__(self, idle_threshold: float = 20.0, heavy_threshold: float = 70.0) -> None:
        self._profiles: List[EnergyProfile] = []
        self._idle_threshold = idle_threshold
        self._heavy_threshold = heavy_threshold
        self._idle_mode = False
        self._heavy_task_window = False

    def measure_energy(self, cpu_percent: Optional[float] = None, memory_percent: Optional[float] = None) -> EnergyProfile:
        """Mede consumo energético. Aceita valores externos para facilitar testes."""
        if _HAS_PSUTIL and cpu_percent is None:
            try:
                cpu_percent = psutil.cpu_percent(interval=0)
                memory_percent = psutil.virtual_memory().percent
            except Exception:
                cpu_percent = 0.0
                memory_percent = 0.0
        else:
            cpu_percent = cpu_percent or 0.0
            memory_percent = memory_percent or 0.0

        cpu_energy = cpu_percent / 100.0 * 50.0
        memory_energy = memory_percent / 100.0 * 20.0
        total_energy = cpu_energy + memory_energy
        efficiency_score = max(0.0, min(1.0, 1.0 - total_energy / 100.0))

        if cpu_percent < self._idle_threshold:
            pattern = "idle"
            self._idle_mode = True
            self._heavy_task_window = False
        elif cpu_percent > self._heavy_threshold:
            pattern = "heavy"
            self._heavy_task_window = True
            self._idle_mode = False
        else:
            pattern = "normal"
            self._idle_mode = False
            self._heavy_task_window = False

        profile = EnergyProfile(
            component="system",
            cpu_energy=cpu_energy,
            memory_energy=memory_energy,
            total_energy=total_energy,
            efficiency_score=efficiency_score,
            workload_pattern=pattern,
        )
        self._profiles.append(profile)
        return profile

    def schedule_workload(self, task_type: str) -> Dict[str, Any]:
        if self._heavy_task_window and task_type == "heavy":
            return {"scheduled": True, "recommendation": "Execute heavy task during current window", "efficiency_impact": 0.8}
        if self._idle_mode:
            return {"scheduled": True, "recommendation": "Idle mode — good for background tasks", "efficiency_impact": 0.9}
        return {"scheduled": True, "recommendation": "Normal operation", "efficiency_impact": 0.6}

    def get_efficiency_metrics(self) -> Dict[str, Any]:
        if not self._profiles:
            return {"status": "no_data"}
        recent = self._profiles[-60:]
        return {
            "avg_efficiency": sum(p.efficiency_score for p in recent) / len(recent),
            "avg_energy": sum(p.total_energy for p in recent) / len(recent),
            "idle_time_ratio": sum(1 for p in recent if p.workload_pattern == "idle") / len(recent),
            "heavy_time_ratio": sum(1 for p in recent if p.workload_pattern == "heavy") / len(recent),
        }

    def get_energy_dashboard(self) -> Dict[str, Any]:
        return {
            "current_profile": self._profiles[-1].to_dict() if self._profiles else None,
            "metrics": self.get_efficiency_metrics(),
            "idle_mode": self._idle_mode,
            "heavy_window": self._heavy_task_window,
        }
