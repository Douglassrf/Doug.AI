# ============================================================
# MISSÃO 308 — MARKET EVOLUTION ENGINE
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class MarketEvolutionReport:
    """Relatório de evolução do mercado."""

    id: str = field(default_factory=lambda: f"mer_{uuid.uuid4().hex[:12]}")
    evolution_score: float = 0.0
    structural_shift_detected: bool = False
    behavioral_drift: float = 0.0
    liquidity_evolution: float = 0.0
    institutional_evolution: float = 0.0
    regime_mutation: bool = False
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "evolution_score": self.evolution_score,
            "structural_shift_detected": self.structural_shift_detected,
            "behavioral_drift": self.behavioral_drift,
            "liquidity_evolution": self.liquidity_evolution,
            "institutional_evolution": self.institutional_evolution,
            "regime_mutation": self.regime_mutation,
            "timeline": self.timeline[-10:],
            "created_at": self.created_at.isoformat(),
        }


class MarketEvolutionEngine:
    """
    Motor de evolução do mercado.

    Implementa:
    - Market Evolution Detector
    - Structural Shift Monitor
    - Behavioral Drift
    - Liquidity Evolution
    - Institutional Evolution
    - Regime Mutation
    - Evolution Score
    - Evolution Timeline
    - Historical Evolution
    - Evolution Dashboard
    """

    def __init__(self):
        self._reports: List[MarketEvolutionReport] = []
        self._history: Dict[str, List[float]] = {
            "volatility": [],
            "liquidity": [],
            "institutional": [],
            "behavioral": [],
        }

    def analyze_evolution(
        self,
        market_data: Dict[str, Any],
        historical_data: Dict[str, Any],
    ) -> MarketEvolutionReport:
        """Analisa evolução do mercado."""
        report = MarketEvolutionReport()

        report.structural_shift_detected = self._detect_structural_shift(
            market_data, historical_data
        )
        report.behavioral_drift = self._calculate_behavioral_drift(
            market_data, historical_data
        )
        report.liquidity_evolution = self._calculate_liquidity_evolution(
            market_data, historical_data
        )
        report.institutional_evolution = self._calculate_institutional_evolution(
            market_data, historical_data
        )
        report.regime_mutation = self._detect_regime_mutation(
            market_data, historical_data
        )
        report.evolution_score = self._calculate_evolution_score(report)
        report.timeline = self._build_timeline(market_data, historical_data)

        self._reports.append(report)
        self._update_history(market_data)

        return report

    def _detect_structural_shift(self, current: Dict[str, Any], historical: Dict[str, Any]) -> bool:
        """Detecta mudança estrutural comparando volatilidade recente vs histórica."""
        if len(self._reports) < 10:
            return False

        recent_vol = current.get("volatility", 0.3)
        historical_vol = historical.get("volatility", 0.3)

        if historical_vol == 0:
            return False

        return abs(recent_vol - historical_vol) / historical_vol > 0.5

    def _calculate_behavioral_drift(
        self, current: Dict[str, Any], historical: Dict[str, Any]
    ) -> float:
        """Calcula drift comportamental."""
        recent = current.get("behavioral", {})
        historic = historical.get("behavioral", {})

        if not recent or not historic:
            return 0.0

        drift = 0.0
        count = 0

        for key in ["trend_consistency", "mean_reversion", "volatility_clustering"]:
            if key in recent and key in historic:
                drift += abs(recent[key] - historic[key])
                count += 1

        return drift / count if count > 0 else 0.0

    def _calculate_liquidity_evolution(
        self, current: Dict[str, Any], historical: Dict[str, Any]
    ) -> float:
        """Calcula evolução da liquidez."""
        recent = current.get("liquidity", 0.5)
        historic = historical.get("liquidity", 0.5)
        return abs(recent - historic)

    def _calculate_institutional_evolution(
        self, current: Dict[str, Any], historical: Dict[str, Any]
    ) -> float:
        """Calcula evolução institucional."""
        recent = current.get("institutional", {})
        historic = historical.get("institutional", {})

        if not recent or not historic:
            return 0.0

        return abs(recent.get("presence", 0.5) - historic.get("presence", 0.5))

    def _detect_regime_mutation(
        self, current: Dict[str, Any], historical: Dict[str, Any]
    ) -> bool:
        """Detecta mutação de regime."""
        return current.get("regime", "unknown") != historical.get("regime", "unknown")

    def _calculate_evolution_score(self, report: MarketEvolutionReport) -> float:
        """Calcula score de evolução."""
        score = 0.0

        if report.structural_shift_detected:
            score += 0.3
        if report.regime_mutation:
            score += 0.2
        if report.behavioral_drift > 0.3:
            score += 0.2
        if report.liquidity_evolution > 0.3:
            score += 0.15
        if report.institutional_evolution > 0.3:
            score += 0.15

        return min(score, 1.0)

    def _build_timeline(
        self, current: Dict[str, Any], historical: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Constrói timeline de evolução."""
        timeline: List[Dict[str, Any]] = []
        now = datetime.now(timezone.utc).isoformat()

        if self._detect_structural_shift(current, historical):
            timeline.append(
                {"event": "structural_shift", "timestamp": now, "severity": "high"}
            )

        if self._detect_regime_mutation(current, historical):
            timeline.append(
                {"event": "regime_mutation", "timestamp": now, "severity": "medium"}
            )

        return timeline

    def _update_history(self, data: Dict[str, Any]) -> None:
        """Atualiza histórico."""
        if "volatility" in data:
            self._history["volatility"].append(data["volatility"])
        if "liquidity" in data:
            self._history["liquidity"].append(data["liquidity"])

    def get_evolution_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de evolução."""
        if not self._reports:
            return {"status": "no_data"}

        recent = self._reports[-10:]

        return {
            "total_reports": len(self._reports),
            "evolution_score": float(np.mean([r.evolution_score for r in recent])),
            "structural_shifts": sum(1 for r in recent if r.structural_shift_detected),
            "regime_mutations": sum(1 for r in recent if r.regime_mutation),
            "avg_behavioral_drift": float(np.mean([r.behavioral_drift for r in recent])),
            "trend": (
                "evolving"
                if recent[-1].evolution_score > recent[0].evolution_score
                else "stable"
            ),
            "latest_report": recent[-1].to_dict() if recent else None,
        }
