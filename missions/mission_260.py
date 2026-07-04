# ============================================================
# MISSÃO 260 — INSTITUTIONAL FOOTPRINT ANALYZER
# Padrão Doug.AI — Nota 10
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


def _deterministic_choice(seed: str, options: List[str]) -> str:
    idx = int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) % len(options)
    return options[idx]


@dataclass
class InstitutionalFootprint:
    """Rastro institucional."""
    id: str = field(default_factory=lambda: f"if_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    volume_pattern: float = 0.0
    hidden_liquidity: float = 0.0
    large_order_ratio: float = 0.0
    accumulation_score: float = 0.0
    distribution_score: float = 0.0
    institutional_bias: float = 0.0
    institutional_confidence: float = 0.0
    execution_pattern: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "timestamp": self.timestamp.isoformat(),
            "volume_pattern": self.volume_pattern,
            "hidden_liquidity": self.hidden_liquidity,
            "large_order_ratio": self.large_order_ratio,
            "accumulation_score": self.accumulation_score,
            "distribution_score": self.distribution_score,
            "institutional_bias": self.institutional_bias,
            "institutional_confidence": self.institutional_confidence,
            "execution_pattern": self.execution_pattern,
        }


class InstitutionalFootprintAnalyzer:
    """Analisador de rastros institucionais."""

    def __init__(self):
        self._footprints: Dict[str, List[InstitutionalFootprint]] = {}
        self._asset_bias: Dict[str, float] = {}

    def analyze_footprint(
        self,
        asset: str,
        volume_data: Dict[str, float],
        order_data: Dict[str, int],
    ) -> InstitutionalFootprint:
        seed_base = f"{asset}:{volume_data}:{order_data}"
        volume_pattern = self._analyze_volume_pattern(volume_data, seed_base)
        hidden_liquidity = self._analyze_hidden_liquidity(volume_data, order_data, seed_base)
        large_order_ratio = self._analyze_large_orders(order_data, seed_base)
        accumulation_score = self._analyze_accumulation(volume_data, seed_base)
        distribution_score = self._analyze_distribution(volume_data, seed_base)
        institutional_bias = max(-1.0, min(1.0, accumulation_score - distribution_score))
        confidence = self._calculate_confidence(volume_data, order_data, seed_base)
        execution_pattern = self._detect_execution_pattern(volume_data, order_data, seed_base)

        footprint = InstitutionalFootprint(
            asset=asset,
            volume_pattern=volume_pattern,
            hidden_liquidity=hidden_liquidity,
            large_order_ratio=large_order_ratio,
            accumulation_score=accumulation_score,
            distribution_score=distribution_score,
            institutional_bias=institutional_bias,
            institutional_confidence=confidence,
            execution_pattern=execution_pattern,
        )

        self._footprints.setdefault(asset, []).append(footprint)
        self._asset_bias[asset] = institutional_bias
        return footprint

    def _analyze_volume_pattern(self, volume: Dict, seed: str) -> float:
        return _deterministic_unit(f"vol:{seed}", 0.3, 0.8)

    def _analyze_hidden_liquidity(self, volume: Dict, orders: Dict, seed: str) -> float:
        return _deterministic_unit(f"hidden:{seed}", 0.2, 0.6)

    def _analyze_large_orders(self, orders: Dict, seed: str) -> float:
        return _deterministic_unit(f"large:{seed}", 0.1, 0.4)

    def _analyze_accumulation(self, volume: Dict, seed: str) -> float:
        return _deterministic_unit(f"acc:{seed}", 0.1, 0.7)

    def _analyze_distribution(self, volume: Dict, seed: str) -> float:
        return _deterministic_unit(f"dist:{seed}", 0.1, 0.6)

    def _calculate_confidence(self, volume: Dict, orders: Dict, seed: str) -> float:
        return _deterministic_unit(f"conf:{seed}", 0.3, 0.8)

    def _detect_execution_pattern(self, volume: Dict, orders: Dict, seed: str) -> str:
        patterns = ["algorithmic", "iceberg", "pacing", "accumulation", "distribution"]
        return _deterministic_choice(f"pat:{seed}", patterns)

    def get_institutional_bias(self, asset: str) -> float:
        return self._asset_bias.get(asset, 0.0)

    def get_institutional_dashboard(self) -> Dict[str, Any]:
        return {
            "assets_tracked": len(self._footprints),
            "avg_bias": np.mean(list(self._asset_bias.values())) if self._asset_bias else 0,
            "high_confidence_assets": [
                asset for asset, bias in self._asset_bias.items() if abs(bias) > 0.5
            ],
            "recent_footprints": [
                fp.to_dict()
                for fps in self._footprints.values()
                for fp in fps[-5:]
            ][-10:],
        }
