from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any
import numpy as np


@dataclass
class CompressionMetrics:
    compression_ratio: float = 0.0
    information_loss: float = 0.0
    explanatory_limit: float = 0.0
    dimension_reduction: float = 0.0
    alert_level: str = "green"  # green | yellow | red
    warning: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "compression_ratio": self.compression_ratio,
            "information_loss": self.information_loss,
            "explanatory_limit": self.explanatory_limit,
            "dimension_reduction": self.dimension_reduction,
            "alert_level": self.alert_level,
            "warning": self.warning,
            "created_at": self.created_at.isoformat(),
        }


class RealityCompressionEngine:
    """Detecta simplificações perigosas por perda de informação excessiva."""

    MAX_SAFE_COMPRESSION = 0.30  # 30%
    MAX_SAFE_INFO_LOSS = 0.40

    def __init__(self):
        self._history: List[CompressionMetrics] = []

    def analyze(self, data: Dict[str, Any]) -> CompressionMetrics:
        m = CompressionMetrics()
        original_dim = int(data.get("original_dim", len(data.get("features", []))))
        reduced_dim = int(data.get("reduced_dim", original_dim))

        if original_dim > 0 and reduced_dim > 0:
            m.dimension_reduction = reduced_dim / original_dim
            m.compression_ratio = 1.0 - m.dimension_reduction

        variance_explained = float(data.get("variance_explained", 1.0))
        m.information_loss = 1.0 - variance_explained
        m.explanatory_limit = max(0.0, 0.8 - m.information_loss * 2) if m.information_loss > 0.3 else 0.8

        if m.information_loss > self.MAX_SAFE_INFO_LOSS:
            m.alert_level = "red"
            m.warning = f"Information loss {m.information_loss:.2%} critical — model oversimplifying"
        elif m.compression_ratio > self.MAX_SAFE_COMPRESSION:
            m.alert_level = "yellow"
            m.warning = f"Compression ratio {m.compression_ratio:.2%} exceeds safe threshold"

        self._history.append(m)
        return m

    def detect_dangerous_simplification(self) -> List[Dict[str, Any]]:
        return [
            {
                "index": i,
                "compression_ratio": m.compression_ratio,
                "information_loss": m.information_loss,
                "level": m.alert_level,
                "warning": m.warning,
            }
            for i, m in enumerate(self._history)
            if m.alert_level in ("yellow", "red")
        ]
