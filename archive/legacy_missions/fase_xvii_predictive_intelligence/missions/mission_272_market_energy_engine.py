# ============================================================
# MISSÃO 272 — MARKET ENERGY ENGINE
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class EnergyIndex:
    """Índice de energia do mercado."""
    id: str = field(default_factory=lambda: f"ei_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    energy_score: float = 0.0
    momentum_pressure: float = 0.0
    order_flow_energy: float = 0.0
    liquidity_energy: float = 0.0
    expansion_probability: float = 0.0
    exhaustion_detected: bool = False
    cycle_phase: str = "accumulating"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "energy_score": self.energy_score,
            "momentum_pressure": self.momentum_pressure,
            "order_flow_energy": self.order_flow_energy,
            "liquidity_energy": self.liquidity_energy,
            "expansion_probability": self.expansion_probability,
            "exhaustion_detected": self.exhaustion_detected,
            "cycle_phase": self.cycle_phase,
            "created_at": self.created_at.isoformat(),
        }


class MarketEnergyEngine:
    """Motor de energia de mercado."""

    def __init__(self):
        self._indices: Dict[str, List[EnergyIndex]] = {}
        self._rankings: List[Dict[str, Any]] = []

    def calculate_energy(self, asset: str, market_data: Dict[str, Any]) -> EnergyIndex:
        momentum_pressure = self._calculate_momentum_pressure(market_data)
        order_flow_energy = self._calculate_order_flow_energy(market_data)
        liquidity_energy = self._calculate_liquidity_energy(market_data)
        energy_score = (
            momentum_pressure * 0.4 + order_flow_energy * 0.35 + liquidity_energy * 0.25
        )
        expansion_probability = self._calculate_expansion_probability(market_data, energy_score)
        exhaustion_detected = self._detect_exhaustion(market_data, energy_score)
        cycle_phase = self._determine_cycle_phase(energy_score, exhaustion_detected)

        index = EnergyIndex(
            asset=asset,
            energy_score=energy_score,
            momentum_pressure=momentum_pressure,
            order_flow_energy=order_flow_energy,
            liquidity_energy=liquidity_energy,
            expansion_probability=expansion_probability,
            exhaustion_detected=exhaustion_detected,
            cycle_phase=cycle_phase,
        )

        self._indices.setdefault(asset, []).append(index)
        return index

    def _calculate_momentum_pressure(self, data: Dict[str, Any]) -> float:
        momentum = abs(data.get("momentum", 0.0))
        trend = data.get("trend_strength", 0.0)
        return min(momentum * 0.5 + trend * 0.5, 1.0)

    def _calculate_order_flow_energy(self, data: Dict[str, Any]) -> float:
        buy_pressure = data.get("buy_pressure", 0.5)
        sell_pressure = data.get("sell_pressure", 0.5)
        imbalance = abs(buy_pressure - sell_pressure)
        volume = min(data.get("volume_ratio", 0.5), 1.0)
        return min(imbalance * 0.6 + volume * 0.4, 1.0)

    def _calculate_liquidity_energy(self, data: Dict[str, Any]) -> float:
        depth = data.get("depth", 0.5)
        spread = data.get("spread", 0.02)
        spread_score = 1 - min(spread / 0.1, 1.0)
        return min(depth * 0.5 + spread_score * 0.5, 1.0)

    def _calculate_expansion_probability(self, data: Dict[str, Any], energy_score: float) -> float:
        volatility = data.get("volatility", 0.3)
        return min(energy_score * 0.5 + volatility * 0.5, 1.0)

    def _detect_exhaustion(self, data: Dict[str, Any], energy_score: float) -> bool:
        momentum = abs(data.get("momentum", 0.0))
        return energy_score > 0.7 and momentum < 0.2

    def _determine_cycle_phase(self, energy_score: float, exhaustion: bool) -> str:
        if exhaustion:
            return "exhausting"
        if energy_score > 0.75:
            return "peaking"
        if energy_score > 0.5:
            return "accelerating"
        return "accumulating"

    def rank_assets(self) -> List[Dict[str, Any]]:
        ranking = []
        for asset, indices in self._indices.items():
            if indices:
                latest = indices[-1]
                ranking.append({
                    "asset": asset,
                    "energy_score": latest.energy_score,
                    "cycle_phase": latest.cycle_phase,
                })
        ranking.sort(key=lambda x: x["energy_score"], reverse=True)
        self._rankings = ranking
        return ranking

    def get_energy_dashboard(self) -> Dict[str, Any]:
        all_indices = [idx for indices in self._indices.values() for idx in indices]
        return {
            "assets_tracked": len(self._indices),
            "total_indices": len(all_indices),
            "avg_energy_score": np.mean([i.energy_score for i in all_indices]) if all_indices else 0,
            "exhaustion_count": sum(1 for i in all_indices if i.exhaustion_detected),
            "cycle_phases": {
                phase: sum(1 for i in all_indices if i.cycle_phase == phase)
                for phase in ["accumulating", "accelerating", "peaking", "exhausting"]
            },
            "top_energy_assets": self.rank_assets()[:5],
        }
