# ============================================================
# MISSÃO 302 — LIVE SHADOW MODE
# Fase Final — Final Trading Operating System
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import hashlib
import numpy as np


def _deterministic_unit(seed: str, lo: float = 0.0, hi: float = 1.0) -> float:
    digest = hashlib.sha256(seed.encode()).hexdigest()
    return lo + (int(digest[:8], 16) / 0xFFFFFFFF) * (hi - lo)


@dataclass
class ShadowSignal:
    """Sinal em shadow mode."""

    id: str = field(default_factory=lambda: f"ss_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    direction: str = ""
    confidence: float = 0.0
    entry_price: float = 0.0
    target_price: float = 0.0
    stop_price: float = 0.0
    risk_score: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    executed: bool = False
    divergence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "direction": self.direction,
            "confidence": self.confidence,
            "entry_price": self.entry_price,
            "target_price": self.target_price,
            "stop_price": self.stop_price,
            "risk_score": self.risk_score,
            "created_at": self.created_at.isoformat(),
            "executed": self.executed,
            "divergence": self.divergence,
        }


@dataclass
class ShadowReport:
    """Relatório de shadow mode."""

    id: str = field(default_factory=lambda: f"sr_{uuid.uuid4().hex[:12]}")
    total_signals: int = 0
    signals_generated: int = 0
    divergence_detected: bool = False
    avg_divergence: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "total_signals": self.total_signals,
            "signals_generated": self.signals_generated,
            "divergence_detected": self.divergence_detected,
            "avg_divergence": self.avg_divergence,
            "created_at": self.created_at.isoformat(),
        }


class LiveShadowMode:
    """
    Modo shadow live.

    Implementa:
    - Sinais gerados
    - Decisões simuladas
    - Risco simulado
    - Performance estimada
    - Divergência entre previsão e realidade
    """

    def __init__(self):
        self._signals: List[ShadowSignal] = []
        self._reports: List[ShadowReport] = []
        self._real_prices: Dict[str, List[float]] = {}
        self._predicted_prices: Dict[str, List[float]] = {}

    def generate_signal(self, decision: Dict[str, Any], market_price: float) -> ShadowSignal:
        """Gera sinal em shadow mode."""
        signal = ShadowSignal(
            asset=decision.get("asset", ""),
            direction=decision.get("direction", ""),
            confidence=decision.get("confidence", 0.5),
            entry_price=market_price,
            target_price=decision.get("target", market_price * 1.02),
            stop_price=decision.get("stop", market_price * 0.98),
            risk_score=decision.get("risk_score", 0.3),
        )
        self._signals.append(signal)
        self._track_prices(signal.asset, market_price)
        return signal

    def _track_prices(self, asset: str, price: float) -> None:
        """Rastreia preços para cálculo de divergência."""
        if asset not in self._real_prices:
            self._real_prices[asset] = []
            self._predicted_prices[asset] = []

        self._real_prices[asset].append(price)
        seed = f"{asset}:{len(self._real_prices[asset])}:{price:.6f}"
        predicted = price * (1 + _deterministic_unit(seed, -0.02, 0.02))
        self._predicted_prices[asset].append(predicted)

    def calculate_divergence(self, asset: str) -> float:
        """Calcula divergência entre previsão e realidade."""
        if asset not in self._real_prices or len(self._real_prices[asset]) < 10:
            return 0.0

        real = np.array(self._real_prices[asset][-10:])
        predicted = np.array(self._predicted_prices[asset][-10:])
        if len(real) == 0:
            return 0.0

        error = float(np.mean(np.abs(real - predicted) / real))
        return min(error, 1.0)

    def generate_shadow_report(self) -> ShadowReport:
        """Gera relatório de shadow mode."""
        signals = [signal for signal in self._signals if not signal.executed]
        report = ShadowReport(
            total_signals=len(self._signals),
            signals_generated=len(signals),
        )

        divergences = [self.calculate_divergence(asset) for asset in self._real_prices]
        if divergences:
            report.avg_divergence = float(np.mean(divergences))
            report.divergence_detected = max(divergences) > 0.05

        self._reports.append(report)
        return report

    def get_shadow_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de shadow mode."""
        return {
            "total_signals": len(self._signals),
            "pending_signals": sum(1 for signal in self._signals if not signal.executed),
            "latest_report": self._reports[-1].to_dict() if self._reports else None,
            "divergence_by_asset": {
                asset: self.calculate_divergence(asset) for asset in self._real_prices
            },
            "recent_signals": [signal.to_dict() for signal in self._signals[-5:]],
        }
