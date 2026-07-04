# ============================================================
# MISSÃO 262 — TRADE EFFICIENCY ANALYZER
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class TradeEfficiency:
    """Eficiência de trade."""
    id: str = field(default_factory=lambda: f"te_{uuid.uuid4().hex[:12]}")
    trade_id: str = ""
    entry_quality: float = 0.0
    exit_quality: float = 0.0
    execution_delay_ms: float = 0.0
    slippage_bps: float = 0.0
    opportunity_lost: float = 0.0
    profit_efficiency: float = 0.0
    execution_score: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "trade_id": self.trade_id,
            "entry_quality": self.entry_quality,
            "exit_quality": self.exit_quality,
            "execution_delay_ms": self.execution_delay_ms,
            "slippage_bps": self.slippage_bps,
            "opportunity_lost": self.opportunity_lost,
            "profit_efficiency": self.profit_efficiency,
            "execution_score": self.execution_score,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ImprovementSuggestion:
    """Sugestão de melhoria."""
    id: str = field(default_factory=lambda: f"is_{uuid.uuid4().hex[:12]}")
    trade_id: str = ""
    metric: str = ""
    current_value: float = 0.0
    suggested_value: float = 0.0
    expected_improvement: float = 0.0
    priority: int = 5
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "trade_id": self.trade_id,
            "metric": self.metric,
            "current_value": self.current_value,
            "suggested_value": self.suggested_value,
            "expected_improvement": self.expected_improvement,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
        }


class TradeEfficiencyAnalyzer:
    """Analisador de eficiência de trades."""

    def __init__(self):
        self._efficiencies: Dict[str, TradeEfficiency] = {}
        self._suggestions: List[ImprovementSuggestion] = []
        self._historical_metrics: Dict[str, List[float]] = {}

    def analyze_trade(
        self,
        trade_id: str,
        entry_data: Dict[str, Any],
        exit_data: Dict[str, Any],
        execution_data: Dict[str, Any],
    ) -> TradeEfficiency:
        entry_quality = self._evaluate_entry_quality(entry_data)
        exit_quality = self._evaluate_exit_quality(exit_data)
        execution_delay = float(execution_data.get("delay_ms", 0.0))
        slippage = float(execution_data.get("slippage_bps", 0.0))
        opportunity_lost = self._calculate_opportunity_lost(entry_data, exit_data)
        profit_efficiency = self._calculate_profit_efficiency(entry_data, exit_data, slippage)
        execution_score = self._calculate_execution_score(
            entry_quality, exit_quality, execution_delay, slippage
        )

        efficiency = TradeEfficiency(
            trade_id=trade_id,
            entry_quality=entry_quality,
            exit_quality=exit_quality,
            execution_delay_ms=execution_delay,
            slippage_bps=slippage,
            opportunity_lost=opportunity_lost,
            profit_efficiency=profit_efficiency,
            execution_score=execution_score,
        )

        self._efficiencies[trade_id] = efficiency
        self._record_historical(trade_id, execution_score)
        self._generate_suggestions(trade_id, efficiency)
        return efficiency

    def _evaluate_entry_quality(self, entry_data: Dict[str, Any]) -> float:
        price_vs_signal = entry_data.get("price_vs_signal", 0.0)
        timing_score = entry_data.get("timing_score", 0.5)
        quality = timing_score * 0.6 + (1 - abs(price_vs_signal)) * 0.4
        return max(0.0, min(1.0, quality))

    def _evaluate_exit_quality(self, exit_data: Dict[str, Any]) -> float:
        target_hit = 1.0 if exit_data.get("hit_target", False) else 0.5
        timing_score = exit_data.get("timing_score", 0.5)
        quality = target_hit * 0.5 + timing_score * 0.5
        return max(0.0, min(1.0, quality))

    def _calculate_opportunity_lost(self, entry_data: Dict[str, Any], exit_data: Dict[str, Any]) -> float:
        optimal_entry = entry_data.get("optimal_price", entry_data.get("price", 0.0))
        actual_entry = entry_data.get("price", optimal_entry)
        optimal_exit = exit_data.get("optimal_price", exit_data.get("price", 0.0))
        actual_exit = exit_data.get("price", optimal_exit)
        if optimal_entry == 0:
            return 0.0
        entry_loss = abs(actual_entry - optimal_entry) / abs(optimal_entry)
        exit_loss = abs(actual_exit - optimal_exit) / abs(optimal_exit) if optimal_exit else 0.0
        return min(1.0, (entry_loss + exit_loss) / 2)

    def _calculate_profit_efficiency(
        self,
        entry_data: Dict[str, Any],
        exit_data: Dict[str, Any],
        slippage_bps: float,
    ) -> float:
        realized = exit_data.get("profit_pct", 0.0)
        max_potential = exit_data.get("max_profit_pct", realized)
        if max_potential <= 0:
            return 0.0
        slippage_penalty = slippage_bps / 10000
        efficiency = (realized / max_potential) - slippage_penalty
        return max(0.0, min(1.0, efficiency))

    def _calculate_execution_score(
        self,
        entry_quality: float,
        exit_quality: float,
        delay_ms: float,
        slippage_bps: float,
    ) -> float:
        delay_penalty = min(delay_ms / 1000, 0.3)
        slippage_penalty = min(slippage_bps / 50, 0.3)
        raw = (entry_quality + exit_quality) / 2 - delay_penalty - slippage_penalty
        return max(0.0, min(1.0, raw))

    def _record_historical(self, trade_id: str, execution_score: float) -> None:
        self._historical_metrics.setdefault("execution_score", []).append(execution_score)

    def _generate_suggestions(self, trade_id: str, efficiency: TradeEfficiency) -> None:
        thresholds = [
            ("entry_quality", efficiency.entry_quality, 0.7, 1),
            ("exit_quality", efficiency.exit_quality, 0.7, 2),
            ("slippage_bps", efficiency.slippage_bps, 5.0, 1),
            ("execution_delay_ms", efficiency.execution_delay_ms, 100.0, 3),
        ]
        for metric, current, target, priority in thresholds:
            needs_improvement = (
                current < target if metric.endswith("quality") else current > target
            )
            if needs_improvement:
                expected = abs(current - target) / max(target, 1e-9)
                self._suggestions.append(
                    ImprovementSuggestion(
                        trade_id=trade_id,
                        metric=metric,
                        current_value=current,
                        suggested_value=target,
                        expected_improvement=min(1.0, expected),
                        priority=priority,
                    )
                )

    def get_suggestions(self, trade_id: str) -> List[ImprovementSuggestion]:
        return [s for s in self._suggestions if s.trade_id == trade_id]

    def get_efficiency_dashboard(self) -> Dict[str, Any]:
        scores = [e.execution_score for e in self._efficiencies.values()]
        return {
            "trades_analyzed": len(self._efficiencies),
            "avg_execution_score": np.mean(scores) if scores else 0,
            "avg_slippage_bps": np.mean([e.slippage_bps for e in self._efficiencies.values()]) if self._efficiencies else 0,
            "suggestions_count": len(self._suggestions),
            "historical_avg": np.mean(self._historical_metrics.get("execution_score", [])) or 0,
        }
