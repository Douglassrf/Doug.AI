# ============================================================
# MISSÃO 264 — ALPHA DECAY MONITOR (stub mínimo)
# Fase XVI — Alpha Generation Intelligence
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class AlphaDecayReport:
    """Relatório de decaimento de alpha."""
    id: str = field(default_factory=lambda: f"ad_{uuid.uuid4().hex[:12]}")
    alpha_id: str = ""
    decay_rate: float = 0.0
    remaining_lifetime_days: float = 0.0
    status: str = "healthy"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "alpha_id": self.alpha_id,
            "decay_rate": self.decay_rate,
            "remaining_lifetime_days": self.remaining_lifetime_days,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


class AlphaDecayMonitor:
    """Monitora decaimento e vida útil dos alphas."""

    def __init__(self):
        self._reports: Dict[str, AlphaDecayReport] = {}

    def evaluate(self, alpha_id: str, decay_rate: float, lifetime_days: float) -> AlphaDecayReport:
        remaining = max(0.0, lifetime_days * (1 - decay_rate))
        if remaining < 7:
            status = "critical"
        elif remaining < 14:
            status = "warning"
        else:
            status = "healthy"

        report = AlphaDecayReport(
            alpha_id=alpha_id,
            decay_rate=decay_rate,
            remaining_lifetime_days=remaining,
            status=status,
        )
        self._reports[alpha_id] = report
        return report

    def get_decay_dashboard(self) -> Dict[str, Any]:
        reports = list(self._reports.values())
        return {
            "alphas_monitored": len(reports),
            "critical": sum(1 for r in reports if r.status == "critical"),
            "warning": sum(1 for r in reports if r.status == "warning"),
            "avg_remaining_days": np.mean([r.remaining_lifetime_days for r in reports]) if reports else 0,
        }
